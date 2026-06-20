import pytest

from quantaengine_lattice import UniverseParams


def test_params_validate_accepts_default():
    params = UniverseParams()
    params.validate()
    assert params.shape == (128, 128)
    assert params.dx > 0


def test_params_rejects_bad_dimension():
    params = UniverseParams(dimensions=4)
    with pytest.raises(ValueError):
        params.validate()


def test_params_roundtrip_dict():
    params = UniverseParams(name="roundtrip", seed=3, grid_size=32)
    loaded = UniverseParams.from_dict(params.to_dict())
    assert loaded.name == "roundtrip"
    assert loaded.seed == 3
    assert loaded.grid_size == 32
