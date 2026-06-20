"""Scheme: analytic_compiler.

Paradigm: forward closed-form effective-physics compilation (white-box, hard
windows). Optimization path: deterministic coordinate ascent.
"""

from .engine import SCHEME_NAME, AnalyticCompiler

METADATA = {
    "name": SCHEME_NAME,
    "paradigm": "forward closed-form compiler",
    "optimizer": "coordinate ascent",
    "philosophy": "conservative, interpretable, benchmark-faithful",
}

__all__ = ["AnalyticCompiler", "SCHEME_NAME", "METADATA"]
