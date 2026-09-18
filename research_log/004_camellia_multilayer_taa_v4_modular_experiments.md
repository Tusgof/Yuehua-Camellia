# 004 — Modular Experiments And Camellia v4

## 1. ข้อมูลพื้นฐาน

- วันที่: 2026-09-18
- เป้าหมาย: แยก return engine, risk overlay และ execution แล้วประเมินหลายมิติแทนการบังคับ CAGR/Sharpe
- แผนก่อนรัน: `e54dfaf032325fc717316bc110e9b1a571abb25d`
- ตัวรัน: `677deb3d37bd5f09814264e117538e6ae95c1168`
- Frozen v4: `0e83f3dac699cfc172a4dff7d322eb6183544458`

## 2. สมมติฐานและวิธีทดลอง

ทดลองห้าคำถามแยกกัน ได้แก่ strategic core, continuous multi-lookback trend, sector momentum, inflation/deflation defense และ cost-aware execution ใช้ข้อมูลสิ้นเดือนหนึ่งเพื่อรับผลตอบแทนเดือนถัดไป คิดต้นทุน 0.10% และ stress ที่ 0.20% ต่อ notional ที่ซื้อหรือขาย

ใช้สาม Research blocks เลือกกติกาตาม CAGR, Calmar, drawdown, Ulcer, downside beta, turnover และ PnL concentration โดยไม่รวมเป็นคะแนนค่าเดียว จากนั้น freeze ก่อนเปิด recent diagnostic ปี 2023–2026

## 3. ผล Attribution

Canary ลด median downside beta จากประมาณ 0.87 เหลือ 0.15 และลด median drawdown จาก -20.77% เหลือ -13.05% จึงยังมีหน้าที่ชัดเจน Ranked defense ให้ผลตอบแทนสูงกว่า SHY-only ส่วน fixed SPY ให้ median CAGR และ Calmar ดีกว่า market-cap rotation แต่ผลนี้เป็นเพียง attribution ที่ไม่ได้ลงทะเบียนเป็น candidate

## 4. ผลการทดลอง

Q11 เพิ่ม median CAGR เป็น 7.18% แต่ worst drawdown แย่ลงเป็น -29.35% และ downside beta เพิ่มเป็น 0.63 Q12 ลด median drawdownแต่ไม่เพิ่มคุณภาพผลตอบแทน Q13 ลด CAGR พร้อมเพิ่ม turnover Q15 ไม่สามารถลด median turnover ได้

Q14 ผ่านเพียงข้อเดียว โดย median CAGR 6.36%, median Calmar 0.99, median drawdown -9.23%, worst drawdown -9.54%, downside beta 0.09 และ turnover 6.51 เท่าต่อปี จึงถูก freeze เป็น v4

## 5. ผลหลัง Freeze

ช่วง 2008–2026 v4 ให้ CAGR 6.18%, Sharpe 0.63, maximum drawdown -12.48%, Calmar 0.50 และ turnover 8.24 เท่าต่อปี เทียบ v2 ที่ CAGR 6.15%, Sharpe 0.62, drawdown -19.76% และ turnover 10.13 เท่า

ช่วง recent diagnostic v4 ให้ CAGR 4.49%, Sharpe 0.14 และ drawdown -10.70% ดีกว่า v2 ในผลตอบแทนแต่ยังตาม 60/40 และ SPY มาก กำไร recent ยังพึ่งห้าเดือนที่ดีที่สุดสูง และไม่มี untouched historical period เหลืออยู่

## 6. ข้อสรุป

กำหนด v4 เป็น `revise` ไม่สร้าง paper plan การแยก Defensive sleeve ตามหน้าที่ช่วยลด drawdown ได้จริง แต่ระบบยังขาด upside participation และฟื้นตัวช้า งานถัดไปควรทดสอบ return engine ที่เรียบง่ายกว่า โดยเฉพาะ fixed SPY เทียบกับ market-cap rotation ภายใต้ Defensive policy ของ v4 พร้อมใช้กฎที่ตรึงล่วงหน้า
