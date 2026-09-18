from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "README.md",
    "PROJECT_BRAIN.md",
    "IMPLEMENT_PLAN.md",
    "AGENTS.md",
    "RESEARCH_LOG_FORMAT.md",
    "config/project.json",
    "experiments/strategy_registry.json",
    "strategies/STRATEGY_TEMPLATE.md",
    "reports/BACKTEST_REPORT_TEMPLATE.md",
    "paper_trading/PAPER_PLAN_TEMPLATE.md",
    "paper_trading/ledger.csv",
)

VALID_STATUSES = {
    "idea",
    "specified",
    "backtested",
    "reject",
    "revise",
    "paper_ready",
    "paper_trading",
    "retired",
}


def load_json(relative_path: str) -> dict:
    with (ROOT / relative_path).open(encoding="utf-8") as handle:
        return json.load(handle)


def validate() -> list[str]:
    errors: list[str] = []

    for relative_path in REQUIRED_FILES:
        if not (ROOT / relative_path).is_file():
            errors.append(f"missing_required_file:{relative_path}")

    project = load_json("config/project.json")
    if project.get("project") != "Camellia":
        errors.append("project_name_must_be_camellia")
    for guard in (
        "live_trading_enabled",
        "broker_connection_enabled",
        "credentials_in_repository_allowed",
    ):
        if project.get(guard) is not False:
            errors.append(f"unsafe_project_guard:{guard}")
    if project.get("paper_trade_requires_owner_approval") is not True:
        errors.append("paper_trade_owner_approval_guard_missing")
    if project.get("max_adjusted_variants_per_idea") != 2:
        errors.append("variant_limit_must_equal_two")

    registry = load_json("experiments/strategy_registry.json")
    if registry.get("schema_version") != 1:
        errors.append("registry_schema_version_must_equal_one")
    if set(registry.get("allowed_statuses", [])) != VALID_STATUSES:
        errors.append("registry_statuses_do_not_match_contract")

    seen_ids: set[str] = set()
    for index, strategy in enumerate(registry.get("strategies", [])):
        prefix = f"strategy[{index}]"
        strategy_id = strategy.get("id")
        if not isinstance(strategy_id, str) or not strategy_id.strip():
            errors.append(f"{prefix}:missing_id")
        elif strategy_id in seen_ids:
            errors.append(f"{prefix}:duplicate_id:{strategy_id}")
        else:
            seen_ids.add(strategy_id)

        if strategy.get("status") not in VALID_STATUSES:
            errors.append(f"{prefix}:invalid_status")

        source = strategy.get("source")
        if not isinstance(source, dict):
            errors.append(f"{prefix}:missing_source")
        else:
            for field in ("creator", "url", "accessed_on"):
                if not source.get(field):
                    errors.append(f"{prefix}:missing_source_{field}")

        spec_path = strategy.get("spec_path")
        if strategy.get("status") != "idea":
            if not isinstance(spec_path, str) or not (ROOT / spec_path).is_file():
                errors.append(f"{prefix}:missing_strategy_spec")

        if strategy.get("status") in {"paper_ready", "paper_trading"}:
            report_path = strategy.get("backtest_report")
            if not isinstance(report_path, str) or not (ROOT / report_path).is_file():
                errors.append(f"{prefix}:paper_status_without_backtest_report")

        if strategy.get("status") == "paper_trading":
            plan_path = strategy.get("paper_plan")
            if not isinstance(plan_path, str) or not (ROOT / plan_path).is_file():
                errors.append(f"{prefix}:paper_trading_without_plan")
            if strategy.get("owner_approved") is not True:
                errors.append(f"{prefix}:paper_trading_without_owner_approval")

    return errors


def main() -> int:
    errors = validate()
    if errors:
        for error in errors:
            print(f"ERROR {error}")
        return 1
    print("Camellia project validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
