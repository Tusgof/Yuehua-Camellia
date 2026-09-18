# Backtest Report: camellia_multilayer_taa v1

## Reproduction

- Evidence type: historical ETF backtest
- Producing code commit: `c64a95b31e008d91873130f3314d79ec803f701d`
- Strategy spec: `strategies/camellia_multilayer_taa.md`
- Data: Yahoo Finance `Adj Close` ผ่าน yfinance 1.2.0
- Data cache SHA-256: `9ca48d680c4c5da36c3e061c02a990840a478150ca68407b1f6a9d22998b61d1`
- Run timestamp: `2026-09-18T10:00:18.106073Z`
- Effective first signal/return: `2008-04-30` / `2008-05-31`
- Last complete return month: `2026-08-31`
- Trials run: 3 — baseline SMA 10 เดือน, sensitivity SMA 9 เดือน และ SMA 11 เดือน
- Base cost: 0.10% ต่อ notional ที่ซื้อหรือขาย; high-cost scenario 0.20%

## Data Audit

- ดาวน์โหลด 13 ETF ได้ 5,209 daily rows และแปลงเป็น 248 เดือนที่จบแล้ว
- วันที่เรียงตามลำดับ ไม่มีวันที่ซ้ำ และไม่พบแถวขาดหลังวันเริ่มซื้อขายของแต่ละ ETF
- `VEA` เริ่มช้าที่สุดเมื่อ `2007-07-26`; ระบบจึงเริ่มสัญญาณจริงในเดือนเมษายน 2008 หลังมีข้อมูลพอสำหรับกฎที่เกี่ยวข้อง
- ตัดเดือนกันยายน 2026 ออกเพราะยังไม่จบเดือน
- ไม่ต่อข้อมูล ETF ย้อนหลังด้วย proxy และไม่เติมข้อมูลที่ไม่มีอยู่

ข้อจำกัดของ audit นี้คือเป็นการตรวจโครงสร้าง ราคา adjusted และความครบถ้วนขั้นพื้นฐาน ไม่ใช่การเทียบราคากับ provider อิสระอีกแห่ง Yahoo Finance อาจแก้ไขข้อมูลย้อนหลังได้ จึงบันทึก hash ของ snapshot ที่ใช้ไว้

## Result Summary

- Decision: `revise`
- ผ่าน: CAGR หลังต้นทุนเป็นบวก, drawdown ต่ำกว่า strategic buy-and-hold และ 60/40, sensitivity SMA 9/11 ผ่าน
- ไม่ผ่าน: Sharpe ต่ำกว่า 60/40 และ maximum drawdown `20.07%` สูงกว่าเพดาน `20%`
- เหตุผลหลัก: ระบบลดความผันผวนได้มาก แต่ผลตอบแทนหลังต้นทุนต่ำ ต้นทุนจาก turnover สูง และผลช่วง test พึ่งพาเดือนกำไรสูงสุดไม่กี่เดือน

## Baseline Results

| Metric | Development 2008-05–2018-12 | Untouched test 2019-01–2026-08 | Full period |
|:--|--:|--:|--:|
| Total return after costs | 76.64% | 26.80% | 123.98% |
| CAGR after costs | 5.48% | 3.15% | 4.50% |
| CAGR before costs | 6.79% | 4.34% | 5.76% |
| Annual volatility | 6.60% | 6.86% | 6.70% |
| Sharpe vs SHY | 0.68 | 0.21 | 0.49 |
| Sortino | 1.42 | 0.71 | 1.09 |
| Maximum drawdown | -7.48% | -20.07% | -20.07% |
| Longest underwater period | 15 เดือน | 60 เดือน | 60 เดือน |
| Annual two-sided turnover | 12.44x | 11.58x | 12.08x |
| Orders counted | 652 | 469 | 1,121 |
| Average Canary CF | 40.23% | 39.67% | 40.00% |
| Average total Defensive allocation | 53.63% | 51.30% | 52.66% |

## Untouched-Test Benchmark Comparison

| Metric | Camellia v1 | Strategic buy-and-hold | 60/40 SPY/IEF | SPY |
|:--|--:|--:|--:|--:|
| CAGR after costs | 3.15% | 13.29% | 10.86% | 17.45% |
| Annual volatility | 6.86% | 13.82% | 10.90% | 16.45% |
| Sharpe vs SHY | 0.21 | 0.85 | 0.86 | 0.95 |
| Maximum drawdown | -20.07% | -24.13% | -20.52% | -23.93% |
| Longest underwater period | 60 เดือน | 25 เดือน | 25 เดือน | 23 เดือน |

ระบบลด volatility ลงชัดเจน แต่ลด drawdown จาก 60/40 เพียงประมาณ 0.45 จุดเปอร์เซ็นต์ แลกกับ CAGR ที่ต่ำกว่าประมาณ 7.71 จุดเปอร์เซ็นต์ และใช้เวลาฟื้นตัวยาวกว่า

## Sensitivity

| Test-period metric | SMA 9 | SMA 10 baseline | SMA 11 |
|:--|--:|--:|--:|
| Net CAGR | 3.10% | 3.15% | 3.13% |
| Sharpe | 0.20 | 0.21 | 0.21 |
| Maximum drawdown | -19.90% | -20.07% | -19.53% |
| Annual two-sided turnover | 11.56x | 11.58x | 11.66x |

ผลใกล้กันมากและทั้ง SMA 9/11 ผ่านเกณฑ์ sensitivity ที่กำหนดไว้ จึงไม่พบว่าผล baseline เกิดจากการเลือก SMA 10 เพียงจุดเดียว

## Reality Checks

- Cost drag: test CAGR ลดจาก 4.34% ก่อนต้นทุนเป็น 3.15% หลังต้นทุน
- High-cost scenario: test CAGR เหลือ 1.96% และ maximum drawdown เพิ่มเป็น -24.00%
- PnL concentration: 5 เดือนที่ดีที่สุดสร้าง 90.63% ของกำไรสะสมช่วง test; เมื่อตัดออก CAGR เหลือ 0.51% และเมื่อตัด 10 เดือนที่ดีที่สุด CAGR เป็น -1.47%
- Statistical diagnostics: test PSR เทียบ Sharpe ศูนย์เท่ากับ 71.57%, DSR ประมาณ 71.50% และ MinTRL 759 เดือน เทียบกับข้อมูลจริง 92 เดือน ตัวเลขนี้ไม่ใช่เงื่อนไขผ่าน แต่บอกว่าหลักฐานเชิงสถิติยังไม่แข็งแรง
- Tail risk: monthly cVaR เท่ากับ 4.33% ที่ระดับ 95% และ 6.11% ที่ระดับ 99%
- Regime use: Canary CF เฉลี่ย 39.67% แต่เมื่อรวม trend gate ระบบถือ Defensive เฉลี่ย 51.30% ในช่วง test
- Lookahead review: signal ใช้ข้อมูลสิ้นเดือน `t` และคูณกับผลตอบแทนเดือน `t+1`; มี unit test ตรวจการเหลื่อมหนึ่งช่วงเวลา
- Cost review: น้ำหนักก่อนซื้อขายถูกปล่อยให้ไหลตามผลตอบแทนเดือนก่อน แล้วคิดส่วนต่างกับ target ใหม่ การสลับ ETF เต็มจำนวนจึงคิดทั้งขาขายและขาซื้อ

## Interpretation

เหตุผลเชิงโครงสร้างของระบบยังคงสมเหตุผล และ sensitivity ไม่ชี้ถึงการเลือก SMA แบบบังเอิญ แต่ baseline v1 ซ้อน Canary gate กับ sleeve trend gate จนถือ Defensive มากกว่าครึ่งหนึ่งโดยเฉลี่ย พร้อมสลับสถานะบ่อย ต้นทุนจึงกินผลตอบแทนประมาณ 1.20 จุดเปอร์เซ็นต์ต่อปีในช่วง test

ความล้มเหลวที่สำคัญกว่าการเกินเพดาน drawdown 0.07 จุดเปอร์เซ็นต์ คือ Sharpe ต่ำกว่า benchmark มาก, underwater นาน 60 เดือน และผลตอบแทนพึ่งพาเดือนเด่นไม่กี่เดือน จึงยังไม่ควรเลื่อนไป paper trade

## Limitations And Next Action

- ข้อมูลมาจาก provider เดียวและยังไม่ได้ cross-check ราคากับแหล่งอื่น
- Monthly adjusted close เป็นแบบจำลองผลตอบแทนรายเดือน ไม่ใช่ราคาเปิดจริงของวันซื้อขายแรกเดือนถัดไป
- Spread/slippage เป็นสมมติฐานคงที่และยังไม่รวมภาษีหรือผลกระทบจากขนาดคำสั่ง
- DSR เป็นการประมาณจากสาม trials ที่เกี่ยวข้องกันสูง จึงไม่ควรตีความเหมือนการทดลองอิสระ

แนวทาง revise ที่ตรงกับปัญหาที่พบคือแยกวัด contribution ของ Canary gate, trend gate และ monthly full rebalance ก่อน แล้วออกแบบ v2 ที่ลด turnover เช่น rebalance threshold หรือไม่ปรับน้ำหนักส่วนที่ target ไม่เปลี่ยน การเปลี่ยนดังกล่าวต้องเป็น strategy version ใหม่และกำหนดก่อนรัน ไม่แก้ v1 ย้อนหลัง
