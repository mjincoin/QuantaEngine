"""Unified universe report and serializers."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from quanta_engine.atomic.hydrogen import AtomicReport
from quanta_engine.complexity.habitability import ComplexityReport
from quanta_engine.core.schema import UniverseConfig
from quanta_engine.cosmology.friedmann import CosmologyReport
from quanta_engine.fields.spectrum import ParticleSpectrum
from quanta_engine.nuclear.stability import NuclearReport
from quanta_engine.stars.stellar_scaling import StellarReport
from quanta_engine.structure.halos import StructureReport
from quanta_engine.validation.report import ValidationReport


@dataclass(slots=True)
class UniverseReport:
    config: UniverseConfig
    config_summary: dict[str, Any]
    validation_report: ValidationReport
    particle_spectrum: ParticleSpectrum
    atomic_report: AtomicReport
    nuclear_report: NuclearReport
    cosmology_report: CosmologyReport
    stellar_report: StellarReport
    structure_report: StructureReport
    complexity_report: ComplexityReport
    final_verdict: str

    def to_json_dict(self) -> dict[str, Any]:
        return {
            "universe_name": self.config.universe.name,
            "final_verdict": self.final_verdict,
            "config_summary": self.config_summary,
            "validation": asdict(self.validation_report)
            | {"passed": self.validation_report.passed},
            "particle_spectrum": self.particle_spectrum.to_list(),
            "atomic": asdict(self.atomic_report),
            "nuclear": asdict(self.nuclear_report),
            "cosmology": asdict(self.cosmology_report),
            "stellar": asdict(self.stellar_report),
            "structure": asdict(self.structure_report),
            "complexity": asdict(self.complexity_report),
        }

    def to_markdown(self) -> str:
        bottlenecks = [
            *self.validation_report.errors,
            *self.atomic_report.warnings,
            *self.nuclear_report.warnings,
            *self.cosmology_report.warnings,
            *self.stellar_report.warnings,
            *self.structure_report.warnings,
        ]
        bottleneck_text = (
            "\n".join(f"- {item}" for item in bottlenecks) or "- None in the MVP criteria."
        )
        a = self.atomic_report
        n = self.nuclear_report
        c = self.cosmology_report
        s = self.stellar_report
        structure = self.structure_report
        complexity = self.complexity_report
        return f"""# Universe Report: {self.config.universe.name}

## Final Verdict
{self.final_verdict}

## Validation
{self.validation_report.to_markdown()}

## Fundamental Parameters
- Effective alpha: {self.config.effective_alpha:.9g}
- Gravity scale: {self.config.dimensionless.gravity_scale:.9g}
- Strong scale: {self.config.dimensionless.strong_scale:.9g}
- H0: {self.config.cosmology.H0_km_s_Mpc:.6g} km/s/Mpc

## Particle Spectrum
{self.particle_spectrum.to_markdown_table()}

## Atomic Layer
- Stable hydrogen: {str(a.stable_hydrogen).lower()}
- Bohr radius: {a.bohr_radius_m:.9g} m
- Binding energy: {a.binding_energy_eV:.9g} eV
- Chemistry energy scale: {a.chemistry_energy_scale_eV:.9g} eV

## Nuclear Layer
- Deuteron stable: {str(n.deuteron_stable).lower()}
- Helium-4 stable: {str(n.helium4_stable).lower()}
- Heavy-element seed possible: {str(n.heavy_element_seed_possible).lower()}

## Cosmology Layer
- Age: {c.age_of_universe_Gyr:.6g} Gyr
- Accelerated expansion: {str(c.accelerated_expansion).lower()}
- Structure growth window: {str(c.structure_growth_window).lower()}

## Stellar Layer
- Hydrogen fusion possible: {str(s.hydrogen_fusion_possible).lower()}
- Long-lived stars possible: {str(s.long_lived_stars_possible).lower()}
- Characteristic lifetime: {s.characteristic_stellar_lifetime_years:.6g} years
- Heavy-element production possible: {str(s.heavy_element_production_possible).lower()}

## Structure Layer
- Structure growth possible: {str(structure.structure_growth_possible).lower()}
- Galaxy formation possible: {str(structure.galaxy_formation_possible).lower()}
- Planet formation possible: {str(structure.planet_formation_possible).lower()}
- Stable orbits possible: {str(structure.stable_orbits_possible).lower()}

## Complexity Layer
- Chemistry score: {complexity.chemistry_score:.4f}
- Energy-gradient score: {complexity.energy_gradient_score:.4f}
- Stability score: {complexity.stability_score:.4f}
- Element-diversity score: {complexity.element_diversity_score:.4f}
- Life-window score: {complexity.life_window_score:.4f}
- Civilization-potential score: {complexity.civilization_potential_score:.4f}

## Key Bottlenecks
{bottleneck_text}

## Comparison to Standard Universe
Use `quanta compare configs/standard_universe.yaml CONFIG` for normalized differences.

> Life and civilization scores are heuristic physical-feasibility indicators, not occurrence probabilities.
"""

    def write(
        self, markdown_path: str | Path | None = None, json_path: str | Path | None = None
    ) -> None:
        if markdown_path is not None:
            target = Path(markdown_path)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(self.to_markdown(), encoding="utf-8")
        if json_path is not None:
            target = Path(json_path)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(
                json.dumps(self.to_json_dict(), indent=2, ensure_ascii=False, allow_nan=False),
                encoding="utf-8",
            )
