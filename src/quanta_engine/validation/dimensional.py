"""Basic dimensional sanity checks for known physical quantities."""

from quanta_engine.core.schema import UniverseConfig


def dimensional_issues(config: UniverseConfig) -> list[str]:
    issues: list[str] = []
    if config.constants.c <= 0:
        issues.append("speed of light c must be positive in m/s")
    if config.constants.hbar <= 0:
        issues.append("hbar must be positive in J s")
    if config.cosmology.H0_km_s_Mpc <= 0:
        issues.append("H0 must be positive in km/s/Mpc")
    return issues
