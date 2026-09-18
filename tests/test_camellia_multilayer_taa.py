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


if __name__ == "__main__":
    unittest.main()
