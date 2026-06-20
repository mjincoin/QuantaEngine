"""Iterative optimization path for analytic_compiler: deterministic, white-box
coordinate ascent with finite-difference probing and step halving."""

from __future__ import annotations

from ...core import AXES, ParameterVector


def coordinate_ascent(engine, start: ParameterVector, budget: int = 70, step0: float = 0.18):
    best = start.copy()
    best_val = engine.objective(best)
    step = step0
    evals = 0
    while evals < budget and step > 1e-3:
        improved = False
        normalized = best.to_normalized()
        for i in range(len(AXES)):
            for sign in (+1.0, -1.0):
                probe = list(normalized)
                probe[i] = min(1.0, max(0.0, probe[i] + sign * step))
                cand = ParameterVector.from_normalized(probe)
                val = engine.objective(cand)
                evals += 1
                if val > best_val + 1e-9:
                    best, best_val, normalized = cand, val, probe
                    improved = True
                if evals >= budget:
                    break
            if evals >= budget:
                break
        if not improved:
            step *= 0.5
    return best
