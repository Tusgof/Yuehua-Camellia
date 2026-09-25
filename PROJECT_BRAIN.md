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
- กลยุทธ์ที่กำลังทำ: `camellia_multilayer_taa` v6 สถานะ `paper_ready`; ใช้ Selective Canary response เพื่อตัด equity เมื่อ VWO เตือน ตัดสินทรัพย์ไวต่อดอกเบี้ยเมื่อ BND/TIP เตือน และเข้า Defensive เต็มเมื่อทั้งสองกลุ่มเตือน
- กลยุทธ์ใน paper trade: Q30 Challenge adapter เริ่ม owner-manual paper trade เมื่อ `2026-09-18`; v6 internal shadow ยังไม่เริ่มลง ledger
- ผลล่าสุด: v6 ช่วงเต็ม CAGR 7.50%, Sharpe 0.83, maximum drawdown -14.44% และ turnover 7.79x; recent diagnostic CAGR 7.69%, Sharpe 0.60 และ maximum drawdown -5.51%
- Research round 7: Q26 Selective Canary ผ่านเกณฑ์ใหม่และสร้าง strategy v6; Q27 Structural Risk Budget และ Q28 Slower Regional Ranking ถูกปฏิเสธ
- Camellia Growth round 8: `reject`; Q29–Q32 ไม่มี candidate ผ่านเกณฑ์ครบ จึงไม่สร้าง v7 โดย Q30 Aggressive Risk-On เป็น shadow candidate ที่น่าติดตามแต่ยังไม่รับ allocation
- Webull: ย้ายองค์ความรู้จาก Lily แล้ว; production read-only เคยยืนยันใน Lily. การตรวจ Camellia วันที่ `2026-09-25` พบ key/secret ใน process environment และสร้าง token ได้ แต่ token ยัง `PENDING` รอ 2FA ในแอป จึงยังไม่ได้อ่านบัญชีหรือ metadata. ตรวจซ้ำด้วย `py -3.11 scripts/check_webull_read_only.py` หลังเจ้าของยืนยันในแอป; สคริปต์จำกัดเฉพาะ read-only และไม่พิมพ์ข้อมูลบัญชี
- Webull MOO: เอกสาร Thailand OpenAPI วันที่ `2026-09-25` มี `MARKET`, `LIMIT`, `STOP_LOSS`, `STOP_LOSS_LIMIT` และ `DAY`/`GTC` แต่ไม่มี native Market-on-Open; `MARKET`+`DAY`+`CORE` ไม่ใช่ MOO. ดู `docs/WEBULL_OPENAPI.md`
- Webull Challenge: ไม่พบ paper-order API จึงใช้ owner-manual execution; DBC, IPAC, PDBC, COMT และ BCI ไม่อยู่ใน Challenge whitelist จึงใช้ VWO แทน IPAC และ GLD/XLE แทน DBC เฉพาะพอร์ต Challenge ตาม `paper_trading/q30_challenge_fills_2026-09-18.json`
- Webull options: เอกสารทางการระบุว่ารองรับ US single-leg options; permission และข้อมูลตลาดของบัญชีเจ้าของยังไม่ยืนยัน

## ขั้นต่อไป

ติดตาม Q30 Challenge adapter จาก owner-confirmed fills ใน `paper_trading/ledger.csv` และ `paper_trading/q30_challenge_fills_2026-09-18.json`; สร้าง v6 internal shadow แยกภายหลังโดยห้ามอนุมาน fill จากสินทรัพย์ทดแทนของ Challenge

เมื่อต้องเริ่ม paper trade ให้อ่าน `docs/WEBULL_OPENAPI.md` และเริ่มจาก offline adapter กับ read-only check ห้ามกระโดดไป order endpoint

## แหล่งหลักด้านวิธีวิจัย

โปรเจกต์ใช้เนื้อหาใน local LLM Wiki เป็นหลัก โดยเฉพาะ `strategy-research-workflow`, `train-test-validation-for-time-series`, `backtest-validation-protocol` และ `lookahead-leakage`
