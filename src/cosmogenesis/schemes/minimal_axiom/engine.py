"""minimal_axiom engine: feasibility from the fewest dimensionless numbers.

Uses anthropic inequalities (Carr-Rees / Barrow-Tipler) over alpha, the
gravitational coupling alpha_G = G m_p^2 / (hbar c), and the mass ratio -- no
layered pipeline, no fixed point. Adversarial I/O: ParameterVector -> UniverseAssessment.
"""

from __future__ import annotations

import math

import numpy as np

from quanta_engine.core.schema import UniverseConfig
from quanta_engine.core.units import MEV_C2_KG

from ...core import BaseEngine, ParameterVector, UniverseAssessment, apply_vector, logistic_window
from .optimizer import restart_hill_climb

SCHEME_NAME = "minimal_axiom"
_ALPHA_G0 = 5.9e-39


def _falling(value: float, threshold: float, width_decades: float = 1.0) -> float:
    if value <= 0:
        return 1.0
    return 1.0 / (1.0 + math.exp((math.log10(value) - math.log10(threshold)) / width_decades))


class MinimalAxiom(BaseEngine):
    name = SCHEME_NAME

    def __init__(self, base_config: UniverseConfig, seed: int = 11) -> None:
        super().__init__(base_config)
        self._rng = np.random.default_rng(seed)

    def _numbers(self, vector: ParameterVector) -> dict[str, float]:
        cfg = apply_vector(self.base_config, vector)
        k = cfg.constants
        d = cfg.dimensionless
        p = cfg.particles
        alpha = d.alpha * d.alpha_scale
        g_eff = k.G * d.gravity_scale
        m_p_kg = p.proton_mass_MeV * MEV_C2_KG
        alpha_g = g_eff * m_p_kg**2 / (k.hbar * k.c)
        beta = p.electron_mass_MeV / p.proton_mass_MeV
        return {"alpha": alpha, "alpha_G": alpha_g, "beta": beta}

    def assess(self, vector: ParameterVector) -> UniverseAssessment:
        cfg = apply_vector(self.base_config, vector)
        n = self._numbers(vector)
        alpha, alpha_g = n["alpha"], n["alpha_G"]
        cc = cfg.dimensionless.cosmological_constant_scale
        amp = math.sqrt(max(cfg.cosmology.primordial_amplitude, 0.0))

        m_atoms = logistic_window(alpha, lo=1e-3, hi=0.1)
        n_star = alpha_g ** (-1.5)
        m_stars = logistic_window(n_star, lo=1e48, hi=1e63)
        hierarchy = math.sqrt(alpha_g) / max(alpha, 1e-12)
        m_hierarchy = _falling(hierarchy, threshold=1e-8, width_decades=1.5)
        m_lambda = _falling(cc, threshold=12.0, width_decades=0.5)
        m_seeds = logistic_window(max(amp, 1e-12), lo=1e-6, hi=3e-4)

        margins = {
            "atoms": m_atoms,
            "stars": m_stars,
            "hierarchy": m_hierarchy,
            "lambda": m_lambda,
            "seeds": m_seeds,
        }
        vals = list(margins.values())
        score = math.exp(sum(math.log(max(v, 1e-9)) for v in vals) / len(vals))
        warnings = [f"weak anthropic margin: {key}" for key, v in margins.items() if v < 0.3]
        return UniverseAssessment(
            scheme=self.name,
            score=score,
            feasible=score > 0.5,
            margins=margins,
            residual=0.0,
            diagnostics={
                "alpha": alpha,
                "alpha_G": alpha_g,
                "N_star": n_star,
                "hierarchy_ratio": hierarchy,
                "free_parameters": 3,  # alpha, alpha_G, beta -- the minimal set
            },
            warnings=warnings,
        )

    def optimize(self, start: ParameterVector, budget: int = 60) -> ParameterVector:
        best = restart_hill_climb(self, start, budget=budget)
        self.last_champion = best
        return best
