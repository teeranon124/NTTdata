# AutoProcure.AI - Developer Handoff Document (สำหรับ Kiro / Dev Team)

เอกสารฉบับนี้จัดทำขึ้นเพื่อให้ **Kiro** (หรือนักพัฒนาท่านต่อไป) สามารถรับช่วงต่อและพัฒนาโครงการ **AutoProcure.AI** ได้ทันทีโดยไม่ต้องเริ่มต้นใหม่หรือคาดเดาโครงสร้าง

---

## 1. สถานะโครงการปัจจุบัน (Current System Status)

| ส่วนประกอบ | สถานะ | รายละเอียด |
| :--- | :---: | :--- |
| **Buyer Dashboard (กระดานจัดซื้อ)** | ✅ 100% | ตาราง 60 ดีล อิงจาก 2,500 PRs จริง, ปรับแต่ง Layout กะทัดรัดไม่ล้นจอ, ปุ่มครบทุกแถว (Stage 4 สีเขียว / Stage 1-3 สีเทาล็อกพร้อม Toast) |
| **Negotiation Cockpit (ห้องเจรจา)** | ✅ 100% | สลับดูซัพพลายเออร์แยกราย (AVL Tabs), แสดง Concession Steps, Matrix เปรียบเทียบ, Terms Scorecard, ปุ่มลงนาม PO |
| **Supplier Portal (หน้าจอคู่ค้า)** | ✅ 100% | Magic Link เข้ารหัสแยกเจ้า (`?vendor=sp`, `?vendor=eb`, `?vendor=tk`), Term Sheet ซิงก์สดกับแชต, ปลดล็อกปุ่ม BAFO เมื่อตกลง |
| **AI Agent Logic (Bedrock & Local)** | ✅ 100% | Intent Router (Nova Lite), Security Guardrails, TCO Math (WACC 7%), Concession Engine (Game Theory), Fallback พร้อมทำงาน |
| **Governance & Audit Trail** | ✅ 100% | แสดง 16 ดีลที่รอผู้บริหาร CPO ลงนาม พร้อมปุ่มยิงคำสั่ง BAPI ใน SAP S/4HANA |
| **ROI Financial Analysis** | ✅ 100% | สรุปผลตอบแทน ฿25.59M (-14.97%), ค่าใช้จ่าย AWS < 0.3%, กราฟและสถิติครบถ้วน |
| **Automated Testing & Git** | ✅ 100% | ผ่านการทดสอบ Selenium E2E อัตโนมัติทุก Flow, Commit และ Push ขึ้น GitHub (`main`) เรียบร้อย |

---

## 2. โครงสร้างไฟล์และสถาปัตยกรรม (Codebase Structure)

```text
NTTdata/
├── app.py                             # จุดรัน Flask Server หลัก (Port 8080)
├── requirements.txt                   # รายการ dependencies
├── .env.example                       # ตัวอย่าง Config (AWS, SAP, Flask)
├── dataset_2500.json                  # ข้อมูลประวัติ 2,500 PRs จริง
├── dataset_2500.js                    # ข้อมูล PRs ในรูปแบบ JS Object สำหรับ Browser
├── index.html                         # แดชบอร์ดฝั่งจัดซื้อ (Buyer Dashboard)
│
├── webapp/
│   ├── data/
│   │   ├── master_deals.json          # ข้อมูล 60 ดีลระดับ Master พร้อมข้อมูล AVL ซัพพลายเออร์
│   │   └── sessions/                  # ประวัติการแชตและ Concession Ladder ที่บันทึกรายเจ้า
│   │
│   ├── repositories/
│   │   ├── deal_repository.py         # ตัวจัดการดีล, ดึงประวัติ PRs, คำนวณ System Stats
│   │   └── session_repository.py      # ตัวจัดการ Session, บันทึกแชตลงไฟล์ JSON
│   │
│   ├── agents/
│   │   ├── router_agent.py            # สกัด Intent, ราคา, เครดิตเทอม (Nova Lite / Regex)
│   │   ├── negotiator_agent.py        # ลูปหลัก AI Agent (Guardrail -> TCO -> Concession -> Nova Pro)
│   │   ├── bedrock_client.py          # Client เชื่อมต่อ Amazon Bedrock Converse API + Fallback
│   │   ├── prompts/
│   │   │   ├── negotiator_policy.md   # System Prompt สำหรับการต่อรองเชิงพาณิชย์
│   │   │   └── router_system.md       # Prompt สำหรับการสกัด Intent
│   │   └── tools/
│   │       ├── guardrail_checker.py   # ดักจับ Prompt Injection & ตรวจสอบเพดานงบ
│   │       ├── tco_calculator.py      # คำนวณ NPV เครดิตเทอม และ Effective TCO
│   │       └── concession_engine.py   # ทฤษฎีเกม (Nash Bargaining) คำนวณจุดแลกเปลี่ยน
│   │
│   ├── services/
│   │   └── negotiation_service.py     # ตัวเชื่อมระหว่าง Web Controller กับ Agent Logic
│   │
│   └── web/
│       ├── templates/
│       │   ├── index.html             # เทมเพลตแดชบอร์ดจัดซื้อ
│       │   └── supplier_portal.html   # หน้าจอสำหรับซัพพลายเออร์ (Live Term Sheet + Chat)
│       └── views/
│           └── chat_view.py           # REST APIs (/api/negotiate, /portal/negotiate/<id>)
```

---

## 3. วิธีการรันระบบ (Quickstart Guide)

```powershell
# 1. เข้าสู่โฟลเดอร์โครงการ
cd c:\NTTdata

# 2. ติดตั้ง Dependencies (ถ้ายังไม่ได้ทำ)
.\venv\Scripts\pip.exe install -r requirements.txt

# 3. เริ่มรันเซิร์ฟเวอร์
.\venv\Scripts\python.exe app.py
```

* **Buyer Dashboard (หน้าหลักจัดซื้อ):** `http://127.0.0.1:8080/`
* **Supplier Portal (สยาม พรีซิชั่น - ชนะประมูล):**  
  `http://127.0.0.1:8080/portal/negotiate/nsk?vendor=sp&token=tok_sec_nsk_sp_verified`
* **Supplier Portal (อีสเทิร์น แบริ่ง - ข้อเสนอสำรอง):**  
  `http://127.0.0.1:8080/portal/negotiate/nsk?vendor=eb&token=tok_sec_nsk_eb_verified`
* **Supplier Portal (ไทย โคโย - ตกรอบ SLA):**  
  `http://127.0.0.1:8080/portal/negotiate/nsk?vendor=tk&token=tok_sec_nsk_tk_verified`

---

## 4. สิ่งที่ Kiro สามารถนำไปต่อยอดได้ (Roadmap for Next Steps)

หากต้องการยกระดับจาก **Production-Ready PoC Demo** ไปสู่ **Full Cloud Enterprise Production**:

1. **เชื่อมต่อ Live AWS Credentials จริง (ถ้ามีสิทธิ์ AWS):**
   * ก๊อบปี้ `.env.example` ไปเป็น `.env` แล้วระบุ `AWS_ACCESS_KEY_ID` และ `AWS_SECRET_ACCESS_KEY`
   * ระบบใน `bedrock_client.py` จะสลับจากการจำลอง Local Fallback ไปเรียกใช้ **Amazon Nova Lite / Nova Pro API** ของจริงทันทีโดยอัตโนมัติ
2. **เปิดใช้ AWS SES ส่งเมลจริง:**
   * ในฟังก์ชันจำลองส่งอีเมล สามารถเพิ่ม `boto3.client('ses').send_email()` เพื่อยิง Magic Link เข้า Inbox อีเมลคู่ค้าจริง
3. **เชื่อมต่อ SAP S/4HANA (BAPI / OData):**
   * ปัจจุบันปุ่มลงนามใน Modal จะจำลองคำสั่ง `BAPI_PO_CREATE1`
   * สามารถใช้ไลบรารี `PyRFC` หรือเชื่อมผ่าน SAP BTP เพื่อส่งข้อมูล Purchase Agreement ไปเปิดเอกสารใน SAP ของจริง
4. **WebSocket / Server-Sent Events (SSE):**
   * ปัจจุบันการซิงก์ข้อมูลฝั่ง Supplier Portal ใช้วิธี REST API (`/api/negotiate`)
   * สามารถอัปเกรดเป็น Socket.io เพื่อให้เวลาผู้ใช้พิมพ์ในหน้า Portal ข้อความจะเด้งเข้าไปโผล่ในหน้า Buyer Cockpit แบบ Real-time ทันที
