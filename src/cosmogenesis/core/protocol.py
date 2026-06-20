"""The contract every scheme implements, plus shared analysis helpers."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from quanta_engine.core.schema import UniverseConfig

from .assessment import UniverseAssessment
from .parameters import AXES, ParameterVector


@runtime_checkable
class UniverseScheme(Protocol):
    """A self-contained universe-generation paradigm.

    The adversarial I/O is deliberately minimal and identical across schemes:
    a ``ParameterVector`` goes in, a ``UniverseAssessment`` comes out, and the
    scheme can iteratively optimize within the shared parameter space.
    """

    name: str

    def assess(self, vector: ParameterVector) -> UniverseAssessment: ...

    def base_score(self, vector: ParameterVector) -> float: ...

    def optimize(self, start: ParameterVector, budget: int) -> ParameterVector: ...


class BaseEngine:
    """Common bookkeeping for a scheme engine (no adversarial penalties here --
    cross-scheme pressure lives entirely in ``cosmogenesis.arena``)."""

    name = "base"

    def __init__(self, base_config: UniverseConfig) -> None:
        self.base_config = base_config
        self.last_champion: ParameterVector = ParameterVector.default()

    def assess(self, vector: ParameterVector) -> UniverseAssessment:  # pragma: no cover
        raise NotImplementedError

    def base_score(self, vector: ParameterVector) -> float:
        return self.assess(vector).score

    # the objective an optimizer maximizes (schemes may override).
    def objective(self, vector: ParameterVector) -> float:
        return self.base_score(vector)

    def optimize(self, start: ParameterVector, budget: int) -> ParameterVector:  # pragma: no cover
        raise NotImplementedError


def fragility_profile(
    champion: ParameterVector,
    score_fn,
    epsilon: float = 0.05,
) -> dict[str, float]:
    """Per-axis worst relative score drop under a +/- epsilon normalized nudge.

    The largest entry marks the axis along which a universe is least robust.
    Shared by scoring, agents, and optimizers.
    """

    base = max(score_fn(champion), 1e-9)
    normalized = champion.to_normalized()
    profile: dict[str, float] = {}
    for i, axis in enumerate(AXES):
        worst = 0.0
        for sign in (+1.0, -1.0):
            probe = list(normalized)
            probe[i] = min(1.0, max(0.0, probe[i] + sign * epsilon))
            s = score_fn(ParameterVector.from_normalized(probe))
            worst = max(worst, max(0.0, (base - s) / base))
        profile[axis.name] = worst
    return profile
