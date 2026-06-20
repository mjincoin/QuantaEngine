"""High-level universe generation engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

from .analysis import FieldMetrics, radial_power_spectrum, summarize_field
from .chaos import apply_chaos
from .cosmology import FriedmannBackground
from .fields import ScalarFieldLattice, ScalarFieldState
from .io import save_result
from .params import UniverseParams
from .spectrum import gaussian_random_field


@dataclass(slots=True)
class UniverseResult:
    """Result container produced by a QuantaEngine run."""

    params: UniverseParams
    times: np.ndarray
    scale_factors: np.ndarray
    initial_phi: np.ndarray
    final_state: ScalarFieldState
    final_density: np.ndarray
    snapshots: list[ScalarFieldState] = field(default_factory=list)
    metrics: FieldMetrics | None = None
    power_spectrum: dict[str, Any] | None = None

    def summary(self) -> dict[str, Any]:
        return {
            "name": self.params.name,
            "seed": self.params.seed,
            "dimensions": self.params.dimensions,
            "grid_size": self.params.grid_size,
            "final_time": float(self.times[-1]),
            "final_scale_factor": float(self.scale_factors[-1]),
            "snapshots": len(self.snapshots),
            "metrics": self.metrics.to_dict() if self.metrics else None,
        }

    def save(self, outdir: str | Path) -> None:
        save_result(self, outdir)


class QuantaEngine:
    """Universe generation engine.

    Typical use:

    >>> params = UniverseParams(seed=1, grid_size=64)
    >>> result = QuantaEngine(params).run(steps=16)
    >>> result.final_density.shape
    (64, 64)
    """

    def __init__(self, params: UniverseParams):
        params.validate()
        self.params = params
        self.rng = np.random.default_rng(params.seed)

    def initial_field(self) -> np.ndarray:
        phi = gaussian_random_field(self.params, self.rng)
        phi = apply_chaos(phi, self.params)
        return phi

    def run(self, steps: int = 128, snapshot_every: int = 16) -> UniverseResult:
        if steps < 1:
            raise ValueError("steps must be at least 1")
        if snapshot_every < 1:
            raise ValueError("snapshot_every must be at least 1")

        p = self.params
        background = FriedmannBackground(p)
        initial_phi = self.initial_field()
        lattice = ScalarFieldLattice(p, initial_phi)

        times = np.empty(steps + 1, dtype=np.float64)
        scale_factors = np.empty(steps + 1, dtype=np.float64)
        times[0] = 0.0
        scale_factors[0] = p.initial_scale_factor
        snapshots: list[ScalarFieldState] = [lattice.state.copy()]

        for i in range(1, steps + 1):
            bg_state = background.step(p.time_step)
            lattice.step(p.time_step, bg_state.scale_factor, background.hubble(bg_state.scale_factor))
            times[i] = bg_state.time
            scale_factors[i] = bg_state.scale_factor
            if i % snapshot_every == 0 or i == steps:
                snapshots.append(lattice.state.copy())

        final_density = lattice.energy_density()
        metrics = summarize_field(lattice.state.phi, final_density)
        ps = radial_power_spectrum(lattice.state.phi, p.box_size)
        return UniverseResult(
            params=p,
            times=times,
            scale_factors=scale_factors,
            initial_phi=initial_phi,
            final_state=lattice.state.copy(),
            final_density=final_density,
            snapshots=snapshots,
            metrics=metrics,
            power_spectrum=ps,
        )
