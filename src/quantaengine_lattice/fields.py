"""Scalar-field lattice evolution.

This module implements a compact periodic-lattice scalar field. It is a toy
semiclassical kernel intended to be easy to replace with more realistic physics.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .params import UniverseParams


@dataclass(slots=True)
class ScalarFieldState:
    phi: np.ndarray
    pi: np.ndarray
    time: float
    scale_factor: float

    def copy(self) -> ScalarFieldState:
        return ScalarFieldState(
            phi=self.phi.copy(),
            pi=self.pi.copy(),
            time=float(self.time),
            scale_factor=float(self.scale_factor),
        )


class ScalarFieldLattice:
    """Periodic scalar field with effective potential V = m²φ²/2 + λφ⁴/4."""

    def __init__(self, params: UniverseParams, initial_phi: np.ndarray):
        self.params = params
        self.state = ScalarFieldState(
            phi=initial_phi.astype(np.float64, copy=True),
            pi=np.zeros_like(initial_phi, dtype=np.float64),
            time=0.0,
            scale_factor=params.initial_scale_factor,
        )

    def laplacian(self, field: np.ndarray) -> np.ndarray:
        dx2 = self.params.dx**2
        lap = np.zeros_like(field)
        for axis in range(field.ndim):
            lap += np.roll(field, 1, axis=axis)
            lap += np.roll(field, -1, axis=axis)
            lap -= 2.0 * field
        return lap / dx2

    def grad_squared(self, field: np.ndarray) -> np.ndarray:
        total = np.zeros_like(field)
        for axis in range(field.ndim):
            grad = (np.roll(field, -1, axis=axis) - np.roll(field, 1, axis=axis)) / (2.0 * self.params.dx)
            total += grad**2
        return total

    def potential(self, field: np.ndarray | None = None) -> np.ndarray:
        if field is None:
            field = self.state.phi
        p = self.params
        return 0.5 * p.scalar_mass**2 * field**2 + 0.25 * p.self_coupling * field**4

    def d_potential(self, field: np.ndarray | None = None) -> np.ndarray:
        if field is None:
            field = self.state.phi
        p = self.params
        return p.scalar_mass**2 * field + p.self_coupling * field**3

    def energy_density(self) -> np.ndarray:
        s = self.state
        a2 = max(s.scale_factor**2, 1.0e-12)
        kinetic = 0.5 * s.pi**2
        gradient = 0.5 * self.params.gradient_strength * self.grad_squared(s.phi) / a2
        return kinetic + gradient + self.potential(s.phi)

    def step(self, dt: float, scale_factor: float, hubble: float) -> ScalarFieldState:
        """Advance the field by one semi-implicit Euler/leapfrog-like step."""

        s = self.state
        a2 = max(scale_factor**2, 1.0e-12)
        force = (
            self.params.gradient_strength * self.laplacian(s.phi) / a2
            - self.d_potential(s.phi)
            - 3.0 * self.params.hubble_damping * hubble * s.pi
        )
        pi_new = s.pi + dt * force
        phi_new = s.phi + dt * pi_new
        self.state = ScalarFieldState(
            phi=phi_new,
            pi=pi_new,
            time=s.time + dt,
            scale_factor=scale_factor,
        )
        return self.state
