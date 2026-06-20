"""Minimal Python API example for QuantaEngine."""

from pathlib import Path

from quantaengine_lattice import QuantaEngine, UniverseParams
from quantaengine_lattice.visualize import save_diagnostics


params = UniverseParams(
    name="quickstart-universe",
    seed=123,
    dimensions=2,
    grid_size=96,
    primordial_rms=1.0e-3,
    chaos_strength=0.02,
    scalar_mass=0.25,
    self_coupling=0.03,
)

result = QuantaEngine(params).run(steps=96, snapshot_every=12)
out = Path("runs/quickstart")
result.save(out)
save_diagnostics(result, out)
print(result.summary())
