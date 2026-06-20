"""Dimensional metadata helpers for report annotations."""

UNITS = {
    "bohr_radius_m": "m",
    "binding_energy_eV": "eV",
    "mass_MeV": "MeV/c^2",
    "age_of_universe_s": "s",
    "stellar_lifetime_years": "yr",
}


def unit_for(quantity: str) -> str:
    return UNITS.get(quantity, "dimensionless")
