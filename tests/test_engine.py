from pathlib import Path

import numpy as np

from quantaengine_lattice import QuantaEngine, UniverseParams


def test_engine_runs_small_2d():
    params = UniverseParams(grid_size=16, dimensions=2, seed=10, time_step=0.001)
    result = QuantaEngine(params).run(steps=4, snapshot_every=2)
    assert result.final_state.phi.shape == (16, 16)
    assert result.final_density.shape == (16, 16)
    assert np.isfinite(result.final_density).all()
    assert result.metrics is not None
    assert result.summary()["snapshots"] >= 2


def test_engine_save(tmp_path: Path):
    params = UniverseParams(grid_size=16, dimensions=2, seed=11, time_step=0.001)
    result = QuantaEngine(params).run(steps=3, snapshot_every=1)
    result.save(tmp_path)
    assert (tmp_path / "result.npz").exists()
    assert (tmp_path / "metadata.json").exists()
