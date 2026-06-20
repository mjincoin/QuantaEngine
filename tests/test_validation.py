from pathlib import Path

from quanta_engine.core.schema import load_config
from quanta_engine.validation.report import ValidationReport
from quanta_engine.validation.universe import validate_universe_config

CONFIG = Path(__file__).parents[1] / "configs" / "standard_universe.yaml"


def test_validation_report_helpers_and_markdown():
    report = ValidationReport()
    report.add_warning("toy warning")
    report.add_score("consistency", 0.8)
    assert report.passed
    assert "toy warning" in report.to_markdown()
    report.add_error("bad physics")
    assert not report.passed


def test_standard_universe_validation_passes():
    report = validate_universe_config(load_config(CONFIG))
    assert report.passed
    assert report.scores["density_closure"] > 0.99


def test_negative_mass_and_large_alpha_are_structured_errors():
    config = load_config(CONFIG)
    config.particles.electron_mass_MeV = -1.0
    config.dimensionless.alpha_scale = 200.0
    report = validate_universe_config(config)
    assert not report.passed
    assert any("mass" in error.lower() for error in report.errors)
    assert any("alpha" in error.lower() for error in report.errors)


def test_density_sum_mismatch_is_warning():
    config = load_config(CONFIG)
    config.cosmology.omega_lambda = 0.1
    report = validate_universe_config(config)
    assert report.passed
    assert any("density" in warning.lower() for warning in report.warnings)
