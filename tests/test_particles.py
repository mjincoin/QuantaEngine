from pathlib import Path

from quanta_engine.core.schema import load_config
from quanta_engine.fields.spectrum import build_effective_particle_spectrum

CONFIG = Path(__file__).parents[1] / "configs" / "standard_universe.yaml"


def test_effective_particle_spectrum_queries_and_exports():
    spectrum = build_effective_particle_spectrum(load_config(CONFIG))
    assert spectrum.get("photon").mass_MeV == 0.0
    assert spectrum.get("electron").charge_e == -1.0
    assert spectrum.total_known_particles() == 7
    assert {particle.name for particle in spectrum.list_stable()} >= {
        "photon",
        "electron",
        "proton",
    }
    assert len(spectrum.to_dataframe()) == 7
    assert "helium4" in spectrum.to_markdown_table()
