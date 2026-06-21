"""Regression tests for remediation round B.

QE-2026-101: each scheme independently reconsiders a rival's suggestion under its
OWN objective and adopts it only if it independently verifies an improvement --
never blindly, never merged.
QE-2026-102: scoring objectives are engine-derived/measured, not self-declared in
theory.yaml.
"""

from __future__ import annotations

import math

import pytest

from cosmogenesis import schemes
from cosmogenesis.arena import bridge, scoring
from cosmogenesis.arena.cards import (
    ChallengeCard,
    ChallengeType,
    JudgeDecision,
    JudgeResult,
    Severity,
)
from cosmogenesis.arena.evolution import evolve
from cosmogenesis.arena.patchgate import ConflictAction, PatchGate
from cosmogenesis.arena.registry import TheoryRegistry
from cosmogenesis.core import ParameterVector
from cosmogenesis.schemes import build_scheme
from quanta_engine.core.schema import load_config

CONFIG = "configs/standard_universe.yaml"


@pytest.fixture(scope="module")
def cfg():
    return load_config(CONFIG)


@pytest.fixture
def registry():
    return TheoryRegistry.from_dir("theories")


# ---------------- QE-2026-101: independent consider loop ----------------
def test_suggestion_adopted_when_self_verified_improvement(cfg):
    engine = build_scheme("analytic_compiler", cfg)
    poor = ParameterVector([0.5, 12.0, 1.0, 5.0, -7.5])  # low own score
    good = ParameterVector.default()  # standard universe, high own score
    decision = engine.consider(poor, good)
    assert decision.adopt is True
    assert decision.own_after > decision.own_before
    # the adopted champion is at least as good (under our OWN objective) as the suggestion
    assert engine.objective(decision.champion) >= engine.objective(good) - 1e-9


def test_suggestion_rejected_when_no_self_verified_improvement(cfg):
    engine = build_scheme("analytic_compiler", cfg)
    good = ParameterVector.default()  # already near our own optimum
    bad = ParameterVector([3.0, 100.0, 2.0, 40.0, -11.0])  # clearly worse for us
    decision = engine.consider(good, bad)
    assert decision.adopt is False
    # rejecting keeps our OWN current champion -- never adopts a worse rival point
    assert decision.champion.values == good.values
    assert "no" in decision.reason.lower() or "keep" in decision.reason.lower()


def test_consider_is_deterministic(cfg):
    engine = build_scheme("analytic_compiler", cfg)
    poor = ParameterVector([0.5, 12.0, 1.0, 5.0, -7.5])
    good = ParameterVector.default()
    d1 = engine.consider(poor, good)
    d2 = build_scheme("analytic_compiler", cfg).consider(poor, good)
    assert d1.adopt == d2.adopt
    assert d1.champion.values == pytest.approx(d2.champion.values)


def test_bridge_consider_never_merges(registry):
    """Considering a rival's suggestion only updates the recipient's own champion."""
    target = registry.get("T-0001")
    rival_suggestion = ParameterVector([0.5, 12.0, 1.0, 5.0, -7.5])
    decision = bridge.consider(target, rival_suggestion)
    # decision concerns only the recipient; there is no merged theory.
    assert isinstance(decision.adopt, bool)
    assert len(decision.champion.values) == len(rival_suggestion.values)


def test_duel_records_independent_considerations(registry):
    from cosmogenesis.arena import run_duel

    rep = run_duel(registry.get("T-0001"), registry.get("T-0003"), registry, rounds=1)
    considered = [c for rd in rep.rounds for c in rd.considerations]
    # every recorded consideration is an independent verdict with before/after evidence
    for c in considered:
        assert c.target_theory_id and c.source_theory_id
        assert isinstance(c.adopted, bool)
        assert c.reason
    assert rep.allow_merge is False


# ---------------- QE-2026-102: measured, not declared ----------------
def test_efficiency_is_engine_derived_not_self_declared(cfg, registry):
    """computational_efficiency must come from the engine's actual cost, not from a
    gameable theory.yaml field."""
    theory = registry.get("T-0001")
    base = scoring.score_theory(theory).computational_efficiency
    # mutate the self-declared philosophy value; the score must NOT follow it.
    gamed = theory.model_copy(deep=True)
    gamed.philosophy.computational_efficiency = 0.01
    assert scoring.score_theory(gamed).computational_efficiency == pytest.approx(base)
    gamed.philosophy.computational_efficiency = 0.99
    assert scoring.score_theory(gamed).computational_efficiency == pytest.approx(base)


def test_efficiency_differs_across_paradigms(registry):
    effs = {t.engine: scoring.score_theory(t).computational_efficiency for t in registry.all()}
    # the minimal-axiom closed-form paradigm must be more efficient than the full
    # analytic pipeline -- a real, engine-derived trade-off.
    assert effs["minimal_axiom"] > effs["analytic_compiler"]


def test_simplicity_reflects_real_free_parameters(registry):
    simp = {t.engine: scoring.score_theory(t).simplicity for t in registry.all()}
    assert simp["minimal_axiom"] > simp["analytic_compiler"]


def test_compute_cost_present_in_diagnostics(cfg):
    for name in ("analytic_compiler", "variational_relaxer", "minimal_axiom"):
        out = build_scheme(name, cfg).assess(ParameterVector.default())
        assert "compute_cost" in out.diagnostics
        assert out.diagnostics["compute_cost"] > 0
        assert "free_parameters" in out.diagnostics


# ---------------- QE-2026-103: calibrated physics windows ----------------
def test_standard_universe_within_calibrated_ranges(cfg):
    expected_scores = {
        "analytic_compiler": (0.98, 1.0),
        "variational_relaxer": (0.82, 0.90),
        "minimal_axiom": (0.88, 0.96),
    }
    for name, (lower, upper) in expected_scores.items():
        engine = build_scheme(name, cfg)
        report = engine.threshold_sensitivity(ParameterVector.default())
        assert lower <= report["baseline_score"] <= upper
        assert report["thresholds"], f"{name} exposes no calibrated thresholds"
        for threshold, evidence in report["thresholds"].items():
            assert evidence["calibrated_min"] <= evidence["nominal"] <= evidence["calibrated_max"]
            assert math.isfinite(evidence["score_low"])
            assert math.isfinite(evidence["score_high"])
            assert evidence["max_abs_score_delta"] >= 0.0, threshold


# ---------------- QE-2026-104: deterministic assess memoization ----------------
def test_assess_memoized_and_deterministic(registry, monkeypatch):
    bridge.clear_assess_cache()
    original = bridge.build_engine
    calls = 0

    def counted(theory):
        nonlocal calls
        calls += 1
        return original(theory)

    monkeypatch.setattr(bridge, "build_engine", counted)
    theory = registry.get("T-0001")
    vector = ParameterVector.default()
    first = bridge.assess(theory, vector)
    # Below the documented rounding precision: same physical cache key.
    near = ParameterVector([vector.values[0] + 1.0e-13, *vector.values[1:]])
    second = bridge.assess(theory, near)
    assert first.to_dict() == second.to_dict()
    assert calls == 1
    # A new theory version must never reuse the old assessment.
    bridge.assess(theory.model_copy(update={"version": theory.bump_patch()}), vector)
    assert calls == 2


# ---------------- QE-2026-105: bounded/decayed novelty archive ----------------
def test_novelty_archive_bounded_no_collapse():
    archive = scoring.NoveltyArchive(capacity=8, max_age_generations=3, dedup_decimals=6)
    scores = []
    for generation in range(30):
        features = [float(generation), float(generation % 5), 0.5]
        scores.append(scoring.novelty_score(features, archive.features(generation)))
        archive.add(features, generation)
        archive.add(features, generation)  # duplicate refreshes; it does not grow the archive
        assert len(archive) <= 8
    assert len(archive) <= 4  # generational expiry is tighter than capacity here
    assert min(scores[-10:]) > 0.0


# ---------------- QE-2026-106: drop-in schemes + conflict strategy ----------------
def test_new_scheme_discovered_without_central_edit(cfg, tmp_path, monkeypatch):
    package_root = tmp_path / "schemes"
    package = package_root / "drop_in_test"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text(
        "from cosmogenesis.core import BaseEngine, UniverseAssessment\n"
        "class DropInTest(BaseEngine):\n"
        "    name = 'drop_in_test'\n"
        "    def assess(self, vector):\n"
        "        return UniverseAssessment(self.name, 0.5, True)\n"
        "    def optimize(self, start, budget):\n"
        "        return start\n"
        "METADATA = {'name': 'drop_in_test', 'paradigm': 'test', 'optimizer': 'none'}\n"
    )
    original_paths = list(schemes.__path__)
    monkeypatch.setattr(schemes, "__path__", [*original_paths, str(package_root)])
    schemes.refresh_scheme_registry()
    try:
        assert "drop_in_test" in schemes.list_schemes()
        assert schemes.build_scheme("drop_in_test", cfg).name == "drop_in_test"
    finally:
        monkeypatch.setattr(schemes, "__path__", original_paths)
        schemes.refresh_scheme_registry()


def test_patchgate_uses_injected_conflict_strategy(registry):
    class KeepUnchanged:
        def choose(self, target, challenge, judge):
            return ConflictAction.UNCHANGED

    target = registry.get("T-0001")
    challenge = ChallengeCard(
        challenge_id="CH-strategy",
        source_theory_id="T-0002",
        target_theory_id=target.theory_id,
        challenge_type=ChallengeType.REPRODUCIBLE_COUNTEREXAMPLE,
        severity=Severity.MAJOR,
        summary="strategy injection",
    )
    judge = JudgeResult(
        judge_result_id="J-strategy",
        challenge_id=challenge.challenge_id,
        target_theory_id=target.theory_id,
        decision=JudgeDecision.PATCH_REQUIRED,
        severity=Severity.MAJOR,
        rationale="would normally patch",
        patch_required=True,
    )
    _, events = PatchGate(registry, conflict_strategy=KeepUnchanged()).process(
        target, [(challenge, judge)]
    )
    assert events[0].outcome.value == "unchanged"


# ---------------- QE-2026-108: convergence metrics + opt-in early stop ----------------
def test_evolution_early_stops_on_stable_ecosystem(registry, tmp_path):
    report = evolve(
        registry.all(),
        registry,
        generations=10,
        rounds=0,
        optimize_budget=1,
        parallel=False,
        out_dir=tmp_path,
        early_stopping=True,
        convergence_patience=1,
        score_delta_tolerance=1.0,
    )
    assert report.stopped_early is True
    assert report.completed_generations < report.requested_generations
    assert report.convergence_reason == "stable_pareto_scores_and_families"
    assert report.convergence_metrics[-1].stable is True


def test_evolution_early_stopping_is_opt_in(registry):
    report = evolve(
        registry.all(),
        registry,
        generations=3,
        rounds=0,
        optimize_budget=1,
        parallel=False,
        early_stopping=False,
        convergence_patience=1,
        score_delta_tolerance=1.0,
    )
    assert report.completed_generations == 3
    assert report.stopped_early is False
