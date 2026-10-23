"""
AWS SES Email Service for supplier Magic Link invitations.
Design goal: Sophisticated, Natural Executive RFQ Invitation (Zero Price Leakage).
"""
import logging
import os
import boto3

logger = logging.getLogger(__name__)


def _is_enabled() -> bool:
    return os.environ.get("SES_ENABLED", "false").lower() in ("1", "true", "yes")


def _sender() -> str:
    return os.environ.get("SES_SENDER_EMAIL", "teeranonn124@gmail.com")


def _region() -> str:
    return os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION", "us-east-1")


def _build_html(vendor_name: str, deal_id: str, portal_url: str, deal_data: dict = None) -> str:
    deal = deal_data or {}
    part_code = deal.get("part_code") or f"{deal_id.upper()}-STD"
    item_name = deal.get("name") or f"อะไหล่อุตสาหกรรมมาตรฐาน MRO ({deal_id.upper()})"
    total_qty = deal.get("total_quantity", 1200)
    total_prs = deal.get("total_prs", 16)
    
    return f"""<!DOCTYPE html>
<html lang="th">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>เรียนเชิญยื่นข้อเสนอราคาและเงื่อนไขทางการค้า — โครงการจัดซื้อกรอบสัญญารายปี 2026</title>
</head>
<body style="margin:0;padding:24px;background-color:#f8fafc;font-family:'Segoe UI',-apple-system,BlinkMacSystemFont,Roboto,Helvetica,Arial,sans-serif;color:#1e293b;line-height:1.65">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:620px;margin:auto;background:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.06);border:1px solid #e2e8f0">
    
    <!-- HEADER -->
    <tr>
      <td style="background:#0f172a;padding:24px 32px;border-bottom:3px solid #2563eb">
        <table width="100%" cellspacing="0" cellpadding="0">
          <tr>
            <td>
              <div style="font-size:12px;font-weight:700;color:#94a3b8;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:4px">
                ฝ่ายบริหารการจัดซื้อและซัพพลายเชนกลาง
              </div>
              <div style="font-size:18px;font-weight:700;color:#ffffff;line-height:1.3">
                หนังสือเชิญยื่นข้อเสนอทางการค้า (Request for Proposal / Quotation)
              </div>
              <div style="font-size:12px;color:#38bdf8;margin-top:4px">
                โครงการจัดทำสัญญาซื้อขายระยะยาวรายปี (Annual Blanket Order 2026)
              </div>
            </td>
          </tr>
        </table>
      </td>
    </tr>

    <!-- CONTENT BODY -->
    <tr>
      <td style="padding:32px">
        <p style="font-size:15px;margin-top:0;color:#0f172a">
          เรียน ผู้จัดการฝ่ายขายและทีมงานดูแลบัญชีลูกค้ารายใหญ่ <strong>{vendor_name}</strong>
        </p>
        
        <p style="font-size:14px;color:#334155;text-align:justify">
          สืบเนื่องจากการทบทวนแผนจัดซื้ออะไหล่ซ่อมบำรุงและงานบำรุงรักษาเชิงป้องกัน (MRO) ประจำปีงบประมาณ 2026 สำหรับกลุ่มโรงงานอุตสาหกรรมในเครือของเรา 
          ฝ่ายจัดซื้อกลางได้รวบรวมปริมาณความต้องการใช้งานจริงเพื่อยกระดับเป็น <strong>สัญญาความร่วมมือทางการค้าระยะยาว 1 ปีเต็ม (Blanket Purchase Order)</strong> 
          เพื่อสร้างความมั่นคงในห่วงโซ่อุปทานร่วมกัน
        </p>

        <p style="font-size:14px;color:#334155;text-align:justify">
          ทางฝ่ายจัดซื้อมีความยินดีขอเรียนเชิญบริษัทของท่าน ในฐานะคู่ค้าที่ผ่านการรับรองมาตรฐาน (Approved Vendor) เข้าร่วมยื่นข้อเสนอราคาและเงื่อนไขทางการค้าพิเศษสำหรับรายการจัดซื้อสำคัญดังต่อไปนี้:
        </p>

        <!-- SPEC CARD (NO TARGET PRICE REVEALED!) -->
        <table width="100%" cellspacing="0" cellpadding="0" style="background:#f8fafc;border:1px solid #cbd5e1;border-radius:12px;margin:20px 0;overflow:hidden">
          <tr>
            <td colspan="2" style="background:#f1f5f9;padding:12px 18px;border-bottom:1px solid #cbd5e1;font-weight:700;font-size:13px;color:#0f172a">
              📦 รายละเอียดรายการจัดซื้อและปริมาณความต้องการ
            </td>
          </tr>
          <tr>
            <td style="padding:10px 18px;font-size:13px;color:#64748b;width:38%;border-bottom:1px solid #e2e8f0">รหัสและรายการสินค้า:</td>
            <td style="padding:10px 18px;font-size:13px;font-weight:700;color:#0f172a;border-bottom:1px solid #e2e8f0">{part_code} — {item_name}</td>
          </tr>
          <tr>
            <td style="padding:10px 18px;font-size:13px;color:#64748b;border-bottom:1px solid #e2e8f0">ปริมาณสั่งซื้อรวมทั้งปี:</td>
            <td style="padding:10px 18px;font-size:13px;font-weight:700;color:#1d4ed8;border-bottom:1px solid #e2e8f0">{total_qty:,.0f} หน่วย (รวบยอดความต้องการใช้งานจาก {total_prs} ใบขอซื้อ)</td>
          </tr>
          <tr>
            <td style="padding:10px 18px;font-size:13px;color:#64748b;border-bottom:1px solid #e2e8f0">จุดรับมอบสินค้า:</td>
            <td style="padding:10px 18px;font-size:13px;color:#334155;border-bottom:1px solid #e2e8f0">คลังพัสดุกลางโรงงานในเครือ (นิคมฯ ชลบุรี, อยุธยา และระยอง) ทยอยส่งตามรอบ</td>
          </tr>
          <tr>
            <td style="padding:10px 18px;font-size:13px;color:#64748b">กรอบความร่วมมือ:</td>
            <td style="padding:10px 18px;font-size:13px;color:#059669;font-weight:600">การันตีคำสั่งซื้อตลอดทั้งปี พร้อมโอกาสขยายสโคปรายการอะไหล่อื่นๆ เพิ่มเติม</td>
          </tr>
        </table>

        <!-- TACTICAL INVITATION -->
        <p style="font-size:14px;color:#334155;text-align:justify">
          เนื่องจากเป็นสัญญาการันตีปริมาณสั่งซื้อล็อตใหญ่ ฝ่ายจัดซื้อจึงเปิดโอกาสให้ท่านนำเสนอ <strong>โครงสร้างราคาขายส่งที่ดีที่สุด (Volume-discounted Pricing)</strong> 
          ตลอดจนเงื่อนไขการสนับสนุนทางธุรกิจ เช่น ระยะเวลาสินเชื่อทางการค้า (Credit Terms), ข้อตกลงระยะเวลาส่งมอบ (SLA Lead-time), และการสำรองสต็อกฉุกเฉิน
        </p>

        <p style="font-size:14px;color:#334155;text-align:justify">
          เพื่อความรวดเร็วและโปร่งใส ท่านสามารถเข้าสู่ระบบเจรจาทางการค้าดิจิทัล เพื่อร่วมพูดคุย ปรับแก้ข้อเสนอ และสรุปเงื่อนไขกับตัวแทนระบบจัดซื้ออัตโนมัติของเราได้โดยตรงผ่านลิงก์เฉพาะบุคคลด้านล่างนี้:
        </p>

        <!-- CTA BUTTON -->
        <table width="100%" cellspacing="0" cellpadding="0" style="margin:28px 0 20px 0">
          <tr>
            <td align="center">
              <a href="{portal_url}" target="_blank"
                 style="background:#2563eb;color:#ffffff;text-decoration:none;font-size:15px;font-weight:700;padding:14px 34px;border-radius:10px;display:inline-block;box-shadow:0 4px 12px rgba(37,99,235,0.25)">
                เข้าสู่ห้องเจรจาข้อเสนอทางการค้า (Supplier Portal) →
              </a>
            </td>
          </tr>
        </table>

        <p style="font-size:11px;color:#64748b;text-align:center;word-break:break-all">
          หรือคัดลอกลิงก์เพื่อเข้าใช้งานผ่านเบราว์เซอร์: <a href="{portal_url}" style="color:#2563eb">{portal_url}</a>
        </p>

        <hr style="border:none;border-top:1px solid #e2e8f0;margin:28px 0 20px 0">

        <!-- SIGNATURE -->
        <table width="100%" cellspacing="0" cellpadding="0">
          <tr>
            <td style="font-size:13px;color:#475569">
              จึงเรียนมาเพื่อโปรดพิจารณาและร่วมยื่นข้อเสนอราคาที่ดีที่สุดสำหรับองค์กรของเรา<br><br>
              ขอแสดงความนับถืออย่างสูง,<br>
              <strong>ฝ่ายบริหารการจัดซื้อเชิงกลยุทธ์และห่วงโซ่อุปทาน</strong><br>
              <span style="font-size:12px;color:#64748b">ระบบจัดซื้ออัจฉริยะ AutoProcure.AI · Enterprise Sourcing Solution</span>
            </td>
          </tr>
        </table>

      </td>
    </tr>

    <!-- FOOTER -->
    <tr>
      <td style="background:#f1f5f9;padding:14px 32px;font-size:11px;color:#64748b;text-align:center">
        อีเมลนี้เป็นเอกสารเชิญยื่นข้อเสนอทางการค้าเฉพาะบุคคล กรุณาอย่าส่งต่อหรือเปิดเผยเงื่อนไขแก่บุคคลภายนอก (Strictly Confidential)
      </td>
    </tr>

  </table>
</body>
</html>"""


def send_magic_link(to_email: str, vendor_name: str, deal_id: str, portal_url: str, deal_data: dict = None) -> dict:
    """
    Send a natural, sophisticated tender invitation with zero target price leakage.
    """
    deal = deal_data or {}
    part_code = deal.get("part_code") or deal_id.upper()
    subject = f"[RFQ-2026] หนังสือเชิญยื่นข้อเสนอราคาอะไหล่ {part_code} (สัญญารายปี) — {vendor_name}"

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
