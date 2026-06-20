# Changelog

## Unreleased

- Added `cosmogenesis`, a multi-scheme parallel adversarial universe-generation
  platform, organized into three clearly named layers
  (see `docs/design/REPO_STRUCTURE.md`):
  - `cosmogenesis.core` — shared `ParameterVector -> UniverseAssessment` contract.
  - `cosmogenesis.schemes` — one self-contained subpackage per scheme
    (`engine.py` + `optimizer.py`): `analytic_compiler` (forward closed-form),
    `variational_relaxer` (self-consistency fixed point), `minimal_axiom`
    (Carr–Rees anthropic inequalities). Register a new scheme without touching the arena.
  - `cosmogenesis.arena` — file-backed `TheorySpec` lineages, schema-validated
    Challenge/Defense cards, a deterministic Verifier + Judge, a PatchGate that
    patches/forks but never merges (parents preserved), multi-objective scoring with
    Pareto front + family elites + novelty archive, and parallel duel/tournament/evolution.
- Added the `genesis-arena` CLI (`python -m cosmogenesis`: `theory-list`, `score`,
  `duel`, `tournament`, `evolve --no-merge`) and three starter theories
  (`T-0001`/`T-0002`/`T-0003`).
- Renamed the legacy `quantaengine` package to `quantaengine_lattice` to remove the
  near-identical-name confusion with `quanta_engine` (the `quantaengine` console
  script is unchanged).
- Retired the earlier two-scheme "consensus" arena in favour of the no-merge,
  multi-lineage platform above.
- Design docs: `docs/design/REPO_STRUCTURE.md`,
  `plans/2026-06-21-GENESIS_ARENA_V2_PARALLEL_ADVERSARIAL.md`.

## 0.2.0

- Added the typed, inheritable effective-universe configuration system.
- Added particle, atomic, nuclear, cosmology, stellar, structure, and complexity layers.
- Added Markdown and JSON universe reports plus comparison and parameter scanning.
- Added variant configurations, end-to-end tests, examples, physics assumptions, and CI report generation.
- Preserved the original `quantaengine` scalar-lattice prototype API.

## 0.1.0

- Initial GitHub-ready seed repository.
- Added config-driven universe generation.
- Added primordial field generation, microscopic chaos, Friedmann-like expansion, scalar-field lattice evolution, CLI, examples, docs, tests, and GitHub Actions.
