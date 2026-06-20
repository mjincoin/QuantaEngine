"""Scheme registry: the one place that maps a scheme name to its engine class.

Adding a new scheme means dropping a subpackage here and registering it below;
no other module needs to change. This is what keeps long-term multi-scheme
parallelism from turning into spaghetti.
"""

from __future__ import annotations

from quanta_engine.core.schema import UniverseConfig

from ..core import UniverseScheme
from .analytic_compiler import METADATA as ANALYTIC_META
from .analytic_compiler import AnalyticCompiler
from .minimal_axiom import METADATA as MINIMAL_META
from .minimal_axiom import MinimalAxiom
from .variational_relaxer import METADATA as VARIATIONAL_META
from .variational_relaxer import VariationalRelaxer

SCHEME_REGISTRY: dict[str, type] = {
    AnalyticCompiler.name: AnalyticCompiler,
    VariationalRelaxer.name: VariationalRelaxer,
    MinimalAxiom.name: MinimalAxiom,
}

SCHEME_METADATA: dict[str, dict] = {
    AnalyticCompiler.name: ANALYTIC_META,
    VariationalRelaxer.name: VARIATIONAL_META,
    MinimalAxiom.name: MINIMAL_META,
}


def list_schemes() -> list[str]:
    return list(SCHEME_REGISTRY)


def build_scheme(name: str, config: UniverseConfig) -> UniverseScheme:
    if name not in SCHEME_REGISTRY:
        raise ValueError(f"unknown scheme '{name}'. known: {list_schemes()}")
    return SCHEME_REGISTRY[name](config)


__all__ = [
    "SCHEME_REGISTRY",
    "SCHEME_METADATA",
    "list_schemes",
    "build_scheme",
    "AnalyticCompiler",
    "VariationalRelaxer",
    "MinimalAxiom",
]
