from __future__ import annotations

import json
import os
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from .metrics import compute_risk_metrics
from .simulation import validate_frame

ARTIFACT_NAMES = (
    "supply_chain_report.md",
    "risk_metrics.json",
    "reliability_distribution.png",
    "reliability_scatter.png",
    "reliability_boxplot.png",
)


def load_results(path: str | Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    if "intervention_triggered" in frame.columns:
        raw = frame["intervention_triggered"]
        if raw.dtype != bool:
            mapped = raw.astype(str).str.lower().map(
                {"true": True, "false": False, "1": True, "0": False}
            )
            if mapped.isna().any():
                raise ValueError("intervention_triggered contains invalid values")
            frame["intervention_triggered"] = mapped.astype(bool)
    validate_frame(frame)
    return frame


def generate_report(
    frame: pd.DataFrame,
    output_dir: str | Path,
    critical_threshold: float = 0.50,
) -> dict[str, Path]:
    validate_frame(frame)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    metrics = compute_risk_metrics(frame, critical_threshold)

    histogram = output / "reliability_distribution.png"
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(frame["final_reliability"], bins=30, edgecolor="black")
    ax.axvline(metrics.var_95, linestyle="--", label="VaR 95%")
    ax.set(
        xlabel="Final reliability",
        ylabel="Frequency",
        title="Final reliability distribution",
    )
    ax.legend()
    fig.tight_layout()
    fig.savefig(histogram, dpi=150)
    plt.close(fig)

    scatter = output / "reliability_scatter.png"
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(
        frame["initial_reliability"],
        frame["final_reliability"],
        s=8,
        alpha=0.35,
    )
    ax.set(
        xlabel="Initial reliability",
        ylabel="Final reliability",
        title="Initial vs final reliability",
    )
    fig.tight_layout()
    fig.savefig(scatter, dpi=150)
    plt.close(fig)

    boxplot = output / "reliability_boxplot.png"
    groups = [
        frame.loc[~frame["intervention_triggered"], "final_reliability"],
        frame.loc[frame["intervention_triggered"], "final_reliability"],
    ]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.boxplot(groups, tick_labels=["No intervention", "Intervention"])
    ax.set(ylabel="Final reliability", title="Reliability by intervention status")
    fig.tight_layout()
    fig.savefig(boxplot, dpi=150)
    plt.close(fig)

    metrics_path = output / "risk_metrics.json"
    metrics_path.write_text(
        json.dumps(metrics.as_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    report = output / "supply_chain_report.md"
    report.write_text(
        "# Supply Chain Resilience Report\n\n"
        f"- Iterations: {len(frame)}\n"
        f"- Scenario: {frame['scenario'].iloc[0]}\n"
        f"- Seed: {int(frame['seed'].iloc[0])}\n"
        f"- Mean initial reliability: {metrics.mean_initial:.4f}\n"
        f"- Mean final reliability: {metrics.mean_final:.4f}\n"
        f"- VaR 95% (5th percentile): {metrics.var_95:.4f}\n"
        f"- CVaR 95%: {metrics.cvar_95:.4f}\n"
        f"- Intervention rate: {metrics.intervention_rate_pct:.2f}%\n"
        f"- Below critical threshold: {metrics.below_threshold_pct:.2f}%\n\n"
        "These synthetic results require human interpretation and do not authorize "
        "operational actions.\n",
        encoding="utf-8",
    )

    artifacts = {name: output / name for name in ARTIFACT_NAMES}
    missing = [
        name
        for name, path in artifacts.items()
        if not path.is_file() or path.stat().st_size == 0
    ]
    if missing:
        raise RuntimeError(f"report generation incomplete: {missing}")
    return artifacts


def atomic_write_csv(frame: pd.DataFrame, path: str | Path) -> Path:
    validate_frame(frame)
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    frame.to_csv(temporary, index=False, lineterminator="\n")
    os.replace(temporary, destination)
    return destination
