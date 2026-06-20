"""Optimizable fundamental-parameter vector shared by both schemes.

The vector spans the same configuration knobs that ``quanta_engine``'s parameter
scans operate on, so a universe found by either scheme is a valid input to the
other (the "same entry point" requirement).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from quanta_engine.core.schema import UniverseConfig


@dataclass(frozen=True, slots=True)
class Axis:
    """One optimizable degree of freedom mapped onto a dotted config path."""

    name: str
    config_path: str
    default: float
    lo: float
    hi: float
    log: bool = False  # optimize in log10 space (for many-orders-of-magnitude knobs)

    def clamp(self, value: float) -> float:
        return min(self.hi, max(self.lo, value))

    def to_config_value(self, value: float) -> float:
        """Map the (already raw) axis value to the value stored in the config."""

        return value


# The shared search space. Bounds are physically motivated windows, wide enough
# to leave the anthropic island yet bounded enough to keep solvers stable.
AXES: tuple[Axis, ...] = (
    Axis("alpha_scale", "dimensionless.alpha_scale", 1.0, 0.25, 3.0),
    Axis("gravity_scale", "dimensionless.gravity_scale", 1.0, 1e-2, 1e2, log=True),
    Axis("strong_scale", "dimensionless.strong_scale", 1.0, 0.5, 2.0),
    Axis("cc_scale", "dimensionless.cosmological_constant_scale", 1.0, 0.0, 50.0),
    Axis(
        "log10_primordial_amplitude",
        "cosmology.primordial_amplitude",
        math.log10(2.1e-9),
        -11.0,
        -5.0,
    ),
)

AXIS_BY_NAME = {axis.name: axis for axis in AXES}
NDIM = len(AXES)


@dataclass(slots=True)
class ParameterVector:
    """A point in the shared fundamental-parameter space."""

    values: list[float]

    def __post_init__(self) -> None:
        if len(self.values) != NDIM:
            raise ValueError(f"expected {NDIM} parameters, got {len(self.values)}")
        self.values = [axis.clamp(float(v)) for axis, v in zip(AXES, self.values, strict=True)]

    @classmethod
    def default(cls) -> ParameterVector:
        return cls([axis.default for axis in AXES])

    def as_dict(self) -> dict[str, float]:
        return {axis.name: v for axis, v in zip(AXES, self.values, strict=True)}

    def copy(self) -> ParameterVector:
        return ParameterVector(list(self.values))

    # --- normalized coordinates (0..1 per axis) for solver-agnostic stepping ---

    def to_normalized(self) -> list[float]:
        out = []
        for axis, v in zip(AXES, self.values, strict=True):
            lo, hi = axis.lo, axis.hi
            span = hi - lo or 1.0
            out.append((v - lo) / span)
        return out

    @classmethod
    def from_normalized(cls, normalized: list[float]) -> ParameterVector:
        values = []
        for axis, n in zip(AXES, normalized, strict=True):
            span = axis.hi - axis.lo or 1.0
            values.append(axis.lo + min(1.0, max(0.0, n)) * span)
        return cls(values)


def _set_path(config: UniverseConfig, dotted: str, value: float) -> None:
    parts = dotted.split(".")
    target: object = config
    for part in parts[:-1]:
        target = getattr(target, part)
    setattr(target, parts[-1], value)


def apply_vector(base: UniverseConfig, vector: ParameterVector) -> UniverseConfig:
    """Return a deep copy of ``base`` with the vector's knobs applied.

    ``log10_primordial_amplitude`` is stored as the linear amplitude in the
    config, everything else maps one-to-one.
    """

    config = base.model_copy(deep=True)
    for axis, raw in zip(AXES, vector.values, strict=True):
        value = 10.0**raw if axis.name == "log10_primordial_amplitude" else raw
        _set_path(config, axis.config_path, float(value))
    return config


def vector_from_config(config: UniverseConfig) -> ParameterVector:
    """Extract the optimizable vector from an existing config."""

    d = config.dimensionless
    amp = max(config.cosmology.primordial_amplitude, 1e-30)
    return ParameterVector(
        [
            d.alpha_scale,
            d.gravity_scale,
            d.strong_scale,
            d.cosmological_constant_scale,
            math.log10(amp),
        ]
    )
