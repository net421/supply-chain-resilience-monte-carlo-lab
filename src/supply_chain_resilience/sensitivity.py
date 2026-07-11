from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np
import pandas as pd

from .scenarios import SCENARIO_CATALOG, Scenario
from .simulation import SupplyChainSimulator


@dataclass(frozen=True)
class SensitivityResult:
    parameter: str
    values: tuple[float, ...]
    mean_final: tuple[float, ...]
    delta: float
    best_value: float


def parameter_sweep(
    parameter: str,
    values: list[float] | np.ndarray,
    iterations: int = 2_000,
    seed: int = 42,
    base: Scenario | None = None,
) -> SensitivityResult:
    base = base or SCENARIO_CATALOG["baseline"]
    values_array = np.asarray(values, dtype=float)
    if values_array.size < 2:
        raise ValueError("at least two values are required")
    means: list[float] = []
    for value in values_array:
        if parameter in {
            "intervention_threshold",
            "mitigation_factor",
            "reliability_min",
        }:
            scenario = replace(base, **{parameter: float(value)})
        elif parameter == "disruption_max":
            scenario = replace(
                base,
                disruption=replace(base.disruption, maximum=float(value)),
            )
        else:
            raise ValueError(f"unknown parameter: {parameter}")
        scenario.validate()
        frame = SupplyChainSimulator(iterations, seed, scenario).run()
        means.append(float(frame["final_reliability"].mean()))
    means_array = np.asarray(means)
    best_index = int(np.argmax(means_array))
    return SensitivityResult(
        parameter=parameter,
        values=tuple(float(v) for v in values_array),
        mean_final=tuple(float(v) for v in means_array),
        delta=float(means_array.max() - means_array.min()),
        best_value=float(values_array[best_index]),
    )


def run_standard_sensitivity(
    iterations: int = 1_000,
    seed: int = 42,
) -> pd.DataFrame:
    sweeps = [
        parameter_sweep(
            "intervention_threshold",
            np.linspace(0.1, 0.5, 9),
            iterations,
            seed,
        ),
        parameter_sweep(
            "mitigation_factor",
            np.linspace(0.1, 0.9, 9),
            iterations,
            seed,
        ),
        parameter_sweep(
            "disruption_max",
            np.linspace(0.25, 0.75, 9),
            iterations,
            seed,
        ),
        parameter_sweep(
            "reliability_min",
            np.linspace(0.60, 0.95, 8),
            iterations,
            seed,
        ),
    ]
    rows = [
        {"parameter": sweep.parameter, "delta": sweep.delta, "best_value": sweep.best_value}
        for sweep in sweeps
    ]
    return pd.DataFrame(rows).sort_values("delta", ascending=False).reset_index(drop=True)
