"""Parallel multi-lineage evolution. No merging, no single winner, anti-collapse."""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from pydantic import BaseModel, Field

from ..core import code_revision, object_fingerprint, software_version, stable_identifier
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


class ConvergenceMetrics(BaseModel):
    generation: int
    pareto_stable: bool
    families_stable: bool
    max_display_score_delta: float | None = None
    stable: bool


class EvolutionReport(BaseModel):
    run_id: str
    run_seed: int = 0
    software_version: str
    code_revision: str | None = None
    generations: list[GenerationSnapshot] = Field(default_factory=list)
    final_theory_ids: list[str] = Field(default_factory=list)
    final_families: list[str] = Field(default_factory=list)
    archive_ids: list[str] = Field(default_factory=list)
    novelty_feature_count: int = 0
    novelty_feature_capacity: int = 0
    requested_generations: int = 0
    completed_generations: int = 0
    stopped_early: bool = False
    convergence_reason: str | None = None
    convergence_metrics: list[ConvergenceMetrics] = Field(default_factory=list)
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
    ordered = []
    for theory_id in keep_ids:
        if theory_id not in seen:
            seen.add(theory_id)
            ordered.append(theory_id)
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
    run_seed: int = 0,
    novelty_threshold: float = 0.4,
    novelty_archive_capacity: int = 128,
    novelty_max_age_generations: int = 8,
    novelty_dedup_decimals: int = 8,
    early_stopping: bool = False,
    convergence_patience: int = 2,
    score_delta_tolerance: float = 1.0e-4,
) -> EvolutionReport:
    """Evolve the population.

    ``lineage_root`` (e.g. ``"theories"``): if set, append each generation's result
    to ``<root>/T-NNNN_<family>/history.jsonl`` (durable, git-tracked).
    ``plan_dir`` (e.g. ``"plans/iterations"``): if set, write an auto-generated
    next-iteration optimization plan there. Both default to None so library/test
    calls never touch the repo; the CLI turns them on.
    """

    run_id = stable_identifier(
        "RUN",
        run_seed,
        [(theory.theory_id, object_fingerprint(theory)) for theory in theories],
        generations,
        rounds,
        min_families,
        elites_per_family,
        population_size,
        optimize_budget,
        novelty_archive_capacity,
        novelty_max_age_generations,
        novelty_dedup_decimals,
        early_stopping,
        convergence_patience,
        score_delta_tolerance,
    )
    revision_root = Path(lineage_root).resolve().parent if lineage_root is not None else None
    report = EvolutionReport(
        run_id=run_id,
        run_seed=run_seed,
        software_version=software_version(),
        code_revision=code_revision(revision_root),
        novelty_feature_capacity=novelty_archive_capacity,
        requested_generations=generations,
    )
    current = list(theories)
    archive: dict[str, TheorySpec] = {}
    novelty_archive = scoring.NoveltyArchive(
        capacity=novelty_archive_capacity,
        max_age_generations=novelty_max_age_generations,
        dedup_decimals=novelty_dedup_decimals,
    )
    last_scores: list = []
    previous_pareto: set[str] | None = None
    previous_families: set[str] | None = None
    previous_best_score: float | None = None
    stable_generations = 0

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
            current,
            registry,
            rounds=rounds,
            generation=g,
            parallel=parallel,
            run_seed=run_seed,
            novelty_archive=novelty_archive.features(g),
        )

        last_scores = tour.scores

        # 3. archive valid + novel theories.
        for s in tour.scores:
            if s.validity >= 1.0 and s.novelty >= novelty_threshold:
                archive[s.theory_id] = registry.get(s.theory_id)
            theory = registry.get(s.theory_id)
            novelty_archive.add(
                bridge.novelty_features(theory, bridge.seed_vector(theory)), generation=g
            )

        # 3b. durable per-lineage history (git-tracked) when requested.
        if lineage_root is not None:
            events_by_theory: dict[str, list] = {}
            considerations_by_theory: dict[str, list] = {}
            for duel in tour.duels:
                for rd in duel.rounds:
                    for ev in rd.patch_events:
                        events_by_theory.setdefault(ev.theory_id, []).append(ev)
                    for co in rd.considerations:
                        considerations_by_theory.setdefault(co.target_theory_id, []).append(co)
            for s in tour.scores:
                append_history(
                    registry.get(s.theory_id),
                    g,
                    s,
                    events_by_theory.get(s.theory_id, []),
                    root=lineage_root,
                    persist_spec=persist_forks,
                    run_id=run_id,
                    run_seed=run_seed,
                    considerations=considerations_by_theory.get(s.theory_id, []),
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

        current_pareto = set(tour.pareto_front)
        current_families = {theory.family for theory in current}
        current_best_score = max((score.display_score for score in tour.scores), default=0.0)
        score_delta = (
            None if previous_best_score is None else abs(current_best_score - previous_best_score)
        )
        pareto_stable = previous_pareto is not None and current_pareto == previous_pareto
        families_stable = previous_families is not None and current_families == previous_families
        stable = (
            pareto_stable
            and families_stable
            and score_delta is not None
            and score_delta <= score_delta_tolerance
        )
        report.convergence_metrics.append(
            ConvergenceMetrics(
                generation=g,
                pareto_stable=pareto_stable,
                families_stable=families_stable,
                max_display_score_delta=score_delta,
                stable=stable,
            )
        )
        stable_generations = stable_generations + 1 if stable else 0
        previous_pareto = current_pareto
        previous_families = current_families
        previous_best_score = current_best_score
        if early_stopping and stable_generations >= max(1, convergence_patience):
            report.stopped_early = True
            report.convergence_reason = "stable_pareto_scores_and_families"
            break

    report.final_theory_ids = [t.theory_id for t in current]
    report.final_families = sorted({t.family for t in current})
    report.archive_ids = list(archive)
    report.novelty_feature_count = len(novelty_archive)
    report.completed_generations = len(report.generations)

    if plan_dir is not None and report.generations:
        report.iteration_plan = str(
            write_iteration_plan(
                last_scores,
                registry,
                report.generations[-1].pareto_front,
                plan_dir,
                report.generations[-1].generation,
                run_id=run_id,
                run_seed=run_seed,
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
        f"- run_id: `{report.run_id}`",
        f"- run_seed: `{report.run_seed}`",
        f"- software_version: `{report.software_version}`",
        f"- code_revision: `{report.code_revision or 'unknown'}`",
        f"- final families: **{', '.join(report.final_families)}**",
        f"- final theories: {', '.join(report.final_theory_ids)}",
        f"- novelty archive: {', '.join(report.archive_ids) or '(none)'}",
        f"- generations: {report.completed_generations}/{report.requested_generations}",
        f"- stopped early: {report.stopped_early}",
        f"- convergence reason: {report.convergence_reason or '(none)'}",
        f"- novelty feature memory: {report.novelty_feature_count}/{report.novelty_feature_capacity}",
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
