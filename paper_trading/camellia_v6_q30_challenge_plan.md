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

The owner must first confirm that all five symbols are eligible in the Challenge and whether fractional/notional orders are supported. If only whole shares are allowed, do not approximate quantities silently; calculate them from the displayed Ask prices and leave residual cash.

## Manual Execution Workflow

1. Owner joins the US Stock & ETF League; this choice cannot be changed later.
2. Owner confirms VTI, DBC, EWJ, IPAC and SHY are searchable and eligible inside the Challenge.
3. Camellia provides notional or whole-share quantities using current displayed Ask prices.
4. Owner manually submits the paper orders during regular US market hours.
5. Owner provides executed quantities, fill prices and timestamps by screenshot or text.
6. Camellia records only those confirmed fills in `paper_trading/ledger.csv` and creates the v6 shadow fills from the same timestamp/Bid-Ask observations.

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
