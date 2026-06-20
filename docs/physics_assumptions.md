# Physics Assumptions And Interpretation Limits

QuantaEngine v0.2 is an effective-theory MVP. It compiles a small set of physical parameters into transparent feasibility indicators. It does not claim precision prediction outside the formulas and calibrations listed here.

## Standard Physics Used Directly

- SI and high-energy unit conversions use exact or standard reference constants.
- Hydrogen uses the reduced-mass Bohr radius `a0 = hbar / (mu c alpha)`.
- Hydrogen binding uses `E1 = mu c^2 alpha^2 / 2`.
- The cosmological background uses the FLRW relation with radiation, matter, curvature, and dark-energy density terms.
- The age of the universe is numerically integrated from `a=1e-8` to `a=1`.

These formulas are standard, but their inputs remain effective parameters and no uncertainty propagation is performed.

## Toy Models

- The particle spectrum is assembled from configured electron, proton, neutron, pion, and binding-energy values. It is not derived from a Lagrangian.
- Light-nucleus stability checks only the sign of scaled deuteron and helium-4 binding energies.
- Hydrogen availability uses the configured proton, electron, and neutron mass ordering.
- Stellar lifetime scales as `1e10 years / gravity_scale^2`, with an extra high-alpha penalty.
- Fusion requires stable hydrogen, stable light nuclei, a broad gravity range, and `alpha < 0.2`.
- Heavy-element production requires fusion and a characteristic lifetime above one million years.

These models are designed for parameter sensitivity and failure-mode exploration, not precision astrophysics.

## Empirical Heuristics

- The configured primordial value is a power amplitude, so its square root is compared with the `1e-7` to `1e-3` structure-growth amplitude window.
- Matter density must exceed `0.05`, and the universe must be older than `0.5 Gyr`, for structure growth.
- Galaxy formation is suppressed when the effective dark-energy density exceeds ten times matter density.
- Planet formation requires galaxy formation and stellar heavy-element production.
- Stable orbits require the effective gravity scale to remain in the broad calibrated interval `1e-4` to `1e4`.

Thresholds are explicit so later modules can replace them without changing the report contract.

## Complexity Scores

All scores are bounded to `[0, 1]` and combine interpretable layer outputs:

- `chemistry_score` compares hydrogen energy and length scales with the standard universe and is zero without stable hydrogen.
- `energy_gradient_score` tracks fusion and long-lived stars.
- `stability_score` combines atoms, light nuclei, cosmic age, and stellar lifetime.
- `element_diversity_score` tracks heavy elements and planets.
- `life_window_score` is gated by the chemistry score.
- `civilization_potential_score` is gated by the life window and combines stability, energy, and stable planetary environments.

The weights are engineering choices for an explainable MVP. They are not fitted to observations.

## Parameters That Are Placeholders

- `strong_scale` and `weak_scale` are effective multipliers, not running couplings.
- `cosmological_constant_scale` multiplies the configured dark-energy density.
- The effective neutrino is massless in the MVP particle table.
- The pion mass is validated and reported as input metadata but is not yet propagated into nuclear rates.
- The BBN model label is reserved for future pluggable networks.

## Claims The Reports Do Not Make

- A life-window score is not the probability that life appears.
- A civilization-potential score is not the probability that civilization appears.
- A high score does not prove habitability or biological evolution.
- A low score identifies a bottleneck in this model, not an impossibility theorem.
- Agreement with standard-universe checkpoints validates implementation behavior, not the completeness of the physical model.
