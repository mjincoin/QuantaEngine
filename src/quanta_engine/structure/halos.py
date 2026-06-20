"""Structure-growth window based on effective primordial perturbations."""

from dataclasses import dataclass, field
from math import sqrt

from quanta_engine.core.schema import UniverseConfig
from quanta_engine.cosmology.friedmann import CosmologyReport
from quanta_engine.stars.stellar_scaling import StellarReport

from .galaxies import dark_energy_allows_galaxies
from .planets import planet_window


@dataclass(slots=True)
class StructureReport:
    structure_growth_possible: bool
    galaxy_formation_possible: bool
    planet_formation_possible: bool
    metallicity_window_score: float
    stable_orbits_possible: bool
    effective_primordial_fluctuation: float
    warnings: list[str] = field(default_factory=list)


def compute_structure_window(
    config: UniverseConfig,
    cosmology_report: CosmologyReport,
    stellar_report: StellarReport,
) -> StructureReport:
    # Config stores a dimensionless power amplitude; its square root is the perturbation amplitude.
    fluctuation = sqrt(max(0.0, config.cosmology.primordial_amplitude))
    matter = config.cosmology.omega_b + config.cosmology.omega_cdm
    structure = (
        1.0e-7 <= fluctuation <= 1.0e-3
        and matter > 0.05
        and cosmology_report.age_of_universe_Gyr > 0.5
    )
    galaxies = structure and dark_energy_allows_galaxies(config)
    planets, stable_orbits = planet_window(
        galaxies,
        stellar_report.heavy_element_production_possible,
        config.dimensionless.gravity_scale,
    )
    metallicity = (
        1.0 if planets else 0.5 if stellar_report.heavy_element_production_possible else 0.0
    )
    warnings: list[str] = []
    if not structure:
        warnings.append(
            "primordial amplitude, matter density, or growth time blocks structure formation"
        )
    if structure and not galaxies:
        warnings.append("dark energy dominates too early for the MVP galaxy criterion")
    if galaxies and not planets:
        warnings.append("galaxies form but heavy-element support for planets is absent")
    return StructureReport(
        structure, galaxies, planets, metallicity, stable_orbits, fluctuation, warnings
    )
