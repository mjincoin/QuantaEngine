import json
from pathlib import Path

from quanta_engine.pipeline import run_universe_pipeline

CONFIGS = Path(__file__).parents[1] / "configs"


def test_standard_universe_pipeline_and_reports(tmp_path: Path):
    report = run_universe_pipeline(CONFIGS / "standard_universe.yaml")
    assert report.validation_report.passed
    assert report.final_verdict != "invalid"
    assert report.atomic_report.stable_hydrogen
    assert report.nuclear_report.deuteron_stable
    assert report.stellar_report.hydrogen_fusion_possible
    assert report.structure_report.structure_growth_possible

    markdown_path = tmp_path / "standard.md"
    json_path = tmp_path / "standard.json"
    report.write(markdown_path, json_path)
    assert "# Universe Report: standard_universe" in markdown_path.read_text(encoding="utf-8")
    data = json.loads(json_path.read_text(encoding="utf-8"))
    assert data["final_verdict"] == report.final_verdict
    assert data["atomic"]["stable_hydrogen"] is True


def test_strong_alpha_changes_atomic_scale():
    standard = run_universe_pipeline(CONFIGS / "standard_universe.yaml")
    strong = run_universe_pipeline(CONFIGS / "strong_alpha_universe.yaml")
    assert strong.atomic_report.bohr_radius_m < standard.atomic_report.bohr_radius_m
    assert strong.atomic_report.binding_energy_eV > standard.atomic_report.binding_energy_eV


def test_pathological_universes_complete_without_crashing():
    atomless = run_universe_pipeline(CONFIGS / "no_stable_atoms_universe.yaml")
    strong_gravity = run_universe_pipeline(CONFIGS / "strong_gravity_universe.yaml")
    smooth = run_universe_pipeline(CONFIGS / "no_perturbations_universe.yaml")
    assert not atomless.atomic_report.stable_hydrogen
    assert not strong_gravity.stellar_report.long_lived_stars_possible
    assert not smooth.structure_report.structure_growth_possible
