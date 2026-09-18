from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_project", ROOT / "scripts" / "validate_project.py"
)
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class ProjectValidationTests(unittest.TestCase):
    def test_repository_contract_passes(self) -> None:
        self.assertEqual(VALIDATOR.validate(), [])

    def test_live_trading_cannot_be_enabled_silently(self) -> None:
        real_load_json = VALIDATOR.load_json

        def fake_load_json(relative_path: str) -> dict:
            payload = real_load_json(relative_path)
            if relative_path == "config/project.json":
                payload["live_trading_enabled"] = True
            return payload

        with patch.object(VALIDATOR, "load_json", side_effect=fake_load_json):
            self.assertIn(
                "unsafe_project_guard:live_trading_enabled", VALIDATOR.validate()
            )

    def test_paper_trading_requires_evidence_and_owner_approval(self) -> None:
        real_load_json = VALIDATOR.load_json

        def fake_load_json(relative_path: str) -> dict:
            if relative_path == "experiments/strategy_registry.json":
                return {
                    "schema_version": 1,
                    "allowed_statuses": sorted(VALIDATOR.VALID_STATUSES),
                    "strategies": [
                        {
                            "id": "example",
                            "status": "paper_trading",
                            "source": {
                                "creator": "Example",
                                "url": "https://example.com",
                                "accessed_on": "2026-09-18",
                            },
                            "spec_path": "strategies/STRATEGY_TEMPLATE.md",
                        }
                    ],
                }
            return real_load_json(relative_path)

        with patch.object(VALIDATOR, "load_json", side_effect=fake_load_json):
            errors = VALIDATOR.validate()

        self.assertIn("strategy[0]:paper_status_without_backtest_report", errors)
        self.assertIn("strategy[0]:paper_trading_without_plan", errors)
        self.assertIn("strategy[0]:paper_trading_without_owner_approval", errors)


if __name__ == "__main__":
    unittest.main()
