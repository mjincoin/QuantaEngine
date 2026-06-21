"""Durable, committed long-term storage of adversarial results.

Two artifacts, both git-tracked (unlike the ephemeral ``reports/.../history``):

- ``theories/T-NNNN_<family>/history.jsonl`` -- append-only, one line per
  generation, the canonical iteration history of each lineage.
- ``plans/iterations/<stamp>.md`` -- an auto-generated next-iteration optimization
  plan recommending concrete actions per lineage.

Timestamps use the machine's local offset (Paris CET/CEST), never a hardcoded one.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from .registry import TheoryRegistry
from .scoring import TheoryScoreVector
from .theory import TheorySpec, save_theory


def local_now() -> str:
    """ISO-8601 timestamp with the local (Paris) UTC offset."""

    return datetime.now().astimezone().isoformat(timespec="seconds")


def theory_dir(theory: TheorySpec, root: str | Path) -> Path:
    """The on-disk directory for a lineage: T-NNNN_<family> under ``root``.

    Reuses an existing ``T-NNNN_*`` directory if one is present (the family can
    drift across versions), otherwise derives ``T-NNNN_<family>``.
    """

    root = Path(root)
    for existing in root.glob(f"{theory.theory_id}_*"):
        if existing.is_dir():
            return existing
    return root / f"{theory.theory_id}_{theory.family}"


def append_history(
    theory: TheorySpec,
    generation: int,
    score: TheoryScoreVector,
    events: list,
    root: str | Path,
    persist_spec: bool = False,
) -> Path | None:
    """Append one generation record to a lineage's history.jsonl.

    By default only records lineages that already exist on disk; pass
    ``persist_spec=True`` to also write a ``theory.yaml`` for new forks so they
    become durable lineages.
    """

    d = theory_dir(theory, root)
    if not d.exists():
        if not persist_spec:
            return None
        d.mkdir(parents=True, exist_ok=True)
        save_theory(theory, d / "theory.yaml")

    record = {
        "timestamp": local_now(),
        "generation": generation,
        "theory_id": theory.theory_id,
        "family": theory.family,
        "engine": theory.engine,
        "version": theory.version,
        "parent_id": theory.parent_id,
        "champion_vector": theory.seed_vector,
        "scores": {
            "validity": score.validity,
            "physical_consistency": score.physical_consistency,
            "benchmark_fit": score.benchmark_fit,
            "generative_power": score.generative_power,
            "robustness": score.robustness,
            "novelty": score.novelty,
            "simplicity": score.simplicity,
            "display": round(score.display_score, 4),
        },
        "events": [
            {
                "outcome": e.outcome.value,
                "summary": e.summary,
                "child_theory_id": e.child_theory_id,
            }
            for e in events
        ],
    }
    path = d / "history.jsonl"
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    return path


def _weakest(score: TheoryScoreVector) -> list[str]:
    objs = {
        "robustness": score.robustness,
        "benchmark_fit": score.benchmark_fit,
        "generative_power": score.generative_power,
        "physical_consistency": score.physical_consistency,
        "novelty": score.novelty,
    }
    return [k for k, _ in sorted(objs.items(), key=lambda kv: kv[1])[:2]]


def write_iteration_plan(
    scores: list[TheoryScoreVector],
    registry: TheoryRegistry,
    pareto_front: list[str],
    plans_dir: str | Path,
    generation: int,
) -> Path:
    """Generate a concrete next-iteration optimization plan and save it."""

    plans_dir = Path(plans_dir)
    plans_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().astimezone().strftime("%Y-%m-%dT%H%M%S")
    path = plans_dir / f"{stamp}_gen{generation}.md"

    lines = [
        f"# Next-iteration optimization plan (after generation {generation})",
        "",
        f"- generated: {local_now()}",
        f"- Pareto front: {', '.join(pareto_front) or '(none)'}",
        "- principle: schemes evolve in parallel and are never merged.",
        "",
        "## Per-lineage recommended actions",
        "",
    ]
    for s in sorted(scores, key=lambda x: x.display_score, reverse=True):
        theory = registry.get(s.theory_id)
        weak = _weakest(s)
        on_front = "yes" if s.theory_id in pareto_front else "no"
        rec = []
        if s.robustness < 0.5:
            rec.append("re-seed toward a more robust basin (robustness penalty)")
        if s.generative_power < 0.34:
            rec.append("broaden exploration or fork an exploratory child (low generative power)")
        if s.benchmark_fit < 0.6:
            rec.append("tighten standard-universe fit")
        if not rec:
            rec.append("hold; defend lineage and keep optimizing within paradigm")
        lines += [
            f"### {s.theory_id} ({theory.family}, {theory.engine} v{theory.version})",
            f"- on Pareto front: {on_front}; display score: {s.display_score:.3f}",
            f"- weakest objectives: {', '.join(weak)}",
            f"- next actions: {'; '.join(rec)}",
            "",
        ]
    lines += [
        "## Suggested commands",
        "```bash",
        "python -m cosmogenesis evolve --generations 3 --min-families 3 --out reports/arena",
        "```",
        "",
        "> History accrues in theories/T-NNNN_<family>/history.jsonl (git-tracked).",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
