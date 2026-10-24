# AutoProcure.AI — Pitch Deck Outline (16 สไลด์)
### ออกแบบให้ตรงเกณฑ์ตัดสิน 6 ข้อของ NTT DATA Digital Innovation Challenge

> **วิธีใช้:** แต่ละ "SLIDE" = 1 หน้า นำไปวางใน Canva / Gamma / PowerPoint
> แต่ละสไลด์ระบุ: เนื้อหาบนสไลด์ · 🎙️ speaker note · 🎯 ตอบเกณฑ์ข้อไหน
> **ธีม:** น้ำเงินเข้ม `#0f172a` + ฟ้า `#2563eb` + เขียว `#059669` · ฟอนต์ Kanit/Inter

---

## 🗺️ Deck Map (เกณฑ์ → สไลด์)
| เกณฑ์กรรมการ | สไลด์ | น้ำหนัก |
| :--- | :--- | :--- |
| 01 Problem clarity | 2, 3 | ปานกลาง |
| 02 Agentic behavior | 6, 7, 8 | **สูงสุด** ⭐ |
| 03 Prototype completeness | 9, 10 | สูง |
| 04 Responsible AI & safety | 11 | สูง ⭐ |
| 05 Creativity & UX | 5, 12 | ปานกลาง |
| 06 Business / social value | 4, 13, 14 | **สูงสุด** ⭐ |
| ภาพรวม/ปิด | 1, 15, 16 | — |

**เวลารวม present: ~12–15 นาที** (สไลด์ 6-7 agentic และ 13-14 business ลงรายละเอียดมากสุด)

---

## SLIDE 1 — Title / Hook
- โลโก้ + ชื่อ **AutoProcure.AI**
- Tagline: *"Autonomous Procurement Agent ที่เจรจาต่อรองราคาแทนคุณ — บริหาร ฿172M, ประหยัด ฿25M"*
- Manufacturing · ทีมข้าวต้มมัดไส้กล้วย · NTT DATA DIC 2026

🎙️ *"ลองนึกภาพพนักงานจัดซื้อที่ไม่เคยพัก เจรจาได้ 24 ชม. กับซัพพลายเออร์ทุกราย — นั่นคือ AutoProcure.AI"*

---

## SLIDE 2 — The Problem: MRO Tail-Spend 🎯(01)
- นิยาม tail-spend: ใบขอซื้อย่อยเยอะ มูลค่า/ใบต่ำ ความถี่สูง
- ตัวเลขจริง: **2,489 PRs · 5 โรงงาน · ฿172.6M/ปี**
- Pain 4 ข้อ: ไม่มีอำนาจต่อรอง · คนจัดซื้อไม่พอ · ราคากลางไม่โปร่งใส · audit ยาก
- กราฟ Pareto: 80% ของจำนวนใบ = tail-spend ที่ถูกละเลย

🎙️ *"Tail-spend คือ 'หาง' ของการใช้จ่าย จำนวนใบเยอะแต่มูลค่า/ใบน้อย ฝ่ายจัดซื้อโฟกัสแต่ดีลใหญ่ ปล่อยหางนี้ซื้อแพงปีละ 172 ล้านบาท"*
🎯 เกณฑ์ 01: problem statement + ตัวเลขชัด

---

## SLIDE 3 — User Persona & Current Workflow 🎯(01)
- **Persona 1:** คุณสมชาย Category Manager — "มี tail-spend 60+ ดีล เจรจาได้แค่ 5 ดีลใหญ่"
- **Persona 2:** วิศวกรโรงงาน — "ต้องการอะไหล่ด่วน กระบวนการช้า"
- **Persona 3:** CPO — "ต้องการธรรมาภิบาล ตรวจสอบก่อนเซ็น"
- Workflow เดิม (เส้นแดง): PR กระจาย → spot buy → ไม่เจรจา → จ่ายแพง → ไม่มี audit

🎙️ *"ผู้ใช้หลักคือ Category Manager ที่จมกับใบขอซื้อ และ CPO ที่ต้องการความโปร่งใส"*
🎯 เกณฑ์ 01: user persona + simple workflow

---

## SLIDE 4 — Business Opportunity 🎯(06)
- **TAM/SAM/SOM funnel:**
  - TAM: MRO procurement ภาคผลิตไทย (EEC)
  - SAM: โรงงานกลาง-ใหญ่ที่มี SAP/ERP
  - SOM (เคสเรา): 5 โรงงาน = ฿172.6M tail-spend/ปี
- Value capture: ประหยัด 14.5% = ฿25M/ปี/กลุ่มโรงงาน
- **Revenue model (SaaS):** success-based (% of savings) หรือ subscription ต่อ seat

🎙️ *"นี่คือโมเดลธุรกิจจริง เราคิดค่าบริการแบบ success-based คือส่วนแบ่งจากเงินที่ลูกค้าประหยัดได้ ลูกค้าได้ประโยชน์ก่อนจ่าย"*
🎯 เกณฑ์ 06: measurable benefit + business model

---

## SLIDE 5 — Solution Overview (3 ขั้น) 🎯(05)
1. **AGGREGATE** — รวบ 2,489 ใบ → 61 ดีลกลยุทธ์ (สร้าง volume leverage)
2. **NEGOTIATE** — AI Multi-Agent เจรจาภาษาไทยเชิงพาณิชย์ 24/7
3. **CLOSE** — ปิดดีล → CPO เซ็น → ออก PO เข้า SAP อัตโนมัติ

🎙️ *"ระบบทำงาน 3 ขั้น: รวบยอดสร้างอำนาจต่อรอง, ให้ AI เจรจา, ปิดวงจรเข้า SAP — end-to-end จริง"*
🎯 เกณฑ์ 05: clear & easy to understand

---

## SLIDE 6 — Agentic Architecture: 5 Specialized Agents 🎯(02)⭐
แผนภาพ pipeline 5 agent (ลูกศรต่อกัน):
1. **Compliance Guardrail** — กัน injection + เพดานราคา
2. **Router (Nova Micro)** — สกัด intent + 5 เงื่อนไขพาณิชย์
3. **Market Intelligence** — RAG จาก Thai MRO Index → BATNA
4. **Strategic Negotiator (Nova Pro)** — Game Theory + โน้มน้าว
5. **Central Arbitrator** — TCO Score + BAFO ranking

ป้าย: *"True Multi-Agent, not single prompt"*

🎙️ *"หัวใจคือ Multi-Agent จริง — แยก AI 5 ตัวตามหน้าที่ ส่งต่องานเป็น pipeline ไม่ใช่ prompt เดียวครอบทุกอย่าง"*
🎯 เกณฑ์ 02: agent plans steps, reasons across info

---

## SLIDE 7 — Agentic Behavior: Task Plan + Tools + RAG 🎯(02)⭐
โชว์ evidence ที่กรรมการระบุ:
- **Task Plan (visible):** audit trace 6 ขั้น (step/agent/thought/tool_call) ที่ระบบ log จริง
- **Tool Calls:** `calculate_tco()` · `evaluate_concessions()` (Nash) · `check_prompt_injection()` · `market_benchmark()`
- **RAG / Custom Chunking:** Thai Industrial MRO Index (10 หมวด) retrieve ด้วย SKU-prefix/brand/keyword → BATNA
- **Use-case LLM:** Nova Micro (parse) + Nova Pro (negotiate)
- **Final output:** คำตอบเจรจาไทย + TCO + strategy

🎙️ *"กรรมการมองหา task plan, tool call, RAG และ use-case LLM — เรามีครบ: audit trace แสดงแผนทีละ step, เรียก tool คำนวณจริง, retrieve ราคากลางแบบ RAG, เลือกโมเดลตามความยาก"*
🎯 เกณฑ์ 02: "RAG/custom chunking, use-case LLM, agentic agent" — ตอบครบทุกคำ

---

## SLIDE 8 — Dynamic Model Gateway (Cost + Routing) 🎯(02,03)
- Diagram: task → classify complexity → route (LIGHT→Nova Micro / HEAVY→Nova Pro)
- **ตารางเปรียบเทียบ cost/turn:**

  | กลยุทธ์ | $/turn | relative |
  | :--- | ---: | ---: |
  | Claude Sonnet ทุกงาน | $0.0109 | 1.0× |
  | **Gateway (Micro + Pro)** | ต่ำกว่ามาก | **~0.1×** |
  | Fallback deterministic | $0 | 0× |

🎙️ *"เราไม่ยิงโมเดลแพงกับทุกงาน Gateway เลือกโมเดลตามความยาก ประหยัด cost เมื่อ scale ข้าม 2,489 PRs"*
🎯 เกณฑ์ 02 + 03: agentic + cost efficiency

---

## SLIDE 9 — Prototype: Live End-to-End Demo 🎯(03)
- 3 screenshot จริง: Plant Terminal → Supplier Portal (เจรจาสด) → Buyer Dashboard (SSE live)
- ป้าย: *"รันจริงบน AWS Bedrock (Nova Micro + Nova Pro)"*
- flow: PR → RFQ email (SES) → negotiate → Stage 4 → PO
- QR code / ลิงก์ demo video

🎙️ *"ทั้งหมดไม่ใช่ mock-up — รันจริงบน AWS Bedrock ข้อความ AI มาจาก Nova Pro สด ๆ"*
🎯 เกณฑ์ 03: end-to-end, realistic data, live demo

---

## SLIDE 10 — AWS Architecture & Deployment 🎯(03)
- Architecture diagram (PNG จาก `ARCHITECTURE.md`)
- Services: Bedrock · Guardrails · Fargate/App Runner · ECR · RDS · SES · Secrets Manager · CloudWatch
- Deployment: Docker multi-stage → ECR → App Runner (serverless)

🎙️ *"สถาปัตยกรรม serverless เต็มตัวบน AWS build เป็น Docker image ขึ้น ECR deploy บน App Runner พร้อม RDS และ Secrets Manager ตามมาตรฐาน production"*
🎯 เกณฑ์ 03: "use AWS" ชัดเจน

---

## SLIDE 11 — Responsible AI & Safety 🎯(04)⭐
4 เสา:
- **Human-in-the-Loop:** CPO เซ็นก่อนออก PO (AI ไม่อนุมัติเอง)
- **Guardrails:** Bedrock Guardrails (ApplyGuardrail + inline) + anti-injection ไทย (authority spoofing) + เพดานราคาที่ AI ข้ามไม่ได้
- **Security:** Magic Link token กันสวมรอยข้ามคู่ค้า (verified 8/8)
- **Audit Trail:** log ทุก decision + model ID + latency + token + TCO score
- **Escalation:** SLA monitor กันการดองแชท

🎙️ *"Responsible AI คือหัวใจ AI เสนอ แต่คนตัดสินใจ มี guardrails หลายชั้น token กันสวมรอย และ audit trail ครบ ตรวจย้อนหลังได้ 100%"*
🎯 เกณฑ์ 04: human approval, guardrails, escalation, audit trail — ครบ

---

## SLIDE 12 — Creativity & UX 🎯(05)
- **Real-time cockpit (SSE):** คู่ค้าพิมพ์ → buyer เห็นสด ไม่ต้อง refresh
- **Live Scorecard** 5 มิติเปลี่ยนตามการเจรจา
- **Award Board** จัดอันดับผู้ชนะอัตโนมัติ
- **Thai-native negotiation** — ภาษาจัดซื้อระดับมืออาชีพ (จุดต่างจากคู่แข่งต่างชาติ)

🎙️ *"ทุกอย่างเกิดสด ผู้บริหารเห็นการเจรจา real-time scorecard ขยับตามข้อเสนอ และ AI พูดภาษาจัดซื้อไทยได้เนียน ซึ่งเครื่องมือต่างชาติทำไม่ได้"*
🎯 เกณฑ์ 05: clear UX + storytelling

---

## SLIDE 13 — Before vs. After (เปรียบเทียบเชิงลึก) 🎯(06)⭐
| มิติ | ❌ Before | ✅ After | ผลลัพธ์ |
| :--- | :--- | :--- | :--- |
| จัดการ tail-spend | 2,489 ใบแยก | 61 ดีลกลยุทธ์ | +อำนาจต่อรอง |
| เจรจา | เฉพาะดีลใหญ่ | AI ทุกดีล 24/7 | ครอบคลุม 100% |
| ราคา | spot buy แพง | BATNA-anchored | **−14.5%** |
| เวลา/ดีล | วัน-สัปดาห์ | นาที | เร็วขึ้นมาก |
| audit | ยาก | ครบทุก step | +ธรรมาภิบาล |
| ออก PO | คีย์มือ | auto → SAP | −error |

🎙️ *"จากซื้อแยกใบจ่ายแพง เป็นรวมยอดให้ AI เจรจาทุกดีล ประหยัด 14.5% เร็วขึ้นจากสัปดาห์เหลือนาที ตรวจสอบได้ครบ"*
🎯 เกณฑ์ 06: before-after + metric

---

## SLIDE 14 — Business Value & ROI 🎯(06)⭐
- **ROI:** ประหยัด **฿25.0M/ปี** จากงบ ฿172.6M (**−14.5%**)
- **Cost:** AWS ~หลักสิบ USD/เดือน = **< 0.01%** ของเงินที่ประหยัด
- **Payback:** คุ้มทันทีเดือนแรก
- **Benchmark:** tail-spend savings อุตสาหกรรมทั่วไป 5–15% → เราทำได้ 14.5% (ปลายสูง)
- **Scalability:** 5 โรงงาน → ทั้ง supply chain

🎙️ *"ลงทุน AWS หลักสิบดอลลาร์/เดือน แลกประหยัด 25 ล้านบาท/ปี ROI มหาศาล และ 14.5% อยู่ปลายสูงของ benchmark 5-15%"*
🎯 เกณฑ์ 06: measurable benefit + benchmark/threshold

---

## SLIDE 15 — Roadmap & Scalability
- **Phase 1 (now):** POC — 5 โรงงาน, Bedrock, closed-loop SAP
- **Phase 2:** SAP จริง (PyRFC/BTP), SES production, Redis SSE multi-instance
- **Phase 3:** ขยาย category, real-time market API, multi-tenant SaaS
- Tech moat: multi-agent + Thai negotiation + model gateway

🎙️ *"ตอนนี้เป็น POC ที่ทำงานจริง ก้าวต่อไปคือเชื่อม SAP production และขยายเป็น SaaS หลายโรงงาน สถาปัตยกรรมรองรับ scale อยู่แล้ว"*

---

## SLIDE 16 — Closing / Call to Action
- สรุป 1 ประโยค: *"AutoProcure.AI — AI ที่เจรจาแทนคุณ ประหยัดจริง ปลอดภัย ตรวจสอบได้"*
- 3 ตัวเลขใหญ่: **฿25M saved · −14.5% · 61 deals automated**
- โลโก้ทีม + NTT DATA + GitHub + demo link

🎙️ *"AutoProcure.AI เปลี่ยน tail-spend ที่รั่วไหลให้เป็นเงินที่ประหยัดได้จริง ด้วย AI ที่รับผิดชอบและตรวจสอบได้ ขอบคุณครับ"*

---

## 📌 Design Tips (ให้ดูระดับ enterprise)
- 1 สไลด์ = 1 ความคิด อย่ายัดเกิน
- ใช้ **ตัวเลขใหญ่** (฿25M, −14.5%) เป็นพระเอกในสไลด์ business
- สไลด์ **6-7 (agentic)** และ **13-14 (business)** ลงรายละเอียดมากสุด (กรรมการเน้น 2 เกณฑ์นี้)
- ใส่ **screenshot จริง** ไม่ใช่ mockup (เกณฑ์ 03)
- footer ทุกสไลด์: หมายเลข + โลโก้ NTT DATA
