import json

import pandas as pd
import pytest
from click.testing import CliRunner

from supply_chain_resilience.cli import cli
from supply_chain_resilience.reporting import ARTIFACT_NAMES, atomic_write_csv, generate_report, load_results
from supply_chain_resilience.simulation import SupplyChainSimulator


def test_atomic_csv_round_trip(tmp_path):
    frame = SupplyChainSimulator(100, 7).run()
    path = atomic_write_csv(frame, tmp_path / "results.csv")
    loaded = load_results(path)
    pd.testing.assert_frame_equal(frame, loaded, check_dtype=False)


def test_report_creates_complete_bundle(tmp_path):
    artifacts = generate_report(SupplyChainSimulator(250, 7).run(), tmp_path)
    assert set(artifacts) == set(ARTIFACT_NAMES)
    assert all(path.is_file() and path.stat().st_size > 0 for path in artifacts.values())
    metrics = json.loads((tmp_path / "risk_metrics.json").read_text())
    assert "cvar_95" in metrics


def test_load_results_rejects_bad_csv(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text("x\n1\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_results(path)


def test_cli_simulate_and_report(tmp_path):
    runner = CliRunner()
    csv_path = tmp_path / "simulation.csv"
    result = runner.invoke(
        cli,
        ["simulate", "--iterations", "120", "--seed", "9", "--output", str(csv_path)],
    )
    assert result.exit_code == 0, result.output
    assert len(pd.read_csv(csv_path)) == 120
    report_dir = tmp_path / "report"
    result = runner.invoke(
        cli,
        ["report", "--input", str(csv_path), "--output-dir", str(report_dir)],
    )
    assert result.exit_code == 0, result.output
    assert all((report_dir / name).is_file() for name in ARTIFACT_NAMES)


def test_cli_compare(tmp_path):
    runner = CliRunner()
    output = tmp_path / "compare.csv"
    result = runner.invoke(
        cli,
        ["compare", "--iterations", "50", "--output", str(output)],
    )
    assert result.exit_code == 0, result.output
    assert len(pd.read_csv(output)) == 8


def test_cli_sensitivity(tmp_path):
    runner = CliRunner()
    output = tmp_path / "sensitivity.csv"
    result = runner.invoke(
        cli,
        ["sensitivity", "--iterations", "50", "--output", str(output)],
    )
    assert result.exit_code == 0, result.output
    assert len(pd.read_csv(output)) == 4


def test_cli_rejects_zero_iterations(tmp_path):
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["simulate", "--iterations", "0", "--output", str(tmp_path / "x.csv")],
    )
    assert result.exit_code != 0


def test_markdown_states_human_review(tmp_path):
    generate_report(SupplyChainSimulator(50).run(), tmp_path)
    text = (tmp_path / "supply_chain_report.md").read_text(encoding="utf-8")
    assert "human interpretation" in text
    assert "do not authorize operational actions" in text
