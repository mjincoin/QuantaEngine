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
configs/                 universe inputs and variants
src/quanta_engine/       multi-scale effective universe pipeline
src/quantaengine/        legacy scalar-field lattice prototype
tests/                   unit, integration, CLI, scan, and E2E tests
examples/                runnable Python demos
reports/                 reproducible demonstration outputs
docs/physics_assumptions.md
plans/                   detailed execution plan
```

The original `quantaengine` scalar-field lattice API remains available for compatibility. New effective-universe work should use `quanta_engine` and the `quanta` CLI.

## Scientific Boundaries

Every physical layer exposes assumptions, warnings, and intermediate values. See [docs/physics_assumptions.md](docs/physics_assumptions.md) for calibrated formulas and limitations, [docs/examples.md](docs/examples.md) for the acceptance scenarios, and [docs/MVP_COMPLETION.md](docs/MVP_COMPLETION.md) for the stage-by-stage verification matrix.

## Development

```bash
python -m pytest
ruff check src tests examples
mypy src/quanta_engine
```

GitHub Actions runs the test suite and generates a standard-universe Markdown and JSON report on every push and pull request.

## License

MIT License. See [LICENSE](LICENSE).
