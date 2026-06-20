from dataclasses import replace
from pathlib import Path

from quanta_engine.atomic.hydrogen import compute_hydrogen_properties
from quanta_engine.core.schema import load_config
from quanta_engine.cosmology.friedmann import compute_friedmann_background
from quanta_engine.nuclear.stability import compute_nuclear_stability
from quanta_engine.stars.stellar_scaling import compute_stellar_window
from quanta_engine.structure.halos import compute_structure_window

CONFIG = Path(__file__).parents[1] / "configs" / "standard_universe.yaml"


def _inputs(config):
    atomic = compute_hydrogen_properties(config)
    nuclear = compute_nuclear_stability(config)
    cosmology = compute_friedmann_background(config)
    stellar = compute_stellar_window(config, atomic, nuclear, cosmology)
    return cosmology, stellar


def test_standard_universe_forms_structures_and_planets():
    config = load_config(CONFIG)
    report = compute_structure_window(config, *_inputs(config))
    assert report.structure_growth_possible
    assert report.galaxy_formation_possible
    assert report.planet_formation_possible


def test_zero_primordial_amplitude_stops_structure_growth():
    config = load_config(CONFIG)
    config.cosmology.primordial_amplitude = 0.0
    report = compute_structure_window(config, *_inputs(config))
    assert not report.structure_growth_possible
    assert not report.galaxy_formation_possible


def test_no_heavy_elements_stops_planet_formation():
    config = load_config(CONFIG)
    cosmology, stellar = _inputs(config)
    stellar = replace(stellar, heavy_element_production_possible=False)
    report = compute_structure_window(config, cosmology, stellar)
    assert report.galaxy_formation_possible
    assert not report.planet_formation_possible
