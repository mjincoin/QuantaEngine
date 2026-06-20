from quanta_engine.pipeline import run_universe_pipeline

report = run_universe_pipeline("configs/standard_universe.yaml")
report.write("reports/standard.md", "reports/standard.json")
print(report.final_verdict)
