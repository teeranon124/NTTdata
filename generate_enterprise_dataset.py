import json
import random
from datetime import datetime, timedelta

random.seed(42)

# Define 60 realistic industrial MRO materials
MATERIALS = [
    # --- เครื่องกล & ส่งกำลัง (Mechanical & Transmission - 22 items) ---
    {
        "id": "nsk", "code": "NSK-6208-2RS1", "name": "ตลับลูกปืน NSK Deep Groove Ball Bearing (6208-2RS1)",
        "cat": "mechanical", "cat_th": "เครื่องกล & ส่งกำลัง", "stage": 4, "stage_label": "รออนุมัติ PO",
        "stock_alert": "ชลบุรี เหลือ 12 (Min: 50)", "stock_type": "Low Stock",
        "unit": "ชิ้น", "pre_p": 450.0, "post_p": 398.0, "supplier": "บจก. สยาม พรีซิชั่น เทค (V-4019)",
        "target_prs": 185
    },
    {
        "id": "skf", "code": "SKF-6310-2Z-C3", "name": "ตลับลูกปืน SKF Deep Groove Ball Bearing (6310-2Z/C3)",
        "cat": "mechanical", "cat_th": "เครื่องกล & ส่งกำลัง", "stage": 4, "stage_label": "รออนุมัติ PO",
        "stock_alert": "อยุธยา เหลือ 8 (Min: 30)", "stock_type": "Safety Stock",
        "unit": "ชิ้น", "pre_p": 1250.0, "post_p": 1090.0, "supplier": "บจก. แบริ่ง แอนด์ เพาเวอร์ ทรานสมิชชั่น (V-1082)",
        "target_prs": 120
    },
    {
        "id": "ntn_ucp", "code": "NTN-UCP205D1", "name": "ชุดตลับลูกปืนตุ๊กตา NTN Pillow Block (UCP205D1 เพลา 25mm)",
        "cat": "mechanical", "cat_th": "เครื่องกล & ส่งกำลัง", "stage": 2, "stage_label": "รวมยอด PR",
        "stock_alert": "ระยอง เหลือ 4 (Min: 20)", "stock_type": "ROP Alert",
        "unit": "ชุด", "pre_p": 680.0, "post_p": 595.0, "supplier": "บจก. สยาม แบริ่ง ซัพพลาย (V-3104)",
        "target_prs": 85
    },
    {
        "id": "koyo_taper", "code": "KOYO-32210JR", "name": "ตลับลูกปืนเตเปอร์ KOYO Tapered Roller Bearing (32210JR)",
        "cat": "mechanical", "cat_th": "เครื่องกล & ส่งกำลัง", "stage": 3, "stage_label": "ประมูล 3 เจ้า",
        "stock_alert": "ฉะเชิงเทรา Line 2-3", "stock_type": "PM Schedule",
        "unit": "ชิ้น", "pre_p": 1420.0, "post_p": 1245.0, "supplier": "บจก. เคพี อินดัสเทรียล พาร์ท (V-2819)",
        "target_prs": 64
    },
    {
        "id": "thk", "code": "THK-SSR20XW1UU", "name": "บล็อกสไลด์ลิเนียร์ไกด์ THK LM Guide (SSR20 Caged Ball)",
        "cat": "mechanical", "cat_th": "เครื่องกล & ส่งกำลัง", "stage": 3, "stage_label": "ประมูล 4 เจ้า",
        "stock_alert": "แผนซ่อมบำรุงประจำไตรมาส", "stock_type": "PM Schedule",
        "unit": "ตัว", "pre_p": 2150.0, "post_p": 1895.0, "supplier": "บจก. สยาม ลิเนียร์ โมชั่น (V-2291)",
        "target_prs": 96
    },
    {
        "id": "iko_bushing", "code": "IKO-LBE25AJ", "name": "บูชลูกปืนแนวเส้นตรง IKO Linear Bushing (LBE25AJ)",
        "cat": "mechanical", "cat_th": "เครื่องกล & ส่งกำลัง", "stage": 1, "stage_label": "ตรวจสต็อกต่ำ",
        "stock_alert": "คลังกลาง เหลือ 5", "stock_type": "Low Stock",
        "unit": "ตัว", "pre_p": 890.0, "post_p": 780.0, "supplier": "บจก. ไทย พรีซิชั่น แมชชีนเนอรี่ (V-4412)",
        "target_prs": 45
    },
    {
        "id": "gates", "code": "GATES-8MGT-1120-20", "name": "สายพานไทม์มิ่งแรงบิดสูง Gates PowerGrip GT3 (8MGT)",
        "cat": "mechanical", "cat_th": "เครื่องกล & ส่งกำลัง", "stage": 3, "stage_label": "ประมูล 3 เจ้า",
        "stock_alert": "ชลบุรี & ระยอง", "stock_type": "Low Stock",
        "unit": "เส้น", "pre_p": 780.0, "post_p": 688.5, "supplier": "บจก. ไทย เบลท์ติ้ง แอนด์ ไดรฟ์ (V-6140)",
        "target_prs": 140
    },
    {
        "id": "mitsuboshi_vbelt", "code": "MITSU-V-B68", "name": "สายพานร่องวี Mitsuboshi Classical V-Belt (B-68)",
        "cat": "mechanical", "cat_th": "เครื่องกล & ส่งกำลัง", "stage": 4, "stage_label": "รออนุมัติ PO",
        "stock_alert": "อยุธยา เหลือ 15", "stock_type": "Safety Stock",
        "unit": "เส้น", "pre_p": 290.0, "post_p": 252.0, "supplier": "บจก. อีสเทิร์น พาวเวอร์ เบลท์ (V-1980)",
        "target_prs": 110
    },
    {
        "id": "bando_ribbed", "code": "BANDO-6PK1210", "name": "สายพานร่องฟันอุตสาหกรรม Bando Ribbed Belt (6PK1210)",
        "cat": "mechanical", "cat_th": "เครื่องกล & ส่งกำลัง", "stage": 2, "stage_label": "เทียบสัญญาเดิม",
        "stock_alert": "ระยอง Line Motor 4", "stock_type": "Low Stock",
        "unit": "เส้น", "pre_p": 480.0, "post_p": 418.0, "supplier": "บจก. ไทย เบลท์ติ้ง แอนด์ ไดรฟ์ (V-6140)",
        "target_prs": 72
    },
    {
        "id": "tsubaki_chain", "code": "TSUBAKI-RS60-1", "name": "โซ่ส่งกำลังอุตสาหกรรม Tsubaki Roller Chain (RS60-1-RP-U)",
        "cat": "mechanical", "cat_th": "เครื่องกล & ส่งกำลัง", "stage": 3, "stage_label": "ต่อรองรอบ 2",
        "stock_alert": "สมุทรปราการ เหลือ 2 กล่อง", "stock_type": "ROP Alert",
        "unit": "กล่อง", "pre_p": 3200.0, "post_p": 2810.0, "supplier": "บจก. สยาม โซ่และระบบขับเคลื่อน (V-5510)",
        "target_prs": 52
    },
    {
        "id": "did_chain", "code": "DID-50-100L", "name": "โซ่ขับส่งกำลัง DID Heavy Duty Chain (DID50-100L)",
        "cat": "mechanical", "cat_th": "เครื่องกล & ส่งกำลัง", "stage": 1, "stage_label": "ตรวจสต็อกต่ำ",
        "stock_alert": "ชลบุรี Line Conveyor", "stock_type": "Low Stock",
        "unit": "กล่อง", "pre_p": 2450.0, "post_p": 2150.0, "supplier": "บจก. สยาม โซ่และระบบขับเคลื่อน (V-5510)",
        "target_prs": 38
    },
    {
        "id": "nbk_coupling", "code": "NBK-MJC-40-EWH", "name": "ข้อต่อเพลายาง NBK Flexible Jaw Coupling (MJC-40-EWH)",
        "cat": "mechanical", "cat_th": "เครื่องกล & ส่งกำลัง", "stage": 2, "stage_label": "รวมยอด PR",
        "stock_alert": "อยุธยา เหลือ 6", "stock_type": "Safety Stock",
        "unit": "ตัว", "pre_p": 1650.0, "post_p": 1450.0, "supplier": "บจก. แอดวานซ์ คัปปลิ้ง ซิสเต็ม (V-7120)",
        "target_prs": 48
    },
    {
        "id": "lovejoy_coupling", "code": "LOVEJOY-L095", "name": "สไปเดอร์ข้อต่อเพลา Lovejoy Spider Insert (L-095 NBR)",
        "cat": "mechanical", "cat_th": "เครื่องกล & ส่งกำลัง", "stage": 4, "stage_label": "ออก PO สำเร็จ",
        "stock_alert": "ระยอง บันทึกใน SAP สำเร็จ", "stock_type": "PO Issued",
        "unit": "ชิ้น", "pre_p": 320.0, "post_p": 275.0, "supplier": "บจก. แอดวานซ์ คัปปลิ้ง ซิสเต็ม (V-7120)",
        "target_prs": 65
    },
    {
        "id": "khk_gear", "code": "KHK-SS2-30", "name": "เฟืองตรงเหล็กกล้า KHK Spur Gear Module 2.0 (SS2-30)",
        "cat": "mechanical", "cat_th": "เครื่องกล & ส่งกำลัง", "stage": 1, "stage_label": "ตรวจสต็อกต่ำ",
        "stock_alert": "ฉะเชิงเทรา เหลือ 3", "stock_type": "Low Stock",
        "unit": "ชิ้น", "pre_p": 1150.0, "post_p": 1010.0, "supplier": "บจก. สยาม เกียร์ แอนด์ แมนูแฟคเจอริ่ง (V-8321)",
        "target_prs": 30
    },
    {
        "id": "misumi_shaft", "code": "MISUMI-PSFHR25-500", "name": "เพลาชุบแข็งเจียระไน Misumi Precision Shaft (Dia 25mm L500)",
        "cat": "mechanical", "cat_th": "เครื่องกล & ส่งกำลัง", "stage": 3, "stage_label": "เจรจาต่อรอง",
        "stock_alert": "อยุธยา & ชลบุรี", "stock_type": "PM Schedule",
        "unit": "ท่อน", "pre_p": 980.0, "post_p": 860.0, "supplier": "บจก. มิซูมิ (ประเทศไทย) (V-9901)",
        "target_prs": 42
    },
    {
        "id": "thk_ballscrew", "code": "THK-BNK1520-3G0", "name": "บอลสกรูความแม่นยำสูง THK Precision Ball Screw (BNK1520)",
        "cat": "mechanical", "cat_th": "เครื่องกล & ส่งกำลัง", "stage": 2, "stage_label": "เทียบสัญญาเดิม",
        "stock_alert": "ระยอง CNC Line", "stock_type": "Safety Stock",
        "unit": "ชุด", "pre_p": 8900.0, "post_p": 7850.0, "supplier": "บจก. สยาม ลิเนียร์ โมชั่น (V-2291)",
        "target_prs": 24
    },
    {
        "id": "asahi_uc208", "code": "ASAHI-UC208", "name": "ลูกปืนเม็ดตลับพร้อมปลอก Asahi Bearing Insert (UC208)",
        "cat": "mechanical", "cat_th": "เครื่องกล & ส่งกำลัง", "stage": 4, "stage_label": "รออนุมัติ PO",
        "stock_alert": "ชลบุรี เหลือ 10", "stock_type": "Low Stock",
        "unit": "ตลับ", "pre_p": 850.0, "post_p": 745.0, "supplier": "บจก. แบริ่ง แอนด์ เพาเวอร์ ทรานสมิชชั่น (V-1082)",
        "target_prs": 55
    },
    {
        "id": "ina_needle", "code": "INA-HK2516", "name": "ตลับลูกปืนเม็ดเข็ม Schaeffler INA Needle Bearing (HK2516)",
        "cat": "mechanical", "cat_th": "เครื่องกล & ส่งกำลัง", "stage": 1, "stage_label": "ตรวจสต็อกต่ำ",
        "stock_alert": "อยุธยา เหลือ 8", "stock_type": "ROP Alert",
        "unit": "ตลับ", "pre_p": 420.0, "post_p": 368.0, "supplier": "บจก. สยาม พรีซิชั่น เทค (V-4019)",
        "target_prs": 40
    },
    {
        "id": "martin_sprocket", "code": "MARTIN-60B18", "name": "สปร็อกเก็ตโซ่ Martin Sprocket Type B (60B18 ฟัน 18)",
        "cat": "mechanical", "cat_th": "เครื่องกล & ส่งกำลัง", "stage": 3, "stage_label": "ประมูล 3 เจ้า",
        "stock_alert": "ฉะเชิงเทรา Line 1", "stock_type": "PM Schedule",
        "unit": "ชิ้น", "pre_p": 1280.0, "post_p": 1120.0, "supplier": "บจก. สยาม โซ่และระบบขับเคลื่อน (V-5510)",
        "target_prs": 35
    },
    {
        "id": "misumi_cam", "code": "MISUMI-CF16-UU", "name": "แคมฟอลโลเวอร์ลูกปืนล้อ Misumi Cam Follower (CF16-UU)",
        "cat": "mechanical", "cat_th": "เครื่องกล & ส่งกำลัง", "stage": 2, "stage_label": "รวมยอด PR",
        "stock_alert": "สมุทรปราการ เหลือ 12", "stock_type": "Low Stock",
        "unit": "ตัว", "pre_p": 720.0, "post_p": 630.0, "supplier": "บจก. มิซูมิ (ประเทศไทย) (V-9901)",
        "target_prs": 45
    },
    {
        "id": "habasit_belt", "code": "HABASIT-F5ENR", "name": "สายพานลำเลียงผ้าใบเรียบ Habasit Flat Conveyor Belt (F-5ENR)",
        "cat": "mechanical", "cat_th": "เครื่องกล & ส่งกำลัง", "stage": 4, "stage_label": "รออนุมัติ PO",
        "stock_alert": "ระยอง กว้าง 600mm", "stock_type": "Safety Stock",
        "unit": "ม้วน", "pre_p": 14500.0, "post_p": 12750.0, "supplier": "บจก. ไทย เบลท์ติ้ง แอนด์ ไดรฟ์ (V-6140)",
        "target_prs": 18
    },
    {
        "id": "chiorino_belt", "code": "CHIORINO-T0", "name": "สายพานส่งกำลังความเร็วสูง Chiorino Flat Drive Belt (T-0)",
        "cat": "mechanical", "cat_th": "เครื่องกล & ส่งกำลัง", "stage": 1, "stage_label": "ตรวจสต็อกต่ำ",
        "stock_alert": "ชลบุรี คลังตัดต่อ", "stock_type": "Low Stock",
        "unit": "เส้น", "pre_p": 2100.0, "post_p": 1850.0, "supplier": "บจก. อีสเทิร์น พาวเวอร์ เบลท์ (V-1980)",
        "target_prs": 28
    },

    # --- ไฟฟ้า & เซนเซอร์ (Electrical & Automation - 18 items) ---
    {
        "id": "omron", "code": "OMRON-E2E-X5ME1", "name": "อินดักทีฟพร็อกซิมิตี้เซนเซอร์ OMRON M18 (E2E Series)",
        "cat": "electrical", "cat_th": "ไฟฟ้า & เซนเซอร์", "stage": 4, "stage_label": "รออนุมัติ PO",
        "stock_alert": "ฉะเชิงเทรา Line 1-3", "stock_type": "Low Stock",
        "unit": "ตัว", "pre_p": 890.0, "post_p": 773.58, "supplier": "บจก. ออโตเมชั่น โซลูชั่น เซ็นเตอร์ (V-3310)",
        "target_prs": 150
    },
    {
        "id": "omron_photo", "code": "OMRON-E3Z-T61", "name": "โฟโตอิเล็กทริกเซนเซอร์ลำแสงส่งผ่าน OMRON Photo Sensor (E3Z-T61)",
        "cat": "electrical", "cat_th": "ไฟฟ้า & เซนเซอร์", "stage": 3, "stage_label": "ประมูล 3 เจ้า",
        "stock_alert": "อยุธยา เหลือ 4 (Min: 15)", "stock_type": "Safety Stock",
        "unit": "ชุด", "pre_p": 2450.0, "post_p": 2150.0, "supplier": "บจก. ออโตเมชั่น โซลูชั่น เซ็นเตอร์ (V-3310)",
        "target_prs": 65
    },
    {
        "id": "keyence_fiber", "code": "KEYENCE-FS-N41N", "name": "ไฟเบอร์ออปติกแอมพลิฟายเออร์ Keyence Digital Fiber (FS-N41N)",
        "cat": "electrical", "cat_th": "ไฟฟ้า & เซนเซอร์", "stage": 2, "stage_label": "รวมยอด PR",
        "stock_alert": "ชลบุรี คลีนรูม Line 2", "stock_type": "Low Stock",
        "unit": "ตัว", "pre_p": 4600.0, "post_p": 4050.0, "supplier": "บจก. เซนเซอร์ เทคโนโลยี แอนด์ คอนโทรล (V-6205)",
        "target_prs": 35
    },
    {
        "id": "schneider", "code": "SCHNEIDER-LC1D25M7", "name": "แมกเนติกคอนแทคเตอร์ Schneider TeSys D (25A 3P 220VAC)",
        "cat": "electrical", "cat_th": "ไฟฟ้า & เซนเซอร์", "stage": 3, "stage_label": "ต่อรองรอบ 2",
        "stock_alert": "คลังไฟฟ้าแจ้งเตือน", "stock_type": "Safety Stock",
        "unit": "ตัว", "pre_p": 950.0, "post_p": 832.0, "supplier": "บจก. สยาม อิเล็คทริค คอนโทรล (V-7711)",
        "target_prs": 130
    },
    {
        "id": "mitsubishi", "code": "MITSUBISHI-FR-D720-0.75K", "name": "อินเวอร์เตอร์ขับมอเตอร์ Mitsubishi FR-D720 (0.75kW 3-Phase)",
        "cat": "electrical", "cat_th": "ไฟฟ้า & เซนเซอร์", "stage": 2, "stage_label": "เทียบสัญญาเดิม",
        "stock_alert": "คลังกลาง เหลือ 5", "stock_type": "ROP Alert",
        "unit": "เครื่อง", "pre_p": 4800.0, "post_p": 4198.5, "supplier": "บจก. ธนบุรี อิลเล็คทริค ซัพพลาย (V-5050)",
        "target_prs": 90
    },
    {
        "id": "mitsu_mccb", "code": "MITSUBISHI-NF63-CV-3P-50A", "name": "เบรกเกอร์โรงงาน Mitsubishi Molded Case Breaker (NF63-CV 3P 50A)",
        "cat": "electrical", "cat_th": "ไฟฟ้า & เซนเซอร์", "stage": 4, "stage_label": "รออนุมัติ PO",
        "stock_alert": "ระยอง ตู้ MDB หลัก", "stock_type": "Low Stock",
        "unit": "ตัว", "pre_p": 1680.0, "post_p": 1470.0, "supplier": "บจก. ธนบุรี อิลเล็คทริค ซัพพลาย (V-5050)",
        "target_prs": 55
    },
    {
        "id": "fuji_contactor", "code": "FUJI-SC-03", "name": "แมกเนติกคอนแทคเตอร์ Fuji Electric Magnetic Contactor (SC-03 220V)",
        "cat": "electrical", "cat_th": "ไฟฟ้า & เซนเซอร์", "stage": 1, "stage_label": "ตรวจสต็อกต่ำ",
        "stock_alert": "อยุธยา เหลือ 6", "stock_type": "ROP Alert",
        "unit": "ตัว", "pre_p": 620.0, "post_p": 545.0, "supplier": "บจก. ธนบุรี อิลเล็คทริค ซัพพลาย (V-5050)",
        "target_prs": 45
    },
    {
        "id": "panasonic_photo", "code": "PANASONIC-CX-421", "name": "เซนเซอร์ตรวจจับชิ้นงาน Panasonic Photoelectric Sensor (CX-421)",
        "cat": "electrical", "cat_th": "ไฟฟ้า & เซนเซอร์", "stage": 3, "stage_label": "เจรจาต่อรอง",
        "stock_alert": "ชลบุรี Packing Line", "stock_type": "Low Stock",
        "unit": "ตัว", "pre_p": 1480.0, "post_p": 1295.0, "supplier": "บจก. เซนเซอร์ เทคโนโลยี แอนด์ คอนโทรล (V-6205)",
        "target_prs": 40
    },
    {
        "id": "sick_laser", "code": "SICK-DX35", "name": "เซนเซอร์วัดระยะเลเซอร์ Sick Laser Distance Sensor (Dx35 Series)",
        "cat": "electrical", "cat_th": "ไฟฟ้า & เซนเซอร์", "stage": 2, "stage_label": "รวมยอด PR",
        "stock_alert": "ระยอง Warehouse Stacker", "stock_type": "Safety Stock",
        "unit": "ตัว", "pre_p": 9800.0, "post_p": 8620.0, "supplier": "บจก. เซนเซอร์ เทคโนโลยี แอนด์ คอนโทรล (V-6205)",
        "target_prs": 18
    },
    {
        "id": "autonics_temp", "code": "AUTONICS-TC4S-14R", "name": "เครื่องควบคุมอุณหภูมิดิจิตอล Autonics Temperature Controller (TC4S)",
        "cat": "electrical", "cat_th": "ไฟฟ้า & เซนเซอร์", "stage": 4, "stage_label": "ออก PO สำเร็จ",
        "stock_alert": "อยุธยา บันทึกใน SAP สำเร็จ", "stock_type": "PO Issued",
        "unit": "เครื่อง", "pre_p": 1350.0, "post_p": 1180.0, "supplier": "บจก. ออโตเมชั่น โซลูชั่น เซ็นเตอร์ (V-3310)",
        "target_prs": 38
    },
    {
        "id": "omron_ssr", "code": "OMRON-G3NA-210B", "name": "โซลิดสเตตรีเลย์ Omron Solid State Relay (G3NA-210B 24VDC/240VAC)",
        "cat": "electrical", "cat_th": "ไฟฟ้า & เซนเซอร์", "stage": 1, "stage_label": "ตรวจสต็อกต่ำ",
        "stock_alert": "ฉะเชิงเทรา เตาอบ Line 1", "stock_type": "Low Stock",
        "unit": "ตัว", "pre_p": 850.0, "post_p": 745.0, "supplier": "บจก. ออโตเมชั่น โซลูชั่น เซ็นเตอร์ (V-3310)",
        "target_prs": 32
    },
    {
        "id": "idec_estop", "code": "IDEC-HW1B-V4R", "name": "สวิตช์ปุ่มกดหยุดฉุกเฉิน IDEC Emergency Stop 22mm (HW1B-V4R)",
        "cat": "electrical", "cat_th": "ไฟฟ้า & เซนเซอร์", "stage": 4, "stage_label": "รออนุมัติ PO",
        "stock_alert": "ทุกโรงงาน ตามมาตรฐานความปลอดภัย", "stock_type": "Safety Stock",
        "unit": "ตัว", "pre_p": 490.0, "post_p": 425.0, "supplier": "บจก. สยาม อิเล็คทริค คอนโทรล (V-7711)",
        "target_prs": 75
    },
    {
        "id": "weidmuller_term", "code": "WEIDMULLER-WDU2.5", "name": "เทอร์มินอลบล็อกต่อสาย Weidmuller DIN-Rail Terminal (WDU 2.5)",
        "cat": "electrical", "cat_th": "ไฟฟ้า & เซนเซอร์", "stage": 2, "stage_label": "รวมยอด PR",
        "stock_alert": "ชลบุรี & อยุธยา", "stock_type": "Low Stock",
        "unit": "กล่อง", "pre_p": 650.0, "post_p": 560.0, "supplier": "บจก. สยาม อิเล็คทริค คอนโทรล (V-7711)",
        "target_prs": 60
    },
    {
        "id": "meanwell_psu", "code": "MEANWELL-NDR-120-24", "name": "สวิตชิ่งพาวเวอร์ซัพพลาย Mean Well DIN Rail 24VDC 5A (NDR-120-24)",
        "cat": "electrical", "cat_th": "ไฟฟ้า & เซนเซอร์", "stage": 3, "stage_label": "ต่อรองรอบ 2",
        "stock_alert": "ระยอง ตู้คอนโทรล Line 3", "stock_type": "Low Stock",
        "unit": "ตัว", "pre_p": 1250.0, "post_p": 1090.0, "supplier": "บจก. ธนบุรี อิลเล็คทริค ซัพพลาย (V-5050)",
        "target_prs": 44
    },
    {
        "id": "abb_mcb", "code": "ABB-S203-C16", "name": "มินิเอเจอร์เซอร์กิตเบรกเกอร์ ABB MCB 3-Pole 16A (S203-C16)",
        "cat": "electrical", "cat_th": "ไฟฟ้า & เซนเซอร์", "stage": 1, "stage_label": "ตรวจสต็อกต่ำ",
        "stock_alert": "สมุทรปราการ เหลือ 5", "stock_type": "ROP Alert",
        "unit": "ตัว", "pre_p": 920.0, "post_p": 810.0, "supplier": "บจก. สยาม อิเล็คทริค คอนโทรล (V-7711)",
        "target_prs": 30
    },
    {
        "id": "siemens_soft", "code": "SIEMENS-3RW3016", "name": "ซอฟต์สตาร์ทเตอร์มอเตอร์ Siemens Sirius Soft Starter (3RW3016 7.5kW)",
        "cat": "electrical", "cat_th": "ไฟฟ้า & เซนเซอร์", "stage": 2, "stage_label": "เทียบสัญญาเดิม",
        "stock_alert": "ฉะเชิงเทรา ปั๊มน้ำหล่อเย็น", "stock_type": "Safety Stock",
        "unit": "เครื่อง", "pre_p": 7200.0, "post_p": 6350.0, "supplier": "บจก. ธนบุรี อิลเล็คทริค ซัพพลาย (V-5050)",
        "target_prs": 16
    },
    {
        "id": "mitsu_plc_io", "code": "MITSUBISHI-QX40", "name": "โมดูลดิจิตอลอินพุต PLC Mitsubishi MELSEC-Q (QX40 16-Point 24VDC)",
        "cat": "electrical", "cat_th": "ไฟฟ้า & เซนเซอร์", "stage": 4, "stage_label": "รออนุมัติ PO",
        "stock_alert": "อยุธยา สำรองตู้เครื่องจักรหลัก", "stock_type": "Safety Stock",
        "unit": "ตัว", "pre_p": 3800.0, "post_p": 3320.0, "supplier": "บจก. ออโตเมชั่น โซลูชั่น เซ็นเตอร์ (V-3310)",
        "target_prs": 25
    },
    {
        "id": "omron_safety", "code": "OMRON-G9SE-201", "name": "เซฟตี้รีเลย์ควบคุมความปลอดภัย Omron Safety Relay Unit (G9SE-201)",
        "cat": "electrical", "cat_th": "ไฟฟ้า & เซนเซอร์", "stage": 3, "stage_label": "ประมูล 3 เจ้า",
        "stock_alert": "ชลบุรี Safety Gate Interlock", "stock_type": "Low Stock",
        "unit": "ตัว", "pre_p": 3100.0, "post_p": 2720.0, "supplier": "บจก. ออโตเมชั่น โซลูชั่น เซ็นเตอร์ (V-3310)",
        "target_prs": 22
    },

    # --- นิวเมติกส์ & ไฮดรอลิกส์ (Pneumatics & Hydraulics - 12 items) ---
    {
        "id": "smc", "code": "SMC-SY5120-5LZD-01", "name": "โซลินอยด์วาล์วนิวเมติกส์ SMC 5/2 Way (24VDC ฐานยึด Sub-base)",
        "cat": "pneumatic", "cat_th": "นิวเมติกส์ & ไฮดรอลิกส์", "stage": 1, "stage_label": "ตรวจสต็อกต่ำ",
        "stock_alert": "ระยอง เหลือ 3 (ROP: 10)", "stock_type": "ROP Alert",
        "unit": "ชิ้น", "pre_p": 1250.0, "post_p": 1089.33, "supplier": "บจก. โกลบอล เอ็มอาร์โอ ซอร์สซิ่ง (V-8802)",
        "target_prs": 125
    },
    {
        "id": "smc_frl", "code": "SMC-AC30-03DG", "name": "ชุดกรองลมดักน้ำปรับแรงดัน SMC FRL Unit (AC30-03DG 3/8 นิ้ว)",
        "cat": "pneumatic", "cat_th": "นิวเมติกส์ & ไฮดรอลิกส์", "stage": 4, "stage_label": "รออนุมัติ PO",
        "stock_alert": "อยุธยา ลมสะอาดเครื่องจักร", "stock_type": "Low Stock",
        "unit": "ชุด", "pre_p": 2850.0, "post_p": 2490.0, "supplier": "บจก. บางกอก นิวเมติกส์ เซ็นเตอร์ (V-3912)",
        "target_prs": 65
    },
    {
        "id": "rexroth", "code": "REXROTH-4WE6D6X-EG24N9K4", "name": "ไฮดรอลิกไดเรกชันนอลวาล์ว Bosch Rexroth 4/3 Way (24VDC)",
        "cat": "pneumatic", "cat_th": "นิวเมติกส์ & ไฮดรอลิกส์", "stage": 4, "stage_label": "ออก PO สำเร็จ",
        "stock_alert": "บันทึกใน SAP สำเร็จ (PO#450098220)", "stock_type": "PO Issued",
        "unit": "ตัว", "pre_p": 6500.0, "post_p": 5670.0, "supplier": "บจก. แหลมฉบัง ไฮดรอลิกส์ เซอร์วิส (V-4520)",
        "target_prs": 55
    },
    {
        "id": "festo_cylinder", "code": "FESTO-DNC-40-100", "name": "กระบอกลมนิวเมติกส์มาตรฐาน Festo ISO Cylinder (DNC-40-100-PPV-A)",
        "cat": "pneumatic", "cat_th": "นิวเมติกส์ & ไฮดรอลิกส์", "stage": 3, "stage_label": "ต่อรองรอบ 2",
        "stock_alert": "ชลบุรี Line Stamping", "stock_type": "Safety Stock",
        "unit": "ตัว", "pre_p": 4200.0, "post_p": 3690.0, "supplier": "บจก. บางกอก นิวเมติกส์ เซ็นเตอร์ (V-3912)",
        "target_prs": 45
    },
    {
        "id": "smc_compact_cyl", "code": "SMC-CDQ2B50-30DZ", "name": "กระบอกลมคอมแพ็คแบบบาง SMC Compact Cylinder (CDQ2B50-30DZ)",
        "cat": "pneumatic", "cat_th": "นิวเมติกส์ & ไฮดรอลิกส์", "stage": 2, "stage_label": "รวมยอด PR",
        "stock_alert": "ฉะเชิงเทรา เหลือ 5", "stock_type": "Low Stock",
        "unit": "ตัว", "pre_p": 2100.0, "post_p": 1840.0, "supplier": "บจก. โกลบอล เอ็มอาร์โอ ซอร์สซิ่ง (V-8802)",
        "target_prs": 50
    },
    {
        "id": "parker_pump", "code": "PARKER-PGP511", "name": "ปั๊มไฮดรอลิกแรงดันสูง Parker Hydraulic Gear Pump (PGP511 Series)",
        "cat": "pneumatic", "cat_th": "นิวเมติกส์ & ไฮดรอลิกส์", "stage": 3, "stage_label": "เจรจาต่อรอง",
        "stock_alert": "ระยอง เครื่องเพรส 200 ตัน", "stock_type": "PM Schedule",
        "unit": "ตัว", "pre_p": 16500.0, "post_p": 14500.0, "supplier": "บจก. แหลมฉบัง ไฮดรอลิกส์ เซอร์วิส (V-4520)",
        "target_prs": 14
    },
    {
        "id": "ckd_valve", "code": "CKD-3PA110-06", "name": "โซลินอยด์วาล์ว 3 ทาง CKD Direct Acting Valve (3PA110-06 24VDC)",
        "cat": "pneumatic", "cat_th": "นิวเมติกส์ & ไฮดรอลิกส์", "stage": 1, "stage_label": "ตรวจสต็อกต่ำ",
        "stock_alert": "สมุทรปราการ เหลือ 4", "stock_type": "ROP Alert",
        "unit": "ตัว", "pre_p": 1100.0, "post_p": 965.0, "supplier": "บจก. โกลบอล เอ็มอาร์โอ ซอร์สซิ่ง (V-8802)",
        "target_prs": 35
    },
    {
        "id": "smc_speed_ctrl", "code": "SMC-AS2201F-02-08S", "name": "วาล์วควบคุมความเร็วกระบอกลม SMC Speed Controller (AS2201F)",
        "cat": "pneumatic", "cat_th": "นิวเมติกส์ & ไฮดรอลิกส์", "stage": 4, "stage_label": "รออนุมัติ PO",
        "stock_alert": "ทุกโรงงาน อะไหล่ใช้ประจำ", "stock_type": "Safety Stock",
        "unit": "ตัว", "pre_p": 280.0, "post_p": 242.0, "supplier": "บจก. บางกอก นิวเมติกส์ เซ็นเตอร์ (V-3912)",
        "target_prs": 95
    },
    {
        "id": "pisco_fitting", "code": "PISCO-POC8-02", "name": "ข้อต่อลมสวมเร็ว Pisco Push-In Tube Fitting (POC8-02 เกลียว 1/4)",
        "cat": "pneumatic", "cat_th": "นิวเมติกส์ & ไฮดรอลิกส์", "stage": 2, "stage_label": "รวมยอด PR",
        "stock_alert": "อยุธยา & ชลบุรี", "stock_type": "Low Stock",
        "unit": "ถุง (10ตัว)", "pre_p": 450.0, "post_p": 388.0, "supplier": "บจก. บางกอก นิวเมติกส์ เซ็นเตอร์ (V-3912)",
        "target_prs": 80
    },
    {
        "id": "koganei_qev", "code": "KOGANEI-QEV2-02", "name": "วาล์วระบายลมด่วน Koganei Quick Exhaust Valve (QEV2-02)",
        "cat": "pneumatic", "cat_th": "นิวเมติกส์ & ไฮดรอลิกส์", "stage": 1, "stage_label": "ตรวจสต็อกต่ำ",
        "stock_alert": "ระยอง Line Ejector", "stock_type": "Low Stock",
        "unit": "ตัว", "pre_p": 820.0, "post_p": 718.0, "supplier": "บจก. โกลบอล เอ็มอาร์โอ ซอร์สซิ่ง (V-8802)",
        "target_prs": 32
    },
    {
        "id": "smc_pu_tubing", "code": "SMC-TU0805B-100", "name": "สายลมโพลียูรีเทน SMC Polyurethane Air Tubing (8mm x 5mm ยาว 100m)",
        "cat": "pneumatic", "cat_th": "นิวเมติกส์ & ไฮดรอลิกส์", "stage": 3, "stage_label": "ประมูล 3 เจ้า",
        "stock_alert": "ฉะเชิงเทรา & อยุธยา", "stock_type": "Safety Stock",
        "unit": "ม้วน", "pre_p": 2200.0, "post_p": 1920.0, "supplier": "บจก. บางกอก นิวเมติกส์ เซ็นเตอร์ (V-3912)",
        "target_prs": 45
    },
    {
        "id": "vickers_relief", "code": "VICKERS-CG-06", "name": "วาล์วจำกัดแรงดันไฮดรอลิก Vickers Hydraulic Relief Valve (CG-06)",
        "cat": "pneumatic", "cat_th": "นิวเมติกส์ & ไฮดรอลิกส์", "stage": 2, "stage_label": "เทียบสัญญาเดิม",
        "stock_alert": "ระยอง ระบบไฮดรอลิกกลาง", "stock_type": "PM Schedule",
        "unit": "ตัว", "pre_p": 9400.0, "post_p": 8250.0, "supplier": "บจก. แหลมฉบัง ไฮดรอลิกส์ เซอร์วิส (V-4520)",
        "target_prs": 15
    },

    # --- ซีลและเคมีภัณฑ์ซ่อมบำรุง (Seals & Maintenance Chemicals - 8 items) ---
    {
        "id": "nok", "code": "NOK-TC-45-68-12-NBR", "name": "ซีลกันน้ำมันอุตสาหกรรม NOK Double Lip Oil Seal (NBR 45x68x12)",
        "cat": "mechanical", "cat_th": "เครื่องกล & ส่งกำลัง", "stage": 2, "stage_label": "รวมยอด PR",
        "stock_alert": "สมุทรปราการ & อยุธยา", "stock_type": "Safety Stock",
        "unit": "ชิ้น", "pre_p": 180.0, "post_p": 158.0, "supplier": "บจก. อีสเทิร์น ซีล แอนด์ ปาร์ค (V-9012)",
        "target_prs": 210
    },
    {
        "id": "skf_seal", "code": "SKF-HMSA10-RG-50", "name": "ซีลเพลาหมุนทนความร้อน SKF Radial Shaft Seal (50x72x8 NBR/FKM)",
        "cat": "mechanical", "cat_th": "เครื่องกล & ส่งกำลัง", "stage": 4, "stage_label": "รออนุมัติ PO",
        "stock_alert": "ชลบุรี มอเตอร์ปั๊มน้ำเคมี", "stock_type": "Low Stock",
        "unit": "ชิ้น", "pre_p": 380.0, "post_p": 330.0, "supplier": "บจก. แบริ่ง แอนด์ เพาเวอร์ ทรานสมิชชั่น (V-1082)",
        "target_prs": 85
    },
    {
        "id": "trelleborg_oring", "code": "TRELLEBORG-VITON-KIT", "name": "ชุดโอริงทนสารเคมีและอุณหภูมิสูง Trelleborg Viton O-Ring Box Kit",
        "cat": "mechanical", "cat_th": "เครื่องกล & ส่งกำลัง", "stage": 3, "stage_label": "ต่อรองรอบ 2",
        "stock_alert": "ระยอง โรงกลั่น & ปิโตรเคมี", "stock_type": "Safety Stock",
        "unit": "กล่อง", "pre_p": 3850.0, "post_p": 3380.0, "supplier": "บจก. อีสเทิร์น ซีล แอนด์ ปาร์ค (V-9012)",
        "target_prs": 35
    },
    {
        "id": "klinger_gasket", "code": "KLINGER-C4400-2MM", "name": "แผ่นปะเก็นไร้ใยหินทนแรงดัน Klinger Non-Asbestos Gasket Sheet (C-4400)",
        "cat": "mechanical", "cat_th": "เครื่องกล & ส่งกำลัง", "stage": 1, "stage_label": "ตรวจสต็อกต่ำ",
        "stock_alert": "อยุธยา หน้าแปลนไอน้ำ", "stock_type": "ROP Alert",
        "unit": "แผ่น", "pre_p": 2900.0, "post_p": 2550.0, "supplier": "บจก. อีสเทิร์น ซีล แอนด์ ปาร์ค (V-9012)",
        "target_prs": 24
    },
    {
        "id": "grundfos_mech_seal", "code": "GRUNDFOS-HQQE-12", "name": "แมคคานิคอลซีลปั๊มน้ำ Grundfos Mechanical Seal Kit (HQQE 12mm)",
        "cat": "mechanical", "cat_th": "เครื่องกล & ส่งกำลัง", "stage": 2, "stage_label": "เทียบสัญญาเดิม",
        "stock_alert": "ฉะเชิงเทรา ปั๊มน้ำ Cooling Tower", "stock_type": "PM Schedule",
        "unit": "ชุด", "pre_p": 4500.0, "post_p": 3950.0, "supplier": "บจก. แหลมฉบัง ไฮดรอลิกส์ เซอร์วิส (V-4520)",
        "target_prs": 20
    },
    {
        "id": "loctite_243", "code": "LOCTITE-243-50ML", "name": "น้ำยาล็อคเกลียวแรงปานกลาง Loctite 243 Threadlocker (ขวด 50ml)",
        "cat": "mechanical", "cat_th": "เครื่องกล & ส่งกำลัง", "stage": 4, "stage_label": "รออนุมัติ PO",
        "stock_alert": "ทุกโรงงาน แผนกซ่อมบำรุง", "stock_type": "Low Stock",
        "unit": "ขวด", "pre_p": 620.0, "post_p": 535.0, "supplier": "บจก. เคมีคอล แอนด์ ซัพพลาย (V-6601)",
        "target_prs": 90
    },
    {
        "id": "mobil_gear_oil", "code": "MOBIL-SHC630-20L", "name": "น้ำมันเกียร์และแบริ่งสังเคราะห์แท้ Mobil SHC 630 Synthetic Oil (20L)",
        "cat": "mechanical", "cat_th": "เครื่องกล & ส่งกำลัง", "stage": 3, "stage_label": "ประมูล 3 เจ้า",
        "stock_alert": "ระยอง & อยุธยา รอบเปลี่ยนถ่ายน้ำมัน", "stock_type": "PM Schedule",
        "unit": "ถัง", "pre_p": 6800.0, "post_p": 5980.0, "supplier": "บจก. เคมีคอล แอนด์ ซัพพลาย (V-6601)",
        "target_prs": 45
    },
    {
        "id": "shinetsu_silicone", "code": "SHINETSU-KE45T", "name": "กาวซิลิโคนซีลปะเก็นอุตสาหกรรม Shin-Etsu Industrial Sealant (KE-45T)",
        "cat": "mechanical", "cat_th": "เครื่องกล & ส่งกำลัง", "stage": 1, "stage_label": "ตรวจสต็อกต่ำ",
        "stock_alert": "ชลบุรี คลังเคมี เหลือ 8 หลอด", "stock_type": "Low Stock",
        "unit": "หลอด", "pre_p": 340.0, "post_p": 295.0, "supplier": "บจก. เคมีคอล แอนด์ ซัพพลาย (V-6601)",
        "target_prs": 40
    }
]

print(f"Total materials: {len(MATERIALS)}")

# Adjust target_prs so total sum is exactly 2,500
current_sum = sum(m["target_prs"] for m in MATERIALS)
diff = 2500 - current_sum
print(f"Initial PR sum: {current_sum}, Diff to 2,500: {diff}")

idx = 0
while diff != 0:
    step = 1 if diff > 0 else -1
    MATERIALS[idx % len(MATERIALS)]["target_prs"] += step
    diff -= step
    idx += 1

while sum(m["target_prs"] for m in MATERIALS) > 2500:
    for m in MATERIALS:
        if m["target_prs"] > 10 and sum(x["target_prs"] for x in MATERIALS) > 2500:
            m["target_prs"] -= 1

while sum(m["target_prs"] for m in MATERIALS) < 2500:
    MATERIALS[0]["target_prs"] += 1

print(f"Verified sum of PRs: {sum(m['target_prs'] for m in MATERIALS)}")

# Plants and lines
PLANTS = [
    {"code": "PLANT-AYU-01", "name": "อยุธยา Hi-Tech (PLANT-AYU-01)", "lines": ["Line 1 Machining", "Line 2 Assembly", "Preventive Maint. Team A", "Utility & Facilities"]},
    {"code": "PLANT-CBI-02", "name": "อมตะซิตี้ ชลบุรี (PLANT-CBI-02)", "lines": ["Line Stamping & Press", "Line 3 Motor Assembly", "Maintenance Workshop B", "Facilities & Water Treatment"]},
    {"code": "PLANT-RYG-03", "name": "อีสเทิร์นซีบอร์ด ระยอง (PLANT-RYG-03)", "lines": ["Line Heavy Press 200T", "Line 4 Robotic Welding", "Utility & Central Boiler", "Die & Mold Shop"]},
    {"code": "PLANT-CCO-04", "name": "เกตเวย์ซิตี้ ฉะเชิงเทรา (PLANT-CCO-04)", "lines": ["Line Surface Mount (SMT)", "Line 2 Oven & Furnace", "Tooling & Fixture Shop"]},
    {"code": "PLANT-SPK-05", "name": "บางปู สมุทรปราการ (PLANT-SPK-05)", "lines": ["Line Packaging & Palletizer", "Main Warehouse & Stacker", "Electrical Substation"]}
]

# Generate the 2,500 realistic PR records
all_prs = []
tx_counter = 1
start_date = datetime(2025, 1, 6)

for m in MATERIALS:
    prs_for_this = m["target_prs"]
    base_post_p = m["post_p"]
    base_pre_p = m["pre_p"]
    
    # We want natural realistic variation in spot price per PR (spot price varies +/- 6% across vendors before AI)
    # And natural dates spread through 2025
    # And realistic quantities (not static 59!)
    
    # Target total quantity for this material
    avg_qty = 15 if base_post_p > 3000 else (45 if base_post_p > 1000 else 120)
    
    for i in range(prs_for_this):
        tx_id = f"TX-MRO-{tx_counter:04d}"
        pr_num = f"PR-2025-{random.randint(10000, 99999)}"
        
        # Natural date distribution between Jan 2025 and Oct 2025
        day_offset = random.randint(0, 280)
        pr_date = start_date + timedelta(days=day_offset)
        date_str = pr_date.strftime("%Y-%m-%d")
        
        plant = random.choice(PLANTS)
        dept_line = random.choice(plant["lines"])
        plant_str = f"{plant['name']} - {dept_line}"
        
        # Realistic quantity: log-normal or varied realistic integer
        if avg_qty <= 20:
            qty = random.choice([2, 4, 6, 8, 10, 12, 15, 20])
        elif avg_qty <= 50:
            qty = random.choice([10, 15, 20, 25, 30, 40, 50, 60])
        else:
            qty = random.choice([25, 50, 75, 100, 120, 150, 200, 250])
            
        # Spot price before AI had maverick price variance (+/- 3% to +8% markup)
        spot_markup = random.uniform(0.98, 1.08)
        actual_pre_p = round(base_pre_p * spot_markup, 2)
        actual_post_p = round(base_post_p, 2) # unified negotiated price
        
        pre_tot = round(actual_pre_p * qty, 2)
        post_tot = round(actual_post_p * qty, 2)
        tco_sav = round(pre_tot - post_tot, 2)
        if tco_sav < 0:
            tco_sav = round(pre_tot * 0.10, 2)
            actual_post_p = round((pre_tot - tco_sav) / qty, 2)
            post_tot = round(actual_post_p * qty, 2)
            
        tco_pct = round((tco_sav / pre_tot) * 100, 2)
        vol_sav = round(tco_sav * 0.70, 2)
        batna_sav = round(tco_sav * 0.30, 2)
        
        all_prs.append({
            "id": tx_id,
            "deal": f"DEAL-2026-{m['id'].upper()}",
            "deal_key": m["id"],
            "pr": pr_num,
            "date": date_str,
            "plant": plant_str,
            "plant_code": plant["code"],
            "code": m["code"],
            "name": m["name"],
            "cat": m["cat_th"],
            "cat_key": m["cat"],
            "qty": qty,
            "unit": m["unit"],
            "mode": "Consolidated_PR",
            "sup_pre": "ร้านค้าตัวแทนย่อยในนิคม (Spot Buy)",
            "pre_p": actual_pre_p,
            "pre_tot": pre_tot,
            "cred_pre": 30,
            "sup_post": m["supplier"],
            "post_p": actual_post_p,
            "post_tot": post_tot,
            "cred_post": 45 if m["stage"] >= 3 else 30,
            "vol_sav": vol_sav,
            "batna_sav": batna_sav,
            "cred_sav": 50.0,
            "tco_sav": tco_sav,
            "tco_pct": tco_pct,
            "rounds": 4 if m["stage"] == 4 else (3 if m["stage"] == 3 else 2),
            "aws": 2.28
        })
        tx_counter += 1

# Exact 2,500 PRs
all_prs = all_prs[:2500]
print(f"Total all_prs generated: {len(all_prs)}")

# Sort all PRs by date descending
all_prs.sort(key=lambda x: x["date"], reverse=True)

# Update each material with calculated aggregated numbers from the generated PRs!
for m in MATERIALS:
    m_prs = [p for p in all_prs if p["deal_key"] == m["id"]]
    m["total_qty"] = sum(p["qty"] for p in m_prs)
    m["total_pre_spend"] = round(sum(p["pre_tot"] for p in m_prs), 2)
    m["total_post_spend"] = round(sum(p["post_tot"] for p in m_prs), 2)
    m["total_savings"] = round(sum(p["tco_sav"] for p in m_prs), 2)
    m["savings_pct"] = round((m["total_savings"] / m["total_pre_spend"]) * 100, 1) if m["total_pre_spend"] > 0 else 12.0
    m["actual_pr_count"] = len(m_prs)

print("Sample Material Summary:")
for m in MATERIALS[:5]:
    print(f"- {m['code']} ({m['name'][:30]}): {m['actual_pr_count']} PRs, {m['total_qty']} {m['unit']}, Savings ฿{m['total_savings']:,.2f} ({m['savings_pct']}%)")

# Write dataset_2500.json
with open('dataset_2500.json', 'w', encoding='utf-8') as f:
    json.dump(all_prs, f, ensure_ascii=False, indent=2)

with open('webapp/web/static/dataset_2500.json', 'w', encoding='utf-8') as f:
    json.dump(all_prs, f, ensure_ascii=False, indent=2)

# Write dataset_2500.js
js_content = f"window.DATASET_2500_DATA = {json.dumps(all_prs, ensure_ascii=False)};\n"
with open('dataset_2500.js', 'w', encoding='utf-8') as f:
    f.write(js_content)

with open('webapp/web/static/dataset_2500.js', 'w', encoding='utf-8') as f:
    f.write(js_content)

# Write master_deals.json
master_deals = {}
for m in MATERIALS:
    master_deals[m["id"]] = {
        "id": m["id"],
        "deal_code": f"DEAL-2026-{m['id'].upper()}",
        "sku": m["code"],
        "name": m["name"],
        "category": m["cat"],
        "category_th": m["cat_th"],
        "stage": m["stage"],
        "stage_label": m["stage_label"],
        "stock_alert": m["stock_alert"],
        "stock_type": m["stock_type"],
        "unit": m["unit"],
        "qty": m["total_qty"],
        "prs_count": m["actual_pr_count"],
        "pre_price": m["pre_p"],
        "post_price": m["post_p"],
        "pre_spend": m["total_pre_spend"],
        "post_spend": m["total_post_spend"],
        "savings": m["total_savings"],
        "savings_pct": m["savings_pct"],
        "supplier": m["supplier"],
        "vendors": [
            {
                "id": f"v1_{m['id']}",
                "name": m["supplier"],
                "price": f"฿{m['post_p']:,.2f}",
                "credit": "45 วัน" if m["stage"] >= 3 else "30 วัน",
                "leadTime": "7 วันทำการ",
                "warranty": "1 ปี",
                "status": "ชนะการประมูล (ออกใบ PO)" if m["stage"] == 4 else ("กำลังเจรจารอบ 2" if m["stage"] == 3 else "รอเปรียบเทียบสัญญา"),
                "statusBadge": "badge-success text-white font-bold" if m["stage"] == 4 else "badge-info text-white",
                "outcome": f"ผู้ชนะ TCO Rank #1 | ประหยัด ฿{m['total_savings']:,.2f} (-{m['savings_pct']}%)",
                "messages": [
                    {
                        "sender": "vendor",
                        "name": f"{m['supplier'].replace('บจก. ', '')} (ฝ่ายขาย)",
                        "time": "10:30",
                        "text": f"เรียนฝ่ายจัดซื้อ ตามคำขอเสนอราคา (RFQ) สำหรับ {m['name']} ยอดรวม {m['total_qty']} {m['unit']} ทางเราขอเสนอราคา ฿{m['pre_p']:,.2f}/{m['unit']} เครดิต 30 วันครับ"
                    },
                    {
                        "sender": "agent",
                        "name": "AI จัดซื้ออัตโนมัติ (Autonomous Agent)",
                        "time": "10:32",
                        "text": f"ขอบคุณครับ จากการรวมใบขอซื้อ {m['actual_pr_count']} PRs ข้ามโรงงาน ทำให้เรามี Volume รวม {m['total_qty']} {m['unit']} ทางระบบขอต่อรองราคาเป้าหมายที่ ฿{m['post_p']:,.2f} พร้อมสัญญารายปี LTA ครับ",
                        "tactic": "[Spend Pooling: รวมยอดข้ามโรงงานเพื่อปลดล็อก Volume Tier]"
                    },
                    {
                        "sender": "vendor",
                        "name": f"{m['supplier'].replace('บจก. ', '')} (ฝ่ายขาย)",
                        "time": "10:38",
                        "text": f"หากผูกสัญญารายปีตามยอดดังกล่าว ทางเรายินดีอนุมัติราคาพิเศษที่ ฿{m['post_p']:,.2f}/{m['unit']} เครดิต 45 วันครับ ขอบคุณครับ"
                    }
                ]
            }
        ]
    }

with open('webapp/data/master_deals.json', 'w', encoding='utf-8') as f:
    json.dump(master_deals, f, ensure_ascii=False, indent=2)

with open('materials_catalog_60.json', 'w', encoding='utf-8') as f:
    json.dump(MATERIALS, f, ensure_ascii=False, indent=2)

print("Generated all files successfully!")
