# 007 — Camellia v6 Selective Canary Research

## 1. ข้อมูลพื้นฐาน

- วันที่: 2026-09-18
- ผู้ทดลอง: Codex ร่วมกับเจ้าของโครงการ
- กลยุทธ์: Camellia Multi-Layer TAA v5 เป็น baseline
- แผนก่อนรัน: `0ec56ed0b1fd331a373967e1a113b42220c96889`
- ตัวรัน: `7b96c40e1d1436dd9cc3d4eca4ee851b60d022ec`
- Freeze ก่อนเปิด recent: `f8b156e28a7e6877414fafb17034941e5ad1a420`
- ข้อมูล: Yahoo Finance adjusted close; 2008-08 ถึง 2026-08

## 2. ปัญหาและสมมติฐาน

ทดสอบสามคำถามจากคำแนะนำภายนอก: Canary ควรลดเฉพาะความเสี่ยงที่เกี่ยวข้องหรือไม่, การเพิ่ม VTI และลด duration จะเพิ่มคุณภาพผลตอบแทนหรือไม่ และ Regional ranking ที่ช้าลงจะลด whipsaw ได้โดยไม่เสีย compounding หรือไม่

## 3. ขั้นตอนการทดลอง

ลงทะเบียน Q26–Q28 และเกณฑ์ใหม่ก่อนรัน ยกเลิกกฎดีขึ้นสี่จากแปดเพื่อลดการนับ drawdown ซ้ำ ใช้สาม Research blocks เดิม ต้นทุน 0.10% และ stress 0.20% สัญญาณสิ้นเดือนรับผลเดือนถัดไป ไม่มีการรวม candidate หลังเห็นผล และนับจำนวนการทดลองสะสม Q1–Q28 สำหรับ DSR โดยประมาณ

## 4. ผลลัพธ์

Q26 ผ่านทุก guardrail และทั้งสอง efficiency tests: median Research CAGR 8.17% เทียบ v5 6.29%, Sharpe 0.99 เทียบ 0.86 และ risk-matched CAGR 7.42% เทียบ 6.29% Worst block drawdown ลึกขึ้นจาก -9.27% เป็น -12.12%

Q27 เพิ่ม median CAGR เป็น 6.56% แต่ Sharpe ลดเหลือ 0.82 และ risk-matched CAGR เหลือ 5.78% Q28 ลด turnover เหลือ 6.88x แต่ median CAGR 5.98% ต่ำกว่า guardrail และ risk-matched CAGR 6.04% ไม่ดีขึ้น

หลัง freeze Q26 แล้ว ช่วงเต็มให้ CAGR 7.50%, Sharpe 0.83, MDD -14.44%, turnover 7.79x และ high-cost CAGR 6.67% ช่วง recent ให้ CAGR 7.69%, Sharpe 0.60 และ MDD -5.51% จึงผ่านระดับ `paper_ready`

## 5. อภิปรายผล ปัญหา และข้อจำกัด

Q26 สนับสนุนแนวคิดว่า Canary มีประโยชน์มากขึ้นเมื่อใช้บอกว่า “ควรตัดอะไร” แทนการใช้ลดทุกสินทรัพย์พร้อมกัน แต่ผลไม่ได้ชนะทุกช่วง: ปี 2013–2018 CAGR ลดจาก 4.32% เป็น 3.67% และ Sharpe ลดจาก 0.95 เป็น 0.62 Full-period drawdown และ recovery แย่กว่า v5 จึงต้องติดตามเป็นความเสี่ยงหลัก

Recent period เคยถูกเปิดดูในรอบก่อนแล้ว จึงไม่ใช่ holdout อิสระ DSR 28 trials ใช้การกระจาย Sharpe ของ candidate ปัจจุบันเพราะไม่มี return series ของทุก trial เก่า จึงเป็นเพียงค่าประมาณ และ backtest/paper trade ไม่รับประกันผลในอนาคต

## 6. สรุปและแนวทางต่อไป

คำตัดสิน: `paper_ready` สร้าง Camellia v6 จาก Q26 และให้แทน v5 เป็น baseline ปัจจุบัน ขั้นต่อไปคือจัดทำ paper-trading plan แยกต่างหาก โดยติดตาม MDD, recovery, สัดส่วนเวลาของแต่ละ Canary state และความต่างระหว่าง proposed กับ simulated fill ห้ามเชื่อม credential หรือส่งคำสั่งโดยไม่มีการอนุมัติใหม่
