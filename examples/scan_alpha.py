from quanta_engine.experiments.scan import save_scan_artifacts, scan_parameter

frame = scan_parameter(
    "configs/standard_universe.yaml",
    "dimensionless.alpha_scale",
    [0.5, 0.8, 1.0, 1.2, 1.5],
)
save_scan_artifacts(frame, "reports/scan_alpha.csv", "dimensionless.alpha_scale")
print(frame.to_string(index=False))
