# Strategy: Camellia Multi-Layer Tactical Asset Allocation v2

## Identity

- ID: `camellia_multilayer_taa`
- Version: `2`
- Status: `revise`
- Source creator: Yuehua Research Lab
- Parent specification: `strategies/camellia_multilayer_taa.md`
- Experiment plan: `experiments/camellia_multilayer_taa_v2_experiment_plan.md`
- Frozen configuration: `experiments/camellia_multilayer_taa_v2_frozen.json`

## Scope

กติกา v2 สืบทอด universe, Canary formula, `B=2`, strategic sleeve weights, Defensive ranking, signal timing, data contract, costs, benchmarks และ metrics จาก v1 ทุกข้อ ยกเว้นสามจุดที่ระบุด้านล่าง

## Changes From v1

### 1. Disable Sleeve Trend Gate

- ปิด 10-month SMA trend gate ระดับ Sleeve
- Risky allocation ถูกควบคุมด้วย Canary fraction เท่านั้น
- ไม่มีการย้ายน้ำหนักของแต่ละ Risky instrument ไป Defensive เพราะราคาอยู่ใต้ SMA

### 2. Hold Top Two U.S. Market-Cap ETFs

- จัดอันดับ `SPY`, `MDY`, `IJR` ด้วยสูตร `13612` เดิม
- เลือกสองอันดับแรกแทน winner-take-all
- แบ่ง U.S. Equity Sleeve 40% เท่ากันเป็น 20%/20% ภายใน Risky budget
- ใช้ลำดับตัดสินกรณีคะแนนเท่ากัน `SPY`, `MDY`, `IJR`

### 3. Five-Percent Portfolio Rebalance Threshold

- คำนวณ one-way target change เป็น `sum(abs(target-pretrade))/2`
- หากค่าน้อยกว่า 5% ให้ข้ามทั้งรอบและถือน้ำหนัก pretrade ต่อ
- หากเท่ากับหรือมากกว่า 5% ให้ rebalance ไป target เต็มจำนวน
- รอบเริ่มต้นพอร์ตต้องซื้อเข้าสู่ target เสมอ

## Frozen Rules That Did Not Change

- Canary basket: `VWO`, `BND`, `TIP`
- Canary score: `13612W`
- `CF=min(1,b/2)`
- Defensive policy: เลือกคะแนน `13612W` สูงสุดจาก `SHY`, `IEF`, `LQD`; fallback เป็น `SHY`
- Risky sleeves: U.S. Equity 40%, VEA 20%, DBC 10%, VNQ 10%, IEF 10%, TLT 10%
- ไม่มี leverage และไม่มี short position
- Signal สิ้นเดือน `t` ใช้กับ return เดือน `t+1`
- ต้นทุน baseline 0.10% ต่อ notional ที่ซื้อหรือขาย และ high-cost 0.20%

## Selection Provenance

v2 ถูกเลือกจาก Development period ถึงธันวาคม 2018 เท่านั้น ตาม commit:

- Pre-registered plan: `fc1fda7b2dfb5cb662a4bdf62a1da8376cbd75e1`
- Experiment runner: `50f3b5541193050017ef130966403bab96c704a1`
- Frozen before test: `9c5ab9d981f50995529205f666789a8b4e5988ef`

ผล Untouched test ไม่ถูกใช้เปลี่ยนกติกา v2

## Result And Current Boundary

- Untouched-test CAGR หลังต้นทุน: 3.31%
- Sharpe: 0.21
- Maximum drawdown: -19.76%
- Annual two-sided turnover: 9.84x
- Decision: `revise`

v2 ลด turnover และผ่านเพดาน drawdown 20% แต่ Sharpe ยังต่ำกว่า 60/40 มาก จึงยังไม่อนุญาตให้สร้าง paper plan
