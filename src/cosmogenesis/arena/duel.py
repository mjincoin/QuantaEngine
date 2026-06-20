"""A single adversarial duel between two theories (the v2 protocol)."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from pydantic import BaseModel, Field

from . import bridge
from .agents import TheoryAgent
from .cards import ChallengeCard, DefenseCard, JudgeResult, PatchEvent
from .judge import Judge
from .patchgate import PatchGate
from .registry import TheoryRegistry
from .theory import TheorySpec
from .verifier import Verifier


class DuelRound(BaseModel):
    round_id: int
    theory_a: str
    theory_b: str
    score_a: float
    score_b: float
    challenges: list[ChallengeCard] = Field(default_factory=list)
    defenses: list[DefenseCard] = Field(default_factory=list)
    judge_results: list[JudgeResult] = Field(default_factory=list)
    patch_events: list[PatchEvent] = Field(default_factory=list)


class DuelReport(BaseModel):
    theory_a_id: str
    theory_b_id: str
    rounds: list[DuelRound] = Field(default_factory=list)
    allow_merge: bool = False  # invariant, asserted below
    merged_theory_id: str | None = None  # always None: theories are never merged


def _one_direction(
    attacker: TheorySpec,
    defender: TheorySpec,
    verifier: Verifier,
    judge: Judge,
    gate: PatchGate,
) -> tuple[TheorySpec, list[ChallengeCard], list[DefenseCard], list[JudgeResult], list[PatchEvent]]:
    challenges = TheoryAgent(attacker).attack(defender)
    defenses = TheoryAgent(defender).defend(challenges)
    defense_by_ch = {d.challenge_id: d for d in defenses}
    judge_results: list[JudgeResult] = []
    decisions = []
    for ch in challenges:
        vr = verifier.reproduce(defender, ch)
        jr = judge.decide(ch, defense_by_ch[ch.challenge_id], vr)
        judge_results.append(jr)
        decisions.append((ch, jr))
    updated, events = gate.process(defender, decisions)
    return updated, challenges, defenses, judge_results, events


def run_duel(
    theory_a: TheorySpec,
    theory_b: TheorySpec,
    registry: TheoryRegistry,
    rounds: int = 1,
    history_dir: str | None = None,
) -> DuelReport:
    assert theory_a.lineage_policy.allow_merge is False
    assert theory_b.lineage_policy.allow_merge is False

    verifier, judge = Verifier(), Judge()
    gate = PatchGate(registry, history_dir=history_dir)
    cur_a, cur_b = theory_a, theory_b
    report = DuelReport(theory_a_id=theory_a.theory_id, theory_b_id=theory_b.theory_id)

    for r in range(rounds):
        # run both universes in parallel (engine evaluations release the GIL on numpy work)
        with ThreadPoolExecutor(max_workers=2) as pool:
            fa = pool.submit(lambda t=cur_a: bridge.assess(t, bridge.seed_vector(t)))
            fb = pool.submit(lambda t=cur_b: bridge.assess(t, bridge.seed_vector(t)))
            out_a, out_b = fa.result(), fb.result()

        # B attacks A, then A attacks B (sequential so patches land deterministically)
        cur_a, ch_ba, df_a, jr_ba, ev_a = _one_direction(cur_b, cur_a, verifier, judge, gate)
        cur_b, ch_ab, df_b, jr_ab, ev_b = _one_direction(cur_a, cur_b, verifier, judge, gate)

        report.rounds.append(
            DuelRound(
                round_id=r,
                theory_a=cur_a.theory_id,
                theory_b=cur_b.theory_id,
                score_a=out_a.score,
                score_b=out_b.score,
                challenges=ch_ba + ch_ab,
                defenses=df_a + df_b,
                judge_results=jr_ba + jr_ab,
                patch_events=ev_a + ev_b,
            )
        )

    return report
