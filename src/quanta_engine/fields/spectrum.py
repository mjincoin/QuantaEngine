"""Build and query the MVP effective particle spectrum."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from quanta_engine.core.schema import UniverseConfig

from .particles import Particle


@dataclass(slots=True)
class ParticleSpectrum:
    particles: list[Particle]

    def get(self, name: str) -> Particle:
        normalized = name.casefold()
        for particle in self.particles:
            if particle.name.casefold() == normalized:
                return particle
        raise KeyError(f"unknown particle: {name}")

    def list_stable(self) -> list[Particle]:
        return [particle for particle in self.particles if particle.stable]

    def total_known_particles(self) -> int:
        return len(self.particles)

    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame([particle.to_dict() for particle in self.particles])

    def to_markdown_table(self) -> str:
        header = "| name | mass (MeV) | charge (e) | stable | lifetime (s) | category |"
        separator = "|---|---:|---:|:---:|---:|---|"
        rows = [
            "| {name} | {mass:.9g} | {charge:.3g} | {stable} | {lifetime} | {category} |".format(
                name=particle.name,
                mass=particle.mass_MeV,
                charge=particle.charge_e,
                stable=str(particle.stable).lower(),
                lifetime="stable" if particle.lifetime_s is None else f"{particle.lifetime_s:.6g}",
                category=particle.category,
            )
            for particle in self.particles
        ]
        return "\n".join([header, separator, *rows])

    def to_list(self) -> list[dict[str, str | float | bool | None]]:
        return [particle.to_dict() for particle in self.particles]


def build_effective_particle_spectrum(config: UniverseConfig) -> ParticleSpectrum:
    p = config.particles
    n = config.nuclear
    strong = config.dimensionless.strong_scale
    deuteron_mass = p.proton_mass_MeV + p.neutron_mass_MeV - n.deuteron_binding_MeV * strong
    helium_mass = 2.0 * (p.proton_mass_MeV + p.neutron_mass_MeV) - n.helium4_binding_MeV * strong
    particles = [
        Particle("photon", 0.0, 0.0, True, None, "gauge boson"),
        Particle("neutrino_effective", 0.0, 0.0, True, None, "lepton"),
        Particle("electron", p.electron_mass_MeV, -1.0, p.electron_mass_MeV > 0, None, "lepton"),
        Particle("proton", p.proton_mass_MeV, 1.0, p.proton_mass_MeV > 0, None, "baryon"),
        Particle("neutron", p.neutron_mass_MeV, 0.0, False, 879.4, "baryon"),
        Particle(
            "deuteron", deuteron_mass, 1.0, n.deuteron_binding_MeV * strong > 0, None, "nucleus"
        ),
        Particle("helium4", helium_mass, 2.0, n.helium4_binding_MeV * strong > 0, None, "nucleus"),
    ]
    return ParticleSpectrum(particles)
