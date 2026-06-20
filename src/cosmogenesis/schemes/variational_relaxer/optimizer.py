"""Iterative optimization path for variational_relaxer: a (mu+lambda) evolution
strategy (CMA-lite). Stochastic and coupling-aware -- the deliberate opposite of
analytic_compiler's deterministic coordinate ascent."""

from __future__ import annotations

import numpy as np

from ...core import ParameterVector


def evolution_strategy(engine, start: ParameterVector, rng, budget: int = 80):
    dim = len(start.values)
    mean = np.array(start.to_normalized(), dtype=float)
    sigma = 0.22
    lam, mu = 10, 4
    best_vec = start.copy()
    best_val = engine.objective(best_vec)
    evals = 0
    while evals < budget:
        samples = []
        for _ in range(lam):
            child = np.clip(mean + sigma * rng.standard_normal(dim), 0.0, 1.0)
            vec = ParameterVector.from_normalized(list(child))
            val = engine.objective(vec)
            evals += 1
            samples.append((val, child))
            if val > best_val:
                best_val, best_vec = val, vec
            if evals >= budget:
                break
        samples.sort(key=lambda t: t[0], reverse=True)
        elites = samples[: min(mu, len(samples))]
        mean = np.mean([c for _, c in elites], axis=0)
        # cool toward exploitation but keep a floor so the search can escape basins.
        sigma = max(sigma * 0.9, 0.05)
    return best_vec
