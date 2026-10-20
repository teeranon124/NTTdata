import os
from flask import Blueprint, request, jsonify, render_template, current_app, send_from_directory
from ...services.negotiation_service import negotiation_service
from ...repositories.deal_repository import deal_repository
from ...repositories.session_repository import session_repository

chat_bp = Blueprint("chat", __name__)
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

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

    result = negotiation_service.negotiate(
        deal_key=deal_key,
        vendor_name=vendor_name,
        latest_user_message=user_message
    )

    return jsonify(result)

@chat_bp.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "online",
        "service": "AutoProcure.AI Enterprise Agent Core",
        "engine": "Amazon Bedrock Nova Native",
        "deals_count": len(deal_repository.get_all_deals())
    })
