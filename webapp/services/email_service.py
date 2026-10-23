"""
AWS SES Email Service for supplier Magic Link invitations.
Design goal: Professional Enterprise RFQ Invitation with rich deal context.
"""
import logging
import os
import boto3

logger = logging.getLogger(__name__)


def _is_enabled() -> bool:
    return os.environ.get("SES_ENABLED", "false").lower() in ("1", "true", "yes")


def _sender() -> str:
    return os.environ.get("SES_SENDER_EMAIL", "procurement-agent@autoprocure.nttdata.co.th")


def _region() -> str:
    return os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION", "us-east-1")


def _build_html(vendor_name: str, deal_id: str, portal_url: str, deal_data: dict = None) -> str:
    deal = deal_data or {}
    part_code = deal.get("part_code") or f"{deal_id.upper()}-STD"
    item_name = deal.get("name") or f"อะไหล่ระบบส่งกำลัง MRO ({deal_id.upper()})"
    total_qty = deal.get("total_quantity", 1200)
    total_prs = deal.get("total_prs", 16)
    budget_unit = deal.get("budget_unit_price", 450.0)
    target_unit = deal.get("target_unit_price", 398.0)
    target_credit = deal.get("target_credit_days", 45)
    
    return f"""<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>หนังสือเชิญเข้าร่วมเจรจาเงื่อนไขสัญญาจัดซื้อ MRO ประจำปี 2026</title>
</head>
<body style="margin:0;padding:24px;background-color:#f1f5f9;font-family:'Segoe UI',-apple-system,BlinkMacSystemFont,Roboto,Helvetica,Arial,sans-serif;color:#1e293b;line-height:1.6">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:640px;margin:auto;background:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 10px 25px -5px rgba(0,0,0,0.05),0 8px 10px -6px rgba(0,0,0,0.01);border:1px solid #e2e8f0">
    
    <!-- HEADER -->
    <tr>
      <td style="background:linear-gradient(135deg,#1e3a8a 0%,#2563eb 100%);padding:28px 32px;color:#ffffff">
        <table width="100%" cellspacing="0" cellpadding="0">
          <tr>
            <td>
              <span style="font-size:11px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;background:rgba(255,255,255,0.15);padding:4px 10px;border-radius:20px;display:inline-block;margin-bottom:8px">
                AUTOPROCURE.AI · NTT DATA ENTERPRISE
              </span>
              <h1 style="margin:0;font-size:20px;font-weight:700;line-height:1.3;color:#ffffff">
                หนังสือเชิญเจรจาข้อตกลงสัญญาจัดซื้อระยะยาว (Blanket Order)
              </h1>
              <p style="margin:6px 0 0 0;font-size:13px;color:#bfdbfe">
                โครงการจัดซื้ออะไหล่ซ่อมบำรุง MRO ประจำปีงบประมาณ 2026 (รวบยอดข้ามโรงงาน)
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>

    <!-- CONTENT BODY -->
    <tr>
      <td style="padding:32px">
        <p style="font-size:15px;margin-top:0">
          เรียน ผู้จัดการฝ่ายขาย / ทีมงานบริหารงานขาย <strong>{vendor_name}</strong>,
        </p>
        <p style="font-size:14px;color:#334155;margin-bottom:20px">
          ฝ่ายจัดซื้อกลางกลุ่มโรงงานอุตสาหกรรมในเครือ (เขตนิคมอุตสาหกรรมชลบุรี, อยุธยา และระยอง) ขอแจ้งให้ทราบว่า 
          บริษัทของท่านได้รับการคัดเลือกในฐานะ <strong>คู่ค้าในบัญชีผู้ค้าที่ได้รับอนุญาต (Approved Vendor List - AVL)</strong> 
          เพื่อเข้าร่วมการเจรจาเงื่อนไขสัญญาจัดซื้อกรอบระยะยาว (Blanket Purchase Agreement) ผ่านระบบ <strong>AutoProcure.AI Autonomous Sourcing Engine</strong>
        </p>

        <!-- DEAL SPECIFICATION CARD -->
        <table width="100%" cellspacing="0" cellpadding="0" style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:12px;margin:20px 0;overflow:hidden">
          <tr>
            <td colspan="2" style="background:#f1f5f9;padding:10px 16px;border-bottom:1px solid #e2e8f0;font-weight:700;font-size:12px;color:#0f172a;text-transform:uppercase;letter-spacing:0.05em">
              📋 ข้อมูลสรุปรายการจัดซื้อ (Deal Summary: {deal_id.upper()})
            </td>
          </tr>
          <tr>
            <td style="padding:10px 16px;font-size:13px;color:#64748b;width:38%;border-bottom:1px solid #f1f5f9">รหัสสินค้า / สเปก:</td>
            <td style="padding:10px 16px;font-size:13px;font-weight:700;color:#0f172a;border-bottom:1px solid #f1f5f9">{part_code} ({item_name})</td>
          </tr>
          <tr>
            <td style="padding:10px 16px;font-size:13px;color:#64748b;border-bottom:1px solid #f1f5f9">ปริมาณความต้องการรวม:</td>
            <td style="padding:10px 16px;font-size:13px;font-weight:700;color:#1e3a8a;border-bottom:1px solid #f1f5f9">{total_qty:,.0f} ชิ้น / ตัว (รวบยอดจาก {total_prs} ใบขอซื้อ PRs)</td>
          </tr>
          <tr>
            <td style="padding:10px 16px;font-size:13px;color:#64748b;border-bottom:1px solid #f1f5f9">รูปแบบสัญญาที่เสนอ:</td>
            <td style="padding:10px 16px;font-size:13px;font-weight:700;color:#059669;border-bottom:1px solid #f1f5f9">สัญญาซื้อขายรายปีการันตีวอลลุ่ม (Blanket Order 1 ปี) ทยอยส่งตามรอบ PM</td>
          </tr>
          <tr>
            <td style="padding:10px 16px;font-size:13px;color:#64748b">กรอบราคาเป้าหมาย & เครดิต:</td>
            <td style="padding:10px 16px;font-size:13px;color:#0f172a">เป้าหมาย <strong>฿{target_unit:,.2f}</strong> / หน่วย (จากเดิม ฿{budget_unit:,.2f}) | เครดิตเทอม <strong>{target_credit} วัน</strong></td>
          </tr>
        </table>

        <!-- HOW IT WORKS -->
        <div style="background:#eff6ff;border-left:4px solid #3b82f6;padding:14px 16px;border-radius:0 8px 8px 0;margin:24px 0">
          <div style="font-weight:700;font-size:13px;color:#1e40af;margin-bottom:4px">
            💡 ขั้นตอนการเข้าเจรจา (Digital Supplier Portal):
          </div>
          <p style="font-size:12px;color:#1e3a8a;margin:0;line-height:1.5">
            ท่านสามารถคลิกปุ่มด้านล่างเพื่อเข้าสู่ <strong>ห้องเจรจาออนไลน์เฉพาะบุคคล (Magic Link)</strong> 
            เพื่อยื่นข้อเสนอ ปรับลดราคา ขยายเครดิตเทอม หรือเพิ่มข้อเสนอพิเศษด้านบริการ (เช่น ส่งฟรี DDP / การันตีสต็อกสำรอง 7 วัน) 
            กับ Autonomous AI Agent ได้แบบสองทางตลอด 24 ชั่วโมง โดยไม่ต้องใช้รหัสผ่าน
          </p>
        </div>

        <!-- ACTION BUTTON -->
        <table width="100%" cellspacing="0" cellpadding="0" style="margin:28px 0 20px 0">
          <tr>
            <td align="center">
              <a href="{portal_url}" target="_blank"
                 style="background:#2563eb;color:#ffffff;text-decoration:none;font-size:15px;font-weight:700;padding:14px 36px;border-radius:12px;display:inline-block;box-shadow:0 4px 6px -1px rgba(37,99,235,0.2),0 2px 4px -2px rgba(37,99,235,0.2)">
                🚀 เข้าสู่ห้องเจรจาต่อรอง (Supplier Portal)
              </a>
            </td>
          </tr>
        </table>

        <p style="font-size:11px;color:#64748b;text-align:center;word-break:break-all;margin-top:12px">
          ลิงก์ตรงสำหรับเปิดผ่านเบราว์เซอร์: <a href="{portal_url}" style="color:#2563eb">{portal_url}</a>
        </p>

        <hr style="border:none;border-top:1px solid #e2e8f0;margin:28px 0 20px 0">

        <!-- SIGNATURE -->
        <table width="100%" cellspacing="0" cellpadding="0">
          <tr>
            <td style="font-size:12px;color:#64748b">
              ขอแสดงความนับถือ,<br>
              <strong>ฝ่ายบริหารการจัดซื้อเชิงกลยุทธ์ (Strategic Procurement & Sourcing Center)</strong><br>
              ระบบจัดการและเจรจาจัดซื้ออัตโนมัติ AutoProcure.AI<br>
              ความร่วมมือพัฒนาโดย <strong>NTT DATA Thailand Innovation Challenge 2026</strong>
            </td>
          </tr>
        </table>

      </td>
    </tr>

    <!-- FOOTER -->
    <tr>
      <td style="background:#f8fafc;padding:16px 32px;border-top:1px solid #e2e8f0;font-size:11px;color:#94a3b8;text-align:center">
        อีเมลฉบับนี้ส่งออกโดยอัตโนมัติผ่าน Amazon Simple Email Service (AWS SES) ภายใต้มาตรฐาน ISO/IEC 27001 และ PDPA<br>
        กรุณาอย่าตอบกลับอีเมลนี้โดยตรง หากมีข้อสงสัยโปรดเข้าดำเนินการผ่าน Supplier Portal
      </td>
    </tr>

  </table>
</body>
</html>"""


def send_magic_link(to_email: str, vendor_name: str, deal_id: str, portal_url: str, deal_data: dict = None) -> dict:
    """
    Send a supplier invite with full commercial context.
    """
    part_code = (deal_data and deal_data.get("part_code")) or deal_id.upper()
    subject = f"[RFQ-2026-MRO] หนังสือเชิญเจรจาสัญญาซื้อขายระยะยาว {part_code} — {vendor_name}"

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
            "detail": "ส่งอีเมลหนังสือเชิญจริงผ่าน AWS SES สำเร็จ",
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
