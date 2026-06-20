# QuantaEngine 创世

QuantaEngine is an open-source multi-scale physics compiler. It starts with fundamental constants, effective particle parameters, and cosmological initial conditions, then evaluates a universe layer by layer:

```text
configuration -> validation -> particles -> atoms -> nuclei -> cosmology
              -> stars -> structure -> complexity -> universe report
```

The MVP answers interpretable feasibility questions: whether hydrogen and light nuclei are stable, whether long-lived stars and heavy elements are possible, whether primordial structure can grow, and whether physical windows for complex chemistry, life, and civilization remain open.

## What It Is

- A typed, inheritable YAML configuration system.
- A modular toy + analytic effective-physics pipeline.
- A reproducible CLI for reports, comparisons, and parameter scans.
- A tested foundation that can later swap in higher-fidelity solvers.

## What It Is Not

QuantaEngine is not a full Standard Model derivation, BBN network, stellar-evolution code, N-body simulation, chemistry network, biological model, or prediction of life. Life-window and civilization-potential scores are physical-feasibility indicators, not probabilities.

## Install

Python 3.11 or newer is required.

```bash
python -m pip install -e ".[dev]"
quanta --version
python -m pytest
```

## Generate A Standard Universe

```bash
quanta validate-config configs/standard_universe.yaml
quanta run configs/standard_universe.yaml \
  --output reports/standard.md \
  --json reports/standard.json
```

Expected standard-universe checkpoints include hydrogen binding near `13.6 eV`, a Bohr radius near `5.29e-11 m`, an age near `13.8 Gyr`, stable light nuclei, long-lived stars, and a nonzero complexity window.

## Compare Universes

```bash
quanta compare \
  configs/standard_universe.yaml \
  configs/strong_alpha_universe.yaml
```

## Scan A Fundamental Parameter

```bash
quanta scan configs/standard_universe.yaml \
  --param dimensionless.alpha_scale \
  --values 0.5,0.8,1.0,1.2,1.5 \
  --output reports/scan_alpha.csv
```

The scan writes CSV data, a PNG score plot, and a Markdown summary.

## Python API

```python
from quanta_engine.pipeline import run_universe_pipeline

report = run_universe_pipeline("configs/standard_universe.yaml")
print(report.to_markdown())
print(report.to_json_dict()["complexity"])
```

## cosmogenesis — multi-scheme parallel adversarial universe generation

The `cosmogenesis` package generates self-consistent universes with **multiple
independent schemes (paradigms) that run in parallel and never merge into a single
winner**. It has three clearly separated layers (see
[docs/design/REPO_STRUCTURE.md](docs/design/REPO_STRUCTURE.md)):

- `cosmogenesis.core` — the shared adversarial I/O contract: every scheme maps a
  `ParameterVector` to a `UniverseAssessment`.
- `cosmogenesis.schemes` — one **self-contained subpackage per scheme**, each with
  its own `engine.py` (physics) and `optimizer.py` (iterative path):

  | Scheme | Paradigm | Optimizer |
  |---|---|---|
  | `analytic_compiler` | forward closed-form effective-physics (white-box) | coordinate ascent |
  | `variational_relaxer` | self-consistency fixed point + cross-layer residual | (μ+λ) evolution strategy |
  | `minimal_axiom` | Carr–Rees anthropic inequalities, fewest parameters | coordinate hill-climb |

- `cosmogenesis.arena` — the platform where **named theory lineages** (`T-0001`…,
  each choosing one scheme) **attack** each other with schema-validated
  `ChallengeCard`s, **defend** per their `DefensePrior`, are judged by a
  deterministic **Verifier + Judge**, and are **patched / forked / left unchanged**
  by a `PatchGate` that preserves parents and **forbids merging**. Selection keeps a
  **Pareto front + family elites + novelty archive**, and duels/evolution run **in parallel**.

A **scheme** is a method library; a **theory** is a named, versioned lineage that
uses a scheme plus a config and keeps its own `history`. Adding a scheme means
dropping a subpackage in `cosmogenesis/schemes/` and registering it — no arena
code changes.

```bash
python -m cosmogenesis theory-list
python -m cosmogenesis duel theories/T-0001_conservative_eft/theory.yaml \
                            theories/T-0003_minimal_axiom/theory.yaml --rounds 1
python -m cosmogenesis evolve --generations 3 --min-families 3 --no-merge --out reports/arena
```

```python
from cosmogenesis import TheoryRegistry, evolve, list_schemes

print(list_schemes())  # ['analytic_compiler', 'variational_relaxer', 'minimal_axiom']
registry = TheoryRegistry.from_dir("theories")
report = evolve(registry.all(), registry, generations=3, min_families=3, out_dir="reports/arena")
print(report.final_families, report.allow_merge)  # multiple families survive; never merged
```

Design: [docs/design/REPO_STRUCTURE.md](docs/design/REPO_STRUCTURE.md),
[plans/2026-06-21-GENESIS_ARENA_V2_PARALLEL_ADVERSARIAL.md](plans/2026-06-21-GENESIS_ARENA_V2_PARALLEL_ADVERSARIAL.md).

## Configuration Inheritance

Variant universes inherit a complete parent and override only selected values:

```yaml
inherit: standard_universe.yaml
universe:
  name: strong_alpha_universe
dimensionless:
  alpha_scale: 1.2
```

Included variants cover strong electromagnetism, weak and strong gravity, unstable atoms, long-lived stars, and absent primordial perturbations.

## Repository Layout

```text
configs/                       universe inputs and variants
src/quanta_engine/             effective-physics base pipeline
src/quantaengine_lattice/      legacy scalar-field lattice prototype (independent)
src/cosmogenesis/              multi-scheme adversarial universe generation
  core/                          shared ParameterVector -> UniverseAssessment contract
  schemes/<name>/                one self-contained scheme (engine.py + optimizer.py)
  arena/                         theories duel / judge / patch-or-fork / evolve (no merge)
theories/T-NNNN_<family>/      named theory lineages + per-lineage history.jsonl
tests/                         unit, integration, CLI, scan, scheme, arena, and E2E tests
examples/                      runnable Python demos
reports/                       reproducible demonstration outputs
docs/design/REPO_STRUCTURE.md  the authoritative directory convention
plans/                         versioned, executable plan packages
```

The legacy `quantaengine_lattice` scalar-field lattice API (formerly `quantaengine`)
remains available for compatibility but is independent of the effective-physics and
adversarial stacks. New work should use `quanta_engine` and `cosmogenesis`.

## Scientific Boundaries

Every physical layer exposes assumptions, warnings, and intermediate values. See [docs/physics_assumptions.md](docs/physics_assumptions.md) for calibrated formulas and limitations, [docs/examples.md](docs/examples.md) for the acceptance scenarios, [docs/MVP_COMPLETION.md](docs/MVP_COMPLETION.md) for the stage-by-stage verification matrix, and [plans/quantaengine-mvp-v1/README.md](plans/quantaengine-mvp-v1/README.md) for the reusable execution package.

## Development

```bash
python -m pytest
ruff check src tests examples
mypy src/quanta_engine
```

GitHub Actions runs the test suite and generates a standard-universe Markdown and JSON report on every push and pull request.

## License

MIT License. See [LICENSE](LICENSE).
