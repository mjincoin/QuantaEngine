"""Tests for cosmogenesis.core (shared contract) and cosmogenesis.schemes."""

from __future__ import annotations

import math

import pytest

from cosmogenesis.core import (
    NDIM,
    ParameterVector,
    UniverseAssessment,
    apply_vector,
    vector_from_config,
)
from cosmogenesis.core.assessment import logistic_window, softmin
from cosmogenesis.schemes import SCHEME_REGISTRY, build_scheme, list_schemes
from quanta_engine.core.schema import load_config

CONFIG = "configs/standard_universe.yaml"


@pytest.fixture(scope="module")
def base_config():
    return load_config(CONFIG)


# ---------------- core: parameter vector ----------------
def test_vector_config_roundtrip(base_config):
    v = vector_from_config(base_config)
    assert len(v.values) == NDIM
    cfg = apply_vector(base_config, v)
    assert cfg.dimensionless.alpha_scale == pytest.approx(base_config.dimensionless.alpha_scale)


def test_normalized_roundtrip():
    v = ParameterVector([1.2, 5.0, 1.1, 2.0, -8.0])
    back = ParameterVector.from_normalized(v.to_normalized())
    assert back.values == pytest.approx(v.values, rel=1e-9)


def test_apply_vector_is_a_copy(base_config):
    v = vector_from_config(base_config)
    v.values[1] = 10.0
    cfg = apply_vector(base_config, v)
    assert cfg.dimensionless.gravity_scale == pytest.approx(10.0)
    assert base_config.dimensionless.gravity_scale == pytest.approx(1.0)


def test_core_helpers():
    assert logistic_window(13.6, 1.0, 120.0) > 0.8
    assert logistic_window(1e-3, 1.0, 120.0) < 0.1
    assert softmin([1.0, 1.0, 0.1]) < 0.3


# ---------------- schemes registry ----------------
def test_registry_lists_three_schemes():
    assert set(list_schemes()) == {"analytic_compiler", "variational_relaxer", "minimal_axiom"}


def test_build_unknown_scheme_raises(base_config):
    with pytest.raises(ValueError):
        build_scheme("does_not_exist", base_config)


@pytest.mark.parametrize("name", ["analytic_compiler", "variational_relaxer", "minimal_axiom"])
def test_scheme_assess_contract(base_config, name):
    engine = build_scheme(name, base_config)
    out = engine.assess(ParameterVector.default())
    assert isinstance(out, UniverseAssessment)
    assert out.scheme == name
    assert 0.0 <= out.score <= 1.0


def test_schemes_disagree_on_strong_gravity(base_config):
    v = ParameterVector([1.0, 50.0, 1.0, 1.0, -8.68])
    scores = {n: build_scheme(n, base_config).assess(v).score for n in list_schemes()}
    assert len({round(s, 3) for s in scores.values()}) >= 2


# ---------------- individual schemes ----------------
def test_analytic_compiler_standard_high(base_config):
    out = build_scheme("analytic_compiler", base_config).assess(ParameterVector.default())
    assert out.feasible and out.score > 0.9 and out.residual == 0.0


def test_variational_relaxer_self_consistency(base_config):
    engine = build_scheme("variational_relaxer", base_config)
    out = engine.assess(ParameterVector.default())
    assert out.diagnostics["relax_converged"]
    assert out.diagnostics["age_years"] / 1e9 == pytest.approx(13.8, abs=1.0)
    # a huge cosmological constant breaks flatness + the time budget
    broken = engine.assess(ParameterVector([1.0, 1.0, 1.0, 40.0, -8.0]))
    assert broken.residual > 0.1 and not broken.feasible


def test_minimal_axiom_three_free_parameters(base_config):
    out = build_scheme("minimal_axiom", base_config).assess(ParameterVector.default())
    assert out.diagnostics["free_parameters"] == 3


# ---------------- optimizers (iterative path per scheme) ----------------
@pytest.mark.parametrize("name", ["analytic_compiler", "variational_relaxer", "minimal_axiom"])
def test_optimizer_does_not_regress(base_config, name):
    engine = build_scheme(name, base_config)
    poor = ParameterVector([0.5, 12.0, 1.4, 6.0, -7.5])
    before = engine.objective(poor)
    champ = engine.optimize(poor, budget=60)
    assert engine.objective(champ) >= before


def test_scheme_registry_classes_have_names():
    for key, cls in SCHEME_REGISTRY.items():
        assert cls.name == key
        assert math.isfinite(0.0)  # sanity
