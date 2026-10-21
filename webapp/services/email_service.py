"""
AWS SES Email Service for supplier Magic Link invitations.

Design goal: NEVER crash a live demo.
- SES_ENABLED=false (default) -> simulated send: logs the invite and returns a
  'simulated' status. No AWS call is made.
- SES_ENABLED=true -> real boto3 ses.send_email(). Any failure (missing identity,
  sandbox restriction, network) is caught and degraded to a 'simulated' result so
  the UI keeps flowing.
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


def _build_html(vendor_name: str, deal_id: str, portal_url: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="th">
<head><meta charset="utf-8"></head>
<body style="font-family:'Segoe UI',Tahoma,sans-serif;background:#f1f5f9;padding:24px;color:#0f172a">
  <div style="max-width:560px;margin:auto;background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 10px 30px rgba(15,23,42,.08)">
    <div style="background:#4338ca;padding:20px 28px;color:#fff">
      <div style="font-size:13px;letter-spacing:.08em;opacity:.85">AUTOPROCURE.AI · NTT DATA</div>
      <div style="font-size:20px;font-weight:700;margin-top:4px">คำเชิญเข้าสู่ห้องเจรจาจัดซื้ออิเล็กทรอนิกส์</div>
    </div>
    <div style="padding:28px">
      <p>เรียน ทีมขาย <strong>{vendor_name}</strong></p>
      <p>ฝ่ายจัดซื้อกลางขอเรียนเชิญท่านเข้าสู่ห้องเจรจาเงื่อนไขทางพาณิชย์สำหรับดีล
         <strong>{deal_id.upper()}</strong> ผ่านลิงก์เฉพาะบุคคล (Magic Link) ด้านล่างนี้</p>
      <p style="text-align:center;margin:28px 0">
        <a href="{portal_url}"
           style="background:#4338ca;color:#fff;text-decoration:none;padding:12px 28px;border-radius:12px;font-weight:700;display:inline-block">
          เข้าสู่ห้องเจรจา (Supplier Portal)
        </a>
      </p>
      <p style="font-size:12px;color:#64748b;word-break:break-all">หากปุ่มไม่ทำงาน กรุณาคัดลอกลิงก์นี้: {portal_url}</p>
      <hr style="border:none;border-top:1px solid #e2e8f0;margin:20px 0">
      <p style="font-size:12px;color:#94a3b8">อีเมลนี้จัดส่งอัตโนมัติโดยระบบ AutoProcure.AI · กรุณาอย่าตอบกลับ</p>
    </div>
  </div>
</body>
</html>"""


def send_magic_link(to_email: str, vendor_name: str, deal_id: str, portal_url: str) -> dict:
    """
    Send a supplier invite. Returns a dict describing the outcome:
      {"status": "live_ses" | "simulated", "detail": "...", "message_id": optional}
    """
    subject = f"[AutoProcure.AI] คำเชิญเจรจาดีล {deal_id.upper()} — {vendor_name}"

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
                "Body": {"Html": {"Data": _build_html(vendor_name, deal_id, portal_url), "Charset": "UTF-8"}},
            },
        )
        message_id = resp.get("MessageId")
        logger.info("SES live invite sent to %s (MessageId=%s)", to_email, message_id)
        return {
            "status": "live_ses",
            "detail": "ส่งอีเมลจริงผ่าน AWS SES สำเร็จ",
            "to": to_email,
            "message_id": message_id,
            "portal_url": portal_url,
        }
    except Exception as e:
        # Degrade gracefully — never break the demo flow.
        logger.warning("SES live send failed (%s) — degrading to simulated.", e)
        return {
            "status": "simulated",
            "detail": f"AWS SES ส่งไม่สำเร็จ ({e.__class__.__name__}) — ใช้โหมดจำลองแทน",
            "to": to_email,
            "portal_url": portal_url,
        }
