# 002 — Five Experiments And Frozen Baseline v2

## 1. ข้อมูลพื้นฐาน

- วันที่: 2026-09-18
- กลยุทธ์: `camellia_multilayer_taa`
- Data snapshot: Yahoo Finance adjusted close, SHA-256 `9ca48d680c4c5da36c3e061c02a990840a478150ca68407b1f6a9d22998b61d1`
- แผนทดลองถูก commit ก่อนรันที่ `fc1fda7b2dfb5cb662a4bdf62a1da8376cbd75e1`
- v2 ถูก freeze ก่อนเปิด Test ที่ `9c5ab9d981f50995529205f666789a8b4e5988ef`

## 2. ปัญหาและสมมติฐาน

v1 มี Sharpe ต่ำ ถือ Defensive เฉลี่ยสูง และ turnover สูง จึงตั้งคำถามห้าข้อเพื่อแยกผลของ `B`, trend gate, จำนวน U.S. winners, Defensive policy และ rebalance threshold โดยเปลี่ยนครั้งละหนึ่งตัว

## 3. ขั้นตอนการทดลอง

ใช้ Development period ถึงปี 2018 เลือกพารามิเตอร์ตามกฎที่เขียนไว้ล่วงหน้า จากนั้นรวมตัวที่ผ่านและ commit เป็น v2 ก่อนเปิดผลปี 2019–2026 ไม่มีการย้อนเลือกจากผู้ชนะใน Test

## 4. ผลลัพธ์

Q2 ปิด trend gate, Q3 เลือก U.S. top two และ Q5 threshold 5% ผ่าน Development rule และถูกรวมเป็น v2 ส่วน Q1 `B=3` กับ Q4 `SHY-only` ไม่ผ่าน

บน Test v2 ให้ CAGR 3.31%, Sharpe 0.21, maximum drawdown -19.76% และ turnover 9.84x เทียบ v1 ที่ 3.15%, 0.21, -20.07% และ 11.58x ตามลำดับ

Q1 ซึ่งถูกคัดออกกลับให้ Test Sharpe 0.37 และ drawdown -16.77% ส่วน Q4 ให้ drawdown -12.98% ตรงกันข้าม Q3 ที่ผ่าน Development กลับมี Test Sharpe เพียง 0.13

## 5. อภิปรายผล ปัญหา และข้อจำกัด

ผลยืนยันว่าการซ้อน trend gate ลดการมีส่วนร่วมในตลาดมากเกินไป แต่พารามิเตอร์อื่นไม่เสถียรข้ามช่วงเวลา v2 ลดต้นทุนได้แต่ไม่ได้สร้าง gross edge เพิ่ม และยังพึ่งพาห้าเดือนที่ดีที่สุดถึง 94.15% ของกำไรสะสม

การทดลองห้าครั้งและ candidate รวมเพิ่มจำนวน trials ทำให้ผลเชิงสถิติยิ่งต้องตีความอย่างระวัง Data provider และ monthly-close execution limitation ยังคงเหมือน v1

## 6. สรุปและแนวทางต่อไป

คำตัดสิน v2 คือ `revise` ยังไม่สร้าง paper plan

รอบถัดไปควรทดสอบ stability ด้วย walk-forward หรือหลายช่วงเวลาที่กำหนดล่วงหน้า โดยให้ความสำคัญกับการแยกผลของ Canary breadth และ Defensive policy มากกว่าการเพิ่มพารามิเตอร์ใหม่
