// AUTO-EXTRACTED from index.html by Phase-F refactor. Do not add server-rendered values here.
        // FULL DATA STORE: MULTI-VENDOR CHATS & PER-DEAL REASONING TIMELINES
        const database = {
            deals: {
                festo_cyl: {
                    "title": "กระบอกลมนิวเมติกส์ Festo (DSBC-32-100-PPVA) ยอดรวม 850 ตัว",
                    "budgetStr": "฿3,850.00/ตัว (฿3,272,500)",
                    "targetStr": "฿3,320.00 - ฿3,380.00/ตัว (เป้าหมายเซฟ -13.5%)",
                    "chips": [
                                        "ขอราคาพิเศษสำหรับวอลลุ่ม 850 ตัว",
                                        "ขยายเครดิตเทอมเป็น 45 วัน",
                                        "การันตีส่งมอบภายใน 7 วัน",
                                        "ขอใบรับรองมาตรฐาน ISO 15552"
                    ],
                    "vendors": [
                                        {
                                                            "id": "v_siam_pneu",
                                                            "name": "บจก. สยาม นิวเมติกส์ แอนด์ ซัพพลาย",
                                                            "email": "teeranonn124@gmail.com",
                                                            "price": "฿3,850.00",
                                                            "credit": "30 วัน",
                                                            "leadTime": "7 วันทำการ",
                                                            "warranty": "1 ปี",
                                                            "cert": "ISO 15552 ✓",
                                                            "status": "รอเริ่มเจรจา (ห้องว่างสด)",
                                                            "statusBadge": "badge-info text-white font-bold",
                                                            "outcome": "ยังไม่มีการเจรจา — รอคู่ค้ายื่นข้อเสนอผ่าน Supplier Portal หรือฝ่ายจัดซื้อเริ่มคุย",
                                                            "ladder": [],
                                                            "messages": []
                                        },
                                        {
                                                            "id": "v_roykaen_part",
                                                            "name": "บจก. รอยแก่น พาร์ท ซัพพลาย",
                                                            "email": "roykaen.30@gmail.com",
                                                            "price": "฿3,890.00",
                                                            "credit": "30 วัน",
                                                            "leadTime": "10 วันทำการ",
                                                            "warranty": "1 ปี",
                                                            "cert": "ISO 15552 ✓",
                                                            "status": "รอเริ่มเจรจา (ห้องว่างสด)",
                                                            "statusBadge": "badge-info text-white font-bold",
                                                            "outcome": "ยังไม่มีการเจรจา — รอคู่ค้ายื่นข้อเสนอผ่าน Supplier Portal หรือฝ่ายจัดซื้อเริ่มคุย",
                                                            "ladder": [],
                                                            "messages": []
                                        },
                                        {
                                                            "id": "v_film_auto",
                                                            "name": "บจก. ฟิล์ม ออโตเมชั่น แอนด์ ทูลส์",
                                                            "email": "filmzazazs63@gmail.com",
                                                            "price": "฿3,820.00",
                                                            "credit": "30 วัน",
                                                            "leadTime": "14 วันทำการ",
                                                            "warranty": "1 ปี",
                                                            "cert": "ISO 15552 ✓",
                                                            "status": "รอเริ่มเจรจา (ห้องว่างสด)",
                                                            "statusBadge": "badge-info text-white font-bold",
                                                            "outcome": "ยังไม่มีการเจรจา — รอคู่ค้ายื่นข้อเสนอผ่าน Supplier Portal หรือฝ่ายจัดซื้อเริ่มคุย",
                                                            "ladder": [],
                                                            "messages": []
                                        }
                    ],
                    reasoning: [
                        { step: 1, agent: 'Demand Aggregator (ERP Listener)', time: 'T+0.32s | Event-Driven', title: 'ตรวจจับใบขอซื้อ PR กระบอกลม Festo และรวมยอดอัตโนมัติ', thought: 'ระบบตรวจจับ PR กระบอกลม Festo DSBC-32-100 จาก 14 แผนกซ่อมบำรุงในเครือ รวมยอดสั่งซื้อเป็น 850 ตัว เพื่อยกระดับจาก Spot Buy เป็น Tier-3 Volume Discount', toolCall: 'sap_aggregate_pr(part_code="DSBC-32-100-PPVA", target_qty=850) ➔ 14 PRs Aggregated' },
                        { step: 2, agent: 'Market Benchmark & TCO Engine', time: 'T+0.85s | RAG Vector', title: 'วิเคราะห์ราคากลางอุตสาหกรรมและคำนวณ TCO Target', thought: 'ดึงข้อมูลสเปกมาตรฐาน ISO 15552 และประวัติการจัดซื้อ 2,500 รายการ คำนวณราคาเป้าหมาย TCO ที่ ฿3,320.00/ตัว (เซฟเป้าหมาย -13.5% หรือ ฿450,500)', toolCall: 'tco_benchmark(catalog_price=3850, historical_avg=3720) ➔ Target: ฿3,320.00' },
                        { step: 3, agent: 'Multi-Vendor Dispatcher', time: 'T+1.40s | AWS SES Batch', title: 'สร้าง Magic Links และส่งหนังสือเชิญยื่นข้อเสนอ 3 เจ้า', thought: 'สร้าง Secure Magic Link Token แยกเฉพาะสำหรับ 3 ซัพพลายเออร์ใน AVL (สยาม นิวเมติกส์, รอยแก่น พาร์ท, ฟิล์ม ออโตเมชั่น) และส่งคำขอใบเสนอราคาผ่าน AWS SES', toolCall: 'aws_ses_batch_dispatch(deal="festo_cyl", vendors=3) ➔ Magic Links Dispatched ✓' },
                        { step: 4, agent: 'Guardrail & Compliance Agent', time: 'T+2.10s | Rule Engine', title: 'ตรวจสอบเงื่อนไขความเสี่ยงและมาตรการควบคุม', thought: 'กำหนด Guardrail: ราคาสูงสุดห้ามเกิน ฿3,850, เครดิตเทอมขั้นต่ำ 30 วัน (เป้าหมาย 45 วัน), ส่งมอบไม่เกิน 14 วัน, และต้องมี ISO 15552', toolCall: 'apply_guardrail(max_price=3850, min_credit=30, cert="ISO 15552") ➔ Guardrails Active ✓' }
                    ]
},
                omron_photo: {
                    "title": "โฟโตอิเล็กทริกเซนเซอร์ Omron (E3Z-T61 2M) ยอดรวม 1,400 ตัว",
                    "budgetStr": "฿1,650.00/ตัว (฿2,310,000)",
                    "targetStr": "฿1,420.00 - ฿1,450.00/ตัว (เป้าหมายเซฟ -13.9%)",
                    "chips": [
                                        "ขอราคาขายส่งวอลลุ่ม 1,400 ตัว",
                                        "ขอเครดิตเทอม 60 วัน",
                                        "รับประกันสินค้า 18 เดือน",
                                        "การันตีสต็อกสำรอง 10%"
                    ],
                    "vendors": [
                                        {
                                                            "id": "v_siam_sensor",
                                                            "name": "บจก. สยาม เซนเซอร์ โซลูชั่น",
                                                            "email": "teeranonn124@gmail.com",
                                                            "price": "฿1,650.00",
                                                            "credit": "30 วัน",
                                                            "leadTime": "5 วันทำการ",
                                                            "warranty": "1 ปี",
                                                            "cert": "CE / RoHS ✓",
                                                            "status": "รอเริ่มเจรจา (ห้องว่างสด)",
                                                            "statusBadge": "badge-info text-white font-bold",
                                                            "outcome": "ยังไม่มีการเจรจา — รอคู่ค้ายื่นข้อเสนอผ่าน Supplier Portal หรือฝ่ายจัดซื้อเริ่มคุย",
                                                            "ladder": [],
                                                            "messages": []
                                        },
                                        {
                                                            "id": "v_roykaen_eng",
                                                            "name": "บจก. รอยแก่น เอ็นจิเนียริ่ง พาร์ท",
                                                            "email": "roykaen.30@gmail.com",
                                                            "price": "฿1,680.00",
                                                            "credit": "30 วัน",
                                                            "leadTime": "7 วันทำการ",
                                                            "warranty": "1 ปี",
                                                            "cert": "CE / RoHS ✓",
                                                            "status": "รอเริ่มเจรจา (ห้องว่างสด)",
                                                            "statusBadge": "badge-info text-white font-bold",
                                                            "outcome": "ยังไม่มีการเจรจา — รอคู่ค้ายื่นข้อเสนอผ่าน Supplier Portal หรือฝ่ายจัดซื้อเริ่มคุย",
                                                            "ladder": [],
                                                            "messages": []
                                        },
                                        {
                                                            "id": "v_film_tech",
                                                            "name": "บจก. ฟิล์ม เทคโนโลยี แอนด์ อีควิปเมนท์",
                                                            "email": "filmzazazs63@gmail.com",
                                                            "price": "฿1,640.00",
                                                            "credit": "30 วัน",
                                                            "leadTime": "10 วันทำการ",
                                                            "warranty": "1 ปี",
                                                            "cert": "CE / RoHS ✓",
                                                            "status": "รอเริ่มเจรจา (ห้องว่างสด)",
                                                            "statusBadge": "badge-info text-white font-bold",
                                                            "outcome": "ยังไม่มีการเจรจา — รอคู่ค้ายื่นข้อเสนอผ่าน Supplier Portal หรือฝ่ายจัดซื้อเริ่มคุย",
                                                            "ladder": [],
                                                            "messages": []
                                        }
                    ],
                    reasoning: [
                        { step: 1, agent: 'Demand Aggregator (ERP Listener)', time: 'T+0.28s | Event-Driven', title: 'ตรวจจับความต้องการเซนเซอร์ Omron และรวมยอด 1,400 ตัว', thought: 'พบใบขอซื้อเซนเซอร์ Omron E3Z-T61 กระจายใน 3 โรงงาน รวมยอดทั้งหมด 1,400 ตัว เพื่อสร้างอำนาจต่อรองราคาขายส่ง', toolCall: 'sap_aggregate_pr(part_code="E3Z-T61-2M", target_qty=1400) ➔ Aggregated' },
                        { step: 2, agent: 'Market Benchmark & TCO Engine', time: 'T+0.72s | RAG Vector', title: 'คำนวณราคา TCO และกำหนดเพดานเจรจาต่อรอง', thought: 'ราคาตลาดปลีกอยู่ที่ ฿1,650/ตัว กำหนดเป้าหมายเจรจาที่ ฿1,420 - ฿1,450/ตัว (เซฟ -13.9% หรือ ฿322,000) พร้อมขยายเครดิตเทอม 60 วัน', toolCall: 'tco_benchmark(catalog_price=1650, target_discount=0.139) ➔ Target: ฿1,420.00' },
                        { step: 3, agent: 'Multi-Vendor Dispatcher', time: 'T+1.15s | AWS SES Batch', title: 'ยิง RFQ พร้อม Magic Token ไปยังคู่ค้า AVL 3 เจ้า', thought: 'จัดส่งอีเมลเชิญเจรจาพร้อม Magic Link Token เฉพาะตัวให้ บจก. สยาม เซนเซอร์, รอยแก่น เอ็นจิเนียริ่ง, และ ฟิล์ม เทคโนโลยี', toolCall: 'aws_ses_batch_dispatch(deal="omron_photo", vendors=3) ➔ 3 Invites Sent ✓' }
                    ]
},
                nsk: {
                    title: "ตลับลูกปืน NSK (6208-2RS1) ยอดรวม 1,200 ชิ้น",
                    budgetStr: "฿450.00/ชิ้น (฿540,000)",
                    targetStr: "฿395.00 - ฿398.00/ชิ้น (เซฟ -11.5%)",
                    chips: ["ยืนยันราคา ฿398 ตามสัญญา 1 ปี", "ขอขยายเครดิต 45 วัน", "การันตีส่งมอบใน 7 วัน", "ขอใบรับรอง JIS B 1514"],
                                        vendors: [
                        {
                            id: "sp",
                            name: "บจก. สยาม พรีซิชั่น (V-4019)",
                            price: "฿398.00",
                            credit: "45 วัน",
                            leadTime: "7 วันทำการ",
                            warranty: "1 ปีเต็ม (ศูนย์ NSK)",
                            cert: "JIS B 1514 / ISO 492 ✓",
                            status: "ชนะการประมูล (ออกใบ PO)",
                            statusBadge: "badge-success text-white font-bold",
                            outcome: "ผู้ชนะ TCO Rank #1 | ประหยัด ฿62,400 (-11.55%) | เครดิต 45 วัน ส่ง 7 วัน",
                            ladder: [
                                { round: "Opening", title: "ราคาเปิดแรกตามใบเสนอราคา", price: "฿425.00", tag: "Initial Ask", color: "border-slate-300 text-slate-500", note: "อ้างอิงต้นทุนนำเข้าและค่าระวางเรือปรับขึ้น" },
                                { round: "Counter 1", title: "AI ดึงราคาตลาด EEC บีบราคา", price: "฿408.00", tag: "Market Pressure", color: "border-blue-300 text-blue-700", note: "แจ้งช่วงราคาคู่แข่งในระบบ ฿405-฿408" },
                                { round: "Concession", title: "AI แลกสัญญา 1 ปี + เครดิต 45 วัน", price: "฿398.00", tag: "Volume Trade-off", color: "border-indigo-300 text-indigo-700", note: "ผูกยอดรวม 1,200 ชิ้น ชลบุรี+ระยอง" },
                                { round: "Awarded", title: "ตกลงทำสัญญาและออกใบ PO", price: "฿398.00", tag: "Winner ✓", color: "border-emerald-500 bg-emerald-50 text-emerald-900 font-bold", note: "ชนะประมูล TCO สูงสุด ประหยัด ฿62,400" }
                            ],
                            messages: [
                                { sender: "vendor", name: "สยาม พรีซิชั่น (ฝ่ายขาย)", time: "10:30", text: "เรียนฝ่ายจัดซื้อกลาง ตามที่ได้รับคำขอเสนอราคา (RFQ) สำหรับตลับลูกปืน NSK Deep Groove Ball Bearing 6208-2RS1 จำนวน 1,200 ชิ้น เนื่องจากสถานการณ์ต้นทุนค่าระวางเรือและอัตราแลกเปลี่ยนเยนปรับตัว ทางเราขอเสนอราคาเปิดที่ 425.00 บาท/ชิ้น เครดิต 30 วัน สต็อกพร้อมส่งภายใน 7 วันทำการครับ" },
                                { sender: "agent", name: "AI จัดซื้ออัตโนมัติ (Autonomous Agent)", time: "10:32", text: "ขอบคุณคุณสมศักดิ์ครับ จากการตรวจสอบประวัติฐานข้อมูลจัดซื้อย้อนหลังและราคาอ้างอิงตลาด (Market Benchmark) ของตลับลูกปืนมาตรฐาน JIS B 1514 ในเขตนิคม EEC สำหรับคำสั่งซื้อขนาด 1,200 ชิ้น ราคาเฉลี่ยอยู่ที่ 400 - 405 บาท อีกทั้งเราได้รับข้อเสนอเบื้องต้นจากคู่ค้ารายอื่นใน AVL ที่ 405 บาท หากทางสยาม พรีซิชั่น สามารถปรับลดราคาลงมาที่ 395 บาท ทางเราพร้อมพิจารณาจัดสรรคำสั่งซื้อให้ทันทีครับ", tactic: "[BATNA Engine: อ้างอิงราคาตลาดและข้อเสนอคู่แข่งในระบบ]" },
                                { sender: "vendor", name: "สยาม พรีซิชั่น (ฝ่ายขาย)", time: "10:35", text: "395 บาทเป็นราคาที่ต่ำกว่าเพดานขั้นต่ำของเรามากเลยครับคุณจัดซื้อ ถ้าสั่งล็อต 1,200 ชิ้นจริงๆ ทางเราลดสุดตัวได้ที่ 408.00 บาท/ชิ้น และขอรักษาระยะเวลาเครดิตเทอมไว้ที่ 30 วันครับ" },
                                { sender: "agent", name: "AI จัดซื้ออัตโนมัติ (Autonomous Agent)", time: "10:37", text: "เข้าใจข้อจำกัดด้านต้นทุนครับ เพื่อให้เกิดข้อตกลงที่เกิดประโยชน์ร่วมกัน (Win-Win) ทางโรงงานขอเสนอเงื่อนไขแลกเปลี่ยนหลายมิติ (Multi-variable Concession): เราขอยืนยันราคาที่ 398.00 บาท/ชิ้น แต่ทางเราจะขยายสัญญาเป็น Blanket Order สัญญารายปี 1 ปีเต็ม การันตียอดสั่งซื้อทั้งเครือต่อเนื่อง และขอยืดเครดิตเทอมเป็น 45 วัน หากท่านอนุมัติได้ ทางเราจะล็อกให้สยามฯ เป็นคู่ค้า Tier-1 ประจำปีสำหรับอะไหล่ NSK ของทุกโรงงานครับ", tactic: "[Concession Exchange: แลกสัญญารายปี 1 ปี กับส่วนลดและเครดิต 45 วัน]" },
                                { sender: "vendor", name: "สยาม พรีซิชั่น (ฝ่ายขาย)", time: "10:41", text: "ข้อเสนอน่าสนใจมากครับ ขอเวลาทางผมปรึกษาผู้อำนวยการฝ่ายขายสักครู่ครับ... ทางผู้บริหารยินดีตกลงตามเงื่อนไขครับ! ที่ราคา 398.00 บาท/ชิ้น เครดิตเทอม 45 วัน พร้อมสัญญารายปี 1,200 ชิ้น และการันตีส่งมอบล็อตแรกเข้าโรงงานชลบุรีภายใน 7 วันทำการครับ" },
                                { sender: "agent", name: "AI จัดซื้ออัตโนมัติ (Autonomous Agent)", time: "10:43", text: "ขอบพระคุณครับ ตกลงตามเงื่อนไข: ราคา ฿398.00/ชิ้น (ประหยัดสุทธิ ฿62,400 / -11.55%), เครดิต 45 วัน, รับประกันศูนย์ 1 ปี, มาตรฐาน JIS B 1514 ทางระบบได้สร้าง Draft PO เข้ารอผู้บริหารลงนามดิจิทัล (Sign-Off) ในระบบ SAP เรียบร้อยแล้วครับ", tactic: "[Award PO: คัดเลือกผู้ชนะและส่งต่อผู้บริหารลงนามใน SAP]" }
                            ]
                        },
                        {
                            id: "eb",
                            name: "บจก. อีสเทิร์น แบริ่ง (V-2022)",
                            price: "฿412.00",
                            credit: "30 วัน",
                            leadTime: "10 วันทำการ",
                            warranty: "1 ปี",
                            cert: "JIS B 1514 ✓",
                            status: "ไม่ได้รับเลือก (ราคาสูงกว่าเป้า)",
                            statusBadge: "badge-ghost text-slate-600 border border-slate-300 font-semibold",
                            outcome: "ผู้แพ้ประมูล Rank #2 | ราคาสูงกว่าผู้ชนะ ฿14/ชิ้น และปฏิเสธเครดิต 45 วัน",
                            ladder: [
                                { round: "Opening", title: "ราคาเปิดแรก", price: "฿440.00", tag: "Initial Ask", color: "border-slate-300 text-slate-500", note: "สูงกว่าราคาตลาดเฉลี่ย 10%" },
                                { round: "Counter 1", title: "AI แจ้งราคาคู่แข่งเพื่อต่อรอง", price: "฿398.00", tag: "AI Target", color: "border-blue-300 text-blue-700", note: "เสนอราคาแข่งขันในระบบ" },
                                { round: "Final Offer", title: "ซัพพลายเออร์ลดได้เต็มที่", price: "฿412.00", tag: "Best Offer", color: "border-amber-300 text-amber-800", note: "ไม่ยอมรับเครดิต 45 วัน" },
                                { round: "Rejected", title: "ตัดสิทธิ์เนื่องจากราคาสูงกว่าคู่แข่ง", price: "฿412.00", tag: "Rejected ✗", color: "border-rose-300 bg-rose-50 text-rose-800 font-bold", note: "แพ้ราคา บจก. สยาม พรีซิชั่น (฿398)" }
                            ],
                            messages: [
                                { sender: "vendor", name: "อีสเทิร์น แบริ่ง (ฝ่ายขาย)", time: "10:31", text: "สวัสดีครับ ทางอีสเทิร์น แบริ่ง ขอเสนอราคา NSK 6208-2RS1 ล็อต 1,200 ชิ้น ที่ราคา 440.00 บาท/ชิ้น เครดิต 30 วัน ส่งมอบ 10 วันทำการครับ" },
                                { sender: "agent", name: "AI จัดซื้ออัตโนมัติ (Autonomous Agent)", time: "10:33", text: "ราคา 440 บาทสูงกว่าราคาเฉลี่ยในระบบค่อนข้างมาก ทางเรามีข้อเสนอจากคู่แข่งใน AVL ที่ต่ำกว่า 400 บาท หากทางอีสเทิร์นสามารถปรับลดราคาลงมาแข่งขันที่ 398 บาท ทางเราพร้อมพิจารณาครับ", tactic: "[Competitive Pressure: แจ้งช่วงราคาคู่แข่งเพื่อกดดันราคา]" },
                                { sender: "vendor", name: "อีสเทิร์น แบริ่ง (ฝ่ายขาย)", time: "10:36", text: "ทางเราตรวจสอบสต็อกแล้ว ลดได้เต็มที่ 420 บาทครับ ถ้าต่ำกว่านี้ทางเราเข้าเนื้อจริงๆ เนื่องจากเป็นเกรด C3 ฝายางแท้" },
                                { sender: "agent", name: "AI จัดซื้ออัตโนมัติ (Autonomous Agent)", time: "10:38", text: "หากทางอีสเทิร์นยืนยันราคาที่ 420 บาท ทางเรามีข้อเสนอจาก บจก. สยาม พรีซิชั่น ที่ 398 บาท พร้อมเงื่อนไขเครดิต 45 วัน หากท่านไม่สามารถปรับลดราคาลงมาใกล้เคียงได้ ทางเราจำเป็นต้องเลือกคู่ค้ารายอื่นครับ", tactic: "[Final Counter: แจ้งสถานะเปรียบเทียบในระบบ]" },
                                { sender: "vendor", name: "อีสเทิร์น แบริ่ง (ฝ่ายขาย)", time: "10:40", text: "ทางเราปรึกษาผู้จัดการแล้ว ลดเต็มที่ได้แค่ 412.00 บาท/ชิ้น และเครดิตเทอมให้ได้แค่ 30 วันเท่านั้นครับ ไม่สามารถสู้ราคา 398 ได้จริงๆ ครับ" },
                                { sender: "agent", name: "AI จัดซื้ออัตโนมัติ (Autonomous Agent)", time: "10:42", text: "ขอบคุณสำหรับข้อเสนอครับ เนื่องจากราคา ฿412.00 สูงกว่าเป้าหมาย TCO และมีคู่ค้ารายอื่นให้เงื่อนไขที่ดีกว่า ทางระบบขอสงวนสิทธิ์ไม่เลือกข้อเสนอนี้ในรอบนี้ และบันทึกประวัติราคาไว้สำหรับการประมูลในรอบถัดไปครับ", tactic: "[Decline Offer: ปฏิเสธข้อเสนอเนื่องจากคะแนน TCO ต่ำกว่าคู่แข่ง]" }
                            ]
                        },
                        {
                            id: "tk",
                            name: "บจก. ไทย โคโย ดิสทริบิวชั่น (V-5510)",
                            price: "฿405.00",
                            credit: "30 วัน",
                            leadTime: "21 วันทำการ",
                            warranty: "1 ปี",
                            cert: "ISO 492 ✓",
                            status: "ตกรอบประมูล (SLA ส่งมอบ 21 วัน)",
                            statusBadge: "badge-error text-white font-semibold",
                            outcome: "ผู้แพ้ประมูล Rank #3 | สินค้าไม่มีในคลัง ต้องรอ 21 วัน เสี่ยงไลน์การผลิตหยุดชะงัก",
                            ladder: [
                                { round: "Opening", title: "ราคาเปิดแรก (ราคาดีแต่ของหมด)", price: "฿405.00", tag: "Stock Out", color: "border-slate-300 text-slate-500", note: "สินค้าไม่มีสต็อกในประเทศ" },
                                { round: "SLA Check", title: "AI ตรวจสอบความเสี่ยงไลน์ผลิต", price: "฿405.00", tag: "Downtime Risk", color: "border-amber-300 text-amber-800", note: "สต็อกคงเหลือ 12 ชิ้น รองรับได้เพียง 4 วัน" },
                                { round: "Disqualified", title: "ตัดสิทธิ์เนื่องจาก Lead Time เกิน SLA", price: "฿405.00", tag: "Disqualified ✗", color: "border-rose-300 bg-rose-50 text-rose-800 font-bold", note: "ไม่ผ่านเกณฑ์ส่งมอบฉุกเฉินภายใน 7 วัน" }
                            ],
                            messages: [
                                { sender: "vendor", name: "ไทย โคโย (ฝ่ายขาย)", time: "10:29", text: "ขอเสนอราคาพิเศษ NSK 6208-2RS1 ที่ 405.00 บาท/ชิ้น เครดิต 30 วัน แต่ปัจจุบันสินค้าหน้าร้านหมด ต้องรอสั่งนำเข้าจากคลังญี่ปุ่น ระยะเวลาส่งมอบ 21 วันทำการครับ" },
                                { sender: "agent", name: "AI จัดซื้ออัตโนมัติ (Autonomous Agent)", time: "10:31", text: "ขอบคุณครับ แม้ราคา 405 บาทจะอยู่ในเกณฑ์แข่งขันได้ แต่จากสัญญาณเตือนคลังโรงงานชลบุรี สต็อกคงเหลือเพียง 12 ชิ้น (ต่ำกว่า Min-Stock 50) การรอสินค้า 21 วันทำการมีความเสี่ยงสูงมากที่จะทำให้ไลน์ผลิตหยุดชะงัก (Downtime Risk) ทางไทย โคโย สามารถจัดส่งด่วนทางอากาศหรือแบ่งส่งล็อตแรก 200 ชิ้นภายใน 5 วันได้หรือไม่ครับ?", tactic: "[Risk Evaluation: ตรวจสอบความเสี่ยง Downtime ต่อไลน์การผลิต]" },
                                { sender: "vendor", name: "ไทย โคโย (ฝ่ายขาย)", time: "10:34", text: "เช็กคลังสิงคโปร์แล้ว ไม่สามารถส่งด่วนได้ครับ ต้องรอตู้คอนเทนเนอร์เข้าตามรอบปกติ 21 วันเท่านั้นครับ" },
                                { sender: "agent", name: "AI จัดซื้ออัตโนมัติ (Autonomous Agent)", time: "10:36", text: "เข้าใจข้อจำกัดครับ แต่เนื่องจากระยะเวลาส่งมอบไม่ผ่านเกณฑ์มาตรฐานความปลอดภัย (Lead Time SLA กำหนดไม่เกิน 7 วัน) เพื่อป้องกันความเสียหายของโรงงาน ทางระบบขอตัดสิทธิ์ข้อเสนอนี้ในรอบนี้ครับ ขอบคุณครับ", tactic: "[Disqualify: ตัดสิทธิ์เนื่องจากไม่ผ่านเกณฑ์ SLA การส่งมอบ]" }
                            ]
                        }
                    ],
                    reasoning: [
                        { step: 1, agent: "Analyst Agent (NTT Tsuzumi SLM)", time: "T+0.42s | Token: 180", title: "การรับสัญญาณคลังและรวมยอดข้ามโรงงาน", thought: "ตรวจพบสต็อกอะไหล่ NSK 6208 ในคลังชลบุรีคงเหลือ 12 ชิ้น (ต่ำกว่า Min-Stock 50) จึงทำหน้าที่กวาดใบขอซื้อ (PR) ทั่วทั้งเครือองค์กร พบโรงงานระยองต้องการ 800 ชิ้น และอยุธยาต้องการ 388 ชิ้น รวมยอดจัดซื้อเป็น 1,200 ชิ้น เพื่อสร้างอำนาจต่อรอง", toolCall: "sap_query_inventory(part_no='6208-2RS1') ➔ Demand: 1,200 units" },
                        { step: 2, agent: "Analyst Agent (RAG + Tsuzumi)", time: "T+1.05s | On-Premise", title: "ค้นหามาตรฐาน JIS B 1514 และคำนวณ TCO", thought: "ค้นหาเอกสารสเปกชิ้นส่วนผ่าน BM25+FAISS จับคู่มาตรฐาน JIS B 1514 และคำนวณสมการ TCO กำหนดเพดานราคาสูงสุดไม่เกิน ฿395.00/ชิ้น", toolCall: "rag_retrieve('NSK 6208 JIS B 1514') ➔ Score: 0.96 | Target: ฿395.00" },
                        { step: 3, agent: "Strategic Negotiator (Game Theory)", time: "T+3.20s | BATNA Engine", title: "การแลกเปลี่ยนผลประโยชน์ (Concession Exchange)", thought: "สยาม พรีซิชั่น เสนอแรกที่ ฿425 สูงกว่าเพดาน TCO ฿30 หากปฏิเสธทันทีอาจเสียคู่ค้า จึงหยิบเงื่อนไขอำนาจต่อรองจากยอด 1,200 ชิ้นมาแลกเปลี่ยน: 'ขอราคา ฿398 แลกสัญญา 1 ปี และเครดิต 45 วัน'", toolCall: "vendor_concession_eval() ➔ สยาม พรีซิชั่น ตกลงที่ ฿398 ✓" },
                        { step: 4, agent: "Guardrail Agent", time: "T+3.45s | Rule Engine", title: "ตรวจสอบความถูกต้องตามระเบียบบริษัท", thought: "ตรวจราคาไม่เกินงบประมาณ (฿398 <= ฿400), คู่ค้าอยู่ใน AVL (V-4019), มีเงื่อนไขค่าปรับส่งช้า 0.5%/วัน ผ่านเกณฑ์ 100%", toolCall: "audit_verify(vendor='V-4019') ➔ 100% COMPLIANT" },
                        { step: 5, agent: "LangGraph Interrupt", time: "T+3.50s | HITL", title: "หยุดรอผู้บริหารลงนามดิจิทัล (Sign-Off)", thought: "ระบบสร้างร่างสัญญาฉบับสมบูรณ์ และระงับการทำงานอัตโนมัติ เพื่อส่งมอบให้ผู้จัดการฝ่ายจัดซื้อตรวจสอบ Audit Trail และลงนาม", toolCall: "interrupt_await_human(role='CPO', action='DIGITAL_SIGN_OFF')" }
                    ]
                },
                smc: {
                    title: "ชุดซีลกระบอกลม SMC (MGPM25) ยอดรวม 80 ชุด",
                    budgetStr: "฿1,850.00/ชุด (฿148,000)",
                    targetStr: "฿1,635.00/ชุด (เซฟ -9.8%)",
                    chips: ["รวมยอด PR ทั่วทั้งเครือ", "กำหนดส่งมอบใน 5 วัน", "ผูกสัญญาซื้อซ้ำ 1 ปี"],
                    vendors: [
                        {
                            id: "pneu",
                            name: "บจก. นิวเมติกส์ เซ็นเตอร์ (V-1102)",
                            price: "฿1,635.00",
                            credit: "30 วัน",
                            leadTime: "5 วันทำการ",
                            warranty: "1 ปี",
                            cert: "SMC Genuine Parts ✓",
                            status: "ตกลงราคาแล้ว (฿1,635.00)",
                            statusBadge: "badge-success text-white",
                            outcome: "ประหยัด ฿14,200 (-9.8%) | ค่าปรับส่งช้า 0.5%/วัน",
                            ladder: [
                                { round: "Ask", title: "ราคาขายปลีกปกติ", price: "฿1,850.00", tag: "List Price", color: "border-slate-300 text-slate-500", note: "ราคาซื้อเฉพาะหน้าร้าน" },
                                { round: "R1", title: "ซัพพลายเออร์ลดเบื้องต้น", price: "฿1,720.00", tag: "Supplier Discount", color: "border-slate-300 text-slate-500", note: "ลดตามยอด 80 ชุด" },
                                { round: "Agreed", title: "AI ต่อรองราคาเหมารวม SLA", price: "฿1,635.00", tag: "Agreed ✓", color: "border-emerald-500 bg-emerald-50 text-emerald-900 font-bold", note: "ประหยัดรวม ฿14,200" }
                            ],
                            messages: [
                                { sender: "vendor", name: "นิวเมติกส์ เซ็นเตอร์", time: "11:10", text: "ชุดซีล SMC MGPM25 ราคาปกติ 1,850 บาท/ชุด สำหรับล็อต 80 ชุด ทางเราลดให้ได้ 1,720 บาทครับ" },
                                { sender: "agent", name: "AI จัดซื้ออัตโนมัติ (Autonomous Agent)", time: "11:12", text: "ทางโรงงานรวมยอดการสั่งซื้อ 80 ชุดเพื่อเปิดออเดอร์ล็อตเดียว ขอต่อรองราคาเหมาที่ 1,635.00 บาท/ชุด พร้อมเงื่อนไขรับประกันส่งมอบภายใน 5 วันทำการครับ", tactic: "[กลยุทธ์ต่อรอง: รวมยอดสั่งซื้อแลกเงื่อนไข SLA จัดส่งด่วน]" },
                                { sender: "vendor", name: "นิวเมติกส์ เซ็นเตอร์", time: "11:15", text: "ยินดีรับเงื่อนไขราคา 1,635.00 บาท/ชุด พร้อมทำข้อตกลง SLA การส่งมอบภายใน 5 วันทำการครับ" }
                            ]
                        }
                    ],
                    reasoning: [
                        { step: 1, agent: "Analyst Agent", time: "T+0.35s", title: "ตรวจจุดสั่งซื้อซ้ำ (Reorder Point)", thought: "สต็อกในคลังเหลือ 3 ชุด ถึงจุด Reorder Point วิกฤตสำหรับรอบ Preventive Maintenance จึงรวมยอดใบขอซื้อทั้งโรงงานได้ 80 ชุด", toolCall: "sap_check_rop('MGPM25') ➔ Low Stock Alert" },
                        { step: 2, agent: "Strategic Negotiator", time: "T+2.10s", title: "เจรจาผูกเงื่อนไข SLA", thought: "ต่อรองราคาลงจาก ฿1,850 เหลือ ฿1,635/ชุด แลกกับการให้สัญญาจัดซื้ออะไหล่นิวเมติกส์ต่อเนื่องและระบุค่าปรับส่งช้า 0.5%/วัน", toolCall: "batna_tradeoff(vendor='V-1102', price=1635) ➔ Agreed ✓" }
                    ]
                },
                schneider: {
                    title: "เบรกเกอร์ Schneider Compact NSX (100A) 25 เครื่อง",
                    budgetStr: "฿8,300.00/ตัว (฿207,500)",
                    targetStr: "฿7,200.00 - ฿7,250.00/ตัว (เซฟ -12.7%)",
                    chips: ["ยื่นราคาปิดดีล ฿7,250", "ขอขยายเครดิตเป็น 60 วัน", "ขอส่งมอบด่วน 3 วันฟรีค่าส่ง", "ขอใบรับรอง IEC 60947"],
                    vendors: [
                        {
                            id: "sec",
                            name: "บจก. สยาม อิเล็คทริค เซ็นเตอร์ (V-1880)",
                            price: "฿7,350.00",
                            credit: "45 วัน",
                            leadTime: "5 วันทำการ",
                            warranty: "2 ปี (On-site)",
                            cert: "IEC 60947-2 Standard ✓",
                            status: "Best Offer (฿7,350.00)",
                            statusBadge: "badge-info text-white",
                            outcome: "กำลังต่อรองรอบที่ 2 เพื่อกดให้ถึงเป้าหมาย ฿7,200 - ฿7,250",
                            ladder: [
                                { round: "Ask", title: "ราคาเปิดแรกซัพพลายเออร์", price: "฿7,600.00", tag: "Initial Ask", color: "border-slate-300 text-slate-500", note: "สูงกว่างบประมาณ TCO ฿400" },
                                { round: "R1", title: "AI สวนราคาเป้าหมายอ้างอิง", price: "฿7,200.00", tag: "AI Counter", color: "border-blue-300 text-blue-700", note: "อิงฐานข้อมูลสัญญาเดิม" },
                                { round: "R2", title: "ซัพพลายเออร์ปรับลดข้อเสนอ", price: "฿7,350.00", tag: "Current Offer", color: "border-amber-400 bg-amber-50 text-amber-900 font-bold", note: "ลดลง ฿250/ตัว (เซฟ ฿6,250)" }
                            ],
                            messages: [
                                { sender: "vendor", name: "สยาม อิเล็คทริค (ฝ่ายขาย)", time: "09:15", text: "Schneider NSX100F 3P จำนวน 25 ตัว ทางเราเสนอราคาที่ 7,600 บาท/ตัว ครับ" },
                                { sender: "agent", name: "AI จัดซื้ออัตโนมัติ (Autonomous Agent)", time: "09:20", text: "จากงบประมาณและข้อมูลราคาอ้างอิงของโรงงาน ทางเรามีเป้าหมายจัดซื้อที่ 7,200 บาท/ตัว หากท่านปรับราคาลงได้ ทางเราพร้อมออกใบสั่งซื้อทันทีครับ", tactic: "[กลยุทธ์ต่อรอง: ยื่นราคาเป้าหมาย TCO]" },
                                { sender: "vendor", name: "สยาม อิเล็คทริค (ฝ่ายขาย)", time: "09:30", text: "ทางเราขอปรับลดราคาลงมาที่ 7,350 บาท/ตัว เป็นข้อเสนอพิเศษสุดสำหรับล็อตนี้แล้วครับ" }
                            ]
                        },
                        {
                            id: "abb",
                            name: "บจก. เพาเวอร์ โซลูชั่น ดีสทริบิวเตอร์ (V-3410)",
                            price: "฿7,480.00",
                            credit: "30 วัน",
                            leadTime: "7 วันทำการ",
                            warranty: "1 ปี",
                            cert: "IEC 60947-2 ✓",
                            status: "เสนอราคา ฿7,480.00",
                            statusBadge: "badge-ghost",
                            outcome: "คู่แข่งรายที่ 2 ยื่นราคาสูงกว่าเจ้าแรก ฿130/ตัว",
                            ladder: [
                                { round: "Ask", title: "ราคาเปิดแรก", price: "฿7,480.00", tag: "Standby Offer", color: "border-slate-300 text-slate-500", note: "สูงกว่าสยาม อิเล็คทริค" }
                            ],
                            messages: [
                                { sender: "vendor", name: "เพาเวอร์ โซลูชั่น (ฝ่ายขาย)", time: "09:25", text: "ยื่นราคา Schneider NSX ที่ 7,480 บาท/ตัว เครดิต 30 วันครับ" },
                                { sender: "agent", name: "AI จัดซื้ออัตโนมัติ (Autonomous Agent)", time: "09:28", text: "ขณะนี้มีข้อเสนอที่ดีกว่าอยู่ที่ 7,350 บาท หากท่านไม่สามารถปรับราคาลงได้ ขออนุญาตจัดลำดับเป็นตัวเลือกรองครับ", tactic: "[กลยุทธ์ต่อรอง: ใช้แรงกดดันราคาจากคู่แข่ง]" }
                            ]
                        },
                        {
                            id: "tep",
                            name: "บจก. ไทย เอ็นจิเนียริ่ง พาร์ท (V-1205)",
                            price: "฿7,550.00",
                            credit: "30 วัน",
                            leadTime: "7 วันทำการ",
                            warranty: "1 ปี",
                            cert: "IEC 60947-2 ✓",
                            status: "เสนอราคา ฿7,550.00",
                            statusBadge: "badge-ghost",
                            outcome: "ราคาสูงกว่าคู่แข่ง และไม่ยอมขยายเครดิตเทอม",
                            ladder: [
                                { round: "Ask", title: "ราคาเปิดแรก", price: "฿7,550.00", tag: "Initial Ask", color: "border-slate-300 text-slate-500", note: "ยื่นราคาที่ ฿7,550" },
                                { round: "R1", title: "ซัพพลายเออร์ยืนราคาเดิม", price: "฿7,550.00", tag: "Rejected", color: "border-rose-300 text-rose-700", note: "ไม่ยอมขยายเครดิตเทอม" }
                            ],
                            messages: [
                                { sender: "vendor", name: "ไทย เอ็นจิเนียริ่ง", time: "09:22", text: "เบรกเกอร์ Schneider NSX100F ยื่นราคาที่ 7,550 บาท/ตัว เครดิต 30 วัน จัดส่ง 7 วันทำการครับ" },
                                { sender: "agent", name: "AI จัดซื้ออัตโนมัติ (Autonomous Agent)", time: "09:26", text: "ขณะนี้มีคู่ค้ารายอื่นยื่นข้อเสนอที่ 7,350 บาท และยินดีให้เครดิต 45 วัน หากไม่สามารถปรับเงื่อนไขได้ ทางเราขอจัดอันดับไว้เป็นตัวเลือกรองครับ", tactic: "[กลยุทธ์ต่อรอง: ปฏิเสธเงื่อนไขไม่ตรงเกณฑ์]" },
                                { sender: "vendor", name: "ไทย เอ็นจิเนียริ่ง", time: "09:29", text: "ทางเราขอยืนยันราคาเดิมที่ 7,550 บาทครับ ไม่สามารถขยายเครดิตเกิน 30 วันได้ครับ" }
                            ]
                        }
                    ],
                    reasoning: [
                        { step: 1, agent: "Analyst Agent", time: "T+0.50s", title: "ดึงสเปกเบรกเกอร์ IEC 60947-2", thought: "ตรวจพบ PR เบรกเกอร์ 25 เครื่อง ดึงสเปกเทียบราคาตลาดและเปิดเทียบเชิญ 3 ตัวแทนจำหน่าย Schneider AVL", toolCall: "benchmark_pricing('NSX100F') ➔ Target: ฿7,200" },
                        { step: 2, agent: "Strategic Negotiator", time: "T+4.15s", title: "เปิดห้องประมูลคู่ขนาน 3 เจ้า", thought: "กำลังต่อรองรอบที่ 2 เพื่อกดให้ถึงราคา TCO ฿7,200", toolCall: "live_bidding() ➔ Ongoing" }
                    ]
                },
                omron: {
                    title: "รีเลย์ Omron MY4N-D2 200 ชุด",
                    budgetStr: "฿220.00/ชุด (฿44,000)",
                    targetStr: "฿185.00/ชุด (เซฟ -15.9%)",
                    chips: ["รวมยอดจัดซื้อ Line A+B", "ขอเครดิต 45 วัน", "ส่งมอบสัปดาห์หน้า"],
                    vendors: [
                        {
                            id: "omr",
                            name: "บจก. ไทย ออโตเมชั่น พาร์ท (V-2900)",
                            price: "฿185.00",
                            credit: "45 วัน",
                            leadTime: "3 วันทำการ",
                            warranty: "1 ปี",
                            cert: "Omron Verified ✓",
                            status: "ตกลงราคาแล้ว (฿185.00)",
                            statusBadge: "badge-success text-white",
                            outcome: "ประหยัด ฿7,000 (-15.9%) จากการรวมยอด Line A + B",
                            ladder: [
                                { round: "Ask", title: "ราคาปลีกเดิม", price: "฿220.00", tag: "List Price", color: "border-slate-300 text-slate-500", note: "สั่งยอดแยกแผนก" },
                                { round: "R1", title: "ส่วนลดเบื้องต้น 200 ตัว", price: "฿195.00", tag: "Volume Quote", color: "border-slate-300 text-slate-500", note: "ลดลง ฿25/ชุด" },
                                { round: "Agreed", title: "AI ปิดดีลยอดรวม 2 ไลน์", price: "฿185.00", tag: "Agreed ✓", color: "border-emerald-500 bg-emerald-50 text-emerald-900 font-bold", note: "เซฟ ฿7,000 (-15.9%)" }
                            ],
                            messages: [
                                { sender: "vendor", name: "ไทย ออโตเมชั่น", time: "14:10", text: "รีเลย์ Omron MY4N-D2 พร้อม Socket ราคาขายปลีก 220 บาท สั่ง 200 ตัว ลดให้ได้ 195 บาท/ชุด ครับ" },
                                { sender: "agent", name: "AI จัดซื้ออัตโนมัติ (Autonomous Agent)", time: "14:12", text: "เราได้รวบรวมยอดเบิกใช้งานของไลน์ผลิตทั้ง 2 ส่วนรวมเป็น 200 ชุด ขอยื่นราคาเป้าหมายที่ 185.00 บาท/ชุด โดยรอบนี้ขอวางบิลรอบสิ้นเดือน เครดิต 45 วันครับ", tactic: "[กลยุทธ์ต่อรอง: ยอดรวมข้ามแผนกแลกเครดิตเทอม]" },
                                { sender: "vendor", name: "ไทย ออโตเมชั่น", time: "14:15", text: "ตกลงครับ ทางเรายินดีให้ราคา 185.00 บาท/ชุด เครดิต 45 วัน พร้อมจัดส่งของให้สัปดาห์หน้าครับ" }
                            ]
                        }
                    ],
                    reasoning: [
                        { step: 1, agent: "Analyst Agent", time: "T+0.28s", title: "รวมยอดจัดซื้อ Line A & Line B", thought: "ตรวจพบ PR รีเลย์จาก 2 แผนก รวบรวมยอดเป็น 200 ชุดเพื่อขอลดราคา Volume Discount", toolCall: "aggregate_orders() ➔ Total 200 Sets" }
                    ]
                },
                bando: {
                    title: "สายพานไทม์มิ่ง Bando (STS S8M) 300 เส้น",
                    budgetStr: "฿310.00/เส้น (฿93,000)",
                    targetStr: "฿285.00/เส้น (เซฟ -8.1%)",
                    chips: ["ยืนราคา ฿285 รวมส่ง 3 โรงงาน", "แบ่งส่ง 3 งวด", "เครดิต 45 วัน"],
                    vendors: [
                        {
                            id: "ban",
                            name: "บจก. เบลท์ แอนด์ พูลเล่ย์ อินดัสทรี (V-1088)",
                            price: "฿285.00",
                            credit: "45 วัน",
                            leadTime: "แบ่งส่ง 3 งวด",
                            warranty: "1 ปี",
                            cert: "Bando Original Part ✓",
                            status: "Best Bidder (฿285.00)",
                            statusBadge: "badge-info text-white",
                            outcome: "ราคาดีที่สุด | ฟรีค่าขนส่ง 3 โรงงาน | เครดิต 45 วัน",
                            ladder: [
                                { round: "Ask", title: "ราคาเปิดแรก", price: "฿310.00", tag: "Initial Ask", color: "border-slate-300 text-slate-500", note: "ราคาเดิมก่อนรวมยอด" },
                                { round: "Agreed", title: "AI สวนราคาเป้าหมาย 3 โรงงาน", price: "฿285.00", tag: "Agreed ✓", color: "border-emerald-500 bg-emerald-50 text-emerald-900 font-bold", note: "เซฟ ฿7,500 ฟรีค่าส่ง 3 จุด" }
                            ],
                            messages: [
                                { sender: "vendor", name: "เบลท์ แอนด์ พูลเล่ย์ (ฝ่ายขาย)", time: "13:05", text: "สายพาน Bando STS S8M จำนวน 300 เส้น เสนอราคาเบื้องต้นที่ 310.00 บาท/เส้น รวมส่ง 3 โรงงานครับ" },
                                { sender: "agent", name: "AI จัดซื้ออัตโนมัติ (Autonomous Agent)", time: "13:08", text: "รอบนี้เราได้รวบรวมยอดจัดซื้อจาก 3 โรงงาน (ชลบุรี, อยุธยา, สระบุรี) รวม 300 เส้น อ้างอิงประวัติราคาเดิมและปริมาณสั่งซื้อ ทางเราขอตั้งราคาเป้าหมายที่ 285.00 บาท/เส้น หากยืนราคานี้ได้ ทางเราพร้อมออกใบสั่งซื้อล็อตเดียวทันทีครับ", tactic: "[กลยุทธ์ต่อรอง: ใช้ Volume Aggregation รวม 3 โรงงาน เพื่อดึงส่วนลดราคาส่ง]" },
                                { sender: "vendor", name: "เบลท์ แอนด์ พูลเล่ย์ (ฝ่ายขาย)", time: "13:12", text: "ยินดีรับราคา 285.00 บาท/เส้น ครับ โดยขอเงื่อนไขส่งมอบแบ่งเป็น 3 งวด งวดละ 100 เส้นตามแผนงานซ่อมบำรุงครับ" }
                            ]
                        },
                        {
                            id: "spt",
                            name: "บจก. สยาม พาวเวอร์ ทรานสมิชชั่น (V-2210)",
                            price: "฿295.00",
                            credit: "30 วัน",
                            leadTime: "7 วันทำการ",
                            warranty: "1 ปี",
                            cert: "Bando Industrial ✓",
                            status: "เสนอราคา ฿295.00",
                            statusBadge: "badge-ghost",
                            outcome: "ราคาสูงกว่าคู่แข่ง ฿10/เส้น ไม่ผ่านเกณฑ์ TCO",
                            ladder: [
                                { round: "Ask", title: "ยื่นราคา", price: "฿295.00", tag: "Higher Quote", color: "border-slate-300 text-slate-500", note: "สูงกว่าเบลท์ แอนด์ พูลเล่ย์" }
                            ],
                            messages: [
                                { sender: "vendor", name: "สยาม พาวเวอร์", time: "13:06", text: "ยื่นราคาที่ 295.00 บาท/เส้น เครดิต 30 วันครับ" },
                                { sender: "agent", name: "AI จัดซื้ออัตโนมัติ (Autonomous Agent)", time: "13:10", text: "ขณะนี้มีข้อเสนอที่ดีกว่าอยู่ที่ 285.00 บาท รวมค่าขนส่งแล้ว หากท่านไม่ปรับลดราคา ขออนุญาตให้สิทธิ์เจ้าอื่นครับ", tactic: "[กลยุทธ์ต่อรอง: ใช้ราคาเปรียบเทียบตลาด]" },
                                { sender: "vendor", name: "สยาม พาวเวอร์", time: "13:13", text: "ทางเราขอยืนยันราคา 295.00 บาทครับ เนื่องจากต้นทุนล็อตนี้นำเข้ามาสูง ไม่สามารถลดเพิ่มได้ครับ" }
                            ]
                        },
                        {
                            id: "ttb",
                            name: "บจก. ไทย ทรานสมิชชั่น เบลท์ (V-3401)",
                            price: "฿305.00",
                            credit: "30 วัน",
                            leadTime: "5 วันทำการ",
                            warranty: "1 ปี",
                            cert: "Bando Industrial ✓",
                            status: "เสนอราคา ฿305.00",
                            statusBadge: "badge-ghost",
                            outcome: "ราคาสูงเกินงบประมาณ ตกรอบการประมูล",
                            ladder: [
                                { round: "Ask", title: "ยื่นราคา", price: "฿305.00", tag: "Logistics Excluded", color: "border-rose-300 text-rose-700", note: "ไม่รวมส่ง 3 โรงงาน" }
                            ],
                            messages: [
                                { sender: "vendor", name: "ไทย ทรานสมิชชั่น", time: "13:04", text: "สายพาน Bando S8M ล็อต 300 เส้น เสนอราคาที่ 305.00 บาท/เส้น ส่งฟรีเฉพาะคลังชลบุรีครับ" },
                                { sender: "agent", name: "AI จัดซื้ออัตโนมัติ (Autonomous Agent)", time: "13:09", text: "ราคา 305.00 บาทสูงกว่าเกณฑ์ TCO และไม่รวมค่าส่ง 3 โรงงาน หากไม่ปรับราคาและเงื่อนไข ทางเราขอสงวนสิทธิ์ไม่รับข้อเสนอนี้ครับ", tactic: "[กลยุทธ์ต่อรอง: ปฏิเสธข้อเสนอที่ไม่รวมค่าส่ง]" },
                                { sender: "vendor", name: "ไทย ทรานสมิชชั่น", time: "13:14", text: "ทางเราไม่สามารถแบกรับค่าขนส่งข้ามจังหวัดเพิ่มเติมได้ ขอคงราคาเดิมครับ" }
                            ]
                        },
                        {
                            id: "abp",
                            name: "บจก. เอเชีย เบลติ้ง ซัพพลาย (V-4520)",
                            price: "฿290.00",
                            credit: "30 วัน",
                            leadTime: "15 วันทำการ",
                            warranty: "1 ปี",
                            cert: "Bando Industrial ✓",
                            status: "SLA ไม่ผ่าน (15 วัน)",
                            statusBadge: "badge-error text-white",
                            outcome: "สต็อกไม่พอ ต้องรอของ 15 วัน เสี่ยงกระทบไลน์ผลิต",
                            ladder: [
                                { round: "Ask", title: "ยื่นราคา", price: "฿290.00", tag: "Stock Shortage", color: "border-rose-300 text-rose-700", note: "ส่งช้า 15 วัน ตกเกณฑ์ SLA" }
                            ],
                            messages: [
                                { sender: "vendor", name: "เอเชีย เบลติ้ง", time: "13:02", text: "ทางเราทำราคาได้ 290.00 บาท/เส้น แต่มีสินค้าพร้อมส่ง 100 เส้น อีก 200 เส้นต้องรอของ 15 วันทำการครับ" },
                                { sender: "agent", name: "AI จัดซื้ออัตโนมัติ (Autonomous Agent)", time: "13:07", text: "ทางโรงงานจำเป็นต้องสำรองเข้าคลังพร้อมกัน 3 จุดภายใน 5 วันทำการ การส่งมอบล่าช้า 15 วันไม่ผ่านเกณฑ์ SLA ความปลอดภัยของสายการผลิตครับ", tactic: "[Risk Control: คัดกรองซัพพลายเออร์ที่ไม่ผ่านเกณฑ์ SLA]" },
                                { sender: "vendor", name: "เอเชีย เบลติ้ง", time: "13:11", text: "เข้าใจครับ หากต้องการสต็อกพร้อมส่งทันที ทางเรายังจัดหาไม่ทันในรอบนี้ครับ" }
                            ]
                        }
                    ],
                    reasoning: [
                        { step: 1, agent: "ERP Scanner", time: "T+0.45s", title: "ตรวจคลังพัสดุกลางและรวมยอด 3 โรงงาน (Spend Aggregation)", thought: "คลังพัสดุกลางแจ้งเตือนสายพานใกล้หมด จึงทำหน้าที่ดึง Demand จากโรงงานชลบุรี อยุธยา และสระบุรี รวมยอดจัดซื้อได้ 300 เส้น", toolCall: "sap_check_stock('S8M') ➔ Aggregated Demand: 300 units" },
                        { step: 2, agent: "TCO Engine", time: "T+1.20s", title: "คำนวณสมการ TCO รวมค่าขนส่ง", thought: "คำนวณต้นทุนรวม (TCO) สินค้า + ขนส่ง 3 จุด กำหนดกรอบราคาไม่เกิน ฿285/เส้น", toolCall: "tco_formula(demand=300, logistics=3_plants) ➔ Target: ฿285.00" },
                        { step: 3, agent: "Strategic Negotiator", time: "T+2.50s", title: "เปิดห้องประมูลเทียบ 4 ซัพพลายเออร์", thought: "เจรจาบีบราคาลงมาที่ ฿285/เส้น ประหยัดต้นทุนรวม ฿7,500", toolCall: "multi_bid_negotiation() ➔ Best: ฿285.00" }
                    ]
                },
                mitsubishi: {
                    title: "เม็ดมีดกลึง Mitsubishi Materials CNMG 500 ชิ้น",
                    budgetStr: "฿195.00/ชิ้น (฿97,500)",
                    targetStr: "฿170.00/ชิ้น (เซฟ -12.8%)",
                    chips: ["อิงราคาเดิมสัญญา LTA", "ขอเครดิต 60 วัน", "ส่งมอบตรงตู้ Tool Crib ใน 3 วัน"],
                    vendors: [
                        {
                            id: "mit",
                            name: "บจก. เคียวเซร่า & มิตซูบิชิ ทูลส์ (V-3088)",
                            price: "฿170.00",
                            credit: "60 วัน",
                            leadTime: "3 วันทำการ",
                            warranty: "ISO 1832 Certified",
                            cert: "Mitsubishi Genuine ✓",
                            status: "เจรจาราคาสำเร็จ (฿170.00)",
                            statusBadge: "badge-success text-white",
                            outcome: "เซฟงบ ฿12,500 (-12.8%) | เครดิต 60 วัน ส่งเข้า Tool Crib 3 วัน",
                            ladder: [
                                { round: "Ask", title: "ราคาเบิกจ่ายหน้าร้านเดิม", price: "฿195.00", tag: "Spot Buy", color: "border-slate-300 text-slate-500", note: "ราคาซื้อย่อยหน้าตู้" },
                                { round: "Agreed", title: "AI ยื่นสัญญา LTA ยอด 500 ชิ้น", price: "฿170.00", tag: "Agreed ✓", color: "border-emerald-500 bg-emerald-50 text-emerald-900 font-bold", note: "ประหยัดงบ ฿12,500 (-12.8%)" }
                            ],
                            messages: [
                                { sender: "vendor", name: "เคียวเซร่า & มิตซูบิชิ ทูลส์ (ฝ่ายขาย)", time: "09:10", text: "เรียนฝ่ายจัดซื้อ สำหรับเม็ดมีดกลึงคาร์ไบด์ Mitsubishi CNMG120408 จำนวน 500 ชิ้น ราคาเบิกจ่ายหน้างานปกติอยู่ที่ 195.00 บาท/ชิ้น ครับ ยอดรวม 97,500 บาท" },
                                { sender: "agent", name: "AI จัดซื้ออัตโนมัติ (Autonomous Agent)", time: "09:12", text: "ขอบคุณครับ อ้างอิงจากสัญญาซื้อขายเดิมที่เคยทำไว้กับทางบริษัทท่าน ล็อตก่อนเราเคยได้ราคา 168.00 บาท/ชิ้น สำหรับรอบนี้เราเปิดสั่งซื้อล็อตใหญ่ 500 ชิ้น เพื่อเติมสต็อกตู้เบิกส่วนกลาง จึงขอทำสัญญาในราคา 170.00 บาท/ชิ้น เครดิตเทอม 60 วันครับ", tactic: "[กลยุทธ์ต่อรอง: อ้างอิงสัญญาเดิมเพื่อคุมราคาและต่อรองส่วนลด Volume]" },
                                { sender: "vendor", name: "เคียวเซร่า & มิตซูบิชิ ทูลส์ (ฝ่ายขาย)", time: "09:15", text: "หากเป็นการรวมยอดล็อตเดียว 500 ชิ้น ทางผู้จัดการยินดีอนุมัติยืนราคาพิเศษ 170.00 บาท/ชิ้น ตามสัญญาเดิมครับ พร้อมจัดส่งเติมเข้าตู้สต็อกภายใน 3 วันทำการครับ" }
                            ]
                        },
                        {
                            id: "sct",
                            name: "บจก. สยาม คาร์ไบด์ แอนด์ ทูลลิ่ง (V-1420)",
                            price: "฿178.00",
                            credit: "30 วัน",
                            leadTime: "5 วันทำการ",
                            warranty: "ISO 1832",
                            cert: "Carbide Verified ✓",
                            status: "ตกรอบ (฿178.00)",
                            statusBadge: "badge-ghost",
                            outcome: "ราคาและเงื่อนไขไม่ผ่านเกณฑ์เป้าหมาย TCO",
                            ladder: [
                                { round: "Ask", title: "ราคาเปิดแรก", price: "฿178.00", tag: "Initial Ask", color: "border-slate-300 text-slate-500", note: "สูงกว่าราคาเป้าหมาย 170" }
                            ],
                            messages: [
                                { sender: "vendor", name: "สยาม คาร์ไบด์", time: "09:11", text: "เสนอราคาเม็ดมีด Mitsubishi CNMG แท้ 178.00 บาท/ชิ้น เครดิต 30 วัน จัดส่ง 5 วันครับ" },
                                { sender: "agent", name: "AI จัดซื้ออัตโนมัติ (Autonomous Agent)", time: "09:14", text: "ราคา 178 บาท สูงกว่าราคาเป้าหมาย (170 บาท) และเครดิตเทอม 30 วันไม่ผ่านเกณฑ์ หากท่านไม่สามารถปรับราคาลงได้ ทางเราจำเป็นต้องเลือกคู่แข่งครับ", tactic: "[กลยุทธ์ต่อรอง: ยื่นข้อเสนอทางเลือกที่ดีกว่า (Counter-Offer)]" },
                                { sender: "vendor", name: "สยาม คาร์ไบด์", time: "09:17", text: "ทางเราลดราคาได้ต่ำสุด 175.00 บาท/ชิ้น ครับ ไม่สามารถลงถึง 170 บาทได้ ต้องขออภัยด้วยครับ" }
                            ]
                        }
                    ],
                    reasoning: [
                        { step: 1, agent: "Tool Crib Scanner", time: "T+0.25s", title: "ตรวจจับสัญญาณสต็อกวิกฤตจาก Smart Tool Crib", thought: "ตู้เบิกเครื่องมืออัตโนมัติ (Smart Tool Crib) แจ้งเตือนเม็ดมีดกลึง Mitsubishi CNMG120408 เหลือ 45 ชิ้น ต่ำกว่าเกณฑ์ Reorder Point (100 ชิ้น) กวาดความต้องการรอบใหม่รวม 500 ชิ้น เพื่อป้องกันการซื้อ Spot Buy รายย่อยหน้าร้านราคาแพง", toolCall: "tool_crib_alert('CNMG120408') ➔ Reorder Point Triggered | Demand: 500 pcs" },
                        { step: 2, agent: "Analyst Agent (RAG + Tsuzumi)", time: "T+0.85s", title: "สืบค้นสัญญาจัดซื้อในอดีต (Contract RAG Retrieval)", thought: "ใช้ NTT Tsuzumi SLM ค้นหาเอกสารสัญญาจัดซื้อในอดีตผ่าน Vector DB (FAISS) พบสัญญาเก่าเลขที่ LTA-2024-MITS-092 เคยจัดซื้อที่ราคา ฿168/ชิ้น จึงคำนวณสมการ TCO และกำหนดเพดานราคาเจรจา (Walk-away Price) ไว้ไม่เกิน ฿170.00/ชิ้น", toolCall: "rag_contract_search('Mitsubishi CNMG120408') ➔ Best Historical Price: ฿168.00 | TCO Ceiling: ฿170.00" },
                        { step: 3, agent: "Strategic Negotiator", time: "T+2.10s", title: "เปิดห้องเจรจาต่อรองด้วย Game Theory (BATNA)", thought: "นำราคาเพดาน ฿170 เข้าเจรจาคู่ขนานกับ 2 ตัวแทนจำหน่าย โดยใช้สัญญาในอดีตเป็นสมอราคา (Price Anchor) แลกกับยอดรวม 500 ชิ้น และเครดิต 60 วัน ผลลัพธ์: บจก. เคียวเซร่า & มิตซูบิชิ ทูลส์ ยอมรับราคา ฿170.00/ชิ้น", toolCall: "batna_negotiate(vendor='V-3088', target_price=170, terms='Credit 60D') ➔ Agreed ✓" },
                        { step: 4, agent: "Compliance Guardrail", time: "T+3.00s", title: "ตรวจสอบระเบียบจัดซื้อและมาตรฐานสินค้า ISO 1832", thought: "ตรวจสอบสเปกเม็ดมีดแท้ตามมาตรฐาน ISO 1832 เครดิตเทอม 60 วัน และผู้ขายอยู่ใน Approved Vendor List (AVL) ถูกต้องตามระเบียบ 100%", toolCall: "guardrail_audit(po_draft) ➔ PASS (100% Policy Compliant)" }
                    ]
                },
                mobil: {
                    title: "น้ำมันเกียร์ Mobil SHC 630 (200L) 20 ถัง",
                    budgetStr: "฿15,800.00/ถัง (฿316,000)",
                    targetStr: "฿13,400.00/ถัง (เซฟ -15.2%)",
                    chips: ["เปิด PO#450098114 เรียบร้อย", "เครดิต 60 วัน", "จัดส่งเข้าคลังเคมีวันจันทร์"],
                    vendors: [
                        {
                            id: "mob",
                            name: "บจก. เอสโซ่ มาร์เก็ตติ้ง (V-0089)",
                            price: "฿13,400.00",
                            credit: "60 วัน",
                            leadTime: "ส่งมอบวันจันทร์",
                            warranty: "รับประกันคุณภาพมาตรฐาน Mobil",
                            cert: "CoA & MSDS Included ✓",
                            status: "ออก PO ใน SAP สำเร็จ ✓",
                            statusBadge: "badge-success text-white",
                            outcome: "ราคา ฿13,400.00/ถัง ประหยัด ฿48,000",
                            ladder: [
                                { round: "Ask", title: "ราคา Spot Buy หน้าคลัง", price: "฿15,800.00", tag: "Spot Price", color: "border-slate-300 text-slate-500", note: "สั่งซื้อเฉพาะหน้า" },
                                { round: "Agreed", title: "AI ทำสัญญารายปี 20 ถัง", price: "฿13,400.00", tag: "Agreed ✓", color: "border-emerald-500 bg-emerald-50 text-emerald-900 font-bold", note: "เซฟงบประมาณ ฿48,000 (-15.2%)" }
                            ],
                            messages: [
                                { sender: "agent", name: "AI จัดซื้ออัตโนมัติ (Autonomous Agent)", time: "15:00", text: "เรียน บจก. เอสโซ่ มาร์เก็ตติ้ง ทางฝ่ายบริหารได้ลงนามอนุมัติสั่งซื้อน้ำมันเกียร์ Mobil SHC 630 จำนวน 20 ถัง ที่ราคา 13,400.00 บาท/ถัง เรียบร้อยแล้วครับ เอกสารใบสั่งซื้อ PO เลขที่ 450098114 ได้ถูกส่งเข้าอีเมลทางการของท่านแล้วครับ" },
                                { sender: "vendor", name: "เอสโซ่ มาร์เก็ตติ้ง", time: "15:02", text: "ได้รับเอกสารใบสั่งซื้อ PO เลขที่ 450098114 เรียบร้อยแล้วครับ ขอบคุณมากครับ ทางเราจะจัดเตรียมสินค้าและส่งมอบเข้าคลังพัสดุในวันจันทร์หน้าครับ" }
                            ]
                        }
                    ],
                    reasoning: [
                        { step: 1, agent: "SAP Dispatcher", time: "Completed", title: "สร้างใบ PO จริงในระบบ SAP S/4HANA", thought: "ผู้บริหารลงนามอนุมัติเรียบร้อย Agent ยิง BAPI_PO_CREATE1 ออกเอกสาร PO#450098114 สำเร็จ 100%", toolCall: "BAPI_PO_CREATE1('450098114') ➔ CONFIRMED ✓" }
                    ]
                },
                skf: {
                    title: "ตลับลูกปืนเม็ดกลมร่องลึก SKF (6310-2Z/C3) - ยอดรวม 800 ชิ้น",
                    budgetStr: "฿680.00 / ชิ้น",
                    targetStr: "฿520.00 / ชิ้น (-15.1%)",
                    vendors: [
                        {
                            name: "บจก. สยามแบริ่ง แอนด์ ทูลส์",
                            price: "฿520.00",
                            credit: "60 วัน (ขยายจาก 30 วัน)",
                            leadTime: "พร้อมส่ง 3 วันทำการ",
                            warranty: "18 เดือน (มาตรฐาน SKF)",
                            cert: "SKF Authorized ✓",
                            status: "ชนะการประมูล (ออกใบ PO)",
                            statusBadge: "badge-success text-white font-bold",
                            outcome: "ผู้ชนะการประมูล | เซฟงบประมาณ ฿128,000 (-15.1%)",
                            ladder: [
                                { round: "Ask", title: "ราคาตั้งต้น Spot Buy", price: "฿680.00", tag: "Initial Quote", color: "border-slate-300 text-slate-500", note: "เครดิต 30 วัน" },
                                { round: "R1", title: "AI เสนอรวมยอดสัญญา LTA 1 ปี", price: "฿550.00", tag: "Counter #1", color: "border-blue-300 text-blue-800", note: "ล็อกโควตา 800 ชิ้น/ปี" },
                                { round: "Agreed", title: "ตกลงปิดดีลสำเร็จ (Final)", price: "฿520.00", tag: "Won Deal ✓", color: "border-emerald-500 bg-emerald-50 text-emerald-900 font-bold", note: "เครดิต 60 วัน + ส่งฟรี DDP" }
                            ],
                            messages: [
                                { sender: "vendor", name: "สยามแบริ่ง แอนด์ ทูลส์ (ฝ่ายขาย)", time: "13:10", text: "สวัสดีครับ ตลับลูกปืน SKF 6310-2Z/C3 ราคามาตรฐานหน้าแคตตาล็อกอยู่ที่ 680 บาท/ชิ้น เครดิต 30 วันครับ" },
                                { sender: "agent", name: "AI จัดซื้ออัตโนมัติ (Autonomous Agent)", time: "13:11", text: "ทางระบบได้รวบรวมความต้องการจากโรงงานในเครือ รวม 800 ชิ้นต่อปี หากทางเราทำสัญญา LTA ล็อกยอดทั้งปี ขอราคาพิเศษที่ 520.00 บาท/ชิ้น พร้อมขยายเครดิตเทอมเป็น 60 วันได้ไหมครับ?", tactic: "[Volume Consolidation + Credit Term Extension]" },
                                { sender: "vendor", name: "สยามแบริ่ง แอนด์ ทูลส์ (ฝ่ายขาย)", time: "13:14", text: "ถ้ารวมยอดสัญญารายปี 800 ชิ้น ทางผู้จัดการอนุมัติราคา 520.00 บาท/ชิ้น พร้อมเครดิต 60 วัน และจัดส่งฟรีถึงคลังทุกสาขาครับ" }
                            ]
                        },
                        {
                            name: "บจก. ยูไนเต็ด อินดัสเทรียล ซัพพลาย",
                            price: "฿565.00",
                            credit: "45 วัน",
                            leadTime: "7 วันทำการ",
                            warranty: "12 เดือน",
                            cert: "ISO 9001 ✓",
                            status: "ไม่ได้รับเลือก (ราคาสูงกว่าเป้า)",
                            statusBadge: "badge-ghost text-slate-600 border border-slate-300",
                            outcome: "ไม่ได้รับเลือก | ราคาสุดท้ายสูงกว่าผู้ชนะ",
                            ladder: [
                                { round: "Ask", title: "ราคาเสนอเริ่มต้น", price: "฿660.00", tag: "Initial", color: "border-slate-300 text-slate-500", note: "เครดิต 30 วัน" },
                                { round: "Final", title: "ราคาต่ำสุดที่ให้ได้", price: "฿565.00", tag: "Outbid", color: "border-slate-300 text-slate-600", note: "ลดลงมากกว่านี้ไม่ได้" }
                            ],
                            messages: [
                                { sender: "vendor", name: "ยูไนเต็ด อินดัสเทรียล (ฝ่ายขาย)", time: "13:15", text: "ทางเราลดสุดได้อยู่ที่ 565 บาท/ชิ้น เครดิต 45 วันครับ ต่ำกว่านี้ไม่ไหวครับ" }
                            ]
                        }
                    ],
                    reasoning: [
                        { step: 1, agent: "Spend Aggregator", time: "13:05:10", title: "รวบรวมความต้องการสัญญา LTA 800 ชิ้น", thought: "ตรวจพบการสั่งซื้อ SKF 6310-2Z/C3 จึงรวมเป็นสัญญารายปี LTA 800 ชิ้น", toolCall: "SELECT SUM(qty) FROM sap_pr WHERE mat_code='MRO-BRG-002' ➔ 800 pcs" },
                        { step: 2, agent: "Negotiation Engine", time: "13:14:22", title: "ปิดดีลราคา TCO ต่ำสุด + ขยายเครดิต 60 วัน", thought: "ซัพพลายเออร์ยอมลดราคาจาก ฿680 เหลือ ฿520 และขยายเครดิตเป็น 60 วัน คิดเป็นผลประหยัดรวม ฿128,000", toolCall: "evaluate_tco(price=520.00, credit_days=60) ➔ RANK #1" }
                    ]
                },
                thk: {
                    title: "บล็อกลิเนียร์ไกด์ความแม่นยำสูง THK (HSR25A) - ยอดรวม 9,786 ตัว",
                    budgetStr: "฿2,600.00 / ตัว",
                    targetStr: "฿2,334.80 / ตัว (-11.0%)",
                    vendors: [
                        {
                            name: "บจก. ทีเอชเค โมชั่น ซิสเต็มส์ (ประเทศไทย)",
                            price: "฿2,334.80",
                            credit: "60 วัน",
                            leadTime: "พร้อมส่ง 5 วันทำการ",
                            warranty: "24 เดือน (แท้ 100% จากญี่ปุ่น)",
                            cert: "THK Official OEM ✓",
                            status: "ชนะการประมูล (กำลังเจรจารอบสุดท้าย)",
                            statusBadge: "badge-success text-white font-bold",
                            outcome: "ผู้นำประมูล | เซฟงบประมาณ ฿2,796,913 (-11.0%)",
                            ladder: [
                                { round: "Ask", title: "ราคาตั้งต้น Spot Buy", price: "฿2,600.00", tag: "Initial Quote", color: "border-slate-300 text-slate-500", note: "เครดิต 30 วัน" },
                                { round: "R1", title: "AI เสนอ Annual Frame Contract", price: "฿2,420.00", tag: "Counter #1", color: "border-blue-300 text-blue-800", note: "รวมยอด 9,786 ตัว" },
                                { round: "Current", title: "ข้อเสนอล่าสุดพร้อมเครดิต 60 วัน", price: "฿2,334.80", tag: "Best Offer ✓", color: "border-emerald-500 bg-emerald-50 text-emerald-900 font-bold", note: "เซฟรวม ฿2,796,913" }
                            ],
                            messages: [
                                { sender: "vendor", name: "ทีเอชเค โมชั่น ซิสเต็มส์", time: "14:05", text: "บล็อกลิเนียร์ไกด์ THK HSR25A ของแท้จากญี่ปุ่น ราคาตั้งต้น 2,600 บาท/ตัว ครับ" },
                                { sender: "agent", name: "AI จัดซื้ออัตโนมัติ (Autonomous Agent)", time: "14:07", text: "เนื่องจากเรามียอดแผนซ่อมบำรุงเครื่อง CNC ทั้งปีรวม 9,786 ตัว จาก 50 PR หากทำสัญญาล็อกโควตารายปี ขอราคาที่ 2,334.80 บาท/ตัว และเครดิต 60 วันได้ไหมครับ?", tactic: "[Annual Frame Contract + OEM Stock Reservation]" },
                                { sender: "vendor", name: "ทีเอชเค โมชั่น ซิสเต็มส์", time: "14:12", text: "ยินดีครับ สำหรับยอด 9,786 ตัว ทางเราให้ราคาพิเศษ 2,334.80 บาท พร้อมเครดิต 60 วัน และสำรอง Safety Stock ไว้ที่คลังบางนาให้ทันทีครับ" }
                            ]
                        }
                    ],
                    reasoning: [
                        { step: 1, agent: "Spend Aggregator", time: "14:00:05", title: "รวบรวมแผน PM เครื่องจักร CNC ทั้งหมด 50 PR", thought: "รวมยอด THK Linear Guide HSR25A จำนวน 9,786 ตัว เพื่อปลดล็อกส่วนลด OEM Tier สูงสุด", toolCall: "aggregate_pr('THK-HSR25A') ➔ 9,786 units" },
                        { step: 2, agent: "Negotiation Engine", time: "14:12:30", title: "เจรจาลดราคา 11.0% พร้อมล็อก Safety Stock", thought: "ประหยัดงบได้ ฿2,796,913 และป้องกันเครื่องจักรหยุดชะงักด้วยการให้ซัพพลายเออร์สำรองสต็อก", toolCall: "verify_sla(safety_stock=True, credit=60) ➔ PASSED ✓" }
                    ]
                },
                gates: {
                    title: "สายพานไทม์มิ่งโพลียูรีเทนเสริมใยเหล็ก Gates (8MGT) - ยอดรวม 14,015 เส้น",
                    budgetStr: "฿1,200.00 / เส้น",
                    targetStr: "฿1,053.60 / เส้น (-12.9%)",
                    vendors: [
                        {
                            name: "บจก. เพาเวอร์ ทรานสมิชชั่น โซลูชั่น",
                            price: "฿1,053.60",
                            credit: "60 วัน",
                            leadTime: "ส่งมอบภายใน 3 วัน",
                            warranty: "18 เดือน",
                            cert: "Gates Authorized ✓",
                            status: "ชนะการประมูล (พร้อมอนุมัติ)",
                            statusBadge: "badge-success text-white font-bold",
                            outcome: "ผู้ชนะการประมูล | เซฟงบประมาณ ฿2,175,905 (-12.9%)",
                            ladder: [
                                { round: "Ask", title: "ราคาป้าย Spot Buy", price: "฿1,200.00", tag: "Initial", color: "border-slate-300 text-slate-500", note: "ซื้อแยกบิลย่อย" },
                                { round: "Agreed", title: "ราคาหลัง AI รวมยอด 14,015 เส้น", price: "฿1,053.60", tag: "Agreed ✓", color: "border-emerald-500 bg-emerald-50 text-emerald-900 font-bold", note: "เซฟ ฿2,175,905 + เครดิต 60 วัน" }
                            ],
                            messages: [
                                { sender: "agent", name: "AI จัดซื้ออัตโนมัติ (Autonomous Agent)", time: "11:20", text: "สวัสดีครับ ทางโรงงานรวบรวมยอดสายพาน Gates Poly Chain GT Carbon จำนวน 14,015 เส้น (50 PR) ขอเสนอทำสัญญาจัดซื้อรายปีที่ราคาเป้าหมาย 1,053.60 บาท/เส้น เครดิต 60 วันครับ", tactic: "[Multi-Plant Spend Aggregation]" },
                                { sender: "vendor", name: "เพาเวอร์ ทรานสมิชชั่น โซลูชั่น", time: "11:25", text: "ตกลงครับ ยอดสั่งซื้อระดับหมื่นเส้น ทางเรามอบส่วนลด Tier สูงสุดเหลือ 1,053.60 บาท/เส้น เครดิต 60 วัน และส่งฟรีทุกโรงงานครับ" }
                            ]
                        }
                    ],
                    reasoning: [
                        { step: 1, agent: "Spend Aggregator", time: "11:15:00", title: "รวบรวมใบขอซื้อสายพาน Gates 50 รายการ", thought: "รวมยอดสายพานส่งกำลังหลัก 14,015 เส้น เพื่อเปลี่ยนจาก Spot Buy เป็นสัญญารายปี", toolCall: "aggregate_pr('GATES-8MGT') ➔ 14,015 pcs" }
                    ]
                },
                nok: {
                    title: "ซีลกันน้ำมันอุตสาหกรรม NOK Double Lip Oil Seal (NBR) - ยอดรวม 39,092 ชิ้น",
                    budgetStr: "฿180.00 / ชิ้น",
                    targetStr: "฿158.90 / ชิ้น (-12.3%)",
                    vendors: [
                        {
                            name: "บจก. อีสเทิร์น ซีล แอนด์ ปาร์ค (V-9012)",
                            price: "฿158.90",
                            credit: "60 วัน",
                            leadTime: "ส่งมอบภายใน 2 วัน",
                            warranty: "12 เดือน (NOK แท้)",
                            cert: "NOK Japan Direct ✓",
                            status: "ชนะการประมูล (พร้อมรวมยอด PR)",
                            statusBadge: "badge-success text-white font-bold",
                            outcome: "ผู้ชนะการประมูล | เซฟงบประมาณ ฿870,789 (-12.3%)",
                            ladder: [
                                { round: "Ask", title: "ราคาตั้งต้น Spot Buy", price: "฿180.00", tag: "Spot Price", color: "border-slate-300 text-slate-500", note: "สั่งซื้อย่อย 50 ครั้ง" },
                                { round: "Agreed", title: "ราคาสัญญารวมยอด 39,092 ชิ้น", price: "฿158.90", tag: "Won Deal ✓", color: "border-emerald-500 bg-emerald-50 text-emerald-900 font-bold", note: "ลดลง 12.3% + เครดิต 60 วัน" }
                            ],
                            messages: [
                                { sender: "agent", name: "AI จัดซื้ออัตโนมัติ (Autonomous Agent)", time: "10:15", text: "ทางเราต้องการสั่งซื้อ Oil Seal NOK TC-45-68-12-NBR ยอดรวมทั้งปี 39,092 ชิ้น ขอราคาขายส่งระดับโรงงานที่ 158.90 บาท/ชิ้น พร้อมเครดิตเทอม 60 วันครับ", tactic: "[High-Volume Tier Unlocking]" },
                                { sender: "vendor", name: "อีสเทิร์น ซีล แอนด์ ปาร์ค", time: "10:18", text: "อนุมัติราคา 158.90 บาท/ชิ้น เครดิต 60 วันครับ ยินดีจัดส่งตามรอบ Kanban ของแต่ละโรงงานครับ" }
                            ]
                        }
                    ],
                    reasoning: [
                        { step: 1, agent: "Spend Aggregator", time: "10:12:00", title: "รวบรวม PR ซีลกันน้ำมัน NOK 39,092 ชิ้น", thought: "ปิดดีลที่ราคา ฿158.90/ชิ้น ประหยัดงบรวม ฿870,789 พร้อมเครดิต 60 วัน", toolCall: "aggregate_pr('NOK-TC-45-68-12') ➔ 39,092 pcs ✓" }
                    ]
                },
                rexroth: {
                    title: "ไฮดรอลิกไดเรกชันนอลวาล์ว Bosch Rexroth 4/3 Way (24VDC) - ยอดรวม 1,786 ตัว",
                    budgetStr: "฿6,500.00 / ตัว",
                    targetStr: "฿5,670.00 / ตัว (-13.3%)",
                    vendors: [
                        {
                            name: "บจก. แหลมฉบัง ไฮดรอลิกส์ เซอร์วิส (V-4520)",
                            price: "฿5,670.00",
                            credit: "90 วัน (ขยายสูงสุด)",
                            leadTime: "พร้อมส่งทันที (Safety Stock)",
                            warranty: "24 เดือน (เพิ่มจาก 12 เดือน)",
                            cert: "Bosch Rexroth OEM ✓",
                            status: "ชนะการประมูล (ออกใบ PO สำเร็จ)",
                            statusBadge: "badge-success text-white font-bold",
                            outcome: "ผู้ชนะการประมูล | เซฟงบประมาณ ฿1,557,537 (-13.3%)",
                            ladder: [
                                { round: "Ask", title: "ราคาตั้งต้น OEM", price: "฿6,500.00", tag: "OEM Quote", color: "border-slate-300 text-slate-500", note: "เครดิต 30 วัน" },
                                { round: "Agreed", title: "ตกลงสัญญา Corporate LTA 1,786 ตัว", price: "฿5,670.00", tag: "Won Deal ✓", color: "border-emerald-500 bg-emerald-50 text-emerald-900 font-bold", note: "เครดิต 90 วัน + ประกัน 24 เดือน" }
                            ],
                            messages: [
                                { sender: "agent", name: "AI จัดซื้ออัตโนมัติ (Autonomous Agent)", time: "09:40", text: "สำหรับวาล์วไฮดรอลิก Bosch Rexroth 4WE6D6X ยอดรวม 1,786 ตัว (50 PR) ทางเราขอทำสัญญา Corporate LTA ที่ราคา 5,670.00 บาท/ตัว ขยายเครดิตเป็น 90 วัน และขอขยายเวลารับประกันเป็น 24 เดือนครับ", tactic: "[SLA & Warranty Lock + 90-Day Credit Extension]" },
                                { sender: "vendor", name: "แหลมฉบัง ไฮดรอลิกส์ เซอร์วิส", time: "09:45", text: "ตกลงตามเงื่อนไขครับ ทางเราอนุมัติราคา 5,670.00 บาท/ตัว เครดิต 90 วัน พร้อมรับประกัน 24 เดือนและสำรองอะไหล่ฉุกเฉินให้ตลอดอายุสัญญาครับ" }
                            ]
                        }
                    ],
                    reasoning: [
                        { step: 1, agent: "SAP Dispatcher", time: "Completed", title: "ออกใบสั่งซื้อ PO#450098220 ใน SAP S/4HANA", thought: "เจรจาอะไหล่ไฮดรอลิกมูลค่าสูงสำเร็จ ลดต้นทุนรวม ฿1,557,537 พร้อมขยายเครดิตเทอมเป็น 90 วัน", toolCall: "BAPI_PO_CREATE1('450098220') ➔ CONFIRMED ✓" }
                    ]
                }
            }
        };

        
        // RAW 2,500 TRANSACTIONS DATASET EMBEDDED
        let DATASET_2500 = window.DATASET_2500_DATA || [];
        let datasetCurrentPage = 1;
        const datasetPageSize = 25;
        let datasetFiltered = DATASET_2500;

