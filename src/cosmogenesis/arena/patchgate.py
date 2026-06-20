"""PatchGate: applies judge decisions locally. Patches, forks, or leaves a theory
untouched -- but NEVER merges two theories, and always preserves the parent."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from ..core import ParameterVector
from . import bridge
from .cards import ChallengeCard, JudgeDecision, JudgeResult, PatchEvent, PatchOutcome
from .registry import TheoryRegistry
from .theory import TheorySpec


class PatchGate:
    def __init__(self, registry: TheoryRegistry, history_dir: str | Path | None = None) -> None:
        self.registry = registry
        self.history_dir = Path(history_dir) if history_dir else None

    def process(
        self,
        target: TheorySpec,
        decisions: list[tuple[ChallengeCard, JudgeResult]],
    ) -> tuple[TheorySpec, list[PatchEvent]]:
        assert target.lineage_policy.allow_merge is False, "merging theories is forbidden"
        current = target
        events: list[PatchEvent] = []

        for challenge, judge in decisions:
            if judge.decision == JudgeDecision.PATCH_REQUIRED and current.lineage_policy.allow_patch:
                current, event = self._patch(current, challenge)
            elif judge.decision == JudgeDecision.FORK_RECOMMENDED and current.lineage_policy.allow_fork:
                event = self._fork(current, challenge)
            elif judge.decision == JudgeDecision.THEORY_INVALIDATED:
                event = PatchEvent(
                    theory_id=current.theory_id,
                    based_on_challenge_id=challenge.challenge_id,
                    outcome=PatchOutcome.INVALIDATED,
                    summary="theory cannot run / core axioms contradictory",
                )
            else:
                event = PatchEvent(
                    theory_id=current.theory_id,
                    based_on_challenge_id=challenge.challenge_id,
                    outcome=PatchOutcome.UNCHANGED,
                    summary=f"no local change ({judge.decision.value})",
                )
            events.append(event)
            self._record(event)

        self.registry.add(current)
        return current, events

    # --- patch: minimal, in-place, bump patch version, parent identity kept ---
    def _patch(self, theory: TheorySpec, challenge: ChallengeCard) -> tuple[TheorySpec, PatchEvent]:
        robust_seed = self._robust_reseed(theory)
        new_version = theory.bump_patch()
        patched = theory.model_copy(
            update={"version": new_version, "seed_vector": list(robust_seed.values)}
        )
        event = PatchEvent(
            theory_id=theory.theory_id,
            based_on_challenge_id=challenge.challenge_id,
            outcome=PatchOutcome.PATCHED,
            summary=f"re-seeded to a more robust point; {theory.version} -> {new_version}",
            new_version=new_version,
        )
        return patched, event

    # --- fork: NEW lineage, parent preserved unchanged ---
    def _fork(self, theory: TheorySpec, challenge: ChallengeCard) -> PatchEvent:
        ctype = challenge.challenge_type.value
        # Rate-limit: never fork a fork, and fork each root at most once per concern.
        already = theory.parent_id is not None or any(
            t.parent_id == theory.theory_id and ctype in t.name for t in self.registry.all()
        )
        if already:
            return PatchEvent(
                theory_id=theory.theory_id,
                based_on_challenge_id=challenge.challenge_id,
                outcome=PatchOutcome.UNCHANGED,
                summary=f"concern '{ctype}' already addressed by an existing fork; no new lineage",
            )
        child_id = self.registry.next_theory_id()
        rng = np.random.default_rng(abs(hash(child_id)) % (2**32))
        base = np.array(bridge.seed_vector(theory).to_normalized())
        explored = np.clip(base + rng.normal(0, 0.25, size=base.shape), 0, 1)
        child = theory.model_copy(
            update={
                "theory_id": child_id,
                "name": f"{theory.name} (fork: {challenge.challenge_type.value})",
                "version": "0.1.0",
                "parent_id": theory.theory_id,
                "family": f"{theory.family}_explore",
                "seed_vector": list(ParameterVector.from_normalized(list(explored)).values),
            }
        )
        self.registry.add(child)  # parent stays in the registry, untouched
        return PatchEvent(
            theory_id=theory.theory_id,
            based_on_challenge_id=challenge.challenge_id,
            outcome=PatchOutcome.FORKED,
            summary=f"forked child {child_id} to absorb concern without altering parent philosophy",
            child_theory_id=child_id,
        )

    def _robust_reseed(self, theory: TheorySpec, samples: int = 24) -> ParameterVector:
        """Pick the nearby point maximizing worst-case score over a small ball."""

        rng = np.random.default_rng(abs(hash(theory.theory_id + theory.version)) % (2**32))
        base = np.array(bridge.seed_vector(theory).to_normalized())
        best_vec = bridge.seed_vector(theory)
        best_robust = -1.0
        for _ in range(samples):
            cand = np.clip(base + rng.normal(0, 0.12, size=base.shape), 0, 1)
            cand_vec = ParameterVector.from_normalized(list(cand))
            worst = min(
                bridge.assess(
                    theory,
                    ParameterVector.from_normalized(list(np.clip(cand + d, 0, 1))),
                ).score
                for d in (np.zeros_like(cand), *(_unit_perturbs(cand.shape[0], 0.05)))
            )
            if worst > best_robust:
                best_robust, best_vec = worst, cand_vec
        return best_vec

    def _record(self, event: PatchEvent) -> None:
        if self.history_dir is None:
            return
        self.history_dir.mkdir(parents=True, exist_ok=True)
        path = self.history_dir / f"{event.theory_id}.history.jsonl"
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(event.model_dump(), ensure_ascii=False) + "\n")


def _unit_perturbs(dim: int, eps: float):
    for i in range(dim):
        for sign in (+1.0, -1.0):
            p = np.zeros(dim)
            p[i] = sign * eps
            yield p
