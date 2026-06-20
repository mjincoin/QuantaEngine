"""Primordial fluctuation generation."""

from __future__ import annotations

import numpy as np

from .params import UniverseParams


def _k_grid(params: UniverseParams) -> np.ndarray:
    freqs = [np.fft.fftfreq(params.grid_size, d=params.dx) * 2.0 * np.pi for _ in range(params.dimensions)]
    meshes = np.meshgrid(*freqs, indexing="ij")
    k2 = np.zeros(params.shape, dtype=np.float64)
    for axis_k in meshes:
        k2 += axis_k**2
    return np.sqrt(k2)


def primordial_power(k: np.ndarray, params: UniverseParams) -> np.ndarray:
    """Return a power-spectrum-like shape P(k).

    This is a transparent toy model inspired by primordial spectra:
    P(k) ∝ (k / pivot)^(n_s - 1) with an ultraviolet damping envelope.
    """

    safe_k = np.maximum(k, 1.0e-12)
    p = (safe_k / params.pivot_k) ** (params.spectral_index - 1.0)
    p *= np.exp(-(safe_k / params.k_cut) ** 2)
    p[k == 0] = 0.0
    return p


def gaussian_random_field(params: UniverseParams, rng: np.random.Generator) -> np.ndarray:
    """Generate a real Gaussian field with a target spectral shape and RMS."""

    white = rng.normal(size=params.shape)
    white_k = np.fft.fftn(white)
    k = _k_grid(params)
    pk = primordial_power(k, params)
    shaped = np.fft.ifftn(white_k * np.sqrt(pk)).real
    shaped -= float(np.mean(shaped))
    rms = float(np.std(shaped))
    if rms > 0 and params.primordial_rms > 0:
        shaped *= params.primordial_rms / rms
    return shaped
