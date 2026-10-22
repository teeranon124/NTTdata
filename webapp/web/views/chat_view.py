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

    pre_p = float(deal.get("pre_price", 450.0))
    post_p = float(deal.get("post_price", 398.0))
    v_id = str(active_vendor.get("id", "v1")).lower()

    # Dynamic pricing tiers for realistic simulation per vendor
    if "sp" in v_id or "siam" in v_id:
        active_vendor["initial_price"] = 425.0
        active_vendor["counter_price"] = 408.0
        active_vendor["final_price"] = post_p
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
    elif "tk" in v_id or "koyo" in v_id or "thai" in v_id:
        active_vendor["initial_price"] = 430.0
        active_vendor["counter_price"] = 415.0
        active_vendor["final_price"] = 405.0
        active_vendor["rank_text"] = "ตกรอบ SLA (ส่งช้าเกิน 7 วันทำการ)"
        active_vendor["rank_badge"] = "badge-error text-white"
        active_vendor["tco_score"] = 58.2
        active_vendor["initial_credit"] = "30 วัน"
    else:
        active_vendor["initial_price"] = round(pre_p * 0.96, 2)
        active_vendor["counter_price"] = round(post_p * 1.05, 2)
        active_vendor["final_price"] = post_p
        active_vendor["rank_text"] = "อยู่ระหว่างประเมินข้อเสนอ"
        active_vendor["rank_badge"] = "badge-info text-white"
        active_vendor["tco_score"] = 85.0
        active_vendor["initial_credit"] = "30 วัน"

    token = request.args.get("token", f"tok_sec_{deal_id}_{active_vendor.get('id', 'v1')}_verified")
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

    result = send_magic_link(
        to_email=email,
        vendor_name=vendor_name,
        deal_id=deal_id,
        portal_url=portal_url,
    )

    mode = "ส่งจริงผ่าน AWS SES" if result.get("status") == "live_ses" else "โหมดจำลอง (Simulation)"
    add_live_event(f"ส่ง Magic Link เชิญ {vendor_name} เข้าห้องเจรจาดีล {deal_id.upper()} ({mode}) → {email}")

    return jsonify({"portal_url": portal_url, **result})

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
        vendor_data = next((v for v in deal.get("vendors", []) if v["name"].replace(" ", "_").lower() == vendor_id.lower()), None)
        if vendor_data and "messages" in vendor_data:
            session["messages"] = vendor_data["messages"]
            if "ladder" in vendor_data:
                session["concession_ladder"] = vendor_data["ladder"]
            session_repository.save_session(deal_id, vendor_id, session)
    return jsonify({"status": "reset", "session": session})

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
        "tco_data": tco_data,
        "concession": concession,
        "messages": result.get("messages", []),
        "ladder": result.get("ladder", [])
    })
