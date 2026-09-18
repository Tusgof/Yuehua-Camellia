# Camellia Multi-Layer TAA — Webull Return-Source Plan For v5

วันที่ตรึงแผน: `2026-09-18`

## เป้าหมายและขอบเขต

Camellia จะถูกประเมินเป็นพอร์ตเดี่ยว ไม่ทดสอบการผสมกับ 60/40 รอบนี้มุ่งเพิ่ม upside participation และแหล่งผลตอบแทนที่ไม่พึ่งหุ้นสหรัฐฯ โดยรักษา Defensive policy ของ v4 เป็น baseline

- ETF แบบ long-only
- ไม่ใช้ leverage และไม่ short
- สัญญาณสิ้นเดือน `t` รับผลตอบแทนเดือน `t+1`
- Base cost 0.10% และ high-cost stress 0.20% ต่อ notional ที่ซื้อหรือขาย
- Rebalance threshold 5% ยกเว้นกติกา rank buffer ที่ระบุแยก

## Webull Boundary

หลักฐาน read-only ของบัญชี Webull Thailand ที่บันทึกใน `docs/WEBULL_OPENAPI.md` ยืนยันเมื่อ 2026-07-15 ว่า VTI, VGK, EWJ, IPAC, VWO, IEF, SCHP, GLDM, PDBC และ VNQI มี `status=OC` และ `fractionable=true`

รอบ v5 ใช้เฉพาะ ETF ใหม่จากรายการที่ยืนยันแล้ว ไม่อ่าน credential และไม่เรียก order endpoint ข้อมูลราคาสำหรับ backtest มาจาก Yahoo Finance adjusted close เช่นเดิม

ETF ที่เริ่มภายหลังจะเข้าร่วม ranking เมื่อมีประวัติครบ 12 เดือนเท่านั้น ห้าม backfill ด้วย proxy:

- Alternative macro: SCHP, GLDM, PDBC, VNQI
- Regional equity: VGK, EWJ, IPAC, VWO
- Broad US: VTI

## Evidence Split

ใช้สาม Research blocks เดิม:

- `2008-08`–`2012-12`
- `2013-01`–`2018-12`
- `2019-01`–`2022-12`

หลัง freeze ให้รายงาน `2023-01`–`2026-08` เป็น recent diagnostic ข้อมูลช่วงนี้เคยถูกเปิดดูแล้ว จึงไม่เรียกว่า untouched holdout แต่เจ้าของอนุญาตให้ใช้ข้อมูลที่มีเพื่อเร่งการตัดสินใจ

## Baseline v4

- Canary: VWO, BND, TIP; `CF=min(1, weak_count/2)`
- US sleeve 40%: Top 2 ของ SPY, MDY, IJR
- VEA 20%, DBC 10%, VNQ 10%, IEF 10%, TLT 10%
- Defensive budget: 50% SHY, 25% deflation pocket, 25% inflation pocket
- Status: `revise`

## ตัวชี้วัดและกฎผ่าน

ใช้ median และ worst block ของ CAGR, high-cost CAGR, Calmar, Ulcer Index, maximum drawdown, recovery months, upside/downside beta เทียบ SPY, turnover และ top-five-month PnL concentration

Candidate ผ่านเมื่อ:

1. CAGR และ high-cost CAGR เป็นบวกทุก block
2. Worst drawdown ไม่ต่ำกว่า -30%
3. เทียบ v4: median CAGR ไม่ลดเกิน 0.50 จุดเปอร์เซ็นต์, worst drawdown ไม่แย่เกิน 3 จุดเปอร์เซ็นต์, downside beta ไม่เพิ่มเกิน 0.10 และ turnover ไม่เกิน 1.25 เท่า
4. ดีขึ้นอย่างน้อยสี่ในแปดด้าน: CAGR, Calmar, Ulcer, median drawdown, recovery, upside beta, turnover และ PnL concentration

ไม่ใช้คะแนนรวมค่าเดียว

## Q16 — Fixed Broad-US Sleeve

การแทน market-cap rotation ด้วย VTI คงที่ 40% ของ Risky budget จะเพิ่ม upside participation และลด timing error หรือไม่?

- Independent variable: US sleeve ถือ VTI แทน Top 2 ของ SPY/MDY/IJR
- ส่วนอื่นใช้ v4

## Q17 — Defensive Pocket Ablation

ผลของ v4 มาจาก deflation pocket และ inflation pocket ร่วมกันจริงหรือไม่?

ทดสอบสองแขนที่ลงทะเบียนล่วงหน้า:

- `q17_deflation_only`: 75% SHY + 25% IEF เมื่อ multi-lookback trend เป็นบวก มิฉะนั้น SHY
- `q17_inflation_only`: 75% SHY + 25% ตัวที่แข็งกว่าระหว่าง GLD/DBC เมื่อ trend เป็นบวก มิฉะนั้น SHY

หากแขนใดผ่านและ Pareto-dominate v4 ให้ใช้กติกาที่เรียบง่ายกว่า หากไม่ผ่านให้คง Defensive policy ของ v4

## Q18 — Rank Buffer

การเปลี่ยน market-cap ETF เฉพาะเมื่อสินทรัพย์นอกพอร์ตขึ้นเป็นอันดับ 1 จะลด turnover โดยไม่เสียผลตอบแทนหรือไม่?

- เริ่มจาก Top 2 ของ SPY/MDY/IJR
- ถ้าสินทรัพย์นอกพอร์ตอยู่เพียงอันดับ 2 ให้คงผู้ถือเดิม
- เปลี่ยนสมาชิกอันดับ 3 ออกเมื่อสินทรัพย์นอกพอร์ตขึ้นเป็นอันดับ 1
- ส่วนอื่นใช้ v4

Q16 และ Q18 เป็น foundation ที่ขัดกัน หากทั้งคู่ผ่าน ให้ Q16 มีลำดับก่อนเพราะเรียบง่ายและใช้ ETF เดียวที่ Webull ยืนยันแล้ว

## Q19 — Alternative Macro Sleeve

การแทน DBC 10% + VNQ 10% ด้วย sleeve ที่เลือกแหล่งผลตอบแทนนอกหุ้นสหรัฐฯ จะเพิ่มความสม่ำเสมอหรือไม่?

- Budget: 20% ของ Risky budget
- Universe: SCHP, GLDM, PDBC, VNQI
- จัดอันดับด้วย `13612W`
- เลือกไม่เกิน Top 2 ที่คะแนนเป็นบวก ตัวละ 10%
- น้ำหนักที่ไม่ได้ใช้ย้ายเข้า Defensive policy ของ v4

## Q20 — Regional Equity Sleeve

การแทน VEA 20% ด้วย regional momentum จะเพิ่มผลตอบแทนจากต่างประเทศโดยไม่เพิ่ม downside มากเกินไปหรือไม่?

- Budget: 20% ของ Risky budget
- Universe: VGK, EWJ, IPAC, VWO
- จัดอันดับด้วย `13612W`
- เลือกไม่เกิน Top 2 ที่คะแนนเป็นบวก ตัวละ 10%
- น้ำหนักที่ไม่ได้ใช้ย้ายเข้า Defensive policy ของ v4

## การรวมและ Freeze

1. ทดสอบทุก candidate แยกจาก v4 รวมเป็นหก candidate จากห้าคำถาม
2. Foundation: ใช้ Q16 หากผ่าน มิฉะนั้นใช้ Q18 หากผ่าน
3. Defense: ใช้แขน Q17 เฉพาะเมื่อผ่านและ Pareto-dominate v4; สองแขนใช้พร้อมกันไม่ได้
4. เพิ่ม Q19/Q20 เมื่อแต่ละข้อผ่าน
5. Candidate รวมต้องผ่านกฎเดียวกันอีกครั้ง หากไม่ผ่านให้เลือก single candidate ที่ Pareto-dominate candidate ที่ผ่านอื่นทั้งหมด; หากไม่มีให้คง v4
6. Commit แผนและตัวรันก่อนเปิดผล แล้ว freeze configuration พร้อม data hash ก่อน recent diagnostic

## คำตัดสิน

- `reject`: ไม่มี candidate ผ่านและหลักฐานทำให้ v4 อ่อนลง
- `revise`: v5 ดีขึ้นบางด้านแต่ยังไม่ผ่าน safety หรือยังไม่พร้อม workflow จริง
- `paper_ready`: candidate ผ่าน Research rule, recent safety, full-period CAGR ไม่ต่ำกว่า v4 เกิน 0.25 จุดเปอร์เซ็นต์, full-period Calmar ไม่ต่ำกว่า v4, full-period drawdownไม่แย่กว่า v4, high-cost CAGR เป็นบวก และ turnover ไม่เกิน 1.25 เท่าของ v4

`paper_ready` หมายถึงพร้อมให้เจ้าของพิจารณาแผน paper trade เท่านั้น ไม่อนุญาตการเชื่อม credential, preview หรือส่งคำสั่งใด ๆ โดยอัตโนมัติ
