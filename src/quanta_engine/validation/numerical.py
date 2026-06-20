"""Reusable finite/range checks."""

import math


def is_positive_finite(value: float) -> bool:
    return math.isfinite(value) and value > 0.0


def closeness_score(value: float, target: float, tolerance: float) -> float:
    if tolerance <= 0:
        raise ValueError("tolerance must be positive")
    return max(0.0, 1.0 - abs(value - target) / tolerance)
