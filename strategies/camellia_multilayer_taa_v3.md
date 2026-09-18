# Strategy: Camellia Multi-Layer Tactical Asset Allocation v3

## Identity

- ID: `camellia_multilayer_taa`
- Version: `3`
- Status: `reject`
- Parent: `strategies/camellia_multilayer_taa_v2.md`
- Plan: `experiments/camellia_multilayer_taa_v3_experiment_plan.md`
- Frozen configuration: `experiments/camellia_multilayer_taa_v3_frozen.json`

## Frozen Change From v2

v3 สืบทอด signal และ allocation ของ v2 แล้วเพิ่ม volatility targeting เพียงอย่างเดียว:

- Target volatility: 15% ต่อปี
- Volatility estimate: trailing 12-month realized volatility ของ v2 net return
- Estimate lag: หนึ่งเดือน
- Leverage cap: 2.0 เท่า
- SHY return เป็น cash/financing proxy
- ผลตอบแทน: `SHY + leverage * (v2_return - SHY)`
- ต้นทุนและ turnover ถูก scale ตาม leverage

## Selection And Result

กติกาถูกเลือกจากสาม Research blocks และ freeze ที่ commit `8c828cc869c846af4bfd4cd262b34f9ee4370a2c` ก่อนประเมินปี 2023–2026

Recent-holdout result:

- CAGR: 1.97%
- Sharpe: -0.08
- Maximum drawdown: -18.79%
- Average leverage: 1.90 เท่า
- High-cost CAGR: -0.26%

Decision: `reject` เพราะไม่เข้าใกล้เป้าหมาย CAGR 15–20% / Sharpe >1 และ leverage ขยายต้นทุนกับความผันผวนโดยไม่มี signal edge เพียงพอ

