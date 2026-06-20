"""Effective particle data structures."""

from dataclasses import asdict, dataclass


@dataclass(frozen=True, slots=True)
class Particle:
    name: str
    mass_MeV: float
    charge_e: float
    stable: bool
    lifetime_s: float | None
    category: str

    def to_dict(self) -> dict[str, str | float | bool | None]:
        return asdict(self)
