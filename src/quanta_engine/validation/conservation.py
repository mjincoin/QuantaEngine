"""Density-budget consistency helpers."""

from quanta_engine.core.schema import UniverseConfig


def density_budget(config: UniverseConfig) -> float:
    curvature = config.spacetime.curvature_k or 0.0
    return (
        config.cosmology.omega_r
        + config.cosmology.omega_b
        + config.cosmology.omega_cdm
        + config.cosmology.omega_lambda
        + curvature
    )
