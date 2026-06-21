"""Automatic scheme discovery for bundled subpackages and installed plugins."""

from __future__ import annotations

import inspect
import pkgutil
from importlib import import_module
from importlib.metadata import entry_points
from types import ModuleType
from typing import Any

from quanta_engine.core.schema import UniverseConfig

from ..core import BaseEngine, UniverseScheme

ENTRY_POINT_GROUP = "quanta_engine.schemes"
SCHEME_REGISTRY: dict[str, type[BaseEngine]] = {}
SCHEME_METADATA: dict[str, dict[str, Any]] = {}


def _engine_class(module: ModuleType) -> type[BaseEngine]:
    candidates = [
        value
        for _, value in inspect.getmembers(module, inspect.isclass)
        if value is not BaseEngine and issubclass(value, BaseEngine) and value.name != "base"
    ]
    if len(candidates) != 1:
        raise ValueError(
            f"scheme module {module.__name__!r} must export exactly one BaseEngine subclass"
        )
    return candidates[0]


def register_scheme(engine: type[BaseEngine], metadata: dict[str, Any] | None = None) -> None:
    name = engine.name
    if not name or name == "base":
        raise ValueError("scheme engine must define a non-empty name")
    existing = SCHEME_REGISTRY.get(name)
    if existing is not None and existing is not engine:
        raise ValueError(f"duplicate scheme name {name!r}")
    SCHEME_REGISTRY[name] = engine
    SCHEME_METADATA[name] = dict(metadata or {"name": name})


def refresh_scheme_registry() -> None:
    """Discover drop-in subpackages and ``quanta_engine.schemes`` entry points."""

    SCHEME_REGISTRY.clear()
    SCHEME_METADATA.clear()
    bundled = sorted(info.name for info in pkgutil.iter_modules(__path__) if info.ispkg)
    for package_name in bundled:
        module = import_module(f"{__name__}.{package_name}")
        register_scheme(_engine_class(module), getattr(module, "METADATA", None))

    plugin_points = entry_points(group=ENTRY_POINT_GROUP)
    for point in sorted(plugin_points, key=lambda item: item.name):
        loaded = point.load()
        if not inspect.isclass(loaded) or not issubclass(loaded, BaseEngine):
            raise TypeError(f"scheme entry point {point.name!r} must load a BaseEngine subclass")
        register_scheme(loaded, getattr(loaded, "METADATA", {"name": loaded.name}))


def list_schemes() -> list[str]:
    return sorted(SCHEME_REGISTRY)


def build_scheme(name: str, config: UniverseConfig) -> UniverseScheme:
    if name not in SCHEME_REGISTRY:
        raise ValueError(f"unknown scheme '{name}'. known: {list_schemes()}")
    return SCHEME_REGISTRY[name](config)


refresh_scheme_registry()


__all__ = [
    "SCHEME_REGISTRY",
    "SCHEME_METADATA",
    "ENTRY_POINT_GROUP",
    "list_schemes",
    "build_scheme",
    "register_scheme",
    "refresh_scheme_registry",
]
