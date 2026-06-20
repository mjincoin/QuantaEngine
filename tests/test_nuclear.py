from pathlib import Path

from quanta_engine.core.schema import load_config
from quanta_engine.nuclear.stability import compute_nuclear_stability

CONFIG = Path(__file__).parents[1] / "configs" / "standard_universe.yaml"


def test_standard_light_nuclei_are_stable():
    report = compute_nuclear_stability(load_config(CONFIG))
    assert report.deuteron_stable
    assert report.helium4_stable
    assert report.hydrogen_available
    assert report.heavy_element_seed_possible
    assert 1.2 < report.neutron_proton_mass_difference_MeV < 1.4


def test_unstable_deuteron_is_reported_without_crash():
    config = load_config(CONFIG)
    config.nuclear.deuteron_binding_MeV = -0.1
    report = compute_nuclear_stability(config)
    assert not report.deuteron_stable
    assert not report.heavy_element_seed_possible
    assert any("deuteron" in warning.lower() for warning in report.warnings)
