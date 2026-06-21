"""Parallel multi-lineage evolution. No merging, no single winner, anti-collapse."""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from pydantic import BaseModel, Field

from . import bridge, scoring
from .ledger import append_history, write_iteration_plan
from .registry import TheoryRegistry
from .theory import TheorySpec
from .tournament import TournamentReport, run_tournament


class GenerationSnapshot(BaseModel):
    generation: int
    theory_ids: list[str]
    families: list[str]
    pareto_front: list[str]
    family_elites: dict[str, list[str]]
    display_ranking: list[tuple[str, float]]


class EvolutionReport(BaseModel):
    generations: list[GenerationSnapshot] = Field(default_factory=list)
    final_theory_ids: list[str] = Field(default_factory=list)
    final_families: list[str] = Field(default_factory=list)
    archive_ids: list[str] = Field(default_factory=list)
    iteration_plan: str | None = None  # path to the auto-generated next-iteration plan
    allow_merge: bool = False  # invariant


def _optimize_one(theory: TheorySpec, budget: int) -> TheorySpec:
    seed = bridge.seed_vector(theory)
    improved = bridge.optimize(theory, seed, budget=budget)
    return theory.model_copy(update={"seed_vector": list(improved.values)})


def _select_next_generation(
    scores: list[scoring.TheoryScoreVector],
    registry: TheoryRegistry,
    min_families: int,
    elites_per_family: int,
    population_size: int,
) -> list[TheorySpec]:
    """Pareto front + per-family elites, then fill by display score. Never collapses
    to one theory; guarantees >= min_families distinct families if available."""

    keep_ids: list[str] = []
    front = scoring.pareto_front(scores)
    keep_ids += [s.theory_id for s in front]

    elites = scoring.family_elites(scores, elites_per_family)
    for fam_scores in elites.values():
        for s in fam_scores:
            if s.theory_id not in keep_ids:
                keep_ids.append(s.theory_id)

    # ensure family diversity
    by_family: dict[str, list[scoring.TheoryScoreVector]] = {}
    for s in scores:
        by_family.setdefault(s.family, []).append(s)
    for fam in list(by_family)[:min_families]:
        best = max(by_family[fam], key=lambda s: s.display_score)
        if best.theory_id not in keep_ids:
            keep_ids.append(best.theory_id)

    # fill remaining slots by display score (anti-collapse: cap per family)
    ranked = sorted(scores, key=lambda s: s.display_score, reverse=True)
    per_family_cap = max(2, population_size // max(len(by_family), 1) + 1)
    fam_count: dict[str, int] = {}
    for s in ranked:
        if len(keep_ids) >= population_size:
            break
        fam_count[s.family] = fam_count.get(s.family, 0)
        if s.theory_id in keep_ids:
            fam_count[s.family] += 1
            continue
        if fam_count[s.family] < per_family_cap:
            keep_ids.append(s.theory_id)
            fam_count[s.family] += 1

    # de-dup preserving order (pareto front + elites come first, so a trim keeps them)
    seen: set[str] = set()
    ordered = [tid for tid in keep_ids if not (tid in seen or seen.add(tid))]
    return [registry.get(tid) for tid in ordered[:population_size]]


def evolve(
    theories: list[TheorySpec],
    registry: TheoryRegistry,
    generations: int = 3,
    rounds: int = 1,
    min_families: int = 3,
    elites_per_family: int = 2,
    population_size: int = 12,
    optimize_budget: int = 60,
    out_dir: str | Path | None = None,
    parallel: bool = True,
    lineage_root: str | Path | None = None,
    plan_dir: str | Path | None = None,
    persist_forks: bool = False,
) -> EvolutionReport:
    """Evolve the population.

    ``lineage_root`` (e.g. ``"theories"``): if set, append each generation's result
    to ``<root>/T-NNNN_<family>/history.jsonl`` (durable, git-tracked).
    ``plan_dir`` (e.g. ``"plans/iterations"``): if set, write an auto-generated
    next-iteration optimization plan there. Both default to None so library/test
    calls never touch the repo; the CLI turns them on.
    """

    report = EvolutionReport()
    current = list(theories)
    archive: dict[str, TheorySpec] = {}
    last_scores: list = []

    for g in range(generations):
        # 1. parallel: each theory independently optimizes its own seed.
        if parallel and len(current) > 1:
            with ThreadPoolExecutor(max_workers=min(4, len(current))) as pool:
                current = list(pool.map(lambda t: _optimize_one(t, optimize_budget), current))
        else:
            current = [_optimize_one(t, optimize_budget) for t in current]
        for t in current:
            registry.add(t)

        # 2. tournament (also runs duels -> may add forks/patches to registry).
        # Durable history goes to theories/ via the ledger below, so we do not write
        # the redundant ephemeral per-event log here.
        tour: TournamentReport = run_tournament(
            current, registry, rounds=rounds, generation=g, parallel=parallel,
        )

        last_scores = tour.scores

        # 3. archive valid + novel theories.
        for s in tour.scores:
            if s.validity >= 1.0 and s.novelty >= 0.5:
                archive[s.theory_id] = registry.get(s.theory_id)

        # 3b. durable per-lineage history (git-tracked) when requested.
        if lineage_root is not None:
            events_by_theory: dict[str, list] = {}
            for duel in tour.duels:
                for rd in duel.rounds:
                    for ev in rd.patch_events:
                        events_by_theory.setdefault(ev.theory_id, []).append(ev)
            for s in tour.scores:
                append_history(
                    registry.get(s.theory_id), g, s,
                    events_by_theory.get(s.theory_id, []),
                    root=lineage_root, persist_spec=persist_forks,
                )

        # 4. anti-collapse selection of next generation.
        all_current = registry.all()
        next_theories = _select_next_generation(
            tour.scores, registry, min_families, elites_per_family, population_size
        )

        report.generations.append(
            GenerationSnapshot(
                generation=g,
                theory_ids=[t.theory_id for t in all_current],
                families=sorted({t.family for t in all_current}),
                pareto_front=tour.pareto_front,
                family_elites=tour.family_elites,
                display_ranking=sorted(
                    [(s.theory_id, round(s.display_score, 4)) for s in tour.scores],
                    key=lambda x: x[1],
                    reverse=True,
                ),
            )
        )
        current = next_theories

    report.final_theory_ids = [t.theory_id for t in current]
    report.final_families = sorted({t.family for t in current})
    report.archive_ids = list(archive)

    if plan_dir is not None and report.generations:
        report.iteration_plan = str(
            write_iteration_plan(
                last_scores, registry, report.generations[-1].pareto_front,
                plan_dir, report.generations[-1].generation,
            )
        )

    if out_dir is not None:
        _write(report, Path(out_dir))
    return report


def _write(report: EvolutionReport, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "evolution_report.json").write_text(
        json.dumps(report.model_dump(), indent=2, ensure_ascii=False), encoding="utf-8"
    )
    lines = [
        "# GenesisArena Parallel Evolution Report",
        "",
        f"- allow_merge: **{report.allow_merge}** (theories are never merged)",
        f"- final families: **{', '.join(report.final_families)}**",
        f"- final theories: {', '.join(report.final_theory_ids)}",
        f"- novelty archive: {', '.join(report.archive_ids) or '(none)'}",
        "",
    ]
    for snap in report.generations:
        lines += [
            f"## Generation {snap.generation}",
            f"- families ({len(snap.families)}): {', '.join(snap.families)}",
            f"- Pareto front: {', '.join(snap.pareto_front)}",
            "- display ranking: "
            + ", ".join(f"{tid}={sc}" for tid, sc in snap.display_ranking[:8]),
            "",
        ]
    (out_dir / "evolution_report.md").write_text("\n".join(lines), encoding="utf-8")
