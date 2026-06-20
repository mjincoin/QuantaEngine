.PHONY: install test lint demo clean

install:
	python -m pip install -e .[dev]

test:
	python -m pytest

lint:
	ruff check src tests examples

demo:
	quanta run configs/standard_universe.yaml --output reports/standard.md --json reports/standard.json

clean:
	rm -rf runs outputs build dist *.egg-info .pytest_cache .ruff_cache .mypy_cache
