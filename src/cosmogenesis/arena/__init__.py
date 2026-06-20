"""The parallel adversarial platform: theories duel, are judged, and evolve --
but are never merged into a single winner."""

from .duel import DuelReport, run_duel
from .evolution import EvolutionReport, evolve
from .registry import TheoryRegistry
from .theory import TheorySpec, load_theory, save_theory
from .tournament import TournamentReport, run_tournament

__all__ = [
    "TheorySpec",
    "TheoryRegistry",
    "load_theory",
    "save_theory",
    "run_duel",
    "DuelReport",
    "run_tournament",
    "TournamentReport",
    "evolve",
    "EvolutionReport",
]
