"""QuantaEngine: from fundamental quanta to generated universes."""

from .engine import QuantaEngine, UniverseResult
from .laws import LawBook, minimal_lawbook
from .params import UniverseParams

__all__ = ["LawBook", "QuantaEngine", "UniverseParams", "UniverseResult", "minimal_lawbook"]
__version__ = "0.1.0"
