"""Run the parallel multi-scheme adversarial arena and persist the results.

Durable outputs (git-tracked):
- theories/T-NNNN_<family>/history.jsonl   per-lineage iteration history
- plans/iterations/<stamp>_genN.md         the auto-generated next-iteration plan
"""

from cosmogenesis import TheoryRegistry, evolve, list_schemes

print("schemes:", list_schemes())

registry = TheoryRegistry.from_dir("theories")
report = evolve(
    registry.all(),
    registry,
    generations=3,
    min_families=3,
    out_dir="reports/arena",          # latest human-readable snapshot
    lineage_root="theories",          # durable per-lineage history.jsonl
    plan_dir="plans/iterations",      # auto-generated next-iteration plan
)

print("final families:", report.final_families, "| allow_merge:", report.allow_merge)
print("next-iteration plan:", report.iteration_plan)
