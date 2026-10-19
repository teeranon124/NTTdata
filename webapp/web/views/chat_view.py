from flask import Blueprint, request, jsonify, render_template, current_app
from ...services.negotiation_service import negotiation_service

chat_bp = Blueprint("chat", __name__)

@chat_bp.route("/")
def index():
    return render_template("index.html")

@chat_bp.route("/api/negotiate", methods=["POST"])
def negotiate():
    data = request.get_json() or {}
    deal_key = data.get("deal_key", "nsk")
    vendor_name = data.get("vendor_name", "ซัพพลายเออร์")
    history = data.get("history", [])
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"error": "Message cannot be empty"}), 400

    result = negotiation_service.negotiate(
        deal_key=deal_key,
        vendor_name=vendor_name,
        conversation_history=history,
        latest_user_message=user_message
    )

    return jsonify(result)

@chat_bp.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "online",
        "service": "AutoProcure.AI Enterprise API",
        "aws_region": current_app.config.get("AWS_REGION"),
        "bedrock_model": current_app.config.get("BEDROCK_MODEL_ID")
    })
