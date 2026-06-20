"""Multi-objective scoring, Pareto front, family niches, novelty -- no single winner."""

from __future__ import annotations

import math

import numpy as np
from pydantic import BaseModel, Field

from ..core import ParameterVector, fragility_profile
from . import bridge
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


def _generative_power(theory: TheorySpec, samples: int = 6) -> float:
    """Fraction of perturbed parameter points that remain feasible (can it make
    varied yet self-consistent universes, not just our own)."""

    rng = np.random.default_rng(abs(hash(theory.theory_id)) % (2**32))
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
    """Fewer free parameters / axioms -> simpler. Minimal-axiom engines win here."""

    out = bridge.assess(theory, bridge.seed_vector(theory))
    free = float(out.diagnostics.get("free_parameters", len(bridge.seed_vector(theory).values)))
    return 1.0 / (1.0 + math.log1p(free))


def score_theory(
    theory: TheorySpec,
    generation: int = 0,
    unresolved_penalty: float = 0.0,
) -> TheoryScoreVector:
    seed = bridge.seed_vector(theory)
    out = bridge.assess(theory, seed)
    return TheoryScoreVector(
        theory_id=theory.theory_id,
        family=theory.family,
        version=theory.version,
        generation=generation,
        validity=1.0 if out.feasible else 0.0,
        physical_consistency=float(np.clip(1.0 - out.residual, 0.0, 1.0)),
        benchmark_fit=_benchmark_fit(theory),
        generative_power=_generative_power(theory),
        robustness=_robustness(theory),
        novelty=0.0,  # filled in against the archive by update_novelty
        simplicity=_simplicity(theory),
        computational_efficiency=theory.philosophy.computational_efficiency,
        unresolved_challenge_penalty=float(np.clip(unresolved_penalty, 0.0, 1.0)),
    )


def pareto_dominates(a: TheoryScoreVector, b: TheoryScoreVector) -> bool:
    no_worse = all(getattr(a, o) >= getattr(b, o) for o in OBJECTIVES)
    strictly_better = any(getattr(a, o) > getattr(b, o) for o in OBJECTIVES)
    penalty_ok = a.unresolved_challenge_penalty <= b.unresolved_challenge_penalty
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
