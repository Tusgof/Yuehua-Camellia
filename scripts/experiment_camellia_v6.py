from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

import backtest_camellia_multilayer_taa as bt
import experiment_camellia_v4 as v4
import experiment_camellia_v5 as v5


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "camellia_multilayer_taa_v6_adjusted_close.csv"
RESEARCH_OUTPUT = ROOT / "reports" / "generated" / "camellia_v6_research.json"
EVALUATION_OUTPUT = ROOT / "reports" / "generated" / "camellia_v6_evaluation.json"
PLAN_COMMIT = "41cb1fb2903e5a6667faa2e7b5a5109dcf53b2de"

MANAGED_FUTURES = ("DBMF", "KMLM", "CTA")
INFLATION_DEFENSE = ("SCHP", "GLDM", "PDBC")
NEW_TICKERS = MANAGED_FUTURES
UNIVERSE = tuple(dict.fromkeys(v5.UNIVERSE + NEW_TICKERS))
BLOCKS = v5.BLOCKS
EXPERIMENTS = {
    "baseline_v5": {},
    "q21_managed_futures": {"managed_futures": True},
    "q22_regional_equal_risk": {"regional_equal_risk": True},
    "q23_regional_rank_persistence": {"regional_rank_persistence": True},
    "q24_inflation_defense": {"inflation_defense": True},
    "q25_canary_consensus": {"canary_consensus": True},
}


def download_prices() -> pd.DataFrame:
    raw = yf.download(
        list(UNIVERSE),
        start="2006-01-01",
        auto_adjust=False,
        actions=False,
        progress=False,
        threads=True,
    )
    if "Adj Close" not in raw:
        raise RuntimeError("Yahoo Finance response has no adjusted close")
    prices = raw["Adj Close"].reindex(columns=UNIVERSE).sort_index()
    prices.index = pd.DatetimeIndex(prices.index).tz_localize(None)
    if prices.empty:
        raise RuntimeError("Yahoo Finance returned no rows")
    return prices


def load_prices(refresh: bool) -> tuple[pd.DataFrame, str]:
    if refresh:
        prices = download_prices()
        DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
        prices.to_csv(DATA_PATH, float_format="%.10f")
    else:
        if not DATA_PATH.is_file():
            raise FileNotFoundError(f"missing cache: {DATA_PATH}; use --refresh-data")
        prices = pd.read_csv(DATA_PATH, index_col=0, parse_dates=True)
        prices = prices.reindex(columns=UNIVERSE)
    return prices, hashlib.sha256(DATA_PATH.read_bytes()).hexdigest()


def data_audit(daily: pd.DataFrame, monthly: pd.DataFrame, digest: str) -> dict[str, object]:
    first_dates = {}
    last_dates = {}
    missing = {}
    for ticker in UNIVERSE:
        series = daily[ticker]
        first = series.first_valid_index()
        last = series.last_valid_index()
        if first is None or last is None:
            raise RuntimeError(f"no valid data for {ticker}")
        first_dates[ticker] = first.date().isoformat()
        last_dates[ticker] = last.date().isoformat()
        missing[ticker] = int(series.loc[first:last].isna().sum())
    return {
        "provider": "Yahoo Finance via yfinance",
        "field": "Adj Close",
        "daily_rows": len(daily),
        "monthly_completed_rows": len(monthly),
        "duplicate_dates": int(daily.index.duplicated().sum()),
        "dates_monotonic": bool(daily.index.is_monotonic_increasing),
        "first_dates": first_dates,
        "last_dates": last_dates,
        "post_inception_missing_daily_rows": missing,
        "cache_sha256": digest,
    }


def _positive_ranked(
    scores: pd.DataFrame, date: pd.Timestamp, universe: tuple[str, ...], count: int
) -> list[str]:
    valid = [
        ticker
        for ticker in universe
        if pd.notna(scores.at[date, ticker]) and scores.at[date, ticker] > 0
    ]
    return sorted(valid, key=lambda ticker: (-scores.at[date, ticker], universe.index(ticker)))[:count]


def _regional_selection(
    weighted: pd.DataFrame,
    date: pd.Timestamp,
    incumbents: list[str] | None,
    persistent: bool,
) -> list[str]:
    ranking = _positive_ranked(weighted, date, v5.REGIONAL, len(v5.REGIONAL))
    if not persistent or incumbents is None:
        return ranking[:2]
    selected = [ticker for ticker in incumbents if ticker in ranking]
    for ticker in ranking:
        if len(selected) == 2:
            break
        if ticker not in selected:
            selected.append(ticker)
    outsiders = [ticker for ticker in ranking if ticker not in selected]
    if len(selected) == 2 and outsiders and ranking[0] == outsiders[0]:
        weakest = max(selected, key=lambda ticker: ranking.index(ticker))
        selected[selected.index(weakest)] = outsiders[0]
    return selected


def _regional_weights(
    selected: list[str], volatility: pd.DataFrame, date: pd.Timestamp, equal_risk: bool
) -> dict[str, float]:
    if len(selected) < 2 or not equal_risk:
        return {ticker: 0.10 for ticker in selected}
    inverse = pd.Series({ticker: 1 / volatility.at[date, ticker] for ticker in selected})
    raw = 0.20 * inverse / inverse.sum()
    first = float(np.clip(raw.iloc[0], 0.05, 0.15))
    return {selected[0]: first, selected[1]: 0.20 - first}


def build_targets(
    prices: pd.DataFrame,
    *,
    managed_futures: bool = False,
    regional_equal_risk: bool = False,
    regional_rank_persistence: bool = False,
    inflation_defense: bool = False,
    canary_consensus: bool = False,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    weighted = bt.momentum(prices, weighted=True)
    blended = v4.multi_lookback_score(prices)
    monthly_returns = prices.pct_change(fill_method=None)
    volatility = monthly_returns.rolling(6).std(ddof=1) * np.sqrt(12)
    horizon_returns = {months: prices.pct_change(months, fill_method=None) for months in (1, 3, 6, 12)}
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

    rows: list[pd.Series] = []
    meta_rows: list[dict[str, object]] = []
    regional_incumbents: list[str] | None = None
    previous_cf: float | None = None
    regime_switches = 0

    for date in signal_dates:
        if canary_consensus:
            weak_count = sum(
                sum(horizon_returns[months].at[date, ticker] < 0 for months in (1, 3, 6, 12)) >= 3
                for ticker in bt.CANARIES
            )
        else:
            weak_count = int((weighted.loc[date, list(bt.CANARIES)] <= 0).sum())
        canary_cf = min(1.0, weak_count / 2)
        if previous_cf is not None and canary_cf != previous_cf:
            regime_switches += 1
        previous_cf = canary_cf
        risky_budget = 1.0 - canary_cf
        target = pd.Series(0.0, index=UNIVERSE)

        managed_available = [ticker for ticker in MANAGED_FUTURES if pd.notna(weighted.at[date, ticker])]
        managed_selected: list[str] = []
        if managed_futures and managed_available:
            target["VTI"] = 0.30 * risky_budget
            managed_selected = _positive_ranked(weighted, date, MANAGED_FUTURES, 1)
            if managed_selected:
                target[managed_selected[0]] = 0.10 * risky_budget
        else:
            target["VTI"] = 0.40 * risky_budget

        regional_selected = _regional_selection(
            weighted, date, regional_incumbents, regional_rank_persistence
        )
        regional_incumbents = regional_selected
        regional_weights = _regional_weights(
            regional_selected, volatility, date, regional_equal_risk
        )
        for ticker, weight in regional_weights.items():
            target[ticker] += weight * risky_budget

        target["DBC"] += 0.10 * risky_budget
        target["VNQ"] += 0.10 * risky_budget
        target["IEF"] += 0.10 * risky_budget
        target["TLT"] += 0.10 * risky_budget
        defensive_budget = 1.0 - float(target.sum())

        target["SHY"] += 0.50 * defensive_budget
        if blended.at[date, "IEF"] > 0:
            target["IEF"] += 0.25 * defensive_budget
            deflation = "IEF"
        else:
            target["SHY"] += 0.25 * defensive_budget
            deflation = "SHY"

        new_inflation_available = [
            ticker for ticker in INFLATION_DEFENSE if pd.notna(blended.at[date, ticker])
        ]
        inflation_universe = (
            INFLATION_DEFENSE if inflation_defense and new_inflation_available else ("GLD", "DBC")
        )
        available = [ticker for ticker in inflation_universe if pd.notna(blended.at[date, ticker])]
        inflation = max(available, key=lambda ticker: blended.at[date, ticker])
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
                "canary_cf": canary_cf,
                "total_defensive": defensive_budget,
                "us_winners": "VTI",
                "regional_winners": ",".join(regional_selected),
                "macro_winners": ",".join(managed_selected),
                "defensive_winner": f"SHY+{deflation}+{inflation}",
                "canary_regime_switches_to_date": regime_switches,
            }
        )
    return pd.DataFrame(rows), pd.DataFrame(meta_rows).set_index("signal_date")


def load_context(refresh_data: bool) -> dict[str, object]:
    daily, digest = load_prices(refresh_data)
    monthly = bt.completed_monthly_prices(daily, pd.Timestamp("2026-09-18"))
    returns = monthly.pct_change(fill_method=None)
    baseline_targets, _ = build_targets(monthly)
    fixed_6040 = pd.DataFrame(0.0, index=baseline_targets.index, columns=UNIVERSE)
    fixed_6040["SPY"] = 0.60
    fixed_6040["IEF"] = 0.40
    sixty_forty = bt.simulate(fixed_6040, returns, 0.001)
    spy = bt.simulate_buy_and_hold({"SPY": 1.0}, returns, sixty_forty.index, 0.001)
    return {
        "daily": daily,
        "monthly": monthly,
        "returns": returns,
        "digest": digest,
        "audit": data_audit(daily, monthly, digest),
        "shy": returns["SHY"],
        "spy": spy,
        "sixty_forty": sixty_forty,
    }


def run_configuration(context, config, high_cost: bool = False):
    targets, meta = build_targets(context["monthly"], **config)
    simulation = bt.simulate(
        targets,
        context["returns"],
        0.002 if high_cost else 0.001,
        rebalance_threshold=0.05,
    )
    return simulation, meta


def summarize_config(context, config):
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
        blocks[name] = item
    return blocks, v5.summarize_metrics(blocks)


def assess(summary, baseline):
    improvements = {
        "cagr": summary["median_cagr"] > baseline["median_cagr"],
        "calmar": summary["median_calmar"] > baseline["median_calmar"],
        "ulcer": summary["median_ulcer_index"] < baseline["median_ulcer_index"],
        "maximum_drawdown": summary["median_maximum_drawdown"] > baseline["median_maximum_drawdown"],
        "recovery": summary["median_recovery_months"] < baseline["median_recovery_months"],
        "upside_beta": summary["median_upside_beta_spy"] > baseline["median_upside_beta_spy"],
        "turnover": summary["median_turnover"] < baseline["median_turnover"],
        "pnl_concentration": summary["median_top_5_months_pnl_share"] < baseline["median_top_5_months_pnl_share"],
    }
    guardrails = {
        "all_cagr_positive": bool(summary["all_cagr_positive"]),
        "all_high_cost_cagr_positive": bool(summary["all_high_cost_cagr_positive"]),
        "worst_drawdown_within_25pct": summary["worst_maximum_drawdown"] >= -0.25,
        "cagr_not_materially_lower": summary["median_cagr"] >= baseline["median_cagr"] - 0.0035,
        "drawdown_not_materially_worse": summary["worst_maximum_drawdown"] >= baseline["worst_maximum_drawdown"] - 0.02,
        "downside_beta_not_materially_higher": summary["median_downside_beta_spy"] <= baseline["median_downside_beta_spy"] + 0.08,
        "turnover_within_cap": summary["median_turnover"] <= baseline["median_turnover"] * 1.25,
    }
    return {
        "improvements": improvements,
        "improvement_count": sum(improvements.values()),
        "guardrails": guardrails,
        "passes": all(guardrails.values()) and sum(improvements.values()) >= 4,
    }


def research_stage(refresh_data: bool) -> dict[str, object]:
    context = load_context(refresh_data)
    block_results = {}
    summaries = {}
    for name, config in EXPERIMENTS.items():
        block_results[name], summaries[name] = summarize_config(context, config)
    baseline = summaries["baseline_v5"]
    assessments = {name: assess(summaries[name], baseline) for name in list(EXPERIMENTS)[1:]}
    accepted = [name for name, item in assessments.items() if item["passes"]]
    combined_config = {}
    for name in accepted:
        combined_config.update(EXPERIMENTS[name])

    combined_blocks = {}
    combined_summary = {}
    combined_assessment = {"passes": False}
    if combined_config:
        combined_blocks, combined_summary = summarize_config(context, combined_config)
        combined_assessment = assess(combined_summary, baseline)

    if combined_config and combined_assessment["passes"]:
        selected_config = combined_config
        selection = "combined_accepted_experiments"
    elif len(accepted) == 1:
        selected_config = dict(EXPERIMENTS[accepted[0]])
        selection = f"single_accepted:{accepted[0]}"
    elif accepted:
        dominant = [
            name
            for name in accepted
            if all(name == other or v5.dominates(summaries[name], summaries[other]) for other in accepted)
        ]
        if len(dominant) == 1:
            selected_config = dict(EXPERIMENTS[dominant[0]])
            selection = f"pareto_dominant:{dominant[0]}"
        else:
            selected_config = {}
            selection = "no_clear_pareto_candidate_keep_v5"
    else:
        selected_config = {}
        selection = "no_experiment_passed_keep_v5"

    return {
        "stage": "research_blocks_only",
        "plan_commit": PLAN_COMMIT,
        "data_sha256": context["digest"],
        "data_audit": context["audit"],
        "webull_owner_confirmed_tradable_fractional": MANAGED_FUTURES,
        "experiments": EXPERIMENTS,
        "block_results": block_results,
        "summaries": summaries,
        "assessments": assessments,
        "accepted_experiments": accepted,
        "combined_config": combined_config,
        "combined_block_results": combined_blocks,
        "combined_summary": combined_summary,
        "combined_assessment": combined_assessment,
        "selected_config": selected_config,
        "selection_rule_result": selection,
    }


def evaluation_stage(config_path: Path) -> dict[str, object]:
    frozen = json.loads(config_path.read_text(encoding="utf-8"))
    context = load_context(False)
    if context["digest"] != frozen["data_sha256"]:
        raise RuntimeError("data snapshot changed after freeze")
    configurations = dict(EXPERIMENTS)
    configurations["frozen_v6"] = frozen["selected_config"]
    results = {}
    for name, config in configurations.items():
        simulation, meta = run_configuration(context, config)
        high_cost, high_meta = run_configuration(context, config, high_cost=True)
        results[name] = {}
        for period, (start, end) in {
            "recent_diagnostic": BLOCKS["recent_diagnostic"],
            "full": ("2008-08-01", "2026-08-31"),
        }.items():
            item = v4.period_metrics(context, simulation, meta, start, end)
            high = v4.period_metrics(context, high_cost, high_meta, start, end)
            item["high_cost_cagr"] = high["cagr"]
            item["high_cost_maximum_drawdown"] = high["maximum_drawdown"]
            results[name][period] = item
    for period in ("recent_diagnostic", "full"):
        bt.add_deflated_sharpe(results, period)

    recent = results["frozen_v6"]["recent_diagnostic"]
    full = results["frozen_v6"]["full"]
    baseline_full = results["baseline_v5"]["full"]
    safety = {
        "recent_net_cagr_positive": recent["cagr"] > 0,
        "recent_high_cost_cagr_positive": recent["high_cost_cagr"] > 0,
        "recent_maximum_drawdown_within_25pct": recent["maximum_drawdown"] >= -0.25,
        "recent_downside_beta_spy_below_one": recent["vs_spy"]["downside_beta"] < 1,
    }
    readiness = {
        "full_cagr_not_lower_than_v5_by_25bp": full["cagr"] >= baseline_full["cagr"] - 0.0025,
        "full_calmar_not_lower_than_v5": full["calmar"] >= baseline_full["calmar"],
        "full_drawdown_not_worse_than_v5": full["maximum_drawdown"] >= baseline_full["maximum_drawdown"],
        "full_high_cost_cagr_positive": full["high_cost_cagr"] > 0,
        "full_turnover_within_125pct_of_v5": full["annual_two_sided_turnover"] <= baseline_full["annual_two_sided_turnover"] * 1.25,
    }
    decision = "paper_ready" if all(safety.values()) and all(readiness.values()) else "revise"
    return {
        "stage": "frozen_v6_evaluation",
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
    parser.add_argument("--refresh-data", action="store_true")
    args = parser.parse_args()
    if args.stage == "research":
        payload = research_stage(args.refresh_data)
        output = RESEARCH_OUTPUT
    else:
        if args.config is None:
            parser.error("--config is required for evaluate")
        if args.refresh_data:
            parser.error("--refresh-data is not allowed during evaluation")
        payload = evaluation_stage(args.config)
        output = EVALUATION_OUTPUT
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")
    print(json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
