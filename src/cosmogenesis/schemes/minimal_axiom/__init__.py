"""Scheme: minimal_axiom.

Paradigm: feasibility from the fewest dimensionless numbers via anthropic
inequalities (Carr-Rees). Optimization path: cheap coordinate hill-climb.
"""

from .engine import SCHEME_NAME, MinimalAxiom

METADATA = {
    "name": SCHEME_NAME,
    "paradigm": "minimal-axiom dimensional analysis",
    "optimizer": "coordinate hill-climb",
    "philosophy": "fewest parameters, maximal falsifiability, order-of-magnitude",
}

__all__ = ["MinimalAxiom", "SCHEME_NAME", "METADATA"]
