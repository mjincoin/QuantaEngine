from pathlib import Path

from quanta_engine.atomic.hydrogen import compute_hydrogen_properties
from quanta_engine.core.schema import load_config
from quanta_engine.cosmology.friedmann import compute_friedmann_background
from quanta_engine.nuclear.stability import compute_nuclear_stability
from quanta_engine.stars.stellar_scaling import compute_stellar_window

CONFIG = Path(__file__).parents[1] / "configs" / "standard_universe.yaml"


def _reports(config):
    return (
        compute_hydrogen_properties(config),
        compute_nuclear_stability(config),
        compute_friedmann_background(config),
    )


def test_standard_universe_has_long_lived_fusing_stars():
    config = load_config(CONFIG)
    report = compute_stellar_window(config, *_reports(config))
    assert report.hydrogen_fusion_possible
    assert report.long_lived_stars_possible
    assert report.heavy_element_production_possible
    assert report.characteristic_stellar_lifetime_years >= 1e9


def test_no_deuteron_suppresses_fusion():
    config = load_config(CONFIG)
    config.nuclear.deuteron_binding_MeV = -1.0
    report = compute_stellar_window(config, *_reports(config))
    assert not report.hydrogen_fusion_possible


def test_strong_gravity_shortens_stellar_lifetime():
    config = load_config(CONFIG)
    config.dimensionless.gravity_scale = 100.0
    report = compute_stellar_window(config, *_reports(config))
    assert report.characteristic_stellar_lifetime_years <= 1e6
    assert not report.long_lived_stars_possible
