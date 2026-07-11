from __future__ import annotations

import json
from pathlib import Path

import click

from .metrics import compare_scenarios, compute_risk_metrics
from .reporting import atomic_write_csv, generate_report, load_results
from .scenarios import SCENARIO_CATALOG
from .sensitivity import run_standard_sensitivity
from .simulation import SupplyChainSimulator


@click.group()
def cli() -> None:
    """Supply-chain resilience Monte Carlo laboratory."""


@cli.command()
@click.option(
    "--scenario",
    type=click.Choice(sorted(SCENARIO_CATALOG)),
    default="baseline",
    show_default=True,
)
@click.option("--iterations", type=click.IntRange(min=1), default=10_000, show_default=True)
@click.option("--seed", type=int, default=42, show_default=True)
@click.option("--output", type=click.Path(path_type=Path, dir_okay=False), required=True)
def simulate(scenario: str, iterations: int, seed: int, output: Path) -> None:
    """Run one deterministic scenario and atomically write CSV evidence."""
    frame = SupplyChainSimulator(iterations, seed, scenario).run()
    atomic_write_csv(frame, output)
    click.echo(
        json.dumps(
            {"rows": len(frame), "scenario": scenario, "seed": seed, "output": str(output)},
            sort_keys=True,
        )
    )


@cli.command()
@click.option(
    "--input",
    "input_path",
    type=click.Path(path_type=Path, exists=True, dir_okay=False),
    required=True,
)
@click.option("--output-dir", type=click.Path(path_type=Path, file_okay=False), required=True)
def report(input_path: Path, output_dir: Path) -> None:
    """Generate a complete fail-closed report bundle."""
    artifacts = generate_report(load_results(input_path), output_dir)
    click.echo(
        json.dumps({name: str(path) for name, path in artifacts.items()}, sort_keys=True)
    )


@cli.command()
@click.option("--iterations", type=click.IntRange(min=1), default=2_000, show_default=True)
@click.option("--seed", type=int, default=42, show_default=True)
@click.option("--output", type=click.Path(path_type=Path, dir_okay=False), required=True)
def compare(iterations: int, seed: int, output: Path) -> None:
    """Run every catalog scenario and write a ranked comparison CSV."""
    results = {
        key: SupplyChainSimulator(iterations, seed, key).run()
        for key in SCENARIO_CATALOG
    }
    table = compare_scenarios(results)
    output.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(output, index=False, lineterminator="\n")
    click.echo(json.dumps({"scenarios": len(table), "output": str(output)}, sort_keys=True))


@cli.command()
@click.option("--iterations", type=click.IntRange(min=1), default=1_000, show_default=True)
@click.option("--seed", type=int, default=42, show_default=True)
@click.option("--output", type=click.Path(path_type=Path, dir_okay=False), required=True)
def sensitivity(iterations: int, seed: int, output: Path) -> None:
    """Run the standard four-parameter sweep."""
    table = run_standard_sensitivity(iterations, seed)
    output.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(output, index=False, lineterminator="\n")
    click.echo(json.dumps({"parameters": len(table), "output": str(output)}, sort_keys=True))


@cli.command()
@click.option(
    "--input",
    "input_path",
    type=click.Path(path_type=Path, exists=True, dir_okay=False),
    required=True,
)
def metrics(input_path: Path) -> None:
    """Print risk metrics as JSON."""
    click.echo(
        json.dumps(
            compute_risk_metrics(load_results(input_path)).as_dict(),
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    cli()
