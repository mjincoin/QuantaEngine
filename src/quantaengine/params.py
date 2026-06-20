"""Universe parameter model.

The guiding idea is that a generated universe should be reproducible from a
small, explicit set of microscopic, cosmological, and numerical parameters.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(slots=True)
class UniverseParams:
    """Parameters controlling one generated universe.

    The simulation currently uses dimensionless code units. Parameters are split
    into conceptual physics controls and numerical controls. Later versions can
    add validated unit conversion layers without breaking configuration files.
    """

    name: str = "quantaengine-universe"
    seed: int = 42

    # Numerical geometry.
    dimensions: int = 2
    grid_size: int = 128
    box_size: float = 1.0

    # Friedmann-like background in Hubble-time units.
    omega_m: float = 0.315
    omega_r: float = 9.0e-5
    omega_lambda: float = 0.685
    omega_k: float = 0.0
    initial_scale_factor: float = 1.0e-1

    # Primordial fluctuation controls.
    primordial_rms: float = 1.0e-3
    spectral_index: float = 0.965
    pivot_k: float = 1.0
    k_cut: float = 64.0
    chaos_strength: float = 0.0
    chaos_rate: float = 3.86

    # Scalar-field effective model.
    scalar_mass: float = 0.2
    self_coupling: float = 0.05
    hubble_damping: float = 1.0
    gradient_strength: float = 1.0e-3

    # Time integration.
    time_step: float = 1.0e-3

    # Future-facing first-principles placeholders.
    fine_structure_alpha: float = 1.0 / 137.035_999_084
    gravitational_coupling: float = 1.0
    electroweak_scale: float = 246.0
    qcd_scale: float = 0.2

    def validate(self) -> None:
        """Raise ValueError when a configuration is inconsistent."""

        if self.dimensions not in (1, 2, 3):
            raise ValueError("dimensions must be 1, 2, or 3")
        if self.grid_size < 8:
            raise ValueError("grid_size must be at least 8")
        if self.box_size <= 0:
            raise ValueError("box_size must be positive")
        if self.initial_scale_factor <= 0:
            raise ValueError("initial_scale_factor must be positive")
        if self.time_step <= 0:
            raise ValueError("time_step must be positive")
        if self.primordial_rms < 0:
            raise ValueError("primordial_rms must be non-negative")
        if self.k_cut <= 0:
            raise ValueError("k_cut must be positive")
        if self.self_coupling < 0:
            raise ValueError("self_coupling should be non-negative for a stable toy potential")
        if self.chaos_strength < 0:
            raise ValueError("chaos_strength must be non-negative")
        if not 0 < self.chaos_rate <= 4:
            raise ValueError("chaos_rate must lie in (0, 4]")
        if self.omega_m < 0 or self.omega_r < 0 or self.omega_lambda < 0:
            raise ValueError("omega_m, omega_r, and omega_lambda should be non-negative")

    @property
    def shape(self) -> tuple[int, ...]:
        return (self.grid_size,) * self.dimensions

    @property
    def dx(self) -> float:
        return self.box_size / self.grid_size

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> UniverseParams:
        allowed = set(cls.__dataclass_fields__)
        unknown = sorted(set(data) - allowed)
        if unknown:
            raise ValueError(f"Unknown UniverseParams fields: {unknown}")
        params = cls(**data)
        params.validate()
        return params
