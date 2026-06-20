"""Analysis helpers and observables."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(slots=True)
class FieldMetrics:
    mean_phi: float
    rms_phi: float
    min_phi: float
    max_phi: float
    mean_density: float
    density_contrast_rms: float
    max_density_contrast: float

    def to_dict(self) -> dict[str, float]:
        return {
            "mean_phi": self.mean_phi,
            "rms_phi": self.rms_phi,
            "min_phi": self.min_phi,
            "max_phi": self.max_phi,
            "mean_density": self.mean_density,
            "density_contrast_rms": self.density_contrast_rms,
            "max_density_contrast": self.max_density_contrast,
        }


def density_contrast(density: np.ndarray) -> np.ndarray:
    mean = float(np.mean(density))
    if mean == 0:
        return np.zeros_like(density)
    return density / mean - 1.0


def summarize_field(phi: np.ndarray, density: np.ndarray) -> FieldMetrics:
    contrast = density_contrast(density)
    return FieldMetrics(
        mean_phi=float(np.mean(phi)),
        rms_phi=float(np.std(phi)),
        min_phi=float(np.min(phi)),
        max_phi=float(np.max(phi)),
        mean_density=float(np.mean(density)),
        density_contrast_rms=float(np.std(contrast)),
        max_density_contrast=float(np.max(contrast)),
    )


def radial_power_spectrum(field: np.ndarray, box_size: float, bins: int = 32) -> dict[str, Any]:
    """Compute a simple binned isotropic power spectrum."""

    f = field - float(np.mean(field))
    fk = np.fft.fftn(f)
    power = np.abs(fk) ** 2 / f.size
    dx = box_size / field.shape[0]
    freqs = [np.fft.fftfreq(n, d=dx) * 2.0 * np.pi for n in field.shape]
    meshes = np.meshgrid(*freqs, indexing="ij")
    k = np.sqrt(sum(axis_k**2 for axis_k in meshes))
    k_flat = k.ravel()
    p_flat = power.ravel()
    max_k = float(np.max(k_flat))
    edges = np.linspace(0.0, max_k, bins + 1)
    k_centers = 0.5 * (edges[1:] + edges[:-1])
    pk = np.zeros(bins)
    counts = np.zeros(bins, dtype=int)
    which = np.digitize(k_flat, edges) - 1
    for idx, val in zip(which, p_flat, strict=False):
        if 0 <= idx < bins:
            pk[idx] += val
            counts[idx] += 1
    nonzero = counts > 0
    pk[nonzero] /= counts[nonzero]
    return {"k": k_centers, "power": pk, "counts": counts}
