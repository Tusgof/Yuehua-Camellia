# Camellia Growth — Research Round 8 (Q29–Q32)

วันที่ตรึงแผน: `2026-09-18`

## เป้าหมาย

ใช้ Camellia v6 เป็น baseline และทดลองนำ risk capacity ของเจ้าของที่ยอมรับ downside ได้ประมาณ 20–25% ไปเพิ่มผลตอบแทนอย่างมีเหตุผล โดยรักษา Selective Canary เป็นโครงสร้างป้องกันหลัก

- สัญญาณสิ้นเดือน `t` รับผลตอบแทนเดือน `t+1`
- Base trading cost 0.10% และ high-cost stress 0.20% ต่อ notional ที่ซื้อหรือขาย
- Whole-portfolio rebalance threshold 5%
- Research blocks: `2008-08–2012-12`, `2013-01–2018-12`, `2019-01–2022-12`
- Recent diagnostic: `2023-01–2026-08`; เปิดหลัง freeze เท่านั้น
- ใช้ Yahoo Finance adjusted-close snapshot เดิมและไม่ backfill ประวัติ ETF
- ทดสอบ 4 candidate แยกเดี่ยว ไม่มีการรวมกติกาหลังเห็นผล
- จำนวนการทดลองสะสมหลังรอบนี้คือ Q1–Q32

## Baseline v6

- Canary: VWO, BND, TIP ด้วย `13612W`
- ไม่มีคำเตือน: VTI 40%, Regional 20%, DBC 10%, VNQ 10%, IEF 10%, TLT 10%
- VWO-only warning: ปิด VTI และ Regional
- BND/TIP warning ขณะที่ VWO แข็งแรง: ปิด VNQ, IEF และ TLT
- VWO พร้อม BND/TIP warning: Defensive 100%
- Regional: Top 2 positive `13612W` จาก VGK, EWJ, IPAC, VWO
- Defensive: 50% SHY, 25% conditional IEF, 25% conditional GLD/DBC

## Q29 — Partial Canary Cuts

คำถาม: การลด sleeve ที่ถูกเตือนเหลือ 50% แทนการปิดทั้งหมดใน single-warning state จะเพิ่ม participation และลด missed rebound โดยยังรักษาการป้องกันเมื่อคำเตือนยืนยันกันหรือไม่?

- VWO-only warning: ถือ VTI 20% และ Regional 10% พร้อม DBC/VNQ/IEF/TLT ตามน้ำหนักเต็ม รวม Risky target 70%
- BND/TIP-only warning: ถือ VNQ/IEF/TLT ครึ่งน้ำหนัก รวม 15% พร้อม Equity และ DBC ตามน้ำหนักเต็ม รวม Risky target 85%
- Combined warning: Defensive 100% เหมือน v6
- No warning: เหมือน v6

## Q30 — Aggressive Risk-On Allocation

คำถาม: การย้าย duration 20% ไปยัง VTI เฉพาะโครงสร้าง Growth จะใช้ risk budget เพิ่มได้คุ้มค่าหรือไม่?

Strategic Risk-On weights:

- VTI 60%
- Regional 20%
- DBC 10%
- VNQ 10%
- IEF 0%, TLT 0%

ใช้ Selective Canary แบบ v6 กับกลุ่มใหม่: VWO warning ปิด VTI/Regional, BND/TIP warning ปิด VNQ และ combined warning เข้า Defensive 100%

## Q31 — Conditional Sector Satellite

คำถาม: Sector momentum ขนาดเล็กและเปิดเฉพาะ no-warning state จะให้ผลต่างจาก Q13 ซึ่งเคยแทน US sleeve ทั้ง 40% หรือไม่?

- เฉพาะ no-warning state: VTI 20% + Top 1 sector 20% + ส่วนอื่นเหมือน v6
- Sector universe: XLB, XLE, XLF, XLI, XLK, XLP, XLU, XLV, XLY
- Ranking: `13612W`; หากไม่มี sector ที่คะแนนเป็นบวกให้ VTI กลับเป็น 40%
- เมื่อมี Canary warning ใช้ v6 เดิมและไม่มี Sector satellite
- Sector ETF ยังไม่มีหลักฐาน Webull Thailand ใน repo; หากผ่านผลตอบแทนจะมีสถานะ `revise` จนกว่าเจ้าของหรือ read-only API จะยืนยันการซื้อขายและ fractional support

## Q32 — Conditional 1.20x Risk-On Overlay

คำถาม: Exposure 1.20 เท่าเฉพาะ no-warning state จะเพิ่ม CAGR โดยไม่เกิดความล้มเหลวแบบ Q10 ซึ่ง target volatility สูงสุด 2 เท่าหรือไม่?

- No warning: คูณ Risky weights ของ v6 ด้วย 1.20 และกู้ 20% ของ NAV
- Canary warning ใดๆ: ไม่ใช้ leverage และใช้ v6 ตามปกติ
- Base financing: ผลตอบแทน SHY รายเดือนที่ไม่ต่ำกว่าศูนย์ + 2% ต่อปี
- Stress financing: ผลตอบแทน SHY รายเดือนที่ไม่ต่ำกว่าศูนย์ + 4% ต่อปี
- Financing notional ถูกนับใน turnover/cost อย่างอนุรักษนิยม
- หากผ่านผลตอบแทนจะมีสถานะ `revise` จนกว่าจะยืนยัน margin availability, borrowing rate และ operational limits ของ Webull Thailand

## เกณฑ์เลือก Growth Candidate

Candidate ต้องผ่านทุกข้อใน Research blocks:

1. Base-cost และ high-cost CAGR เป็นบวกทุก block
2. Worst maximum drawdown ไม่ต่ำกว่า -25%
3. Median CAGR สูงกว่า v6 อย่างน้อย 1.00 จุดเปอร์เซ็นต์
4. Median Sharpe ไม่ต่ำกว่า v6 เกิน 0.10
5. Median risk-matched CAGR ไม่ต่ำกว่า v6 เกิน 0.25 จุดเปอร์เซ็นต์
6. Median upside beta ต่อ SPY สูงกว่า v6
7. Median downside beta ไม่สูงกว่า v6 เกิน 0.15
8. Median turnover ไม่เกิน 1.25 เท่าของ v6
9. Median gross-net CAGR spread ไม่สูงกว่า v6 เกิน 0.35 จุดเปอร์เซ็นต์

หากมีหลาย candidate ผ่าน ให้เลือก median CAGR สูงสุด; หากเท่ากันให้เลือก Sharpe สูงกว่า ไม่มีการรวม candidate ในรอบนี้

รายงาน approximate DSR ด้วยจำนวนการทดลองสะสม 32 ครั้ง แต่ไม่ใช้เป็นเกณฑ์ผ่านเพราะไม่มี return correlation ครบทุก trial เก่า

## Freeze, Recent และสถานะ v7

Freeze ผู้ชนะจาก Research blocks ก่อนเปิด recent diagnostic แล้วตรวจ:

1. Recent base/high-cost CAGR เป็นบวก
2. Recent และ full maximum drawdown ไม่ต่ำกว่า -25%
3. Full CAGR สูงกว่า v6 อย่างน้อย 0.75 จุดเปอร์เซ็นต์
4. Full Sharpe ไม่ต่ำกว่า v6 เกิน 0.10
5. Full turnover ไม่เกิน 1.25 เท่าของ v6
6. Full high-cost CAGR เป็นบวก

สถานะ:

- `paper_ready`: ผ่านทั้งหมดและใช้เฉพาะสินทรัพย์/วิธี execution ที่ยืนยันแล้วใน v6
- `revise`: ผ่านผล backtest แต่ต้องยืนยัน Sector ETF หรือ margin/financing บน Webull
- `reject`: ไม่มี candidate ผ่าน Research หรือ frozen candidate ล้มเหลวใน recent/full checks

หากได้ v7 ระดับ `paper_ready` สามารถออกแบบ paper plan ให้รัน v6 และ v7 แยก ledger พร้อมกันได้ แต่การสร้าง paper plan และการเชื่อม Webull เป็น milestone แยกต่างหาก
