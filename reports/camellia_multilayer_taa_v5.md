# Backtest Report: camellia_multilayer_taa v5

## Reproduction And Evidence Boundary

- Pre-registered plan: `8a2413221f8dd4cecc2a57712d718f2d44c23d3b`
- Runner: `fc5e8abd4701c704a4d656cad3ea1e3187bebf2f`
- Frozen before recent diagnostic: `b58134b2e78aea39be6388a6ea8d41b5316d1dcf`
- Data SHA-256: `cb90a45a432e09cd52f70e12ce60a0349ff78bce35d76cdb655279a9f586d62c`
- Research blocks: 2008-08–2012-12, 2013-01–2018-12 and 2019-01–2022-12
- Recent diagnostic: 2023-01–2026-08
- Trials: six isolated candidates from five questions, followed by one combined frozen candidate

The recent period is a diagnostic rather than an untouched holdout because earlier Camellia versions had already exposed it. Selection used only the three Research blocks. This round evaluates Camellia as a standalone portfolio; 60/40 is not part of the selection or final decision.

## Data Audit And Webull Boundary

- Yahoo Finance adjusted-close snapshot contains 5,209 daily rows and 248 completed monthly rows.
- Dates are monotonic, contain no duplicates and have no missing daily observations after each ETF's inception.
- IPAC, SCHP, GLDM, PDBC and VNQI begin after the backtest start. They entered rankings only after 12 months of actual history; no proxy history was inserted.
- Stored read-only Webull Thailand metadata confirms `status=OC` and `fractionable=true` for VTI, VGK, EWJ, IPAC, VWO, IEF, SCHP, GLDM, PDBC and VNQI.
- No credentials were read and no Webull API, preview or order endpoint was called.

## Q16–Q20 Results

Median values are across the three Research blocks. A candidate also had to pass every guardrail and improve at least four of eight dimensions.

| Candidate | Median CAGR | Calmar | Median / worst MDD | Downside beta vs SPY | Turnover | Improved | Result |
|:--|--:|--:|--:|--:|--:|--:|:--|
| v4 reference | 6.36% | 0.99 | -9.23% / -9.54% | 0.09 | 6.51x | — | Reference |
| Q16: fixed VTI | 6.22% | 1.17 | -8.92% / -9.67% | 0.10 | 6.36x | 4/8 | Passed |
| Q17a: deflation-only defense | 4.06% | 1.11 | -10.42% / -11.81% | 0.10 | 6.39x | 4/8 | Rejected: CAGR guardrail failed |
| Q17b: inflation-only defense | 6.07% | 0.91 | -9.23% / -9.73% | 0.10 | 6.73x | 2/8 | Rejected: insufficient improvement |
| Q18: market-cap rank buffer | 5.88% | 1.07 | -9.30% / -9.54% | 0.09 | 6.35x | 4/8 | Passed, but Q16 had priority |
| Q19: alternative macro sleeve | 5.82% | 1.04 | -7.19% / -9.53% | 0.07 | 7.72x | 4/8 | Rejected: CAGR guardrail failed |
| Q20: regional equity sleeve | 6.38% | 0.78 | -7.79% / -8.92% | 0.05 | 7.38x | 4/8 | Passed |

Q19 is informative despite rejection: alternative macro assets improved drawdown, Ulcer Index, downside beta and PnL concentration, but the return loss was too large. Q17 shows that both defensive pockets contribute; deleting either one did not produce a superior system.

## Frozen v5 Selection

The pre-registered combination rule selected Q16 plus Q20:

- Replace SPY/MDY/IJR rotation with fixed VTI for 40% of the Risky budget.
- Replace fixed VEA with a 20% regional sleeve selecting at most two positive-momentum ETFs from VGK, EWJ, IPAC and VWO.
- Retain v4's DBC, VNQ, IEF and TLT sleeves and its inflation/deflation Defensive policy.

The combined candidate improved four dimensions: Calmar, Ulcer Index, drawdown and top-five-month PnL concentration. It passed every return, drawdown, downside-beta and turnover guardrail.

| Research block | CAGR | Sharpe | MDD | Calmar | High-cost CAGR |
|:--|--:|--:|--:|--:|--:|
| 2008–2012 | 10.24% | 0.86 | -7.79% | 1.32 | 9.54% |
| 2013–2018 | 4.32% | 0.95 | -3.62% | 1.20 | 3.36% |
| 2019–2022 | 6.29% | 0.83 | -9.27% | 0.68 | 5.53% |

## Frozen Evaluation

### Full period: 2008-08–2026-08

| Metric | v4 | v5 | Change |
|:--|--:|--:|--:|
| CAGR | 6.18% | 6.47% | +0.29 pp |
| Annual volatility | 7.71% | 6.96% | -0.74 pp |
| Sharpe | 0.63 | 0.74 | +0.11 |
| Sortino | 1.39 | 1.67 | +0.28 |
| Maximum drawdown | -12.48% | -11.79% | +0.68 pp |
| Calmar | 0.50 | 0.55 | +0.05 |
| Longest underwater period | 52 months | 36 months | -16 months |
| Recovery from pre-trough peak | 53 months | 37 months | -16 months |
| Annual two-sided turnover | 8.24x | 8.33x | +0.09x |
| High-cost CAGR | 5.31% | 5.59% | +0.28 pp |
| Top-five-month PnL share | 28.47% | 24.05% | -4.42 pp |

v5 improves return quality and recovery while keeping turnover nearly unchanged. Its full-period DSR is 0.997 and high-cost CAGR remains positive.

### Recent diagnostic: 2023-01–2026-08

| Metric | v4 | v5 | Change |
|:--|--:|--:|--:|
| CAGR | 4.49% | 5.75% | +1.26 pp |
| Annual volatility | 7.63% | 6.90% | -0.73 pp |
| Sharpe | 0.14 | 0.34 | +0.21 |
| Sortino | 0.91 | 1.30 | +0.39 |
| Maximum drawdown | -10.70% | -8.13% | +2.57 pp |
| Calmar | 0.42 | 0.71 | +0.29 |
| Recovery from pre-trough peak | 14 months | 12 months | -2 months |
| Annual two-sided turnover | 10.00x | 10.25x | +0.25x |
| High-cost CAGR | 3.45% | 4.68% | +1.22 pp |
| Top-five-month PnL share | 109.14% | 75.63% | -33.51 pp |

The recent result passes all safety checks. It is still not independent evidence, and recent Sharpe remains modest, but the gain is less concentrated and the drawdown is shallower than v4.

## Decision

Decision: `paper_ready`

All recent-safety and full-period readiness checks passed. This status permits preparation of a separately approved paper-trading plan only. The next milestone should build an offline signal/order proposal and a read-only Webull validation path with explicit position limits and stop conditions. It must not access credentials or submit orders without new owner authorization.
