"""End-to-end effective universe generation pipeline."""

from pathlib import Path

from quanta_engine.atomic.hydrogen import compute_hydrogen_properties
from quanta_engine.complexity.habitability import compute_complexity_report
from quanta_engine.core.result import UniverseReport
from quanta_engine.core.schema import UniverseConfig, load_config
from quanta_engine.cosmology.friedmann import compute_friedmann_background
from quanta_engine.fields.spectrum import build_effective_particle_spectrum
from quanta_engine.nuclear.stability import compute_nuclear_stability
from quanta_engine.stars.stellar_scaling import compute_stellar_window
from quanta_engine.structure.halos import compute_structure_window
from quanta_engine.validation.universe import validate_universe_config


def run_universe_pipeline(config_path: str | Path | UniverseConfig) -> UniverseReport:
    """Compile one configuration through every MVP physical layer."""

    config = config_path if isinstance(config_path, UniverseConfig) else load_config(config_path)
    validation = validate_universe_config(config)
    particles = build_effective_particle_spectrum(config)
    atomic = compute_hydrogen_properties(config)
    nuclear = compute_nuclear_stability(config)
    cosmology = compute_friedmann_background(config)
    stellar = compute_stellar_window(config, atomic, nuclear, cosmology)
    structure = compute_structure_window(config, cosmology, stellar)
    complexity = compute_complexity_report(config, atomic, nuclear, cosmology, stellar, structure)
    verdict = complexity.qualitative_summary if validation.passed else "invalid"
    summary = {
        "name": config.universe.name,
        "description": config.universe.description,
        "effective_alpha": config.effective_alpha,
        "effective_G": config.effective_G,
        "gravity_scale": config.dimensionless.gravity_scale,
        "strong_scale": config.dimensionless.strong_scale,
    }
    return UniverseReport(
        config=config,
        config_summary=summary,
        validation_report=validation,
        particle_spectrum=particles,
        atomic_report=atomic,
        nuclear_report=nuclear,
        cosmology_report=cosmology,
        stellar_report=stellar,
        structure_report=structure,
        complexity_report=complexity,
        final_verdict=verdict,
    )
