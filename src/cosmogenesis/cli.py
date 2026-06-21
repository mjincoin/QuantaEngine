"""CLI for the GenesisArena parallel adversarial platform."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from .arena import evolve, load_theory, run_tournament, scoring
from .arena.registry import TheoryRegistry

app = typer.Typer(
    name="genesis-arena",
    help="Parallel multi-theory adversarial universe generation (no merging).",
    no_args_is_help=True,
)
console = Console()

_THEORIES_DIR = "theories"


def _registry() -> TheoryRegistry:
    return TheoryRegistry.from_dir(_THEORIES_DIR)


@app.command("theory-list")
def theory_list() -> None:
    reg = _registry()
    table = Table("Theory", "Family", "Version", "Engine", "Parent")
    for t in reg.all():
        table.add_row(t.theory_id, t.family, t.version, t.engine, t.parent_id or "-")
    console.print(table)


@app.command("theory-show")
def theory_show(theory_id: str) -> None:
    t = _registry().get(theory_id)
    console.print(t.model_dump())


@app.command("score")
def score() -> None:
    reg = _registry()
    table = Table("Theory", "Family", "valid", "consist", "bench", "gen", "robust", "simpl", "display")
    for t in reg.all():
        s = scoring.score_theory(t)
        table.add_row(
            t.theory_id, t.family, f"{s.validity:.2f}", f"{s.physical_consistency:.2f}",
            f"{s.benchmark_fit:.2f}", f"{s.generative_power:.2f}", f"{s.robustness:.2f}",
            f"{s.simplicity:.2f}", f"{s.display_score:.3f}",
        )
    console.print(table)


@app.command("duel")
def duel(
    theory_a: Annotated[Path, typer.Argument(exists=True, dir_okay=False)],
    theory_b: Annotated[Path, typer.Argument(exists=True, dir_okay=False)],
    rounds: Annotated[int, typer.Option("--rounds")] = 1,
) -> None:
    from .arena import run_duel

    reg = _registry()
    a, b = load_theory(theory_a), load_theory(theory_b)
    reg.add(a)
    reg.add(b)
    report = run_duel(a, b, reg, rounds=rounds)
    console.print(f"Duel {a.theory_id} vs {b.theory_id}: allow_merge={report.allow_merge}")
    for rd in report.rounds:
        console.print(
            f"  round {rd.round_id}: {len(rd.challenges)} challenges, "
            f"{len(rd.patch_events)} patch-events"
        )
        for ev in rd.patch_events:
            console.print(f"    [{ev.outcome.value}] {ev.theory_id}: {ev.summary}")
    console.print(f"merged_theory_id: {report.merged_theory_id} (always None)")


@app.command("tournament")
def tournament(
    rounds: Annotated[int, typer.Option("--rounds")] = 1,
    out: Annotated[Path | None, typer.Option("--out")] = None,
) -> None:
    reg = _registry()
    report = run_tournament(reg.all(), reg, rounds=rounds, history_dir=str(out / "history") if out else None)
    console.print(f"Pareto front: {report.pareto_front}")
    console.print(f"Family elites: {report.family_elites}")


@app.command("evolve")
def evolve_cmd(
    generations: Annotated[int, typer.Option("--generations")] = 3,
    rounds: Annotated[int, typer.Option("--rounds")] = 1,
    min_families: Annotated[int, typer.Option("--min-families")] = 3,
    elites_per_family: Annotated[int, typer.Option("--elites-per-family")] = 2,
    population_size: Annotated[int, typer.Option("--population-size")] = 12,
    out: Annotated[Path | None, typer.Option("--out")] = None,
    no_merge: Annotated[bool, typer.Option("--no-merge/--allow-merge")] = True,
    record: Annotated[
        bool, typer.Option("--record/--no-record", help="Append per-lineage history.jsonl.")
    ] = True,
    persist_forks: Annotated[
        bool, typer.Option("--persist-forks", help="Also write theory.yaml for new forks.")
    ] = False,
) -> None:
    assert no_merge, "merging is not supported by design"
    reg = _registry()
    report = evolve(
        reg.all(), reg, generations=generations, rounds=rounds, min_families=min_families,
        elites_per_family=elites_per_family, population_size=population_size, out_dir=out,
        lineage_root=(_THEORIES_DIR if record else None),
        plan_dir=("plans/iterations" if record else None),
        persist_forks=persist_forks,
    )
    console.print(f"allow_merge: {report.allow_merge}")
    console.print(f"Final families ({len(report.final_families)}): {', '.join(report.final_families)}")
    console.print(f"Final theories: {', '.join(report.final_theory_ids)}")
    console.print(f"Novelty archive: {', '.join(report.archive_ids) or '(none)'}")
    if report.iteration_plan:
        console.print(f"Next-iteration plan: {report.iteration_plan}")
    if record:
        console.print(f"Lineage history appended under: {_THEORIES_DIR}/T-*/history.jsonl")
    if out is not None:
        console.print(f"Artifacts: {out.resolve()}")


def main() -> None:
    app(prog_name="genesis-arena")


if __name__ == "__main__":
    main()
