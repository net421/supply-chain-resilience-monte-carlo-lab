# Architecture

The lab separates configuration, stochastic sampling, simulation, metrics, sensitivity and evidence publication.

1. `distributions.py` validates and samples five distribution families.
2. `scenarios.py` defines immutable scenario contracts.
3. `simulation.py` produces deterministic vectorized event rows.
4. `metrics.py` computes lower-tail reliability VaR/CVaR and scenario comparisons.
5. `sensitivity.py` uses common random seeds across sweep points to reduce Monte Carlo noise.
6. `reporting.py` validates inputs and atomically writes Markdown, JSON and three headless PNG charts.
7. `cli.py` exposes installable fail-closed commands.

No module performs network access or autonomous operational writes.
