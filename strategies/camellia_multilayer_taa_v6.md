# Strategy: Camellia Multi-Layer Tactical Asset Allocation v6

## Identity

- ID: `camellia_multilayer_taa`
- Version: `6`
- Status: `paper_ready`
- Parent baseline: `strategies/camellia_multilayer_taa_v5.md`
- Research plan: `experiments/camellia_multilayer_taa_round7_experiment_plan.md`
- Frozen configuration: `experiments/camellia_multilayer_taa_v6_frozen_round7.json`

## Monthly Rules

- Calculate signals at the close of month `t`; portfolio weights receive returns from month `t+1`.
- Canary universe: VWO, BND and TIP using weighted `13612W` momentum.
- Treat VWO as the equity-risk warning. Treat either BND or TIP at or below zero as a rate-sensitive warning.
- Apply the Canary response by warning type:
  - No warning: open all Risky sleeves.
  - VWO-only warning: close VTI and Regional equity; keep DBC, VNQ, IEF and TLT.
  - BND/TIP warning while VWO remains positive: close VNQ, IEF and TLT; keep VTI, Regional equity and DBC.
  - VWO warning together with a BND/TIP warning: close all Risky sleeves and allocate 100% through the Defensive policy.
- Open Risky sleeves use these strategic weights:
  - 40% fixed VTI.
  - 20% Regional equity: rank VGK, EWJ, IPAC and VWO by `13612W`; allocate 10% to each of at most two assets with positive momentum.
  - 10% DBC, 10% VNQ, 10% IEF and 10% TLT.
- Any closed sleeve and each unused 10% Regional allocation move into the Defensive budget.
- An ETF enters the Regional ranking only after it has a full 12-month signal history. No proxy or pre-inception backfill is used.
- Whole-portfolio rebalance threshold: 5% one-way turnover.
- No leverage and no short positions.

## Defensive Policy

- 50% SHY.
- 25% deflation pocket: IEF when its average `sign(R1), sign(R3), sign(R6), sign(R12)` is positive; otherwise SHY.
- 25% inflation pocket: the stronger of GLD and DBC when its multi-lookback score is positive; otherwise SHY.

## Execution Universe And Costs

- Execution assets are unchanged from v5: VTI, VGK, EWJ, IPAC, VWO, DBC, VNQ, IEF, TLT, SHY and GLD.
- Backtest prices: Yahoo Finance adjusted close.
- Base cost: 0.10% per notional bought or sold.
- High-cost stress: 0.20% per notional bought or sold.
- Frozen data SHA-256: `d172c79deb9ee206ee3c433c26d6cbd28d017c7b4186283a11be41546ce0c75f`.
- Effective evaluation: 2008-08 through 2026-08.

No Webull credential, account API, preview endpoint or order endpoint was used to create or evaluate v6.

## Result And Status

Full-period result after base costs:

- CAGR: 7.50%
- Annual volatility: 7.42%
- Sharpe versus SHY: 0.83
- Sortino: 1.86
- Maximum drawdown: -14.44%
- Calmar: 0.52
- Longest underwater period: 47 months
- Annual two-sided turnover: 7.79x
- High-cost CAGR: 6.67%
- Risk-matched CAGR at v5 volatility: 7.13%

Decision: `paper_ready`. This means the frozen rules are ready for the owner to consider a separately approved paper-trading plan. It does not authorize credential access, broker connection, order preview or any live order.
