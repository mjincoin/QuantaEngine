"""Law specification layer.

This module is the beginning of a Geant4-inspired modular physics description:
rather than hard-coding every universe, users can eventually define laws, fields,
constants, symmetries, and couplings in a structured `LawBook`.

The v0.1 engine still uses `UniverseParams` for numerical evolution, but this
module establishes the public data model for future first-principles modules.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .params import UniverseParams


@dataclass(slots=True)
class ConstantSpec:
    name: str
    value: float
    unit: str = "natural"
    description: str = ""


@dataclass(slots=True)
class FieldSpec:
    name: str
    kind: str = "scalar"
    mass: float = 0.0
    spin: float = 0.0
    description: str = ""


@dataclass(slots=True)
class CouplingSpec:
    name: str
    fields: list[str]
    strength: float
    operator: str = ""
    description: str = ""


@dataclass(slots=True)
class LawBook:
    """Structured law description for a generated universe."""

    name: str = "minimal-lawbook"
    constants: list[ConstantSpec] = field(default_factory=list)
    fields: list[FieldSpec] = field(default_factory=list)
    couplings: list[CouplingSpec] = field(default_factory=list)
    symmetries: list[str] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LawBook:
        constants = [ConstantSpec(**item) for item in data.get("constants", [])]
        fields_ = [FieldSpec(**item) for item in data.get("fields", [])]
        couplings = [CouplingSpec(**item) for item in data.get("couplings", [])]
        return cls(
            name=data.get("name", "minimal-lawbook"),
            constants=constants,
            fields=fields_,
            couplings=couplings,
            symmetries=list(data.get("symmetries", [])),
            notes=data.get("notes", ""),
        )

    def to_universe_params(self, base: UniverseParams | None = None) -> UniverseParams:
        """Map a minimal LawBook into current UniverseParams.

        This is intentionally conservative. It maps the first scalar field mass
        and a φ⁴-like coupling into the v0.1 scalar-field toy kernel. Richer law
        interpretation should live in future physics modules.
        """

        params = base or UniverseParams(name=self.name)
        scalar_fields = [f for f in self.fields if f.kind.lower() == "scalar"]
        if scalar_fields:
            params.scalar_mass = scalar_fields[0].mass
        for coupling in self.couplings:
            op = coupling.operator.replace(" ", "").lower()
            if "phi^4" in op or "φ^4" in op or coupling.name.lower() in {"lambda", "self_coupling"}:
                params.self_coupling = coupling.strength
        for constant in self.constants:
            key = constant.name.lower()
            if key in {"alpha", "fine_structure_alpha"}:
                params.fine_structure_alpha = constant.value
            elif key in {"qcd_scale", "lambda_qcd"}:
                params.qcd_scale = constant.value
            elif key in {"electroweak_scale", "vev", "higgs_vev"}:
                params.electroweak_scale = constant.value
        params.validate()
        return params


def minimal_lawbook() -> LawBook:
    """Return a small example lawbook matching the default scalar kernel."""

    return LawBook(
        name="minimal-scalar-universe",
        constants=[
            ConstantSpec("fine_structure_alpha", 1.0 / 137.035_999_084, "dimensionless"),
            ConstantSpec("electroweak_scale", 246.0, "GeV"),
            ConstantSpec("qcd_scale", 0.2, "GeV"),
        ],
        fields=[FieldSpec("phi", kind="scalar", mass=0.2, spin=0.0)],
        couplings=[CouplingSpec("lambda", fields=["phi"], strength=0.05, operator="phi^4")],
        symmetries=["translation", "rotation", "Z2(phi -> -phi)"],
        notes="Minimal toy scalar-field universe used by QuantaEngine v0.1.",
    )
