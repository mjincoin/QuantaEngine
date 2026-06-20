"""Iterative optimization path for minimal_axiom: a cheap coordinate hill-climb,
in keeping with the scheme's minimal-machinery philosophy."""

from __future__ import annotations

from ...core import AXES, ParameterVector


def restart_hill_climb(engine, start: ParameterVector, budget: int = 60, step0: float = 0.2):
    best = start.copy()
    best_val = engine.objective(best)
    step = step0
    evals = 0
    while evals < budget and step > 1e-3:
        improved = False
        base = best.to_normalized()
        for i in range(len(AXES)):
            for sign in (+1.0, -1.0):
                probe = list(base)
                probe[i] = min(1.0, max(0.0, probe[i] + sign * step))
                cand = ParameterVector.from_normalized(probe)
                val = engine.objective(cand)
                evals += 1
                if val > best_val + 1e-9:
                    best, best_val, base = cand, val, probe
                    improved = True
                if evals >= budget:
                    break
            if evals >= budget:
                break
        if not improved:
            step *= 0.5
    return best
