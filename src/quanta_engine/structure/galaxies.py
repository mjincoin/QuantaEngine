"""Galaxy formation criterion."""

from quanta_engine.core.schema import UniverseConfig


def dark_energy_allows_galaxies(config: UniverseConfig) -> bool:
    matter = config.cosmology.omega_b + config.cosmology.omega_cdm
    dark_energy = config.cosmology.omega_lambda * config.dimensionless.cosmological_constant_scale
    return matter > 0 and dark_energy < 10.0 * matter
