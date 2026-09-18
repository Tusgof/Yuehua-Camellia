from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
SPEC = importlib.util.spec_from_file_location(
    "camellia_backtest", ROOT / "scripts" / "backtest_camellia_multilayer_taa.py"
)
assert SPEC and SPEC.loader
BACKTEST = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BACKTEST)

V4_SPEC = importlib.util.spec_from_file_location(
    "camellia_v4", ROOT / "scripts" / "experiment_camellia_v4.py"
)
assert V4_SPEC and V4_SPEC.loader
V4 = importlib.util.module_from_spec(V4_SPEC)
V4_SPEC.loader.exec_module(V4)

V5_SPEC = importlib.util.spec_from_file_location(
    "camellia_v5", ROOT / "scripts" / "experiment_camellia_v5.py"
)
assert V5_SPEC and V5_SPEC.loader
V5 = importlib.util.module_from_spec(V5_SPEC)
V5_SPEC.loader.exec_module(V5)

V6_SPEC = importlib.util.spec_from_file_location(
    "camellia_v6", ROOT / "scripts" / "experiment_camellia_v6.py"
)
assert V6_SPEC and V6_SPEC.loader
V6 = importlib.util.module_from_spec(V6_SPEC)
V6_SPEC.loader.exec_module(V6)

ROUND7_SPEC = importlib.util.spec_from_file_location(
    "camellia_round7", ROOT / "scripts" / "experiment_camellia_round7.py"
)
assert ROUND7_SPEC and ROUND7_SPEC.loader
ROUND7 = importlib.util.module_from_spec(ROUND7_SPEC)
ROUND7_SPEC.loader.exec_module(ROUND7)


class CamelliaBacktestTests(unittest.TestCase):
    def test_weighted_and_unweighted_momentum_are_distinct(self) -> None:
        index = pd.date_range("2020-01-31", periods=13, freq="ME")
        prices = pd.DataFrame({"SPY": np.arange(100.0, 113.0)}, index=index)
        weighted = BACKTEST.momentum(prices, weighted=True).iloc[-1, 0]
        unweighted = BACKTEST.momentum(prices, weighted=False).iloc[-1, 0]
        self.assertNotAlmostEqual(weighted, unweighted)

    def test_simulation_uses_next_month_return(self) -> None:
        dates = pd.date_range("2020-01-31", periods=3, freq="ME")
        returns = pd.DataFrame(0.0, index=dates, columns=BACKTEST.TICKERS)
        returns.loc[dates[1], "SPY"] = 0.10
        returns.loc[dates[2], "SPY"] = -0.20
        targets = pd.DataFrame(0.0, index=dates[:2], columns=BACKTEST.TICKERS)
        targets["SPY"] = 1.0

        result = BACKTEST.simulate(targets, returns, cost_rate=0.0)

        self.assertEqual(result.index[0], dates[1])
        self.assertAlmostEqual(result.iloc[0]["gross_return"], 0.10)
        self.assertAlmostEqual(result.iloc[1]["gross_return"], -0.20)

    def test_full_switch_charges_both_sides(self) -> None:
        dates = pd.date_range("2020-01-31", periods=3, freq="ME")
        returns = pd.DataFrame(0.0, index=dates, columns=BACKTEST.TICKERS)
        targets = pd.DataFrame(0.0, index=dates[:2], columns=BACKTEST.TICKERS)
        targets.loc[dates[0], "SPY"] = 1.0
        targets.loc[dates[1], "IEF"] = 1.0

        result = BACKTEST.simulate(targets, returns, cost_rate=0.001)

        self.assertAlmostEqual(result.iloc[0]["cost"], 0.001)
        self.assertAlmostEqual(result.iloc[1]["two_sided_turnover"], 2.0)
        self.assertAlmostEqual(result.iloc[1]["cost"], 0.002)

    def test_zero_weight_missing_return_does_not_contaminate_simulation(self) -> None:
        dates = pd.date_range("2024-01-31", periods=3, freq="ME")
        targets = pd.DataFrame(
            {"SPY": [1.0, 1.0], "NEW": [0.0, 0.0]}, index=dates[:2]
        )
        returns = pd.DataFrame(
            {"SPY": [0.01, 0.02, 0.03], "NEW": [np.nan, np.nan, 0.01]}, index=dates
        )
        result = BACKTEST.simulate(targets, returns, cost_rate=0.0)
        self.assertFalse(bool(result["net_return"].isna().any()))
        self.assertAlmostEqual(float(result.iloc[-1]["net_return"]), 0.03)

    def test_rebalance_threshold_skips_small_whole_rebalance(self) -> None:
        dates = pd.date_range("2020-01-31", periods=3, freq="ME")
        returns = pd.DataFrame(0.0, index=dates, columns=BACKTEST.TICKERS)
        targets = pd.DataFrame(0.0, index=dates[:2], columns=BACKTEST.TICKERS)
        targets.loc[dates[0], ["SPY", "IEF"]] = [0.50, 0.50]
        targets.loc[dates[1], ["SPY", "IEF"]] = [0.53, 0.47]

        result = BACKTEST.simulate(
            targets, returns, cost_rate=0.001, rebalance_threshold=0.05
        )

        self.assertTrue(result.iloc[1]["rebalance_skipped"])
        self.assertEqual(result.iloc[1]["cost"], 0.0)

    def test_top_two_us_assets_split_us_sleeve(self) -> None:
        dates = pd.date_range("2018-01-31", periods=25, freq="ME")
        base = np.linspace(100.0, 130.0, len(dates))
        prices = pd.DataFrame(
            {ticker: base * (1 + rank / 1000) for rank, ticker in enumerate(BACKTEST.TICKERS)},
            index=dates,
        )

        targets, meta = BACKTEST.build_targets(prices, 10, us_top_count=2)

        selected = meta.iloc[-1]["us_winners"].split(",")
        self.assertEqual(len(selected), 2)
        self.assertAlmostEqual(targets.iloc[-1][selected].sum(), 0.40)

    def test_completed_month_excludes_current_partial_month(self) -> None:
        index = pd.to_datetime(["2026-08-31", "2026-09-17"])
        prices = pd.DataFrame({"SPY": [100.0, 101.0]}, index=index)

        monthly = BACKTEST.completed_monthly_prices(
            prices, pd.Timestamp("2026-09-18")
        )

        self.assertEqual(list(monthly.index), [pd.Timestamp("2026-08-31")])

    def test_v4_baseline_matches_v2_targets(self) -> None:
        dates = pd.date_range("2016-01-31", periods=30, freq="ME")
        prices = pd.DataFrame(
            {
                ticker: np.linspace(100.0 + rank, 140.0 + rank, len(dates))
                for rank, ticker in enumerate(V4.UNIVERSE)
            },
            index=dates,
        )

        expected, _ = BACKTEST.build_targets(
            prices.loc[:, list(BACKTEST.TICKERS)],
            10,
            trend_gate=False,
            us_top_count=2,
        )
        actual, _ = V4.build_modular_targets(prices)

        pd.testing.assert_frame_equal(
            actual.loc[:, list(BACKTEST.TICKERS)], expected, check_freq=False
        )
        self.assertAlmostEqual(float(actual.loc[:, list(V4.EXTRA_TICKERS)].sum().sum()), 0.0)

    def test_cost_aware_execution_trades_when_canary_risk_rises(self) -> None:
        dates = pd.date_range("2020-01-31", periods=3, freq="ME")
        returns = pd.DataFrame(0.0, index=dates, columns=V4.UNIVERSE)
        targets = pd.DataFrame(0.0, index=dates[:2], columns=V4.UNIVERSE)
        targets.loc[dates[0], ["SPY", "SHY"]] = [0.90, 0.10]
        targets.loc[dates[1], ["SPY", "SHY"]] = [0.80, 0.20]
        meta = pd.DataFrame(
            {"canary_cf": [0.0, 0.5]}, index=dates[:2]
        )

        result = V4.simulate_cost_aware(targets, returns, meta, cost_rate=0.001)

        self.assertTrue(result.iloc[1]["target_changed"])
        self.assertGreater(result.iloc[1]["cost"], 0.0)

    def test_v4_diversified_defense_keeps_half_in_shy(self) -> None:
        dates = pd.date_range("2016-01-31", periods=30, freq="ME")
        prices = pd.DataFrame(
            {
                ticker: np.linspace(100.0 + rank, 140.0 + rank, len(dates))
                for rank, ticker in enumerate(V4.UNIVERSE)
            },
            index=dates,
        )
        prices.loc[:, list(BACKTEST.CANARIES)] = np.linspace(
            140.0, 100.0, len(dates)
        )[:, None]

        targets, meta = V4.build_modular_targets(
            prices, diversified_defense=True
        )
        defensive_budget = float(meta.iloc[-1]["total_defensive"])

        self.assertGreater(defensive_budget, 0.0)
        self.assertGreaterEqual(targets.iloc[-1]["SHY"], 0.5 * defensive_budget)
        self.assertAlmostEqual(float(targets.iloc[-1].sum()), 1.0)

    def test_v5_baseline_matches_v4(self) -> None:
        dates = pd.date_range("2016-01-31", periods=30, freq="ME")
        prices = pd.DataFrame(
            {
                ticker: np.linspace(100.0 + rank, 140.0 + rank, len(dates))
                for rank, ticker in enumerate(V5.UNIVERSE)
            },
            index=dates,
        )

        expected, _ = V4.build_modular_targets(
            prices.loc[:, list(V4.UNIVERSE)], diversified_defense=True
        )
        actual, _ = V5.build_targets(prices)

        pd.testing.assert_frame_equal(
            actual.loc[:, list(V4.UNIVERSE)], expected, check_freq=False
        )
        self.assertAlmostEqual(float(actual.loc[:, list(V5.NEW_TICKERS)].sum().sum()), 0.0)

    def test_v5_fixed_vti_uses_forty_percent_of_risky_budget(self) -> None:
        dates = pd.date_range("2016-01-31", periods=30, freq="ME")
        prices = pd.DataFrame(
            {
                ticker: np.linspace(100.0 + rank, 140.0 + rank, len(dates))
                for rank, ticker in enumerate(V5.UNIVERSE)
            },
            index=dates,
        )

        targets, meta = V5.build_targets(prices, fixed_vti=True)
        risky_budget = 1 - float(meta.iloc[-1]["canary_cf"])

        self.assertAlmostEqual(targets.iloc[-1]["VTI"], 0.40 * risky_budget)
        self.assertAlmostEqual(float(targets.iloc[-1].sum()), 1.0)

    def test_v5_unused_regional_weight_moves_to_defense(self) -> None:
        dates = pd.date_range("2016-01-31", periods=30, freq="ME")
        prices = pd.DataFrame(
            {
                ticker: np.linspace(100.0 + rank, 140.0 + rank, len(dates))
                for rank, ticker in enumerate(V5.UNIVERSE)
            },
            index=dates,
        )
        prices["VWO"] = np.linspace(140.0, 100.0, len(dates))
        prices.loc[:, ["VGK", "EWJ", "IPAC"]] = np.nan

        targets, meta = V5.build_targets(prices, regional_equity=True)
        canary_cf = float(meta.iloc[-1]["canary_cf"])
        risky_budget = 1 - canary_cf

        self.assertEqual(meta.iloc[-1]["regional_winners"], "")
        self.assertAlmostEqual(
            float(meta.iloc[-1]["total_defensive"]), canary_cf + 0.20 * risky_budget
        )
        self.assertAlmostEqual(float(targets.iloc[-1].sum()), 1.0)

    def test_v6_baseline_matches_v5(self) -> None:
        dates = pd.date_range("2016-01-31", periods=30, freq="ME")
        prices = pd.DataFrame(
            {
                ticker: np.linspace(100.0 + rank, 140.0 + rank, len(dates))
                for rank, ticker in enumerate(V6.UNIVERSE)
            },
            index=dates,
        )
        expected, _ = V5.build_targets(prices.loc[:, list(V5.UNIVERSE)], fixed_vti=True, regional_equity=True)
        actual, _ = V6.build_targets(prices)
        pd.testing.assert_frame_equal(actual.loc[:, list(V5.UNIVERSE)], expected, check_freq=False)
        self.assertAlmostEqual(float(actual.loc[:, list(V6.NEW_TICKERS)].sum().sum()), 0.0)

    def test_v6_managed_futures_replaces_ten_percent_of_vti(self) -> None:
        dates = pd.date_range("2016-01-31", periods=30, freq="ME")
        prices = pd.DataFrame(
            {
                ticker: np.linspace(100.0 + rank, 140.0 + rank, len(dates))
                for rank, ticker in enumerate(V6.UNIVERSE)
            },
            index=dates,
        )
        targets, meta = V6.build_targets(prices, managed_futures=True)
        risky_budget = 1 - float(meta.iloc[-1]["canary_cf"])
        self.assertAlmostEqual(targets.iloc[-1]["VTI"], 0.30 * risky_budget)
        self.assertAlmostEqual(
            float(targets.iloc[-1][list(V6.MANAGED_FUTURES)].sum()), 0.10 * risky_budget
        )
        self.assertAlmostEqual(float(targets.iloc[-1].sum()), 1.0)

    def test_v6_equal_risk_regional_weights_are_bounded(self) -> None:
        dates = pd.date_range("2016-01-31", periods=30, freq="ME")
        prices = pd.DataFrame(
            {
                ticker: np.linspace(100.0 + rank, 140.0 + rank, len(dates))
                for rank, ticker in enumerate(V6.UNIVERSE)
            },
            index=dates,
        )
        prices["VGK"] = 100 * np.cumprod(np.tile([1.08, 0.94], 15))
        targets, meta = V6.build_targets(prices, regional_equal_risk=True)
        selected = meta.iloc[-1]["regional_winners"].split(",")
        weights = targets.iloc[-1][selected]
        self.assertAlmostEqual(float(weights.sum()), 0.20)
        self.assertTrue(bool((weights >= 0.05 - 1e-12).all()))
        self.assertTrue(bool((weights <= 0.15 + 1e-12).all()))

    def test_v6_canary_consensus_requires_three_negative_horizons(self) -> None:
        dates = pd.date_range("2016-01-31", periods=30, freq="ME")
        prices = pd.DataFrame(
            {
                ticker: np.linspace(100.0 + rank, 140.0 + rank, len(dates))
                for rank, ticker in enumerate(V6.UNIVERSE)
            },
            index=dates,
        )
        for ticker in V6.bt.CANARIES:
            prices.loc[dates[-1], ticker] = prices.loc[dates[-2], ticker] * 0.99
        _, meta = V6.build_targets(prices, canary_consensus=True)
        self.assertEqual(int(meta.iloc[-1]["weak_canaries"]), 0)

    def _round7_prices(self) -> pd.DataFrame:
        dates = pd.date_range("2016-01-31", periods=30, freq="ME")
        return pd.DataFrame(
            {
                ticker: np.linspace(100.0 + rank, 140.0 + rank, len(dates))
                for rank, ticker in enumerate(ROUND7.UNIVERSE)
            },
            index=dates,
        )

    def test_round7_baseline_matches_v5(self) -> None:
        prices = self._round7_prices()
        expected, _ = V5.build_targets(
            prices.loc[:, list(V5.UNIVERSE)], fixed_vti=True, regional_equity=True
        )
        actual, _ = ROUND7.build_targets(prices)
        pd.testing.assert_frame_equal(
            actual.loc[:, list(V5.UNIVERSE)], expected, check_freq=False
        )

    def test_round7_structural_budget_raises_vti_and_halves_duration(self) -> None:
        prices = self._round7_prices()
        targets, meta = ROUND7.build_targets(prices, structural_risk_budget=True)
        risky_budget = 1 - float(meta.iloc[-1]["canary_cf"])
        self.assertAlmostEqual(float(targets.iloc[-1]["VTI"]), 0.50 * risky_budget)
        self.assertAlmostEqual(float(targets.iloc[-1]["IEF"]), 0.05 * risky_budget)
        self.assertAlmostEqual(float(targets.iloc[-1]["TLT"]), 0.05 * risky_budget)

    def test_round7_selective_rate_warning_keeps_equity_and_cuts_rate_sleeves(self) -> None:
        prices = self._round7_prices()
        prices["TIP"] = np.linspace(140.0, 100.0, len(prices))
        targets, meta = ROUND7.build_targets(prices, selective_canary=True)
        self.assertEqual(meta.iloc[-1]["canary_regime"], "rate_sensitive_cut")
        self.assertAlmostEqual(float(targets.iloc[-1]["VTI"]), 0.40)
        self.assertGreaterEqual(float(meta.iloc[-1]["total_defensive"]), 0.30)

    def test_round7_rejects_combined_candidate_flags(self) -> None:
        with self.assertRaises(ValueError):
            ROUND7.build_targets(
                self._round7_prices(),
                structural_risk_budget=True,
                slower_regional_ranking=True,
            )


if __name__ == "__main__":
    unittest.main()
