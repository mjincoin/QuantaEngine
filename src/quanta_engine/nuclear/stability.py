"""Light-nucleus stability checks for the MVP."""

from dataclasses import dataclass, field

from quanta_engine.core.schema import UniverseConfig


@dataclass(slots=True)
class NuclearReport:
    neutron_proton_mass_difference_MeV: float
    deuteron_stable: bool
    helium4_stable: bool
    hydrogen_available: bool
    helium_available: bool
    heavy_element_seed_possible: bool
    warnings: list[str] = field(default_factory=list)


def compute_nuclear_stability(config: UniverseConfig) -> NuclearReport:
    p = config.particles
    strong = config.dimensionless.strong_scale
    deuteron_stable = config.nuclear.deuteron_binding_MeV * strong > 0
    helium4_stable = config.nuclear.helium4_binding_MeV * strong > 0
    mass_difference = p.neutron_mass_MeV - p.proton_mass_MeV
    hydrogen_available = p.proton_mass_MeV + p.electron_mass_MeV < p.neutron_mass_MeV
    warnings: list[str] = []
    if not deuteron_stable:
        warnings.append("deuteron is unstable; ordinary stellar nucleosynthesis is suppressed")
    if mass_difference <= 0:
        warnings.append("neutron is not heavier than proton; hydrogen chemistry may be altered")
    if not helium4_stable:
        warnings.append("helium4 is unstable; heavy-element seeds are unavailable")
    if not hydrogen_available:
        warnings.append("neutral hydrogen is energetically disfavored in this toy criterion")
    return NuclearReport(
        neutron_proton_mass_difference_MeV=mass_difference,
        deuteron_stable=deuteron_stable,
        helium4_stable=helium4_stable,
        hydrogen_available=hydrogen_available,
        helium_available=helium4_stable,
        heavy_element_seed_possible=deuteron_stable and helium4_stable,
        warnings=warnings,
    )
