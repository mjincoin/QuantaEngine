from pathlib import Path

import pytest

from quanta_engine.core.schema import load_config
from quanta_engine.cosmology.friedmann import compute_friedmann_background
from quantaengine import UniverseParams
from quantaengine.cosmology import FriedmannBackground

CONFIG = Path(__file__).parents[1] / "configs" / "standard_universe.yaml"


def test_background_expands_for_positive_density():
    params = UniverseParams(initial_scale_factor=0.01, time_step=0.001)
    bg = FriedmannBackground(params)
    a0 = bg.state.scale_factor
    bg.step(params.time_step)
    assert bg.state.scale_factor > a0
    assert bg.hubble() >= 0


def test_standard_universe_age_is_observationally_reasonable():
    report = compute_friedmann_background(load_config(CONFIG))
    assert report.age_of_universe_Gyr == pytest.approx(13.8, rel=0.08)
    assert 10.0 < report.age_of_universe_Gyr < 20.0
    assert len(report.expansion_history_sample) == 200
    assert report.accelerated_expansion


def test_low_dark_energy_disables_acceleration():
    config = load_config(CONFIG)
    config.cosmology.omega_lambda = 0.01
    report = compute_friedmann_background(config)
    assert not report.accelerated_expansion


def test_negative_density_returns_warning_instead_of_crashing():
    config = load_config(CONFIG)
    config.cosmology.omega_cdm = -0.2
    report = compute_friedmann_background(config)
    assert report.age_of_universe_Gyr > 0
    assert report.warnings
