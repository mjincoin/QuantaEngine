"""Typer command-line interface for the effective universe pipeline."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from quanta_engine import __version__
from quanta_engine.core.schema import load_config
from quanta_engine.experiments.compare import compare_universes
from quanta_engine.experiments.scan import save_scan_artifacts, scan_parameter
from quanta_engine.pipeline import run_universe_pipeline
from quanta_engine.validation.universe import validate_universe_config

app = typer.Typer(
    name="quanta",
    help="Generate and compare universes through transparent effective-physics layers.",
    no_args_is_help=True,
)
console = Console()


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"QuantaEngine {__version__}")
        raise typer.Exit()


@app.callback()
def root(
    version: Annotated[
        bool,
        typer.Option(
            "--version", callback=_version_callback, is_eager=True, help="Show version and exit."
        ),
    ] = False,
) -> None:
    """Compile fundamental parameters into an interpretable universe report."""


@app.command("validate-config")
def validate_config(config: Annotated[Path, typer.Argument(exists=True, dir_okay=False)]) -> None:
    report = validate_universe_config(load_config(config))
    console.print(f"Passed: {report.passed}")
    for error in report.errors:
        console.print(f"[red]ERROR[/red] {error}")
    for warning in report.warnings:
        console.print(f"[yellow]WARNING[/yellow] {warning}")
    if not report.passed:
        raise typer.Exit(code=1)


@app.command()
def run(
    config: Annotated[Path, typer.Argument(exists=True, dir_okay=False)],
    output: Annotated[
        Path | None, typer.Option("--output", "-o", help="Markdown report path.")
    ] = None,
    json_output: Annotated[Path | None, typer.Option("--json", help="JSON report path.")] = None,
) -> None:
    report = run_universe_pipeline(config)
    report.write(output, json_output)
    if output is None and json_output is None:
        console.print(report.to_markdown())
    else:
        console.print(f"Universe: {report.config.universe.name}")
        console.print(f"Final verdict: {report.final_verdict}")
        if output is not None:
            console.print(f"Markdown: {output.resolve()}")
        if json_output is not None:
            console.print(f"JSON: {json_output.resolve()}")
    if not report.validation_report.passed:
        raise typer.Exit(code=1)


@app.command()
def compare(
    config_a: Annotated[Path, typer.Argument(exists=True, dir_okay=False)],
    config_b: Annotated[Path, typer.Argument(exists=True, dir_okay=False)],
) -> None:
    comparison = compare_universes(config_a, config_b)
    table = Table("Metric", "Universe A", "Universe B", "Delta")
    for metric, values in comparison.items():
        table.add_row(metric, str(values["a"]), str(values["b"]), str(values.get("delta", "-")))
    console.print(table)


@app.command()
def scan(
    config: Annotated[Path, typer.Argument(exists=True, dir_okay=False)],
    parameter: Annotated[str, typer.Option("--param", help="Dotted parameter path.")],
    values: Annotated[str, typer.Option("--values", help="Comma-separated numeric values.")],
    output: Annotated[Path | None, typer.Option("--output", "-o", help="CSV output path.")] = None,
) -> None:
    try:
        parsed_values = [float(value.strip()) for value in values.split(",") if value.strip()]
    except ValueError as exc:
        raise typer.BadParameter("--values must contain numbers") from exc
    if not parsed_values:
        raise typer.BadParameter("--values must not be empty")
    frame = scan_parameter(config, parameter, parsed_values)
    if output is None:
        console.print(frame.to_string(index=False))
    else:
        paths = save_scan_artifacts(frame, output, parameter)
        for kind, path in paths.items():
            console.print(f"{kind}: {path.resolve()}")


def main() -> None:
    app(prog_name="quanta")
