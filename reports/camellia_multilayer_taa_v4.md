# Backtest Report: camellia_multilayer_taa v4

## Reproduction And Evidence Boundary

- Pre-registered plan: `e54dfaf032325fc717316bc110e9b1a571abb25d`
- Runner: `677deb3d37bd5f09814264e117538e6ae95c1168`
- Frozen before recent diagnostic: `0e83f3dac699cfc172a4dff7d322eb6183544458`
- Data SHA-256: `8a2da5507b8336c5cceb18d54fc67bbb440e1ff765f1dd3c04525958f5b4c82e`
- Research blocks: 2008-08–2012-12, 2013-01–2018-12 and 2019-01–2022-12
- Recent diagnostic: 2023-01–2026-08
- Trials: five isolated questions plus one frozen candidate

The recent period is not an untouched holdout because v1–v3 results from the same years were already known. The best possible decision for this round was therefore `revise`, not `paper_ready`.

## Attribution Before v4

Median values across the three Research blocks:

| Component set | CAGR | Calmar | Median MDD | Downside beta vs SPY | Turnover |
|:--|--:|--:|--:|--:|--:|
| v2 | 4.65% | 0.97 | -13.05% | 0.15 | 8.43x |
| No Canary | 4.61% | 0.38 | -20.77% | 0.87 | 1.55x |
| Fixed SPY instead of size rotation | 5.71% | 1.01 | -12.68% | 0.16 | 8.28x |
| SHY-only defense | 3.87% | 0.98 | -10.21% | 0.10 | 6.60x |
| Strategic buy-and-hold | 7.08% | 0.37 | -24.26% | 0.87 | 0.00x |

The Canary module provides real downside protection. The ranked bond defense adds return but also drawdown. The market-cap rotation did not beat the simpler fixed-SPY attribution, so its complexity remains unproven.

## Five Experiments

| Question | Median CAGR | Calmar | Median / worst MDD | Downside beta | Turnover | Result |
|:--|--:|--:|--:|--:|--:|:--|
| v2 reference | 4.65% | 0.97 | -13.05% / -14.82% | 0.15 | 8.43x | Reference |
| Q11: 70% core + 30% tactical | 7.18% | 0.40 | -18.15% / -29.35% | 0.63 | 2.52x | Rejected: return rose but protection deteriorated materially |
| Q12: continuous multi-lookback trend | 4.35% | 0.45 | -9.51% / -16.34% | 0.17 | 7.95x | Rejected: drawdown improved, but return quality and concentration did not |
| Q13: sector momentum | 3.83% | 0.96 | -12.82% / -14.82% | 0.10 | 10.06x | Rejected: lower return and higher turnover |
| Q14: inflation/deflation defense | 6.36% | 0.99 | -9.23% / -9.54% | 0.09 | 6.51x | Passed five of six improvement dimensions |
| Q15: cost-aware execution | 4.64% | 0.97 | -13.08% / -14.82% | 0.15 | 8.43x | Rejected: 15% trigger did not reduce median turnover |

Q14 was the only accepted experiment and became frozen v4. Its Research-block results were:

| Block | CAGR | Sharpe | MDD | Calmar | High-cost CAGR |
|:--|--:|--:|--:|--:|--:|
| 2008–2012 | 10.80% | 0.83 | -9.54% | 1.13 | 10.10% |
| 2013–2018 | 3.80% | 0.77 | -3.85% | 0.99 | 2.80% |
| 2019–2022 | 6.36% | 0.76 | -9.23% | 0.69 | 5.68% |

## Frozen v4 Evaluation

### Full period: 2008-08–2026-08

| Metric | v2 | v4 | 60/40 | SPY |
|:--|--:|--:|--:|--:|
| CAGR | 6.15% | 6.18% | 8.84% | 12.49% |
| Annual volatility | 7.84% | 7.71% | 9.66% | 15.61% |
| Sharpe | 0.62 | 0.63 | 0.78 | 0.73 |
| Maximum drawdown | -19.76% | -12.48% | -25.07% | -41.80% |
| Calmar | 0.31 | 0.50 | 0.35 | 0.30 |
| Longest underwater period | 60 months | 52 months | 25 months | 27 months |
| Annual two-sided turnover | 10.13x | 8.24x | — | — |
| High-cost CAGR | 5.08% | 5.31% | — | — |

v4 keeps approximately the same CAGR as v2 while reducing maximum drawdown by 7.28 percentage points, reducing turnover by 18.7%, improving Calmar, and shortening the longest underwater period by eight months. It still trails 60/40 in CAGR and Sharpe and remains underwater much longer.

### Recent diagnostic: 2023-01–2026-08

| Metric | v2 | v4 | 60/40 | SPY |
|:--|--:|--:|--:|--:|
| CAGR | 2.77% | 4.49% | 14.22% | 22.39% |
| Annual volatility | 7.35% | 7.63% | 9.19% | 12.60% |
| Sharpe | -0.11 | 0.14 | 1.18 | 1.42 |
| Maximum drawdown | -10.50% | -10.70% | -7.28% | -8.33% |
| Calmar | 0.26 | 0.42 | 1.95 | 2.69 |

v4 improves return and Sharpe versus v2 but does not improve recent drawdown. It substantially lags both benchmarks during the equity-led regime. The five best months produced 109.14% of cumulative recent PnL; removing them turns CAGR negative at -0.58%.

## Safety Checks And Decision

All frozen safety checks passed:

- Recent net CAGR is positive
- Recent maximum drawdown is above -30%
- Recent high-cost CAGR is positive at 3.45%
- Recent downside beta versus SPY is below one at 0.60

Decision: `revise`

v4 is a real improvement over Camellia's prior defensive architecture, especially across the full period, but it is not yet a complete high-quality standalone system. Its main remaining weakness is upside participation: it protects long crises better while recovering too slowly and missing too much of strong equity regimes.

The next research priority should be the return engine, not another Defensive parameter. Attribution suggests testing removal of market-cap rotation in favor of a simpler SPY sleeve, while retaining the v4 Defensive policy. That question must be pre-registered as a new round rather than selected retroactively from this attribution.
