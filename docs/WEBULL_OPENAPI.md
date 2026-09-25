# คู่มือ Webull OpenAPI สำหรับ Camellia

อัปเดตล่าสุด: `2026-09-25`

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

เจ้าของบัญชียืนยันผ่านหน้าแอป Webull Thailand เมื่อ `2026-09-18` เพิ่มเติมว่า ETF ต่อไปนี้ค้นหาเจอ ซื้อขายได้ และรองรับ fractional shares:

- DBMF
- KMLM
- CTA

หลักฐานชุดนี้เป็นคำยืนยันจากเจ้าของ ไม่ใช่ผลตอบกลับจาก OpenAPI จึงไม่ควรตีความเป็นการยืนยันค่า `status=OC`, minimum notional, spread, liquidity หรือคุณภาพราคา fill

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

## Paper Trading Challenge 2026

ตรวจหน้ากิจกรรมและ Terms and Conditions ทางการเมื่อ `2026-09-18`:

- กิจกรรมใช้บัญชีทดลองเฉพาะการแข่งขัน เงินเริ่มต้น USD 20,000
- เลือกได้เพียงหนึ่งสนามและเปลี่ยนภายหลังไม่ได้
- สนามหุ้นและ ETF ใช้คำสั่งระหว่างเวลาซื้อขายปกติและจับคู่ที่ Bid/Ask แบบ real-time
- จำกัดสูงสุด 300 คำสั่งต่อวันทำการ
- รายชื่อหลักทรัพย์ที่เข้าแข่งขันอยู่หลังหน้า login
- Terms ไม่ได้ระบุการส่งคำสั่งผ่าน OpenAPI

เอกสาร OpenAPI ทางการระบุ account type เพียง `CASH` และ account class `INDIVIDUAL_CASH` และไม่มี paper/simulated/Challenge account หรือ paper-order endpoint ดังนั้น Camellia ถือว่า **Challenge ไม่รองรับการส่งคำสั่งผ่าน API** จนกว่า Webull จะมีเอกสารทางการหรือ endpoint ที่พิสูจน์ตรงกันข้าม ห้ามใช้ production brokerage order endpoint ทดลองกับ Challenge

การตรวจ read-only เมื่อ `2026-09-18` พบว่า environment ยังมี App Key/Secret แต่ token directory เดิมไม่มีอยู่แล้ว SDK ไม่ตอบกลับภายใน 30 วินาที จึงหยุดโดยไม่อ่าน payload บัญชีและไม่เรียก preview/place/replace/cancel

การตรวจ Camellia อีกครั้งเมื่อ `2026-09-25` ใช้ Python 3.11.9 และ SDK 2.0.13: key/secret มีใน process environment, host `api.webull.co.th` ติดต่อได้, แต่ token ใหม่มีสถานะ `PENDING` หลังจำกัดเวลารอยืนยัน 12 วินาที จึงยังไม่ได้อ่าน account list, balance, positions หรือ instrument metadata และไม่มี order call ต้องให้เจ้าของยืนยันคำขอ OpenAPI ที่รู้จักในแอป Webull ก่อนเรียก read-only probe ซ้ำ ห้ามส่ง OTP ในแชต

หลังเจ้าของยืนยันคำขอในแอปวันที่ `2026-09-25` การเรียก probe ซ้ำสำเร็จ: authentication, account list, balance, positions และ instrument metadata ตอบกลับสำเร็จ บน Python 3.11.9 / SDK 2.0.13 / region `th` / host `api.webull.co.th`; VTI, EWJ, VWO, GLD, XLE, SHY, DBC และ IPAC คืน `status=OC` และ `fractionable=true` ทุกตัว เรียก read-only 4 endpoints และ order 0 ครั้ง ผลนี้ไม่ยืนยันสิทธิ์ส่ง order, ขั้นต่ำ fractional, ราคา fill หรือ MOO และไม่ได้บันทึกค่าบัญชีหรือ response ดิบลง repo

เมื่อเจ้าของอนุมัติให้ตรวจ `preview` วันที่ `2026-09-25` Camellia เรียก production preview endpoint สองครั้งกับ VTI จำนวน `0.01` หุ้น: `MARKET` + `DAY` + `CORE` ได้ HTTP 200 และมี estimated cost/fee; `MOO` ถูกปฏิเสธด้วย `OPENAPI_PARAM_ERR` ทั้งสองครั้งเป็น preview และ `orders_sent=0` การทดสอบนี้ยืนยันว่าบัญชีและสิทธิ์ API ใช้ order preview ได้ แต่ยังไม่ใช่หลักฐานว่าส่งคำสั่งหรือจับคู่จริงได้

คำสั่งตรวจซ้ำจาก root โปรเจกต์:

```powershell
py -3.11 scripts/check_webull_read_only.py
```

สคริปต์จำกัดเวลารวม 40 วินาที ใช้เฉพาะ auth และ read-only endpoints ที่ระบุไว้ด้านล่าง เก็บ token ภายนอก repo ที่ `%LOCALAPPDATA%/Yuehua-Camellia/webull-token` และพิมพ์เฉพาะสถานะ endpoint กับ metadata สาธารณะของ ETF เมื่อสำเร็จ

## Market-on-Open (MOO) สำหรับบัญชีจริง

ตรวจเอกสาร Webull Thailand อย่างเป็นทางการเมื่อ `2026-09-25`: [Trading API Overview](https://developer.webull.co.th/apis/docs/trade-api/overview.md), [Stock Trading](https://developer.webull.co.th/apis/docs/trade-api/stock.md) และ [Place Order schema](https://developer.webull.co.th/apis/docs/reference/trade-api/common-order-place.md) ระบุ order type ของหุ้นสหรัฐฯ เพียง `MARKET`, `LIMIT`, `STOP_LOSS`, `STOP_LOSS_LIMIT`; `time_in_force` มี `DAY`/`GTC` และ `support_trading_session=CORE` หมายถึงช่วงเวลาซื้อขายปกติ ไม่ได้หมายถึงจับคู่ที่ราคาเปิด

ดังนั้น **ยังไม่มี native MOO ผ่าน Webull Thailand OpenAPI ตามเอกสารปัจจุบัน** และไม่ควรส่ง `MARKET` + `DAY` + `CORE` แล้วเรียกว่า MOO การตั้งเวลาส่ง market order หลังเปิดตลาดเป็นเพียงการประมาณ ซึ่งอาจได้ราคา/เวลาแตกต่างจาก opening auction; ยังไม่ใช่ความสามารถที่ทดสอบหรืออนุมัติให้ใช้งาน

## ตัวเลือกที่ปรับแต่งได้ในคำสั่งหุ้น

- `order_type`: `MARKET`, `LIMIT`, `STOP_LOSS`, `STOP_LOSS_LIMIT`
- `side`: `BUY` หรือ `SELL`
- `quantity`: จำนวนหน่วย รวมจำนวนทศนิยมสำหรับ fractional เมื่อโบรกเกอร์รองรับ
- `entrust_type`: `QTY` หรือ `AMOUNT` โดย `AMOUNT` ใช้สั่งเป็นมูลค่าเงินสำหรับ fractional US stocks
- `limit_price`: ใช้กับ `LIMIT` และ `STOP_LOSS_LIMIT`
- `stop_price`: ใช้กับ `STOP_LOSS` และ `STOP_LOSS_LIMIT`
- `time_in_force`: `DAY` หรือ `GTC`
- `support_trading_session`: `CORE`, `ALL`, `NIGHT` หรือ `ALL_DAY` ตามสิทธิ์และช่วงเวลาที่รองรับ
- `client_order_id`: รหัสอ้างอิงของเราที่ไม่ซ้ำกัน ความยาวไม่เกิน 32 ตัวอักษร

สำหรับ Camellia การส่งคำสั่งเชิงระบบที่เหมาะสมคือสร้าง order preview ก่อนทุกครั้ง ตรวจ estimated cost/fee และค่อยแยกงาน place order ที่ได้รับอนุมัติเป็นครั้ง ๆ ส่วน MOO ยังไม่มีค่าที่ใช้งานได้ใน schema หรือ preview ของบัญชีนี้

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
