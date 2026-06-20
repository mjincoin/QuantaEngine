"""Hydrogen properties from a reduced-mass Bohr model."""

from dataclasses import dataclass, field

from quanta_engine.core.schema import UniverseConfig
from quanta_engine.core.units import MeV_to_kg


@dataclass(slots=True)
class AtomicReport:
    bohr_radius_m: float
    binding_energy_eV: float
    rydberg_energy_eV: float
    electron_velocity_over_c: float
    stable_hydrogen: bool
    chemistry_energy_scale_eV: float
    warnings: list[str] = field(default_factory=list)


def compute_hydrogen_properties(config: UniverseConfig) -> AtomicReport:
    alpha = config.effective_alpha
    electron = config.particles.electron_mass_MeV
    proton = config.particles.proton_mass_MeV
    warnings: list[str] = []

    masses_valid = electron > 0 and proton > 0 and proton > electron
    if not masses_valid:
        warnings.append(
            "positive electron and proton masses with proton heavier than electron are required"
        )
    if alpha <= 0:
        warnings.append("alpha must be positive")
    if alpha >= 1:
        warnings.append("alpha is supercritical for the non-relativistic hydrogenic model")

    safe_electron = max(abs(electron), 1e-30)
    safe_proton = max(abs(proton), 1e-30)
    reduced_mass_MeV = safe_electron * safe_proton / (safe_electron + safe_proton)
    reduced_mass_kg = MeV_to_kg(reduced_mass_MeV)
    safe_alpha = max(abs(alpha), 1e-30)
    safe_hbar = max(abs(config.constants.hbar), 1e-99)
    safe_c = max(abs(config.constants.c), 1e-30)
    bohr_radius = safe_hbar / (reduced_mass_kg * safe_c * safe_alpha)
    binding_energy = 0.5 * reduced_mass_MeV * 1.0e6 * safe_alpha**2
    stable = masses_valid and 0 < alpha < 1 and bohr_radius > 0 and binding_energy > 0
    return AtomicReport(
        bohr_radius_m=bohr_radius,
        binding_energy_eV=binding_energy,
        rydberg_energy_eV=binding_energy,
        electron_velocity_over_c=abs(alpha),
        stable_hydrogen=stable,
        chemistry_energy_scale_eV=binding_energy,
        warnings=warnings,
    )
