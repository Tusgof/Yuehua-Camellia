from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "camellia_backtest", ROOT / "scripts" / "backtest_camellia_multilayer_taa.py"
)
assert SPEC and SPEC.loader
BACKTEST = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BACKTEST)


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

    def test_completed_month_excludes_current_partial_month(self) -> None:
        index = pd.to_datetime(["2026-08-31", "2026-09-17"])
        prices = pd.DataFrame({"SPY": [100.0, 101.0]}, index=index)

        monthly = BACKTEST.completed_monthly_prices(
            prices, pd.Timestamp("2026-09-18")
        )

        self.assertEqual(list(monthly.index), [pd.Timestamp("2026-08-31")])


if __name__ == "__main__":
    unittest.main()
