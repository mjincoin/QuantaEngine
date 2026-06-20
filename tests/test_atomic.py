from pathlib import Path

import pytest

from quanta_engine.atomic.hydrogen import compute_hydrogen_properties
from quanta_engine.core.schema import load_config

CONFIGS = Path(__file__).parents[1] / "configs"


def test_standard_hydrogen_matches_bohr_model():
    report = compute_hydrogen_properties(load_config(CONFIGS / "standard_universe.yaml"))
    assert report.stable_hydrogen
    assert report.binding_energy_eV == pytest.approx(13.6, rel=0.01)
    assert report.bohr_radius_m == pytest.approx(5.29e-11, rel=0.01)
    assert report.electron_velocity_over_c == pytest.approx(1 / 137.0, rel=0.01)


def test_supercritical_alpha_returns_unstable_warning():
    report = compute_hydrogen_properties(load_config(CONFIGS / "no_stable_atoms_universe.yaml"))
    assert not report.stable_hydrogen
    assert any("alpha" in warning.lower() for warning in report.warnings)
