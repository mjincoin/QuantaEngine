import math

from quanta_engine.core.units import (
    J_to_eV,
    MeV_to_kg,
    Mpc_to_meter,
    eV_to_J,
    kg_to_MeV,
    scale_value,
    year_to_second,
)


def test_energy_conversions_round_trip():
    assert math.isclose(J_to_eV(eV_to_J(13.6)), 13.6, rel_tol=1e-12)


def test_mass_conversions_round_trip():
    assert math.isclose(kg_to_MeV(MeV_to_kg(938.27208816)), 938.27208816, rel_tol=1e-12)


def test_time_distance_and_scale_helpers():
    assert year_to_second(1.0) == 31_557_600.0
    assert math.isclose(Mpc_to_meter(1.0), 3.085677581491367e22, rel_tol=1e-12)
    assert scale_value(4.0, 1.5) == 6.0
