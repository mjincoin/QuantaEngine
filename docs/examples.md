# Acceptance Examples

## Standard Universe

`quanta run configs/standard_universe.yaml` should report stable hydrogen, approximately `13.6 eV` binding, approximately `5.29e-11 m` Bohr radius, stable deuterium and helium-4, an age between `10` and `20 Gyr`, long-lived stars, structure growth, and nonzero life and civilization windows.

## Strong Electromagnetism

`strong_alpha_universe.yaml` raises binding energy and reduces atomic radius. `no_stable_atoms_universe.yaml` crosses `alpha=1`; the pipeline completes, validation marks it invalid, and chemistry, life, and civilization windows fall to zero.

## Strong Gravity

`strong_gravity_universe.yaml` shortens the characteristic stellar lifetime from `1e10` to `1e6` years and closes the long-lived-star window.

## No Primordial Perturbations

`no_perturbations_universe.yaml` completes normally but closes structure, galaxy, and planet formation windows.

## Reproducible Commands

```bash
python examples/demo.py
python examples/run_standard_universe.py
python examples/scan_alpha.py
python examples/scan_gravity.py
python examples/compare_universes.py
```
