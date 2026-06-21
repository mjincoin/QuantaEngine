"""Tests for the cosmogenesis.arena parallel adversarial platform."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from cosmogenesis.arena import bridge as engines
from cosmogenesis.arena import run_duel, run_tournament, scoring
from cosmogenesis.arena.agents import TheoryAgent
from cosmogenesis.arena.cards import (
    ChallengeCard,
    ChallengeType,
    JudgeDecision,
    Severity,
)
from cosmogenesis.arena.evolution import evolve
from cosmogenesis.arena.judge import Judge
from cosmogenesis.arena.patchgate import PatchGate
from cosmogenesis.arena.registry import TheoryRegistry
from cosmogenesis.arena.verifier import Verifier
from cosmogenesis.core import ParameterVector

THEORIES = "theories"


@pytest.fixture
def registry():
    return TheoryRegistry.from_dir(THEORIES)


# ---------------- theory identity ----------------
def test_registry_loads_three_families(registry):
    assert len(registry.all()) == 3
    assert registry.families() == {"conservative_eft", "exploratory_generative", "minimal_axiom"}


def test_theory_version_bumps(registry):
    t = registry.get("T-0001")
    assert t.bump_patch() == "0.1.1"
    assert t.bump_minor() == "0.2.0"


def test_next_theory_id(registry):
    assert registry.next_theory_id() == "T-0004"


def test_lineage_policy_forbids_merge(registry):
    for t in registry.all():
        assert t.lineage_policy.allow_merge is False


# ---------------- three distinct paradigms ----------------
def test_three_engines_differ(registry):
    v = ParameterVector([1.0, 50.0, 1.0, 1.0, -8.68])  # strong gravity
    scores = {t.engine: engines.assess(t, v).score for t in registry.all()}
    assert len(set(round(s, 3) for s in scores.values())) >= 2  # they disagree


def test_minimal_axiom_reports_three_free_params(registry):
    t = registry.get("T-0003")
    out = engines.assess(t, engines.seed_vector(t))
    assert out.diagnostics["free_parameters"] == 3


# ---------------- scoring / pareto / niche ----------------
def test_score_vector_in_range(registry):
    s = scoring.score_theory(registry.get("T-0001"))
    for obj in scoring.OBJECTIVES:
        assert 0.0 <= getattr(s, obj) <= 1.0
    assert 0.0 <= s.display_score <= 1.0


def test_pareto_dominance():
    a = scoring.TheoryScoreVector(
        theory_id="A", family="f", version="0.1.0", validity=1, physical_consistency=1,
        benchmark_fit=1, generative_power=1, robustness=1, novelty=1, simplicity=1,
        computational_efficiency=1,
    )
    b = scoring.TheoryScoreVector(
        theory_id="B", family="f", version="0.1.0", validity=0.5, physical_consistency=0.5,
        benchmark_fit=0.5, generative_power=0.5, robustness=0.5, novelty=0.5, simplicity=0.5,
        computational_efficiency=0.5,
    )
    assert scoring.pareto_dominates(a, b)
    assert not scoring.pareto_dominates(b, a)


def test_pareto_front_and_family_elites(registry):
    scores = [scoring.score_theory(t) for t in registry.all()]
    front = scoring.pareto_front(scores)
    assert front  # non-empty
    elites = scoring.family_elites(scores, elites_per_family=1)
    assert set(elites) == registry.families()


def test_novelty_archive_empty_gives_one():
    assert scoring.novelty_score([1.0, 2.0], []) == 1.0


# ---------------- verifier / agents / judge ----------------
def test_verifier_benchmark(registry):
    bench = Verifier().benchmark(registry.get("T-0001"))
    assert bench["standard_feasible"] is True
    assert bench["standard_score"] > 0.9
    # the analytic compiler must at least score the extreme universes lower
    assert bench["big_alpha_degrades"] is True
    assert bench["huge_gravity_degrades"] is True


def test_agent_attack_is_schema_valid(registry):
    # conservative attacks exploratory (fragility)
    cards = TheoryAgent(registry.get("T-0001")).attack(registry.get("T-0002"))
    for c in cards:
        assert isinstance(c, ChallengeCard)
        assert c.source_theory_id == "T-0001"
        assert c.target_theory_id == "T-0002"


def test_judge_rejects_unreproduced(registry):
    ch = ChallengeCard(
        challenge_id="CH-test",
        source_theory_id="T-0003",
        target_theory_id="T-0001",
        challenge_type=ChallengeType.REPRODUCIBLE_COUNTEREXAMPLE,
        severity=Severity.CRITICAL,
        summary="bogus",
        probe_vector=list(engines.seed_vector(registry.get("T-0001")).values),
        expected_failure_mode="infeasible",
    )
    defense = TheoryAgent(registry.get("T-0001")).defend([ch])[0]
    vr = Verifier().reproduce(registry.get("T-0001"), ch)
    jr = Judge().decide(ch, defense, vr)
    # standard universe is feasible -> the "infeasible" claim cannot reproduce -> rejected
    assert not vr.reproduced
    assert jr.decision == JudgeDecision.CHALLENGE_REJECTED


# ---------------- patchgate: no-merge, fork preserves parent ----------------
def test_fork_preserves_parent_and_never_merges(registry):
    gate = PatchGate(registry)
    target = registry.get("T-0002")
    ch = ChallengeCard(
        challenge_id="CH-fork",
        source_theory_id="T-0003",
        target_theory_id="T-0002",
        challenge_type=ChallengeType.OVERFITTING_TO_STANDARD_UNIVERSE,
        severity=Severity.MINOR,
        summary="low generative power",
        expected_failure_mode="low generative power",
        suggested_resolution="fork",
    )
    from cosmogenesis.arena.cards import JudgeResult

    jr = JudgeResult(
        judge_result_id="J-fork", challenge_id="CH-fork", target_theory_id="T-0002",
        decision=JudgeDecision.FORK_RECOMMENDED, severity=Severity.MINOR, rationale="x",
        fork_recommended=True,
    )
    _, events = gate.process(target, [(ch, jr)])
    assert "T-0002" in registry  # parent preserved
    assert events[0].merged is False
    assert events[0].outcome.value in ("forked", "unchanged")
    if events[0].outcome.value == "forked":
        assert events[0].child_theory_id in registry
        # second identical fork is rate-limited
        _, events2 = gate.process(target, [(ch, jr)])
        assert events2[0].outcome.value == "unchanged"


# ---------------- duel / tournament / evolution ----------------
def test_duel_no_merge(registry):
    rep = run_duel(registry.get("T-0001"), registry.get("T-0002"), registry, rounds=1)
    assert rep.allow_merge is False
    assert rep.merged_theory_id is None
    assert "T-0001" in registry and "T-0002" in registry


def test_tournament_keeps_families(registry):
    rep = run_tournament(registry.all(), registry, rounds=1)
    assert len(rep.pareto_front) >= 1
    assert set(rep.family_elites) >= {"conservative_eft", "exploratory_generative", "minimal_axiom"}


def test_evolution_parallel_no_collapse(registry, tmp_path):
    rep = evolve(
        registry.all(), registry, generations=2, rounds=1, min_families=3,
        population_size=10, out_dir=tmp_path,
    )
    assert rep.allow_merge is False
    assert len(rep.final_families) >= 3  # anti-collapse: multiple lineages survive
    for root in ("T-0001", "T-0002", "T-0003"):
        assert root in registry  # original lineages preserved
    assert (tmp_path / "evolution_report.json").exists()
    assert (tmp_path / "evolution_report.md").exists()


def test_evolution_default_does_not_touch_repo(tmp_path):
    """Without lineage_root/plan_dir, evolve must not write any durable history."""
    import shutil

    src = tmp_path / "theories"
    shutil.copytree("theories", src)
    for h in src.rglob("history.jsonl"):
        h.unlink()  # start from a clean copy
    reg = TheoryRegistry.from_dir(str(src))
    evolve(reg.all(), reg, generations=1, min_families=3, population_size=8)
    assert not list(src.rglob("history.jsonl"))  # nothing written by default


def test_ledger_persists_history_and_plan(tmp_path):
    """With lineage_root + plan_dir, each lineage accrues history and a plan is made."""
    import shutil

    src = tmp_path / "theories"
    plans = tmp_path / "plans_iter"
    shutil.copytree("theories", src)
    for h in src.rglob("history.jsonl"):
        h.unlink()  # start from a clean copy so record counts are deterministic
    reg = TheoryRegistry.from_dir(str(src))
    rep = evolve(
        reg.all(), reg, generations=2, min_families=3, population_size=8,
        lineage_root=str(src), plan_dir=str(plans), persist_forks=True,
    )
    # per-lineage history.jsonl with 2 generation records for each seed lineage
    for tid in ("T-0001", "T-0002", "T-0003"):
        hist = list(src.glob(f"{tid}_*/history.jsonl"))
        assert hist, f"missing history for {tid}"
        records = [json.loads(line) for line in hist[0].read_text().splitlines()]
        assert len(records) == 2
        assert records[0]["theory_id"] == tid
        assert "scores" in records[0] and "timestamp" in records[0]
    # an auto-generated next-iteration plan exists
    assert rep.iteration_plan is not None
    plan = Path(rep.iteration_plan)
    assert plan.exists() and "Next-iteration optimization plan" in plan.read_text()
