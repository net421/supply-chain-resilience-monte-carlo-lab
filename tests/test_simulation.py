import pandas as pd
import pytest

from supply_chain_resilience.scenarios import SCENARIO_CATALOG, Scenario
from supply_chain_resilience.simulation import REQUIRED_COLUMNS, SupplyChainSimulator, validate_frame


def test_catalog_has_eight_scenarios():
    assert len(SCENARIO_CATALOG) == 8


@pytest.mark.parametrize("key", sorted(SCENARIO_CATALOG))
def test_every_scenario_runs(key):
    frame = SupplyChainSimulator(200, 17, key).run()
    assert tuple(frame.columns) == REQUIRED_COLUMNS
    assert len(frame) == 200
    assert frame["scenario"].nunique() == 1


def test_same_seed_is_byte_identical():
    first = SupplyChainSimulator(500, 42, "baseline").run().to_csv(index=False)
    second = SupplyChainSimulator(500, 42, "baseline").run().to_csv(index=False)
    assert first == second


def test_different_scenarios_change_results():
    baseline = SupplyChainSimulator(1000, 42, "baseline").run()
    disaster = SupplyChainSimulator(1000, 42, "natural_disaster").run()
    assert baseline["final_reliability"].mean() != disaster["final_reliability"].mean()


def test_intervention_never_increases_disruption():
    frame = SupplyChainSimulator(1000, 42, "baseline").run()
    assert (frame["disruption_impact"] <= frame["disruption_raw"]).all()


def test_invalid_iterations_fail():
    with pytest.raises(ValueError):
        SupplyChainSimulator(0)


def test_unknown_scenario_fails():
    with pytest.raises(ValueError):
        SupplyChainSimulator(10, scenario="unknown")


def test_invalid_scenario_contract_fails():
    with pytest.raises(ValueError):
        Scenario("bad", "bad", reliability_min=0.9, reliability_max=0.8).validate()


def test_validation_rejects_missing_columns():
    with pytest.raises(ValueError):
        validate_frame(pd.DataFrame({"x": [1]}))
