# PROJECT_BRAIN

## เป้าหมาย

Camellia นำกลยุทธ์จากแหล่งภายนอกมาทำให้เป็นกติกาที่ทดสอบซ้ำได้ ทดสอบย้อนหลังอย่างรวดเร็วแต่ไม่หลอกตัวเอง และนำเฉพาะกลยุทธ์ที่ผ่านเกณฑ์ไปทดลองในพอร์ตจำลอง

## สิ่งที่โปรเจกต์นี้ไม่ใช่

- ไม่ใช่งานค้นคว้ากลไกตลาดเชิงลึกแบบ Lily
- ไม่ใช่โรงงานปรับพารามิเตอร์เพื่อหาเส้นผลตอบแทนที่สวยที่สุด
- ไม่ใช่ระบบส่งคำสั่งเงินจริง
- ไม่ต้องใช้ locked gates, evidence tiers หรือ tracker หลายชั้นกับงานทั่วไป

## วิธีตัดสินใจ

แต่ละกลยุทธ์ต้องมี:

1. แหล่งที่มาและเหตุผลที่น่าจะใช้ได้
2. กติกาที่ทำซ้ำได้ รวมเวลาเกิดสัญญาณและเวลาส่งคำสั่ง
3. เกณฑ์ผ่านที่เขียนก่อน backtest
4. ผลหลังต้นทุนและการเปรียบเทียบกับวิธีพื้นฐานที่เหมาะสม
5. การทดสอบบนช่วงเวลาภายหลังที่ไม่ได้ใช้ปรับกติกา
6. คำตัดสินเดียว: `reject`, `revise`, `paper_ready`, `paper_trading` หรือ `retired`

อนุญาตให้ลองรุ่นพื้นฐานหนึ่งรุ่นและรุ่นปรับแก้ที่มีเหตุผลไม่เกินสองรุ่นต่อแนวคิด หากต้องลองมากกว่านั้นให้ถือว่าเป็นงานวิจัยใหม่ ไม่ใช่การปรับเล็กน้อย

## ขอบเขตความปลอดภัย

- ข้อมูลลับอยู่ใน environment variables เท่านั้น
- ห้ามเก็บเลขบัญชี token หรือ API secret ใน Git
- การเชื่อมต่อโบรกเกอร์เริ่มด้วย read-only หรือ paper environment เท่านั้น
- ทุกคำสั่งซื้อ paper ต้องมีเพดานขนาดสถานะและเงื่อนไขหยุด
- Live trading ต้องเป็น milestone ใหม่และต้องได้รับอนุมัติจากเจ้าของ

## สถานะปัจจุบัน

- โครงสร้างโปรเจกต์: พร้อมใช้งานและมีตัวตรวจพื้นฐาน
- กลยุทธ์ที่กำลังทำ: `camellia_multilayer_taa` v4 สถานะ `revise`; ใช้ Defensive policy แยก SHY, deflation และ inflation pocket โดยไม่ใช้ leverage
- กลยุทธ์ใน paper trade: ยังไม่มี
- ผลล่าสุด: v4 ช่วงเต็ม CAGR 6.18%, Sharpe 0.63, maximum drawdown -12.48% และ turnover 8.24x; recent diagnostic CAGR 4.49%, Sharpe 0.14 และ maximum drawdown -10.70%
- Webull: ย้ายองค์ความรู้จาก Lily แล้ว; production read-only เคยยืนยันใน Lily แต่ Camellia ยังไม่อ่าน credential หรือเชื่อม API
- Webull options: เอกสารทางการระบุว่ารองรับ US single-leg options; permission และข้อมูลตลาดของบัญชีเจ้าของยังไม่ยืนยัน

## ขั้นต่อไป

เก็บ Defensive policy ของ v4 แล้วทดสอบ return engine ที่เรียบง่ายกว่า โดยเริ่มจาก fixed SPY เทียบกับ market-cap rotation ตามแผนที่ตรึงล่วงหน้า ห้ามเลือกย้อนหลังจาก attribution รอบ v4

เมื่อต้องเริ่ม paper trade ให้อ่าน `docs/WEBULL_OPENAPI.md` และเริ่มจาก offline adapter กับ read-only check ห้ามกระโดดไป order endpoint

## แหล่งหลักด้านวิธีวิจัย

โปรเจกต์ใช้เนื้อหาใน local LLM Wiki เป็นหลัก โดยเฉพาะ `strategy-research-workflow`, `train-test-validation-for-time-series`, `backtest-validation-protocol` และ `lookahead-leakage`
