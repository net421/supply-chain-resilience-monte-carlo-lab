from __future__ import annotations

import numpy as np
import pandas as pd

from .distributions import sample
from .scenarios import SCENARIO_CATALOG, Scenario


REQUIRED_COLUMNS = (
    "iteration",
    "scenario",
    "seed",
    "initial_reliability",
    "disruption_raw",
    "disruption_impact",
    "final_reliability",
    "intervention_triggered",
)


class SupplyChainSimulator:
    def __init__(
        self,
        iterations: int = 10_000,
        seed: int = 42,
        scenario: Scenario | str = "baseline",
    ) -> None:
        if iterations <= 0:
            raise ValueError("iterations must be positive")
        if isinstance(scenario, str):
            try:
                scenario = SCENARIO_CATALOG[scenario]
            except KeyError as exc:
                raise ValueError(f"unknown scenario: {scenario}") from exc
        scenario.validate()
        self.iterations = iterations
        self.seed = int(seed)
        self.scenario = scenario

    def run(self) -> pd.DataFrame:
        rng = np.random.default_rng(self.seed)
        initial = rng.uniform(
            self.scenario.reliability_min,
            self.scenario.reliability_max,
            self.iterations,
        )
        disruption_raw = sample(rng, self.iterations, self.scenario.disruption)
        triggered = disruption_raw > self.scenario.intervention_threshold
        disruption_impact = np.where(
            triggered,
            disruption_raw * self.scenario.mitigation_factor,
            disruption_raw,
        )
        final = np.clip(initial - disruption_impact, 0.0, 1.0)
        frame = pd.DataFrame(
            {
                "iteration": np.arange(self.iterations, dtype=int),
                "scenario": self.scenario.name,
                "seed": self.seed,
                "initial_reliability": initial,
                "disruption_raw": disruption_raw,
                "disruption_impact": disruption_impact,
                "final_reliability": final,
                "intervention_triggered": triggered,
            }
        )
        validate_frame(frame)
        return frame


def validate_frame(frame: pd.DataFrame) -> None:
    missing = set(REQUIRED_COLUMNS) - set(frame.columns)
    if missing:
        raise ValueError(f"missing required columns: {sorted(missing)}")
    if frame.empty:
        raise ValueError("simulation frame must not be empty")
    numeric = frame[
        ["initial_reliability", "disruption_raw", "disruption_impact", "final_reliability"]
    ]
    if not np.isfinite(numeric.to_numpy()).all():
        raise ValueError("simulation contains non-finite values")
    if (
        not frame["initial_reliability"].between(0, 1).all()
        or not frame["final_reliability"].between(0, 1).all()
    ):
        raise ValueError("reliability values must be within [0, 1]")
    if (frame["disruption_impact"] < 0).any() or (
        frame["disruption_impact"] > frame["disruption_raw"] + 1e-12
    ).any():
        raise ValueError(
            "disruption impact must be non-negative and no greater than raw disruption"
        )
