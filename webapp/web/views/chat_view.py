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
                    active_vendor = v
                    break
        if not active_vendor:
            active_vendor = vendors[0]
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
    prs = deal_repository.get_prs_for_deal(deal_id)
    limit = request.args.get("limit", default=250, type=int)
    return jsonify({
        "deal_id": deal_id,
        "count": len(prs),
        "transactions": prs[:limit]
    })

@chat_bp.route("/api/stats")
def get_stats():
    stats = deal_repository.get_system_stats()
    return jsonify({"stats": stats})

@chat_bp.route("/api/chat/<deal_id>/<vendor_id>", methods=["GET"])
def get_chat_session(deal_id, vendor_id):
    deal = deal_repository.get_deal(deal_id)
    if not deal:
        return jsonify({"error": "Deal not found"}), 404

    session = session_repository.get_session(deal_id, vendor_id)
    if not session:
        session = session_repository.create_session(deal_id, vendor_id)
        # Seed initial opening messages from vendor profile
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
    session = session_repository.create_session(deal_id, vendor_id)
    if deal:
        vendor_data = next((v for v in deal.get("vendors", []) if v["name"].replace(" ", "_").lower() == vendor_id.lower()), None)
        if vendor_data and "messages" in vendor_data:
            session["messages"] = vendor_data["messages"]
            if "ladder" in vendor_data:
                session["concession_ladder"] = vendor_data["ladder"]
            session_repository.save_session(deal_id, vendor_id, session)
    return jsonify({"status": "reset", "session": session})

@chat_bp.route("/api/negotiate", methods=["POST"])
def negotiate():
    data = request.json or {}
    deal_id = data.get("deal_id", "nsk")
    vendor_id = data.get("vendor_id", "siam_precision")
    vendor_name = data.get("vendor_name", "สยาม พรีซิชั่น (ฝ่ายขาย)")
    message = data.get("message", "")
    round_num = data.get("round", 1)

    result = negotiation_service.process_turn(
        deal_id=deal_id,
        vendor_id=vendor_id,
        vendor_name=vendor_name,
        user_message=message,
        round_num=round_num
    )

    if result.get("agent_reply"):
        add_live_event(f"AI Agent เจรจาดีล {deal_id.upper()} กับ {vendor_name}: เสนอเงื่อนไขรอบ {round_num}")

    return jsonify(result)
