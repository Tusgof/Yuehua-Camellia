from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

import backtest_camellia_multilayer_taa as bt


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "camellia_multilayer_taa_v4_adjusted_close.csv"
RESEARCH_OUTPUT = ROOT / "reports" / "generated" / "camellia_v4_research.json"
EVALUATION_OUTPUT = ROOT / "reports" / "generated" / "camellia_v4_evaluation.json"
PLAN_COMMIT = "e54dfaf032325fc717316bc110e9b1a571abb25d"

SECTORS = ("XLB", "XLE", "XLF", "XLI", "XLK", "XLP", "XLU", "XLV", "XLY")
EXTRA_TICKERS = SECTORS + ("GLD",)
UNIVERSE = tuple(dict.fromkeys(bt.TICKERS + EXTRA_TICKERS))
STRATEGIC = bt.STRATEGIC_WEIGHTS
BLOCKS = {
    "block_1": ("2008-08-01", "2012-12-31"),
    "block_2": ("2013-01-01", "2018-12-31"),
    "block_3": ("2019-01-01", "2022-12-31"),
    "recent_diagnostic": ("2023-01-01", "2026-08-31"),
}
EXPERIMENTS = {
    "baseline_v2": {},
    "q11_core_overlay": {"core_fraction": 0.70},
    "q12_continuous_trend": {"continuous_trend": True},
    "q13_sector_momentum": {"sector_momentum": True},
    "q14_diversified_defense": {"diversified_defense": True},
    "q15_cost_aware_execution": {"cost_aware_execution": True},
}
ATTRIBUTION = {
    "v2": {},
    "no_canary": {"disable_canary": True},
    "fixed_spy": {"fixed_spy": True},
    "shy_only_defense": {"shy_only_defense": True},
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


def multi_lookback_score(prices: pd.DataFrame) -> pd.DataFrame:
    returns = [prices / prices.shift(months) - 1 for months in (1, 3, 6, 12)]
    signs = [np.sign(item) for item in returns]
    return sum(signs) / len(signs)


def _ranked_defensive(weighted: pd.DataFrame, date: pd.Timestamp) -> str:
    scores = weighted.loc[date, list(bt.DEFENSIVE)]
    winner = bt.ranked_winner(scores, bt.TIE_ORDER_DEFENSIVE)
    return winner if scores[winner] > 0 else "SHY"


def build_modular_targets(
    prices: pd.DataFrame,
    *,
    core_fraction: float = 0.0,
    continuous_trend: bool = False,
    sector_momentum: bool = False,
    diversified_defense: bool = False,
    disable_canary: bool = False,
    fixed_spy: bool = False,
    shy_only_defense: bool = False,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if not 0 <= core_fraction <= 1:
        raise ValueError("core_fraction must be between zero and one")
    weighted = bt.momentum(prices, weighted=True)
    unweighted = bt.momentum(prices, weighted=False)
    blended = multi_lookback_score(prices)
    required_tickers = list(bt.TICKERS)
    if sector_momentum:
        required_tickers.extend(SECTORS)
    if diversified_defense:
        required_tickers.append("GLD")
    required = pd.concat(
        [prices.loc[:, required_tickers], weighted.loc[:, required_tickers]], axis=1
    )
    eligible = required.notna().all(axis=1) & (prices.index >= "2008-01-01")
    signal_dates = prices.index[eligible]
    signal_dates = signal_dates[signal_dates < prices.index[-1]]
    if signal_dates.empty:
        raise RuntimeError("no eligible signal dates")

    rows: list[pd.Series] = []
    meta_rows: list[dict[str, object]] = []
    other_risky = {"VEA": 0.20, "DBC": 0.10, "VNQ": 0.10, "IEF": 0.10, "TLT": 0.10}
    core = pd.Series(0.0, index=UNIVERSE)
    for ticker, weight in STRATEGIC.items():
        core[ticker] = weight

    for date in signal_dates:
        canary_scores = weighted.loc[date, list(bt.CANARIES)]
        weak_count = int((canary_scores <= 0).sum())
        canary_cf = 0.0 if (continuous_trend or disable_canary) else min(1.0, weak_count / 2)
        risky_budget = 1.0 - canary_cf
        tactical = pd.Series(0.0, index=UNIVERSE)

        if sector_momentum:
            ranked = sorted(
                SECTORS,
                key=lambda ticker: (-weighted.at[date, ticker], SECTORS.index(ticker)),
            )
            selected = ranked[:3]
            for ticker in selected:
                tactical[ticker] = 0.40 * risky_budget / 3
        elif fixed_spy:
            selected = ["SPY"]
            tactical["SPY"] = 0.40 * risky_budget
        else:
            ranked = sorted(
                bt.US_EQUITY,
                key=lambda ticker: (
                    -unweighted.at[date, ticker],
                    bt.TIE_ORDER_US[ticker],
                ),
            )
            selected = ranked[:2]
            for ticker in selected:
                tactical[ticker] = 0.20 * risky_budget
        for ticker, weight in other_risky.items():
            tactical[ticker] += weight * risky_budget

        if continuous_trend:
            for ticker in list(tactical[tactical > 0].index):
                multiplier = float((blended.at[date, ticker] + 1) / 2)
                tactical[ticker] *= multiplier

        defensive_budget = 1.0 - float(tactical.sum())
        if shy_only_defense:
            tactical["SHY"] += defensive_budget
            defensive_label = "SHY"
        elif diversified_defense:
            tactical["SHY"] += 0.50 * defensive_budget
            if blended.at[date, "IEF"] > 0:
                tactical["IEF"] += 0.25 * defensive_budget
                deflation = "IEF"
            else:
                tactical["SHY"] += 0.25 * defensive_budget
                deflation = "SHY"
            inflation = max(("GLD", "DBC"), key=lambda ticker: blended.at[date, ticker])
            if blended.at[date, inflation] > 0:
                tactical[inflation] += 0.25 * defensive_budget
            else:
                tactical["SHY"] += 0.25 * defensive_budget
                inflation = "SHY"
            defensive_label = f"SHY+{deflation}+{inflation}"
        else:
            winner = _ranked_defensive(weighted, date)
            tactical[winner] += defensive_budget
            defensive_label = winner

        target = core_fraction * core + (1 - core_fraction) * tactical
        if not np.isclose(float(target.sum()), 1.0, atol=1e-12):
            raise AssertionError(f"target weights do not sum to one at {date}")
        rows.append(target.rename(date))
        meta_rows.append(
            {
                "signal_date": date,
                "weak_canaries": weak_count,
                "canary_cf": (1 - core_fraction) * canary_cf,
                "total_defensive": (1 - core_fraction) * defensive_budget,
                "us_winners": ",".join(selected),
                "defensive_winner": defensive_label,
            }
        )
    return pd.DataFrame(rows), pd.DataFrame(meta_rows).set_index("signal_date")


def simulate_cost_aware(
    targets: pd.DataFrame,
    asset_returns: pd.DataFrame,
    meta: pd.DataFrame,
    cost_rate: float,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    previous_target: pd.Series | None = None
    previous_canary = 0.0
    dates = asset_returns.index
    for signal_date, target in targets.iterrows():
        position = dates.get_loc(signal_date)
        return_date = dates[position + 1]
        if previous_target is None:
            pretrade = pd.Series(0.0, index=target.index)
        else:
            realized = asset_returns.loc[signal_date, target.index]
            portfolio_return = float((previous_target * realized).sum())
            pretrade = previous_target * (1 + realized) / (1 + portfolio_return)
        changes = target - pretrade
        proposed_one_way = float(changes.abs().sum() / 2)
        current_canary = float(meta.at[signal_date, "canary_cf"])
        risk_escalation = previous_target is not None and current_canary > previous_canary
        execute = previous_target is None or proposed_one_way >= 0.15 or risk_escalation
        executed_target = target if execute else pretrade
        executed_changes = executed_target - pretrade
        turnover = float(executed_changes.abs().sum())
        cost = cost_rate * turnover
        gross = float((executed_target * asset_returns.loc[return_date, target.index]).sum())
        rows.append(
            {
                "date": return_date,
                "signal_date": signal_date,
                "gross_return": gross,
                "net_return": gross - cost,
                "cost": cost,
                "two_sided_turnover": turnover,
                "one_way_turnover": turnover / 2,
                "orders": int((executed_changes.abs() > 1e-10).sum()),
                "target_changed": execute,
                "rebalance_skipped": not execute,
            }
        )
        previous_target = executed_target
        previous_canary = current_canary
    return pd.DataFrame(rows).set_index("date")


def load_context(refresh_data: bool) -> dict[str, object]:
    daily, digest = load_prices(refresh_data)
    monthly = bt.completed_monthly_prices(daily, pd.Timestamp("2026-09-18"))
    returns = monthly.pct_change(fill_method=None)
    baseline_targets, _ = build_modular_targets(monthly)
    fixed_6040 = pd.DataFrame(0.0, index=baseline_targets.index, columns=UNIVERSE)
    fixed_6040["SPY"] = 0.60
    fixed_6040["IEF"] = 0.40
    sixty_forty = bt.simulate(fixed_6040, returns, 0.001)
    return_dates = sixty_forty.index
    spy = bt.simulate_buy_and_hold({"SPY": 1.0}, returns, return_dates, 0.001)
    strategic = bt.simulate_buy_and_hold(STRATEGIC, returns, return_dates, 0.001)
    strategic_high_cost = bt.simulate_buy_and_hold(
        STRATEGIC, returns, return_dates, 0.002
    )
    return {
        "daily": daily,
        "monthly": monthly,
        "returns": returns,
        "digest": digest,
        "audit": data_audit(daily, monthly, digest),
        "shy": returns["SHY"],
        "spy": spy,
        "sixty_forty": sixty_forty,
        "strategic": strategic,
        "strategic_high_cost": strategic_high_cost,
    }


def run_configuration(
    context: dict[str, object], config: dict[str, object], high_cost: bool = False
) -> tuple[pd.DataFrame, pd.DataFrame]:
    target_keys = {
        "core_fraction",
        "continuous_trend",
        "sector_momentum",
        "diversified_defense",
        "disable_canary",
        "fixed_spy",
        "shy_only_defense",
    }
    target_config = {key: value for key, value in config.items() if key in target_keys}
    targets, meta = build_modular_targets(
        context["monthly"], **target_config  # type: ignore[arg-type]
    )
    cost_rate = 0.002 if high_cost else 0.001
    if config.get("cost_aware_execution"):
        simulation = simulate_cost_aware(targets, context["returns"], meta, cost_rate)  # type: ignore[arg-type]
    else:
        simulation = bt.simulate(
            targets,
            context["returns"],  # type: ignore[arg-type]
            cost_rate,
            rebalance_threshold=0.05,
        )
    return simulation, meta


def period_metrics(
    context: dict[str, object],
    simulation: pd.DataFrame,
    meta: pd.DataFrame | None,
    start: str,
    end: str,
) -> dict[str, object]:
    frame = simulation.loc[start:end]
    result = bt.performance_metrics(
        frame,
        context["shy"],  # type: ignore[arg-type]
        context["spy"]["net_return"],  # type: ignore[index]
        context["sixty_forty"]["net_return"],  # type: ignore[index]
    )
    if meta is not None:
        aligned = meta.reindex(frame["signal_date"])
        result["average_canary_cf"] = float(aligned["canary_cf"].mean())
        result["average_total_defensive"] = float(aligned["total_defensive"].mean())
    return result


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


def summarize_metrics(blocks: dict[str, dict[str, object]]) -> dict[str, object]:
    def median(key: str) -> float:
        return float(np.median([float(item[key]) for item in blocks.values()]))

    downside_betas = [float(item["vs_spy"]["downside_beta"]) for item in blocks.values()]  # type: ignore[index]
    concentrations = [float(item["top_5_months_pnl_share"]) for item in blocks.values()]  # type: ignore[arg-type]
    return {
        "median_cagr": median("cagr"),
        "median_high_cost_cagr": median("high_cost_cagr"),
        "median_calmar": median("calmar"),
        "median_ulcer_index": median("ulcer_index"),
        "median_maximum_drawdown": median("maximum_drawdown"),
        "worst_maximum_drawdown": min(float(item["maximum_drawdown"]) for item in blocks.values()),
        "median_downside_beta_spy": float(np.median(downside_betas)),
        "median_turnover": median("annual_two_sided_turnover"),
        "median_top_5_months_pnl_share": float(np.median(concentrations)),
        "all_cagr_positive": all(float(item["cagr"]) > 0 for item in blocks.values()),
    }


def assess(summary: dict[str, object], baseline: dict[str, object]) -> dict[str, object]:
    improvements = {
        "cagr": summary["median_cagr"] > baseline["median_cagr"],
        "calmar": summary["median_calmar"] > baseline["median_calmar"],
        "ulcer": summary["median_ulcer_index"] < baseline["median_ulcer_index"],
        "maximum_drawdown": summary["median_maximum_drawdown"] > baseline["median_maximum_drawdown"],
        "turnover": summary["median_turnover"] < baseline["median_turnover"],
        "pnl_concentration": summary["median_top_5_months_pnl_share"] < baseline["median_top_5_months_pnl_share"],
    }
    guardrails = {
        "all_cagr_positive": bool(summary["all_cagr_positive"]),
        "median_high_cost_cagr_positive": summary["median_high_cost_cagr"] > 0,
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
        "passes": all(guardrails.values()) and sum(improvements.values()) >= 3,
    }


def dominates(left: dict[str, object], right: dict[str, object]) -> bool:
    directions = {
        "median_cagr": 1,
        "median_calmar": 1,
        "median_ulcer_index": -1,
        "median_maximum_drawdown": 1,
        "median_turnover": -1,
        "median_top_5_months_pnl_share": -1,
    }
    weakly_better = []
    strictly_better = []
    for key, direction in directions.items():
        lvalue = float(left[key]) * direction
        rvalue = float(right[key]) * direction
        weakly_better.append(lvalue >= rvalue)
        strictly_better.append(lvalue > rvalue)
    return all(weakly_better) and any(strictly_better)


def research_stage(refresh_data: bool) -> dict[str, object]:
    context = load_context(refresh_data)
    block_results = {}
    summaries = {}
    for name, config in EXPERIMENTS.items():
        block_results[name], summaries[name] = summarize_config(context, config)
    baseline = summaries["baseline_v2"]
    assessments = {
        name: assess(summaries[name], baseline) for name in list(EXPERIMENTS)[1:]
    }
    accepted = [name for name, item in assessments.items() if item["passes"]]

    combined_config: dict[str, object] = {}
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
            if all(
                name == other or dominates(summaries[name], summaries[other])
                for other in accepted
            )
        ]
        if len(dominant) == 1:
            selected_config = dict(EXPERIMENTS[dominant[0]])
            selection = f"pareto_dominant:{dominant[0]}"
        else:
            selected_config = {}
            selection = "no_clear_pareto_candidate_keep_v2"
    else:
        selected_config = {}
        selection = "no_experiment_passed_keep_v2"

    attribution = {}
    for name, config in ATTRIBUTION.items():
        blocks, summary = summarize_config(context, config)
        attribution[name] = {"blocks": blocks, "summary": summary}
    strategic_blocks = {}
    for name, (start, end) in BLOCKS.items():
        if name == "recent_diagnostic":
            continue
        strategic_blocks[name] = period_metrics(
            context, context["strategic"], None, start, end  # type: ignore[arg-type]
        )
        high = period_metrics(
            context,
            context["strategic_high_cost"],  # type: ignore[arg-type]
            None,
            start,
            end,
        )
        strategic_blocks[name]["high_cost_cagr"] = high["cagr"]
    attribution["strategic_buy_hold"] = {
        "blocks": strategic_blocks,
        "summary": summarize_metrics(strategic_blocks),
    }

    return {
        "stage": "research_blocks_only",
        "plan_commit": PLAN_COMMIT,
        "data_sha256": context["digest"],
        "data_audit": context["audit"],
        "experiments": EXPERIMENTS,
        "attribution": attribution,
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
    configurations["frozen_v4"] = frozen["selected_config"]
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
    recent = results["frozen_v4"]["recent_diagnostic"]
    safety_vetoes = {
        "net_cagr_not_positive": recent["cagr"] <= 0,
        "maximum_drawdown_below_minus_30pct": recent["maximum_drawdown"] < -0.30,
        "high_cost_cagr_not_positive": recent["high_cost_cagr"] <= 0,
        "downside_beta_spy_above_one": recent["vs_spy"]["downside_beta"] > 1,
    }
    return {
        "stage": "frozen_v4_evaluation",
        "frozen_config": frozen,
        "results": results,
        "safety_vetoes": safety_vetoes,
        "safety_veto_triggered": any(safety_vetoes.values()),
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
