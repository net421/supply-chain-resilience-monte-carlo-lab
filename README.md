# Supply Chain Resilience Monte Carlo Lab

A deterministic Python laboratory for evaluating supply-chain reliability under disruption, mitigation thresholds and scenario uncertainty.

## What it demonstrates

- vectorized Monte Carlo simulation with local seeded RNG;
- eight disruption scenarios and five distribution families;
- intervention-threshold and mitigation-policy analysis;
- lower-tail reliability VaR and CVaR;
- recovery-time and resilience metrics;
- parameter-sweep sensitivity analysis;
- fail-closed CSV, Markdown, PNG and JSON evidence generation;
- reproducible CLI, tests and GitHub Actions.

## Architecture

```text
Scenario + seed + iteration count
              |
              v
      Monte Carlo engine
              |
      simulation_results.csv
          /       |       \
         v        v        v
 risk metrics  sensitivity  report bundle
  JSON/CSV      CSV/JSON    Markdown + 3 PNGs
```

## Quick start

```bash
python -m pip install -e ".[dev]"
sc-resilience simulate --scenario baseline --iterations 1000 --seed 42 --output output/simulation.csv
sc-resilience report --input output/simulation.csv --output-dir output/report
sc-resilience compare --iterations 1000 --seed 42 --output output/scenarios.csv
make verify
```

The `verify` target runs the test suite, executes the same simulation twice and checks byte-identical CSV output, creates all report artifacts, evaluates all catalog scenarios and writes release evidence.

## Scenario catalog

`baseline`, `bullwhip`, `natural_disaster`, `supplier_bankruptcy`, `labor_strike`, `cyber_attack`, `global_pandemic`, and `mild`.

## Model boundary

This is a synthetic, local Monte Carlo laboratory. Reliability is an abstract normalized score, not a calibrated probability of real-world service or failure. Scenario parameters are illustrative and must be estimated from domain data before operational use. Outputs support human analysis; they do not authorize procurement, inventory, supplier or logistics actions.

## Portfolio relationship

This repository connects the historical near-critical research and Supply Chain Digital Twin lineage to the active Control Tower, Causal Experimentation Lab and Decision Twin Agent. These are evidence relationships, not a claim of one deployed production platform.

## Security

The core package performs no network calls, reads no credentials and writes only to user-supplied output paths. Generated data and release evidence are excluded from version control.

## License

MIT
