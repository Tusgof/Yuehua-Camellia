# Camellia Multi-Layer TAA — Diversified Return Engine Plan For v6

วันที่ตรึงแผน: `2026-09-18`

## เป้าหมายและขอบเขต

เก็บ v5 เป็น baseline `paper_ready` ที่ไม่แก้ย้อนหลัง แล้วทดสอบว่าการเพิ่มแหล่งผลตอบแทนและปรับโครงสร้างความเสี่ยงช่วย Camellia ได้หรือไม่ โดยไม่ใช้ leverage, short, options หรือข้อมูล proxy ก่อน ETF เริ่มซื้อขายจริง

- สัญญาณสิ้นเดือน `t` รับผลตอบแทนเดือน `t+1`
- ต้นทุนฐาน 0.10% และ high-cost stress 0.20% ต่อ notional ที่ซื้อหรือขาย
- Rebalance threshold 5%
- ราคา Yahoo Finance adjusted close
- Camellia เป็นพอร์ตเดี่ยว ไม่ใช้ 60/40 เป็นเกณฑ์เลือก
- ไม่อ่าน credential ไม่เรียก Webull API และไม่ส่งคำสั่ง

เจ้าของยืนยันผ่านแอป Webull Thailand เมื่อ 2026-09-18 ว่า DBMF, KMLM และ CTA ค้นหาเจอ ซื้อขายได้ และรองรับ fractional shares หลักฐานนี้ไม่ใช่ผล OpenAPI และไม่ยืนยัน minimum notional หรือราคา fill

## Evidence Split

ใช้ Research blocks เดิมเพื่อรักษาความต่อเนื่อง:

- `2008-08`–`2012-12`
- `2013-01`–`2018-12`
- `2019-01`–`2022-12`

หลัง freeze จึงรายงาน `2023-01`–`2026-08` เป็น recent diagnostic ซึ่งไม่ใช่ untouched holdout ระดับโครงการ

ETF ที่เริ่มภายหลังเข้าร่วมกติกาเมื่อมีประวัติครบ 12 เดือนเท่านั้น ห้าม backfill ด้วย proxy หากยังไม่มี ETF ที่เข้าเกณฑ์ใน sleeve ใหม่ ให้ใช้กติกา v5 เดิมในส่วนนั้น เพื่อไม่ลงโทษ candidate จากการไม่มีผลิตภัณฑ์ในอดีต

## Baseline v5

- Canary: VWO, BND, TIP; `CF=min(1, weak_count/2)` จาก `13612W`
- Risky budget: VTI 40%, regional Top 2 positive จาก VGK/EWJ/IPAC/VWO ตัวละ 10%, DBC 10%, VNQ 10%, IEF 10%, TLT 10%
- Defensive budget: 50% SHY, 25% conditional IEF, 25% conditional GLD/DBC
- ไม่มี leverage และไม่มี short

## ตัวชี้วัดและกฎผ่าน

ใช้ median และ worst block ของ CAGR, high-cost CAGR, Calmar, Ulcer Index, maximum drawdown, recovery months, upside/downside beta เทียบ SPY, turnover และ top-five-month PnL concentration

Candidate ผ่านเมื่อ:

1. CAGR และ high-cost CAGR เป็นบวกทุก Research block
2. Worst drawdown ไม่ต่ำกว่า -25%
3. เทียบ v5: median CAGR ไม่ลดเกิน 0.35 จุดเปอร์เซ็นต์, worst drawdown ไม่แย่เกิน 2 จุดเปอร์เซ็นต์, downside beta ไม่เพิ่มเกิน 0.08 และ turnover ไม่เกิน 1.25 เท่า
4. ดีขึ้นอย่างน้อยสี่ในแปดด้าน: CAGR, Calmar, Ulcer, median drawdown, recovery, upside beta, turnover และ PnL concentration

ไม่ใช้คะแนนรวมค่าเดียวและไม่บังคับ CAGR/Sharpe เป็นเป้าหมายเดี่ยว

## Q21 — Managed Futures Sleeve

การแบ่ง 10% ของ Risky budget จาก VTI ไปยัง managed-futures ETF จะเพิ่มความสม่ำเสมอและลด equity dependence หรือไม่?

- เมื่อมี ETF ที่มีข้อมูลครบ 12 เดือน: VTI ลดจาก 40% เหลือ 30%
- จัดอันดับ DBMF, KMLM และ CTA ด้วย `13612W`
- ให้ 10% แก่ตัวอันดับหนึ่งเมื่อคะแนนเป็นบวก; หากไม่มีคะแนนบวกให้งบ 10% เข้า Defensive
- ก่อนมี ETF ใดครบ 12 เดือน ให้คง VTI 40% แบบ v5

## Q22 — Regional Equal-Risk Weighting

การแบ่ง regional sleeve ตาม inverse trailing 6-month volatility แทนตัวละ 10% จะลด volatility drag หรือไม่?

- Universe และ Top 2 positive เหมือน v5
- ใช้ความผันผวนรายเดือนย้อนหลัง 6 เดือนที่ lag แล้ว
- น้ำหนักรวม 20%; แต่ละตัวมี floor 5% และ cap 15%
- ถ้ามีผู้ผ่านเพียงตัวเดียวให้ 10% และส่งอีก 10% เข้า Defensive เหมือน v5

## Q23 — Regional Rank Persistence

การคงผู้ชนะ regional เดิมจนกว่าสินทรัพย์นอกพอร์ตจะขึ้นเป็นอันดับหนึ่ง จะลด whipsaw โดยไม่เสียผลตอบแทนหรือไม่?

- เริ่มด้วย Top 2 positive ตาม v5
- ถ้าผู้ถือนอกพอร์ตขึ้นเพียงอันดับสอง ให้คงสมาชิกเดิมที่ยังมีโมเมนตัมบวก
- เปลี่ยนสมาชิกเมื่อ outsider ขึ้นอันดับหนึ่ง หรือ incumbent มีโมเมนตัมไม่เป็นบวก
- น้ำหนักตัวละ 10%; งบที่ว่างเข้า Defensive

## Q24 — Inflation-Defense Universe

การนำหลักฐานด้านความเสี่ยงจาก Q19 มาใช้เฉพาะ inflation pocket จะช่วยโดยไม่ดึงผลตอบแทนออกจาก Risky budget หรือไม่?

- Deflation pocket คง IEF/SHY แบบ v5
- เมื่อมีข้อมูลครบ 12 เดือน ใช้ตัวคะแนน multi-lookback สูงสุดจาก SCHP, GLDM และ PDBC ใน inflation pocket
- ถือผู้ชนะเฉพาะเมื่อคะแนนเป็นบวก มิฉะนั้นถือ SHY
- ก่อนมีตัวใหม่เข้าเกณฑ์ ใช้ GLD/DBC แบบ v5

## Q25 — Canary Horizon Consensus

การนับ Canary ว่าอ่อนแอเมื่อผลตอบแทน 1/3/6/12 เดือนติดลบอย่างน้อยสามช่วง จะลด false alarm โดยยังรักษาการป้องกันหรือไม่?

- เปลี่ยนเฉพาะนิยาม weak Canary
- คง VWO, BND, TIP และ `CF=min(1, weak_count/2)`
- รายงานจำนวน regime switches, average Defensive fraction, downside beta และ crisis drawdown เพิ่มเติม

## การรวมและ Freeze

1. ทดสอบ Q21–Q25 แยกจาก v5 รวมทั้งหมดห้า candidate
2. Candidate ที่ผ่านจะถูกรวมตามลำดับ Q21, Q22/Q23, Q24 และ Q25
3. Q22 กับ Q23 ใช้ร่วมกันได้: Q23 เลือกสมาชิกและ Q22 แบ่งน้ำหนัก
4. Candidate รวมต้องผ่านกฎเดิมอีกครั้ง
5. หากชุดรวมไม่ผ่าน ให้เลือก single candidate เฉพาะเมื่อมัน Pareto-dominate candidate ที่ผ่านตัวอื่นทุกตัวในแปดมิติ หากไม่มีให้คง v5
6. Commit แผนและตัวรันก่อนดูผล จากนั้น freeze configuration พร้อม data hash ก่อน recent diagnostic

## คำตัดสิน

- `reject`: หลักฐานใหม่ทำให้โครงสร้างอ่อนลงและไม่มี candidate ผ่าน
- `revise`: มีประโยชน์บางด้านแต่ชุดที่เลือกไม่ผ่าน recent safety หรือ readiness ของ v5
- `paper_ready`: ผ่าน Research rule, recent safety, full-period CAGR ไม่ต่ำกว่า v5 เกิน 0.25 จุดเปอร์เซ็นต์, Calmar และ drawdownไม่แย่กว่า v5, high-cost CAGR เป็นบวก และ turnover ไม่เกิน 1.25 เท่า

`paper_ready` ไม่อนุญาตให้เชื่อม credential, เรียก preview หรือส่งคำสั่ง
