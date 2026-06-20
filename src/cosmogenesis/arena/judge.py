"""Judge: combines challenge + defense + verification into a structured decision.

Indifferent to which theory "wins"; applies deterministic rules and never merges.
"""

from __future__ import annotations

from .cards import (
    ChallengeCard,
    DefenseCard,
    DefenseStance,
    JudgeDecision,
    JudgeResult,
    Severity,
    VerificationResult,
)


class Judge:
    def decide(
        self,
        challenge: ChallengeCard,
        defense: DefenseCard,
        verification: VerificationResult,
    ) -> JudgeResult:
        decision, patch_required, fork = self._rule(challenge, defense, verification)
        return JudgeResult(
            judge_result_id=f"J-{challenge.challenge_id}",
            challenge_id=challenge.challenge_id,
            target_theory_id=challenge.target_theory_id,
            decision=decision,
            severity=challenge.severity,
            rationale=self._rationale(decision, verification),
            patch_required=patch_required,
            fork_recommended=fork,
        )

    @staticmethod
    def _rule(
        ch: ChallengeCard, df: DefenseCard, vr: VerificationResult
    ) -> tuple[JudgeDecision, bool, bool]:
        # Not reproducible -> reject (or ask for tests if no probe was given).
        if not vr.reproduced:
            if ch.probe_vector is None and df.stance == DefenseStance.REQUEST_TEST:
                return JudgeDecision.NEEDS_MORE_TESTS, False, False
            return JudgeDecision.CHALLENGE_REJECTED, False, False

        # Reproduced hard error -> must patch.
        if vr.is_hard_error:
            return JudgeDecision.PATCH_REQUIRED, True, False

        # Reproduced soft issue.
        if df.stance == DefenseStance.FORK_INSTEAD_OF_PATCH or ch.suggested_resolution == "fork":
            return JudgeDecision.FORK_RECOMMENDED, False, True
        if ch.severity in (Severity.CRITICAL, Severity.FATAL):
            # severe but not in the hard-type set: still requires a patch.
            return JudgeDecision.PATCH_REQUIRED, True, False
        return JudgeDecision.CHALLENGE_UPHELD_NO_PATCH, False, False

    @staticmethod
    def _rationale(decision: JudgeDecision, vr: VerificationResult) -> str:
        return f"{decision.value}; verifier: {vr.verifier_summary}"
