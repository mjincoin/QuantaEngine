"""Physical constants used for metadata and future SI-aware modules.

The current numerical kernels use dimensionless natural units by default.
These SI constants are included so future modules can explicitly bridge between
laboratory/high-energy-physics conventions and cosmological units.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SIConstants:
    """A compact set of SI constants."""

    c: float = 299_792_458.0
    hbar: float = 1.054_571_817e-34
    G: float = 6.674_30e-11
    k_B: float = 1.380_649e-23
    e: float = 1.602_176_634e-19
    epsilon_0: float = 8.854_187_8128e-12
    mu_0: float = 1.256_637_06212e-6


SI = SIConstants()
