# 003 — Return-Target Experiments And Rejected v3

## 1. ข้อมูลพื้นฐาน

- วันที่: 2026-09-18
- เป้าหมาย: CAGR 15–20% และ Sharpe มากกว่า 1
- แผนก่อนรัน: `b1d63f9e3c32931d455258d472f2fb98549da038`
- Frozen v3: `8c828cc869c846af4bfd4cd262b34f9ee4370a2c`

## 2. ปัญหาและสมมติฐาน

ทดสอบว่าการลดการป้องกัน, partial trend, cross-asset ranking, blended defense หรือ volatility targeting สามารถยกระดับผลตอบแทนและ Sharpe ของ v2 ได้หรือไม่

## 3. ขั้นตอนการทดลอง

เปลี่ยนทีละพารามิเตอร์ ใช้ median จากสาม Research blocks เลือกกติกา และ freeze ก่อนเปิดผลปี 2023–2026 Volatility targeting ใช้ข้อมูลย้อนหลัง 12 เดือนแบบ lag หนึ่งเดือน, SHY เป็น financing proxy และ leverage ไม่เกิน 2 เท่า

## 4. ผลลัพธ์

มีเพียง volatility targeting ที่ผ่าน Research rule จึงกลายเป็น v3 แต่ recent holdout ให้ CAGR 1.97%, Sharpe -0.08 และ drawdown -18.79% ด้วย leverage เฉลี่ย 1.90 เท่า High-cost CAGR ติดลบ -0.26%

ตลอดปี 2008–2026 v3 ให้ CAGR 8.27%, Sharpe 0.59 และ maximum drawdown -37.60% ยังต่ำกว่าเป้าหมายอย่างมาก

## 5. อภิปรายผล ปัญหา และข้อจำกัด

Leverage ไม่สามารถสร้าง Sharpe ได้ หาก signal เดิมไม่มี edge สม่ำเสมอ Q10 ทำได้ดีในปี 2008–2012 แต่เสื่อมต่อเนื่องใน block หลัง ส่วน Q6 ทำได้ดีที่สุดใน recent holdoutทั้งที่ไม่ผ่านกฎเลือก แสดง regime dependence ชัดเจน

ช่วง recent holdout สั้นและไม่ใช่ untouched ระดับโครงการ เพราะผล v1/v2 เคยถูกเปิดดูแล้ว จึงใช้ได้เป็น stress check ไม่ใช่หลักฐานยืนยัน deployability

## 6. สรุปและแนวทางต่อไป

คำตัดสิน v3 คือ `reject` และยังไม่สร้าง paper plan ควรหยุดเพิ่ม leverage และพารามิเตอร์ จนกว่าจะอธิบาย return source ที่อยู่รอดข้ามหลาย regime ได้

