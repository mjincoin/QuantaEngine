"""Configuration and result IO."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np
import yaml

from .params import UniverseParams

if TYPE_CHECKING:
    from .engine import UniverseResult


def load_config(path: str | Path) -> UniverseParams:
    """Load UniverseParams from YAML or JSON."""

    path = Path(path)
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".json"}:
        data = json.loads(text)
    else:
        data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise ValueError("configuration must contain a mapping/object")
    return UniverseParams.from_dict(data)


def save_config(params: UniverseParams, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix.lower() == ".json":
        path.write_text(json.dumps(params.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    else:
        path.write_text(yaml.safe_dump(params.to_dict(), sort_keys=False), encoding="utf-8")


def _jsonable_summary(summary: dict[str, Any]) -> dict[str, Any]:
    def convert(value: Any) -> Any:
        if isinstance(value, np.ndarray):
            return value.tolist()
        if isinstance(value, np.generic):
            return value.item()
        if isinstance(value, dict):
            return {k: convert(v) for k, v in value.items()}
        if isinstance(value, list):
            return [convert(v) for v in value]
        return value

    return convert(summary)


def save_result(result: UniverseResult, outdir: str | Path) -> None:
    """Save result arrays and metadata."""

    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    snapshot_phi = np.stack([s.phi for s in result.snapshots], axis=0)
    snapshot_times = np.array([s.time for s in result.snapshots], dtype=np.float64)
    snapshot_scale_factors = np.array([s.scale_factor for s in result.snapshots], dtype=np.float64)
    if result.power_spectrum is not None:
        k = result.power_spectrum["k"]
        power = result.power_spectrum["power"]
    else:
        k = np.array([])
        power = np.array([])

    np.savez_compressed(
        out / "result.npz",
        times=result.times,
        scale_factors=result.scale_factors,
        initial_phi=result.initial_phi,
        final_phi=result.final_state.phi,
        final_pi=result.final_state.pi,
        final_density=result.final_density,
        snapshot_phi=snapshot_phi,
        snapshot_times=snapshot_times,
        snapshot_scale_factors=snapshot_scale_factors,
        power_k=k,
        power=power,
    )
    metadata = {
        "params": result.params.to_dict(),
        "summary": result.summary(),
    }
    (out / "metadata.json").write_text(
        json.dumps(_jsonable_summary(metadata), indent=2, sort_keys=True),
        encoding="utf-8",
    )
