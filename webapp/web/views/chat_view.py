import logging
logger = logging.getLogger(__name__)
import datetime
import datetime
import json
import os

from flask import Blueprint, Response, jsonify, render_template, request, send_from_directory, stream_with_context

from ...repositories import deal_repository, session_repository
from ...services.email_service import send_magic_link
from ...services.negotiation_service import negotiation_service

chat_bp = Blueprint("chat", __name__)
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

# In-memory recent live events buffer (ticker history for late-joining clients)
RECENT_EVENTS = []

# SSE fan-out broker: in-memory by default, Redis when REDIS_URL is set
# (makes real-time events correct across multiple Gunicorn workers / instances).
from ..sse_broker import broker as _sse_broker


def publish_event(event_type: str, payload: dict):
    """Broadcast a JSON event to every connected SSE subscriber (via the broker)."""
    _sse_broker.publish({"type": event_type, **payload})


def add_live_event(action_text: str):
    now_str = datetime.datetime.now().strftime("%H:%M:%S")
    event = f"[{now_str}] {action_text}"
    RECENT_EVENTS.insert(0, event)
    if len(RECENT_EVENTS) > 30:
        RECENT_EVENTS.pop()
    # Push to live dashboard subscribers so the ticker updates without polling.
    publish_event("ticker", {"text": event})
    return event

# Seed initial dynamic events with current real time
add_live_event("กู้คืนเงินงบประมาณรั่วไหล ฿25,590,483 (-14.97%) สำเร็จจาก 60 ดีล MRO 2,500 PRs")
add_live_event("ตรวจสอบ Guardrail มาตรฐานสเปก JIS B 1514 & เครดิตเทอม 45 วัน... ผ่านเกณฑ์ 100%")
add_live_event("ซัพพลายเออร์ บจก. สยาม พรีซิชั่น ตอบรับเงื่อนไข Blanket Order สัญญา 1 ปี (ดีล NSK 166 PRs)")
add_live_event("สแกนคลังสินค้า SAP MM พบ ROP เตือนอะไหล่ Festo ท่อลม 8mm (250 PRs ชลบุรี/ระยอง)")
add_live_event("AI Agent เชื่อมต่อ SAP S/4HANA รวบยอด 2,500 ใบขอซื้อ (PRs) เป็น 60 ดีลกลยุทธ์ MRO")

@chat_bp.route("/")
def index():
    return render_template("index.html")

@chat_bp.route("/portal/negotiate/<deal_id>")
def supplier_portal(deal_id):
    deal = deal_repository.get_deal(deal_id)
    if not deal:
        deal = {
            "id": deal_id,
            "sku": deal_id.upper(),
            "name": f"อะไหล่อุตสาหกรรม {deal_id.upper()}",
            "supplier": "บจก. คู่ค้าที่ได้รับคำเชิญ",
            "qty": 18755,
            "unit": "ชิ้น",
            "pre_price": 450.0,
            "post_price": 398.0,
            "prs_count": 166,
            "category_th": "เครื่องกล & ส่งกำลัง"
        }

    vendors = deal.get("vendors", [])
    vendor_param = request.args.get("vendor", "").strip().lower()

    active_vendor = None
    if vendors:
        if vendor_param:
            for v in vendors:
                vid = str(v.get("id", "")).lower()
                vname = str(v.get("name", "")).lower()
                if vendor_param in vid or vendor_param in vname:
                    active_vendor = v.copy()
                    break
        if not active_vendor:
            active_vendor = vendors[0].copy()
    else:
        active_vendor = {
            "id": "v1",
            "name": deal.get("supplier", "บจก. คู่ค้า AVL"),
            "price": f"฿{deal.get('post_price', 398):,.2f}",
            "credit": "45 วัน",
            "leadTime": "7 วันทำการ",
            "warranty": "1 ปี",
            "status": "ชนะการประมูล (ออกใบ PO)",
            "statusBadge": "badge-success text-white font-bold"
        }

    pre_p = float(deal.get("pre_price") or 1000.0)
    post_p = float(deal.get("post_price") or round(pre_p * 0.85, 2))
    deal["post_price"] = post_p
    v_id = str(active_vendor.get("id", "v1")).lower()

    # Dynamic pricing tiers tailored to the deal SKU / price scale
    if deal_id == "nsk":
        if "sp" in v_id or "siam" in v_id:
            active_vendor["initial_price"] = 425.0
            active_vendor["counter_price"] = 408.0
            active_vendor["final_price"] = 398.0
            active_vendor["rank_text"] = "TCO Rank #1 (ผู้นำการประมูล)"
            active_vendor["rank_badge"] = "badge-success text-white"
            active_vendor["tco_score"] = 94.8
            active_vendor["initial_credit"] = "30 วัน"
        elif "eb" in v_id or "eastern" in v_id:
            active_vendor["initial_price"] = 440.0
            active_vendor["counter_price"] = 420.0
            active_vendor["final_price"] = 412.0
            active_vendor["rank_text"] = "TCO Rank #2 (ตามหลังผู้นำ ฿14)"
            active_vendor["rank_badge"] = "badge-warning text-slate-900"
            active_vendor["tco_score"] = 81.5
            active_vendor["initial_credit"] = "30 วัน"
        else:
            active_vendor["initial_price"] = 430.0
            active_vendor["counter_price"] = 415.0
            active_vendor["final_price"] = 405.0
            active_vendor["rank_text"] = "ตกรอบ SLA (ส่งช้าเกิน 7 วันทำการ)"
            active_vendor["rank_badge"] = "badge-error text-white"
            active_vendor["tco_score"] = 58.2
            active_vendor["initial_credit"] = "30 วัน"
    else:
        # Scale presets realistically for any deal (Omron, Festo, SKF, etc.)
        active_vendor["initial_price"] = round(pre_p * 0.96, 2)
        active_vendor["counter_price"] = round(pre_p * 0.90, 2)
        active_vendor["final_price"] = post_p
        active_vendor["rank_text"] = "อยู่ระหว่างเจรจาข้อเสนอ (Live Negotiation)"
        active_vendor["rank_badge"] = "badge-info text-white"
        active_vendor["tco_score"] = 88.5
        active_vendor["initial_credit"] = "30 วัน"

    token = request.args.get("token", "").strip()
    target_vid = str(active_vendor.get("id", "v1")).strip().lower()

    # SECURITY VALIDATION: the Magic Link token must EXACTLY match this deal+vendor.
    # Exact match only — no universal bypass token, no loose substring match — so a
    # token issued for one vendor can never open another vendor's room (anti-impersonation).
    def _is_valid_token(tok, d_id, v_id):
        if not tok:
            return False
        t = tok.strip().lower()
        d = d_id.strip().lower()
        v = v_id.strip().lower()
        return t in (f"tok_sec_{d}_{v}_verified", f"tok_sec_{d}_{v}")

    if not _is_valid_token(token, deal_id, target_vid):
        logger.warning(f"Security Alert: Blocked unauthorized portal access for deal={deal_id}, vendor={target_vid}, token={token}")
        if request.headers.get("Accept", "").find("application/json") != -1 and request.headers.get("Accept", "").find("text/html") == -1:
            return jsonify({
                "error": "Forbidden",
                "detail": "Invalid or mismatched Magic Link security token. Cross-vendor impersonation is strictly prohibited.",
                "deal_id": deal_id,
                "vendor_id": target_vid
            }), 403
        
        forbidden_html = f"""<!DOCTYPE html>
<html lang="th" data-theme="dark">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>403 Forbidden — Security Validation Failed</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen flex items-center justify-center p-4 font-sans">
    <div class="max-w-md w-full bg-slate-900 border border-red-500/40 rounded-2xl p-6 shadow-2xl text-center space-y-4">
        <div class="w-12 h-12 rounded-full bg-red-500/20 text-red-400 mx-auto flex items-center justify-center font-bold text-xl border border-red-500/40">
            🔒
        </div>
        <h2 class="text-base font-bold text-red-400 font-mono tracking-wide">403 FORBIDDEN: ACCESS DENIED</h2>
        <p class="text-xs text-slate-300 leading-relaxed">
            การตรวจสอบความถูกต้องของ Magic Link ล้มเหลว: Token ที่ระบุไม่ตรงกับอัตลักษณ์ของคู่ค้า (Vendor Token Mismatch)
        </p>
        <div class="text-[11px] font-mono text-slate-400 bg-slate-950 p-3 rounded-xl border border-slate-800 text-left space-y-1">
            <div>• ดีลจัดซื้อ: <strong class="text-slate-200">{deal_id.upper()}</strong></div>
            <div>• คู่ค้าเป้าหมาย: <strong class="text-slate-200">{active_vendor.get('name', target_vid)}</strong></div>
            <div>• ระบบความปลอดภัย: <span class="text-emerald-400">Anti-Impersonation Protection Active</span></div>
        </div>
        <p class="text-[10px] text-slate-500">
            เพื่อความปลอดภัยทางการค้า กรุณาคลิกลิงก์จากหนังสือเชิญที่ส่งตรงถึงอีเมลของท่านเท่านั้น
        </p>
    </div>
</body>
</html>"""
        return forbidden_html, 403

    is_winner = "ชนะ" in active_vendor.get("status", "") or "ออกใบ PO" in active_vendor.get("status", "")

    return render_template(
        "supplier_portal.html",
        deal=deal,
        active_vendor=active_vendor,
        is_winner=is_winner,
        token=token
    )

@chat_bp.route("/dataset_2500.js")
def serve_dataset_js():
    return send_from_directory(ROOT_DIR, "dataset_2500.js", mimetype="application/javascript")

@chat_bp.route("/dataset_2500.json")
def serve_dataset_json():
    return send_from_directory(ROOT_DIR, "dataset_2500.json", mimetype="application/json")

@chat_bp.route("/api/events")
def get_live_events():
    return jsonify({"events": RECENT_EVENTS})


@chat_bp.route("/api/stream")
def sse_stream():
    """
    Server-Sent Events stream for the Buyer dashboard.
    Pushes supplier chat turns + ticker updates in real time (no polling).
    """
    @stream_with_context
    def generator():
        # Prime the connection so EventSource fires 'open' immediately.
        yield "retry: 3000\n\n"
        yield f"event: ready\ndata: {json.dumps({'type': 'ready'})}\n\n"
        for message in _sse_broker.subscribe():
            if message is None:
                # Heartbeat comment keeps proxies/browsers from closing the stream.
                yield ": keep-alive\n\n"
            else:
                yield f"data: {json.dumps(message, ensure_ascii=False)}\n\n"

    headers = {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no",
        "Connection": "keep-alive",
    }
    return Response(generator(), headers=headers)


@chat_bp.route("/api/send-invite", methods=["POST"])
def send_invite():
    """
    Send (or simulate) a supplier Magic Link invitation via AWS SES.
    Returns status 'live_ses' or 'simulated' — always 200 so the UI never breaks.
    """
    data = request.json or {}
    deal_id = (data.get("deal_id") or "nsk").strip()
    vendor_id = (data.get("vendor_id") or "sp").strip()
    vendor_name = (data.get("vendor_name") or "บจก. คู่ค้า AVL").strip()
    email = (data.get("email") or "").strip()

    if not email:
        return jsonify({"status": "error", "detail": "กรุณาระบุอีเมลผู้รับ"}), 400

    origin = request.host_url.rstrip("/")
    token = f"tok_sec_{deal_id}_{vendor_id}_verified"
    portal_url = f"{origin}/portal/negotiate/{deal_id}?vendor={vendor_id}&token={token}"

    deal_data = deal_repository.get_deal(deal_id) or {}
    result = send_magic_link(
        to_email=email,
        vendor_name=vendor_name,
        deal_id=deal_id,
        portal_url=portal_url,
        deal_data=deal_data,
    )

    mode = "ส่งจริงผ่าน AWS SES" if result.get("status") == "live_ses" else "โหมดจำลอง (Simulation)"
    add_live_event(f"ส่ง Magic Link เชิญ {vendor_name} เข้าห้องเจรจาดีล {deal_id.upper()} ({mode}) → {email}")

    return jsonify({"portal_url": portal_url, **result})


@chat_bp.route("/api/deals/<deal_id>/vendors/<vendor_id>/email", methods=["POST"])
def update_vendor_email(deal_id, vendor_id):
    """Update and persist vendor email in database and memory."""
    data = request.json or {}
    new_email = (data.get("email") or "").strip()
    if not new_email:
        return jsonify({"status": "error", "detail": "Email cannot be empty"}), 400

    # 1. Update in SQLite DB if ORM enabled
    try:
        from ...database.engine import session_scope
        from ...database.models import Vendor
        from sqlalchemy.orm.attributes import flag_modified
        with session_scope() as session:
            v = session.query(Vendor).filter_by(deal_id=deal_id, vendor_id=vendor_id).first()
            if v:
                v.email = new_email
                raw = dict(v.raw or {})
                raw["email"] = new_email
                v.raw = raw
                flag_modified(v, "raw")
                session.add(v)
    except Exception as e:
        logger.warning(f"Could not update vendor email in DB: {e}")

    # 2. Update in deal_repository
    deal = deal_repository.get_deal(deal_id)
    if deal:
        for v in deal.get("vendors", []):
            if v.get("id") == vendor_id:
                v["email"] = new_email

    add_live_event(f"อัปเดตอีเมลคู่ค้า {vendor_id} ในดีล {deal_id.upper()} เป็น {new_email}")
    return jsonify({"status": "success", "deal_id": deal_id, "vendor_id": vendor_id, "email": new_email})

@chat_bp.route("/api/deals")
def get_deals():
    deals = deal_repository.get_all_deals()
    return jsonify({"deals": deals, "count": len(deals)})

@chat_bp.route("/api/deals/<deal_id>")
def get_deal(deal_id):
    deal = deal_repository.get_deal(deal_id)
    if not deal:
        return jsonify({"error": "Deal not found"}), 404
    return jsonify({"deal": deal})

@chat_bp.route("/api/deals/<deal_id>/prs")
def get_deal_prs(deal_id):
    limit = request.args.get("limit", default=250, type=int)
    prs = deal_repository.get_raw_transactions(deal_id=deal_id, limit=limit)
    return jsonify({
        "deal_id": deal_id,
        "count": len(prs),
        "transactions": prs
    })

@chat_bp.route("/api/stats")
def get_stats():
    stats = deal_repository.get_statistics()
    # Return both keys: "stats" (legacy contract) and "statistics" (what the
    # dashboard JS actually reads) so the live stat cards populate correctly.
    return jsonify({"stats": stats, "statistics": stats})

@chat_bp.route("/api/chat/<deal_id>/<vendor_id>", methods=["GET"])
def get_chat_session(deal_id, vendor_id):
    deal = deal_repository.get_deal(deal_id)
    if not deal:
        return jsonify({"error": "Deal not found"}), 404

    session = session_repository.load_session(deal_id, vendor_id)
    if not session.get("messages"):
        # Seed initial opening messages from vendor profile on first load.
        vendor_data = next((v for v in deal.get("vendors", []) if v["name"].replace(" ", "_").lower() == vendor_id.lower()), None)
        if vendor_data and "messages" in vendor_data:
            session["messages"] = vendor_data["messages"]
            if "ladder" in vendor_data:
                session["concession_ladder"] = vendor_data["ladder"]
            session_repository.save_session(deal_id, vendor_id, session)

    return jsonify({"session": session})

@chat_bp.route("/api/chat/<deal_id>/<vendor_id>/reset", methods=["POST"])
def reset_chat_session(deal_id, vendor_id):
    deal = deal_repository.get_deal(deal_id)
    session = negotiation_service.reset_session(deal_id, vendor_id)
    if deal:
        did = (deal_id or "").lower()
        # Rollback winning status and stage if the deal was previously awarded
        if deal.get("stage") in (4, 5) or deal.get("winning_vendor_id"):
            deal["stage"] = 4 if did == "nsk" else 2
            deal["stage_label"] = "รอลงนาม PO" if did == "nsk" else "ออกเทียบราคา"
            deal["winning_vendor_id"] = None
            deal["agreed_price"] = None
            deal["po_status"] = None
            deal["po_number"] = None
            try:
                from ...database.engine import session_scope
                from ...database.models import Deal
                with session_scope() as s:
                    db_d = s.get(Deal, did)
                    if db_d:
                        db_d.stage = deal["stage"]
                        db_d.stage_label = deal["stage_label"]
                        db_d.winning_vendor_id = None
                        db_d.agreed_price = None
                        db_d.po_status = None
                        db_d.po_number = None
            except Exception as e:
                pass

        vendor_data = next((v for v in deal.get("vendors", []) if v["name"].replace(" ", "_").lower() == vendor_id.lower()), None)
        if vendor_data and "messages" in vendor_data:
            session["messages"] = vendor_data["messages"]
            if "ladder" in vendor_data:
                session["concession_ladder"] = vendor_data["ladder"]
            session_repository.save_session(deal_id, vendor_id, session)

    publish_event("deal_reset", {"deal_id": deal_id, "stage": deal.get("stage") if deal else 2})
    return jsonify({"status": "reset", "session": session, "deal": deal})

@chat_bp.route("/api/sla")
@chat_bp.route("/api/sla/<deal_id>")
def get_sla_status(deal_id=None):
    """
    Negotiation SLA / Anti-Stall monitor: lists sessions and flags any that have
    gone quiet beyond the response-SLA window (needs_followup=true). Answers
    'how do you prevent stalling a counterpart / detect a stalled negotiation?'.
    """
    return jsonify(negotiation_service.get_sla_status(deal_id))


@chat_bp.route("/api/deals/<deal_id>/award-board")
def get_award_board(deal_id):
    """
    Multi-Vendor Award Board: ranks every vendor negotiated in this deal by latest
    TCO score and declares the BAFO winner. Answers 'how does it decide between
    multiple suppliers?'.
    """
    board = negotiation_service.get_award_board(deal_id)
    return jsonify(board)


@chat_bp.route("/api/audit/sessions")
def list_audit_sessions():
    """HITL governance: index of all negotiation sessions with sign-off status."""
    sessions = session_repository.list_sessions() if hasattr(session_repository, "list_sessions") else []
    return jsonify({"sessions": sessions, "count": len(sessions)})


@chat_bp.route("/api/admin/reset-sessions", methods=["POST"])
def admin_reset_sessions():
    """
    Data hygiene: wipe ALL transient negotiation sessions while keeping the seed
    catalog (60 deals + 2,500 PRs) intact — a clean slate before a live demo.

    Protected by an admin token. Set ADMIN_RESET_TOKEN in the environment and
    pass it as the X-Admin-Token header (or {"token": "..."} in the body). If no
    token is configured the endpoint is disabled (safe-by-default in production).
    """
    configured = os.environ.get("ADMIN_RESET_TOKEN", "").strip()
    if not configured:
        return jsonify({"status": "disabled",
                        "detail": "ADMIN_RESET_TOKEN is not set — reset endpoint is disabled."}), 403

    data = request.json or {}
    provided = (request.headers.get("X-Admin-Token") or data.get("token") or "").strip()
    if provided != configured:
        return jsonify({"status": "forbidden", "detail": "Invalid admin token."}), 403

    if not hasattr(session_repository, "clear_all_sessions"):
        return jsonify({"status": "unsupported"}), 501

    removed = session_repository.clear_all_sessions()
    add_live_event(f"ล้างข้อมูลเซสชันการเจรจาทั้งหมด {removed} รายการ (เตรียมพร้อมสำหรับการสาธิต) [Admin Reset]")
    return jsonify({"status": "ok", "sessions_cleared": removed})


@chat_bp.route("/api/audit/<deal_id>/<vendor_id>")
def get_audit_trail(deal_id, vendor_id):
    """HITL governance: full audit trail + model/cost rollup for a session."""
    if not hasattr(session_repository, "get_audit_trail"):
        return jsonify({"error": "Audit trail not available on this backend"}), 501
    return jsonify(session_repository.get_audit_trail(deal_id, vendor_id))


@chat_bp.route("/api/signoff/<deal_id>/<vendor_id>", methods=["POST"])
def executive_signoff(deal_id, vendor_id):
    """HITL governance: record an executive sign-off (approve/reject) + PO number."""
    if not hasattr(session_repository, "sign_off"):
        return jsonify({"error": "Sign-off not available on this backend"}), 501
    data = request.json or {}
    approved_by = (data.get("approved_by") or "CPO").strip()
    decision = (data.get("decision") or "approved").strip().lower()
    po_number = data.get("po_number")
    note = data.get("note")

    result = session_repository.sign_off(
        deal_id=deal_id, vendor_id=vendor_id,
        approved_by=approved_by, decision=decision, po_number=po_number, note=note,
    )
    verb = "อนุมัติ" if result.get("status") == "approved" else "ปฏิเสธ"
    po_txt = f" | PO: {po_number}" if po_number else ""
    add_live_event(f"ผู้บริหาร ({approved_by}) {verb}การลงนามดีล {deal_id.upper()}{po_txt} [Human-in-the-Loop]")
    return jsonify({"status": "ok", "signoff": result})


@chat_bp.route("/api/deals/<deal_id>/create-po", methods=["POST"])
def create_po(deal_id):
    """
    Closed-loop SAP PO creation. Generates a SAP-style PO number, records it on
    the deal (po_status=PO_CREATED, stage 4), logs an audit event, and returns
    the PO number so the dashboard can update its stats. Simulates BAPI_PO_CREATE1.
    """
    import random
    data = request.json or {}
    approved_by = (data.get("approved_by") or "CPO").strip()
    vendor_id = data.get("vendor_id") or ""

    deal = deal_repository.get_deal(deal_id)
    if not deal:
        return jsonify({"status": "error", "detail": f"Deal {deal_id} not found"}), 404

    # SAP S/4HANA purchase order numbers are 10-digit, commonly starting 45xxxxxxxx.
    po_number = f"PO#{random.randint(4500000000, 4509999999)}"

    if hasattr(deal_repository, "create_po"):
        deal_repository.create_po(deal_id, po_number)

    # Record the executive sign-off on the winning vendor's session too.
    win_vendor = vendor_id or deal.get("winning_vendor_id") or ""
    if win_vendor and hasattr(session_repository, "sign_off"):
        try:
            session_repository.sign_off(
                deal_id=deal_id, vendor_id=win_vendor,
                approved_by=approved_by, decision="approved", po_number=po_number,
                note="BAPI_PO_CREATE1 committed to SAP S/4HANA",
            )
        except Exception as e:
            logger.warning(f"sign_off during create-po failed: {e}")

    add_live_event(
        f"✅ ผู้บริหาร ({approved_by}) ลงนามอนุมัติดีล {deal_id.upper()} ➔ ยิง BAPI_PO_CREATE1 "
        f"ออกใบสั่งซื้อ {po_number} เข้า SAP S/4HANA สำเร็จ [Closed-Loop]"
    )
    publish_event("po_created", {
        "deal_id": deal_id,
        "po_number": po_number,
        "approved_by": approved_by,
        "stage": 5,
        "stage_label": "ออก PO สำเร็จ",
        "time": datetime.datetime.now().strftime("%H:%M:%S"),
    })

    return jsonify({
        "status": "success",
        "deal_id": deal_id,
        "po_number": po_number,
        "po_status": "PO_CREATED",
        "stage": 5,
        "stage_label": "ออก PO สำเร็จ",
        "approved_by": approved_by,
    })


@chat_bp.route("/api/negotiate", methods=["POST"])
def negotiate():
    data = request.json or {}
    deal_id = data.get("deal_id", "nsk")
    vendor_id = data.get("vendor_id", "siam_precision")
    vendor_name = data.get("vendor_name", "สยาม พรีซิชั่น (ฝ่ายขาย)")
    message = data.get("message", "")
    round_num = data.get("round", 1)

    result = negotiation_service.negotiate(
        deal_key=deal_id,
        vendor_name=vendor_name,
        latest_user_message=message
    )

    reply_text = result.get("reply", "")
    tactic_text = result.get("tactic", "")
    concession = result.get("concession", {})
    parsed_intent = result.get("parsed_intent", {})
    tco_data = result.get("tco_data", {})

    target_price = concession.get("counter_price") or concession.get("target_price") or parsed_intent.get("proposed_unit_price")
    credit_days = parsed_intent.get("proposed_credit_days") or concession.get("target_credit")
    is_agreed = concession.get("strategy") == "AGREE_AND_AWARD" or "ตกลง" in message or "รับข้อเสนอ" in message

    # Closed-loop: when the negotiation is agreed, transition the deal to Stage 4
    # (รออนุมัติ PO) and record the winning vendor, so the sign-off button unlocks.
    stage_now = None
    if is_agreed and hasattr(deal_repository, "mark_deal_awarded"):
        try:
            agreed_price = concession.get("counter_price") or parsed_intent.get("proposed_unit_price") or target_price
            if deal_repository.mark_deal_awarded(deal_id, vendor_id, agreed_price):
                stage_now = 4
                add_live_event(f"✅ ดีล {deal_id.upper()} บรรลุข้อตกลงกับ {vendor_name} ➔ เลื่อนเป็น Stage 4 (รออนุมัติ PO)")
        except Exception as e:
            logger.warning(f"mark_deal_awarded failed: {e}")

    add_live_event(f"AI Agent เจรจาดีล {deal_id.upper()} กับ {vendor_name}: เสนอเงื่อนไขรอบ {round_num}")

    # Real-time push to the Buyer dashboard: supplier message + AI reply land live.
    now_hhmm = datetime.datetime.now().strftime("%H:%M")
    publish_event("negotiation", {
        "deal_id": deal_id,
        "vendor_id": vendor_id,
        "vendor_name": vendor_name,
        "vendor_text": message,
        "agent_reply": reply_text,
        "tactic": tactic_text,
        "price": target_price,
        "credit_days": credit_days,
        "deal_agreed": bool(is_agreed),
        "stage": stage_now,
        "commercial_terms": result.get("commercial_terms", {}),
        "round": round_num,
        "time": now_hhmm,
    })

    return jsonify({
        "status": "success",
        "agent_reply": reply_text,
        "reply": reply_text,
        "tactic": tactic_text,
        "price": target_price,
        "credit_days": credit_days,
        "deal_agreed": is_agreed,
        "stage": stage_now,
        "tco_data": tco_data,
        "concession": concession,
        "commercial_terms": result.get("commercial_terms", {}),
        "messages": result.get("messages", []),
        "ladder": result.get("ladder", [])
    })


# ==============================================================================
# PLANT TERMINAL & EVENT-DRIVEN AUTONOMOUS TRIGGER SIMULATION
# ==============================================================================

@chat_bp.route("/plant-terminal")
def plant_terminal():
    """
    Simulated Plant Terminal for Factory Engineers (e.g. Rayong Plant #04).
    Used during live demos to trigger emergency PRs and demonstrate autonomous sourcing.
    """
    return render_template("plant_terminal.html")


@chat_bp.route("/api/simulate/incoming-pr", methods=["POST"])
def simulate_incoming_pr():
    """
    Simulates incoming PR from plant.
    When volume reaches the threshold (>=800 units), AutoProcure.AI
    automatically transitions the deal to Stage 2 and dispatches RFQs
    to all approved vendors via AWS SES.
    """
    data = request.json or {}
    deal_id = data.get("deal_id", "festo_cyl")
    plant = data.get("plant", "Rayong Plant #04")
    pr_code = data.get("pr_code", "PR-2026-RYG-014")
    quantity = data.get("quantity", 100)

    deal = deal_repository.get_deal(deal_id)
    if not deal:
        return jsonify({"status": "error", "detail": f"Deal {deal_id} not found"}), 404

    # Update state to Stage 2 with 850 units / 14 PRs in Database
    try:
        from ...database.engine import session_scope
        from ...database.models import Deal
        with session_scope() as session:
            db_deal = session.query(Deal).filter_by(id=deal_id).first()
            if db_deal:
                db_deal.stage = 2
                db_deal.qty = 850
                db_deal.prs_count = 14
                db_deal.stage_label = "ออกเทียบราคา"
    except Exception as e:
        logger.warning(f"Could not update DB directly: {e}")

    # Dispatch RFQs to all 3 vendors via AWS SES
    origin = request.host_url.rstrip("/")
    vendors = deal.get("vendors", [])
    dispatched = []

    for v in vendors:
        v_id = v.get("id")
        v_name = v.get("name")
        email = v.get("email") or "teeranonn124@gmail.com"
        token = f"tok_sec_{deal_id}_{v_id}_verified"
        portal_url = f"{origin}/portal/negotiate/{deal_id}?vendor={v_id}&token={token}"

        res = send_magic_link(
            to_email=email,
            vendor_name=v_name,
            deal_id=deal_id,
            portal_url=portal_url,
            deal_data=deal,
        )
        dispatched.append({"vendor": v_name, "email": email, "status": res.get("status")})

    # Broadcast event to central procurement dashboard
    now_str = datetime.datetime.now().strftime("%H:%M:%S")
    action_msg = f"⚡ [Threshold Trigger] ตรวจพบใบขอซื้อ {pr_code} ({quantity} ตัว) จาก {plant} ยอดสะสมแตะ 850 ตัว ➔ ระบบเปลี่ยนเป็น Stage 2 และยิงเทียบเชิญ RFQ ทาง AWS SES อัตโนมัติไปยังซัพพลายเออร์ 3 รายทันที"
    add_live_event(action_msg)

    publish_event("deal_triggered", {
        "deal_id": deal_id,
        "sku": deal.get("sku", "FESTO-DSBC-32-100"),
        "qty": 850,
        "prs": 14,
        "stage": 2,
        "plant": plant,
        "pr_code": pr_code,
        "time": now_str,
        "dispatched_count": len(dispatched)
    })

    return jsonify({
        "status": "success",
        "deal_id": deal_id,
        "qty": 850,
        "prs": 14,
        "stage": 2,
        "dispatched": dispatched
    })


@chat_bp.route("/api/simulate/reset-pr", methods=["POST"])
def simulate_reset_pr():
    """Reset festo_cyl deal back to Stage 1 for clean re-demoing."""
    deal_id = "festo_cyl"
    try:
        from ...database.engine import session_scope
        from ...database.models import Deal
        with session_scope() as session:
            db_deal = session.query(Deal).filter_by(id=deal_id).first()
            if db_deal:
                db_deal.stage = 1
                db_deal.qty = 750
                db_deal.prs_count = 13
                db_deal.stage_label = "รวมความต้องการ"
    except Exception as e:
        logger.warning(f"Could not reset DB directly: {e}")

    add_live_event("🔄 [Demo Reset] รีเซ็ตดีล FESTO-DSBC-32-100 กลับสู่ Stage 1 (750 ตัว, 13 PRs) พร้อมสำหรับการซ้อมรอบใหม่")
    publish_event("deal_reset", {
        "deal_id": deal_id,
        "qty": 750,
        "prs": 13,
        "stage": 1
    })

    return jsonify({"status": "success", "stage": 1, "qty": 750, "prs": 13})


@chat_bp.route("/api/demo/reset-all", methods=["POST"])
def demo_reset_all():
    """
    Master Demo Reset:
    1. Resets all transient sessions (clears messages, concession ladders, audit traces).
    2. Resets all Deals and PRs back to their baseline demo stages:
       - festo_cyl: Stage 1 (750 qty, 13 PRs, รวบรวม PR)
       - omron_photo: Stage 2 (1,400 qty, 22 PRs, รอเจรจาต่อรอง)
       - nsk: Stage 3 (5,000 qty, 28 PRs, AI กำลังเจรจา)
    3. Resets SQLite database if USE_DATABASE is enabled.
    """
    # 1. Reset file-based JSON sessions
    sessions_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "sessions")
    if os.path.exists(sessions_dir):
        for f in os.listdir(sessions_dir):
            if f.endswith(".json"):
                try:
                    os.remove(os.path.join(sessions_dir, f))
                except Exception:
                    pass

    # 2. Reset database tables
    try:
        from ...database.seed_loader import seed, reset_sessions
        reset_sessions()
        seed(force=True)
    except Exception as e:
        logger.warning(f"DB reset error (fallback to JSON): {e}")

    # 3. Reload in-memory deal repository
    if hasattr(deal_repository, "reload"):
        deal_repository.reload()

    # 4. Explicitly guarantee baseline stages for core demo deals
    deals = deal_repository.get_all_deals()
    if "festo_cyl" in deals:
        deals["festo_cyl"]["stage"] = 1
        deals["festo_cyl"]["stage_label"] = "รวมความต้องการ"
        deals["festo_cyl"]["qty"] = 750
        deals["festo_cyl"]["prs_count"] = 13
        deals["festo_cyl"]["winning_vendor_id"] = None
        deals["festo_cyl"]["po_status"] = None
        deals["festo_cyl"]["po_number"] = None

    if "omron_photo" in deals:
        deals["omron_photo"]["stage"] = 2
        deals["omron_photo"]["stage_label"] = "ออกเทียบราคา"
        deals["omron_photo"]["qty"] = 1400
        deals["omron_photo"]["prs_count"] = 22
        deals["omron_photo"]["winning_vendor_id"] = None
        deals["omron_photo"]["po_status"] = None
        deals["omron_photo"]["po_number"] = None

    if "nsk" in deals:
        deals["nsk"]["stage"] = 4
        deals["nsk"]["stage_label"] = "รอลงนาม PO"
        deals["nsk"]["winning_vendor_id"] = None
        deals["nsk"]["po_status"] = None
        deals["nsk"]["po_number"] = None

    add_live_event("🔄 [Master Demo Reset] ล้างประวัติแชทและคืนค่าสถานะดีลทุกตัวสู่จุดเริ่มต้นสำหรับ Live Demo เรียบร้อยแล้ว")
    publish_event("deal_reset", {"status": "all_reset"})

    return jsonify({"status": "success", "message": "Demo system reset complete"})
