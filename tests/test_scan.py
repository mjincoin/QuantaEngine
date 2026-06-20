from pathlib import Path

from quanta_engine.experiments.compare import compare_universes
from quanta_engine.experiments.scan import save_scan_artifacts, scan_parameter

CONFIGS = Path(__file__).parents[1] / "configs"


def test_alpha_scan_returns_required_columns_and_artifacts(tmp_path: Path):
    frame = scan_parameter(
        CONFIGS / "standard_universe.yaml",
        "dimensionless.alpha_scale",
        [0.5, 1.0, 1.5],
    )
    assert len(frame) == 3
    assert {
        "binding_energy_eV",
        "stable_hydrogen",
        "life_window_score",
        "civilization_potential_score",
    } <= set(frame.columns)
    assert frame.loc[0, "binding_energy_eV"] < frame.loc[2, "binding_energy_eV"]

    paths = save_scan_artifacts(frame, tmp_path / "scan_alpha.csv", "dimensionless.alpha_scale")
    assert all(path.exists() for path in paths.values())


def test_compare_reports_key_differences():
    comparison = compare_universes(
        CONFIGS / "standard_universe.yaml",
        CONFIGS / "strong_alpha_universe.yaml",
    )
    assert comparison["atomic.binding_energy_eV"]["delta"] > 0
    assert "complexity.life_window_score" in comparison
