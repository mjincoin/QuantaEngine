"""Structured adversarial artifacts: Challenge / Defense / Verification / Judge / Patch.

All Pydantic so they are YAML/JSON serializable and schema-validated -- critique
never bypasses validation (a core requirement of the self-play design).
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class Severity(StrEnum):
    INFO = "info"
    MINOR = "minor"
    MAJOR = "major"
    CRITICAL = "critical"
    FATAL = "fatal"


HARD_SEVERITIES = {Severity.CRITICAL, Severity.FATAL}


class ChallengeType(StrEnum):
    INTERNAL_CONTRADICTION = "internal_contradiction"
    NUMERICAL_INSTABILITY = "numerical_instability"
    FAILED_BENCHMARK = "failed_benchmark"
    REPRODUCIBLE_COUNTEREXAMPLE = "reproducible_counterexample"
    OVERFITTING_TO_STANDARD_UNIVERSE = "overfitting_to_standard_universe"
    UNDERCONSTRAINED_PARAMETER = "underconstrained_parameter"
    LOW_GENERATIVE_POWER = "low_generative_power"
    FRAGILITY = "fragility"
    MISLEADING_CLAIM = "misleading_claim"


class EvidenceType(StrEnum):
    NUMERICAL_RESULT = "numerical_result"
    BENCHMARK = "benchmark"
    CONFIG_SNIPPET = "config_snippet"
    ARGUMENT = "argument"


class EvidenceItem(BaseModel):
    evidence_type: EvidenceType
    summary: str
    content: str | dict[str, Any] = ""
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class ChallengeCard(BaseModel):
    challenge_id: str
    source_theory_id: str
    target_theory_id: str
    challenge_type: ChallengeType
    severity: Severity
    summary: str
    detailed_argument: str = ""
    evidence: list[EvidenceItem] = Field(default_factory=list)
    # A reproducible probe: a parameter vector + the failure the source claims.
    probe_vector: list[float] | None = None
    expected_failure_mode: str | None = None
    suggested_resolution: str | None = None  # "patch" | "fork" | "annotate"


class DefenseStance(StrEnum):
    REJECT = "reject"
    ACCEPT = "accept"
    PARTIAL_ACCEPT = "partial_accept"
    REQUEST_TEST = "request_test"
    FORK_INSTEAD_OF_PATCH = "fork_instead_of_patch"


class DefenseCard(BaseModel):
    defense_id: str
    challenge_id: str
    target_theory_id: str
    stance: DefenseStance
    summary: str
    argument: str = ""
    counter_evidence: list[EvidenceItem] = Field(default_factory=list)


class VerificationResult(BaseModel):
    verification_id: str
    challenge_id: str
    target_theory_id: str
    reproduced: bool
    is_hard_error: bool
    measured: dict[str, Any] = Field(default_factory=dict)
    verifier_summary: str = ""


class JudgeDecision(StrEnum):
    CHALLENGE_REJECTED = "challenge_rejected"
    CHALLENGE_UPHELD_NO_PATCH = "challenge_upheld_no_patch"
    PATCH_REQUIRED = "patch_required"
    NEEDS_MORE_TESTS = "needs_more_tests"
    FORK_RECOMMENDED = "fork_recommended"
    THEORY_INVALIDATED = "theory_invalidated"


class JudgeResult(BaseModel):
    judge_result_id: str
    challenge_id: str
    target_theory_id: str
    decision: JudgeDecision
    severity: Severity
    rationale: str
    patch_required: bool = False
    fork_recommended: bool = False


class PatchOutcome(StrEnum):
    UNCHANGED = "unchanged"
    PATCHED = "patched"
    FORKED = "forked"
    INVALIDATED = "invalidated"


class PatchEvent(BaseModel):
    theory_id: str
    based_on_challenge_id: str
    outcome: PatchOutcome
    summary: str
    new_version: str | None = None
    child_theory_id: str | None = None
    # invariant of the whole system: theories are never merged.
    merged: bool = False
