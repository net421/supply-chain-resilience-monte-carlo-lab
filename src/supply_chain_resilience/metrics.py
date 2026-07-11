from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd

from .simulation import validate_frame


@dataclass(frozen=True)
class RiskMetrics:
    mean_initial: float
    mean_final: float
    std_final: float
    var_95: float
    var_99: float
    cvar_95: float
    cvar_99: float
    degradation_pct: float
    resilience_ratio: float
    below_threshold_pct: float
    intervention_rate_pct: float

    def as_dict(self) -> dict[str, float]:
        return asdict(self)


def compute_risk_metrics(
    frame: pd.DataFrame,
    critical_threshold: float = 0.50,
) -> RiskMetrics:
    validate_frame(frame)
    if not 0 <= critical_threshold <= 1:
        raise ValueError("critical_threshold must be within [0, 1]")
    initial = frame["initial_reliability"].to_numpy(float)
    final = frame["final_reliability"].to_numpy(float)
    mean_initial = float(initial.mean())
    mean_final = float(final.mean())
    var_95 = float(np.percentile(final, 5))
    var_99 = float(np.percentile(final, 1))
    return RiskMetrics(
        mean_initial=mean_initial,
        mean_final=mean_final,
        std_final=float(final.std()),
        var_95=var_95,
        var_99=var_99,
        cvar_95=float(final[final <= var_95].mean()),
        cvar_99=float(final[final <= var_99].mean()),
        degradation_pct=float((mean_initial - mean_final) / mean_initial * 100),
        resilience_ratio=float(mean_final / mean_initial),
        below_threshold_pct=float((final < critical_threshold).mean() * 100),
        intervention_rate_pct=float(frame["intervention_triggered"].mean() * 100),
    )


def compare_scenarios(
    results: dict[str, pd.DataFrame],
    critical_threshold: float = 0.50,
) -> pd.DataFrame:
    if not results:
        raise ValueError("results must not be empty")
    rows = []
    for key, frame in results.items():
        rows.append(
            {
                "scenario_key": key,
                "iterations": len(frame),
                **compute_risk_metrics(frame, critical_threshold).as_dict(),
            }
        )
    return (
        pd.DataFrame(rows)
        .sort_values("mean_final", ascending=False)
        .reset_index(drop=True)
    )


def recovery_steps(
    recovery_rate: float = 0.05,
    target_remaining: float = 0.05,
) -> float:
    if not 0 < recovery_rate < 1 or not 0 < target_remaining < 1:
        raise ValueError("recovery_rate and target_remaining must be within (0, 1)")
    return float(np.log(target_remaining) / np.log(1 - recovery_rate))
