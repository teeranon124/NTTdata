# Project Summary — AutoProcure.AI
**หัวข้อการแข่งขัน: Manufacturing**

## Project Summary (โครงการที่นำเสนอ)
AutoProcure.AI คือระบบ **Autonomous Multi-Agent Procurement** ที่เปลี่ยนงานจัดซื้ออะไหล่ซ่อมบำรุงโรงงาน (MRO tail-spend) ที่กระจัดกระจาย ให้กลายเป็นดีลเชิงกลยุทธ์ที่ AI เจรจาต่อรองราคากับซัพพลายเออร์ได้เองแบบ End-to-End บน AWS

## Problem Statement (ปัญหา/ความท้าทาย)
โรงงานผลิตมีใบขอซื้ออะไหล่ MRO จำนวนมหาศาล มูลค่าต่อใบต่ำแต่ความถี่สูง (tail-spend) ฝ่ายจัดซื้อมีกำลังคนจำกัด เจรจาไม่ทันทุกใบ ทำให้ซื้อแบบ spot buy ราคาแพงกว่าตลาด ไม่มีอำนาจต่อรอง ไม่มีราคากลางอ้างอิง และตรวจสอบธรรมาภิบาลย้อนหลังได้ยาก — ในโครงการนี้คือ **2,489 ใบขอซื้อจาก 5 โรงงาน มูลค่า ฿172.6 ล้าน/ปี**

## Proposed Solution (แนวทางแก้ไข)
1. **Spend Aggregation** — รวบ 2,489 PRs เป็น 61 ดีลเชิงกลยุทธ์ (Blanket Order/LTA)
2. **Autonomous Multi-Agent Negotiation** — AI 5 agent (Compliance → Router → Market Intel → Negotiator → Arbitrator) เจรจาเป็นภาษาไทยเชิงพาณิชย์ อ้างอิงราคากลางตลาด (BATNA) + Game Theory บน Amazon Bedrock
3. **Closed-Loop to SAP** — ตกลงได้ → เลื่อน stage อัตโนมัติ → CPO ลงนาม (HITL) → ออก PO เข้า SAP S/4HANA

## Expected Benefits (ประโยชน์ที่คาดว่าจะได้รับ)
- ประหยัดงบจัดซื้อ MRO **~14.5% (฿25.0 ล้าน)** จากข้อมูลจริงในระบบ
- ปลดภาระฝ่ายจัดซื้อ — AI รับงาน tail-spend 24/7
- ธรรมาภิบาลโปร่งใส (audit trail + HITL ก่อนออก PO)
- ต้นทุน AWS ต่ำ (pay-as-you-go + model tiering) และขยายสู่ production ได้

## AI Technologies Used
Amazon Bedrock (Converse API) · Amazon Nova Micro (router) · Amazon Nova Pro (negotiator) · Amazon Bedrock Guardrails (prompt-injection defense) · Dynamic Model Gateway · Game Theory (Nash Bargaining) · TCO/NPV Engine (WACC 7%)

## Current Social & Country-wise Issue
ภาคการผลิตไทย (โดยเฉพาะ EEC) เผชิญแรงกดดันด้านต้นทุนและการขาดแคลนบุคลากรจัดซื้อที่มีทักษะ AutoProcure.AI ช่วยยกระดับขีดความสามารถการแข่งขันของโรงงานไทยด้วยการลดต้นทุนจัดซื้อและเพิ่มความโปร่งใส โดยใช้ AI ที่สื่อสารภาษาไทยเชิงธุรกิจได้
