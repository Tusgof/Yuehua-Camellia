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


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "camellia_multilayer_taa_v5_adjusted_close.csv"
RESEARCH_OUTPUT = ROOT / "reports" / "generated" / "camellia_v5_research.json"
EVALUATION_OUTPUT = ROOT / "reports" / "generated" / "camellia_v5_evaluation.json"
PLAN_COMMIT = "8a2413221f8dd4cecc2a57712d718f2d44c23d3b"

NEW_TICKERS = ("VTI", "VGK", "EWJ", "IPAC", "SCHP", "GLDM", "PDBC", "VNQI")
UNIVERSE = tuple(dict.fromkeys(v4.UNIVERSE + NEW_TICKERS))
ALT_MACRO = ("SCHP", "GLDM", "PDBC", "VNQI")
REGIONAL = ("VGK", "EWJ", "IPAC", "VWO")
WEBULL_VERIFIED = (
    "VTI",
    "VGK",
    "EWJ",
    "IPAC",
    "VWO",
    "IEF",
    "SCHP",
    "GLDM",
    "PDBC",
    "VNQI",
)
BLOCKS = v4.BLOCKS
EXPERIMENTS = {
    "baseline_v4": {},
    "q16_fixed_vti": {"fixed_vti": True},
    "q17_deflation_only": {"defense_mode": "deflation_only"},
    "q17_inflation_only": {"defense_mode": "inflation_only"},
    "q18_rank_buffer": {"rank_buffer": True},
    "q19_alternative_macro": {"alternative_macro": True},
    "q20_regional_equity": {"regional_equity": True},
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
    digest = hashlib.sha256(DATA_PATH.read_bytes()).hexdigest()
    return prices, digest


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


def _available_positive_ranked(
    weighted: pd.DataFrame,
    date: pd.Timestamp,
    universe: tuple[str, ...],
    count: int,
) -> list[str]:
    available = [
        ticker
        for ticker in universe
        if pd.notna(weighted.at[date, ticker]) and weighted.at[date, ticker] > 0
    ]
    return sorted(
        available,
        key=lambda ticker: (-weighted.at[date, ticker], universe.index(ticker)),
    )[:count]


def build_targets(
    prices: pd.DataFrame,
    *,
    fixed_vti: bool = False,
    defense_mode: str = "v4",
    rank_buffer: bool = False,
    alternative_macro: bool = False,
    regional_equity: bool = False,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if fixed_vti and rank_buffer:
        raise ValueError("fixed_vti and rank_buffer are incompatible")
    if defense_mode not in ("v4", "deflation_only", "inflation_only"):
        raise ValueError("unsupported defense_mode")

    weighted = bt.momentum(prices, weighted=True)
    unweighted = bt.momentum(prices, weighted=False)
    blended = v4.multi_lookback_score(prices)
    required = pd.concat(
        [
            prices.loc[:, list(bt.TICKERS) + ["GLD"]],
            weighted.loc[:, list(bt.TICKERS) + ["GLD"]],
        ],
        axis=1,
    )
    if fixed_vti:
        required = pd.concat([required, weighted.loc[:, ["VTI"]]], axis=1)
    eligible = required.notna().all(axis=1) & (prices.index >= "2008-01-01")
    signal_dates = prices.index[eligible]
    signal_dates = signal_dates[signal_dates < prices.index[-1]]
    if signal_dates.empty:
        raise RuntimeError("no eligible signal dates")

    rows: list[pd.Series] = []
    meta_rows: list[dict[str, object]] = []
    buffered_us: list[str] | None = None

    for date in signal_dates:
        canary_scores = weighted.loc[date, list(bt.CANARIES)]
        weak_count = int((canary_scores <= 0).sum())
        canary_cf = min(1.0, weak_count / 2)
        risky_budget = 1.0 - canary_cf
        target = pd.Series(0.0, index=UNIVERSE)

        if fixed_vti:
            us_selected = ["VTI"]
            target["VTI"] = 0.40 * risky_budget
        else:
            ranking = sorted(
                bt.US_EQUITY,
                key=lambda ticker: (-unweighted.at[date, ticker], bt.TIE_ORDER_US[ticker]),
            )
            if rank_buffer and buffered_us is not None:
                outsider = next(ticker for ticker in bt.US_EQUITY if ticker not in buffered_us)
                if ranking[0] == outsider:
                    buffered_us = ranking[:2]
            else:
                buffered_us = ranking[:2]
            us_selected = list(buffered_us) if rank_buffer else ranking[:2]
            for ticker in us_selected:
                target[ticker] = 0.20 * risky_budget

        if regional_equity:
            regional_selected = _available_positive_ranked(weighted, date, REGIONAL, 2)
            for ticker in regional_selected:
                target[ticker] += 0.10 * risky_budget
        else:
            regional_selected = ["VEA"]
            target["VEA"] += 0.20 * risky_budget

        if alternative_macro:
            macro_selected = _available_positive_ranked(weighted, date, ALT_MACRO, 2)
            for ticker in macro_selected:
                target[ticker] += 0.10 * risky_budget
        else:
            macro_selected = ["DBC", "VNQ"]
            target["DBC"] += 0.10 * risky_budget
            target["VNQ"] += 0.10 * risky_budget

        target["IEF"] += 0.10 * risky_budget
        target["TLT"] += 0.10 * risky_budget
        defensive_budget = 1.0 - float(target.sum())

        if defense_mode == "deflation_only":
            target["SHY"] += 0.75 * defensive_budget
            if blended.at[date, "IEF"] > 0:
                target["IEF"] += 0.25 * defensive_budget
                defense_label = "SHY+IEF"
            else:
                target["SHY"] += 0.25 * defensive_budget
                defense_label = "SHY"
        elif defense_mode == "inflation_only":
            target["SHY"] += 0.75 * defensive_budget
            inflation = max(("GLD", "DBC"), key=lambda ticker: blended.at[date, ticker])
            if blended.at[date, inflation] > 0:
                target[inflation] += 0.25 * defensive_budget
            else:
                target["SHY"] += 0.25 * defensive_budget
                inflation = "SHY"
            defense_label = f"SHY+{inflation}"
        else:
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
            defense_label = f"SHY+{deflation}+{inflation}"

        if not np.isclose(float(target.sum()), 1.0, atol=1e-12):
            raise AssertionError(f"target weights do not sum to one at {date}")
        rows.append(target.rename(date))
        meta_rows.append(
            {
                "signal_date": date,
                "weak_canaries": weak_count,
                "canary_cf": canary_cf,
                "total_defensive": defensive_budget,
                "us_winners": ",".join(us_selected),
                "regional_winners": ",".join(regional_selected),
                "macro_winners": ",".join(macro_selected),
                "defensive_winner": defense_label,
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


def period_metrics(context, simulation, meta, start: str, end: str):
    return v4.period_metrics(context, simulation, meta, start, end)


def summarize_metrics(blocks: dict[str, dict[str, object]]) -> dict[str, object]:
    def median(key: str) -> float:
        return float(np.median([float(item[key]) for item in blocks.values()]))

    return {
        "median_cagr": median("cagr"),
        "median_high_cost_cagr": median("high_cost_cagr"),
        "median_calmar": median("calmar"),
        "median_ulcer_index": median("ulcer_index"),
        "median_maximum_drawdown": median("maximum_drawdown"),
        "worst_maximum_drawdown": min(float(item["maximum_drawdown"]) for item in blocks.values()),
        "median_recovery_months": median("recovery_months_from_pre_trough_peak"),
        "median_upside_beta_spy": float(np.median([float(item["vs_spy"]["upside_beta"]) for item in blocks.values()])),  # type: ignore[index]
        "median_downside_beta_spy": float(np.median([float(item["vs_spy"]["downside_beta"]) for item in blocks.values()])),  # type: ignore[index]
        "median_turnover": median("annual_two_sided_turnover"),
        "median_top_5_months_pnl_share": float(np.median([float(item["top_5_months_pnl_share"]) for item in blocks.values()])),
        "all_cagr_positive": all(float(item["cagr"]) > 0 for item in blocks.values()),
        "all_high_cost_cagr_positive": all(float(item["high_cost_cagr"]) > 0 for item in blocks.values()),
    }


def summarize_config(context: dict[str, object], config: dict[str, object]):
    simulation, meta = run_configuration(context, config)
    high_cost, high_meta = run_configuration(context, config, high_cost=True)
    blocks = {}
    for name, (start, end) in BLOCKS.items():
        if name == "recent_diagnostic":
            continue
        item = period_metrics(context, simulation, meta, start, end)
        high = period_metrics(context, high_cost, high_meta, start, end)
        item["high_cost_cagr"] = high["cagr"]
        item["high_cost_maximum_drawdown"] = high["maximum_drawdown"]
        blocks[name] = item
    return blocks, summarize_metrics(blocks)


def assess(summary: dict[str, object], baseline: dict[str, object]) -> dict[str, object]:
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
        "worst_drawdown_within_30pct": summary["worst_maximum_drawdown"] >= -0.30,
        "cagr_not_materially_lower": summary["median_cagr"] >= baseline["median_cagr"] - 0.005,
        "drawdown_not_materially_worse": summary["worst_maximum_drawdown"] >= baseline["worst_maximum_drawdown"] - 0.03,
        "downside_beta_not_materially_higher": summary["median_downside_beta_spy"] <= baseline["median_downside_beta_spy"] + 0.10,
        "turnover_within_cap": summary["median_turnover"] <= baseline["median_turnover"] * 1.25,
    }
    return {
        "improvements": improvements,
        "improvement_count": sum(improvements.values()),
        "guardrails": guardrails,
        "passes": all(guardrails.values()) and sum(improvements.values()) >= 4,
    }


def dominates(left: dict[str, object], right: dict[str, object]) -> bool:
    directions = {
        "median_cagr": 1,
        "median_calmar": 1,
        "median_ulcer_index": -1,
        "median_maximum_drawdown": 1,
        "median_recovery_months": -1,
        "median_upside_beta_spy": 1,
        "median_turnover": -1,
        "median_top_5_months_pnl_share": -1,
    }
    comparisons = []
    strict = []
    for key, direction in directions.items():
        lvalue = float(left[key]) * direction
        rvalue = float(right[key]) * direction
        comparisons.append(lvalue >= rvalue)
        strict.append(lvalue > rvalue)
    return all(comparisons) and any(strict)


def research_stage(refresh_data: bool) -> dict[str, object]:
    context = load_context(refresh_data)
    block_results = {}
    summaries = {}
    for name, config in EXPERIMENTS.items():
        block_results[name], summaries[name] = summarize_config(context, config)
    baseline = summaries["baseline_v4"]
    assessments = {
        name: assess(summaries[name], baseline) for name in list(EXPERIMENTS)[1:]
    }
    accepted = [name for name, item in assessments.items() if item["passes"]]

    combined_config: dict[str, object] = {}
    if "q16_fixed_vti" in accepted:
        combined_config.update(EXPERIMENTS["q16_fixed_vti"])
    elif "q18_rank_buffer" in accepted:
        combined_config.update(EXPERIMENTS["q18_rank_buffer"])

    defense_candidates = [
        name
        for name in ("q17_deflation_only", "q17_inflation_only")
        if name in accepted and dominates(summaries[name], baseline)
    ]
    if len(defense_candidates) == 1:
        combined_config.update(EXPERIMENTS[defense_candidates[0]])
    for name in ("q19_alternative_macro", "q20_regional_equity"):
        if name in accepted:
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
            if all(name == other or dominates(summaries[name], summaries[other]) for other in accepted)
        ]
        if len(dominant) == 1:
            selected_config = dict(EXPERIMENTS[dominant[0]])
            selection = f"pareto_dominant:{dominant[0]}"
        else:
            selected_config = {}
            selection = "no_clear_pareto_candidate_keep_v4"
    else:
        selected_config = {}
        selection = "no_experiment_passed_keep_v4"

    return {
        "stage": "research_blocks_only",
        "plan_commit": PLAN_COMMIT,
        "data_sha256": context["digest"],
        "data_audit": context["audit"],
        "webull_verified_status_oc_fractionable": WEBULL_VERIFIED,
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
    configurations["frozen_v5"] = frozen["selected_config"]
    results = {}
    for name, config in configurations.items():
        simulation, meta = run_configuration(context, config)
        high_cost, high_meta = run_configuration(context, config, high_cost=True)
        results[name] = {}
        for period, (start, end) in {
            "recent_diagnostic": BLOCKS["recent_diagnostic"],
            "full": ("2008-08-01", "2026-08-31"),
        }.items():
            item = period_metrics(context, simulation, meta, start, end)
            high = period_metrics(context, high_cost, high_meta, start, end)
            item["high_cost_cagr"] = high["cagr"]
            item["high_cost_maximum_drawdown"] = high["maximum_drawdown"]
            results[name][period] = item
    for period in ("recent_diagnostic", "full"):
        bt.add_deflated_sharpe(results, period)

    recent = results["frozen_v5"]["recent_diagnostic"]
    full = results["frozen_v5"]["full"]
    v4_full = results["baseline_v4"]["full"]
    safety = {
        "recent_net_cagr_positive": recent["cagr"] > 0,
        "recent_high_cost_cagr_positive": recent["high_cost_cagr"] > 0,
        "recent_maximum_drawdown_within_30pct": recent["maximum_drawdown"] >= -0.30,
        "recent_downside_beta_spy_below_one": recent["vs_spy"]["downside_beta"] < 1,
    }
    paper_ready = {
        "full_cagr_not_lower_than_v4_by_25bp": full["cagr"] >= v4_full["cagr"] - 0.0025,
        "full_calmar_not_lower_than_v4": full["calmar"] >= v4_full["calmar"],
        "full_drawdown_not_worse_than_v4": full["maximum_drawdown"] >= v4_full["maximum_drawdown"],
        "full_high_cost_cagr_positive": full["high_cost_cagr"] > 0,
        "full_turnover_within_125pct_of_v4": full["annual_two_sided_turnover"] <= v4_full["annual_two_sided_turnover"] * 1.25,
    }
    decision = "paper_ready" if all(safety.values()) and all(paper_ready.values()) else "revise"
    return {
        "stage": "frozen_v5_evaluation",
        "frozen_config": frozen,
        "results": results,
        "recent_safety_checks": safety,
        "paper_ready_checks": paper_ready,
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
    output.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False),
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
