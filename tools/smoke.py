from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path

from supply_chain_resilience.metrics import compare_scenarios
from supply_chain_resilience.reporting import ARTIFACT_NAMES, atomic_write_csv, generate_report
from supply_chain_resilience.scenarios import SCENARIO_CATALOG
from supply_chain_resilience.sensitivity import run_standard_sensitivity
from supply_chain_resilience.simulation import SupplyChainSimulator


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        first = atomic_write_csv(
            SupplyChainSimulator(500, 42, "baseline").run(),
            root / "first.csv",
        )
        second = atomic_write_csv(
            SupplyChainSimulator(500, 42, "baseline").run(),
            root / "second.csv",
        )
        assert first.read_bytes() == second.read_bytes()
        artifacts = generate_report(
            SupplyChainSimulator(500, 42, "baseline").run(),
            root / "report",
        )
        assert set(artifacts) == set(ARTIFACT_NAMES)
        scenarios = {
            key: SupplyChainSimulator(200, 42, key).run()
            for key in SCENARIO_CATALOG
        }
        comparison = compare_scenarios(scenarios)
        sensitivity = run_standard_sensitivity(100, 42)
        result = {
            "status": "pass",
            "deterministic_csv_sha256": sha256(first),
            "rows": 500,
            "scenario_count": len(comparison),
            "sensitivity_parameters": len(sensitivity),
            "report_artifacts": sorted(artifacts),
            "human_review_required": True,
            "autonomous_action_authorized": False,
        }
        print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
