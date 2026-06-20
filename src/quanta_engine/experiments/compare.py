"""Key-output comparison between two universe configurations."""

from pathlib import Path
from typing import Any

from quanta_engine.pipeline import run_universe_pipeline


def compare_universes(config_a: str | Path, config_b: str | Path) -> dict[str, dict[str, Any]]:
    a = run_universe_pipeline(config_a)
    b = run_universe_pipeline(config_b)
    metrics: dict[str, tuple[Any, Any]] = {
        "atomic.binding_energy_eV": (
            a.atomic_report.binding_energy_eV,
            b.atomic_report.binding_energy_eV,
        ),
        "atomic.bohr_radius_m": (a.atomic_report.bohr_radius_m, b.atomic_report.bohr_radius_m),
        "stellar.lifetime_years": (
            a.stellar_report.characteristic_stellar_lifetime_years,
            b.stellar_report.characteristic_stellar_lifetime_years,
        ),
        "structure.growth_possible": (
            a.structure_report.structure_growth_possible,
            b.structure_report.structure_growth_possible,
        ),
        "complexity.life_window_score": (
            a.complexity_report.life_window_score,
            b.complexity_report.life_window_score,
        ),
        "complexity.civilization_potential_score": (
            a.complexity_report.civilization_potential_score,
            b.complexity_report.civilization_potential_score,
        ),
        "final_verdict": (a.final_verdict, b.final_verdict),
    }
    comparison: dict[str, dict[str, Any]] = {}
    for name, (left, right) in metrics.items():
        item = {"a": left, "b": right}
        if (
            isinstance(left, (int, float))
            and not isinstance(left, bool)
            and isinstance(right, (int, float))
        ):
            item["delta"] = right - left
        comparison[name] = item
    return comparison
