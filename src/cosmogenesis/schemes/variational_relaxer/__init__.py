"""Scheme: variational_relaxer.

Paradigm: a universe as the fixed point of coupled constraints, with soft windows
and an explicit cross-layer self-consistency residual. Optimization path: a
(mu+lambda) evolution strategy.
"""

from .engine import SCHEME_NAME, VariationalRelaxer

METADATA = {
    "name": SCHEME_NAME,
    "paradigm": "variational self-consistency fixed point",
    "optimizer": "(mu+lambda) evolution strategy",
    "philosophy": "exploratory, self-consistency-driven, generative",
}

__all__ = ["VariationalRelaxer", "SCHEME_NAME", "METADATA"]
