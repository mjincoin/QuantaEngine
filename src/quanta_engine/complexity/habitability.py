"""Documented combinations of physical feasibility indicators."""

from dataclasses import dataclass

from quanta_engine.atomic.chemistry_window import chemistry_window_score
from quanta_engine.atomic.hydrogen import AtomicReport
from quanta_engine.core.schema import UniverseConfig
from quanta_engine.cosmology.friedmann import CosmologyReport
from quanta_engine.nuclear.stability import NuclearReport
from quanta_engine.stars.stellar_scaling import StellarReport
from quanta_engine.structure.halos import StructureReport

from .civilization import civilization_potential_score
from .life_window import life_window_score


@dataclass(slots=True)
class ComplexityReport:
    chemistry_score: float
    energy_gradient_score: float
    stability_score: float
    element_diversity_score: float
    life_window_score: float
    civilization_potential_score: float
    qualitative_summary: str


def _summary(
    chemistry: float, energy: float, elements: float, life: float, civilization: float
) -> str:
    if civilization >= 0.7:
        return "civilization window plausible"
    if life >= 0.6:
        return "life window plausible"
    if chemistry >= 0.5 and elements >= 0.5:
        return "complex chemistry possible"
    if energy > 0:
        return "stellar but chemically poor"
    if chemistry > 0:
        return "simple atoms only"
    return "sterile"


def compute_complexity_report(
    config: UniverseConfig,
    atomic_report: AtomicReport,
    nuclear_report: NuclearReport,
    cosmology_report: CosmologyReport,
    stellar_report: StellarReport,
    structure_report: StructureReport,
) -> ComplexityReport:
    """Score physical windows; these values are not probabilities of life."""

    chemistry = chemistry_window_score(
        atomic_report.stable_hydrogen,
        atomic_report.binding_energy_eV,
        atomic_report.bohr_radius_m,
    )
    energy = 0.5 * float(stellar_report.hydrogen_fusion_possible) + 0.5 * float(
        stellar_report.long_lived_stars_possible
    )
    age_support = min(1.0, max(0.0, cosmology_report.age_of_universe_Gyr / 10.0))
    lifetime_support = min(
        1.0,
        max(
            0.0,
            stellar_report.characteristic_stellar_lifetime_years
            / max(config.stellar.min_lifetime_years_for_complexity, 1.0),
        ),
    )
    stability = (
        sum(
            [
                float(atomic_report.stable_hydrogen),
                float(nuclear_report.deuteron_stable),
                float(nuclear_report.helium4_stable),
                age_support,
                lifetime_support,
            ]
        )
        / 5.0
    )
    elements = 0.5 * float(stellar_report.heavy_element_production_possible) + 0.5 * float(
        structure_report.planet_formation_possible
    )
    structures = float(structure_report.structure_growth_possible)
    life = life_window_score(chemistry, energy, stability, elements, structures)
    civilization = civilization_potential_score(
        life,
        stability,
        energy,
        float(
            structure_report.planet_formation_possible and structure_report.stable_orbits_possible
        ),
    )
    return ComplexityReport(
        chemistry_score=chemistry,
        energy_gradient_score=energy,
        stability_score=stability,
        element_diversity_score=elements,
        life_window_score=life,
        civilization_potential_score=civilization,
        qualitative_summary=_summary(chemistry, energy, elements, life, civilization),
    )
