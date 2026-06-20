"""cosmogenesis: a multi-scheme, parallel, adversarial universe-generation platform.

Three layers, each a clearly named subpackage:

- ``cosmogenesis.core``    the shared adversarial I/O contract (ParameterVector ->
  UniverseAssessment) every scheme implements.
- ``cosmogenesis.schemes`` one self-contained subpackage per scheme (paradigm +
  optimizer): ``analytic_compiler``, ``variational_relaxer``, ``minimal_axiom``.
- ``cosmogenesis.arena``   the platform that makes named theory lineages duel, be
  judged, patched/forked (never merged), and evolved with a Pareto ecosystem.

See docs/design/REPO_STRUCTURE.md.
"""

from .arena import (
    DuelReport,
    EvolutionReport,
    TheoryRegistry,
    TheorySpec,
    TournamentReport,
    evolve,
    load_theory,
    run_duel,
    run_tournament,
)
from .core import (
    ParameterVector,
    UniverseAssessment,
    apply_vector,
    vector_from_config,
)
from .schemes import build_scheme, list_schemes

__all__ = [
    # core contract
    "ParameterVector",
    "UniverseAssessment",
    "apply_vector",
    "vector_from_config",
    # schemes
    "build_scheme",
    "list_schemes",
    # arena platform
    "TheorySpec",
    "TheoryRegistry",
    "load_theory",
    "run_duel",
    "DuelReport",
    "run_tournament",
    "TournamentReport",
    "evolve",
    "EvolutionReport",
]

__version__ = "0.3.0"
