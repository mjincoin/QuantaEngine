from pprint import pprint

from quanta_engine.experiments.compare import compare_universes

pprint(
    compare_universes(
        "configs/standard_universe.yaml",
        "configs/strong_alpha_universe.yaml",
    )
)
