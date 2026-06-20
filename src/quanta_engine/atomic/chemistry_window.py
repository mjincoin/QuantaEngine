"""Interpretable chemistry-window scoring."""

from __future__ import annotations

import math

from quanta_engine.core.constants import STANDARD_BOHR_RADIUS_M, STANDARD_HYDROGEN_BINDING_EV


def chemistry_window_score(stable: bool, binding_energy_eV: float, bohr_radius_m: float) -> float:
    if not stable or binding_energy_eV <= 0 or bohr_radius_m <= 0:
        return 0.0
    energy_ratio = min(
        binding_energy_eV / STANDARD_HYDROGEN_BINDING_EV,
        STANDARD_HYDROGEN_BINDING_EV / binding_energy_eV,
    )
    radius_ratio = min(
        bohr_radius_m / STANDARD_BOHR_RADIUS_M, STANDARD_BOHR_RADIUS_M / bohr_radius_m
    )
    return max(0.0, min(1.0, math.sqrt(energy_ratio * radius_ratio)))
