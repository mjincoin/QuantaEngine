from pathlib import Path

import pytest
from pydantic import ValidationError

from quanta_engine.core.schema import load_config

CONFIGS = Path(__file__).parents[1] / "configs"


def test_standard_universe_loads():
    config = load_config(CONFIGS / "standard_universe.yaml")
    assert config.universe.name == "standard_universe"
    assert config.effective_alpha == pytest.approx(0.0072973525693)


def test_child_config_inherits_and_overrides_alpha_scale():
    config = load_config(CONFIGS / "strong_alpha_universe.yaml")
    assert config.constants.c == 299_792_458.0
    assert config.dimensionless.alpha_scale == 1.2
    assert config.effective_alpha == pytest.approx(0.0072973525693 * 1.2)


def test_missing_required_sections_raise_helpful_error(tmp_path: Path):
    bad = tmp_path / "bad.yaml"
    bad.write_text("universe:\n  name: incomplete\n", encoding="utf-8")
    with pytest.raises(ValidationError) as exc:
        load_config(bad)
    assert "constants" in str(exc.value)
    assert "particles" in str(exc.value)


def test_inheritance_cycle_is_rejected(tmp_path: Path):
    (tmp_path / "a.yaml").write_text("inherit: b.yaml\n", encoding="utf-8")
    (tmp_path / "b.yaml").write_text("inherit: a.yaml\n", encoding="utf-8")
    with pytest.raises(ValueError, match="inheritance cycle"):
        load_config(tmp_path / "a.yaml")
