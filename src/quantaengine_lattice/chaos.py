"""Microscopic chaotic perturbation utilities."""

from __future__ import annotations

import numpy as np

from .params import UniverseParams


def logistic_chaos(shape: tuple[int, ...], rate: float, seed_value: float = 0.417) -> np.ndarray:
    """Create a deterministic logistic-map perturbation field.

    The logistic map is not a microscopic quantum theory. It is included as a
    controllable chaos source so users can study sensitivity to tiny changes in
    microscopic initial conditions.
    """

    size = int(np.prod(shape))
    x = np.empty(size, dtype=np.float64)
    value = min(max(seed_value, 1.0e-9), 1.0 - 1.0e-9)
    for i in range(size):
        value = rate * value * (1.0 - value)
        x[i] = value
    x = x.reshape(shape)
    x -= float(np.mean(x))
    std = float(np.std(x))
    if std > 0:
        x /= std
    return x


def apply_chaos(field: np.ndarray, params: UniverseParams) -> np.ndarray:
    """Return a field with optional chaotic microscopic modulation."""

    if params.chaos_strength == 0:
        return field
    seed_value = ((params.seed % 10_000) + 1) / 10_001.0
    chaos = logistic_chaos(field.shape, params.chaos_rate, seed_value=seed_value)
    return field + params.chaos_strength * params.primordial_rms * chaos
