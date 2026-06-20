"""Weighted life-window feasibility score."""


def life_window_score(
    chemistry: float,
    energy: float,
    stability: float,
    elements: float,
    structures: float,
) -> float:
    if chemistry <= 0:
        return 0.0
    support = 0.30 * energy + 0.25 * stability + 0.25 * elements + 0.20 * structures
    return max(0.0, min(1.0, chemistry * support))
