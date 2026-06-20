"""analytic_compiler engine: forward closed-form effective-physics compiler.

Wraps quanta_engine's transparent layer pipeline; hard windows, white-box.
Adversarial I/O: ParameterVector -> UniverseAssessment.
"""

from __future__ import annotations

from quanta_engine.core.schema import UniverseConfig
from quanta_engine.pipeline import run_universe_pipeline

from ...core import BaseEngine, ParameterVector, UniverseAssessment, apply_vector
from .optimizer import coordinate_ascent

SCHEME_NAME = "analytic_compiler"


class AnalyticCompiler(BaseEngine):
    name = SCHEME_NAME

    def __init__(self, base_config: UniverseConfig) -> None:
        super().__init__(base_config)

    def assess(self, vector: ParameterVector) -> UniverseAssessment:
        config = apply_vector(self.base_config, vector)
        report = run_universe_pipeline(config)
        c = report.complexity_report
        margins = {
            "chemistry": c.chemistry_score,
            "energy": c.energy_gradient_score,
            "stability": c.stability_score,
            "elements": c.element_diversity_score,
            "life": c.life_window_score,
            "civilization": c.civilization_potential_score,
        }
        warnings = list(report.validation_report.errors)
        for rep in (
            report.atomic_report,
            report.nuclear_report,
            report.cosmology_report,
            report.stellar_report,
            report.structure_report,
        ):
            warnings.extend(getattr(rep, "warnings", []))
        return UniverseAssessment(
            scheme=self.name,
            score=c.civilization_potential_score,
            feasible=report.validation_report.passed and report.final_verdict != "sterile",
            margins=margins,
            residual=0.0,  # this paradigm performs no cross-layer self-consistency check
            diagnostics={
                "verdict": report.final_verdict,
                "stable_hydrogen": report.atomic_report.stable_hydrogen,
                "deuteron_stable": report.nuclear_report.deuteron_stable,
                "helium4_stable": report.nuclear_report.helium4_stable,
                "fusion": report.stellar_report.hydrogen_fusion_possible,
                "long_lived_stars": report.stellar_report.long_lived_stars_possible,
                "stellar_lifetime_years": report.stellar_report.characteristic_stellar_lifetime_years,
                "age_Gyr": report.cosmology_report.age_of_universe_Gyr,
                "structure": report.structure_report.structure_growth_possible,
                "planets": report.structure_report.planet_formation_possible,
                "hard_window_failures": self._hard_failures(report),
            },
            warnings=warnings,
        )

    @staticmethod
    def _hard_failures(report) -> float:
        windows = [
            report.atomic_report.stable_hydrogen,
            report.nuclear_report.deuteron_stable,
            report.nuclear_report.helium4_stable,
            report.stellar_report.hydrogen_fusion_possible,
            report.stellar_report.long_lived_stars_possible,
            report.structure_report.structure_growth_possible,
            report.structure_report.planet_formation_possible,
        ]
        return 1.0 - sum(bool(w) for w in windows) / len(windows)

    def hard_window_failures(self, vector: ParameterVector) -> float:
        """Fraction of hard windows that fail (used by the arena's verifier)."""

        return float(self.assess(vector).diagnostics["hard_window_failures"])

    def optimize(self, start: ParameterVector, budget: int = 70) -> ParameterVector:
        best = coordinate_ascent(self, start, budget=budget)
        self.last_champion = best
        return best
