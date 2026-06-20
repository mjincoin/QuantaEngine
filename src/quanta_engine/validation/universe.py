"""Cross-section physical consistency checks."""

from quanta_engine.core.schema import UniverseConfig

from .conservation import density_budget
from .dimensional import dimensional_issues
from .report import ValidationReport


def validate_universe_config(config: UniverseConfig) -> ValidationReport:
    """Return errors and warnings without raising on implausible physics."""

    report = ValidationReport()
    for issue in dimensional_issues(config):
        report.add_error(issue)
    if config.constants.G <= 0:
        report.add_error("gravitational constant G must be positive")
    if config.constants.k_B <= 0:
        report.add_error("Boltzmann constant k_B must be positive")

    masses = {
        "electron mass": config.particles.electron_mass_MeV,
        "proton mass": config.particles.proton_mass_MeV,
        "neutron mass": config.particles.neutron_mass_MeV,
        "pion mass": config.particles.pion_mass_MeV,
    }
    for name, value in masses.items():
        if value <= 0:
            report.add_error(f"{name} must be positive")

    alpha = config.effective_alpha
    if alpha <= 0:
        report.add_error("effective alpha must be positive")
    elif alpha >= 1:
        report.add_error("effective alpha must be below 1 for the hydrogenic model")
    elif alpha > 0.2:
        report.add_warning("effective alpha is outside the calibrated stellar toy-model range")

    densities = {
        "omega_r": config.cosmology.omega_r,
        "omega_b": config.cosmology.omega_b,
        "omega_cdm": config.cosmology.omega_cdm,
        "omega_lambda": config.cosmology.omega_lambda,
    }
    for name, value in densities.items():
        if value < 0:
            report.add_error(f"{name} must be non-negative")
    total = density_budget(config)
    closure_error = abs(total - 1.0)
    report.add_score("density_closure", 1.0 - closure_error)
    if closure_error > 0.05:
        report.add_warning(f"cosmic density budget differs from unity by {closure_error:.3g}")

    if config.nuclear.deuteron_binding_MeV <= 0:
        report.add_error("deuteron binding energy must be positive for standard nucleosynthesis")
    if config.nuclear.helium4_binding_MeV <= 0:
        report.add_error("helium-4 binding energy must be positive")
    if config.stellar.min_lifetime_years_for_complexity <= 0:
        report.add_error("minimum stellar lifetime must be positive")
    if config.cosmology.primordial_amplitude < 0:
        report.add_error("primordial amplitude must be non-negative")

    report.add_score("atomic_coupling", 1.0 if 0 < alpha < 1 else 0.0)
    report.add_score("positive_masses", 1.0 if all(value > 0 for value in masses.values()) else 0.0)
    return report
