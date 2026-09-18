# Strategy: Camellia Multi-Layer Tactical Asset Allocation v4

## Identity

- ID: `camellia_multilayer_taa`
- Version: `4`
- Status: `revise`
- Parent baseline: `strategies/camellia_multilayer_taa_v2.md`
- Rejected predecessor: `strategies/camellia_multilayer_taa_v3.md`
- Plan: `experiments/camellia_multilayer_taa_v4_experiment_plan.md`
- Frozen configuration: `experiments/camellia_multilayer_taa_v4_frozen.json`

## Rules Retained From v2

- Monthly signal at close of month `t`; return begins in month `t+1`
- Canary universe: VWO, BND and TIP with weighted `13612W`
- Canary cash fraction: `min(1, weak_count / 2)`
- US equity sleeve 40%: Top 2 of SPY, MDY and IJR by unweighted `13612`
- Other risky sleeves: VEA 20%, DBC 10%, VNQ 10%, IEF 10%, TLT 10%
- Sleeve trend gate disabled
- Whole-portfolio rebalance threshold: 5% one-way turnover
- No leverage and no short positions

## v4 Defensive Policy

The total Defensive budget is divided by economic role:

- 50% remains in SHY
- 25% deflation pocket: IEF when its average `sign(R1), sign(R3), sign(R6), sign(R12)` is positive; otherwise SHY
- 25% inflation pocket: the stronger of GLD and DBC when its multi-lookback score is positive; otherwise SHY

This replaces the v2 winner-take-all selection among SHY, IEF and LQD. DBC can hold both its strategic risky allocation and an inflation-defense allocation in the same month.

## Costs And Data

- Base cost: 0.10% per notional bought or sold
- High-cost stress: 0.20%
- Data field: Yahoo Finance adjusted close
- Frozen data SHA-256: `8a2da5507b8336c5cceb18d54fc67bbb440e1ff765f1dd3c04525958f5b4c82e`
- Effective evaluation: 2008-08 through 2026-08

## Result And Status

Full-period result after base costs:

- CAGR: 6.18%
- Sharpe versus SHY: 0.63
- Maximum drawdown: -12.48%
- Calmar: 0.50
- Annual two-sided turnover: 8.24x
- Longest underwater period: 52 months

Decision: `revise`. v4 materially improves drawdown and turnover versus v2, but it still trails 60/40 on full-period return and Sharpe, performs weakly in the recent equity-led regime, and has no genuinely untouched historical period left for confirmation.
