"""Coarse epoch labels derived from scale factor."""


def epoch_for_scale_factor(scale_factor: float) -> str:
    if scale_factor <= 0:
        raise ValueError("scale_factor must be positive")
    if scale_factor < 1e-9:
        return "radiation plasma"
    if scale_factor < 1e-3:
        return "nucleosynthesis and recombination approach"
    if scale_factor < 0.5:
        return "matter-dominated structure growth"
    return "late-time expansion"
