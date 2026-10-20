import os
import datetime
from flask import Blueprint, request, jsonify, render_template, current_app, send_from_directory
from ...services.negotiation_service import negotiation_service
from ...repositories.deal_repository import deal_repository
from ...repositories.session_repository import session_repository

chat_bp = Blueprint("chat", __name__)
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

# In-memory recent live events buffer
RECENT_EVENTS = []

def add_live_event(action_text: str):
    now_str = datetime.datetime.now().strftime("%H:%M:%S")
    event = f"[{now_str}] {action_text}"
    RECENT_EVENTS.insert(0, event)
    if len(RECENT_EVENTS) > 30:
        RECENT_EVENTS.pop()
    return event

# Seed initial dynamic events with current real time
add_live_event("กู้คืนเงินงบประมาณรั่วไหล ฿12,591,973 (-12.6%) สำเร็จจาก 10 ดีลหลัก 2,500 PRs")
add_live_event("ตรวจสอบ Guardrail มาตรฐานสเปก JIS B 1514 & เครดิตเทอม 45 วัน... ผ่านเกณฑ์ 100%")
add_live_event("ซัพพลายเออร์ บจก. สยาม พรีซิชั่น ตอบรับเงื่อนไข Blanket Order สัญญา 1 ปี (ดีล NSK 250 PRs)")
add_live_event("สแกนคลังสินค้า SAP MM พบ ROP เตือนอะไหล่ Festo ท่อลม 8mm (250 PRs ชลบุรี/ระยอง)")
add_live_event("AI Agent เชื่อมต่อ SAP S/4HANA รวบยอด 2,500 ใบขอซื้อ (PRs) เป็น 10 ดีลกลยุทธ์")

@chat_bp.route("/")
def index():
    return render_template("index.html")

@chat_bp.route("/dataset_2500.js")
def serve_dataset_js():
    return send_from_directory(ROOT_DIR, "dataset_2500.js", mimetype="application/javascript")

@chat_bp.route("/dataset_2500.json")
def serve_dataset_json():
    return send_from_directory(ROOT_DIR, "dataset_2500.json", mimetype="application/json")

@chat_bp.route("/api/deals", methods=["GET"])
def get_deals():
    """
    Returns all 10 consolidated deals and overall statistics aggregated from 2,500 transactions.
    """
    deals = deal_repository.get_all_deals()
    stats = deal_repository.get_statistics()
    return jsonify({
        "status": "success",
        "deals": deals,
        "statistics": stats
    })

@chat_bp.route("/api/deals/<deal_id>", methods=["GET"])
def get_deal_detail(deal_id):
    """
    Returns detail of a single deal by ID.
    """
    deal = deal_repository.get_deal(deal_id)
    if not deal:
        return jsonify({"error": "Deal not found"}), 404
    return jsonify({"status": "success", "deal": deal})

@chat_bp.route("/api/deals/<deal_id>/prs", methods=["GET"])
def get_deal_prs(deal_id):
    """
    Returns PR transactions from the 2,500 dataset corresponding to this deal.
    """
    limit = request.args.get("limit", 250, type=int)
    offset = request.args.get("offset", 0, type=int)
    prs = deal_repository.get_raw_transactions(deal_id=deal_id, limit=limit, offset=offset)
    return jsonify({
        "status": "success",
        "deal_id": deal_id,
        "total_returned": len(prs),
        "transactions": prs
    })

@chat_bp.route("/api/stats", methods=["GET"])
def get_stats():
    """
    Returns global KPIs and stage counts.
    """
    stats = deal_repository.get_statistics()
    return jsonify({"status": "success", "statistics": stats})

@chat_bp.route("/api/events", methods=["GET"])
def get_events():
    """
    Returns dynamic real-time live events stream.
    """
    return jsonify({
        "status": "success",
        "server_time": datetime.datetime.now().strftime("%H:%M:%S"),
        "events": RECENT_EVENTS
    })

@chat_bp.route("/api/chat/<deal_id>/<vendor_id>", methods=["GET"])
def get_chat_session(deal_id, vendor_id):
    """
    Returns persistent chat messages, concession ladder, and audit traces for a specific deal and vendor.
    """
    session = session_repository.load_session(deal_id, vendor_id)
    return jsonify({"status": "success", "session": session})

@chat_bp.route("/api/chat/<deal_id>/<vendor_id>/reset", methods=["POST"])
def reset_chat_session(deal_id, vendor_id):
    """
    Resets the chat session for a specific deal and vendor.
    """
    session = negotiation_service.reset_session(deal_id, vendor_id)
    add_live_event(f"ผู้ใช้รีเซ็ตห้องเจรจาต่อรองดีล {deal_id} ({vendor_id}) เพื่อเริ่มกลยุทธ์ใหม่")
    return jsonify({"status": "success", "session": session})

@chat_bp.route("/api/negotiate", methods=["POST"])
def negotiate():
    """
    Executes a multi-turn negotiation turn with the AI Agent.
    """
    data = request.get_json() or {}
    deal_key = data.get("deal_key", "nsk")
    vendor_name = data.get("vendor_name", "บจก. ซัพพลายเออร์")
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"error": "Message cannot be empty"}), 400

    add_live_event(f"ซัพพลายเออร์ {vendor_name} ({deal_key.upper()}) ส่งข้อเสนอ: '{user_message[:30]}...' -> Agent เริ่มคำนวณ Nash Bargaining")

    result = negotiation_service.negotiate(
        deal_key=deal_key,
        vendor_name=vendor_name,
        latest_user_message=user_message
    )

    tactic = result.get("tactic_used", "Game Theory Concession")
    price = result.get("current_offered_price", "")
    add_live_event(f"AI Agent ตอบกลับ {vendor_name}: ยื่นข้อเสนอ {price} พร้อมยุทธวิธี {tactic}")

    return jsonify(result)

@chat_bp.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "online",
        "service": "AutoProcure.AI Enterprise Agent Core",
        "engine": "Amazon Bedrock Nova Native",
        "deals_count": len(deal_repository.get_all_deals())
    })
