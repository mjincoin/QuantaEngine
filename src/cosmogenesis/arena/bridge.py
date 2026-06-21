"""Bridge from a TheorySpec to a scheme engine in cosmogenesis.schemes.

This is the only place the arena touches the scheme registry; everything else in
the arena is paradigm-agnostic.
"""

from __future__ import annotations

from collections import OrderedDict
from copy import deepcopy
from functools import lru_cache
from threading import RLock

from quanta_engine.core.schema import load_config

from ..core import ParameterVector, UniverseAssessment, vector_from_config
from ..schemes import build_scheme
from .theory import TheorySpec

_ASSESS_CACHE_MAXSIZE = 4096
_ASSESS_CACHE: OrderedDict[tuple[str, str, tuple[float, ...]], UniverseAssessment] = OrderedDict()
_ASSESS_CACHE_LOCK = RLock()
_ASSESS_CACHE_HITS = 0
_ASSESS_CACHE_MISSES = 0
_VECTOR_ROUND_DIGITS = 12


@lru_cache(maxsize=32)
def _load(config_path: str):
    return load_config(config_path)


def build_engine(theory: TheorySpec):
    """Instantiate the scheme engine named by ``theory.engine``."""

    return build_scheme(theory.engine, _load(str(theory.resolve_base_config())))


def seed_vector(theory: TheorySpec) -> ParameterVector:
    if theory.seed_vector is not None:
        return ParameterVector(list(theory.seed_vector))
    return vector_from_config(_load(str(theory.resolve_base_config())))


def assess(theory: TheorySpec, vector: ParameterVector) -> UniverseAssessment:
    """Assess with deterministic bounded memoization.

    The public cache identity is ``(theory_id, version, rounded-vector)``. Version
    bumps therefore invalidate old physics, while sub-femtoscale floating noise does
    not create duplicate entries. The lock prevents parallel cache stampedes.
    """

    global _ASSESS_CACHE_HITS, _ASSESS_CACHE_MISSES
    key = (
        theory.theory_id,
        theory.version,
        tuple(round(value, _VECTOR_ROUND_DIGITS) for value in vector.values),
    )
    with _ASSESS_CACHE_LOCK:
        cached = _ASSESS_CACHE.get(key)
        if cached is not None:
            _ASSESS_CACHE_HITS += 1
            _ASSESS_CACHE.move_to_end(key)
            return deepcopy(cached)
        _ASSESS_CACHE_MISSES += 1
        result = build_engine(theory).assess(ParameterVector(list(key[2])))
        _ASSESS_CACHE[key] = deepcopy(result)
        _ASSESS_CACHE.move_to_end(key)
        while len(_ASSESS_CACHE) > _ASSESS_CACHE_MAXSIZE:
            _ASSESS_CACHE.popitem(last=False)
        return result


def clear_assess_cache() -> None:
    """Clear memoized assessments (primarily for tests and long-lived workers)."""

    global _ASSESS_CACHE_HITS, _ASSESS_CACHE_MISSES
    with _ASSESS_CACHE_LOCK:
        _ASSESS_CACHE.clear()
        _ASSESS_CACHE_HITS = 0
        _ASSESS_CACHE_MISSES = 0


def assess_cache_info() -> dict[str, int]:
    with _ASSESS_CACHE_LOCK:
        return {
            "hits": _ASSESS_CACHE_HITS,
            "misses": _ASSESS_CACHE_MISSES,
            "size": len(_ASSESS_CACHE),
            "maxsize": _ASSESS_CACHE_MAXSIZE,
        }


def optimize(theory: TheorySpec, vector: ParameterVector, budget: int = 70) -> ParameterVector:
    return build_engine(theory).optimize(vector, budget=budget)


def consider(theory: TheorySpec, suggestion: ParameterVector, budget: int = 20):
    """The theory independently reconsiders a rival's ``suggestion`` under its own
    objective, starting from its current champion. Deterministic (fresh engine)."""

    engine = build_engine(theory)
    current = seed_vector(theory)
    return engine.consider(current, suggestion, budget=budget)


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
