"""Typed configuration models and YAML inheritance."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict


class ConfigSection(BaseModel):
    model_config = ConfigDict(extra="forbid")


class UniverseMetadata(ConfigSection):
    name: str
    description: str = ""


class SpacetimeConfig(ConfigSection):
    dimensions: int
    metric_signature: str
    gravity_model: str
    curvature_k: float | None = None


class ConstantsConfig(ConfigSection):
    c: float
    hbar: float
    G: float
    k_B: float


class DimensionlessConfig(ConfigSection):
    alpha: float
    alpha_scale: float = 1.0
    gravity_scale: float = 1.0
    strong_scale: float = 1.0
    weak_scale: float = 1.0
    cosmological_constant_scale: float = 1.0


class ParticleConfig(ConfigSection):
    electron_mass_MeV: float
    proton_mass_MeV: float
    neutron_mass_MeV: float
    pion_mass_MeV: float


class CosmologyConfig(ConfigSection):
    H0_km_s_Mpc: float
    omega_b: float
    omega_cdm: float
    omega_lambda: float
    omega_r: float = 9.0e-5
    primordial_amplitude: float
    scalar_spectral_index: float


class NuclearConfig(ConfigSection):
    deuteron_binding_MeV: float
    helium4_binding_MeV: float
    bbn_model: str = "toy"


class AtomicConfig(ConfigSection):
    model: str = "hydrogenic"
    require_stable_hydrogen: bool = True


class StellarConfig(ConfigSection):
    model: str = "scaling"
    min_lifetime_years_for_complexity: float
    require_hydrogen_fusion: bool = True


class ComplexityConfig(ConfigSection):
    require_stable_atoms: bool = True
    require_long_lived_stars: bool = True
    require_heavy_elements: bool = True
    require_energy_gradients: bool = True


class UniverseConfig(ConfigSection):
    universe: UniverseMetadata
    spacetime: SpacetimeConfig
    constants: ConstantsConfig
    dimensionless: DimensionlessConfig
    particles: ParticleConfig
    cosmology: CosmologyConfig
    nuclear: NuclearConfig
    atomic: AtomicConfig
    stellar: StellarConfig
    complexity: ComplexityConfig

    @property
    def effective_alpha(self) -> float:
        return self.dimensionless.alpha * self.dimensionless.alpha_scale

    @property
    def effective_G(self) -> float:
        return self.constants.G * self.dimensionless.gravity_scale


def deep_merge(parent: dict[str, Any], child: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge mappings while replacing scalar and list values."""

    result = deepcopy(parent)
    for key, value in child.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result


def _load_mapping(path: Path, stack: tuple[Path, ...]) -> dict[str, Any]:
    resolved = path.expanduser().resolve()
    if resolved in stack:
        chain = " -> ".join(str(item.name) for item in (*stack, resolved))
        raise ValueError(f"configuration inheritance cycle detected: {chain}")
    if not resolved.is_file():
        raise FileNotFoundError(f"configuration file not found: {resolved}")
    data = yaml.safe_load(resolved.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"configuration must contain a mapping: {resolved}")
    child = dict(data)
    inherit = child.pop("inherit", None)
    if inherit is None:
        return child
    if not isinstance(inherit, str) or not inherit.strip():
        raise ValueError(f"inherit must be a non-empty filename in {resolved}")
    parent = _load_mapping(resolved.parent / inherit, (*stack, resolved))
    return deep_merge(parent, child)


def load_config(path: str | Path) -> UniverseConfig:
    """Load, inherit, deep-merge, and validate a universe YAML file."""

    return UniverseConfig.model_validate(_load_mapping(Path(path), ()))
