# MVP API Reference

## Configuration

`quanta_engine.core.schema.load_config(path)` loads YAML, follows `inherit` files relative to the child, deep-merges overrides, detects cycles, and validates the result as `UniverseConfig`.

## Pipeline

`quanta_engine.pipeline.run_universe_pipeline(path_or_config)` returns `UniverseReport` after running validation, particles, atomic, nuclear, cosmology, stellar, structure, and complexity layers.

## Reports

`UniverseReport.to_markdown()` and `UniverseReport.to_json_dict()` produce serializable reports. `UniverseReport.write(markdown_path, json_path)` creates either or both files.

## Experiments

- `scan_parameter(base_config_path, parameter_path, values)` returns a pandas DataFrame.
- `save_scan_artifacts(frame, csv_path, parameter_path)` writes CSV, PNG, and Markdown outputs.
- `compare_universes(config_a, config_b)` returns key values and numeric deltas.
