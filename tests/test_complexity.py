from dataclasses import replace
from pathlib import Path

from quanta_engine.complexity.habitability import compute_complexity_report
from quanta_engine.pipeline import run_universe_pipeline

CONFIGS = Path(__file__).parents[1] / "configs"


def test_standard_universe_scores_high():
    report = run_universe_pipeline(CONFIGS / "standard_universe.yaml")
    assert report.complexity_report.life_window_score > 0.5
    assert report.complexity_report.civilization_potential_score > 0.5


def test_unstable_atoms_gate_life_scores_near_zero():
    report = run_universe_pipeline(CONFIGS / "no_stable_atoms_universe.yaml")
    assert report.complexity_report.chemistry_score == 0.0
    assert report.complexity_report.life_window_score < 0.1
    assert report.complexity_report.civilization_potential_score < 0.1


def test_no_stars_lowers_energy_gradient_score():
    report = run_universe_pipeline(CONFIGS / "standard_universe.yaml")
    no_stars = replace(
        report.stellar_report,
        hydrogen_fusion_possible=False,
        long_lived_stars_possible=False,
        heavy_element_production_possible=False,
    )
    complexity = compute_complexity_report(
        report.config,
        report.atomic_report,
        report.nuclear_report,
        report.cosmology_report,
        no_stars,
        report.structure_report,
    )
    assert complexity.energy_gradient_score < report.complexity_report.energy_gradient_score
