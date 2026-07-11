import numpy as np
import pytest

from supply_chain_resilience.metrics import compare_scenarios, compute_risk_metrics, recovery_steps
from supply_chain_resilience.sensitivity import parameter_sweep, run_standard_sensitivity
from supply_chain_resilience.simulation import SupplyChainSimulator


def test_risk_metrics_are_consistent():
    frame = SupplyChainSimulator(5000, 42).run()
    metrics = compute_risk_metrics(frame)
    assert 0 <= metrics.mean_final <= metrics.mean_initial <= 1
    assert metrics.cvar_99 <= metrics.var_99 <= metrics.var_95
    assert metrics.cvar_95 <= metrics.var_95
    assert 0 <= metrics.intervention_rate_pct <= 100
    assert 0 <= metrics.below_threshold_pct <= 100


def test_invalid_threshold_fails():
    frame = SupplyChainSimulator(10).run()
    with pytest.raises(ValueError):
        compute_risk_metrics(frame, critical_threshold=1.5)


def test_compare_scenarios_is_ranked():
    results = {
        key: SupplyChainSimulator(300, 42, key).run()
        for key in ("baseline", "mild", "natural_disaster")
    }
    table = compare_scenarios(results)
    assert list(table["mean_final"]) == sorted(table["mean_final"], reverse=True)
    assert set(table["scenario_key"]) == set(results)


def test_compare_scenarios_requires_input():
    with pytest.raises(ValueError):
        compare_scenarios({})


def test_recovery_steps():
    assert recovery_steps(0.05, 0.05) > 0
    with pytest.raises(ValueError):
        recovery_steps(0)


def test_threshold_sensitivity_returns_expected_shape():
    result = parameter_sweep(
        "intervention_threshold",
        np.linspace(0.1, 0.5, 5),
        300,
        42,
    )
    assert len(result.values) == 5
    assert len(result.mean_final) == 5
    assert result.delta >= 0


def test_standard_sensitivity_has_four_parameters():
    table = run_standard_sensitivity(200, 42)
    assert len(table) == 4
    assert list(table["delta"]) == sorted(table["delta"], reverse=True)


def test_unknown_sensitivity_parameter_fails():
    with pytest.raises(ValueError):
        parameter_sweep("unknown", [0.1, 0.2], 20, 42)
