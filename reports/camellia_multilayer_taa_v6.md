# Backtest Report: camellia_multilayer_taa v6

## Reproduction And Evidence Boundary

- Pre-registered plan: `0ec56ed0b1fd331a373967e1a113b42220c96889`
- Research runner: `7b96c40e1d1436dd9cc3d4eca4ee851b60d022ec`
- Frozen before recent diagnostic: `f8b156e28a7e6877414fafb17034941e5ad1a420`
- Data SHA-256: `d172c79deb9ee206ee3c433c26d6cbd28d017c7b4186283a11be41546ce0c75f`
- Research blocks: 2008-08–2012-12, 2013-01–2018-12 and 2019-01–2022-12
- Recent diagnostic: 2023-01–2026-08
- New trials: Q26–Q28; cumulative declared trial count: 28

The earlier round named v6 was rejected and did not create a strategy version. This work is research round 7 but produces strategy v6. Selection used only the three Research blocks. The recent period is not an untouched holdout because prior Camellia rounds had already exposed it.

## Selection Process Change

The prior `improve four of eight dimensions` rule was retired because Calmar, Ulcer Index and drawdown rewarded overlapping behavior. The new process first required positive base/high-cost CAGR in every block, maximum drawdown above -20%, limited deterioration in CAGR/upside beta, and caps on turnover and cost drag. A candidate then had to improve both median Sharpe and median risk-matched CAGR versus v5.

Risk-matched CAGR scales monthly excess returns after the fact to the volatility of v5 in the same block. It is a comparison diagnostic, not a tradable leverage rule.

DSR uses a cumulative trial count of 28 and the dispersion of the current candidates to estimate the expected maximum Sharpe. Historical trial-return correlation is unavailable, so DSR should be read as an approximate multiple-testing diagnostic rather than a precise probability.

## Q26–Q28 Research Results

Median values are across the three Research blocks.

| Candidate | Median CAGR | Median Sharpe | Risk-matched CAGR | Worst MDD | Upside beta | Turnover | Result |
|:--|--:|--:|--:|--:|--:|--:|:--|
| v5 reference | 6.29% | 0.86 | 6.29% | -9.27% | 0.156 | 7.23x | Reference |
| Q26: Selective Canary response | 8.17% | 0.99 | 7.42% | -12.12% | 0.208 | 7.63x | Passed |
| Q27: Structural risk budget | 6.56% | 0.82 | 5.78% | -9.71% | 0.205 | 7.34x | Rejected: efficiency tests failed |
| Q28: Slower Regional ranking | 5.98% | 0.87 | 6.04% | -8.95% | 0.149 | 6.88x | Rejected: CAGR and risk-matched tests failed |

Q27 increased raw return and upside participation but did so with lower Sharpe and lower risk-matched CAGR. Q28 reduced turnover and slightly improved median Sharpe, but its return loss exceeded the guardrail.

Q26 passed every pre-registered guardrail and both efficiency tests. It replaces the portfolio-wide Canary fraction with a selective response: VWO warnings close equity, BND/TIP warnings close rate-sensitive sleeves, and warnings from both groups trigger full defense.

## Q26 Results By Research Block

| Research block | v5 CAGR | v6 CAGR | v6 Sharpe | v6 risk-matched CAGR | v6 MDD | v6 high-cost CAGR |
|:--|--:|--:|--:|--:|--:|--:|
| 2008–2012 | 10.24% | 12.12% | 1.06 | 12.32% | -6.22% | 11.50% |
| 2013–2018 | 4.32% | 3.67% | 0.62 | 3.03% | -8.05% | 2.80% |
| 2019–2022 | 6.29% | 8.17% | 0.99 | 7.42% | -12.12% | 7.35% |

The improvement is not uniform. Q26 was materially weaker than v5 in 2013–2018 and accepted deeper drawdown in 2019–2022. Its advantage comes from two of three blocks and higher median efficiency, not domination in every regime.

## Frozen Evaluation

### Full period: 2008-08–2026-08

| Metric | v5 | v6 | Change |
|:--|--:|--:|--:|
| CAGR | 6.47% | 7.50% | +1.03 pp |
| High-cost CAGR | 5.59% | 6.67% | +1.08 pp |
| Annual volatility | 6.96% | 7.42% | +0.46 pp |
| Sharpe | 0.74 | 0.83 | +0.09 |
| Risk-matched CAGR | 6.47% | 7.13% | +0.66 pp |
| Sortino | 1.67 | 1.86 | +0.18 |
| Maximum drawdown | -11.79% | -14.44% | -2.64 pp |
| Calmar | 0.55 | 0.52 | -0.03 |
| Longest underwater period | 36 months | 47 months | +11 months |
| Recovery from pre-trough peak | 37 months | 48 months | +11 months |
| Annual two-sided turnover | 8.33x | 7.79x | -0.54x |
| Top-five-month PnL share | 24.05% | 24.41% | +0.36 pp |
| Approximate DSR, 28 trials | 0.997 | 0.999 | +0.002 |

v6 earns more raw and risk-matched return with lower turnover, but it gives back some of v5's drawdown protection. This is the main tradeoff and should be watched explicitly in paper trading.

### Recent diagnostic: 2023-01–2026-08

| Metric | v5 | v6 | Change |
|:--|--:|--:|--:|
| CAGR | 5.75% | 7.69% | +1.93 pp |
| High-cost CAGR | 4.68% | 6.68% | +2.00 pp |
| Annual volatility | 6.90% | 7.41% | +0.51 pp |
| Sharpe | 0.34 | 0.60 | +0.26 |
| Risk-matched CAGR | 5.75% | 7.43% | +1.68 pp |
| Maximum drawdown | -8.13% | -5.51% | +2.62 pp |
| Calmar | 0.71 | 1.39 | +0.69 |
| Recovery from pre-trough peak | 12 months | 9 months | -3 months |
| Annual two-sided turnover | 10.25x | 9.50x | -0.76x |
| Approximate DSR, 28 trials | 0.567 | 0.735 | +0.167 |

These recent values passed every safety check, but they remain diagnostic rather than independent confirmation.

## Data And Broker Boundary

- The frozen Yahoo Finance adjusted-close snapshot contains 5,209 daily rows and 248 completed monthly rows.
- Dates are monotonic and contain no duplicates. Assets enter a ranking only after 12 months of real history; no proxy history is inserted.
- v6 introduces no new execution asset beyond v5.
- No Webull credential was read and no API, preview or order endpoint was called.

## Decision

Decision: `paper_ready`

Q26 passed the new Research selection process and every recent/full readiness check. Camellia v6 replaces v5 as the active baseline. `paper_ready` permits preparation of a separately approved paper-trading plan only; it does not authorize broker access or any order.
