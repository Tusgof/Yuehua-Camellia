from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

import backtest_camellia_multilayer_taa as bt


ROOT = Path(__file__).resolve().parents[1]
DEVELOPMENT_OUTPUT = ROOT / "reports" / "generated" / "camellia_v2_development.json"
EVALUATION_OUTPUT = ROOT / "reports" / "generated" / "camellia_v2_evaluation.json"
EXPECTED_DATA_HASH = "9ca48d680c4c5da36c3e061c02a990840a478150ca68407b1f6a9d22998b61d1"

EXPERIMENTS = {
    "baseline_v1": {},
    "q1_breadth_b3": {"breadth_level": 3},
    "q2_trend_gate_disabled": {"trend_gate": False},
    "q3_us_top_two": {"us_top_count": 2},
    "q4_defensive_shy_only": {"defensive_policy": "shy_only"},
    "q5_rebalance_threshold_5pct": {"rebalance_threshold": 0.05},
}


def load_context() -> dict[str, object]:
    daily, digest = bt.load_prices(cache_only=True)
    if digest != EXPECTED_DATA_HASH:
        raise RuntimeError(f"data snapshot changed: {digest}")
    now = pd.Timestamp("2026-09-18")
    monthly = bt.completed_monthly_prices(daily, now)
    returns = monthly.pct_change(fill_method=None)
    baseline_targets, _ = bt.build_targets(monthly, 10)
    baseline_dates = returns.index[returns.index.get_loc(baseline_targets.index[0]) + 1 :]
    baseline_dates = baseline_dates[: len(baseline_targets)]
    fixed_6040 = pd.DataFrame(
        [
            {
                ticker: 0.60 if ticker == "SPY" else 0.40 if ticker == "IEF" else 0.0
                for ticker in bt.TICKERS
            }
        ]
        * len(baseline_targets),
        index=baseline_targets.index,
    )
    sixty_forty = bt.simulate(fixed_6040, returns, 0.001)
    spy = bt.simulate_buy_and_hold({"SPY": 1.0}, returns, baseline_dates, 0.001)
    return {
        "monthly": monthly,
        "returns": returns,
        "shy": returns["SHY"],
        "sixty_forty": sixty_forty,
        "spy": spy,
    }


def run_configuration(
    context: dict[str, object], parameters: dict[str, object], high_cost: bool = False
) -> tuple[pd.DataFrame, pd.DataFrame]:
    target_keys = {
        "breadth_level",
        "trend_gate",
        "us_top_count",
        "defensive_policy",
    }
    target_parameters = {
        key: value for key, value in parameters.items() if key in target_keys
    }
    targets, meta = bt.build_targets(
        context["monthly"], 10, **target_parameters  # type: ignore[arg-type]
    )
    simulation = bt.simulate(
        targets,
        context["returns"],  # type: ignore[arg-type]
        0.002 if high_cost else 0.001,
        rebalance_threshold=float(parameters.get("rebalance_threshold", 0.0)),
    )
    return simulation, meta


def metrics_for_period(
    context: dict[str, object],
    simulation: pd.DataFrame,
    meta: pd.DataFrame,
    period: str,
) -> dict[str, object]:
    frame = bt.period_slice(simulation, period)
    metrics = bt.performance_metrics(
        frame,
        context["shy"],  # type: ignore[arg-type]
        context["spy"]["net_return"],  # type: ignore[index]
        context["sixty_forty"]["net_return"],  # type: ignore[index]
    )
    aligned_meta = meta.reindex(frame["signal_date"])
    metrics["average_canary_cf"] = float(aligned_meta["canary_cf"].mean())
    metrics["average_total_defensive"] = float(
        aligned_meta["total_defensive"].mean()
    )
    metrics["rebalance_skipped_months"] = int(frame["rebalance_skipped"].sum())
    return metrics


def development_stage() -> dict[str, object]:
    context = load_context()
    results: dict[str, dict[str, object]] = {}
    for name, parameters in EXPERIMENTS.items():
        simulation, meta = run_configuration(context, parameters)
        results[name] = metrics_for_period(context, simulation, meta, "development")

    baseline = results["baseline_v1"]
    accepted = []
    for name in list(EXPERIMENTS)[1:]:
        result = results[name]
        if (
            result["sharpe"] > baseline["sharpe"]
            and result["cagr"] > 0
            and result["maximum_drawdown"] >= -0.20
        ):
            accepted.append(name)

    combined: dict[str, object] = {}
    for name in accepted:
        combined.update(EXPERIMENTS[name])
    if combined:
        simulation, meta = run_configuration(context, combined)
        combined_metrics = metrics_for_period(context, simulation, meta, "development")
    else:
        combined_metrics = {}

    combined_passes = bool(combined) and (
        combined_metrics["sharpe"] > baseline["sharpe"]
        and combined_metrics["cagr"] > 0
        and combined_metrics["maximum_drawdown"] >= -0.20
    )
    if combined_passes:
        selected = combined
        selection = "combined_accepted_experiments"
    elif accepted:
        best = max(accepted, key=lambda name: results[name]["sharpe"])
        selected = EXPERIMENTS[best]
        selection = f"best_single:{best}"
    else:
        turnover_candidates = [
            name
            for name in list(EXPERIMENTS)[1:]
            if results[name]["annual_two_sided_turnover"]
            < baseline["annual_two_sided_turnover"]
            and results[name]["cagr"] >= baseline["cagr"]
            and results[name]["maximum_drawdown"] >= -0.20
        ]
        if not turnover_candidates:
            selected = {}
            selection = "no_viable_v2_change"
        else:
            best = min(
                turnover_candidates,
                key=lambda name: results[name]["annual_two_sided_turnover"],
            )
            selected = EXPERIMENTS[best]
            selection = f"lowest_turnover_fallback:{best}"

    return {
        "stage": "development_only",
        "plan_commit": "fc1fda7b2dfb5cb662a4bdf62a1da8376cbd75e1",
        "data_sha256": EXPECTED_DATA_HASH,
        "experiments": EXPERIMENTS,
        "development_results": results,
        "accepted_experiments": accepted,
        "combined_parameters": combined,
        "combined_development_metrics": combined_metrics,
        "combined_passes": combined_passes,
        "selected_parameters": selected,
        "selection_rule_result": selection,
    }


def evaluation_stage(config_path: Path) -> dict[str, object]:
    frozen = json.loads(config_path.read_text(encoding="utf-8"))
    context = load_context()
    configurations = dict(EXPERIMENTS)
    configurations["baseline_v2"] = frozen["selected_parameters"]
    results: dict[str, dict[str, dict[str, object]]] = {}
    for name, parameters in configurations.items():
        simulation, meta = run_configuration(context, parameters)
        high_cost, high_meta = run_configuration(context, parameters, high_cost=True)
        results[name] = {}
        for period in ("development", "test", "full"):
            metrics = metrics_for_period(context, simulation, meta, period)
            high_metrics = metrics_for_period(context, high_cost, high_meta, period)
            metrics["high_cost_cagr"] = high_metrics["cagr"]
            metrics["high_cost_maximum_drawdown"] = high_metrics["maximum_drawdown"]
            results[name][period] = metrics

    for period in ("development", "test", "full"):
        bt.add_deflated_sharpe(results, period)
    return {
        "stage": "frozen_v2_evaluation",
        "data_sha256": EXPECTED_DATA_HASH,
        "frozen_config": frozen,
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("development", "evaluate"), required=True)
    parser.add_argument("--config", type=Path)
    args = parser.parse_args()
    if args.stage == "development":
        payload = development_stage()
        output = DEVELOPMENT_OUTPUT
    else:
        if args.config is None:
            parser.error("--config is required for evaluate")
        payload = evaluation_stage(args.config)
        output = EVALUATION_OUTPUT
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False),
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
