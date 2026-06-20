"""Rule-based, deterministic theory agents: attack rivals, defend self.

Each family attacks along the dimension its philosophy cares about, producing
schema-valid ChallengeCards (never free-form text). Defense follows the theory's
DefensePrior: defend by default, accept only hard reproducible errors.
"""

from __future__ import annotations

import itertools

import numpy as np

from ..core import ParameterVector, fragility_profile
from . import bridge
from .cards import (
    ChallengeCard,
    ChallengeType,
    DefenseCard,
    DefenseStance,
    EvidenceItem,
    EvidenceType,
    JudgeDecision,
    JudgeResult,
    Severity,
)
from .theory import TheorySpec

_counter = itertools.count(1)


def _cid() -> str:
    return f"CH-{next(_counter):05d}"


class TheoryAgent:
    """One agent per theory; behaviour parameterized by the theory's philosophy."""

    def __init__(self, theory: TheorySpec) -> None:
        self.theory = theory

    # ---------------- attack ----------------
    def attack(self, target: TheorySpec) -> list[ChallengeCard]:
        cards: list[ChallengeCard] = []
        target_seed = bridge.seed_vector(target)

        # Conservative families attack fragility & overclaiming.
        if self.theory.philosophy.conservatism >= 0.6:
            cards += self._attack_fragility(target, target_seed)

        # Exploratory/novel families attack overfitting to the standard universe.
        if self.theory.philosophy.novelty >= 0.6:
            cards += self._attack_overfitting(target)

        # Minimal-axiom families attack under-constrained / excess-parameter use.
        if self.theory.philosophy.bottom_up_derivation >= 0.7 and (
            self.theory.philosophy.conservatism < 0.6
        ):
            cards += self._attack_underconstrained(target, target_seed)

        return cards

    def _attack_fragility(self, target, seed) -> list[ChallengeCard]:
        profile = fragility_profile(seed, lambda v: bridge.assess(target, v).score, epsilon=0.05)
        if not profile:
            return []
        axis = max(profile, key=profile.get)
        drop = profile[axis]
        if drop < 0.25:
            return []
        idx = list(profile).index(axis)
        probe = seed.to_normalized()
        probe[idx] = min(1.0, probe[idx] + 0.05)
        return [
            ChallengeCard(
                challenge_id=_cid(),
                source_theory_id=self.theory.theory_id,
                target_theory_id=target.theory_id,
                challenge_type=ChallengeType.FRAGILITY,
                severity=Severity.MAJOR if drop > 0.5 else Severity.MINOR,
                summary=f"Champion is fragile along '{axis}' ({drop*100:.0f}% drop on 5% nudge).",
                detailed_argument="A robust universe theory should not collapse under a small "
                "perturbation of a fundamental constant.",
                evidence=[
                    EvidenceItem(
                        evidence_type=EvidenceType.NUMERICAL_RESULT,
                        summary="fragility profile",
                        content={k: round(v, 3) for k, v in profile.items()},
                    )
                ],
                probe_vector=list(ParameterVector.from_normalized(probe).values),
                expected_failure_mode="score drops sharply (fragile)",
                suggested_resolution="patch",
            )
        ]

    def _attack_overfitting(self, target) -> list[ChallengeCard]:
        rng = np.random.default_rng(abs(hash(target.theory_id)) % (2**32))
        base = np.array(bridge.seed_vector(target).to_normalized())
        feasible = 0
        for _ in range(6):
            probe = np.clip(base + rng.normal(0, 0.25, size=base.shape), 0, 1)
            if bridge.assess(target, ParameterVector.from_normalized(list(probe))).feasible:
                feasible += 1
        gp = feasible / 6
        if gp >= 0.34:
            return []
        return [
            ChallengeCard(
                challenge_id=_cid(),
                source_theory_id=self.theory.theory_id,
                target_theory_id=target.theory_id,
                challenge_type=ChallengeType.OVERFITTING_TO_STANDARD_UNIVERSE,
                severity=Severity.MINOR,
                summary=f"Low generative power ({gp:.2f}): theory mostly reproduces our universe.",
                detailed_argument="A creation engine should generate diverse self-consistent "
                "universes, not only the standard one.",
                evidence=[
                    EvidenceItem(
                        evidence_type=EvidenceType.ARGUMENT,
                        summary="generative power estimate",
                        content={"generative_power": gp},
                    )
                ],
                expected_failure_mode="low generative power",
                suggested_resolution="fork",
            )
        ]

    def _attack_underconstrained(self, target, seed) -> list[ChallengeCard]:
        out = bridge.assess(target, seed)
        free = int(out.diagnostics.get("free_parameters", len(seed.values)))
        if free <= 3:
            return []
        return [
            ChallengeCard(
                challenge_id=_cid(),
                source_theory_id=self.theory.theory_id,
                target_theory_id=target.theory_id,
                challenge_type=ChallengeType.UNDERCONSTRAINED_PARAMETER,
                severity=Severity.INFO,
                summary=f"Uses {free} free parameters; fewer axioms could suffice.",
                detailed_argument="Extra free parameters reduce falsifiability and explanatory "
                "economy.",
                expected_failure_mode="parameter economy",
                suggested_resolution="annotate",
            )
        ]

    # ---------------- defend ----------------
    def defend(self, challenges: list[ChallengeCard]) -> list[DefenseCard]:
        defenses = []
        for ch in challenges:
            defenses.append(self._defend_one(ch))
        return defenses

    def _defend_one(self, ch: ChallengeCard) -> DefenseCard:
        prior = self.theory.defense_prior
        # Philosophy clash but no hard error -> fork, don't overwrite.
        if ch.suggested_resolution == "fork" and prior.conservatism >= 0.6:
            stance = DefenseStance.FORK_INSTEAD_OF_PATCH
            summary = "Concern reflects a different philosophy; would fork rather than overwrite."
        elif ch.severity in (Severity.INFO, Severity.MINOR):
            stance = DefenseStance.REJECT
            summary = "Soft / stylistic concern below evidence threshold; defending lineage."
        elif ch.probe_vector is None:
            stance = DefenseStance.REQUEST_TEST
            summary = "No reproducible probe supplied; request a concrete counterexample."
        else:
            stance = DefenseStance.PARTIAL_ACCEPT
            summary = "Reproducible probe acknowledged; will accept a minimal patch if verified."
        return DefenseCard(
            defense_id=f"D-{ch.challenge_id}",
            challenge_id=ch.challenge_id,
            target_theory_id=self.theory.theory_id,
            stance=stance,
            summary=summary,
        )

    # ---------------- patch proposal hook (used by PatchGate) ----------------
    def accepts_patch(self, judge: JudgeResult) -> bool:
        return judge.decision in (JudgeDecision.PATCH_REQUIRED,)
