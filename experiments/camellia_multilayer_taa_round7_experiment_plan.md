# Camellia Multi-Layer TAA — Advisor Experiment Plan (Q26–Q28)

วันที่ตรึงแผน: `2026-09-18`

## เป้าหมายและขอบเขต

รอบนี้ทดสอบคำแนะนำที่ได้จาก Fable 5.1 และการทบทวนหลักฐานเดิม โดยใช้ Camellia v5 เป็น baseline และไม่ผสมพอร์ต 60/40 ไม่ใช้ leverage, short หรือ options

- สัญญาณสิ้นเดือน `t` รับผลตอบแทนเดือน `t+1`
- Base cost 0.10% และ high-cost stress 0.20% ต่อ notional ที่ซื้อหรือขาย
- Rebalance threshold 5%
- ใช้ข้อมูลและ Research blocks เดิม: `2008-08–2012-12`, `2013-01–2018-12`, `2019-01–2022-12`
- ช่วง `2023-01–2026-08` เป็น recent diagnostic ซึ่งจะเปิดดูหลังตรึงผล Research เท่านั้น
- ใช้ data snapshot เดิมจากงานวิจัยรอบ v6 เพื่อไม่ให้การเปลี่ยนข้อมูลปะปนกับผลของกติกา
- รอบนี้มี 3 candidate แบบแยกเดี่ยว ไม่มีการสร้าง candidate ผสมภายหลังเห็นผล

งานวิจัยนี้เรียกว่า round 7 เพื่อไม่เขียนทับหลักฐาน Q21–Q25 แต่ถ้าผ่านจะสร้าง strategy version 6 เพราะรอบก่อนถูกปฏิเสธและไม่เคยสร้าง strategy v6

## Baseline v5

- Canary: VWO, BND, TIP ด้วย `13612W`
- `CF=min(1, weak_count/2)`
- Risky allocation: VTI 40%, Regional 20%, DBC 10%, VNQ 10%, IEF 10%, TLT 10%
- Regional: เลือกไม่เกินสองตัวที่ `13612W > 0` จาก VGK, EWJ, IPAC, VWO
- Defensive: SHY 50%, conditional IEF 25%, conditional GLD/DBC 25%

## Q26 — Selective Canary Response

คำถาม: การให้ Canary ลดเฉพาะความเสี่ยงที่มันมีเหตุผลรองรับ จะรักษาผลตอบแทนได้ดีกว่าการลดทุก sleeve พร้อมกันหรือไม่?

- VWO อ่อนแอเพียงกลุ่มเดียว: ปิด VTI และ Regional; คง DBC, VNQ, IEF, TLT
- BND หรือ TIP อ่อนแอ โดย VWO ยังแข็งแรง: ปิด VNQ, IEF, TLT; คง VTI, Regional และ DBC
- VWO อ่อนแอพร้อมกับ BND หรือ TIP: เข้า Defensive 100%
- น้ำหนักที่ถูกปิดและน้ำหนัก Regional ที่ไม่มีผู้ชนะย้ายเข้า Defensive policy ของ v5
- Canary score และ Regional ranking ยังคงใช้ `13612W`

## Q27 — Structural Risk Budget

คำถาม: การเพิ่ม VTI และลด duration โดยไม่เพิ่ม leverage จะเพิ่มผลตอบแทนและ upside participation โดยไม่ทำลายประสิทธิภาพต่อความเสี่ยงหรือไม่?

- VTI 50%
- Regional 20%
- DBC 10%
- VNQ 10%
- IEF 5%
- TLT 5%
- Canary และ Defensive policy เหมือน v5

## Q28 — Slower Regional Ranking

คำถาม: การใช้ `13612` แบบไม่ถ่วงน้ำหนักเฉพาะ Regional ranking จะลดความไวต่อเดือนล่าสุด ลด turnover และเพิ่ม net compounding หรือไม่?

- Canary ยังคงใช้ `13612W`
- Regional ใช้ `(R1 + R3 + R6 + R12) / 4`
- กติกาอื่นเหมือน v5

## กระบวนการเลือกใหม่

ยกเลิกกฎ `ดีขึ้น 4 จาก 8` เพราะ Calmar, Ulcer และ drawdown ให้รางวัลพฤติกรรมด้านเดียวกันซ้ำหลายครั้ง

Candidate ต้องผ่าน hard guardrails ทุกข้อ:

1. Base-cost CAGR และ high-cost CAGR เป็นบวกทุก Research block
2. Worst Research maximum drawdown ไม่ต่ำกว่า -20%
3. Median CAGR ไม่ต่ำกว่า v5 เกิน 0.25 จุดเปอร์เซ็นต์
4. Median upside beta ต่อ SPY ไม่ต่ำกว่า v5 เกิน 0.03
5. Median two-sided turnover ไม่เกิน 1.15 เท่าของ v5
6. Median gross-net CAGR spread ไม่สูงกว่า v5 เกิน 0.25 จุดเปอร์เซ็นต์

Candidate ที่ผ่าน hard guardrails ต้องทำให้ทั้ง median Sharpe และ median risk-matched CAGR สูงกว่า v5 จึงจะรับได้ โดย risk-matched CAGR เป็น diagnostic ที่ปรับ excess return ของแต่ละ block ให้มี volatility เท่ากับ v5 block เดียวกัน ไม่ใช่กติกา leverage ที่นำไปเทรด

ถ้ามีมากกว่าหนึ่ง candidate ผ่าน ให้เลือก median Sharpe สูงสุด; หากเท่ากันให้เลือก turnover ต่ำกว่า ไม่มีการรวมกติกาจากหลาย candidate ในรอบนี้

รายงาน DSR ด้วยจำนวนการทดลองสะสม `28` ครั้ง (Q1–Q28) เพื่อเปิดเผยผลของ multiple testing แต่ไม่ใช้ DSR เป็นด่านผ่าน เพราะ trial returns จากงานเดิมไม่ได้ถูกเก็บครบพอสำหรับประเมินความสัมพันธ์ระหว่างการทดลองอย่างแม่นยำ

## Recent และคำตัดสิน

หลังเลือกและ freeze จาก Research blocks แล้ว จึงเปิด recent diagnostic และ full period

Strategy v6 จะได้สถานะ `paper_ready` เมื่อ:

1. มี candidate ที่ผ่านกระบวนการเลือกข้างต้น
2. Recent base/high-cost CAGR เป็นบวก
3. Recent maximum drawdown ไม่ต่ำกว่า -20% และ downside beta ต่อ SPY ต่ำกว่า 1
4. Full CAGR ไม่ต่ำกว่า v5 เกิน 0.25 จุดเปอร์เซ็นต์
5. Full Sharpe และ full risk-matched CAGR สูงกว่า v5
6. Full turnover ไม่เกิน 1.15 เท่าของ v5 และ full high-cost CAGR เป็นบวก

หากไม่มี candidate ผ่าน ให้คง v5 เป็น active strategy และบันทึกรอบนี้เป็น `reject` โดยไม่สร้าง strategy v6
