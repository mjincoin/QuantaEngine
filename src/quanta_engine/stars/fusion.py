"""First-order hydrogen-fusion feasibility criterion."""

from quanta_engine.atomic.hydrogen import AtomicReport
from quanta_engine.core.schema import UniverseConfig
from quanta_engine.nuclear.stability import NuclearReport


def hydrogen_fusion_possible(
    config: UniverseConfig,
    atomic: AtomicReport,
    nuclear: NuclearReport,
) -> bool:
    gravity = config.dimensionless.gravity_scale
    return (
        atomic.stable_hydrogen
        and nuclear.heavy_element_seed_possible
        and 1.0e-4 <= gravity <= 1.0e4
        and 0 < config.effective_alpha < 0.2
    )
