# Research Report: Camellia Multi-Layer TAA Round v6

## Reproduction And Decision Boundary

- Pre-registered plan: `41cb1fb2903e5a6667faa2e7b5a5109dcf53b2de`
- Research runner: `0895e6c34f7bbe7b45ababfefaec5e0df890d96e`
- Frozen before recent diagnostic: `f71249e6d7692cc55b8aabe9e3c9596894b6f887`
- Data SHA-256: `d172c79deb9ee206ee3c433c26d6cbd28d017c7b4186283a11be41546ce0c75f`
- Research blocks: 2008-08–2012-12, 2013-01–2018-12 and 2019-01–2022-12
- Recent diagnostic: 2023-01–2026-08
- Trials: five isolated candidates; no candidate passed and no combined candidate was formed

Decision: `reject` the v6 modifications and retain v5 as the active `paper_ready` strategy. There is no v6 strategy specification because no rule change was accepted.

## Webull And Data Boundary

The owner confirmed in the Webull Thailand app on 2026-09-18 that DBMF, KMLM and CTA are searchable, tradable and support fractional shares. This is owner-supplied app evidence, not an OpenAPI response, and does not establish `status=OC`, minimum notional, spread or fill quality.

Yahoo Finance adjusted-close data contains 5,209 daily rows and 248 completed monthly rows. DBMF begins 2019-05-08, KMLM 2020-12-02 and CTA 2022-03-08. Each entered the experiment only after 12 months of real history; no proxy backfill was used. No Webull credentials or API endpoints were accessed.

## Research Results

Median values are across the three Research blocks.

| Candidate | Median CAGR | Calmar | Median / worst MDD | Turnover | Improved | Result |
|:--|--:|--:|--:|--:|--:|:--|
| v5 reference | 6.29% | 1.20 | -7.79% / -9.27% | 7.23x | — | Reference |
| Q21: Managed Futures | 6.20% | 1.20 | -7.71% / -7.79% | 7.33x | 1/8 | Rejected: insufficient breadth of improvement |
| Q22: regional equal risk | 6.25% | 1.17 | -7.79% / -9.12% | 7.26x | 0/8 | Rejected |
| Q23: regional rank persistence | 6.09% | 1.39 | -7.79% / -9.50% | 7.02x | 3/8 | Rejected: only three dimensions improved |
| Q24: inflation-defense universe | 4.94% | 1.27 | -7.79% / -10.41% | 7.60x | 4/8 | Rejected: CAGR guardrail failed |
| Q25: Canary horizon consensus | 5.66% | 1.33 | -7.85% / -12.39% | 6.61x | 4/8 | Rejected: CAGR and drawdown guardrails failed |

Q21 has an important evidence limitation: the first two blocks necessarily use v5 because no managed-futures ETF had 12 months of history. Its improvement is concentrated in the late part of block three and therefore cannot satisfy the pre-registered multi-block requirement.

## Post-Freeze Diagnostics

These figures were not used for selection.

| Candidate | Recent CAGR | Sharpe | MDD | Calmar | Full CAGR | Full MDD |
|:--|--:|--:|--:|--:|--:|--:|
| v5 | 5.75% | 0.34 | -8.13% | 0.71 | 6.47% | -11.79% |
| Q21: Managed Futures | 5.51% | 0.33 | -6.52% | 0.85 | 6.40% | -10.11% |
| Q22: regional equal risk | 5.68% | 0.33 | -8.15% | 0.70 | 6.38% | -11.67% |
| Q23: regional rank persistence | 5.78% | 0.35 | -7.99% | 0.72 | 6.64% | -12.01% |
| Q24: inflation defense | 5.62% | 0.32 | -8.23% | 0.68 | 6.43% | -12.89% |
| Q25: Canary consensus | 9.42% | 0.80 | -4.18% | 2.26 | 7.57% | -12.39% |

Q25 is the clearest example of why the freeze matters. Its recent and full-period headline values look attractive only after adding the already exposed 2023–2026 regime, while its Research-block CAGR and worst drawdown failed the rules. It cannot be promoted retroactively.

Q21 reduced drawdown in the recent and full periods but did not improve recent return or Sharpe. Its live history is too short to establish behavior across several independent regimes. DBMF, KMLM and CTA should remain observational candidates rather than enter Camellia's active rules.

## Data-Handling Correction

The simulator now treats a missing return as zero only when the asset weight is exactly zero. It raises an error if an actually held asset has a missing return. This prevents a late-inception ETF with zero weight from contaminating pre-trade weights with `NaN`. Regression tests confirm v6 baseline target weights match v5. The corrected v5 metrics differ from the published v5 values only at rounding noise.

## Final Decision

- v6 research round: `reject`
- Active strategy: Camellia v5
- Active strategy status: `paper_ready`
- Broker action: none

The useful next step is to paper-track Q21 alongside v5 without allocating simulated capital to it as an accepted strategy. This will accumulate forward evidence for Managed Futures while v5 proceeds through its separately approved paper-trading workflow.
