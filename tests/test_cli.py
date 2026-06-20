import json
from pathlib import Path

from typer.testing import CliRunner

from quanta_engine.cli import app

CONFIG = Path(__file__).parents[1] / "configs" / "standard_universe.yaml"
runner = CliRunner()


def test_version_and_validate_commands():
    version = runner.invoke(app, ["--version"])
    assert version.exit_code == 0
    assert "QuantaEngine" in version.stdout
    validation = runner.invoke(app, ["validate-config", str(CONFIG)])
    assert validation.exit_code == 0
    assert "Passed" in validation.stdout


def test_run_command_writes_markdown_and_json(tmp_path: Path):
    markdown = tmp_path / "standard.md"
    json_path = tmp_path / "standard.json"
    result = runner.invoke(
        app,
        ["run", str(CONFIG), "--output", str(markdown), "--json", str(json_path)],
    )
    assert result.exit_code == 0, result.stdout
    assert markdown.exists()
    assert json.load(json_path.open(encoding="utf-8"))["final_verdict"] != "invalid"
