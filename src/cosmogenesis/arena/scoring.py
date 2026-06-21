"""Multi-objective scoring, Pareto front, family niches, novelty -- no single winner."""

from __future__ import annotations

import math
from collections import OrderedDict
from dataclasses import dataclass

import numpy as np
from pydantic import BaseModel, Field

from ..core import ParameterVector, fragility_profile, stable_seed
from . import bridge
from .cards import JudgeDecision, JudgeResult, PatchEvent, PatchOutcome
from .theory import TheorySpec

OBJECTIVES = (
    "validity",
    "physical_consistency",
    "benchmark_fit",
    "generative_power",
    "robustness",
    "novelty",
    "simplicity",
    "computational_efficiency",
)


@dataclass(frozen=True, slots=True)
class _NoveltyEntry:
    features: tuple[float, ...]
    generation: int


class NoveltyArchive:
    """Bounded, generation-decayed, feature-deduplicated novelty memory.

    Time is the deterministic generation counter -- never wall-clock time. Re-adding
    the same rounded behavior refreshes its generation instead of growing storage.
    """

    def __init__(
        self,
        capacity: int = 128,
        max_age_generations: int = 8,
        dedup_decimals: int = 8,
    ) -> None:
        if capacity < 1:
            raise ValueError("novelty archive capacity must be positive")
        if max_age_generations < 0:
            raise ValueError("novelty archive age must be non-negative")
        self.capacity = capacity
        self.max_age_generations = max_age_generations
        self.dedup_decimals = dedup_decimals
        self._entries: OrderedDict[tuple[float, ...], _NoveltyEntry] = OrderedDict()

    def _key(self, features: list[float]) -> tuple[float, ...]:
        return tuple(round(float(value), self.dedup_decimals) for value in features)

    def _prune(self, generation: int) -> None:
        expired = [
            key
            for key, entry in self._entries.items()
            if generation - entry.generation > self.max_age_generations
        ]
        for key in expired:
            del self._entries[key]
        while len(self._entries) > self.capacity:
            self._entries.popitem(last=False)

    def add(self, features: list[float], generation: int) -> None:
        self._prune(generation)
        key = self._key(features)
        self._entries[key] = _NoveltyEntry(tuple(float(v) for v in features), generation)
        self._entries.move_to_end(key)
        self._prune(generation)

    def features(self, generation: int) -> list[list[float]]:
        self._prune(generation)
        return [list(entry.features) for entry in self._entries.values()]

    def __len__(self) -> int:
        return len(self._entries)


class TheoryScoreVector(BaseModel):
    theory_id: str
    family: str
    version: str
    generation: int = 0

    validity: float = Field(ge=0.0, le=1.0)
    physical_consistency: float = Field(ge=0.0, le=1.0)
    benchmark_fit: float = Field(ge=0.0, le=1.0)
    generative_power: float = Field(ge=0.0, le=1.0)
    robustness: float = Field(ge=0.0, le=1.0)
    novelty: float = Field(default=0.0, ge=0.0, le=1.0)
    simplicity: float = Field(ge=0.0, le=1.0)
    computational_efficiency: float = Field(ge=0.0, le=1.0)
    unresolved_challenge_penalty: float = Field(default=0.0, ge=0.0, le=1.0)

    @property
    def display_score(self) -> float:
        return (
            0.20 * self.validity
            + 0.15 * self.physical_consistency
            + 0.15 * self.benchmark_fit
            + 0.15 * self.generative_power
            + 0.10 * self.robustness
            + 0.10 * self.novelty
            + 0.05 * self.simplicity
            + 0.05 * self.computational_efficiency
            - 0.05 * self.unresolved_challenge_penalty
        )


def _benchmark_fit(theory: TheorySpec) -> float:
    """How well the theory reproduces the standard universe at its seed point."""

    out = bridge.assess(theory, bridge.seed_vector(theory))
    return out.score


def _generative_power(theory: TheorySpec, samples: int = 6, run_seed: int = 0) -> float:
    """Fraction of perturbed parameter points that remain feasible (can it make
    varied yet self-consistent universes, not just our own)."""

    rng = np.random.default_rng(
        stable_seed(run_seed, "generative-power", theory.theory_id, theory.version)
    )
    base = np.array(bridge.seed_vector(theory).to_normalized())
    feasible = 0
    for _ in range(samples):
        probe = np.clip(base + rng.normal(0, 0.2, size=base.shape), 0, 1)
        vec = ParameterVector.from_normalized(list(probe))
        if bridge.assess(theory, vec).feasible:
            feasible += 1
    return feasible / samples


def _robustness(theory: TheorySpec) -> float:
    seed = bridge.seed_vector(theory)
    profile = fragility_profile(seed, lambda v: bridge.assess(theory, v).score, epsilon=0.05)
    return 1.0 - min(1.0, max(profile.values()) if profile else 0.0)


def _simplicity(theory: TheorySpec) -> float:
    """Fewer free parameters / axioms -> simpler. Engine-derived (QE-2026-102): each
    engine reports its real structural free-parameter count, not a YAML self-report."""

    out = bridge.assess(theory, bridge.seed_vector(theory))
    free = float(out.diagnostics.get("free_parameters", len(bridge.seed_vector(theory).values)))
    return 1.0 / (1.0 + math.log1p(free))


def _efficiency(theory: TheorySpec) -> float:
    """Computational efficiency derived from the engine's actual compute cost
    (QE-2026-102), not from the gameable ``theory.philosophy.computational_efficiency``
    self-report. Cheaper paradigms (closed-form) score higher."""

    out = bridge.assess(theory, bridge.seed_vector(theory))
    cost = float(out.diagnostics.get("compute_cost", 1.0))
    return 1.0 / (1.0 + math.log1p(max(cost, 0.0)))


def score_theory(
    theory: TheorySpec,
    generation: int = 0,
    unresolved_penalty: float = 0.0,
    invalidated: bool = False,
    run_seed: int = 0,
) -> TheoryScoreVector:
    seed = bridge.seed_vector(theory)
    out = bridge.assess(theory, seed)
    return TheoryScoreVector(
        theory_id=theory.theory_id,
        family=theory.family,
        version=theory.version,
        generation=generation,
        validity=0.0 if invalidated else (1.0 if out.feasible else 0.0),
        physical_consistency=(0.0 if invalidated else float(np.clip(1.0 - out.residual, 0.0, 1.0))),
        benchmark_fit=_benchmark_fit(theory),
        generative_power=_generative_power(theory, run_seed=run_seed),
        robustness=_robustness(theory),
        novelty=0.0,  # filled in against the archive by update_novelty
        simplicity=_simplicity(theory),
        computational_efficiency=_efficiency(theory),
        unresolved_challenge_penalty=(
            1.0 if invalidated else float(np.clip(unresolved_penalty, 0.0, 1.0))
        ),
    )


def adversarial_outcome(
    judge_results: list[JudgeResult], patch_events: list[PatchEvent]
) -> tuple[float, bool]:
    """Return unresolved-challenge penalty and invalidation state."""

    event_by_challenge = {event.based_on_challenge_id: event for event in patch_events}
    unresolved = 0.0
    considered = 0
    invalidated = False
    for result in judge_results:
        event = event_by_challenge.get(result.challenge_id)
        if event and event.outcome == PatchOutcome.INVALIDATED:
            invalidated = True
        if result.decision == JudgeDecision.THEORY_INVALIDATED:
            invalidated = True
        if result.decision == JudgeDecision.CHALLENGE_REJECTED:
            continue
        considered += 1
        if event and event.outcome in (PatchOutcome.PATCHED, PatchOutcome.FORKED):
            continue
        if result.decision == JudgeDecision.NEEDS_MORE_TESTS:
            unresolved += 0.5
        else:
            unresolved += 1.0
    if invalidated:
        return 1.0, True
    return (unresolved / considered if considered else 0.0), False


def pareto_dominates(a: TheoryScoreVector, b: TheoryScoreVector) -> bool:
    no_worse = all(getattr(a, o) >= getattr(b, o) for o in OBJECTIVES)
    penalty_ok = a.unresolved_challenge_penalty <= b.unresolved_challenge_penalty
    strictly_better = any(getattr(a, o) > getattr(b, o) for o in OBJECTIVES) or (
        a.unresolved_challenge_penalty < b.unresolved_challenge_penalty
    )
    return no_worse and strictly_better and penalty_ok


def pareto_front(scores: list[TheoryScoreVector]) -> list[TheoryScoreVector]:
    front = []
    for s in scores:
        if not any(pareto_dominates(other, s) for other in scores if other is not s):
            front.append(s)
    return front


def family_elites(
    scores: list[TheoryScoreVector], elites_per_family: int = 2
) -> dict[str, list[TheoryScoreVector]]:
    groups: dict[str, list[TheoryScoreVector]] = {}
    for s in scores:
        groups.setdefault(s.family, []).append(s)
    elites: dict[str, list[TheoryScoreVector]] = {}
    for family, members in groups.items():
        elites[family] = sorted(
            members,
            key=lambda s: (s.validity, s.physical_consistency, s.generative_power, s.robustness),
            reverse=True,
        )[:elites_per_family]
    return elites


def novelty_score(features: list[float], archive: list[list[float]], k: int = 3) -> float:
    if not archive:
        return 1.0
    arr = np.array(archive, dtype=float)
    f = np.array(features, dtype=float)
    span = arr.max(axis=0) - arr.min(axis=0)
    span[span == 0] = 1.0
    dists = np.linalg.norm((arr - f) / span, axis=1)
    nearest = np.sort(dists)[:k]
    return float(np.tanh(nearest.mean() / max(len(f) ** 0.5, 1.0)))
