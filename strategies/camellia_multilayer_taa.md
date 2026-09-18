# Strategy: Camellia Multi-Layer Tactical Asset Allocation

## Identity

- ID: `camellia_multilayer_taa`
- Version: `1`
- Status: `specified`
- Source creator: Yuehua Research Lab
- Source URL: `file:///D:/Fogust/Workspace/LLM%20Wiki/LLM%20Wiki/wiki/synthesis.md`
- Source accessed date: `2026-09-18`
- Source basis: ระบบผสมที่เจ้าของอนุมัติ โดยสังเคราะห์ GTAA ของ Mebane T. Faber, Regime-Aware Market-Cap HAA ของ Peter B. Richman และ DAA ของ Wouter J. Keller กับ Jan Willem Keuning

## Idea

- Market behavior expected: Canary breadth ใช้ลดงบสินทรัพย์เสี่ยงเมื่อหลายตลาดอ่อนแรง, การกระจายหลายสินทรัพย์ลดการพึ่งพาตลาดเดียว, relative momentum เลือกขนาดหุ้นสหรัฐฯ ที่แข็งแรง และ trend filter ลดการถือสินทรัพย์ที่อยู่ในขาลง
- Why it may persist: นักลงทุนและสถาบันปรับสถานะไม่พร้อมกัน แนวโน้มราคาจึงต่อเนื่องได้ระยะหนึ่ง ขณะที่ความเสี่ยงมักแพร่จากตลาดสินเชื่อ อัตราดอกเบี้ย และตลาดเกิดใหม่ไปยังสินทรัพย์เสี่ยงอื่น การใช้หลายชั้นมีเป้าหมายให้แต่ละกลไกทำหน้าที่ต่างกัน
- What would make it stop working: Canary ไม่เตือนก่อนการลดลงจริง, ตลาดกลับทิศถี่จนเกิด whipsaw, correlation ระหว่างหุ้นกับบอนด์สูงพร้อมกัน, relative momentum เลือกผู้ชนะย้อนหลังที่กลับตัวทันที หรือต้นทุนการสลับพอร์ตสูงกว่าผลที่ระบบสร้างได้

## Signal Definitions

ใช้ราคา adjusted close รายเดือนซึ่งรวมผลของ split และเงินปันผลตามข้อมูลจาก provider

- `R_n(i,t) = P(i,t) / P(i,t-n) - 1`
- `13612W(i,t) = [12R_1 + 4R_3 + 2R_6 + R_12] / 4`
- `13612(i,t) = [R_1 + R_3 + R_6 + R_12] / 4`
- `SMA10(i,t) = mean[P(i,t), ..., P(i,t-9)]`
- Canary อ่อนแรงเมื่อ `13612W <= 0`
- Trend ผ่านเมื่อ `P(i,t) > SMA10(i,t)`; กรณีเท่ากันถือว่าไม่ผ่าน

## Rules

### Layer 1 — Canary Breadth

- Canary basket: `VWO`, `BND`, `TIP`
- นับ `b` เป็นจำนวน Canary ที่มี `13612W <= 0`
- ใช้ breadth protection level `B=2`
- Defensive fraction: `CF = min(1, b / 2)` จึงได้ `0%`, `50%` หรือ `100%`
- Risky budget: `1-CF`
- ไม่มี buffer band ใน baseline

### Layer 2 — Strategic Sleeves

กระจาย Risky budget ตามน้ำหนักต่อไปนี้:

| Sleeve | Target weight within Risky budget | Instruments |
|:--|--:|:--|
| U.S. Equity | 40% | เลือกหนึ่งตัวจาก `SPY`, `MDY`, `IJR` |
| International Equity | 20% | `VEA` |
| Real Assets | 20% | `DBC` 10%, `VNQ` 10% |
| Fixed Income | 20% | `IEF` 10%, `TLT` 10% |

น้ำหนักรวมสูงสุดของพอร์ตเท่ากับ 100% ไม่มี leverage และไม่มี short position

### Layer 3 — U.S. Market-Cap Rotation

- จัดอันดับ `SPY`, `MDY`, `IJR` ด้วย `13612` แบบไม่ถ่วงน้ำหนัก
- ถือเฉพาะอันดับหนึ่ง (`T=1`) ด้วยน้ำหนักทั้งหมดของ U.S. Equity Sleeve
- หากคะแนนเท่ากัน ใช้ลำดับตัดสิน `SPY`, `MDY`, `IJR`

### Layer 4 — Trend Gate And Defense

- นำ 10-month SMA trend gate ไปใช้กับ Risky instrument ที่ได้รับ target weight แล้วทุกตัว
- น้ำหนักของสินทรัพย์ที่ไม่ผ่าน trend gate ถูกย้ายไป Defensive allocation ทั้งหมด
- รวม Defensive fraction จาก Canary กับน้ำหนักที่ไม่ผ่าน trend gate แล้วนำไปลงทุนในสินทรัพย์เดียวที่มี `13612W` สูงสุดจาก `SHY`, `IEF`, `LQD`
- หากคะแนน Defensive สูงสุดไม่เป็นบวก ให้ถือ `SHY`
- หากคะแนนเท่ากัน ใช้ลำดับตัดสิน `SHY`, `IEF`, `LQD`

### Timing And Execution

- Bar frequency: รายเดือน
- Decision timestamp: หลังทราบ adjusted close ของวันซื้อขายสุดท้ายในเดือน `t`
- Earliest execution timestamp: ช่วงซื้อขายแรกที่ทำได้ในเดือน `t+1`
- Backtest return contract: target weights จากสัญญาณเดือน `t` ใช้กับผลตอบแทนของเดือน `t+1`; ห้ามใช้ผลตอบแทนเดือน `t` ที่สร้างสัญญาณ
- Entry/exit: ปรับจากน้ำหนักปลายเดือนเดิมไปยัง target weights ใหม่ทุกเดือน
- Rebalance threshold: `0%` ใน baseline หมายถึงปรับทุกส่วนต่างของน้ำหนัก
- Missing-data rule: ห้ามเติมราคาย้อนหลังหรือแทนข้อมูลขาดด้วยศูนย์ เริ่มประเมินเมื่อสินทรัพย์ทุกตัวมีข้อมูลครบสำหรับ lookback 12 เดือน หากข้อมูลขาดหลังเริ่มระบบ ให้คงน้ำหนักเดิมในรอบนั้นและบันทึกเหตุการณ์

## Backtest Contract

- Data source and fields: Yahoo Finance monthly adjusted close/total-return series พร้อมบันทึกวันดาวน์โหลด timezone และสถานะการปรับเงินปันผล/split
- Requested sample start: `2008-01`; วันเริ่มผลจริงเลื่อนไปเดือนแรกที่ทุกสินทรัพย์มี lookback 12 เดือนครบ โดยไม่สร้าง proxy ย้อนหลัง
- Development period: วันเริ่มผลจริงถึง `2018-12`
- Untouched test period: `2019-01` ถึงเดือนเต็มล่าสุด ณ วันที่รัน
- Benchmark 1: strategic buy-and-hold เริ่มด้วย `SPY` 40%, `VEA` 20%, `DBC` 10%, `VNQ` 10%, `IEF` 10%, `TLT` 10% แล้วปล่อยให้น้ำหนักลอย
- Benchmark 2: 60/40 ที่ `SPY` 60% และ `IEF` 40% ปรับกลับสู่น้ำหนักเป้าหมายทุกเดือน
- Benchmark 3: buy-and-hold `SPY`
- Commission: `0%` แยกจาก spread/slippage
- Base spread/slippage: `0.10%` ต่อ notional ที่ซื้อหรือขาย
- High-cost scenario: `0.20%` ต่อ notional ที่ซื้อหรือขาย
- Cost formula: `cost_t = rate * sum(abs(target_weight_t - pretrade_weight_t))`; การสลับเต็มจาก ETF หนึ่งไปอีก ETF หนึ่งจึงคิดทั้งขาขายและขาซื้อ
- Tax/financing/borrow cost: `0%` ใน backtest; ไม่มี leverage หรือ short borrow
- Baseline version: กติกาทั้งหมดในเอกสารนี้
- Allowed adjustments: สอง sensitivity runs เท่านั้น คือเปลี่ยน trend gate เป็น SMA 9 เดือนและ SMA 11 เดือน โดยตรึงกติกาอื่นเหมือน baseline
- Trial count: ต้องรายงานทุก run รวม baseline, sensitivity และ run ที่ล้มเหลว ห้ามเลือกเก็บเฉพาะผลที่ดีที่สุด

## Parameter Inventory

พารามิเตอร์ต่อไปนี้เป็นแหล่ง model risk ที่ต้องบันทึก แต่ไม่อนุญาตให้ค้นหาทุกชุดผสมใน M2:

- Canary basket, สูตร `13612W` เทียบกับ `13612`, ค่า `B` และ regime threshold/buffer
- SMA lookback, จำนวนสินทรัพย์อันดับต้น `T` และ strategic sleeve weights
- Defensive universe/ranking, execution lag และ rebalance threshold
- ค่าอื่นนอก baseline หรือสอง sensitivity runs ต้องตั้งคำถามวิจัยใหม่และเพิ่ม version ก่อนเห็นผล

## Required Metrics

รายงานทั้ง Development, Untouched test และ Full period พร้อม benchmark ที่เกี่ยวข้อง

### Return And Compounding

- Total return, CAGR, annualized arithmetic mean และ geometric mean
- Volatility drag โดยเปรียบเทียบ arithmetic กับ geometric return
- Alpha, beta, upside beta และ downside beta เทียบ `SPY` และ 60/40 จากผลตอบแทนรายเดือน

### Risk And Path

- Annualized volatility, maximum drawdown, drawdown duration และ recovery time เป็นจำนวนเดือน
- Historical monthly VaR และ cVaR ที่ระดับ 95% และ 99%
- Ulcer Index และ UPI โดยใช้ `(CAGR - annualized SHY return) / Ulcer Index`
- `K50 = R * [1 - D/(1-D)]` เมื่อ `D<50%` และ `R>0`; มิฉะนั้นเป็นศูนย์
- `K25 = R * [1 - 2D/(1-2D)]` เมื่อ `D<25%` และ `R>0`; มิฉะนั้นเป็นศูนย์
- ใน K25/K50 ให้ `R` เป็น CAGR และ `D` เป็นค่าสัมบูรณ์ของ maximum drawdown ในรูป decimal ใช้เป็น diagnostic เท่านั้น ห้ามใช้เลือก variant

### Risk-Adjusted Return

- Sharpe ratio โดยใช้ผลตอบแทน `SHY` เป็น risk-free proxy
- Sortino ratio โดยใช้ minimum acceptable return เท่ากับ 0% ต่อเดือน
- Calmar ratio เท่ากับ CAGR หารด้วยค่าสัมบูรณ์ของ maximum drawdown

### Statistical Inference

- Sample length, skewness, excess kurtosis และ lag-1 autocorrelation
- PSR เทียบ null Sharpe เท่ากับศูนย์
- DSR โดยใช้จำนวน trials ที่รันจริง
- Minimum Track Record Length ที่ระดับความเชื่อมั่น 95%
- Metric เหล่านี้เป็นหลักฐานประกอบ ไม่มี acceptance threshold เพิ่มเติมใน version 1

### Implementation And Friction

- One-way turnover เท่ากับครึ่งหนึ่งของ two-sided turnover และรายงานทั้งสองค่า
- Gross/net CAGR spread, ต้นทุนรวม และผล high-cost scenario
- Average Canary defensive fraction `CF` และ average total Defensive allocation หลัง trend gate
- Switch count, จำนวนคำสั่งซื้อ/ขาย และจำนวนเดือนที่ target เปลี่ยน
- สัดส่วน PnL ที่มาจาก 1, 3, 5 และ 10 เดือนที่ดีที่สุด พร้อมผลเมื่อเอาเดือนเหล่านั้นออก

## Pass/Fail Rule — Locked Before Backtest

### Required net return behavior

- CAGR หลังต้นทุนใน Untouched test ต้องมากกว่าศูนย์
- Sharpe หลังต้นทุนใน Untouched test ต้องสูงกว่า benchmark 60/40

### Maximum acceptable drawdown

- Maximum drawdown หลังต้นทุนใน Untouched test ต้องไม่เกิน 20%
- Maximum drawdown ต้องต่ำกว่าทั้ง strategic buy-and-hold และ 60/40 ในช่วงเดียวกัน

### Required robustness/sensitivity

- SMA 9 เดือนและ SMA 11 เดือนต้องมี CAGR หลังต้นทุนมากกว่าศูนย์และ maximum drawdown ไม่เกิน 25% ใน Untouched test
- High-cost scenario และ metric อื่นต้องเปิดเผยครบ แต่ไม่มี threshold เพิ่มเติมใน version 1

### Decision

- `paper_ready`: ผ่านเงื่อนไขผลตอบแทน, Sharpe, drawdown และ sensitivity ทุกข้อ
- `reject`: CAGR หลังต้นทุนไม่เป็นบวกและไม่ได้ลด maximum drawdown เมื่อเทียบ strategic buy-and-hold ใน Untouched test
- `revise`: ผลอยู่ระหว่างสองกรณีข้างต้น หรือพบข้อผิดพลาดด้านข้อมูล/การจำลองที่ต้องแก้ก่อนตัดสิน

## Ambiguities Resolved

- ผู้สร้างระบบผสมคือ Yuehua Research Lab; งานของ Faber, Richman, Keller และ Keuning เป็นแหล่งแนวคิด ไม่ใช่ผู้สร้างระบบ Camellia รุ่นนี้
- Canary สามตัวใช้ `B=2`; เมื่ออ่อนแรงสองหรือสามตัวจึงเป็น Defensive 100%
- Canary ใช้ `13612W` แต่ U.S. market-cap ranking ใช้ `13612`
- Real Assets แบ่ง `DBC` และ `VNQ` เท่ากัน ส่วน Fixed Income แบ่ง `IEF` และ `TLT` เท่ากัน
- Defensive sleeve เป็น active bond selection ไม่ใช่เงินสดแท้เสมอ และ fallback คือ `SHY`
- Baseline ไม่มี buffer band และไม่มี rebalance threshold
- ข้อมูล ETF ไม่ถูกต่อย้อนหลังด้วย proxy ก่อนวันมีข้อมูลจริง
- Metric จำนวนมากใช้เพื่ออธิบายผล ไม่ได้เพิ่มเงื่อนไขผ่านโดยปริยาย

