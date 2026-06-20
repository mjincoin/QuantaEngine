"""Friedmann-like background expansion in dimensionless Hubble-time units."""

from __future__ import annotations

from dataclasses import dataclass

from .params import UniverseParams


@dataclass(slots=True)
class BackgroundState:
    """Scale-factor state for a generated universe."""

    time: float
    scale_factor: float


class FriedmannBackground:
    """Flat/open/closed background expansion with tunable density terms.

    We use dimensionless Hubble-time units, so the Hubble constant is set to 1.
    This keeps the prototype transparent and avoids implying production-level
    SI/cosmological validation.
    """

    def __init__(self, params: UniverseParams):
        self.params = params
        self.state = BackgroundState(time=0.0, scale_factor=params.initial_scale_factor)

    def e2(self, a: float) -> float:
        p = self.params
        return (
            p.omega_r / a**4
            + p.omega_m / a**3
            + p.omega_k / a**2
            + p.omega_lambda
        )

    def hubble(self, a: float | None = None) -> float:
        if a is None:
            a = self.state.scale_factor
        value = self.e2(a)
        if value <= 0:
            return 0.0
        return value**0.5

    def da_dt(self, a: float) -> float:
        return a * self.hubble(a)

    def step(self, dt: float) -> BackgroundState:
        """Advance the scale factor with RK4."""

        a0 = self.state.scale_factor
        k1 = self.da_dt(a0)
        k2 = self.da_dt(a0 + 0.5 * dt * k1)
        k3 = self.da_dt(a0 + 0.5 * dt * k2)
        k4 = self.da_dt(a0 + dt * k3)
        a1 = max(1.0e-12, a0 + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4))
        self.state = BackgroundState(time=self.state.time + dt, scale_factor=a1)
        return self.state

    def integrate(self, steps: int, dt: float) -> list[BackgroundState]:
        states = [self.state]
        for _ in range(steps):
            states.append(self.step(dt))
        return states
