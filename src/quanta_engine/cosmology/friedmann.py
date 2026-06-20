"""Numerical FLRW background solver for the MVP pipeline."""

from dataclasses import dataclass, field
from math import sqrt

import numpy as np
from scipy.integrate import quad

from quanta_engine.core.schema import UniverseConfig
from quanta_engine.core.units import Mpc_to_meter, year_to_second


@dataclass(slots=True)
class CosmologyReport:
    age_of_universe_s: float
    age_of_universe_Gyr: float
    expansion_history_sample: list[dict[str, float]]
    matter_radiation_equality_estimate: float | None
    accelerated_expansion: bool
    structure_growth_window: bool
    warnings: list[str] = field(default_factory=list)


def compute_friedmann_background(config: UniverseConfig) -> CosmologyReport:
    c = config.cosmology
    warnings: list[str] = []
    raw = {
        "radiation": c.omega_r,
        "baryons": c.omega_b,
        "dark matter": c.omega_cdm,
        "dark energy": c.omega_lambda * config.dimensionless.cosmological_constant_scale,
    }
    for name, value in raw.items():
        if value < 0:
            warnings.append(
                f"negative {name} density was clipped to zero for numerical integration"
            )
    omega_r = max(0.0, raw["radiation"])
    omega_m = max(0.0, raw["baryons"]) + max(0.0, raw["dark matter"])
    omega_lambda = max(0.0, raw["dark energy"])
    if config.spacetime.curvature_k is None:
        omega_k = 1.0 - omega_r - omega_m - omega_lambda
    else:
        omega_k = config.spacetime.curvature_k

    h0 = abs(c.H0_km_s_Mpc) * 1000.0 / Mpc_to_meter(1.0)
    if h0 == 0:
        h0 = 1.0e-30
        warnings.append("H0 was zero; a numerical floor was used")

    def e2(a: float) -> float:
        value = omega_r / a**4 + omega_m / a**3 + omega_k / a**2 + omega_lambda
        if value <= 0:
            return 1.0e-30
        return value

    integral, _ = quad(lambda a: 1.0 / (a * sqrt(e2(a))), 1.0e-8, 1.0, limit=300)
    age_s = integral / h0
    age_gyr = age_s / year_to_second(1.0) / 1.0e9
    scales = np.logspace(-4, 0, 200)
    history = [
        {
            "scale_factor": float(a),
            "redshift": float(1.0 / a - 1.0),
            "H_per_s": float(h0 * sqrt(e2(float(a)))),
        }
        for a in scales
    ]
    equality = omega_r / omega_m if omega_m > 0 else None
    accelerated = omega_lambda > 0.5 * omega_m + omega_r
    fluctuation_amplitude = sqrt(max(0.0, c.primordial_amplitude))
    structure_window = omega_m > 0.05 and 1.0e-7 <= fluctuation_amplitude <= 1.0e-3
    return CosmologyReport(
        age_of_universe_s=age_s,
        age_of_universe_Gyr=age_gyr,
        expansion_history_sample=history,
        matter_radiation_equality_estimate=equality,
        accelerated_expansion=accelerated,
        structure_growth_window=structure_window,
        warnings=warnings,
    )
