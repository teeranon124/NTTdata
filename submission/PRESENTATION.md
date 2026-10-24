# AutoProcure.AI
### Autonomous MRO Procurement & Negotiation Agent
**NTT DATA Digital Innovation Challenge 2026 — Final Submission**

- **หัวข้อการแข่งขัน:** Manufacturing
- **ทีม:** ข้าวต้มมัดไส้กล้วย (Khaotom Mat Sai Kluai)
- **Repository:** github.com/teeranon124/NTTdata (branch `main`)

---

## 1. Project Name

**AutoProcure.AI** — ระบบ Multi-Agent อัตโนมัติสำหรับบริหารและ**เจรจาต่อรองราคา**จัดซื้ออะไหล่ซ่อมบำรุงโรงงาน (MRO Tail-Spend) แบบ End-to-End ตั้งแต่รวบรวมใบขอซื้อ → เจรจากับซัพพลายเออร์ด้วย AI → ออกใบสั่งซื้อเข้า SAP

---

## 2. Use Case / Pain Point (Problem Statement)

### ปัญหา: "Tail-Spend" ในงานจัดซื้อ MRO ของโรงงานอุตสาหกรรม

โรงงานผลิตมีใบขอซื้ออะไหล่ซ่อมบำรุง (MRO) กระจัดกระจายจำนวนมหาศาล แต่ละใบมูลค่าต่ำ ความถี่สูง ซึ่งเป็น "หางของการใช้จ่าย" (tail-spend) ที่มักถูกละเลย เกิดปัญหา:

| ปัญหา | ผลกระทบ |
| :--- | :--- |
| **ซื้อแบบ Spot Buy แยกใบ** | ไม่มีอำนาจต่อรอง จ่ายแพงกว่าราคาตลาด |
| **ไม่มีเวลาเจรจาทุกใบ** | ฝ่ายจัดซื้อมีคนจำกัด เจรจา tail-spend ไม่ไหว |
| **ราคากลางไม่โปร่งใส** | ซัพพลายเออร์ตั้งราคาเผื่อต่อ อ้างต้นทุนสูง |
| **ไม่มี audit trail** | ตรวจสอบย้อนหลัง/ธรรมาภิบาลทำได้ยาก |

> **บริบทจริงในโครงการ:** รวบรวม **2,489 ใบขอซื้อ (PRs)** จาก **5 โรงงาน** (นิคมฯ ชลบุรี/ระยอง/อยุธยา) มูลค่ารวม **฿172.6 ล้าน/ปี** — เป็นงบที่รั่วไหลเพราะไม่ถูกจัดการเชิงกลยุทธ์

---

## 3. Proposed Solution (AWS Solution)

**AutoProcure.AI** เปลี่ยน tail-spend ที่กระจัดกระจายให้เป็น**ดีลเชิงกลยุทธ์** แล้วให้ AI Agent เจรจาต่อรองอัตโนมัติ 24/7:

1. **Spend Aggregation** — รวบ 2,489 PRs → **61 ดีลเชิงกลยุทธ์** (Blanket Order / LTA รายปี)
2. **Autonomous Multi-Agent Negotiation** — AI เจรจากับซัพพลายเออร์เป็นภาษาไทยเชิงพาณิชย์ อ้างอิงราคากลางตลาด (BATNA) และทฤษฎีเกม (Nash Bargaining)
3. **Closed-Loop to SAP** — เมื่อตกลงได้ → เลื่อนสถานะดีลอัตโนมัติ → CPO ลงนาม (Human-in-the-Loop) → ยิง `BAPI_PO_CREATE1` ออกใบสั่งซื้อเข้า SAP S/4HANA

### จุดเด่นเชิงวิศวกรรม
- **True Multi-Agent Orchestration** — แยก 5 agent ตามหน้าที่ (Compliance → Router → Market Intel → Negotiator → Arbitrator)
- **Dynamic Model Gateway** — เลือกโมเดลตามความยากของงาน (คุม cost)
- **Multi-Vendor Award Board** — เทียบหลายซัพพลายเออร์ จัดอันดับ BAFO Winner ด้วย TCO Score + Consistency Guard
- **Anti-Stall SLA Monitor** — กันการ "ดองแชท" ด้วยการเฝ้าระวัง SLA
- **Guardrails** — ป้องกัน Prompt Injection (ตาม AWS Bedrock best practices) + เพดานราคาที่ AI ข้ามไม่ได้

---

## 4. AI Technologies Used

| เทคโนโลยี | บทบาท |
| :--- | :--- |
| **Amazon Bedrock (Converse API)** | แกนกลางเรียก LLM แบบ unified |
| **Amazon Nova Micro** | Router/Intent Agent (FAST tier) — สกัดเจตนา + 5 เงื่อนไขพาณิชย์ |
| **Amazon Nova Pro** | Strategic Negotiator (STRONG tier) — เจรจาภาษาไทย + โน้มน้าว |
| **Amazon Bedrock Guardrails** | Prompt Injection defense (ApplyGuardrail + inline Converse) |
| **Dynamic Model Gateway** | Routing โมเดลตามความซับซ้อนของ task (cost optimization) |
| **Game Theory (Nash Bargaining)** | เครื่องยนต์คำนวณจุดแลกเปลี่ยน Win-Win |
| **TCO Engine (NPV, WACC 7%)** | คำนวณต้นทุนรวมจากราคา + เครดิตเทอม |

---

## 5. AWS Architecture & Services Used

ดูแผนภาพ: `submission/ARCHITECTURE.md` (Mermaid diagram)

### AWS Services
| Service | การใช้งาน |
| :--- | :--- |
| **Amazon Bedrock** | LLM inference (Nova Micro + Nova Pro) ผ่าน Converse API |
| **Amazon Bedrock Guardrails** | กรอง Prompt Injection / content policy |
| **AWS App Runner / ECS Fargate** | รัน container (serverless, pay-as-you-go) |
| **Amazon ECR** | เก็บ Docker image (`autoprocure:latest`) |
| **Amazon RDS (PostgreSQL)** | ฐานข้อมูลเชิงสัมพันธ์ (Deals, Vendors, Sessions, MessageLog, AuditTrail) |
| **Amazon SES** | ส่ง RFQ Magic Link ให้ซัพพลายเออร์ |
| **AWS Secrets Manager** | เก็บ DB credentials / API keys |
| **Amazon CloudWatch** | Logs & metrics |

### Tech Stack
Python 3.12 · Flask · SQLAlchemy ORM · Gunicorn (gthread) · boto3 · Server-Sent Events (SSE) · Docker (multi-stage, non-root)

### Data Flow
```
PR Ingestion (5 โรงงาน) → Spend Aggregation (61 ดีล)
   → AWS SES (RFQ Magic Link) → Supplier Portal
   → Multi-Agent Pipeline [Compliance → Router(Nova Micro) → Market Intel → Negotiator(Nova Pro) → Arbitrator]
   → SSE live cockpit (Buyer) → CPO Sign-off (HITL)
   → SAP S/4HANA (BAPI_PO_CREATE1)
```

---

## 6. AWS Pricing / Cost Estimation

> ประมาณการ region `us-east-1` — อ้างอิงราคา public ของ AWS/Bedrock
> ตรวจสอบเพิ่มเติมที่ **AWS Pricing Calculator**: https://calculator.aws/

### 6.1 Compute — เลือก Serverless (Pay-as-you-go) อย่างมีเหตุผล
| ตัวเลือก | รูปแบบคิดเงิน | ค่าใช้จ่ายขณะ idle | ประมาณ/เดือน (POC) |
| :--- | :--- | :--- | :--- |
| EC2 t3.small (always-on) | รายชั่วโมง 24×7 | **จ่ายแม้ไม่ใช้** | ~$15–20 + ops |
| **Fargate (serverless)** | ต่อวินาที | scale-to-min | **~$7–12** |
| **App Runner (serverless)** | ต่อวินาที | idle ต่ำ | ~$10–18 |

**เหตุผล:** POC มีทราฟฟิกหลักสิบ request/วัน → serverless ไม่จ่ายค่า idle 24×7 และไม่ต้องดูแล server เอง

### 6.2 Model Tier — Dynamic Model Gateway (ตัวคุม cost หลัก)
| โมเดล | Tier | Input $/1M | Output $/1M |
| :--- | :--- | ---: | ---: |
| Amazon Nova Micro / Lite | FAST (งานเบา) | ~$0.035–0.06 | ~$0.14–0.24 |
| Amazon Nova Pro | STRONG (เจรจา) | ~$0.80 | ~$3.20 |
| Claude 3.5 Sonnet | STRONG (ทางเลือก) | ~$3.00 | ~$15.00 |

**กลยุทธ์:** งานเบา (parse/intent) → Nova Micro | งานหนัก (เจรจา) → Nova Pro → ประหยัด token อย่างมีนัยสำคัญเมื่อ scale ข้าม 2,489 PRs × หลายรอบ × หลายเจ้า

### 6.3 Supporting Services (POC ~ ต่อเดือน)
| Service | ประมาณ |
| :--- | :--- |
| RDS PostgreSQL (db.t4g.micro) | ~$13–16 |
| Amazon SES (<1k emails) | <$1 |
| ECR / CloudWatch | ~$2–4 |

**รวม POC: ระดับหลักสิบดอลลาร์/เดือน** — model inference คิดตามใช้จริง (fallback mode = $0)

---

## 7. Before vs. After Improvement

| มิติ | ❌ Before (Manual / Spot Buy) | ✅ After (AutoProcure.AI) |
| :--- | :--- | :--- |
| **การจัดการ tail-spend** | กระจัดกระจาย 2,489 ใบ ไม่มีอำนาจต่อรอง | รวบเป็น 61 ดีลกลยุทธ์ มี volume leverage |
| **การเจรจา** | คนทำไม่ไหว เจรจาแค่ดีลใหญ่ | AI เจรจาอัตโนมัติ 24/7 ทุกดีล |
| **ราคากลาง** | ไม่โปร่งใส ซัพพลายเออร์ตั้งเผื่อ | อ้างอิง Thai MRO Index + BATNA leverage |
| **เลือกผู้ชนะ** | ใช้ดุลยพินิจ | Award Board จัดอันดับ TCO Score เป็นกลาง |
| **ความปลอดภัย** | เสี่ยงถูกหลอก/สวมรอย | Guardrails + Magic Link token (anti-impersonation) |
| **Audit & ธรรมาภิบาล** | ตรวจย้อนหลังยาก | บันทึกทุก decision/model/cost + HITL sign-off |
| **ออก PO** | คีย์มือเข้า SAP | Closed-loop → BAPI_PO_CREATE1 อัตโนมัติ |

### 📊 ผลลัพธ์เชิงตัวเลข (จากข้อมูลจริงในระบบ)
- **ยอดใช้จ่ายที่บริหาร:** ฿172.6 ล้าน/ปี
- **มูลค่าที่ประหยัดได้:** **฿25.0 ล้าน (−14.5%)**
- **ครอบคลุม:** 2,489 PRs · 207,055 ชิ้น · 61 ดีล · 5 โรงงาน
- **ต้นทุน AWS:** หลักสิบดอลลาร์/เดือน (< 0.01% ของมูลค่าที่ประหยัด)

---

## Expected Benefits (ประโยชน์ที่คาดว่าจะได้รับ)

1. **ประหยัดงบจัดซื้อ MRO ~14.5%** จากการรวมยอด + เจรจาอัตโนมัติ
2. **ปลดภาระฝ่ายจัดซื้อ** — AI รับงาน tail-spend ที่คนทำไม่ไหว
3. **ธรรมาภิบาลโปร่งใส** — audit trail ครบ + HITL control ก่อนออก PO
4. **ขยายผลได้** — สถาปัตยกรรม multi-agent + serverless พร้อม scale สู่ production จริง
5. **ต้นทุนต่ำ** — pay-as-you-go + model tiering คุม cost ตั้งแต่วันแรก
