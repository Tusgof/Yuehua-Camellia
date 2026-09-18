from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

import backtest_camellia_multilayer_taa as bt
import experiment_camellia_v2 as v2


ROOT = Path(__file__).resolve().parents[1]
RESEARCH_OUTPUT = ROOT / "reports" / "generated" / "camellia_v3_research.json"
EVALUATION_OUTPUT = ROOT / "reports" / "generated" / "camellia_v3_evaluation.json"
PLAN_COMMIT = "b1d63f9e3c32931d455258d472f2fb98549da038"

V2 = {"trend_gate": False, "us_top_count": 2, "rebalance_threshold": 0.05}
EXPERIMENTS = {
    "baseline_v2": {},
    "q6_soft_canary": {"breadth_level": 3, "max_canary_cf": 2 / 3},
    "q7_partial_trend": {"trend_gate": True, "trend_retention": 0.5},
    "q8_cross_asset_top4": {"risky_top_count": 4},
    "q9_blended_defense": {"defensive_shy_fraction": 0.5},
    "q10_volatility_target": {
        "volatility_target": 0.15,
        "volatility_lookback": 12,
        "leverage_cap": 2.0,
    },
}
BLOCKS = {
    "block_1": ("2008-08-01", "2012-12-31"),
    "block_2": ("2013-01-01", "2018-12-31"),
    "block_3": ("2019-01-01", "2022-12-31"),
    "recent_holdout": ("2023-01-01", "2026-08-31"),
}


def apply_volatility_target(
    simulation: pd.DataFrame,
    shy_returns: pd.Series,
    target: float,
    lookback: int,
    cap: float,
) -> pd.DataFrame:
    result = simulation.copy()
    realized = result["net_return"].rolling(lookback).std(ddof=1) * math.sqrt(12)
    leverage = (target / realized.shift(1)).clip(lower=0.0, upper=cap).fillna(1.0)
    risk_free = shy_returns.reindex(result.index)
    result["gross_return"] = risk_free + leverage * (
        result["gross_return"] - risk_free
    )
    result["net_return"] = risk_free + leverage * (result["net_return"] - risk_free)
    result["cost"] = result["cost"] * leverage
    result["one_way_turnover"] = result["one_way_turnover"] * leverage
    result["two_sided_turnover"] = result["two_sided_turnover"] * leverage
    result["leverage"] = leverage
    return result


def run(context: dict[str, object], changes: dict[str, object], high_cost: bool = False):
    parameters = dict(V2)
    parameters.update(changes)
    vol_target = parameters.pop("volatility_target", None)
    vol_lookback = int(parameters.pop("volatility_lookback", 12))
    leverage_cap = float(parameters.pop("leverage_cap", 1.0))
    simulation, meta = v2.run_configuration(context, parameters, high_cost=high_cost)
    if vol_target is not None:
        simulation = apply_volatility_target(
            simulation,
            context["shy"],  # type: ignore[arg-type]
            float(vol_target),
            vol_lookback,
            leverage_cap,
        )
    else:
        simulation["leverage"] = 1.0
    return simulation, meta


def metrics(context, simulation, meta, start: str, end: str):
    frame = simulation.loc[start:end]
    result = bt.performance_metrics(
        frame,
        context["shy"],
        context["spy"]["net_return"],
        context["sixty_forty"]["net_return"],
    )
    aligned = meta.reindex(frame["signal_date"])
    result["average_canary_cf"] = float(aligned["canary_cf"].mean())
    result["average_total_defensive"] = float(aligned["total_defensive"].mean())
    result["average_leverage"] = float(frame["leverage"].mean())
    result["maximum_leverage"] = float(frame["leverage"].max())
    return result


def summarize_blocks(context, changes):
    simulation, meta = run(context, changes)
    results = {
        name: metrics(context, simulation, meta, start, end)
        for name, (start, end) in BLOCKS.items()
        if name != "recent_holdout"
    }
    cagrs = [item["cagr"] for item in results.values()]
    sharpes = [item["sharpe"] for item in results.values()]
    return results, {
        "median_cagr": float(np.median(cagrs)),
        "median_sharpe": float(np.median(sharpes)),
        "all_cagr_positive": all(value > 0 for value in cagrs),
        "worst_maximum_drawdown": min(
            item["maximum_drawdown"] for item in results.values()
        ),
    }


def research_stage():
    context = v2.load_context()
    block_results = {}
    summaries = {}
    for name, changes in EXPERIMENTS.items():
        block_results[name], summaries[name] = summarize_blocks(context, changes)
    baseline = summaries["baseline_v2"]
    accepted = []
    for name in list(EXPERIMENTS)[1:]:
        summary = summaries[name]
        common = summary["all_cagr_positive"] and summary["worst_maximum_drawdown"] >= -0.30
        if name == "q10_volatility_target":
            passes = (
                common
                and summary["median_cagr"] > baseline["median_cagr"]
                and summary["median_sharpe"] >= baseline["median_sharpe"] - 0.05
            )
        else:
            passes = (
                common
                and summary["median_cagr"] > baseline["median_cagr"]
                and summary["median_sharpe"] > baseline["median_sharpe"]
            )
        if passes:
            accepted.append(name)
    combined = {}
    for name in accepted:
        combined.update(EXPERIMENTS[name])
    combined_blocks, combined_summary = summarize_blocks(context, combined)
    combined_passes = (
        combined_summary["all_cagr_positive"]
        and combined_summary["worst_maximum_drawdown"] >= -0.30
        and combined_summary["median_cagr"] > baseline["median_cagr"]
        and combined_summary["median_sharpe"] > baseline["median_sharpe"]
    )
    if combined and combined_passes:
        selected = combined
        selection = "combined_accepted_experiments"
    else:
        candidates = accepted or list(EXPERIMENTS)[1:]
        best = max(
            candidates,
            key=lambda name: min(summaries[name]["median_cagr"] / 0.15, 1)
            + min(summaries[name]["median_sharpe"], 1),
        )
        selected = EXPERIMENTS[best]
        selection = f"best_single:{best}"
    return {
        "stage": "research_blocks_only",
        "plan_commit": PLAN_COMMIT,
        "experiments": EXPERIMENTS,
        "block_results": block_results,
        "summaries": summaries,
        "accepted_experiments": accepted,
        "combined_parameters": combined,
        "combined_block_results": combined_blocks,
        "combined_summary": combined_summary,
        "combined_passes": combined_passes,
        "selected_parameters": selected,
        "selection_rule_result": selection,
    }


def evaluation_stage(config_path: Path):
    frozen = json.loads(config_path.read_text(encoding="utf-8"))
    context = v2.load_context()
    configurations = dict(EXPERIMENTS)
    configurations["baseline_v3"] = frozen["selected_parameters"]
    results = {}
    for name, changes in configurations.items():
        simulation, meta = run(context, changes)
        high_cost, high_meta = run(context, changes, high_cost=True)
        results[name] = {}
        for period, (start, end) in {
            "recent_holdout": BLOCKS["recent_holdout"],
            "full": ("2008-08-01", "2026-08-31"),
        }.items():
            item = metrics(context, simulation, meta, start, end)
            high = metrics(context, high_cost, high_meta, start, end)
            item["high_cost_cagr"] = high["cagr"]
            item["high_cost_maximum_drawdown"] = high["maximum_drawdown"]
            results[name][period] = item
    for period in ("recent_holdout", "full"):
        bt.add_deflated_sharpe(results, period)
    return {"stage": "frozen_v3_evaluation", "frozen_config": frozen, "results": results}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("research", "evaluate"), required=True)
    parser.add_argument("--config", type=Path)
    args = parser.parse_args()
    if args.stage == "research":
        payload = research_stage()
        output = RESEARCH_OUTPUT
    else:
        if args.config is None:
            parser.error("--config is required for evaluate")
        payload = evaluation_stage(args.config)
        output = EVALUATION_OUTPUT
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, allow_nan=False), encoding="utf-8")
    print(json.dumps(payload, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
