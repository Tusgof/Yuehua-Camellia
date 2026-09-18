# Backtest Report: camellia_multilayer_taa v3

## Reproduction

- Pre-registered plan: `b1d63f9e3c32931d455258d472f2fb98549da038`
- Runner: `a13e6aa9d17c52bb833686fe7d243659d00302b0`
- Frozen before recent holdout: `8c828cc869c846af4bfd4cd262b34f9ee4370a2c`
- Research blocks: 2008–2012, 2013–2018, 2019–2022
- Recent holdout: 2023-01 ถึง 2026-08
- Search count: 5 isolated questions plus one frozen candidate

## Five Questions

| Question | Median Research CAGR / Sharpe | Recent CAGR / Sharpe / MDD | Answer |
|:--|--:|--:|:--|
| Q6: softer Canary `CF=min(2/3,b/3)` | 5.41% / 0.71 | 5.88% / 0.32 / -8.61% | เพิ่ม CAGR บางช่วงแต่ median Sharpe ต่ำกว่า v2 จึงไม่ผ่าน |
| Q7: retain 50% เมื่อใต้ SMA10 | 4.65% / 0.95 | 2.46% / -0.17 / -10.07% | Sharpe Research ดีขึ้นแต่ CAGR ไม่ดีขึ้น และ recent ล้มเหลว |
| Q8: cross-asset Top 4 | 4.24% / 0.71 | 1.77% / -0.22 / -14.25% | ไม่สนับสนุน relative-momentum allocation รูปนี้ |
| Q9: Defensive 50% SHY + 50% winner | 4.28% / 0.89 | 3.00% / -0.08 / -10.50% | ลดความเสี่ยงบางส่วนแต่ไม่เพิ่ม CAGR/Sharpe |
| Q10: target vol 15%, cap 2x | 8.63% / 0.90 | 1.97% / -0.08 / -18.79% | เพิ่ม CAGR ในบาง Research blocks แต่ leverage ขยาย signal ที่อ่อนใน recent regime |

## Why Q10 Became v3

Q10 เป็นข้อเดียวที่ผ่านกฎ Research ที่ตรึงไว้: median CAGR สูงกว่า v2, median Sharpe ไม่ลดเกิน 0.05, ทุก block CAGR เป็นบวก และ drawdown ไม่เกิน 30%

ผลแต่ละ Research block แสดงความไม่สม่ำเสมออยู่แล้ว:

| Block | CAGR | Sharpe | MDD |
|:--|--:|--:|--:|
| 2008–2012 | 16.55% | 1.09 | -13.05% |
| 2013–2018 | 8.63% | 0.90 | -10.47% |
| 2019–2022 | 4.90% | 0.37 | -24.27% |

## Frozen v3 Result

| Metric | Recent holdout | Full 2008–2026 |
|:--|--:|--:|
| CAGR | 1.97% | 8.27% |
| Sharpe | -0.08 | 0.59 |
| Maximum drawdown | -18.79% | -37.60% |
| Annual volatility | 13.09% | 12.25% |
| Average leverage | 1.90x | 1.80x |
| Maximum leverage | 2.00x | 2.00x |
| Annual two-sided turnover | 21.70x | 18.54x |
| High-cost CAGR | -0.26% | 6.29% |

## Comparison With v2 In Recent Holdout

v2 แบบไม่ใช้ leverage ให้ CAGR 2.77%, Sharpe -0.11 และ MDD -10.50% v3 ไม่ได้เพิ่ม CAGR แต่เพิ่ม drawdown, volatility และ turnover เกือบสองเท่า

Q6 ทำผลงาน recent ดีที่สุดในห้าข้อ แต่ถูกคัดออกตาม Research rule จึงไม่ถูกนำมาแทน v3 หลังเห็นผล การเปิดเผยผลนี้เป็นหลักฐานเพิ่มเติมว่าพารามิเตอร์ Canary เปลี่ยนพฤติกรรมตาม regime

## Decision

Decision: `reject`

เป้าหมาย CAGR 15–20% / Sharpe >1 ไม่สำเร็จ ต้นเหตุไม่ใช่ leverage ต่ำ แต่คือ signal edge ไม่สม่ำเสมอ การเพิ่ม leverage ก่อนแก้ edge ทำให้ต้นทุนและ drawdownสูงขึ้น

ข้อเสนอคือหยุดเพิ่มพารามิเตอร์ในสถาปัตยกรรมนี้ชั่วคราว คง v2 เป็น baseline สำหรับศึกษา และหาหลักฐานของ return source ที่แข็งแรงกว่าก่อนพยายามเพิ่ม leverageอีกครั้ง

