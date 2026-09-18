from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from statistics import NormalDist

import numpy as np
import pandas as pd
import yfinance as yf


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "camellia_multilayer_taa_adjusted_close.csv"
OUTPUT_PATH = ROOT / "reports" / "generated" / "camellia_multilayer_taa_v1.json"

TICKERS = (
    "VWO",
    "BND",
    "TIP",
    "SPY",
    "MDY",
    "IJR",
    "VEA",
    "DBC",
    "VNQ",
    "IEF",
    "TLT",
    "SHY",
    "LQD",
)
CANARIES = ("VWO", "BND", "TIP")
US_EQUITY = ("SPY", "MDY", "IJR")
DEFENSIVE = ("SHY", "IEF", "LQD")
RISKY_UNIVERSE = ("SPY", "MDY", "IJR", "VEA", "DBC", "VNQ", "IEF", "TLT")
TIE_ORDER_US = {ticker: rank for rank, ticker in enumerate(US_EQUITY)}
TIE_ORDER_DEFENSIVE = {ticker: rank for rank, ticker in enumerate(DEFENSIVE)}
STRATEGIC_WEIGHTS = {
    "SPY": 0.40,
    "VEA": 0.20,
    "DBC": 0.10,
    "VNQ": 0.10,
    "IEF": 0.10,
    "TLT": 0.10,
}


def download_adjusted_close() -> pd.DataFrame:
    raw = yf.download(
        list(TICKERS),
        start="2006-01-01",
        auto_adjust=False,
        actions=False,
        progress=False,
        threads=True,
    )
    if "Adj Close" not in raw:
        raise RuntimeError("Yahoo Finance response has no adjusted close")
    prices = raw["Adj Close"].reindex(columns=TICKERS).sort_index()
    prices.index = pd.DatetimeIndex(prices.index).tz_localize(None)
    if prices.empty:
        raise RuntimeError("Yahoo Finance returned no rows")
    return prices


def load_prices(cache_only: bool) -> tuple[pd.DataFrame, str]:
    if cache_only:
        if not DATA_PATH.is_file():
            raise FileNotFoundError(f"missing cache: {DATA_PATH}")
        prices = pd.read_csv(DATA_PATH, index_col=0, parse_dates=True)
        prices = prices.reindex(columns=TICKERS)
    else:
        prices = download_adjusted_close()
        DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
        prices.to_csv(DATA_PATH, float_format="%.10f")
    digest = hashlib.sha256(DATA_PATH.read_bytes()).hexdigest()
    return prices, digest


def completed_monthly_prices(daily: pd.DataFrame, now: pd.Timestamp) -> pd.DataFrame:
    current_month_start = now.to_period("M").start_time
    completed = daily.loc[daily.index < current_month_start]
    return completed.resample("ME").last()


def momentum(prices: pd.DataFrame, weighted: bool) -> pd.DataFrame:
    r1 = prices / prices.shift(1) - 1
    r3 = prices / prices.shift(3) - 1
    r6 = prices / prices.shift(6) - 1
    r12 = prices / prices.shift(12) - 1
    if weighted:
        return (12 * r1 + 4 * r3 + 2 * r6 + r12) / 4
    return (r1 + r3 + r6 + r12) / 4


def ranked_winner(scores: pd.Series, order: dict[str, int]) -> str:
    return min(scores.index, key=lambda ticker: (-scores[ticker], order[ticker]))


def build_targets(
    prices: pd.DataFrame,
    sma_months: int,
    *,
    breadth_level: int = 2,
    trend_gate: bool = True,
    trend_retention: float = 0.0,
    us_top_count: int = 1,
    risky_top_count: int | None = None,
    defensive_policy: str = "ranked",
    defensive_shy_fraction: float = 0.0,
    max_canary_cf: float = 1.0,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if breadth_level <= 0:
        raise ValueError("breadth_level must be positive")
    if us_top_count not in (1, 2, 3):
        raise ValueError("us_top_count must be between one and three")
    if defensive_policy not in ("ranked", "shy_only"):
        raise ValueError("unsupported defensive_policy")
    if not 0 <= trend_retention <= 1:
        raise ValueError("trend_retention must be between zero and one")
    if risky_top_count is not None and not 1 <= risky_top_count <= len(RISKY_UNIVERSE):
        raise ValueError("invalid risky_top_count")
    if not 0 <= defensive_shy_fraction <= 1:
        raise ValueError("defensive_shy_fraction must be between zero and one")
    weighted = momentum(prices, weighted=True)
    unweighted = momentum(prices, weighted=False)
    sma = prices.rolling(sma_months, min_periods=sma_months).mean()
    required = pd.concat(
        [
            weighted.loc[:, list(CANARIES) + list(DEFENSIVE)],
            unweighted.loc[:, list(US_EQUITY)],
            prices.loc[:, list(TICKERS)],
            sma.loc[:, list(US_EQUITY) + ["VEA", "DBC", "VNQ", "IEF", "TLT"]],
        ],
        axis=1,
    )
    if risky_top_count is not None:
        required = pd.concat(
            [required, weighted.loc[:, list(RISKY_UNIVERSE)]], axis=1
        )
    eligible = required.notna().all(axis=1) & (prices.index >= "2008-01-01")
    signal_dates = prices.index[eligible]
    signal_dates = signal_dates[signal_dates < prices.index[-1]]
    if signal_dates.empty:
        raise RuntimeError("no eligible signal dates")

    rows: list[pd.Series] = []
    meta_rows: list[dict[str, object]] = []
    risky_fixed = {"VEA": 0.20, "DBC": 0.10, "VNQ": 0.10, "IEF": 0.10, "TLT": 0.10}

    for date in signal_dates:
        canary_scores = weighted.loc[date, list(CANARIES)]
        weak_count = int((canary_scores <= 0).sum())
        canary_cf = min(max_canary_cf, weak_count / breadth_level)
        risky_budget = 1.0 - canary_cf

        if risky_top_count is not None:
            risky_selected = sorted(
                RISKY_UNIVERSE,
                key=lambda ticker: (-weighted.at[date, ticker], RISKY_UNIVERSE.index(ticker)),
            )[:risky_top_count]
            risky_weights = {
                ticker: risky_budget / risky_top_count for ticker in risky_selected
            }
            us_selected = [ticker for ticker in risky_selected if ticker in US_EQUITY]
        else:
            us_ranked = sorted(
                US_EQUITY,
                key=lambda ticker: (-unweighted.at[date, ticker], TIE_ORDER_US[ticker]),
            )
            us_selected = us_ranked[:us_top_count]
            risky_weights = {
                ticker: 0.40 * risky_budget / us_top_count for ticker in us_selected
            }
            risky_weights.update(
                {ticker: weight * risky_budget for ticker, weight in risky_fixed.items()}
            )

        target = pd.Series(0.0, index=TICKERS, dtype=float)
        failed_trend = 0.0
        for ticker, weight in risky_weights.items():
            if not trend_gate or prices.at[date, ticker] > sma.at[date, ticker]:
                target[ticker] += weight
            else:
                retained = weight * trend_retention
                target[ticker] += retained
                failed_trend += weight - retained

        if defensive_policy == "shy_only":
            defensive_winner = "SHY"
        else:
            defensive_scores = weighted.loc[date, list(DEFENSIVE)]
            defensive_winner = ranked_winner(defensive_scores, TIE_ORDER_DEFENSIVE)
            if defensive_scores[defensive_winner] <= 0:
                defensive_winner = "SHY"
        total_defensive = canary_cf + failed_trend
        target["SHY"] += total_defensive * defensive_shy_fraction
        target[defensive_winner] += total_defensive * (1 - defensive_shy_fraction)

        if not math.isclose(float(target.sum()), 1.0, abs_tol=1e-12):
            raise AssertionError(f"target weights do not sum to one at {date}")
        rows.append(target.rename(date))
        meta_rows.append(
            {
                "signal_date": date,
                "weak_canaries": weak_count,
                "canary_cf": canary_cf,
                "total_defensive": total_defensive,
                "us_winners": ",".join(us_selected),
                "defensive_winner": defensive_winner,
            }
        )

    return pd.DataFrame(rows), pd.DataFrame(meta_rows).set_index("signal_date")


def simulate(
    targets: pd.DataFrame,
    asset_returns: pd.DataFrame,
    cost_rate: float,
    rebalance_threshold: float = 0.0,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    previous_target: pd.Series | None = None
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

        proposed_changes = target - pretrade
        proposed_one_way = float(proposed_changes.abs().sum() / 2)
        skip_rebalance = previous_target is not None and proposed_one_way < rebalance_threshold
        executed_target = pretrade if skip_rebalance else target
        changes = executed_target - pretrade
        two_sided_turnover = float(changes.abs().sum())
        cost = cost_rate * two_sided_turnover
        gross_return = float(
            (executed_target * asset_returns.loc[return_date, target.index]).sum()
        )
        rows.append(
            {
                "date": return_date,
                "signal_date": signal_date,
                "gross_return": gross_return,
                "net_return": gross_return - cost,
                "cost": cost,
                "two_sided_turnover": two_sided_turnover,
                "one_way_turnover": two_sided_turnover / 2,
                "orders": int((changes.abs() > 1e-10).sum()),
                "target_changed": not skip_rebalance,
                "rebalance_skipped": skip_rebalance,
            }
        )
        previous_target = executed_target

    return pd.DataFrame(rows).set_index("date")


def simulate_buy_and_hold(
    weights: dict[str, float],
    asset_returns: pd.DataFrame,
    return_dates: pd.DatetimeIndex,
    cost_rate: float,
) -> pd.DataFrame:
    current = pd.Series(weights, dtype=float).reindex(TICKERS, fill_value=0.0)
    rows: list[dict[str, object]] = []
    for index, date in enumerate(return_dates):
        gross_return = float((current * asset_returns.loc[date, current.index]).sum())
        cost = cost_rate if index == 0 else 0.0
        rows.append(
            {
                "date": date,
                "gross_return": gross_return,
                "net_return": gross_return - cost,
                "cost": cost,
                "two_sided_turnover": 1.0 if index == 0 else 0.0,
                "one_way_turnover": 0.5 if index == 0 else 0.0,
                "orders": sum(weight > 0 for weight in weights.values()) if index == 0 else 0,
                "target_changed": index == 0,
            }
        )
        current = current * (1 + asset_returns.loc[date, current.index]) / (1 + gross_return)
    return pd.DataFrame(rows).set_index("date")


def drawdown_details(returns: pd.Series) -> tuple[pd.Series, float, int, int]:
    equity = (1 + returns).cumprod()
    drawdown = equity / equity.cummax() - 1
    max_drawdown = float(drawdown.min())
    longest = 0
    current = 0
    for value in drawdown:
        current = current + 1 if value < 0 else 0
        longest = max(longest, current)

    trough = drawdown.idxmin()
    peak = equity.loc[:trough].idxmax()
    recovered = equity.loc[trough:]
    recovered = recovered[recovered >= equity.loc[peak]]
    recovery = (
        int(returns.index.get_loc(recovered.index[0]) - returns.index.get_loc(peak))
        if not recovered.empty
        else int(len(returns) - 1 - returns.index.get_loc(peak))
    )
    return drawdown, max_drawdown, longest, recovery


def beta_metrics(returns: pd.Series, benchmark: pd.Series) -> dict[str, float | None]:
    aligned = pd.concat([returns, benchmark], axis=1, join="inner").dropna()
    aligned.columns = ["strategy", "benchmark"]
    variance = float(aligned["benchmark"].var(ddof=1))
    beta = float(aligned.cov().iloc[0, 1] / variance) if variance > 0 else None
    alpha = (
        float((aligned["strategy"].mean() - beta * aligned["benchmark"].mean()) * 12)
        if beta is not None
        else None
    )

    def conditional_beta(mask: pd.Series) -> float | None:
        subset = aligned.loc[mask]
        variance_ = float(subset["benchmark"].var(ddof=1))
        if len(subset) < 3 or variance_ <= 0:
            return None
        return float(subset.cov().iloc[0, 1] / variance_)

    return {
        "alpha_annual": alpha,
        "beta": beta,
        "upside_beta": conditional_beta(aligned["benchmark"] > 0),
        "downside_beta": conditional_beta(aligned["benchmark"] < 0),
    }


def sharpe_inference(excess: pd.Series) -> dict[str, float | int | None]:
    excess = excess.dropna()
    standard_deviation = float(excess.std(ddof=1))
    if len(excess) < 3 or standard_deviation <= 0:
        return {"psr_vs_zero": None, "min_track_record_months_95": None}
    sharpe = float(excess.mean() / standard_deviation)
    skewness = float(excess.skew())
    raw_kurtosis = float(excess.kurt() + 3)
    variance_term = 1 - skewness * sharpe + ((raw_kurtosis - 1) / 4) * sharpe**2
    if variance_term <= 0 or sharpe <= 0:
        min_track = None
    else:
        z95 = NormalDist().inv_cdf(0.95)
        min_track = int(math.ceil(1 + variance_term * (z95 / sharpe) ** 2))
    z_score = sharpe * math.sqrt(len(excess) - 1) / math.sqrt(max(variance_term, 1e-12))
    return {
        "psr_vs_zero": float(NormalDist().cdf(z_score)),
        "min_track_record_months_95": min_track,
    }


def pnl_concentration(returns: pd.Series) -> dict[str, float | None]:
    capital = (1 + returns).cumprod().shift(1, fill_value=1.0)
    pnl = capital * returns
    total = float(pnl.sum())
    result: dict[str, float | None] = {}
    for count in (1, 3, 5, 10):
        top_dates = pnl.nlargest(min(count, len(pnl))).index
        result[f"top_{count}_months_pnl_share"] = (
            float(pnl.loc[top_dates].sum() / total) if total > 0 else None
        )
        without = returns.drop(top_dates)
        result[f"cagr_without_top_{count}_months"] = (
            float((1 + without).prod() ** (12 / len(without)) - 1)
            if len(without) > 0 and (1 + without).prod() > 0
            else None
        )
    return result


def performance_metrics(
    simulation: pd.DataFrame,
    shy_returns: pd.Series,
    spy_returns: pd.Series,
    sixty_forty_returns: pd.Series,
) -> dict[str, object]:
    returns = simulation["net_return"].dropna()
    gross = simulation.loc[returns.index, "gross_return"]
    months = len(returns)
    total_growth = float((1 + returns).prod())
    gross_growth = float((1 + gross).prod())
    cagr = float(total_growth ** (12 / months) - 1)
    gross_cagr = float(gross_growth ** (12 / months) - 1)
    volatility = float(returns.std(ddof=1) * math.sqrt(12))
    excess = returns - shy_returns.reindex(returns.index)
    excess_std = float(excess.std(ddof=1))
    sharpe = float(excess.mean() / excess_std * math.sqrt(12)) if excess_std > 0 else None
    downside = np.minimum(returns, 0)
    downside_deviation = float(np.sqrt(np.mean(downside**2)) * math.sqrt(12))
    sortino = float(returns.mean() * 12 / downside_deviation) if downside_deviation > 0 else None
    drawdown, max_drawdown, longest, recovery = drawdown_details(returns)
    ulcer_index = float(np.sqrt(np.mean(np.square(drawdown))))
    shy_growth = float((1 + shy_returns.reindex(returns.index)).prod())
    shy_cagr = float(shy_growth ** (12 / months) - 1)
    upi = float((cagr - shy_cagr) / ulcer_index) if ulcer_index > 0 else None
    d = abs(max_drawdown)
    k50 = float(cagr * (1 - d / (1 - d))) if d < 0.50 and cagr > 0 else 0.0
    k25 = float(cagr * (1 - 2 * d / (1 - 2 * d))) if d < 0.25 and cagr > 0 else 0.0

    def tail_metrics(level: float) -> tuple[float, float]:
        quantile = float(returns.quantile(1 - level))
        tail = returns[returns <= quantile]
        return -quantile, float(-tail.mean())

    var95, cvar95 = tail_metrics(0.95)
    var99, cvar99 = tail_metrics(0.99)
    inference = sharpe_inference(excess)
    result: dict[str, object] = {
        "months": months,
        "start": returns.index[0].date().isoformat(),
        "end": returns.index[-1].date().isoformat(),
        "total_return": total_growth - 1,
        "cagr": cagr,
        "gross_cagr": gross_cagr,
        "gross_net_cagr_spread": gross_cagr - cagr,
        "annualized_arithmetic_mean": float(returns.mean() * 12),
        "annualized_volatility": volatility,
        "sharpe": sharpe,
        "sortino": sortino,
        "calmar": float(cagr / d) if d > 0 else None,
        "maximum_drawdown": max_drawdown,
        "longest_underwater_months": longest,
        "recovery_months_from_pre_trough_peak": recovery,
        "monthly_var_95": var95,
        "monthly_cvar_95": cvar95,
        "monthly_var_99": var99,
        "monthly_cvar_99": cvar99,
        "ulcer_index": ulcer_index,
        "upi": upi,
        "k50": k50,
        "k25": k25,
        "skewness": float(returns.skew()),
        "excess_kurtosis": float(returns.kurt()),
        "lag1_autocorrelation": float(returns.autocorr(1)),
        "total_cost": float(simulation.loc[returns.index, "cost"].sum()),
        "annual_one_way_turnover": float(
            simulation.loc[returns.index, "one_way_turnover"].sum() * 12 / months
        ),
        "annual_two_sided_turnover": float(
            simulation.loc[returns.index, "two_sided_turnover"].sum() * 12 / months
        ),
        "orders": int(simulation.loc[returns.index, "orders"].sum()),
        "months_target_changed": int(simulation.loc[returns.index, "target_changed"].sum()),
        **inference,
        **pnl_concentration(returns),
        "vs_spy": beta_metrics(returns, spy_returns.reindex(returns.index)),
        "vs_sixty_forty": beta_metrics(
            returns, sixty_forty_returns.reindex(returns.index)
        ),
    }
    return result


def add_deflated_sharpe(
    variant_metrics: dict[str, dict[str, dict[str, object]]], period: str
) -> None:
    sharpes = [
        float(periods[period]["sharpe"])
        for periods in variant_metrics.values()
        if periods[period]["sharpe"] is not None
    ]
    if len(sharpes) < 2:
        benchmark = 0.0
    else:
        sigma = float(np.std(np.array(sharpes) / math.sqrt(12), ddof=1))
        trials = len(sharpes)
        euler_gamma = 0.5772156649015329
        benchmark = sigma * (
            (1 - euler_gamma) * NormalDist().inv_cdf(1 - 1 / trials)
            + euler_gamma * NormalDist().inv_cdf(1 - 1 / (trials * math.e))
        )
    for periods in variant_metrics.values():
        observed = periods[period]["sharpe"]
        months = int(periods[period]["months"])
        if observed is None or months < 3:
            periods[period]["dsr"] = None
            continue
        monthly_sharpe = float(observed) / math.sqrt(12)
        z_score = (monthly_sharpe - benchmark) * math.sqrt(months - 1)
        periods[period]["dsr"] = float(NormalDist().cdf(z_score))


def audit_data(daily: pd.DataFrame, monthly: pd.DataFrame, digest: str) -> dict[str, object]:
    first_dates = {
        ticker: daily[ticker].first_valid_index().date().isoformat() for ticker in TICKERS
    }
    last_dates = {
        ticker: daily[ticker].last_valid_index().date().isoformat() for ticker in TICKERS
    }
    post_inception_missing = {}
    for ticker in TICKERS:
        series = daily[ticker]
        valid = series.loc[series.first_valid_index() : series.last_valid_index()]
        post_inception_missing[ticker] = int(valid.isna().sum())
    return {
        "provider": "Yahoo Finance via yfinance",
        "field": "Adj Close",
        "daily_rows": len(daily),
        "monthly_completed_rows": len(monthly),
        "duplicate_dates": int(daily.index.duplicated().sum()),
        "dates_monotonic": bool(daily.index.is_monotonic_increasing),
        "first_dates": first_dates,
        "last_dates": last_dates,
        "post_inception_missing_daily_rows": post_inception_missing,
        "cache_sha256": digest,
    }


def period_slice(frame: pd.DataFrame, period: str) -> pd.DataFrame:
    if period == "development":
        return frame.loc[:"2018-12-31"]
    if period == "test":
        return frame.loc["2019-01-01":]
    return frame


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache-only", action="store_true")
    args = parser.parse_args()

    now = pd.Timestamp.now(tz="UTC").tz_localize(None)
    daily, digest = load_prices(args.cache_only)
    monthly = completed_monthly_prices(daily, now)
    asset_returns = monthly.pct_change(fill_method=None)

    targets_by_variant: dict[str, pd.DataFrame] = {}
    meta_by_variant: dict[str, pd.DataFrame] = {}
    simulations: dict[str, dict[str, pd.DataFrame]] = {}
    for sma_months in (10, 9, 11):
        name = f"sma_{sma_months}"
        targets, meta = build_targets(monthly, sma_months)
        targets_by_variant[name] = targets
        meta_by_variant[name] = meta
        simulations[name] = {
            "base_cost": simulate(targets, asset_returns, 0.001),
            "high_cost": simulate(targets, asset_returns, 0.002),
        }

    baseline_dates = simulations["sma_10"]["base_cost"].index
    fixed_6040_targets = pd.DataFrame(
        [{ticker: 0.60 if ticker == "SPY" else 0.40 if ticker == "IEF" else 0.0 for ticker in TICKERS}]
        * len(targets_by_variant["sma_10"]),
        index=targets_by_variant["sma_10"].index,
    )
    sixty_forty = simulate(fixed_6040_targets, asset_returns, 0.001)
    strategic = simulate_buy_and_hold(
        STRATEGIC_WEIGHTS, asset_returns, baseline_dates, 0.001
    )
    spy = simulate_buy_and_hold({"SPY": 1.0}, asset_returns, baseline_dates, 0.001)
    shy_returns = asset_returns["SHY"]

    variant_metrics: dict[str, dict[str, dict[str, object]]] = {}
    for variant, costs in simulations.items():
        variant_metrics[variant] = {}
        for period in ("development", "test", "full"):
            frame = period_slice(costs["base_cost"], period)
            metrics = performance_metrics(
                frame,
                shy_returns,
                spy["net_return"],
                sixty_forty["net_return"],
            )
            high_cost_metrics = performance_metrics(
                period_slice(costs["high_cost"], period),
                shy_returns,
                spy["net_return"],
                sixty_forty["net_return"],
            )
            metrics["high_cost_cagr"] = high_cost_metrics["cagr"]
            metrics["high_cost_maximum_drawdown"] = high_cost_metrics[
                "maximum_drawdown"
            ]
            meta = meta_by_variant[variant].reindex(frame["signal_date"])
            metrics["average_canary_cf"] = float(meta["canary_cf"].mean())
            metrics["average_total_defensive"] = float(meta["total_defensive"].mean())
            variant_metrics[variant][period] = metrics

    for period in ("development", "test", "full"):
        add_deflated_sharpe(variant_metrics, period)

    benchmark_metrics: dict[str, dict[str, dict[str, object]]] = {}
    for name, frame in {
        "strategic_buy_hold": strategic,
        "sixty_forty": sixty_forty,
        "spy": spy,
    }.items():
        benchmark_metrics[name] = {}
        for period in ("development", "test", "full"):
            benchmark_metrics[name][period] = performance_metrics(
                period_slice(frame, period),
                shy_returns,
                spy["net_return"],
                sixty_forty["net_return"],
            )

    test = variant_metrics["sma_10"]["test"]
    sensitivity_pass = all(
        variant_metrics[name]["test"]["cagr"] > 0
        and variant_metrics[name]["test"]["maximum_drawdown"] >= -0.25
        for name in ("sma_9", "sma_11")
    )
    pass_checks = {
        "test_net_cagr_positive": test["cagr"] > 0,
        "test_sharpe_above_sixty_forty": test["sharpe"]
        > benchmark_metrics["sixty_forty"]["test"]["sharpe"],
        "test_max_drawdown_within_20_percent": test["maximum_drawdown"] >= -0.20,
        "test_drawdown_below_strategic_buy_hold": abs(test["maximum_drawdown"])
        < abs(benchmark_metrics["strategic_buy_hold"]["test"]["maximum_drawdown"]),
        "test_drawdown_below_sixty_forty": abs(test["maximum_drawdown"])
        < abs(benchmark_metrics["sixty_forty"]["test"]["maximum_drawdown"]),
        "sma_9_and_11_sensitivity": sensitivity_pass,
    }
    if all(pass_checks.values()):
        decision = "paper_ready"
    elif test["cagr"] <= 0 and not pass_checks["test_drawdown_below_strategic_buy_hold"]:
        decision = "reject"
    else:
        decision = "revise"

    payload = {
        "strategy_id": "camellia_multilayer_taa",
        "version": 1,
        "run_timestamp_utc": now.isoformat(),
        "trial_count": 3,
        "data_audit": audit_data(daily, monthly, digest),
        "effective_first_signal": targets_by_variant["sma_10"].index[0]
        .date()
        .isoformat(),
        "effective_first_return": baseline_dates[0].date().isoformat(),
        "last_complete_return_month": baseline_dates[-1].date().isoformat(),
        "variants": variant_metrics,
        "benchmarks": benchmark_metrics,
        "pass_checks": pass_checks,
        "decision": decision,
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False),
        encoding="utf-8",
    )
    print(json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
