# คู่มือ Webull OpenAPI สำหรับ Camellia

อัปเดตล่าสุด: `2026-09-18`

เอกสารนี้ย้ายเฉพาะความรู้ที่ใช้ซ้ำได้จาก Lily และตรวจข้อมูลปัจจุบันจากเอกสารทางการ ไม่ย้าย credential, token, Account ID, response ดิบ หรือระบบ governance ของ Lily

## สรุปแบบสั้น

Webull Thailand เป็นตัวเลือกหลักสำหรับการทดลองพอร์ตจำลองของ Camellia เพราะบัญชีของเจ้าของเคยผ่านการเชื่อมต่อแบบอ่านอย่างเดียวใน Lily แล้ว และ ETF ที่ตรวจสิบตัวแสดงว่าสามารถซื้อแบบเศษหน่วยได้

Camellia จะใช้ Webull ตามลำดับนี้:

```text
โค้ดจำลองที่ไม่ต่อเครือข่าย
        ↓
อ่านบัญชีและข้อมูลตลาดเท่านั้น
        ↓
พอร์ตจำลองภายใน Camellia — ไม่ส่ง order ไป Webull
        ↓
Order preview เฉพาะเมื่อเจ้าของอนุมัติเป็นงานแยก
        ↓
Live order อยู่นอกขอบเขตปัจจุบัน
```

คำว่า `paper trade` ใน Camellia หมายถึงการจำลองสถานะและราคา fill ภายในโปรเจกต์ ไม่ได้หมายความว่า Webull Thailand มี paper account/API ที่เรายืนยันแล้ว

## สิ่งที่ยืนยันจากบัญชีจริงแล้ว

Lily ตรวจ production API เมื่อ `2026-07-15` โดยใช้ region `th`, host `api.webull.co.th`, Python 3.11 และ SDK 2.0.13 ผลที่ยืนยันได้คือ:

- authentication สำเร็จ
- อ่าน account list, balance และ positions ได้
- อ่าน instrument metadata ได้
- VTI, VGK, EWJ, IPAC, VWO, IEF, SCHP, GLDM, PDBC และ VNQI คืน `status=OC` และ `fractionable=true`
- ไม่มีการเรียก preview/place/replace/cancel และไม่มี order ถูกส่ง
- ไม่มี credential, token, Account ID, ยอดเงิน หรือรายการถือครองถูกบันทึกลง Git

หลักฐานต้นทาง:

- Lily `reports/feasibility/l_0_webull_th_read_only_capability.json`
- Lily `reports/feasibility/l_0_webull_th_read_only_capability.md`
- Producing commit: `4d109be190ff28339c5d142958623f0b7e06299e`

ข้อจำกัด: ผลดังกล่าวยืนยัน “ความสามารถในการอ่าน” ณ วันตรวจเท่านั้น ไม่ยืนยันขั้นต่ำต่อคำสั่ง ราคา fill, slippage, ค่าแลก THB/USD, ค่าธรรมเนียมจริง หรือความพร้อมของกลยุทธ์

## สถานะ API ปัจจุบันจากเอกสารทางการ

ตรวจเมื่อ `2026-09-18`:

- Trading API ของ Webull Thailand ระบุว่ารองรับ US stocks และ US single-leg options
- หุ้นและ options ใช้ unified order endpoints เดียวกัน โดยแยกด้วย `instrument_type`
- options ใช้ `instrument_type: OPTION`, `option_strategy: SINGLE` และส่งรายละเอียดใน `legs`
- เอกสารระบุ order type สำหรับ options ได้แก่ `MARKET`, `LIMIT`, `STOP_LOSS` และ `STOP_LOSS_LIMIT`
- รองรับจำนวนแบบ `QTY` หรือจำนวนสัญญา และ time-in-force `DAY`/`GTC`
- เอกสารแสดง endpoint สำหรับ option contracts, tick, snapshot และ historical bars
- เอกสารเตือนว่า OpenAPI option market-data access ต้องมี paid subscription และ subscription module ยังอยู่ระหว่างพัฒนา
- Python SDK ทางการรองรับ Python 3.8–3.14
- SDK release ล่าสุดที่ตรวจพบคือ `3.0.1` เผยแพร่ `2026-09-16`

สิ่งเหล่านี้เป็นความสามารถตามเอกสาร ไม่ใช่หลักฐานว่าบัญชี Webull Thailand ของเจ้าของมี permission หรือ subscription นั้นแล้ว

## สิ่งที่ยังไม่ยืนยัน

- permission ซื้อขาย options ของบัญชีเจ้าของ
- entitlement สำหรับ option market data และราคาของ subscription
- ความพร้อมของ option historical bars สำหรับ backtest ที่เราต้องการ
- minimum fractional quantity หรือ minimum notional ต่อคำสั่ง
- ราคา fill, spread, slippage และค่าธรรมเนียมที่เกิดจริง
- ต้นทุนแปลงเงินบาทเป็นดอลลาร์
- สิทธิ์ใช้ UAT/test account ของเจ้าของ
- Webull paper-trading endpoint ที่เหมาะกับบัญชีไทย

Lily เคยลองยืนยัน UAT แล้ว authentication ไม่เข้าสู่สถานะพร้อมภายในเวลาที่กำหนด และไม่พบขั้นตอนสาธารณะสำหรับจัดสรร test account ที่เจ้าของควบคุมได้ ดังนั้น hostname UAT เป็นเพียงข้อมูลอ้างอิง ไม่ใช่สิทธิ์ใช้งานที่ยืนยันแล้ว

## การตั้งค่า credential

Camellia ใช้ชื่อตัวแปรของตัวเองเพื่อไม่ให้ปะปนกับโปรเจกต์อื่น:

- `CAMELLIA_WEBULL_APP_KEY`
- `CAMELLIA_WEBULL_APP_SECRET`
- `CAMELLIA_WEBULL_ACCOUNT_ID`
- `CAMELLIA_WEBULL_TOKEN_DIR`
- `CAMELLIA_WEBULL_ENV`

แนวทางที่ต้องใช้:

1. ตั้งค่าเป็น **User environment variables** ของ Windows ไม่ใช่ System variables เพราะเป็น credential ของผู้ใช้คนเดียว
2. ห้ามใส่ค่าจริงใน `.env.example`, source code, test, report, screenshot หรือ chat
3. token directory ต้องอยู่นอก repo เช่น `%LOCALAPPDATA%/Yuehua-Camellia/webull-token`
4. log แสดงได้เพียงว่าค่ามีหรือไม่มี ห้ามแสดงบางส่วนของ secret หากไม่จำเป็น
5. Account ID ถือเป็นข้อมูลส่วนตัว แม้ไม่ใช่ secret
6. Camellia ห้ามอ่าน credential จนกว่าจะมีงานเชื่อม API ที่เจ้าของอนุมัติ
7. ค่าเริ่มต้นของ `CAMELLIA_WEBULL_ENV` คือ `disabled`; เปลี่ยนเป็น production read-only ได้เฉพาะในงานที่อนุมัติแล้ว

ดูชื่อค่าตัวอย่างได้จาก `.env.example` แต่ห้ามแทน placeholder ด้วยค่าจริงในไฟล์ที่ track โดย Git

## ลำดับการพัฒนาที่อนุญาต

### W0 — Offline adapter

- pin SDK version เมื่อเริ่ม implement จริง ไม่ pin ตามความทรงจำจาก Lily
- เขียน adapter หลัง interface ของ Camellia เพื่อเปลี่ยน provider ได้
- ใช้ fake response ใน tests
- network และ credential เป็นศูนย์

### W1 — Read-only capability check

- ขออนุมัติเจ้าของก่อนอ่าน credential
- ตรวจ authentication และ endpoint ที่จำเป็นเท่านั้น
- เริ่มจาก account list, balance, positions และ instrument/market-data metadata
- ไม่เก็บ response ดิบหรือข้อมูลบัญชีลง Git
- ไม่มี order endpoint

### W2 — Internal paper trade

- ใช้สัญญาณจากกลยุทธ์และข้อมูลราคาที่อนุมัติ
- บันทึก proposed order ลง `paper_trading/ledger.csv`
- จำลอง fill และต้นทุนภายใน Camellia
- ไม่เรียก preview/place/replace/cancel ของ Webull

### W3 — Preview probe

- เป็นงานแยกและต้องได้รับอนุมัติเจ้าของ
- ตรวจ environment, account, symbol, side, quantity และ price ก่อน request
- จำกัดจำนวน request และปิด automatic retry
- preview ไม่ใช่ fill และไม่พิสูจน์คุณภาพ execution

### W4 — Live trading

อยู่นอกแผนปัจจุบัน ต้องมี milestone และการอนุมัติใหม่โดยเฉพาะ ห้ามนำ flag ตัวเดียวมาใช้ปลดล็อก live order

## Endpoint ที่เคยใช้แบบอ่านอย่างเดียว

รายการนี้มาจากหลักฐาน Lily และต้องตรวจเทียบเอกสาร/SDK อีกครั้งเมื่อ implement เพราะ API อาจเปลี่ยน:

- `/openapi/auth/token/create`
- `/openapi/auth/token/check`
- `/openapi/auth/token/refresh`
- `/openapi/account/list`
- `/openapi/assets/balance`
- `/openapi/assets/positions`
- `/openapi/instrument/stock/list`

อย่าคัดลอก order path หรือ request shape เก่าจาก Lily โดยตรง เพราะ Lily ใช้ SDK 2.0.13 และเคยพบความต่างระหว่าง path ใน helper ของ SDK กับเอกสาร Webull Thailand

## กฎสำหรับ options

ก่อนเขียน options adapter ต้องตรวจอย่างน้อย:

- permission และ market-data entitlement ของบัญชี
- contract multiplier, expiration, strike, call/put และ OCC symbol
- bid/ask ไม่ใช่ใช้ราคากลางอย่างเดียว
- position intent เช่น `BUY_TO_OPEN`/`SELL_TO_CLOSE`
- assignment/exercise, วันหมดอายุ และสภาพคล่อง
- fee ต่อสัญญาและ slippage ต่อขา

เริ่มจาก single-leg เท่านั้นตามเอกสารปัจจุบัน ห้ามสมมติว่า multi-leg, spread หรือ complex order รองรับ

## แหล่งอ้างอิง

แหล่งทางการ:

- <https://developer.webull.co.th/apis/docs/trade-api/overview>
- <https://developer.webull.co.th/apis/docs/trade-api/option>
- <https://developer.webull.co.th/apis/docs/sdk.md>
- <https://www.webull.co.th/open-api>
- <https://github.com/webull-inc/webull-openapi-python-sdk/releases/tag/3.0.1>

คู่มือภาษาไทยประกอบการใช้งาน:

- <https://github.com/nutdnuy/webull-openapi-thai-lab/tree/304f5aa1b2389a981f997ebe8481740db2bb00eb>

คู่มือภาษาไทยเป็น secondary source ใช้เพื่อเรียน workflow และ guardrails ส่วนความสามารถ API ให้ยึดเอกสาร Webull Thailand และผลตรวจบัญชีของเราเป็นหลัก
