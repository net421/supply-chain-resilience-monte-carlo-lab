# Model Card and Claim Boundaries

## Intended use

Education, portfolio evidence, scenario exploration, testable analytics engineering and human-reviewed resilience analysis.

## Not intended for

Production forecasting, calibrated disruption probability estimation, autonomous supplier decisions, inventory replenishment, routing or emergency response.

## Key assumptions

- reliability is normalized to `[0, 1]`;
- disruption impact subtracts from initial reliability;
- mitigation is represented by a multiplicative reduction after a threshold;
- scenario distributions are illustrative;
- iterations are independent within a run;
- no network topology, time dependence or recovery process is simulated directly.

## Interpretation

For lower-tail reliability, VaR 95% is the 5th percentile and CVaR 95% is the mean of observations at or below that percentile. Higher values are preferable.
