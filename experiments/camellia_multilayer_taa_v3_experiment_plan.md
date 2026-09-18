# Camellia Multi-Layer TAA — Five-Experiment Plan For v3

วันที่ตรึงแผน: `2026-09-18`

## Objective And Evidence Boundary

เป้าหมายเชิงความทะเยอทะยานคือ CAGR 15–20% และ Sharpe มากกว่า 1 โดยยังรายงาน drawdown, leverage, turnover และต้นทุนครบ เป้าหมายนี้ไม่ใช่การรับรองว่าจะทำได้

เพราะผลปี 2019–2026 ของ v1/v2 ถูกเปิดดูแล้ว รอบนี้จะใช้สาม Research blocks เพื่อเลือกกติกา:

- `2008-05`–`2012-12`
- `2013-01`–`2018-12`
- `2019-01`–`2022-12`

หลัง freeze v3 จึงประเมิน `2023-01`–`2026-08` เป็น recent holdout ของพารามิเตอร์ v3 แต่ไม่เรียกว่า untouched ระดับโครงการ

## Dependent Variables

- Primary: median block CAGR และ median block Sharpe หลังต้นทุน
- Constraints: ทุก block CAGR ต้องเป็นบวก และ maximum drawdown ต้องไม่เกิน 30%
- Secondary: turnover, cost drag, Defensive fraction, realized volatility, leverage เฉลี่ย/สูงสุด และ PnL concentration
- Recent-holdout target: CAGR อย่างน้อย 15% และ Sharpe มากกว่า 1 พร้อม maximum drawdown ไม่เกิน 30%

## Q6 — Softer Canary Mapping

การเปลี่ยน Canary mapping เป็น `CF=min(2/3,b/3)` ซึ่งคง Risky exposure อย่างน้อยหนึ่งในสาม จะเพิ่ม CAGR/Sharpe โดยไม่ทำให้ drawdown เกิน 30% หรือไม่?

- Independent variable: breadth level 3 และ maximum Canary CF 66.67%

## Q7 — Partial Trend Reduction

การเปิด SMA10 gate แต่ลดเฉพาะ 50% ของน้ำหนักสินทรัพย์ที่ไม่ผ่าน แทนการย้ายทั้งก้อน จะลด downside โดยไม่สูญเสีย upside มากเหมือน v1 หรือไม่?

- Independent variable: below-trend retention 50%

## Q8 — Cross-Asset Relative Momentum

การยกเลิก strategic sleeve weights ชั่วคราว แล้วแบ่ง Risky budget เท่ากันให้ Top 4 จาก `SPY, MDY, IJR, VEA, DBC, VNQ, IEF, TLT` ตาม `13612W` จะเพิ่ม CAGR/Sharpe หรือไม่?

- Independent variable: risky allocation mode เป็น cross-asset Top 4

## Q9 — Blended Defense

การแบ่ง Defensive allocation เป็น 50% `SHY` และ 50% momentum-ranked winner จาก `SHY/IEF/LQD` จะลดความเสี่ยง duration/credit และรักษาผลตอบแทนได้ดีกว่านโยบาย winner-take-all หรือไม่?

- Independent variable: SHY defensive fraction 50%

## Q10 — Volatility Targeting

การ scale ผลตอบแทนส่วนเกินเหนือ SHY ไปยัง volatility target 15% ด้วย trailing 12-month volatility และ leverage cap 2 เท่า จะยก CAGR เข้าใกล้เป้าหมายโดย Sharpe ไม่ลดลงอย่างมีนัยสำคัญหรือไม่?

- Independent variable: target volatility 15%, lookback 12 เดือน, leverage cap 2.0
- Volatility estimate ต้อง lag หนึ่งเดือน
- SHY เป็น financing/cash proxy
- รายงาน leverage distribution และ high-cost result แยกจาก signal edge

## Selection Rule — Frozen Before Run

สำหรับ Q6–Q9 ให้ผ่านเมื่อ median block CAGR และ Sharpe สูงกว่า v2, ทุก block CAGR เป็นบวก และทุก block drawdown ไม่เกิน 30%

Q10 ผ่านเมื่อ median CAGR สูงกว่า v2, median Sharpe ไม่ต่ำกว่า v2 เกิน 0.05, ทุก block CAGR เป็นบวก และ drawdown ไม่เกิน 30%

รวมทุก parameter ที่ผ่านเป็น candidate v3 หาก candidate ยังผ่านข้อจำกัดและมี median CAGR กับ Sharpe สูงกว่า v2 ให้ freeze candidate นั้น หากไม่ผ่าน ให้เลือก single experiment ที่ผ่านและมีคะแนน `min(CAGR/15%,1) + min(Sharpe/1,1)` สูงสุด

หลัง freeze ห้ามเปลี่ยน v3 จากผล recent holdout แม้ว่าการทดลองอื่นจะทำได้ดีกว่า
