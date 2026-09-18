# 008 — Camellia Growth Research Round

## 1. ข้อมูลพื้นฐาน

- วันที่: 2026-09-18
- ผู้ทดลอง: Codex ร่วมกับเจ้าของโครงการ
- Baseline: Camellia v6
- แผนก่อนรัน: `a1110d656aafcdf8dcdf1c8d288b7ee86ae2851a`
- ตัวรัน: `6377f3deb3b9d5fc73a3a32a8b55cef993b49ef5`
- Freeze: `dcf4b24d968dab3bdbdf77a1944bbea0dc550a1f`
- ข้อมูล: Yahoo Finance adjusted close; 2008-08 ถึง 2026-08

## 2. ปัญหาและสมมติฐาน

เจ้าของรับ downside ได้ประมาณ 20–25% จึงทดลองใช้ risk capacity ที่ v6 ยังไม่ได้ใช้ผ่าน Partial Canary cuts, Aggressive Risk-On allocation, Sector satellite และ conditional 1.20x overlay โดยไม่ยกเลิก Selective Canary

## 3. ขั้นตอนการทดลอง

ลงทะเบียน Q29–Q32 และเกณฑ์ก่อนรัน ใช้สาม Research blocks เดิม คิดต้นทุนซื้อขาย 0.10% และ stress 0.20% Q32 คิด financing จาก SHY บวก 2% ต่อปีและ stress 4% ไม่มีการรวม candidate หลังเห็นผล และ freeze ค่า `selected_config={}` ก่อนเปิด recent เพราะไม่มี candidate ผ่านครบ

## 4. ผลลัพธ์

Q29, Q31 และ Q32 เพิ่มผลตอบแทนไม่ถึงขั้นต่ำหรือทำให้ผลตอบแทนลดลง Q30 ให้ median CAGR 9.54% เทียบ v6 8.17%, Sharpe 0.92, worst MDD -13.93% และ turnover 8.30x แต่ risk-matched CAGR 7.65% ต่ำกว่า v6 8.17% เกินกรอบที่ยอมรับ จึงไม่ผ่าน

หลัง freeze Q30 ให้ full CAGR 9.33%, Sharpe 0.86, MDD -15.40% และ recent CAGR 9.99% ตัวเลขเหล่านี้น่าสนใจแต่ไม่สามารถนำมาย้อนคำตัดสิน Research ได้

## 5. อภิปรายผล ปัญหา และข้อจำกัด

Q30 แสดงว่าการเพิ่ม VTI และตัด strategic duration เพิ่ม raw return ได้ทุก Research block โดย drawdown ยังต่ำกว่าเพดานมาก แต่ผลตอบแทนที่เพิ่มส่วนหนึ่งมาจาก volatility และ equity beta ที่สูงขึ้น ไม่ใช่ edge ใหม่ทั้งหมด

ช่วง recent เคยถูกเปิดดูแล้ว การสร้าง v7 จากตัวเลข post-freeze จะเป็น selection bias Q31 ยังขาดหลักฐานซื้อขายบน Webull และ Q32 ยังขาดข้อมูล margin/borrowing rate จริง DSR ใช้ trial count สะสม 32 ครั้งแต่ยังเป็นค่าประมาณเพราะไม่มี correlation ของทุก trial เก่า

## 6. สรุปและแนวทางต่อไป

คำตัดสิน: `reject` และคง v6 เป็น active `paper_ready` strategy ไม่สร้าง v7 Q30 สามารถเดินเป็น shadow signal แบบ allocation ศูนย์ระหว่าง paper trade ของ v6 เพื่อเก็บ forward evidence โดยต้องแยก ledger และห้ามเรียกผล shadow ว่าผล paper strategy ที่ได้รับการยอมรับแล้ว
