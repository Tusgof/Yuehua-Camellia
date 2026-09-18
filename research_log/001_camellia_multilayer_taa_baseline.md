# 001 — Camellia Multi-Layer TAA Baseline

## 1. ข้อมูลพื้นฐาน

- วันที่: 2026-09-18
- ผู้ทดลอง: Codex ภายใต้ Yuehua Research Lab
- กลยุทธ์: `camellia_multilayer_taa` v1
- สินทรัพย์: VWO, BND, TIP, SPY, MDY, IJR, VEA, DBC, VNQ, IEF, TLT, SHY และ LQD
- ข้อมูล: Yahoo Finance adjusted close รายเดือน
- ช่วงผลจริง: พฤษภาคม 2008 ถึงสิงหาคม 2026
- Producing code commit: `c64a95b31e008d91873130f3314d79ec803f701d`

## 2. ปัญหาและสมมติฐาน

คำถามคือระบบที่รวม Canary breadth, multi-asset sleeves, market-cap momentum, trend gate และ defensive bond selection จะให้ผลตอบแทนหลังต้นทุนเป็นบวก พร้อมลด drawdown และให้ Sharpe สูงกว่า 60/40 ในช่วงปี 2019 เป็นต้นไปหรือไม่

เหตุผลที่คาดว่าจะใช้ได้คือแต่ละชั้นทำหน้าที่ต่างกัน: Canary ลดงบความเสี่ยง, sleeves กระจายสินทรัพย์, relative momentum เลือกกลุ่มหุ้นที่แข็งแรง และ trend gate ลดการถือสินทรัพย์ขาลง

## 3. ขั้นตอนการทดลอง

- ล็อกกติกาและเกณฑ์ผ่านก่อนรัน
- ใช้สัญญาณสิ้นเดือน `t` กับผลตอบแทนเดือน `t+1`
- Development สิ้นสุดธันวาคม 2018 และ Untouched test เริ่มมกราคม 2019
- คิดต้นทุน 0.10% ต่อมูลค่าที่ซื้อหรือขาย และทดสอบ 0.20% เพิ่ม
- รันสามครั้งเท่านั้น: SMA 10 baseline และ sensitivity SMA 9/11
- เปรียบเทียบกับ strategic buy-and-hold, 60/40 SPY/IEF และ SPY

## 4. ผลลัพธ์

ช่วง Untouched test baseline ให้ CAGR หลังต้นทุน 3.15%, volatility 6.86%, Sharpe 0.21 และ maximum drawdown -20.07% ขณะที่ 60/40 ให้ CAGR 10.86%, Sharpe 0.86 และ drawdown -20.52%

ระบบจึงลด drawdown จาก 60/40 เพียงเล็กน้อย แต่เสียผลตอบแทนและ risk-adjusted return มาก ต้นทุนลด CAGR จาก 4.34% เหลือ 3.15% เพราะ two-sided turnover ประมาณ 11.58 เท่าต่อปี

SMA 9 และ 11 ให้ผลใกล้ baseline และผ่าน sensitivity rule อย่างไรก็ตาม 5 เดือนที่ดีที่สุดสร้างกำไรสะสม 90.63% ของช่วง test และเมื่อตัด 10 เดือนที่ดีที่สุด CAGR กลายเป็น -1.47%

## 5. อภิปรายผล ปัญหา และข้อจำกัด

ผลไม่ได้ชี้ว่าแนวคิดแต่ละชั้นไม่มีเหตุผล แต่ชี้ว่าการซ้อน Canary กับ trend gate ในรูปปัจจุบันทำให้พอร์ตอยู่ Defensive เฉลี่ย 51.30% และเกิดการสลับสูง ระบบจึงรับ upside น้อยแต่ยังไม่ตัด drawdown ปีที่ยากได้มากพอ

ข้อมูลมาจาก Yahoo Finance แหล่งเดียว การซื้อขายจริงอาจต่างจาก monthly adjusted close และต้นทุนคงที่เป็นเพียงสมมติฐาน นอกจากนี้ช่วง test 92 เดือนยังสั้นเมื่อเทียบกับ MinTRL ที่ประมาณได้ 759 เดือน

## 6. สรุปและแนวทางต่อไป

คำตัดสินคือ `revise` เพราะไม่ผ่าน Sharpe และ maximum drawdown rule แม้ CAGR เป็นบวกและ sensitivity ผ่าน

ก่อนสร้าง v2 ควรแยก attribution ของ Canary, trend gate และการ rebalance เพื่อดูว่าชั้นใดสร้างการลดความเสี่ยงจริงและชั้นใดสร้าง turnover จากนั้นจึงกำหนดกฎลด turnover ล่วงหน้า เช่น rebalance threshold โดยไม่ย้อนกลับไปเลือกค่าจากผล v1

