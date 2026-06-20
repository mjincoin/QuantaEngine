"""Shared adversarial I/O contract for every scheme.

- ``ParameterVector`` is the common, scheme-agnostic search space.
- ``UniverseAssessment`` is the common verdict every scheme returns.
- ``UniverseScheme`` / ``BaseEngine`` is the contract a scheme implements.
"""

from .assessment import UniverseAssessment, logistic_window, softmin
from .parameters import (
    AXES,
    AXIS_BY_NAME,
    NDIM,
    ParameterVector,
    apply_vector,
    vector_from_config,
)
from .protocol import BaseEngine, UniverseScheme, fragility_profile

__all__ = [
    "ParameterVector",
    "AXES",
    "AXIS_BY_NAME",
    "NDIM",
    "apply_vector",
    "vector_from_config",
    "UniverseAssessment",
    "softmin",
    "logistic_window",
    "UniverseScheme",
    "BaseEngine",
    "fragility_profile",
]
