# Camellia Multi-Layer TAA — Five-Experiment Plan For v2

วันที่ตรึงแผน: `2026-09-18`

## เป้าหมาย

อธิบายสาเหตุที่ v1 มี Sharpe ต่ำ, ถือ Defensive มาก และมี turnover สูง โดยเปลี่ยนพารามิเตอร์ครั้งละหนึ่งตัวจาก baseline v1 ห้ามเลือกค่าจากผลช่วง Untouched test

## การควบคุมการทดลอง

- ใช้ data snapshot เดิม SHA-256 `9ca48d680c4c5da36c3e061c02a990840a478150ca68407b1f6a9d22998b61d1`
- ใช้ต้นทุน 0.10% ต่อ notional ที่ซื้อหรือขาย
- ใช้ signal เดือน `t` กับ return เดือน `t+1`
- ตัวแปรที่ไม่ได้ระบุให้เปลี่ยนต้องเหมือน v1 ทุกข้อ
- ใช้ Development period ถึง `2018-12` สำหรับเลือกพารามิเตอร์เข้า v2 เท่านั้น
- Freeze v2 ก่อนเปิดดูผล Untouched test ตั้งแต่ `2019-01`
- รายงานการทดลองครบทั้งห้าครั้ง ไม่ตัดผลที่ไม่สนับสนุนสมมติฐานออก

## ตัวแปรตามมาตรฐาน

- Primary metric: Development-period Sharpe หลังต้นทุน เทียบ SHY
- Secondary metrics: net CAGR, maximum drawdown, annual two-sided turnover, gross/net CAGR spread, average Canary CF และ average total Defensive allocation
- Reality checks หลัง freeze: Untouched-test metrics เดิมทั้งหมด, high-cost scenario และ top-month PnL concentration

## คำถามที่ 1 — Breadth Protection Level

**คำถาม:** การเปลี่ยน `B` จาก 2 เป็น 3 ซึ่งทำให้ Canary สามตัวมีน้ำหนักเสียงเท่ากัน จะลดการป้องกันที่เร็วเกินไปและเพิ่ม CAGR/Sharpe ได้หรือไม่ โดย drawdown ยังไม่เกินขอบเขตเดิม?

- ตัวแปรต้น: `B=3` แทน `B=2`
- กติกาใหม่เฉพาะจุด: `CF=min(1,b/3)` จึงได้ 0%, 33.33%, 66.67%, 100%
- ตัวแปรตามที่เน้น: Sharpe, CAGR, maximum drawdown, average Canary CF และ average total Defensive allocation

## คำถามที่ 2 — Sleeve Trend Gate Ablation

**คำถาม:** การปิด 10-month SMA trend gate ระดับ Sleeve จะลดการป้องกันซ้ำซ้อนและเพิ่ม CAGR/Sharpe ได้หรือไม่ โดยยังใช้ Canary gate ควบคุมความเสี่ยงรวม?

- ตัวแปรต้น: trend gate `disabled` แทน SMA 10 เดือน
- Canary, allocation, ranking และ Defensive policy คงเดิม
- ตัวแปรตามที่เน้น: Sharpe, CAGR, maximum drawdown, turnover และ average total Defensive allocation

## คำถามที่ 3 — U.S. Top Assets Count

**คำถาม:** การเพิ่ม `T` จาก 1 เป็น 2 และแบ่ง U.S. Equity Sleeve เท่ากันระหว่างสองอันดับแรก จะลด concentration/rotation และเพิ่ม Sharpe ได้หรือไม่?

- ตัวแปรต้น: `T=2` แทน `T=1`
- น้ำหนัก U.S. Equity 40% คงเดิม โดยแบ่ง 20%/20% ภายใน Risky budget
- ตัวแปรตามที่เน้น: Sharpe, CAGR, maximum drawdown และ turnover

## คำถามที่ 4 — Defensive Universe Policy

**คำถาม:** การใช้ `SHY` เพียงตัวเดียวแทนการหมุน `SHY/IEF/LQD` จะลด turnover และป้องกัน duration/credit surprise ได้หรือไม่ โดยไม่ทำให้ CAGR/Sharpe ลดลง?

- ตัวแปรต้น: Defensive policy `SHY-only` แทน momentum-ranked `SHY/IEF/LQD`
- ตัวแปรตามที่เน้น: turnover, gross/net CAGR spread, Sharpe, CAGR และ maximum drawdown

## คำถามที่ 5 — Rebalance Threshold

**คำถาม:** การข้ามทั้งรอบ rebalance เมื่อ one-way target change ต่ำกว่า 5% ของพอร์ต จะลด turnover/cost drag และเพิ่ม net CAGR/Sharpe ได้หรือไม่ โดยไม่เพิ่ม drawdown มาก?

- ตัวแปรต้น: portfolio-level rebalance threshold `5%` แทน `0%`
- กติกาใหม่เฉพาะจุด: หาก `sum(abs(target-pretrade))/2 < 5%` ให้คง pretrade weights ทั้งหมดในเดือนนั้น มิฉะนั้น rebalance ไป target เต็มจำนวน
- ตัวแปรตามที่เน้น: turnover, gross/net CAGR spread, Sharpe, CAGR และ maximum drawdown

## กฎสร้าง Baseline v2 — ตรึงก่อนรัน

แต่ละพารามิเตอร์มีสิทธิ์เข้า v2 เมื่อ Development period เป็นไปตามทุกข้อ:

1. Sharpe สูงกว่า v1
2. Net CAGR มากกว่าศูนย์
3. Maximum drawdown ไม่เกิน 20%

นำพารามิเตอร์ที่ผ่านทั้งหมดมารวมเป็น candidate v2 แล้วตรวจเฉพาะ Development period:

- หาก candidate v2 มี Sharpe สูงกว่า v1, CAGR มากกว่าศูนย์ และ drawdown ไม่เกิน 20% ให้ freeze candidate นั้นเป็น v2
- หาก candidate รวมไม่ผ่าน ให้ใช้การทดลองเดี่ยวที่ผ่านและมี Development Sharpe สูงสุด
- หากไม่มีการทดลองใดผ่าน ให้คงสถาปัตยกรรม v1 และใช้เฉพาะการทดลองที่ลด turnover มากที่สุดโดย CAGR ไม่ลดและ drawdown ไม่เกิน 20%; หากไม่มีเช่นกัน ให้หยุดโดยไม่สร้าง v2 เชิงผลลัพธ์

หลัง freeze แล้วจึงคำนวณ Untouched-test result ของทั้งห้าการทดลองและ v2 เพื่อรายงาน แต่ห้ามย้อนกลับไปเปลี่ยน v2 จากผล test
