# Research Report: Camellia Growth Round 8

## Reproduction And Decision Boundary

- Pre-registered plan: `a1110d656aafcdf8dcdf1c8d288b7ee86ae2851a`
- Research runner: `6377f3deb3b9d5fc73a3a32a8b55cef993b49ef5`
- Frozen before recent diagnostic: `dcf4b24d968dab3bdbdf77a1944bbea0dc550a1f`
- Data SHA-256: `d172c79deb9ee206ee3c433c26d6cbd28d017c7b4186283a11be41546ce0c75f`
- Research blocks: 2008-08–2012-12, 2013-01–2018-12 and 2019-01–2022-12
- Recent diagnostic: 2023-01–2026-08
- New trials: Q29–Q32; cumulative declared trial count: 32

Decision: `reject` the Growth candidates and retain Camellia v6 as the active `paper_ready` strategy. No strategy v7 was created because no candidate passed the pre-registered Research rules.

## Questions

- Q29 retained half of the warned sleeve in a single-warning Canary state.
- Q30 used VTI 60%, Regional 20%, DBC 10% and VNQ 10%, removing IEF/TLT from the strategic Risk-On allocation.
- Q31 replaced 20% VTI with the strongest positive-momentum sector only in the no-warning state.
- Q32 used 1.20x exposure only in the no-warning state, charging SHY plus a 2% annual financing spread and SHY plus 4% in the stress case.

Q31 differs from the rejected Q13: Q13 replaced the full 40% US sleeve with Top 3 sectors, while Q31 used one 20% satellite only when all Canaries were healthy.

## Research Results

Median values are across the three Research blocks.

| Candidate | Median CAGR | Sharpe | Risk-matched CAGR | Worst MDD | Upside / downside beta | Turnover | Result |
|:--|--:|--:|--:|--:|--:|--:|:--|
| v6 reference | 8.17% | 0.99 | 8.17% | -12.12% | 0.208 / 0.108 | 7.63x | Reference |
| Q29: partial cuts | 7.58% | 0.82 | 6.82% | -13.18% | 0.225 / 0.221 | 6.55x | Rejected |
| Q30: aggressive Risk-On | 9.54% | 0.92 | 7.65% | -13.93% | 0.263 / 0.136 | 8.30x | Rejected: risk-matched guardrail |
| Q31: sector satellite | 7.64% | 0.90 | 7.42% | -12.96% | 0.242 / 0.125 | 8.53x | Rejected |
| Q32: conditional 1.20x | 8.51% | 0.96 | 7.93% | -12.71% | 0.207 / 0.096 | 9.12x | Rejected |

Q29 weakened both return and efficiency despite lower turnover. Q31 repeated the broad lesson from Q13 at smaller scale: sector selection added turnover without enough net return. Q32 retained efficiency reasonably well but added only 0.34 percentage points of median CAGR, below the required 1.00 point, and did not improve upside beta.

Q30 was the closest candidate. It passed every rule except risk-matched CAGR, which was 7.65% versus v6 at 8.17%, worse by 0.52 percentage points and outside the allowed 0.25-point deterioration.

## Q30 By Research Block

| Block | v6 CAGR | Q30 CAGR | Q30 high-cost CAGR | Q30 Sharpe | Q30 risk-matched CAGR | Q30 MDD |
|:--|--:|--:|--:|--:|--:|--:|
| 2008–2012 | 12.12% | 14.29% | 13.61% | 0.98 | 11.45% | -10.84% |
| 2013–2018 | 3.67% | 5.29% | 4.42% | 0.77 | 4.50% | -9.76% |
| 2019–2022 | 8.17% | 9.54% | 8.62% | 0.92 | 7.65% | -13.93% |

Q30 raised raw CAGR in every Research block and stayed well inside the -25% loss ceiling. The rejection is not because the strategy lost money or breached downside limits; it is because its incremental return was not efficient enough after matching v6's volatility under the rule declared before seeing results.

## Post-Freeze Diagnostics

These values were not used for selection.

### Full period: 2008-08–2026-08

| Candidate | CAGR | High-cost CAGR | Sharpe | Risk-matched CAGR | Volatility | MDD | Turnover |
|:--|--:|--:|--:|--:|--:|--:|--:|
| v6 | 7.50% | 6.67% | 0.83 | 7.50% | 7.42% | -14.44% | 7.79x |
| Q29 | 7.52% | 6.80% | 0.78 | 7.15% | 7.93% | -15.50% | 6.77x |
| Q30 | 9.33% | 8.47% | 0.86 | 7.87% | 9.17% | -15.40% | 7.98x |
| Q31 | 6.61% | 5.61% | 0.71 | 6.60% | 7.43% | -14.82% | 9.44x |
| Q32 | 7.87% | 6.66% | 0.78 | 7.18% | 8.35% | -16.04% | 9.52x |

### Recent diagnostic: 2023-01–2026-08

| Candidate | CAGR | High-cost CAGR | Sharpe | MDD | Turnover |
|:--|--:|--:|--:|--:|--:|
| v6 | 7.69% | 6.68% | 0.60 | -5.51% | 9.50x |
| Q29 | 8.20% | 7.26% | 0.67 | -5.18% | 8.81x |
| Q30 | 9.99% | 8.99% | 0.83 | -7.24% | 9.24x |
| Q31 | 7.88% | 6.65% | 0.59 | -8.09% | 11.56x |
| Q32 | 7.08% | 5.59% | 0.45 | -7.79% | 11.57x |

Q30 looks attractive in the already exposed full/recent data. Promoting it after seeing these values would violate the freeze and would turn the recent diagnostic into an optimization period.

## Broker And Implementation Boundary

- Q29 and Q30 use only the existing v6 asset set.
- Sector ETFs in Q31 have price history in the frozen dataset but do not have recorded Webull Thailand tradability/fractional confirmation in this repo.
- Q32 is a theoretical financed portfolio. Margin availability and actual borrowing rates on the owner's Webull account were not checked.
- No credential, account API, preview or order endpoint was accessed.

## Final Decision And Forward Use

- Research round 8: `reject`
- Active strategy: Camellia v6, status `paper_ready`
- Strategy v7: not created
- Broker action: none

Q30 may be recorded as a zero-allocation shadow signal next to v6 during paper trading. Forward observations can show whether its higher equity exposure continues to add return efficiently without retroactively changing the frozen Research decision. It must not be represented as an accepted v7 until new evidence and a separately pre-registered decision rule support promotion.
