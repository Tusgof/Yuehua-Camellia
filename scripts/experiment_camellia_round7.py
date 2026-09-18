from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from statistics import NormalDist

import numpy as np
import pandas as pd

import backtest_camellia_multilayer_taa as bt
import experiment_camellia_v4 as v4
import experiment_camellia_v5 as v5
import experiment_camellia_v6 as previous_round


ROOT = Path(__file__).resolve().parents[1]
RESEARCH_OUTPUT = ROOT / "reports" / "generated" / "camellia_round7_research.json"
EVALUATION_OUTPUT = ROOT / "reports" / "generated" / "camellia_round7_evaluation.json"
PLAN_COMMIT = "0ec56ed"
CUMULATIVE_TRIALS = 28
UNIVERSE = previous_round.UNIVERSE
REGIONAL = v5.REGIONAL
BLOCKS = v5.BLOCKS
EXPERIMENTS = {
    "baseline_v5": {},
    "q26_selective_canary": {"selective_canary": True},
    "q27_structural_risk_budget": {"structural_risk_budget": True},
    "q28_slower_regional_ranking": {"slower_regional_ranking": True},
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
    selective_canary: bool = False,
    structural_risk_budget: bool = False,
    slower_regional_ranking: bool = False,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if sum((selective_canary, structural_risk_budget, slower_regional_ranking)) > 1:
        raise ValueError("round-7 candidates must be tested in isolation")

    weighted = bt.momentum(prices, weighted=True)
    unweighted = bt.momentum(prices, weighted=False)
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
        "VTI": 0.50 if structural_risk_budget else 0.40,
        "regional": 0.20,
        "DBC": 0.10,
        "VNQ": 0.10,
        "IEF": 0.05 if structural_risk_budget else 0.10,
        "TLT": 0.05 if structural_risk_budget else 0.10,
    }
    regional_scores = unweighted if slower_regional_ranking else weighted
    rows: list[pd.Series] = []
    meta_rows: list[dict[str, object]] = []

    for date in signal_dates:
        weak = {ticker: bool(weighted.at[date, ticker] <= 0) for ticker in bt.CANARIES}
        weak_count = sum(weak.values())
        target = pd.Series(0.0, index=UNIVERSE)
        regional_selected = _positive_ranked(regional_scores, date, REGIONAL, 2)

        if selective_canary:
            rate_warning = weak["BND"] or weak["TIP"]
            combined_warning = weak["VWO"] and rate_warning
            equity_open = not weak["VWO"] and not combined_warning
            rate_open = not rate_warning and not combined_warning
            diversifier_open = not combined_warning
            if combined_warning:
                regime = "combined_full_defense"
            elif weak["VWO"]:
                regime = "vwo_equity_cut"
            elif rate_warning:
                regime = "rate_sensitive_cut"
            else:
                regime = "no_warning"
            scale = 1.0
        else:
            scale = 1.0 - min(1.0, weak_count / 2)
            equity_open = rate_open = diversifier_open = True
            regime = f"breadth_cf_{1 - scale:.1f}"

        if equity_open:
            target["VTI"] += strategic["VTI"] * scale
            each_regional = strategic["regional"] / 2
            for ticker in regional_selected:
                target[ticker] += each_regional * scale
        if diversifier_open:
            target["DBC"] += strategic["DBC"] * scale
        if rate_open:
            for ticker in ("VNQ", "IEF", "TLT"):
                target[ticker] += strategic[ticker] * scale

        defensive_budget = 1.0 - float(target.sum())
        canary_defense = defensive_budget - (
            strategic["regional"] * scale
            if equity_open and len(regional_selected) == 0
            else strategic["regional"] * scale / 2
            if equity_open and len(regional_selected) == 1
            else 0.0
        )
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
                "weak_canaries": weak_count,
                "canary_cf": max(0.0, canary_defense),
                "canary_regime": regime,
                "total_defensive": defensive_budget,
                "us_winners": "VTI" if equity_open else "",
                "regional_winners": ",".join(regional_selected) if equity_open else "",
                "defensive_winner": f"SHY+{deflation}+{inflation}",
            }
        )
    return pd.DataFrame(rows), pd.DataFrame(meta_rows).set_index("signal_date")


def load_context() -> dict[str, object]:
    return previous_round.load_context(False)


def run_configuration(
    context: dict[str, object], config: dict[str, object], high_cost: bool = False
) -> tuple[pd.DataFrame, pd.DataFrame]:
    targets, meta = build_targets(context["monthly"], **config)  # type: ignore[arg-type]
    simulation = bt.simulate(
        targets,
        context["returns"],  # type: ignore[arg-type]
        0.002 if high_cost else 0.001,
        rebalance_threshold=0.05,
    )
    return simulation, meta


def _risk_matched_cagr(
    simulation: pd.DataFrame, shy: pd.Series, target_volatility: float
) -> float:
    returns = simulation["net_return"].dropna()
    volatility = float(returns.std(ddof=1) * math.sqrt(12))
    if volatility <= 0:
        raise ValueError("risk matching requires positive volatility")
    cash = shy.reindex(returns.index).fillna(0.0)
    scaled = cash + (returns - cash) * target_volatility / volatility
    growth = float((1 + scaled).prod())
    return float(growth ** (12 / len(scaled)) - 1)


def _summarize(blocks: dict[str, dict[str, object]]) -> dict[str, object]:
    def median(key: str) -> float:
        return float(np.median([float(item[key]) for item in blocks.values()]))

    return {
        "median_cagr": median("cagr"),
        "median_high_cost_cagr": median("high_cost_cagr"),
        "median_sharpe": median("sharpe"),
        "median_risk_matched_cagr": median("risk_matched_cagr"),
        "median_annualized_volatility": median("annualized_volatility"),
        "median_maximum_drawdown": median("maximum_drawdown"),
        "worst_maximum_drawdown": min(float(item["maximum_drawdown"]) for item in blocks.values()),
        "median_upside_beta_spy": float(np.median([float(item["vs_spy"]["upside_beta"]) for item in blocks.values()])),  # type: ignore[index]
        "median_downside_beta_spy": float(np.median([float(item["vs_spy"]["downside_beta"]) for item in blocks.values()])),  # type: ignore[index]
        "median_turnover": median("annual_two_sided_turnover"),
        "median_gross_net_cagr_spread": median("gross_net_cagr_spread"),
        "all_cagr_positive": all(float(item["cagr"]) > 0 for item in blocks.values()),
        "all_high_cost_cagr_positive": all(float(item["high_cost_cagr"]) > 0 for item in blocks.values()),
    }


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
        frame = simulation.loc[start:end]
        item = v4.period_metrics(context, simulation, meta, start, end)
        high = v4.period_metrics(context, high_cost, high_meta, start, end)
        item["high_cost_cagr"] = high["cagr"]
        item["high_cost_maximum_drawdown"] = high["maximum_drawdown"]
        item["risk_matched_cagr"] = _risk_matched_cagr(
            frame, context["shy"], target_volatilities[name]  # type: ignore[arg-type]
        )
        blocks[name] = item
    return blocks, _summarize(blocks)


def assess(summary: dict[str, object], baseline: dict[str, object]) -> dict[str, object]:
    guardrails = {
        "all_cagr_positive": bool(summary["all_cagr_positive"]),
        "all_high_cost_cagr_positive": bool(summary["all_high_cost_cagr_positive"]),
        "worst_drawdown_within_20pct": summary["worst_maximum_drawdown"] >= -0.20,
        "cagr_not_lower_by_more_than_25bp": summary["median_cagr"] >= baseline["median_cagr"] - 0.0025,
        "upside_beta_not_lower_by_more_than_003": summary["median_upside_beta_spy"] >= baseline["median_upside_beta_spy"] - 0.03,
        "turnover_within_115pct": summary["median_turnover"] <= baseline["median_turnover"] * 1.15,
        "cost_drag_not_higher_by_more_than_25bp": summary["median_gross_net_cagr_spread"] <= baseline["median_gross_net_cagr_spread"] + 0.0025,
    }
    efficiency = {
        "median_sharpe_above_v5": summary["median_sharpe"] > baseline["median_sharpe"],
        "median_risk_matched_cagr_above_v5": summary["median_risk_matched_cagr"] > baseline["median_risk_matched_cagr"],
    }
    return {
        "guardrails": guardrails,
        "efficiency_tests": efficiency,
        "passes": all(guardrails.values()) and all(efficiency.values()),
    }


def _expected_max_sharpe_benchmark(sharpes: list[float], trials: int) -> float:
    sigma = float(np.std(np.asarray(sharpes) / math.sqrt(12), ddof=1))
    euler_gamma = 0.5772156649015329
    return sigma * (
        (1 - euler_gamma) * NormalDist().inv_cdf(1 - 1 / trials)
        + euler_gamma * NormalDist().inv_cdf(1 - 1 / (trials * math.e))
    )


def add_cumulative_dsr(
    results: dict[str, dict[str, dict[str, object]]], period: str
) -> None:
    sharpes = [float(periods[period]["sharpe"]) for periods in results.values()]
    benchmark = _expected_max_sharpe_benchmark(sharpes, CUMULATIVE_TRIALS)
    for periods in results.values():
        item = periods[period]
        monthly_sharpe = float(item["sharpe"]) / math.sqrt(12)
        months = int(item["months"])
        variance_term = max(
            1e-12,
            1
            - float(item["skewness"]) * monthly_sharpe
            + ((float(item["excess_kurtosis"]) + 2) / 4) * monthly_sharpe**2,
        )
        z_score = (monthly_sharpe - benchmark) * math.sqrt(months - 1) / math.sqrt(variance_term)
        item["dsr_cumulative_28_trials"] = float(NormalDist().cdf(z_score))
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
    baseline = summaries["baseline_v5"]
    assessments = {
        name: assess(summaries[name], baseline) for name in list(EXPERIMENTS)[1:]
    }
    accepted = [name for name, item in assessments.items() if item["passes"]]
    selected = min(
        accepted,
        key=lambda name: (-float(summaries[name]["median_sharpe"]), float(summaries[name]["median_turnover"])),
        default=None,
    )
    selected_config = dict(EXPERIMENTS[selected]) if selected else {}
    selection = f"accepted_best_efficiency:{selected}" if selected else "no_candidate_passed_keep_v5"
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
        "selected_config": selected_config,
        "selection_rule_result": selection,
    }


def evaluation_stage(config_path: Path) -> dict[str, object]:
    frozen = json.loads(config_path.read_text(encoding="utf-8"))
    context = load_context()
    if context["digest"] != frozen["data_sha256"]:
        raise RuntimeError("data snapshot changed after freeze")
    baseline_simulation, _ = run_configuration(context, {})
    configurations = dict(EXPERIMENTS)
    configurations["frozen_v6"] = frozen["selected_config"]
    results: dict[str, dict[str, dict[str, object]]] = {}
    periods = {
        "recent_diagnostic": BLOCKS["recent_diagnostic"],
        "full": ("2008-08-01", "2026-08-31"),
    }
    target_volatilities = {
        name: float(baseline_simulation.loc[start:end, "net_return"].std(ddof=1) * math.sqrt(12))
        for name, (start, end) in periods.items()
    }
    for name, config in configurations.items():
        simulation, meta = run_configuration(context, config)
        high_cost, high_meta = run_configuration(context, config, high_cost=True)
        results[name] = {}
        for period, (start, end) in periods.items():
            item = v4.period_metrics(context, simulation, meta, start, end)
            high = v4.period_metrics(context, high_cost, high_meta, start, end)
            item["high_cost_cagr"] = high["cagr"]
            item["high_cost_maximum_drawdown"] = high["maximum_drawdown"]
            item["risk_matched_cagr"] = _risk_matched_cagr(
                simulation.loc[start:end], context["shy"], target_volatilities[period]  # type: ignore[arg-type]
            )
            results[name][period] = item
    for period in periods:
        add_cumulative_dsr(results, period)

    recent = results["frozen_v6"]["recent_diagnostic"]
    full = results["frozen_v6"]["full"]
    baseline_full = results["baseline_v5"]["full"]
    safety = {
        "recent_net_cagr_positive": recent["cagr"] > 0,
        "recent_high_cost_cagr_positive": recent["high_cost_cagr"] > 0,
        "recent_maximum_drawdown_within_20pct": recent["maximum_drawdown"] >= -0.20,
        "recent_downside_beta_spy_below_one": recent["vs_spy"]["downside_beta"] < 1,
    }
    readiness = {
        "full_cagr_not_lower_than_v5_by_25bp": full["cagr"] >= baseline_full["cagr"] - 0.0025,
        "full_sharpe_above_v5": full["sharpe"] > baseline_full["sharpe"],
        "full_risk_matched_cagr_above_v5": full["risk_matched_cagr"] > baseline_full["risk_matched_cagr"],
        "full_high_cost_cagr_positive": full["high_cost_cagr"] > 0,
        "full_turnover_within_115pct_of_v5": full["annual_two_sided_turnover"] <= baseline_full["annual_two_sided_turnover"] * 1.15,
    }
    decision = (
        "paper_ready"
        if frozen["selected_config"] and all(safety.values()) and all(readiness.values())
        else "reject"
        if not frozen["selected_config"]
        else "revise"
    )
    return {
        "stage": "frozen_strategy_v6_evaluation",
        "frozen_config": frozen,
        "results": results,
        "recent_safety_checks": safety,
        "paper_ready_checks": readiness,
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
