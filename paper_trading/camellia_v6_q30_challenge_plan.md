# Paper Trade Plan: Camellia v6 + Q30 Growth Shadow

## Approval And Scope

- Owner approval date: `2026-09-18`
- Backtest reports:
  - `reports/camellia_multilayer_taa_v6.md`
  - `reports/camellia_growth_round8_research.md`
- Campaign: Webull Thailand Paper Trading Challenge, US Stock & ETF League
- Campaign period: `2026-09-14 00:00` through `2026-10-12 00:00` Asia/Bangkok
- Starting challenge capital: USD 20,000
- Minimum forward observation after the campaign: continue internal tracking until at least 12 monthly signal cycles are recorded

The Challenge has one simulated account and permits only one league. It cannot hold two independently measurable portfolios. Q30 therefore uses the Challenge account while v6 runs as an internal shadow book with the same USD 20,000 starting NAV and the same observed Bid/Ask timestamps.

Q30 remains a rejected Research candidate and is not strategy v7. Running it in the Challenge is a forward-data experiment, not retroactive promotion.

## API Decision

- Challenge orders cannot be routed through the documented Webull Thailand OpenAPI.
- Challenge terms describe a dedicated USD 20,000 simulated account.
- The official OpenAPI account schema exposes only `CASH` / `INDIVIDUAL_CASH`; no paper, simulated or Challenge account type is documented.
- The official API contains brokerage account order endpoints but no Challenge paper-order endpoint.
- A read-only reconnection attempt on `2026-09-18` did not complete within 30 seconds because the previous token directory was absent. No account payload was printed and no order/preview endpoint was called.

All Challenge orders must be entered manually by the owner in the Webull app. Camellia produces proposals and monitors owner-reported fills only.

## Current Signal And Initial Allocation

- Signal date: `2026-08-31`
- Data snapshot SHA-256: `d172c79deb9ee206ee3c433c26d6cbd28d017c7b4186283a11be41546ce0c75f`
- Canary state: rate warning; VWO positive while BND or TIP is non-positive

### Q30 — Challenge account

| Symbol | Target weight | Target notional |
|:--|--:|--:|
| VTI | 60.0% | USD 12,000 |
| DBC | 12.5% | USD 2,500 |
| EWJ | 10.0% | USD 2,000 |
| IPAC | 10.0% | USD 2,000 |
| SHY | 7.5% | USD 1,500 |

### v6 — Internal shadow book

| Symbol | Target weight | Target notional |
|:--|--:|--:|
| VTI | 40.0% | USD 8,000 |
| SHY | 22.5% | USD 4,500 |
| DBC | 17.5% | USD 3,500 |
| EWJ | 10.0% | USD 2,000 |
| IPAC | 10.0% | USD 2,000 |

The table above is the original signal allocation. The Challenge rejected DBC and IPAC, and subsequently rejected the closer commodity substitutes PDBC, COMT and BCI. It is retained as proposal provenance, not as the executed portfolio. The Challenge accepts whole-share orders only, and its whitelist differs from the Webull Thailand live brokerage universe.

### Executed Q30 Challenge adapter

The execution adapter preserves the Q30 research definition while handling the Challenge whitelist:

- IPAC was replaced by VWO, the next positive Regional `13612W` rank on the `2026-08-31` signal date.
- The unavailable DBC sleeve was represented by equal target notionals in GLD and XLE. This is an execution-only inflation/energy proxy; it does not change Q30 or v6 research definitions.
- A read-only comparison over the stored 2008-2026 sample produced 9.69% CAGR, 0.90 Sharpe, -14.26% maximum drawdown and 3.82x annual one-way turnover, versus 9.33%, 0.86, -15.40% and 3.99x for original Q30. These results justify operational similarity, not strategy promotion.

Owner-confirmed fills on `2026-09-18`:

| Symbol | Quantity | Average fill | Cost | Fill-based weight |
|:--|--:|--:|--:|--:|
| VTI | 32 | USD 374.64 | USD 11,988.48 | 59.94% |
| EWJ | 21 | USD 96.63 | USD 2,029.23 | 10.15% |
| VWO | 33 | USD 59.79 | USD 1,973.07 | 9.87% |
| GLD | 3 | USD 399.30 | USD 1,197.90 | 5.99% |
| XLE | 20 | USD 64.6755 | USD 1,293.51 | 6.47% |
| SHY | 18 | USD 81.28 | USD 1,463.04 | 7.32% |
| Cash | - | - | USD 54.77 | 0.27% |

Total invested capital is USD 19,945.23. The individual XLE child fills remain in `paper_trading/ledger.csv`; the aggregate fill record is `paper_trading/q30_challenge_fills_2026-09-18.json`.

## Manual Execution Workflow

1. Owner joins the US Stock & ETF League; this choice cannot be changed later.
2. Owner verifies every proposed symbol inside the Challenge-specific whitelist.
3. Camellia provides whole-share quantities using current displayed Ask prices and leaves a cash buffer.
4. Owner manually submits the paper orders during regular US market hours.
5. Owner provides executed quantities, fill prices and timestamps by screenshot or text.
6. Camellia records only those confirmed fills in `paper_trading/ledger.csv`. The v6 internal shadow remains separate and is not inferred from Challenge substitutes.

Do not mark an order filled from a proposal alone.

## Monitoring

- Recalculate signals after each completed month; apply new weights in the next tradable session.
- Record signal date, Canary state, target weight, proposed notional, owner-confirmed fill, spread estimate, turnover and tracking error.
- Track Q30 and v6 with separate NAVs and ledgers.
- Compare cumulative net return, volatility, drawdown, turnover, realized Sharpe and performance by Canary state.
- Operational review after 6 monthly cycles; strategy review after at least 12 cycles. The four-week Challenge result alone is not enough to promote Q30.

## Stop Conditions

- Risk stop: Q30 drawdown reaches -25% from its shadow or Challenge peak.
- Execution stop: a required symbol becomes ineligible, price data are stale, fills cannot be reconciled, or proposed weights do not sum to 100%.
- Process stop: signal is calculated with an incomplete month, owner fill evidence is missing, or the Challenge resets/changes holdings unexpectedly.
- Strategy review: Q30 Sharpe trails v6 by more than 0.10 after a minimally informative forward sample, turnover exceeds 1.25x v6, or high-cost return becomes persistently negative.

## Prohibited

- No real-money order, deposit, withdrawal or account-permission change.
- No production brokerage order endpoint, including preview/place/replace/cancel.
- No credential or Account ID in the repository, screenshots, reports or chat.
- No automatic promotion of Q30 to v7.
