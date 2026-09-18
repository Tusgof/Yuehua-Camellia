# 005 — Webull Return Sources And Camellia v5

## 1. ข้อมูลพื้นฐาน

- วันที่: 2026-09-18
- เป้าหมาย: พัฒนา Camellia เป็นพอร์ตเดี่ยว เพิ่มแหล่งผลตอบแทนนอกหุ้นสหรัฐฯ และใช้เฉพาะ ETF ใหม่ที่มีหลักฐานว่า Webull Thailand รองรับ
- แผนก่อนรัน: `8a2413221f8dd4cecc2a57712d718f2d44c23d3b`
- ตัวรัน: `fc5e8abd4701c704a4d656cad3ea1e3187bebf2f`
- Frozen v5: `b58134b2e78aea39be6388a6ea8d41b5316d1dcf`
- ข้อมูล: Yahoo Finance adjusted close, 2006-01 ถึง 2026-09; ผลที่ใช้ประเมิน 2008-08 ถึง 2026-08

## 2. ปัญหาและสมมติฐาน

v4 ป้องกันขาลงได้ดีขึ้นแต่ยังฟื้นตัวช้าและมีส่วนร่วมในขาขึ้นไม่มาก รอบนี้จึงถามห้าคำถาม: เปลี่ยน market-cap rotation เป็น VTI คงที่, ตัด defensive pocket ทีละส่วน, ใส่ rank buffer, เพิ่ม alternative macro sleeve และเพิ่ม regional equity sleeve

สมมติฐานหลักคือ return engine ที่เรียบง่ายขึ้นร่วมกับหุ้นภูมิภาคจะลด timing error และเพิ่มแหล่งผลตอบแทน โดยไม่ทำลายหน้าที่ของ Canary และ Defensive policy

## 3. ขั้นตอนการทดลอง

ใช้สัญญาณสิ้นเดือน `t` รับผลตอบแทนเดือน `t+1` คิดต้นทุน 0.10% ต่อมูลค่าที่ซื้อหรือขาย และ stress ที่ 0.20% ใช้ Research blocks สามช่วง ได้แก่ 2008–2012, 2013–2018 และ 2019–2022 ก่อน freeze แล้วจึงเปิด recent diagnostic ปี 2023–2026

ผู้สมัครต้องมีกำไรหลังต้นทุนและ high-cost ทุกช่วง, drawdown ไม่ต่ำกว่า -30%, ไม่เสีย CAGR/drawdown/downside beta/turnover เกินเพดาน และดีขึ้นอย่างน้อยสี่จากแปดมิติ ETF ที่เริ่มภายหลังเข้าร่วม ranking เมื่อมีข้อมูลจริงครบ 12 เดือน โดยไม่เติม proxy ย้อนหลัง

## 4. ผลลัพธ์

Q16, Q18 และ Q20 ผ่านเกณฑ์ ส่วน Q17a, Q17b และ Q19 ไม่ผ่าน Q17a ลด median CAGR เหลือ 4.06% Q17b ดีขึ้นเพียงสองมิติ และ Q19 แม้ลดความเสี่ยงหลายด้านแต่ median CAGR ลดเหลือ 5.82% จนผิด guardrail

กฎรวมที่ตรึงไว้เลือก Q16 ก่อน Q18 และรวม Q20 จึงได้ v5 ที่ถือ VTI คงที่ 40% ของ Risky budget และใช้ 20% หมุนระหว่าง VGK, EWJ, IPAC และ VWO ไม่เกินสองตัวที่โมเมนตัมเป็นบวก ส่วน Defensive policy คงแบบ v4

ช่วงเต็ม v5 ให้ CAGR 6.47%, Sharpe 0.74, Sortino 1.67, maximum drawdown -11.79%, Calmar 0.55, recovery 37 เดือน และ turnover 8.33 เท่าต่อปี ช่วงล่าสุดให้ CAGR 5.75%, Sharpe 0.34, maximum drawdown -8.13% และ high-cost CAGR 4.68%

## 5. อภิปรายผล ปัญหา และข้อจำกัด

v5 ดีขึ้นจาก v4 ทั้ง CAGR, ความผันผวน, Sharpe, Sortino, drawdown, Calmar, เวลาฟื้นตัว และการกระจุกตัวของกำไร โดย turnover เพิ่มเพียงเล็กน้อย ผลจึงสนับสนุนว่าการลด market-cap timing และกระจายหุ้นตามภูมิภาคมีประโยชน์ร่วมกัน

อย่างไรก็ตาม CAGR ยังไม่สูงใกล้ 15–20% และ recent Sharpe ยังต่ำกว่า 1 ผลช่วงล่าสุดไม่ใช่ untouched holdout เพราะเคยถูกเปิดดูในรุ่นก่อน อีกทั้งราคา backtest มาจาก Yahoo ไม่ใช่ Webull fill จริง สถานะ Webull ที่ใช้เป็น metadata แบบ read-only ที่บันทึกไว้เท่านั้น ไม่มีการอ่าน credential หรือเรียก API ในรอบนี้

## 6. สรุปและแนวทางต่อไป

กำหนด v5 เป็น `paper_ready` เพราะผ่าน Research rules, recent safety และเกณฑ์ช่วงเต็มทั้งหมด ความหมายคือพร้อมให้เจ้าของพิจารณาแผน paper trade แยกต่างหาก ไม่ใช่การอนุมัติให้เชื่อมบัญชีหรือส่งคำสั่ง

ขั้นต่อไปควรสร้าง offline adapter ที่แปลงสัญญาณรายเดือนเป็น proposed orders พร้อมเพดานขนาดสถานะ เงื่อนไขหยุด และบันทึก simulated fill จากนั้นจึงขออนุมัติสำหรับ read-only Webull validation เป็น milestone ใหม่
