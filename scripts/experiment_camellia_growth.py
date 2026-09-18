from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from statistics import NormalDist

import numpy as np
import pandas as pd

import backtest_camellia_multilayer_taa as bt
import experiment_camellia_round7 as r7
import experiment_camellia_v4 as v4
import experiment_camellia_v5 as v5


ROOT = Path(__file__).resolve().parents[1]
RESEARCH_OUTPUT = ROOT / "reports" / "generated" / "camellia_growth_research.json"
EVALUATION_OUTPUT = ROOT / "reports" / "generated" / "camellia_growth_evaluation.json"
PLAN_COMMIT = "a1110d6"
CUMULATIVE_TRIALS = 32
SECTORS = ("XLB", "XLE", "XLF", "XLI", "XLK", "XLP", "XLU", "XLV", "XLY")
UNIVERSE = tuple(dict.fromkeys(r7.UNIVERSE + ("_FINANCING",)))
BLOCKS = r7.BLOCKS
EXPERIMENTS = {
    "baseline_v6": {},
    "q29_partial_canary_cuts": {"partial_canary_cuts": True},
    "q30_aggressive_risk_on": {"aggressive_risk_on": True},
    "q31_sector_satellite": {"sector_satellite": True},
    "q32_conditional_overlay": {"conditional_overlay": True},
}


def _positive_ranked(
    scores: pd.DataFrame, date: pd.Timestamp, universe: tuple[str, ...], count: int
) -> list[str]:
    available = [
        ticker
        for ticker in universe
        if pd.notna(scores.at[date, ticker]) and scores.at[date, ticker] > 0
    ]
    return sorted(
        available,
        key=lambda ticker: (-scores.at[date, ticker], universe.index(ticker)),
    )[:count]


def build_targets(
    prices: pd.DataFrame,
    *,
    partial_canary_cuts: bool = False,
    aggressive_risk_on: bool = False,
    sector_satellite: bool = False,
    conditional_overlay: bool = False,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if sum((partial_canary_cuts, aggressive_risk_on, sector_satellite, conditional_overlay)) > 1:
        raise ValueError("Growth candidates must be tested in isolation")

    weighted = bt.momentum(prices, weighted=True)
    blended = v4.multi_lookback_score(prices)
    required = pd.concat(
        [
            prices.loc[:, list(bt.TICKERS) + ["GLD", "VTI"]],
            weighted.loc[:, list(bt.TICKERS) + ["GLD", "VTI"]],
        ],
        axis=1,
    )
    eligible = required.notna().all(axis=1) & (prices.index >= "2008-01-01")
    signal_dates = prices.index[eligible]
    signal_dates = signal_dates[signal_dates < prices.index[-1]]
    if signal_dates.empty:
        raise RuntimeError("no eligible signal dates")

    strategic = {
        "VTI": 0.60 if aggressive_risk_on else 0.40,
        "regional": 0.20,
        "DBC": 0.10,
        "VNQ": 0.10,
        "IEF": 0.00 if aggressive_risk_on else 0.10,
        "TLT": 0.00 if aggressive_risk_on else 0.10,
    }
    rows: list[pd.Series] = []
    meta_rows: list[dict[str, object]] = []

    for date in signal_dates:
        weak = {ticker: bool(weighted.at[date, ticker] <= 0) for ticker in bt.CANARIES}
        rate_warning = weak["BND"] or weak["TIP"]
        combined_warning = weak["VWO"] and rate_warning
        if combined_warning:
            regime = "combined_full_defense"
        elif weak["VWO"]:
            regime = "vwo_warning"
        elif rate_warning:
            regime = "rate_warning"
        else:
            regime = "no_warning"

        if combined_warning:
            equity_multiplier = rate_multiplier = diversifier_multiplier = 0.0
        elif partial_canary_cuts and weak["VWO"]:
            equity_multiplier, rate_multiplier, diversifier_multiplier = 0.5, 1.0, 1.0
        elif partial_canary_cuts and rate_warning:
            equity_multiplier, rate_multiplier, diversifier_multiplier = 1.0, 0.5, 1.0
        elif weak["VWO"]:
            equity_multiplier, rate_multiplier, diversifier_multiplier = 0.0, 1.0, 1.0
        elif rate_warning:
            equity_multiplier, rate_multiplier, diversifier_multiplier = 1.0, 0.0, 1.0
        else:
            equity_multiplier = rate_multiplier = diversifier_multiplier = 1.0

        exposure_multiplier = 1.20 if conditional_overlay and regime == "no_warning" else 1.0
        target = pd.Series(0.0, index=UNIVERSE)
        regional_selected = _positive_ranked(weighted, date, v5.REGIONAL, 2)
        sector_selected: list[str] = []

        vti_weight = strategic["VTI"]
        if sector_satellite and regime == "no_warning":
            sector_selected = _positive_ranked(weighted, date, SECTORS, 1)
            if sector_selected:
                vti_weight -= 0.20
                target[sector_selected[0]] += 0.20

        target["VTI"] += vti_weight * equity_multiplier * exposure_multiplier
        for ticker in regional_selected:
            target[ticker] += 0.10 * equity_multiplier * exposure_multiplier
        if sector_selected:
            target[sector_selected[0]] *= equity_multiplier * exposure_multiplier
        target["DBC"] += strategic["DBC"] * diversifier_multiplier * exposure_multiplier
        for ticker in ("VNQ", "IEF", "TLT"):
            target[ticker] += strategic[ticker] * rate_multiplier * exposure_multiplier

        if conditional_overlay and regime == "no_warning":
            target["_FINANCING"] = -0.20

        defensive_budget = 1.0 - float(target.sum())
        if defensive_budget < -1e-12:
            raise AssertionError(f"negative defensive budget at {date}: {defensive_budget}")
        defensive_budget = max(0.0, defensive_budget)
        target["SHY"] += 0.50 * defensive_budget
        if blended.at[date, "IEF"] > 0:
            target["IEF"] += 0.25 * defensive_budget
            deflation = "IEF"
        else:
            target["SHY"] += 0.25 * defensive_budget
            deflation = "SHY"
        inflation = max(("GLD", "DBC"), key=lambda ticker: blended.at[date, ticker])
        if blended.at[date, inflation] > 0:
            target[inflation] += 0.25 * defensive_budget
        else:
            target["SHY"] += 0.25 * defensive_budget
            inflation = "SHY"

        if not np.isclose(float(target.sum()), 1.0, atol=1e-12):
            raise AssertionError(f"target weights do not sum to one at {date}")
        rows.append(target.rename(date))
        meta_rows.append(
            {
                "signal_date": date,
                "weak_canaries": sum(weak.values()),
                "canary_regime": regime,
                "canary_cf": defensive_budget,
                "total_defensive": defensive_budget,
                "us_winners": "VTI",
                "regional_winners": ",".join(regional_selected),
                "sector_winner": ",".join(sector_selected),
                "gross_exposure": float(target[target > 0].sum()),
                "financing_weight": float(target["_FINANCING"]),
                "defensive_winner": f"SHY+{deflation}+{inflation}",
            }
        )
    return pd.DataFrame(rows), pd.DataFrame(meta_rows).set_index("signal_date")


def load_context() -> dict[str, object]:
    return r7.load_context()


def run_configuration(
    context: dict[str, object], config: dict[str, object], high_cost: bool = False
) -> tuple[pd.DataFrame, pd.DataFrame]:
    targets, meta = build_targets(context["monthly"], **config)  # type: ignore[arg-type]
    returns = context["returns"].copy()  # type: ignore[union-attr]
    annual_spread = 0.04 if high_cost else 0.02
    returns["_FINANCING"] = context["shy"].clip(lower=0.0) + annual_spread / 12  # type: ignore[union-attr]
    simulation = bt.simulate(
        targets,
        returns,
        0.002 if high_cost else 0.001,
        rebalance_threshold=0.05,
    )
    return simulation, meta


def summarize_config(
    context: dict[str, object],
    config: dict[str, object],
    target_volatilities: dict[str, float],
) -> tuple[dict[str, dict[str, object]], dict[str, object]]:
    simulation, meta = run_configuration(context, config)
    high_cost, high_meta = run_configuration(context, config, high_cost=True)
    blocks = {}
    for name, (start, end) in BLOCKS.items():
        if name == "recent_diagnostic":
            continue
        item = v4.period_metrics(context, simulation, meta, start, end)
        high = v4.period_metrics(context, high_cost, high_meta, start, end)
        item["high_cost_cagr"] = high["cagr"]
        item["high_cost_maximum_drawdown"] = high["maximum_drawdown"]
        item["risk_matched_cagr"] = r7._risk_matched_cagr(
            simulation.loc[start:end], context["shy"], target_volatilities[name]  # type: ignore[arg-type]
        )
        blocks[name] = item
    return blocks, r7._summarize(blocks)


def assess(summary: dict[str, object], baseline: dict[str, object]) -> dict[str, object]:
    guardrails = {
        "all_cagr_positive": bool(summary["all_cagr_positive"]),
        "all_high_cost_cagr_positive": bool(summary["all_high_cost_cagr_positive"]),
        "worst_drawdown_within_25pct": summary["worst_maximum_drawdown"] >= -0.25,
        "median_cagr_higher_by_100bp": summary["median_cagr"] >= baseline["median_cagr"] + 0.01,
        "median_sharpe_not_lower_by_more_than_010": summary["median_sharpe"] >= baseline["median_sharpe"] - 0.10,
        "risk_matched_cagr_not_lower_by_more_than_25bp": summary["median_risk_matched_cagr"] >= baseline["median_risk_matched_cagr"] - 0.0025,
        "upside_beta_above_v6": summary["median_upside_beta_spy"] > baseline["median_upside_beta_spy"],
        "downside_beta_not_higher_by_more_than_015": summary["median_downside_beta_spy"] <= baseline["median_downside_beta_spy"] + 0.15,
        "turnover_within_125pct": summary["median_turnover"] <= baseline["median_turnover"] * 1.25,
        "cost_drag_not_higher_by_more_than_35bp": summary["median_gross_net_cagr_spread"] <= baseline["median_gross_net_cagr_spread"] + 0.0035,
    }
    return {"guardrails": guardrails, "passes": all(guardrails.values())}


def add_cumulative_dsr(
    results: dict[str, dict[str, dict[str, object]]], period: str
) -> None:
    sharpes = [float(periods[period]["sharpe"]) for periods in results.values()]
    benchmark = r7._expected_max_sharpe_benchmark(sharpes, CUMULATIVE_TRIALS)
    for periods in results.values():
        item = periods[period]
        monthly_sharpe = float(item["sharpe"]) / math.sqrt(12)
        variance_term = max(
            1e-12,
            1
            - float(item["skewness"]) * monthly_sharpe
            + ((float(item["excess_kurtosis"]) + 2) / 4) * monthly_sharpe**2,
        )
        z_score = (
            (monthly_sharpe - benchmark)
            * math.sqrt(int(item["months"]) - 1)
            / math.sqrt(variance_term)
        )
        item["dsr_cumulative_32_trials"] = float(NormalDist().cdf(z_score))
        item["dsr_expected_max_monthly_sharpe"] = benchmark


def research_stage() -> dict[str, object]:
    context = load_context()
    baseline_simulation, _ = run_configuration(context, {})
    target_volatilities = {
        name: float(baseline_simulation.loc[start:end, "net_return"].std(ddof=1) * math.sqrt(12))
        for name, (start, end) in BLOCKS.items()
        if name != "recent_diagnostic"
    }
    block_results = {}
    summaries = {}
    for name, config in EXPERIMENTS.items():
        block_results[name], summaries[name] = summarize_config(
            context, config, target_volatilities
        )
    baseline = summaries["baseline_v6"]
    assessments = {
        name: assess(summaries[name], baseline) for name in list(EXPERIMENTS)[1:]
    }
    accepted = [name for name, item in assessments.items() if item["passes"]]
    selected = min(
        accepted,
        key=lambda name: (-float(summaries[name]["median_cagr"]), -float(summaries[name]["median_sharpe"])),
        default=None,
    )
    return {
        "stage": "research_blocks_only",
        "plan_commit": PLAN_COMMIT,
        "data_sha256": context["digest"],
        "data_audit": context["audit"],
        "cumulative_trials": CUMULATIVE_TRIALS,
        "experiments": EXPERIMENTS,
        "block_results": block_results,
        "summaries": summaries,
        "assessments": assessments,
        "accepted_experiments": accepted,
        "selected_config": dict(EXPERIMENTS[selected]) if selected else {},
        "selected_experiment": selected,
        "selection_rule_result": f"accepted_highest_cagr:{selected}" if selected else "no_candidate_passed_keep_v6",
    }


def evaluation_stage(config_path: Path) -> dict[str, object]:
    frozen = json.loads(config_path.read_text(encoding="utf-8"))
    context = load_context()
    if context["digest"] != frozen["data_sha256"]:
        raise RuntimeError("data snapshot changed after freeze")
    baseline_simulation, _ = run_configuration(context, {})
    configurations = dict(EXPERIMENTS)
    configurations["frozen_v7"] = frozen["selected_config"]
    periods = {
        "recent_diagnostic": BLOCKS["recent_diagnostic"],
        "full": ("2008-08-01", "2026-08-31"),
    }
    target_volatilities = {
        name: float(baseline_simulation.loc[start:end, "net_return"].std(ddof=1) * math.sqrt(12))
        for name, (start, end) in periods.items()
    }
    results: dict[str, dict[str, dict[str, object]]] = {}
    for name, config in configurations.items():
        simulation, meta = run_configuration(context, config)
        high_cost, high_meta = run_configuration(context, config, high_cost=True)
        results[name] = {}
        for period, (start, end) in periods.items():
            item = v4.period_metrics(context, simulation, meta, start, end)
            high = v4.period_metrics(context, high_cost, high_meta, start, end)
            item["high_cost_cagr"] = high["cagr"]
            item["high_cost_maximum_drawdown"] = high["maximum_drawdown"]
            item["risk_matched_cagr"] = r7._risk_matched_cagr(
                simulation.loc[start:end], context["shy"], target_volatilities[period]  # type: ignore[arg-type]
            )
            results[name][period] = item
    for period in periods:
        add_cumulative_dsr(results, period)

    recent = results["frozen_v7"]["recent_diagnostic"]
    full = results["frozen_v7"]["full"]
    baseline_full = results["baseline_v6"]["full"]
    safety = {
        "recent_net_cagr_positive": recent["cagr"] > 0,
        "recent_high_cost_cagr_positive": recent["high_cost_cagr"] > 0,
        "recent_maximum_drawdown_within_25pct": recent["maximum_drawdown"] >= -0.25,
        "full_maximum_drawdown_within_25pct": full["maximum_drawdown"] >= -0.25,
    }
    readiness = {
        "full_cagr_higher_than_v6_by_75bp": full["cagr"] >= baseline_full["cagr"] + 0.0075,
        "full_sharpe_not_lower_than_v6_by_010": full["sharpe"] >= baseline_full["sharpe"] - 0.10,
        "full_high_cost_cagr_positive": full["high_cost_cagr"] > 0,
        "full_turnover_within_125pct_of_v6": full["annual_two_sided_turnover"] <= baseline_full["annual_two_sided_turnover"] * 1.25,
    }
    selected = frozen.get("selected_experiment")
    broker_ready = selected in {"q29_partial_canary_cuts", "q30_aggressive_risk_on"}
    if not frozen["selected_config"]:
        decision = "reject"
    elif all(safety.values()) and all(readiness.values()):
        decision = "paper_ready" if broker_ready else "revise"
    else:
        decision = "revise"
    return {
        "stage": "frozen_strategy_v7_evaluation",
        "frozen_config": frozen,
        "results": results,
        "recent_safety_checks": safety,
        "paper_ready_checks": readiness,
        "broker_ready_without_new_validation": broker_ready,
        "decision": decision,
    }


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
    output.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False),
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
