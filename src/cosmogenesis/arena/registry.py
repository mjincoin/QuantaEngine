"""TheoryRegistry: tracks theory lineages. Never merges; always preserves parents."""

from __future__ import annotations

from pathlib import Path

from .theory import TheorySpec, load_theory


class TheoryRegistry:
    def __init__(self) -> None:
        self._theories: dict[str, TheorySpec] = {}

    def add(self, theory: TheorySpec) -> None:
        self._theories[theory.theory_id] = theory

    def get(self, theory_id: str) -> TheorySpec:
        return self._theories[theory_id]

    def __contains__(self, theory_id: str) -> bool:
        return theory_id in self._theories

    def all(self) -> list[TheorySpec]:
        return list(self._theories.values())

    def families(self) -> set[str]:
        return {t.family for t in self._theories.values()}

    def next_theory_id(self) -> str:
        nums = [int(tid.split("-")[1]) for tid in self._theories if tid.startswith("T-")]
        return f"T-{(max(nums) + 1) if nums else 1:04d}"

    def lineage(self, theory_id: str) -> list[str]:
        chain = [theory_id]
        cur = self._theories.get(theory_id)
        while cur and cur.parent_id:
            chain.append(cur.parent_id)
            cur = self._theories.get(cur.parent_id)
        return list(reversed(chain))

    @classmethod
    def from_dir(cls, root: str | Path) -> TheoryRegistry:
        registry = cls()
        for path in sorted(Path(root).glob("T-*/theory.yaml")):
            registry.add(load_theory(path))
        return registry
