"""Common assessment record produced by every scheme (shared entry point)."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class UniverseAssessment:
    """Scheme-agnostic verdict on one universe.

    Both the analytic Scheme A and the variational Scheme B return this, so the
    arena can compare them and let each evaluate the other's universes.
    """

    scheme: str
    score: float  # primary feasibility objective in [0, 1]
    feasible: bool
    margins: dict[str, float] = field(default_factory=dict)  # per-window soft scores
    residual: float = 0.0  # global self-consistency residual (A reports 0.0)
    diagnostics: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def softmin(values: list[float], sharpness: float = 8.0) -> float:
    """Smooth minimum in [0, 1]: dominated by the worst margin but differentiable.

    Used by Scheme B so a single failing window pulls the score down without the
    hard discontinuities Scheme A uses.
    """

    import math

    if not values:
        return 0.0
    clipped = [min(1.0, max(0.0, v)) for v in values]
    # -1/k * logsumexp(-k v) shifted; numerically stable form.
    k = sharpness
    m = min(clipped)
    s = sum(math.exp(-k * (v - m)) for v in clipped)
    return m - math.log(s / len(clipped)) / k


def logistic_window(value: float, lo: float, hi: float, width_frac: float = 0.15) -> float:
    """Soft membership in [lo, hi] as a product of two logistics in log space.

    Returns ~1 well inside the window, ~0 well outside, smooth at the edges.
    """

    import math

    if value <= 0 or lo <= 0 or hi <= 0:
        return 0.0
    lv, llo, lhi = math.log(value), math.log(lo), math.log(hi)
    w = max(1e-6, width_frac * (lhi - llo))
    rising = 1.0 / (1.0 + math.exp(-(lv - llo) / w))
    falling = 1.0 / (1.0 + math.exp((lv - lhi) / w))
    return rising * falling
