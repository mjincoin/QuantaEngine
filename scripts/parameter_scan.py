"""Small parameter scan over microscopic-law controls.

This shows how QuantaEngine can be used as an engine for searching how different
fundamental parameters change emergent macroscopic structure.
"""

from __future__ import annotations

import csv
from dataclasses import replace
from pathlib import Path

from quantaengine_lattice import QuantaEngine, UniverseParams


out = Path("runs/parameter_scan")
out.mkdir(parents=True, exist_ok=True)
base = UniverseParams(name="scan", seed=2026, grid_size=64, chaos_strength=0.01)

rows = []
for scalar_mass in [0.1, 0.2, 0.4]:
    for self_coupling in [0.0, 0.03, 0.08]:
        params = replace(
            base,
            name=f"m{scalar_mass:.2f}_lambda{self_coupling:.2f}",
            scalar_mass=scalar_mass,
            self_coupling=self_coupling,
        )
        result = QuantaEngine(params).run(steps=64, snapshot_every=16)
        run_dir = out / params.name
        result.save(run_dir)
        summary = result.summary()
        metrics = summary["metrics"] or {}
        rows.append(
            {
                "name": params.name,
                "scalar_mass": scalar_mass,
                "self_coupling": self_coupling,
                "final_scale_factor": summary["final_scale_factor"],
                "rms_phi": metrics.get("rms_phi"),
                "density_contrast_rms": metrics.get("density_contrast_rms"),
                "max_density_contrast": metrics.get("max_density_contrast"),
            }
        )

with (out / "scan_summary.csv").open("w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)

print(f"Wrote scan to {out.resolve()}")
