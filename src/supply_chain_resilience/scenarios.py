from __future__ import annotations

from dataclasses import dataclass

from .distributions import DistType, Distribution


@dataclass(frozen=True)
class Scenario:
    name: str
    description: str
    reliability_min: float = 0.80
    reliability_max: float = 1.00
    disruption: Distribution = Distribution()
    intervention_threshold: float = 0.30
    mitigation_factor: float = 0.50

    def validate(self) -> None:
        if not 0 <= self.reliability_min < self.reliability_max <= 1:
            raise ValueError("reliability bounds must satisfy 0 <= min < max <= 1")
        if not 0 <= self.intervention_threshold <= 1:
            raise ValueError("intervention_threshold must be within [0, 1]")
        if not 0 <= self.mitigation_factor <= 1:
            raise ValueError("mitigation_factor must be within [0, 1]")
        self.disruption.validate()


def _scenario(name: str, description: str, **kwargs: object) -> Scenario:
    scenario = Scenario(name=name, description=description, **kwargs)
    scenario.validate()
    return scenario


SCENARIO_CATALOG: dict[str, Scenario] = {
    "baseline": _scenario("Baseline", "Moderate uniform mixed-risk environment."),
    "bullwhip": _scenario(
        "Bullwhip Effect",
        "Amplified upstream variability.",
        disruption=Distribution(DistType.TRIANGULAR, 0.0, 0.7, mode=0.5),
        intervention_threshold=0.35,
    ),
    "natural_disaster": _scenario(
        "Natural Disaster",
        "Heavy-tailed high-impact event.",
        disruption=Distribution(DistType.LOGNORMAL, 0.0, 0.9, mean=-0.5, sigma=0.9),
        intervention_threshold=0.45,
        mitigation_factor=0.30,
    ),
    "supplier_bankruptcy": _scenario(
        "Supplier Bankruptcy",
        "Critical tier-one supplier failure.",
        reliability_min=0.70,
        reliability_max=0.90,
        disruption=Distribution(DistType.TRIANGULAR, 0.2, 0.8, mode=0.6),
        intervention_threshold=0.40,
        mitigation_factor=0.35,
    ),
    "labor_strike": _scenario(
        "Labor Strike",
        "Expert-elicited PERT disruption.",
        disruption=Distribution(DistType.PERT, 0.0, 0.6, mode=0.30),
        intervention_threshold=0.35,
    ),
    "cyber_attack": _scenario(
        "Cyber Attack",
        "Truncated-normal systems disruption.",
        disruption=Distribution(DistType.NORMAL_TRUNC, 0.0, 0.6, mean=0.35, scale=0.10),
        intervention_threshold=0.40,
        mitigation_factor=0.40,
    ),
    "global_pandemic": _scenario(
        "Global Pandemic",
        "Systemic shock with reduced baseline reliability.",
        reliability_min=0.65,
        reliability_max=0.90,
        disruption=Distribution(DistType.UNIFORM, 0.1, 0.6),
        intervention_threshold=0.30,
        mitigation_factor=0.40,
    ),
    "mild": _scenario(
        "Mild Disruptions",
        "Minor operational variability.",
        disruption=Distribution(DistType.UNIFORM, 0.0, 0.2),
        intervention_threshold=0.15,
        mitigation_factor=0.60,
    ),
}
