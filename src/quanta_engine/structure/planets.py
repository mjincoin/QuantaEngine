"""Planet formation and stable-orbit heuristics."""


def planet_window(galaxies: bool, heavy_elements: bool, gravity_scale: float) -> tuple[bool, bool]:
    planets = galaxies and heavy_elements
    stable_orbits = planets and 1.0e-4 <= gravity_scale <= 1.0e4
    return planets, stable_orbits
