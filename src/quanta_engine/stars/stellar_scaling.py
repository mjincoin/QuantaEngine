"""Stellar window report assembled from transparent scaling relations."""

from dataclasses import dataclass, field

from quanta_engine.atomic.hydrogen import AtomicReport
from quanta_engine.core.schema import UniverseConfig
from quanta_engine.cosmology.friedmann import CosmologyReport
from quanta_engine.nuclear.stability import NuclearReport

from .fusion import hydrogen_fusion_possible
from .lifetime import characteristic_lifetime_years


@dataclass(slots=True)
class StellarReport:
    hydrogen_fusion_possible: bool
    long_lived_stars_possible: bool
    characteristic_stellar_lifetime_years: float
    stellar_energy_window_score: float
    heavy_element_production_possible: bool
    warnings: list[str] = field(default_factory=list)


def compute_stellar_window(
    config: UniverseConfig,
    atomic_report: AtomicReport,
    nuclear_report: NuclearReport,
    cosmology_report: CosmologyReport,
) -> StellarReport:
    """Evaluate a habitability heuristic, not a stellar-evolution model."""

    lifetime = characteristic_lifetime_years(config)
    fusion = hydrogen_fusion_possible(config, atomic_report, nuclear_report)
    long_lived = lifetime > config.stellar.min_lifetime_years_for_complexity
    heavy_elements = fusion and nuclear_report.helium4_stable and lifetime > 1.0e6
    lifetime_score = min(
        1.0, lifetime / max(abs(config.stellar.min_lifetime_years_for_complexity), 1.0)
    )
    age_score = min(1.0, cosmology_report.age_of_universe_Gyr / 1.0)
    score = (
        (0.6 * float(fusion) + 0.3 * lifetime_score + 0.1 * age_score)
        if fusion
        else 0.1 * lifetime_score
    )
    warnings: list[str] = []
    if not fusion:
        warnings.append("hydrogen fusion is unavailable under the MVP criteria")
    if not long_lived:
        warnings.append("characteristic stellar lifetime is below the complexity threshold")
    if not heavy_elements:
        warnings.append("stellar heavy-element production is suppressed")
    return StellarReport(fusion, long_lived, lifetime, min(1.0, score), heavy_elements, warnings)
