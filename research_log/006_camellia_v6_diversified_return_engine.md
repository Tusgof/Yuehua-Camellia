# 006 — Diversified Return Engine Research Round

## 1. ข้อมูลพื้นฐาน

- วันที่: 2026-09-18
- เป้าหมาย: ทดสอบ Managed Futures, equal-risk regional, rank persistence, inflation defense และ Canary consensus โดยเก็บ v5 เป็น baseline
- แผนก่อนรัน: `41cb1fb2903e5a6667faa2e7b5a5109dcf53b2de`
- ตัวรัน Research: `0895e6c34f7bbe7b45ababfefaec5e0df890d96e`
- Freeze: `f71249e6d7692cc55b8aabe9e3c9596894b6f887`
- ข้อมูล: Yahoo Finance adjusted close; ช่วงประเมิน 2008-08 ถึง 2026-08

## 2. ปัญหาและสมมติฐาน

แม้ v5 ผ่านระดับ `paper_ready` แต่ยังพึ่งสินทรัพย์ long-only และมี Sharpe ช่วงล่าสุดต่ำ สมมติฐานรอบนี้คือ Managed Futures อาจเพิ่ม return source ที่ต่างจากหุ้นจริง ส่วน equal-risk, persistence, inflation-defense universe และ Canary consensus อาจเพิ่มคุณภาพพอร์ตโดยไม่ต้องใช้ leverage

## 3. ขั้นตอนการทดลอง

ตรึงคำถาม Q21–Q25 และเกณฑ์ผ่านก่อนดูผล ใช้สาม Research blocks เดิม คิดต้นทุนฐาน 0.10% และ stress 0.20% ต่อ notional สัญญาณสิ้นเดือนรับผลตอบแทนเดือนถัดไป ETF ที่เกิดภายหลังเข้าร่วมเมื่อมีข้อมูลจริงครบ 12 เดือนและไม่มี proxy backfill

เจ้าของยืนยันผ่านแอปว่า DBMF, KMLM และ CTA ซื้อขายและรองรับ fractional shares บน Webull Thailand แต่รอบนี้ไม่ได้อ่าน credential หรือเรียก API

## 4. ผลลัพธ์

ไม่มี candidate ผ่านเกณฑ์ Q21 ดีขึ้นเพียงหนึ่งจากแปดมิติ Q22 ไม่ดีขึ้น Q23 ดีขึ้นสามมิติ Q24 และ Q25 ดีขึ้นสี่มิติแต่ผิด CAGR guardrail และ Q25 ผิด drawdown guardrail เพิ่มด้วย จึง freeze ค่า `selected_config={}` และคง v5

หลัง freeze พบว่า Q21 ลด full-period drawdown จาก -11.79% เหลือ -10.11% แต่ CAGR ลดจาก 6.47% เหลือ 6.40% ช่วงล่าสุด CAGR 5.51% ต่ำกว่า v5 ที่ 5.75% Q25 ให้ผลช่วงล่าสุดสูงมาก แต่เป็นผลในข้อมูลที่เปิดดูแล้ว และ Research blocks ไม่ผ่าน จึงไม่เลือกย้อนหลัง

## 5. อภิปรายผล ปัญหา และข้อจำกัด

Managed Futures ยังเป็นแนวคิดที่มีเหตุผล แต่ DBMF เริ่มปี 2019, KMLM ปี 2020 และ CTA ปี 2022 ทำให้หลักฐานข้าม regime ไม่พอ การที่ Q21 ลด drawdown เป็นข้อมูลน่าติดตาม ไม่ใช่หลักฐานเพียงพอสำหรับเปลี่ยนระบบ

Rank persistence ลด turnover และเพิ่ม Calmar/PnL concentration แต่ผลตอบแทน Research ลดลง Inflation-defense universe วางสินทรัพย์ถูกตำแหน่งกว่ารอบ Q19 แต่ยังเสีย CAGR มาก Canary consensus แสดง regime dependence รุนแรงและไม่ควรนำผล recent ที่สวยมาใช้ลบผล Research ที่ล้มเหลว

ระหว่างงานแก้ simulator ให้ `NaN` ของสินทรัพย์น้ำหนักศูนย์ไม่ปนเปื้อน pre-trade weights และให้หยุดทันทีเมื่อสินทรัพย์ที่ถือจริงขาดผลตอบแทน ตัวเลข v5 หลังแก้ต่างจากเดิมเพียงระดับการปัดเศษ

## 6. สรุปและแนวทางต่อไป

คำตัดสินรอบ v6 คือ `reject` และคง Camellia v5 สถานะ `paper_ready` ไม่สร้าง strategy spec v6 ขั้นต่อไปควรเดิน paper trade ของ v5 และบันทึก Q21 เป็น shadow signal เพื่อสะสมหลักฐานไปข้างหน้า โดยยังไม่รวมเข้า allocation จริงหรือพอร์ตจำลองหลัก
