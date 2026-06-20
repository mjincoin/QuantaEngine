from quanta_engine.pipeline import run_universe_pipeline

report = run_universe_pipeline("configs/standard_universe.yaml")
print(report.to_markdown())
