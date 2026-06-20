"""Round-robin tournament: every pair duels; theories scored multi-objectively."""

from __future__ import annotations

import itertools
from concurrent.futures import ThreadPoolExecutor

from pydantic import BaseModel, Field

from . import scoring
from .duel import DuelReport, run_duel
from .registry import TheoryRegistry
from .scoring import TheoryScoreVector
from .theory import TheorySpec


class TournamentReport(BaseModel):
    generation: int = 0
    duels: list[DuelReport] = Field(default_factory=list)
    scores: list[TheoryScoreVector] = Field(default_factory=list)
    pareto_front: list[str] = Field(default_factory=list)
    family_elites: dict[str, list[str]] = Field(default_factory=dict)
    allow_merge: bool = False


def run_tournament(
    theories: list[TheorySpec],
    registry: TheoryRegistry,
    rounds: int = 1,
    generation: int = 0,
    history_dir: str | None = None,
    parallel: bool = True,
) -> TournamentReport:
    pairs = list(itertools.combinations(theories, 2))

    def _duel(pair):
        a, b = pair
        return run_duel(a, b, registry, rounds=rounds, history_dir=history_dir)

    if parallel and len(pairs) > 1:
        with ThreadPoolExecutor(max_workers=min(4, len(pairs))) as pool:
            duels = list(pool.map(_duel, pairs))
    else:
        duels = [_duel(p) for p in pairs]

    # rescore current registry theories (patches/forks may have appeared)
    current = registry.all()
    scores = [scoring.score_theory(t, generation=generation) for t in current]

    # novelty against an archive of seed features
    archive_features = [
        list(t.seed_vector or scoring.bridge.seed_vector(t).values) for t in current
    ]
    for s, t in zip(scores, current, strict=True):
        feats = list(t.seed_vector or scoring.bridge.seed_vector(t).values)
        others = [f for f in archive_features if f is not feats]
        s.novelty = scoring.novelty_score(feats, others)

    front = scoring.pareto_front(scores)
    elites = scoring.family_elites(scores)
    return TournamentReport(
        generation=generation,
        duels=duels,
        scores=scores,
        pareto_front=[s.theory_id for s in front],
        family_elites={fam: [s.theory_id for s in es] for fam, es in elites.items()},
    )
