"""Finite-difference sensitivity helper."""


def normalized_sensitivity(x0: float, x1: float, y0: float, y1: float) -> float:
    if x0 == 0 or y0 == 0 or x1 == x0:
        raise ValueError("normalized sensitivity requires non-zero baselines and parameter change")
    return ((y1 - y0) / y0) / ((x1 - x0) / x0)
