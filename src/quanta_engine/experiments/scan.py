"""Parameter scans across effective universes."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from quanta_engine.core.schema import UniverseConfig, load_config
from quanta_engine.pipeline import run_universe_pipeline


def _set_parameter(config: UniverseConfig, parameter_path: str, value: float) -> None:
    parts = parameter_path.split(".")
    if len(parts) < 2 or any(not part for part in parts):
        raise ValueError("parameter path must contain a section and field")
    target: object = config
    for part in parts[:-1]:
        if not hasattr(target, part):
            raise ValueError(f"unknown parameter path: {parameter_path}")
        target = getattr(target, part)
    field = parts[-1]
    if not hasattr(target, field):
        raise ValueError(f"unknown parameter path: {parameter_path}")
    setattr(target, field, value)


def scan_parameter(
    base_config_path: str | Path,
    parameter_path: str,
    values: Iterable[float],
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    base = load_config(base_config_path)
    for value in values:
        config = base.model_copy(deep=True)
        _set_parameter(config, parameter_path, float(value))
        report = run_universe_pipeline(config)
        rows.append(
            {
                "parameter": parameter_path,
                "value": float(value),
                "stable_hydrogen": report.atomic_report.stable_hydrogen,
                "binding_energy_eV": report.atomic_report.binding_energy_eV,
                "stellar_lifetime_years": report.stellar_report.characteristic_stellar_lifetime_years,
                "structure_growth_possible": report.structure_report.structure_growth_possible,
                "life_window_score": report.complexity_report.life_window_score,
                "civilization_potential_score": report.complexity_report.civilization_potential_score,
                "final_verdict": report.final_verdict,
            }
        )
    return pd.DataFrame(rows)


def _markdown_table(frame: pd.DataFrame) -> str:
    columns = list(frame.columns)
    header = "| " + " | ".join(columns) + " |"
    separator = "|" + "|".join("---" for _ in columns) + "|"
    rows = [
        "| "
        + " | ".join(f"{value:.6g}" if isinstance(value, float) else str(value) for value in row)
        + " |"
        for row in frame.itertuples(index=False, name=None)
    ]
    return "\n".join([header, separator, *rows])


def save_scan_artifacts(
    frame: pd.DataFrame,
    csv_path: str | Path,
    parameter_path: str,
) -> dict[str, Path]:
    csv_target = Path(csv_path)
    csv_target.parent.mkdir(parents=True, exist_ok=True)
    png_target = csv_target.with_suffix(".png")
    markdown_target = csv_target.with_suffix(".md")
    frame.to_csv(csv_target, index=False)

    fig, ax = plt.subplots(figsize=(8, 5), constrained_layout=True)
    ax.plot(frame["value"], frame["life_window_score"], marker="o", label="life window")
    ax.plot(
        frame["value"],
        frame["civilization_potential_score"],
        marker="s",
        label="civilization window",
    )
    ax.set_xlabel(parameter_path)
    ax.set_ylabel("feasibility score")
    ax.set_ylim(-0.02, 1.02)
    ax.grid(alpha=0.25)
    ax.legend()
    fig.savefig(png_target, dpi=160)
    plt.close(fig)

    markdown_target.write_text(
        f"# Parameter Scan: {parameter_path}\n\n{_markdown_table(frame)}\n\n"
        "> Scores are physical-feasibility heuristics, not occurrence probabilities.\n",
        encoding="utf-8",
    )
    return {"csv": csv_target, "plot": png_target, "markdown": markdown_target}
