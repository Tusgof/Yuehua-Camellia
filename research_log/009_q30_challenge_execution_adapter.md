# 009 — Q30 Challenge Execution Adapter

## 1. Basic information

- Date: 2026-09-18
- Researcher: Codex under Yuehua Research Lab
- Strategy: Q30 Aggressive Risk-On shadow candidate
- Data: stored Yahoo Finance adjusted-close cache
- Sample: 2008 through August 2026
- Analysis base commit: `daab5a9`

## 2. Problem and hypothesis

The Webull Thailand Paper Trading Challenge rejected DBC, IPAC, PDBC, COMT and BCI. The question was whether a Challenge-only adapter could preserve Q30's regional momentum and inflation-diversifier roles without changing the research strategy.

The structural hypothesis was:

- remove IPAC from the Regional universe and promote the next positive `13612W` rank;
- split the unavailable DBC weight equally between GLD and XLE to retain gold/inflation and energy exposure.

## 3. Method

- Q30 rules, monthly lag, 0.10% transaction cost and 5% rebalance threshold were unchanged.
- Original Q30 was the benchmark.
- The Regional universe excluded IPAC; VWO was the next rank on the live signal date.
- DBC weight was tested as SHY, GLD, XLE, XLB, GLD/XLE, GLD/XLE/XLB and XLE/XLB.
- The equal GLD/XLE mix was selected for its economic interpretation and then checked across the existing chronological research blocks.

## 4. Results

| Configuration | CAGR | Sharpe | Maximum drawdown | Annual one-way turnover |
|:--|--:|--:|--:|--:|
| Original Q30 | 9.33% | 0.86 | -15.40% | 3.99x |
| Challenge adapter | 9.69% | 0.90 | -14.26% | 3.82x |

Monthly net-return correlation with original Q30 was 0.9897. The adapter did not improve every chronological block: its middle block Sharpe was 0.76 versus 0.77 and its third-block CAGR was 9.25% versus 9.54%. It nevertheless remained close to the baseline without a block-level failure.

## 5. Discussion and limitations

GLD plus XLE is not broad commodities. XLE adds equity and company-specific risk, while GLD concentrates the metals exposure in gold. The favorable full-period result must not be used to redefine Q30 after observing the Challenge whitelist. Whole-share rounding and the short competition window also create tracking error.

## 6. Decision

Decision: `continue` as a Challenge execution adapter only.

Original Q30 remains a rejected shadow candidate rather than v7, and v6 remains the accepted `paper_ready` baseline. Internal comparisons must keep original Q30/v6 holdings separate from the Challenge adapter.
