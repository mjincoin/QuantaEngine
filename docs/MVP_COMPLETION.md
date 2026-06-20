# MVP Completion Matrix

This matrix records the implementation and verification evidence for stages 0 through 11 of `plans/2026-06-20-QuantaEngine_PROJECT_PLAN.md`.

| Stage | Delivered | Verification |
|---|---|---|
| 0. Project foundation | Python 3.11+ package, `quanta` Typer CLI, README, editable install | `pip install -e ".[dev]"`; `quanta --version` |
| 1. Config and units | Pydantic schemas, relative inheritance, cycle detection, deep merge, unit helpers | `pytest tests/test_config_schema.py tests/test_units.py` |
| 2. Validation | Structured errors, warnings, scores, dimensional and density checks | `pytest tests/test_validation.py` |
| 3. Particles | Effective photon, neutrino, electron, proton, neutron, deuteron, helium-4 spectrum | `pytest tests/test_particles.py` |
| 4. Atoms | Reduced-mass Bohr radius, hydrogen binding, stability and chemistry window | `pytest tests/test_atomic.py` |
| 5. Nuclei | Deuteron, helium-4, hydrogen availability and heavy-seed criteria | `pytest tests/test_nuclear.py` |
| 6. Cosmology | Numerical FLRW age integration and 200-point expansion history | `pytest tests/test_cosmology.py` |
| 7. Stars | Fusion, lifetime, long-lived-star and heavy-element windows | `pytest tests/test_stars.py` |
| 8. Structure | Perturbation, galaxy, planet, metallicity and stable-orbit windows | `pytest tests/test_structure.py` |
| 9. Complexity | Bounded chemistry, energy, stability, element, life and civilization indicators | `pytest tests/test_complexity.py` |
| 10. Pipeline | Unified report, Markdown/JSON serialization, CLI run/validate/compare | `pytest tests/test_e2e_universe.py tests/test_cli.py` |
| 11. Experiments | Parameter scan DataFrame, CSV/PNG/Markdown artifacts, comparison deltas | `pytest tests/test_scan.py`; `quanta scan ...` |

## End-To-End Evidence

The final local acceptance run produced:

- `42 passed` across legacy regression tests and the new MVP suite.
- `88%` statement coverage for `quanta_engine`.
- Ruff checks clean and Mypy clean for all 44 new-package source files.
- No broken installed requirements from `python -m pip check`.
- All five Python examples completed successfully.

Standard universe checkpoints:

| Observable | Result | Acceptance |
|---|---:|---:|
| Hydrogen binding energy | 13.5983 eV | approximately 13.6 eV |
| Bohr radius | 5.2947e-11 m | approximately 5.29e-11 m |
| Universe age | 13.8029 Gyr | 10 to 20 Gyr |
| Stable deuteron and helium-4 | true | true |
| Long-lived stars | true | true |
| Structure growth | true | true |
| Life-window score | 0.9997 | greater than 0.5 |

Failure-universe checkpoints:

- Supercritical alpha: stable hydrogen false; life and civilization scores `0.0`; pipeline returns a complete invalid report.
- Gravity scale `100`: characteristic stellar lifetime `1.0e6` years; long-lived-star window false.
- Primordial amplitude `0`: structure, galaxy, and planet formation windows false.

## Model Boundary

Stages 0 through 11 and the first-round tasks A through O are complete for the documented MVP. The V2 through V6 roadmap remains intentionally unimplemented: Lagrangian DSL, external high-energy tools, precision cosmology, chemical networks, biological evolution, and civilization agents are future work.
