# Strategy: Camellia Multi-Layer Tactical Asset Allocation v5

## Identity

- ID: `camellia_multilayer_taa`
- Version: `5`
- Status: `paper_ready`
- Parent baseline: `strategies/camellia_multilayer_taa_v4.md`
- Plan: `experiments/camellia_multilayer_taa_v5_experiment_plan.md`
- Frozen configuration: `experiments/camellia_multilayer_taa_v5_frozen.json`

## Monthly Rules

- Calculate signals at the close of month `t`; portfolio weights receive returns from month `t+1`.
- Canary universe: VWO, BND and TIP using weighted `13612W` momentum.
- Defensive fraction: `min(1, weak_canary_count / 2)`.
- The remaining Risky budget is allocated as follows:
  - 40% fixed VTI.
  - 20% regional equity sleeve: rank VGK, EWJ, IPAC and VWO by `13612W`; allocate 10% to each of at most two assets with positive momentum.
  - 10% DBC, 10% VNQ, 10% IEF and 10% TLT.
- If fewer than two regional ETFs have positive momentum, move each unused 10% allocation into the Defensive budget.
- An ETF enters the regional ranking only after it has the full 12-month signal history. No proxy or pre-inception backfill is used.
- Whole-portfolio rebalance threshold: 5% one-way turnover.
- No leverage and no short positions.

## Defensive Policy

The Defensive budget retains the v4 policy:

- 50% SHY.
- 25% deflation pocket: IEF when its average `sign(R1), sign(R3), sign(R6), sign(R12)` is positive; otherwise SHY.
- 25% inflation pocket: the stronger of GLD and DBC when its multi-lookback score is positive; otherwise SHY.

## Execution Universe And Costs

- New v5 execution assets verified in the stored Webull Thailand metadata: VTI, VGK, EWJ, IPAC and VWO have `status=OC` and `fractionable=true`.
- Backtest prices: Yahoo Finance adjusted close.
- Base cost: 0.10% per notional bought or sold.
- High-cost stress: 0.20% per notional bought or sold.
- Frozen data SHA-256: `cb90a45a432e09cd52f70e12ce60a0349ff78bce35d76cdb655279a9f586d62c`.
- Effective evaluation: 2008-08 through 2026-08.

No Webull credential, account API, preview endpoint or order endpoint was used to create or evaluate v5.

## Result And Status

Full-period result after base costs:

- CAGR: 6.47%
- Annual volatility: 6.96%
- Sharpe versus SHY: 0.74
- Sortino: 1.67
- Maximum drawdown: -11.79%
- Calmar: 0.55
- Longest underwater period: 36 months
- Annual two-sided turnover: 8.33x
- High-cost CAGR: 5.59%

Decision: `paper_ready`. This means the frozen rules are ready for the owner to consider a separately approved paper-trading plan. It does not authorize credential access, broker connection, order preview or any live order.
