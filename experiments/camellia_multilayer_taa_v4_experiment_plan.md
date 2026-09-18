# Camellia Multi-Layer TAA — Modular Five-Experiment Plan For v4

วันที่ตรึงแผน: `2026-09-18`

## เป้าหมายและขอบเขตหลักฐาน

รอบนี้ไม่ใช้ CAGR หรือ Sharpe ค่าเดียวเป็นเป้าหมายบังคับ แต่ถามว่าระบบให้ผลตอบแทนคุ้มกับความเสี่ยง ต้นทุน และเวลาฟื้นตัวหรือไม่ โดยยังคงกรอบ ETF แบบ long-only, ไม่ใช้ leverage, คำนวณสัญญาณจากราคาสิ้นเดือน `t` และรับผลตอบแทนในเดือน `t+1`

ข้อมูลปี 2019–2026 เคยถูกเปิดดูใน v1–v3 แล้ว จึงไม่มีช่วง untouched เหลืออยู่ในข้อมูล ETF ชุดนี้ การเลือกกติกาจะใช้สาม Research blocks:

- `2008-08`–`2012-12`
- `2013-01`–`2018-12`
- `2019-01`–`2022-12`

หลัง freeze จะรายงาน `2023-01`–`2026-08` เป็น recent diagnostic เท่านั้น ไม่เรียกว่า holdout และไม่ใช้ย้อนกลับไปเลือกกติกาอื่น

## Baseline และต้นทุน

- Baseline: v2 แบบไม่ใช้ sleeve trend gate, เลือกหุ้นสหรัฐฯ Top 2, rebalance threshold 5%
- Base cost: 0.10% ต่อ notional ที่ซื้อหรือขาย
- High-cost stress: 0.20% ต่อ notional
- Benchmark: SPY, 60/40 SPY/IEF และ strategic buy-and-hold ใน universe เดิม
- ข้อมูลเพิ่ม: `XLB, XLE, XLF, XLI, XLK, XLP, XLU, XLV, XLY, GLD`

## Attribution ก่อนทดลอง

รายงานผลของ strategic buy-and-hold, v2, v2 ที่ไม่มี Canary, v2 ที่ใช้ SPY แทน market-cap rotation และ v2 ที่ใช้ SHY อย่างเดียวใน Defensive sleeve เพื่อดูผลส่วนเพิ่มของแต่ละโมดูล Attribution ใช้เพื่อวินิจฉัย ไม่ใช้เพิ่มจำนวน candidate ในการคัดเลือก v4

## ตัวชี้วัดตัดสิน

วัด median และ worst block ของ:

- Net CAGR, geometric/arithmetic gap และผลภายใต้ต้นทุนสูง
- Maximum drawdown, Ulcer Index, recovery และ Calmar
- Downside beta เทียบ SPY และ 60/40
- Annual two-sided turnover และ gross/net CAGR spread
- Top-five-month PnL concentration
- Average defensive allocation

Candidate มีสิทธิ์ผ่านเมื่อ:

1. CAGR หลังต้นทุนเป็นบวกทุก Research block และ median high-cost CAGR เป็นบวก
2. ไม่มี block ใดมี maximum drawdown แย่กว่า `-30%`
3. เมื่อเทียบ v2: median CAGR ไม่ลดเกิน 0.50 จุดเปอร์เซ็นต์, worst drawdown ไม่แย่เกิน 3 จุดเปอร์เซ็นต์, downside beta ไม่เพิ่มเกิน 0.10 และ turnover ไม่เกิน 1.25 เท่า
4. ปรับดีขึ้นอย่างน้อยสามในหกด้าน: CAGR สูงขึ้น, Calmar สูงขึ้น, Ulcer ต่ำลง, maximum drawdown ดีขึ้น, turnover ต่ำลง, และ top-five-month concentration ต่ำลง

ไม่ใช้คะแนนรวมค่าเดียว หากหลาย candidate ผ่าน ให้นำโมดูลที่ไม่ขัดกันมารวมตามลำดับ Q11 → Q15 แล้ว candidate รวมต้องผ่านกฎเดียวกันอีกครั้ง หาก candidate รวมไม่ผ่าน ให้เลือก single candidate ที่มี Pareto dominance ชัดที่สุด; หากไม่มีให้คง v2 และตัดสิน v4 เป็น `reject`

## Q11 — Strategic Core + Tactical Overlay

การคง 70% ของพอร์ตใน strategic core และให้ v2 ควบคุมเพียง tactical overlay 30% จะลดค่าเสียโอกาสและระยะเวลาฟื้นตัวโดยยังรักษาการป้องกันขาลงได้หรือไม่?

- Independent variable: `70% strategic target + 30% v2 target`
- Strategic target: SPY 40%, VEA 20%, DBC 10%, VNQ 10%, IEF 10%, TLT 10%

## Q12 — Continuous Multi-Lookback Trend

การแทน Canary breadth แบบขั้นบันไดด้วยคะแนน trend ต่อเนื่องของสินทรัพย์เสี่ยง จะลด timing risk และให้ผลสม่ำเสมอกว่าหรือไม่?

- ใช้ค่าเฉลี่ยของ `sign(R1), sign(R3), sign(R6), sign(R12)`
- แปลงคะแนนจาก `[-1, 1]` เป็น long-only multiplier `[0, 1]`
- คูณ multiplier กับ target ของ v2 รายสินทรัพย์ และย้ายส่วนที่เหลือเข้า Defensive policy เดิม
- ปิด Canary gate เพื่อไม่ป้องกันซ้ำสองชั้น

## Q13 — Sector Momentum Return Engine

การแทน market-cap rotation ใน US equity sleeve 40% ด้วย Top 3 sector ETFs ตาม `13612W` จะเพิ่มแหล่งผลตอบแทนและลดการพึ่งพาสินทรัพย์ที่เคลื่อนไหวคล้ายกันหรือไม่?

- Sector universe: `XLB, XLE, XLF, XLI, XLK, XLP, XLU, XLV, XLY`
- เลือก Top 3 และแบ่งน้ำหนัก US sleeve เท่ากัน
- Canary, สินทรัพย์อื่น และ Defensive policy ใช้กติกา v2

## Q14 — Inflation/Deflation Defensive Sleeve

การแยก Defensive budget ตามหน้าที่จะป้องกันวิกฤตเงินฝืดและเงินเฟ้อได้ดีกว่า ranked bond winner หรือไม่?

- 50% ของ Defensive budget อยู่ SHY เสมอ
- Deflation pocket 25%: ถือ IEF เมื่อ multi-lookback trend เป็นบวก มิฉะนั้น SHY
- Inflation pocket 25%: เลือกตัวที่ trend แข็งกว่าระหว่าง GLD/DBC เมื่อคะแนนเป็นบวก มิฉะนั้น SHY
- Risky allocation และ Canary ใช้กติกา v2

## Q15 — Cost-Aware Execution

การคำนวณสัญญาณทุกเดือนแต่ชะลอคำสั่งที่ไม่สำคัญ จะลด turnover อย่างน้อยครึ่งหนึ่งโดยไม่ทำลายการป้องกันหรือไม่?

- ใช้ target ของ v2 ไม่เปลี่ยน signal
- ซื้อขายเมื่อเริ่มระบบ, one-way proposed turnover อย่างน้อย 15%, หรือ Canary CF เพิ่มขึ้นจากเดือนก่อน
- หากไม่เข้าเงื่อนไข ให้คงน้ำหนักที่ไหลตามตลาด

## การ Freeze และคำตัดสิน

- Commit แผนนี้ก่อนเขียนตัวรันหรือเปิดผลทดลอง
- Commit ตัวรันก่อนรัน Research stage
- Freeze candidate ที่เลือกพร้อม data hash และ commit ของแผน/ตัวรันก่อน recent diagnostic
- Recent diagnostic มี safety veto หาก net CAGR ไม่เป็นบวก, maximum drawdown แย่กว่า `-30%`, high-cost CAGR ไม่เป็นบวก หรือ downside beta เทียบ SPY มากกว่า 1
- เนื่องจากไม่มี untouched period จริง สถานะดีที่สุดของ v4 รอบนี้คือ `revise`; ห้ามเลื่อนไป `paper_ready`
