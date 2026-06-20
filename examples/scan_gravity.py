from quanta_engine.experiments.scan import save_scan_artifacts, scan_parameter

frame = scan_parameter(
    "configs/standard_universe.yaml",
    "dimensionless.gravity_scale",
    [0.1, 0.3, 1.0, 10.0, 100.0],
)
save_scan_artifacts(frame, "reports/scan_gravity.csv", "dimensionless.gravity_scale")
print(frame.to_string(index=False))
