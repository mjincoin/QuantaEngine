"""Bridge from a TheorySpec to a scheme engine in cosmogenesis.schemes.

This is the only place the arena touches the scheme registry; everything else in
the arena is paradigm-agnostic.
"""

from __future__ import annotations

from functools import lru_cache

from quanta_engine.core.schema import load_config

from ..core import ParameterVector, UniverseAssessment, vector_from_config
from ..schemes import build_scheme
from .theory import TheorySpec


@lru_cache(maxsize=32)
def _load(config_path: str):
    return load_config(config_path)


def build_engine(theory: TheorySpec):
    """Instantiate the scheme engine named by ``theory.engine``."""

    return build_scheme(theory.engine, _load(theory.base_config))


def seed_vector(theory: TheorySpec) -> ParameterVector:
    if theory.seed_vector is not None:
        return ParameterVector(list(theory.seed_vector))
    return vector_from_config(_load(theory.base_config))


def assess(theory: TheorySpec, vector: ParameterVector) -> UniverseAssessment:
    return build_engine(theory).assess(vector)


def optimize(theory: TheorySpec, vector: ParameterVector, budget: int = 70) -> ParameterVector:
    return build_engine(theory).optimize(vector, budget=budget)


def novelty_features(theory: TheorySpec, vector: ParameterVector) -> list[float]:
    """Scheme-agnostic feature vector for novelty search (same axes per engine)."""

    out = assess(theory, vector)
    diag = out.diagnostics
    return [
        *vector.values,
        float(diag.get("binding_eV", diag.get("alpha", 0.0)) or 0.0),
        out.score,
        out.residual,
    ]
