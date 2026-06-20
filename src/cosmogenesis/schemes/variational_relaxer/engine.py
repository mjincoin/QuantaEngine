"""variational_relaxer engine: a universe as a fixed point of coupled constraints.

Emergent scales come from extremizing balance functionals; soft logistic windows
replace hard booleans; a global cross-layer self-consistency RESIDUAL plus a small
fixed-point relaxation can reject a universe that passes every individual window.
Adversarial I/O: ParameterVector -> UniverseAssessment.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from quanta_engine.core.schema import UniverseConfig
from quanta_engine.core.units import JULIAN_YEAR_S, MEGAPARSEC_M

from ...core import (
    BaseEngine,
    ParameterVector,
    UniverseAssessment,
    apply_vector,
    logistic_window,
    softmin,
)
from .optimizer import evolution_strategy

SCHEME_NAME = "variational_relaxer"
_ALPHA0 = 0.0072973525693


@dataclass(slots=True)
class _Emergent:
    binding_eV: float
    bohr_radius_m: float
    nuclear_margin: float
    ignition_margin: float
    stellar_lifetime_years: float
    age_years: float
    amplitude: float
    margins: dict[str, float]
    residual_terms: dict[str, float]
    relax_converged: bool


class VariationalRelaxer(BaseEngine):
    name = SCHEME_NAME

    def __init__(self, base_config: UniverseConfig, seed: int = 7) -> None:
        super().__init__(base_config)
        self._rng = np.random.default_rng(seed)
        self._residual_lambda = 2.0

    def _derive(self, vector: ParameterVector) -> _Emergent:
        cfg = apply_vector(self.base_config, vector)
        k = cfg.constants
        d = cfg.dimensionless
        p = cfg.particles
        cos = cfg.cosmology

        alpha = d.alpha * d.alpha_scale
        g_scale = d.gravity_scale
        strong = d.strong_scale
        cc = d.cosmological_constant_scale

        # atomic scale by energy extremization: E(r)=h^2/(2 mu r^2)-alpha hc/r
        mu_MeV = (p.electron_mass_MeV * p.proton_mass_MeV) / (
            p.electron_mass_MeV + p.proton_mass_MeV
        )
        mu_J = mu_MeV * 1e6 * 1.602176634e-19
        binding_J = 0.5 * mu_J * alpha**2
        binding_eV = binding_J / 1.602176634e-19
        bohr = k.hbar / (max(mu_J, 1e-40) / k.c**2 * k.c * max(alpha, 1e-9))

        atomic_margin = logistic_window(binding_eV, lo=1.0, hi=120.0)
        relativistic = 1.0 / (1.0 + math.exp((alpha - 0.5) / 0.05))
        atomic = atomic_margin * relativistic

        eff_strong = strong - 0.08 * (alpha / _ALPHA0 - 1.0)
        nuclear = logistic_window(max(eff_strong, 1e-6), lo=0.8, hi=1.45, width_frac=0.25)

        ignition = 1.0 / (1.0 + math.exp(-(math.log10(g_scale) + 1.4) / 0.4))
        lifetime_years = 1.0e10 * g_scale**-2.0 * (alpha / _ALPHA0) ** 0.5
        lifetime_margin = logistic_window(lifetime_years, lo=1.0e9, hi=1.0e13)

        omega_m = max(cos.omega_b + cos.omega_cdm, 1e-6)
        omega_lambda = max(cos.omega_lambda * cc, 1e-9)
        h0_per_s = abs(cos.H0_km_s_Mpc) * 1000.0 / MEGAPARSEC_M
        age_s = (2.0 / (3.0 * h0_per_s * math.sqrt(omega_lambda))) * math.asinh(
            math.sqrt(omega_lambda / omega_m)
        )
        age_years = age_s / JULIAN_YEAR_S

        amplitude = math.sqrt(max(cos.primordial_amplitude, 0.0))
        supp = 1.0 / (1.0 + omega_lambda / omega_m)
        amp_eff = amplitude * supp * 8.0
        structure = logistic_window(max(amplitude, 1e-12), lo=1e-6, hi=3e-4)

        margins = {
            "atomic": atomic,
            "nuclear": nuclear,
            "ignition": ignition,
            "lifetime": lifetime_margin,
            "structure": structure,
            "age": logistic_window(age_years, lo=2e9, hi=5e10),
        }

        # cross-layer self-consistency residuals
        omega_r = max(cos.omega_r, 0.0)
        curvature = cfg.spacetime.curvature_k or 0.0
        r_flat = abs(omega_m + omega_lambda + omega_r + curvature - 1.0)
        needed = max(cfg.stellar.min_lifetime_years_for_complexity, lifetime_years * 0.3)
        r_time = max(0.0, (needed - age_years) / max(needed, 1.0))
        e_thermal_eV = 1.380649e-23 * 300.0 / 1.602176634e-19
        r_chem = max(0.0, (e_thermal_eV - binding_eV) / max(binding_eV, 1e-9))

        # fixed-point relaxation of emergent state [metallicity, structure amp, lifetime]
        z, s, lf = 0.1, max(amp_eff, 1e-6), lifetime_margin
        converged = False
        last = math.inf
        for _ in range(64):
            z_new = 0.6 * ignition * nuclear * s
            s_new = structure * omega_m * (1.0 + 0.2 * z)
            l_new = lifetime_margin
            delta = abs(z_new - z) + abs(s_new - s) + abs(l_new - lf)
            z, s, lf = z_new, s_new, l_new
            if delta < 1e-6:
                converged = True
                break
            if delta > last + 1.0:
                break
            last = delta
        r_relax = 0.0 if converged else 0.5

        residual_terms = {
            "flatness": r_flat,
            "time_budget": r_time,
            "chemistry_thermal": r_chem,
            "relaxation": r_relax,
        }
        return _Emergent(
            binding_eV=binding_eV,
            bohr_radius_m=bohr,
            nuclear_margin=nuclear,
            ignition_margin=ignition,
            stellar_lifetime_years=lifetime_years,
            age_years=age_years,
            amplitude=amplitude,
            margins=margins,
            residual_terms=residual_terms,
            relax_converged=converged,
        )

    def assess(self, vector: ParameterVector) -> UniverseAssessment:
        e = self._derive(vector)
        residual = sum(e.residual_terms.values())
        base_margin = softmin(list(e.margins.values()))
        score = base_margin * math.exp(-self._residual_lambda * residual)
        warnings = []
        if not e.relax_converged:
            warnings.append("self-consistency relaxation did not converge (internally inconsistent)")
        for name, val in e.residual_terms.items():
            if val > 0.05:
                warnings.append(f"high self-consistency residual: {name}={val:.3f}")
        return UniverseAssessment(
            scheme=self.name,
            score=score,
            feasible=score > 0.5 and e.relax_converged,
            margins=e.margins,
            residual=residual,
            diagnostics={
                "binding_eV": e.binding_eV,
                "stellar_lifetime_years": e.stellar_lifetime_years,
                "age_years": e.age_years,
                "amplitude": e.amplitude,
                "residual_terms": e.residual_terms,
                "relax_converged": e.relax_converged,
            },
            warnings=warnings,
        )

    def residual(self, vector: ParameterVector) -> float:
        return self.assess(vector).residual

    def optimize(self, start: ParameterVector, budget: int = 80) -> ParameterVector:
        best = evolution_strategy(self, start, self._rng, budget=budget)
        self.last_champion = best
        return best
