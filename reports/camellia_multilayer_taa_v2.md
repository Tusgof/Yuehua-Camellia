# Backtest Report: camellia_multilayer_taa v2

## Reproduction And Freeze

- Evidence type: five isolated historical experiments followed by frozen v2 evaluation
- Experiment plan commit: `fc1fda7b2dfb5cb662a4bdf62a1da8376cbd75e1`
- Runner commit: `50f3b5541193050017ef130966403bab96c704a1`
- Frozen-before-test commit: `9c5ab9d981f50995529205f666789a8b4e5988ef`
- Data snapshot SHA-256: `9ca48d680c4c5da36c3e061c02a990840a478150ca68407b1f6a9d22998b61d1`
- Evaluation timestamp: `2026-09-18T10:11:39.7581452Z`
- Development: `2008-05` ถึง `2018-12`
- Untouched test for this experiment cycle: `2019-01` ถึง `2026-08`

v2 ถูกเลือกจาก Development period เท่านั้น จากนั้น commit configuration ก่อนเปิดผล Test

## Five Questions And Answers

| Question / independent variable | Development result vs v1 | Test result vs v1 | Answer |
|:--|:--|:--|:--|
| Q1: `B=3` แทน `B=2` | CAGR 5.08% vs 5.48%, Sharpe 0.59 vs 0.68, MDD ใกล้เดิม | CAGR 4.28%, Sharpe 0.37, MDD -16.77% | ไม่ผ่านกฎเลือกจาก Development แม้ Test ภายหลังดีขึ้นมาก แสดง regime instability |
| Q2: ปิด Sleeve trend gate | CAGR 8.33%, Sharpe 0.89, MDD -13.27% | CAGR 4.03%, Sharpe 0.31, MDD -19.41% | สนับสนุนสมมติฐาน การป้องกันซ้ำซ้อนลดผลตอบแทนและ Sharpe |
| Q3: U.S. `T=2` แทน `T=1` | CAGR 5.71%, Sharpe 0.71, MDD -7.48% | CAGR 2.60%, Sharpe 0.13, MDD -19.23% | ผล Development ดีแต่ไม่อยู่รอดใน Test; diversification ลด edge ของ winner ในช่วงหลัง |
| Q4: Defensive เป็น `SHY-only` | Turnover ลดเหลือ 8.26x แต่ CAGR/Sharpe ลดเป็น 3.73%/0.48 | CAGR 3.25%, Sharpe 0.24, MDD -12.98%, turnover 7.85x | ลด turnover และ drawdown ได้จริง แต่ผลตอบแทน Development อ่อน จึงไม่ผ่านกฎเลือก |
| Q5: rebalance threshold 5% | Sharpe เพิ่มเล็กน้อย 0.675→0.682; turnover 12.44x→12.42x | CAGR/Sharpe ลดเล็กน้อย; turnover 11.58x→11.55x | ข้ามรอบเล็กได้ แต่ turnover หลักมาจากการเปลี่ยน target ขนาดใหญ่ จึงแก้ปัญหาได้น้อย |

## Development Selection

Q2, Q3 และ Q5 ผ่านกฎ Development ที่ตรึงไว้ จึงถูกรวมเป็น baseline v2:

- ปิด Sleeve trend gate
- เลือก U.S. top two และแบ่งน้ำหนักเท่ากัน
- ใช้ portfolio rebalance threshold 5%

Candidate รวมให้ Development CAGR 8.03%, Sharpe 0.87, MDD -13.05% และ annual two-sided turnover 10.31x จึงผ่านกฎ freeze

## Untouched-Test Result

| Metric | v1 | Frozen v2 | Change |
|:--|--:|--:|--:|
| Net CAGR | 3.15% | 3.31% | +0.16 จุดเปอร์เซ็นต์ |
| Gross CAGR | 4.34% | 4.33% | -0.01 จุดเปอร์เซ็นต์ |
| Cost drag | 1.20% | 1.02% | ดีขึ้น 0.18 จุดเปอร์เซ็นต์ |
| Sharpe | 0.210 | 0.212 | แทบไม่เปลี่ยน |
| Annual volatility | 6.86% | 7.53% | สูงขึ้น 0.67 จุดเปอร์เซ็นต์ |
| Maximum drawdown | -20.07% | -19.76% | ดีขึ้น 0.31 จุดเปอร์เซ็นต์ |
| Annual two-sided turnover | 11.58x | 9.84x | ลดลง 15.0% |
| Average total Defensive | 51.30% | 39.67% | ลดลง 11.63 จุดเปอร์เซ็นต์ |
| Longest underwater | 60 เดือน | 60 เดือน | ไม่เปลี่ยน |
| High-cost CAGR | 1.96% | 2.30% | +0.34 จุดเปอร์เซ็นต์ |

## Reality Checks

- v2 ผ่านเพดาน maximum drawdown 20% แต่ Sharpe 0.21 ยังต่ำกว่า 60/40 ที่ประมาณ 0.86 มาก
- v2 ลด turnover ได้จริง แต่กำไรสุทธิเพิ่มเพียงเล็กน้อย เพราะ gross CAGR ไม่ดีขึ้น
- Five-best-month PnL share เพิ่มจาก 90.63% เป็น 94.15%; เมื่อตัดห้าเดือนนั้น CAGR เหลือ 0.35%
- PSR เทียบ Sharpe ศูนย์เท่ากับ 71.87%, DSR ประมาณ 61.17% และ MinTRL 736 เดือน เทียบกับ Test จริง 92 เดือน
- Q1 และ Q4 ทำได้ดีใน Test ทั้งที่ไม่ผ่าน Development rule ส่วน Q3 กลับทิศจากดีเป็นแย่ นี่เป็นหลักฐานว่าความสัมพันธ์ของพารามิเตอร์ไม่เสถียรข้าม regime
- การคง freeze rule ป้องกันไม่ให้นำ Q1/Q4 มาใส่ v2 หลังเห็นผล แต่ผลของสองคำถามยังถูกเปิดเผยครบ

## Decision

Decision: `revise`

v2 ดีกว่า v1 ด้านต้นทุน, turnover และ drawdown เล็กน้อย แต่ไม่แก้ปัญหา Sharpe ต่ำ, underwater 60 เดือน หรือการพึ่งพาเดือนกำไรสูงสุด จึงยังไม่พร้อม paper trade

ข้อค้นพบสำคัญที่สุดคือการปิด Sleeve trend gate มีผลเชิงบวกค่อนข้างสม่ำเสมอ ขณะที่ `T=2`, `B`, Defensive policy และ threshold แสดง regime dependence สูง การวิจัยรอบถัดไปควรใช้ walk-forward หรือหลายช่วงเวลา แทนการเลือกจาก split เดียว
