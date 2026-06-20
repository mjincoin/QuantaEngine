"""Deterministic verifier: reproduces challenges and runs benchmarks. No opinions."""

from __future__ import annotations

from ..core import ParameterVector
from . import bridge
from .cards import (
    ChallengeCard,
    ChallengeType,
    Severity,
    VerificationResult,
)
from .theory import TheorySpec

# Challenge types that constitute HARD errors when reproduced.
_HARD_TYPES = {
    ChallengeType.FAILED_BENCHMARK,
    ChallengeType.REPRODUCIBLE_COUNTEREXAMPLE,
    ChallengeType.INTERNAL_CONTRADICTION,
    ChallengeType.NUMERICAL_INSTABILITY,
}


class Verifier:
    """Independent arbiter for hard physics & benchmark facts."""

    def reproduce(self, target: TheorySpec, challenge: ChallengeCard) -> VerificationResult:
        measured: dict[str, float | bool] = {}
        reproduced = False

        if challenge.probe_vector is not None:
            probe = ParameterVector(list(challenge.probe_vector))
            out = bridge.assess(target, probe)
            seed_out = bridge.assess(target, bridge.seed_vector(target))
            measured = {
                "probe_score": out.score,
                "probe_feasible": out.feasible,
                "probe_residual": out.residual,
                "seed_score": seed_out.score,
            }
            mode = (challenge.expected_failure_mode or "").lower()
            if "infeasible" in mode or "counterexample" in mode:
                reproduced = not out.feasible
            elif "fragile" in mode or "drop" in mode:
                reproduced = (seed_out.score - out.score) / max(seed_out.score, 1e-9) > 0.3
            elif "residual" in mode or "inconsistent" in mode:
                reproduced = out.residual > 0.1
            else:
                reproduced = out.score < 0.5
        else:
            # No probe: only "overfitting / low generative power" style soft claims,
            # checked structurally.
            gp = _generative_power_quick(target)
            measured = {"generative_power": gp}
            if challenge.challenge_type in (
                ChallengeType.OVERFITTING_TO_STANDARD_UNIVERSE,
                ChallengeType.LOW_GENERATIVE_POWER,
            ):
                reproduced = gp < 0.34

        is_hard = reproduced and challenge.challenge_type in _HARD_TYPES and (
            challenge.severity in (Severity.CRITICAL, Severity.FATAL)
        )
        summary = (
            f"reproduced={reproduced}; hard={is_hard}; "
            f"type={challenge.challenge_type.value}; measured={measured}"
        )
        return VerificationResult(
            verification_id=f"V-{challenge.challenge_id}",
            challenge_id=challenge.challenge_id,
            target_theory_id=target.theory_id,
            reproduced=reproduced,
            is_hard_error=is_hard,
            measured=measured,
            verifier_summary=summary,
        )

    def benchmark(self, theory: TheorySpec) -> dict[str, float | bool]:
        """Standard universe should be feasible; extreme universes should score worse.

        Feasibility flips are engine-specific (the analytic compiler keeps a
        "feasible" flag while only lowering the score; the minimal-axiom engine is
        deliberately insensitive to some knobs), so the universal signal is the
        SCORE degradation, not the boolean flag.
        """

        seed = bridge.seed_vector(theory)
        big_alpha = ParameterVector([3.0, *seed.values[1:]])
        huge_gravity = ParameterVector([seed.values[0], 100.0, *seed.values[2:]])
        std = bridge.assess(theory, seed)
        s_alpha = bridge.assess(theory, big_alpha).score
        s_grav = bridge.assess(theory, huge_gravity).score
        return {
            "standard_feasible": std.feasible,
            "standard_score": std.score,
            "big_alpha_score": s_alpha,
            "huge_gravity_score": s_grav,
            "big_alpha_degrades": s_alpha < std.score - 0.05,
            "huge_gravity_degrades": s_grav < std.score - 0.05,
        }


def _generative_power_quick(theory: TheorySpec, samples: int = 5) -> float:
    import numpy as np

    rng = np.random.default_rng(7)
    base = np.array(bridge.seed_vector(theory).to_normalized())
    ok = 0
    for _ in range(samples):
        probe = np.clip(base + rng.normal(0, 0.2, size=base.shape), 0, 1)
        if bridge.assess(theory, ParameterVector.from_normalized(list(probe))).feasible:
            ok += 1
    return ok / samples
