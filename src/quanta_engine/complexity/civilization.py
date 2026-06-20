"""Civilization-window feasibility score."""


def civilization_potential_score(
    life_window: float,
    stability: float,
    energy: float,
    planets: float,
) -> float:
    support = 0.35 * stability + 0.30 * energy + 0.35 * planets
    return max(0.0, min(1.0, life_window * support))
