"""Stellar lifetime scaling used by the MVP."""

from quanta_engine.core.constants import STANDARD_STELLAR_LIFETIME_YEARS
from quanta_engine.core.schema import UniverseConfig


def characteristic_lifetime_years(config: UniverseConfig) -> float:
    gravity = max(abs(config.dimensionless.gravity_scale), 1.0e-12)
    alpha_penalty = max(1.0, abs(config.dimensionless.alpha_scale)) ** 1.5
    return STANDARD_STELLAR_LIFETIME_YEARS / (gravity**2 * alpha_penalty)
