"""Optional visualization helpers."""

from __future__ import annotations

from pathlib import Path

import numpy as np


def _project_to_2d(array: np.ndarray) -> np.ndarray:
    if array.ndim == 1:
        return array[None, :]
    if array.ndim == 2:
        return array
    if array.ndim == 3:
        return np.mean(array, axis=0)
    raise ValueError("array must be 1D, 2D, or 3D")


def save_map(array: np.ndarray, path: str | Path, title: str = "QuantaEngine map") -> None:
    """Save a diagnostic PNG map.

    Matplotlib is imported lazily so headless numerical use stays lightweight.
    """

    import matplotlib.pyplot as plt

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    image = _project_to_2d(array)
    fig, ax = plt.subplots(figsize=(7, 6), constrained_layout=True)
    im = ax.imshow(image, origin="lower", aspect="equal")
    ax.set_title(title)
    ax.set_xlabel("lattice x")
    ax.set_ylabel("lattice y / projection")
    fig.colorbar(im, ax=ax, shrink=0.85)
    fig.savefig(path, dpi=160)
    plt.close(fig)


def save_diagnostics(result, outdir: str | Path) -> None:
    out = Path(outdir)
    save_map(result.initial_phi, out / "initial_phi.png", "Initial microscopic field φ")
    save_map(result.final_state.phi, out / "final_phi.png", "Final evolved field φ")
    save_map(result.final_density, out / "final_density.png", "Final energy-density structure")
