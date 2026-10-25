"""
AWS SES Email Service for supplier Magic Link invitations.
Design goal: Sharp, Direct, Tactical RFP (No Early Concessions, No Price Leakage).
"""
import logging
import os
import boto3

logger = logging.getLogger(__name__)


def _is_enabled() -> bool:
    return os.environ.get("SES_ENABLED", "true").lower() in ("1", "true", "yes")


def _sender() -> str:
    return os.environ.get("SES_SENDER_EMAIL", "teeranonn124@gmail.com")


def _region() -> str:
    return os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION", "us-east-1")


def _build_html(vendor_name: str, deal_id: str, portal_url: str, deal_data: dict = None) -> str:
    deal = deal_data or {}
    part_code = deal.get("part_code") or f"{deal_id.upper()}-STD"
    item_name = deal.get("name") or f"อะไหล่อุตสาหกรรม ({deal_id.upper()})"
    total_qty = deal.get("total_quantity", 1200)
    total_prs = deal.get("total_prs", 16)
    
    return f"""<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="utf-8">
  <title>หนังสือเชิญยื่นข้อเสนอราคา — {part_code}</title>
</head>
<body style="margin:0;padding:20px;background:#f8fafc;font-family:'Segoe UI',-apple-system,sans-serif;color:#0f172a;line-height:1.6">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:580px;margin:auto;background:#fff;border-radius:12px;border:1px solid #e2e8f0;overflow:hidden">
    
    <tr>
      <td style="background:#0f172a;padding:20px 28px;border-bottom:3px solid #2563eb;color:#fff">
        <div style="font-size:11px;font-weight:700;color:#94a3b8;letter-spacing:.08em;text-transform:uppercase">ฝ่ายจัดซื้อและบริหารซัพพลายเชน</div>
        <div style="font-size:17px;font-weight:700;margin-top:2px">หนังสือเชิญยื่นข้อเสนอราคา (Request for Quotation)</div>
      </td>
    </tr>

    <tr>
      <td style="padding:28px">
        <p style="margin-top:0;font-size:14px">
          เรียน ผู้จัดการฝ่ายขาย <strong>{vendor_name}</strong>,
        </p>
        
        <p style="font-size:13px;color:#334155">
          ฝ่ายจัดซื้อขอเชิญบริษัทของท่านในฐานะคู่ค้าที่ผ่านการรับรอง (Approved Vendor) 
          เข้าร่วมยื่นข้อเสนอราคาและเงื่อนไขทางการค้า สำหรับรายการจัดซื้อต่อไปนี้:
        </p>

        <table width="100%" cellspacing="0" cellpadding="0" style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;margin:16px 0;font-size:13px">
          <tr>
            <td style="padding:10px 14px;color:#64748b;width:35%;border-bottom:1px solid #e2e8f0">รายการสินค้า:</td>
            <td style="padding:10px 14px;font-weight:700;color:#0f172a;border-bottom:1px solid #e2e8f0">{part_code} ({item_name})</td>
          </tr>
          <tr>
            <td style="padding:10px 14px;color:#64748b;border-bottom:1px solid #e2e8f0">ปริมาณความต้องการ:</td>
            <td style="padding:10px 14px;font-weight:700;color:#1d4ed8;border-bottom:1px solid #e2e8f0">{total_qty:,.0f} หน่วย (สัญญารายปี LTA ครอบคลุม 3 โรงงานหลัก)</td>
          </tr>
          <tr>
            <td style="padding:10px 14px;color:#64748b">รูปแบบการจัดซื้อ:</td>
            <td style="padding:10px 14px;color:#059669;font-weight:600">พิจารณาสัญญา Blanket Order 1 ปี หรือสั่งซื้อรายครั้ง ตามความคุ้มค่าของข้อเสนอ</td>
          </tr>
        </table>

        <p style="font-size:13px;color:#334155">
          ทางเราเปิดรับข้อเสนอทั้งในมิติด้านราคาขายส่ง, เครดิตเทอม, และเงื่อนไขการส่งมอบ (SLA) 
          โดยคู่ค้าที่เสนอเงื่อนไขได้เหมาะสมที่สุดจะได้รับการพิจารณาเป็นคู่สัญญาหลัก 
          ท่านสามารถคลิกเข้าสู่ห้องเจรจาออนไลน์เพื่อยื่นและปรับข้อเสนอได้ทันที:
        </p>

        <div style="text-align:center;margin:24px 0">
          <a href="{portal_url}" target="_blank"
             style="background:#2563eb;color:#fff;text-decoration:none;font-size:14px;font-weight:700;padding:12px 28px;border-radius:8px;display:inline-block">
            เข้าสู่ห้องเจรจาข้อเสนอ (Supplier Portal) →
          </a>
        </div>

        <p style="font-size:11px;color:#64748b;text-align:center;word-break:break-all">
          ลิงก์ตรง: <a href="{portal_url}" style="color:#2563eb">{portal_url}</a>
        </p>

        <hr style="border:none;border-top:1px solid #e2e8f0;margin:20px 0">

        <p style="font-size:12px;color:#64748b;margin-bottom:0">
          ขอแสดงความนับถือ,<br>
          <strong>ฝ่ายบริหารการจัดซื้อเชิงกลยุทธ์</strong><br>
          ระบบจัดซื้ออัตโนมัติ J-RAJA
        </p>
      </td>
    </tr>

    <tr>
      <td style="background:#f1f5f9;padding:10px 24px;font-size:10px;color:#94a3b8;text-align:center">
        เอกสารความลับทางการค้าเฉพาะบุคคล (Strictly Confidential)
      </td>
    </tr>

  </table>
</body>
</html>"""


def send_magic_link(to_email: str, vendor_name: str, deal_id: str, portal_url: str, deal_data: dict = None) -> dict:
    deal = deal_data or {}
    part_code = deal.get("part_code") or deal_id.upper()
    subject = f"[RFQ-2026] ขอเชิญยื่นข้อเสนอราคาอะไหล่ {part_code} — {vendor_name}"

    if not _is_enabled():
        logger.info("SES disabled — simulated invite to %s (%s) %s", to_email, vendor_name, portal_url)
        return {
            "status": "simulated",
            "detail": "SES_ENABLED=false — จำลองการส่งอีเมล (ไม่ได้เรียก AWS จริง)",
            "to": to_email,
            "portal_url": portal_url,
        }

    try:
        client = boto3.client("ses", region_name=_region())
        resp = client.send_email(
            Source=_sender(),
            Destination={"ToAddresses": [to_email]},
            Message={
                "Subject": {"Data": subject, "Charset": "UTF-8"},
                "Body": {"Html": {"Data": _build_html(vendor_name, deal_id, portal_url, deal_data), "Charset": "UTF-8"}},
            },
        )
        message_id = resp.get("MessageId")
        logger.info("SES live invite sent to %s (MessageId=%s)", to_email, message_id)
        return {
            "status": "live_ses",
            "detail": "ส่งหนังสือเชิญจริงผ่าน AWS SES สำเร็จ",
            "to": to_email,
            "message_id": message_id,
            "portal_url": portal_url,
        }
    except Exception as e:
        logger.warning("SES send failed: %s (fallback to simulated response)", e)
        return {
            "status": "simulated",
            "detail": f"AWS SES Error: {str(e)}",
            "to": to_email,
            "portal_url": portal_url,
        }


def send_po_award_email(to_email: str, vendor_name: str, deal_id: str, po_number: str, approved_by: str, deal_data: dict = None) -> dict:
    """
    Send official Contract Award & SAP PO Confirmation email to the winning vendor via AWS SES.
    """
    deal = deal_data or {}
    part_code = deal.get("part_code") or deal.get("sku") or deal_id.upper()
    deal_title = deal.get("name") or part_code
    qty = deal.get("qty") or deal.get("total_quantity") or 850
    unit = deal.get("unit") or "ตัว"
    agreed_price = deal.get("agreed_price") or deal.get("post_price") or 0.0
    total_spend = agreed_price * qty if agreed_price else (deal.get("post_spend") or 0.0)
    
    subject = f"[SAP PO Confirmed] ใบสั่งซื้อเลขที่ {po_number} ได้รับการอนุมัติลงนามสมบูรณ์ — {part_code} ({vendor_name})"
    
    html = f"""<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="utf-8">
  <title>แจ้งยืนยันการอนุมัติสัญญา Blanket Order และออกใบสั่งซื้อ (PO)</title>
</head>
<body style="margin:0;padding:20px;background:#f8fafc;font-family:'Segoe UI',-apple-system,sans-serif;color:#0f172a;line-height:1.6">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:600px;margin:auto;background:#fff;border-radius:12px;border:1px solid #e2e8f0;overflow:hidden;box-shadow:0 4px 12px rgba(0,0,0,0.05)">
    <tr>
      <td style="background:#064e3b;padding:24px 28px;border-bottom:3px solid #10b981;color:#fff">
        <div style="font-size:11px;font-weight:700;color:#6ee7b7;letter-spacing:.08em;text-transform:uppercase">NTT DATA Thailand Enterprise Sourcing Hub</div>
        <div style="font-size:18px;font-weight:700;margin-top:3px">หนังสือแจ้งยืนยันการอนุมัติสัญญา &amp; ออกใบสั่งซื้อ (PO Confirmation)</div>
      </td>
    </tr>

    <tr>
      <td style="padding:28px">
        <div style="background:#ecfdf5;border:1px solid #a7f3d0;border-radius:8px;padding:12px 16px;margin-bottom:20px;color:#065f46;font-size:13px;font-weight:600">
          ✓ ได้รับการลงนามอนุมัติสมบูรณ์โดย {approved_by} เรียบร้อยแล้ว
        </div>

        <p style="margin-top:0;font-size:14px">
          เรียน ผู้จัดการฝ่ายขายและการตลาด <strong>{vendor_name}</strong>,
        </p>
        
        <p style="font-size:13px;color:#334155">
          ทางฝ่ายบริหารการจัดซื้อเชิงกลยุทธ์ ขอแจ้งให้ทราบอย่างเป็นทางการว่า บริษัทของท่านได้รับการคัดเลือกเป็น 
          <strong>คู่สัญญาหลัก (Awarded Supplier)</strong> ภายใต้สัญญา Blanket Order 1 ปีเต็ม สำหรับรายการจัดซื้อต่อไปนี้:
        </p>

        <table width="100%" cellspacing="0" cellpadding="0" style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;margin:18px 0;font-size:13px">
          <tr>
            <td style="padding:10px 14px;color:#64748b;width:38%;border-bottom:1px solid #e2e8f0">เลขที่ใบสั่งซื้อ (SAP PO):</td>
            <td style="padding:10px 14px;font-weight:700;color:#047857;border-bottom:1px solid #e2e8f0;font-family:monospace;font-size:14px">{po_number}</td>
          </tr>
          <tr>
            <td style="padding:10px 14px;color:#64748b;border-bottom:1px solid #e2e8f0">รายการชิ้นส่วน:</td>
            <td style="padding:10px 14px;font-weight:700;color:#0f172a;border-bottom:1px solid #e2e8f0">{part_code} ({deal_title})</td>
          </tr>
          <tr>
            <td style="padding:10px 14px;color:#64748b;border-bottom:1px solid #e2e8f0">ปริมาณตามสัญญา:</td>
            <td style="padding:10px 14px;font-weight:700;color:#1d4ed8;border-bottom:1px solid #e2e8f0">{qty:,} {unit} (สัญญา 1 ปี ครอบคลุมทุกโรงงาน)</td>
          </tr>
          <tr>
            <td style="padding:10px 14px;color:#64748b;border-bottom:1px solid #e2e8f0">ราคาต่อหน่วยที่ตกลง:</td>
            <td style="padding:10px 14px;font-weight:700;color:#0f172a;border-bottom:1px solid #e2e8f0">฿{agreed_price:,.2f} / {unit}</td>
          </tr>
          <tr>
            <td style="padding:10px 14px;color:#64748b;border-bottom:1px solid #e2e8f0">มูลค่าสัญญารวม:</td>
            <td style="padding:10px 14px;font-weight:700;color:#047857;border-bottom:1px solid #e2e8f0">฿{total_spend:,.2f}</td>
          </tr>
          <tr>
            <td style="padding:10px 14px;color:#64748b">สถานะการส่งมอบ:</td>
            <td style="padding:10px 14px;color:#059669;font-weight:600">ลงนามสมบูรณ์ ➔ พร้อมออกเอกสาร Purchase Order ฉบับเต็ม</td>
          </tr>
        </table>

        <p style="font-size:13px;color:#334155">
          ทางฝ่ายจัดซื้อขอขอบพระคุณ <strong>{vendor_name}</strong> ที่ร่วมมือเป็นพันธมิตรทางธุรกิจ และเจ้าหน้าที่จัดซื้อจะติดต่อประสานงานเรื่องการวางบิลและการจัดส่งงวดแรกตามแผนงานต่อไป
        </p>

        <hr style="border:none;border-top:1px solid #e2e8f0;margin:22px 0">

        <p style="font-size:12px;color:#64748b;margin-bottom:0">
          ขอแสดงความนับถือ,<br>
          <strong>{approved_by}</strong><br>
          ฝ่ายบริหารการจัดซื้อเชิงกลยุทธ์ (Strategic Procurement Department)<br>
          ระบบจัดซื้ออัตโนมัติ J-RAJA
        </p>
      </td>
    </tr>

    <tr>
      <td style="background:#f1f5f9;padding:12px 24px;font-size:10px;color:#94a3b8;text-align:center">
        เอกสารยืนยันสัญญานี้สร้างโดยระบบ J-RAJA และเชื่อมตรงเข้าสู่ SAP S/4HANA (BAPI_PO_CREATE1)
      </td>
    </tr>
  </table>
</body>
</html>"""

    if not _is_enabled():
        logger.info("SES disabled — simulated PO email to %s (%s)", to_email, po_number)
        return {"status": "simulated", "to": to_email, "po_number": po_number}

    try:
        client = boto3.client("ses", region_name=_region())
        resp = client.send_email(
            Source=_sender(),
            Destination={"ToAddresses": [to_email]},
            Message={
                "Subject": {"Data": subject, "Charset": "UTF-8"},
                "Body": {"Html": {"Data": html, "Charset": "UTF-8"}},
            },
        )
        msg_id = resp.get("MessageId")
        logger.info("SES live PO email sent to %s (MessageId=%s)", to_email, msg_id)
        return {"status": "live_ses", "message_id": msg_id, "to": to_email, "po_number": po_number}
    except Exception as e:
        logger.warning("SES send PO email failed: %s", e)
        return {"status": "error", "detail": str(e), "to": to_email}
