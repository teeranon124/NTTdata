import logging
import time
from typing import Dict, List, Optional
from ..repositories import deal_repository, session_repository
from ..agents.router_agent import parse_supplier_intent
from ..agents.negotiator_agent import run_negotiation_turn

logger = logging.getLogger(__name__)

class BedrockNegotiationService:
    def __init__(self):
        pass

    def get_session(self, deal_id: str, vendor_id: str) -> dict:
        return session_repository.load_session(deal_id, vendor_id)

    def reset_session(self, deal_id: str, vendor_id: str) -> dict:
        session = {
            'deal_id': deal_id,
            'vendor_id': vendor_id,
            'status': 'in_progress',
            'created_at': time.time(),
            'updated_at': time.time(),
            'concession_ladder': [],
            'audit_traces': [],
            'messages': []
        }
        session_repository.save_session(deal_id, vendor_id, session)
        return session

    def negotiate(self, deal_key: str, vendor_name: str, conversation_history: Optional[list] = None, latest_user_message: str = "") -> dict:
        """
        Conducts negotiation turn as an Autonomous Enterprise MRO Procurement Agent.
        Uses Deal Repository, Session Repository, Router Agent (Nova Lite), and Negotiator Agent (Nova Pro).
        """
        deal_key = deal_key.lower().strip()
        deal_data = deal_repository.get_deal(deal_key)
        
        # Fallback deal data if deal_key is not standard
        if not deal_data:
            deal_data = {
                "id": deal_key,
                "deal_code": f"DEAL-2026-{deal_key.upper()}",
                "part_code": f"{deal_key.upper()}-STD",
                "name": f"อะไหล่มาตรฐาน MRO {deal_key.upper()}",
                "category": "Industrial MRO",
                "total_prs": 250,
                "total_quantity": 5000,
                "plants": ["PLANT-AYU-01", "PLANT-CBI-02", "PLANT-RYG-03"],
                "budget_unit_price": 500.0,
                "target_unit_price": 440.0,
                "budget_total_thb": 2500000.0,
                "target_total_thb": 2200000.0,
                "total_savings_thb": 300000.0,
                "savings_pct": 12.0,
                "standard_credit_days": 30,
                "target_credit_days": 45,
                "stage": 3,
                "stage_meta": {"label": "AI กำลังเจรจา", "badge": "Stage 3", "class": "badge-primary text-white"}
            }

        vendor_id = vendor_name.replace(" ", "_").lower()
        
        # Load or initialize persistent session
        session = session_repository.load_session(deal_key, vendor_id)
        
        # Record incoming supplier message
        now_time = time.strftime("%H:%M")
        user_msg_entry = {
            "sender": "vendor",
            "name": vendor_name,
            "time": now_time,
            "text": latest_user_message
        }
        session["messages"].append(user_msg_entry)
        
        # Step A: Router Agent (Nova Lite / Deterministic Parser)
        parsed_intent = parse_supplier_intent(latest_user_message)
        
        # Step B: Strategic Negotiator Turn (Guardrail -> TCO -> Concession Engine -> Nova Pro)
        # We pass recent conversation history (excluding the current user message which is passed directly)
        history_msgs = session["messages"][:-1]
        
        agent_result = run_negotiation_turn(
            deal_data=deal_data,
            vendor_name=vendor_name,
            user_message=latest_user_message,
            history=history_msgs,
            parsed_entities=parsed_intent
        )
        
        # Record agent reply into session
        agent_reply = agent_result.get("reply", "")
        agent_tactic = agent_result.get("tactic", "[Autonomous Negotiation Engine]")

        # Pull production auditability metadata produced by the orchestrator.
        model_meta = agent_result.get("model_meta", {}) or {}
        arbitration = agent_result.get("arbitration", {}) or {}
        tco_score = arbitration.get("tco_score")

        agent_msg_entry = {
            "sender": "agent",
            "name": "AutoProcure AI (Procurement Agent)",
            "time": time.strftime("%H:%M"),
            "text": agent_reply,
            "tactic": agent_tactic,
            # --- additive auditability metadata (ignored by the frontend) ---
            "model_id": model_meta.get("model_id"),
            "latency_ms": model_meta.get("latency_ms"),
            "input_tokens": model_meta.get("input_tokens"),
            "output_tokens": model_meta.get("output_tokens"),
            "tco_score": tco_score,
        }
        session["messages"].append(agent_msg_entry)
        
        # Update session concession ladder if price/concession was proposed
        tco_data = agent_result.get("tco_data", {})
        concession = agent_result.get("concession", {})
        
        if parsed_intent.get("proposed_unit_price"):
            offered_p = parsed_intent["proposed_unit_price"]
            ladder_entry = {
                "round": f"Round {len(session.get('concession_ladder', [])) + 1}",
                "title": f"ข้อเสนอจากคู่ค้า ฿{offered_p:,.2f}",
                "price": f"฿{offered_p:,.2f}",
                "tag": parsed_intent.get("intent", "Offer"),
                "color": "border-slate-300 text-slate-700",
                "note": f"เครดิต {parsed_intent.get('proposed_credit_days', 30)} วัน"
            }
            session["concession_ladder"].append(ladder_entry)
            
        if concession.get("target_price"):
            ladder_entry = {
                "round": f"Counter {len(session.get('concession_ladder', [])) + 1}",
                "title": f"AI เสนอกลับ: {concession.get('strategy', 'Counter')}",
                "price": f"฿{concession.get('target_price', 0):,.2f}",
                "tag": concession.get("tactic_label", "Concession"),
                "color": "border-blue-400 bg-blue-50 text-blue-900 font-bold",
                "note": concession.get("rationale", "")
            }
            session["concession_ladder"].append(ladder_entry)
            
        # Store audit trace in session, stamped with model/cost telemetry so the
        # DB AuditTrail rows carry model_id, tier, latency, tokens and tco_score.
        if "audit_trace" in agent_result:
            session["audit_traces"].append({
                "timestamp": time.time(),
                "time": now_time,
                "trace": agent_result["audit_trace"],
                # --- additive auditability metadata (Pillar 4) ---
                "model_id": model_meta.get("model_id"),
                "tier": model_meta.get("tier"),
                "latency_ms": model_meta.get("latency_ms"),
                "input_tokens": model_meta.get("input_tokens"),
                "output_tokens": model_meta.get("output_tokens"),
                "tco_score": tco_score,
                "status": model_meta.get("status"),
            })

        # Save updated session
        session_repository.save_session(deal_key, vendor_id, session)

        return {
            "status": "success",
            "reply": agent_reply,
            "tactic": agent_tactic,
            "parsed_intent": parsed_intent,
            "tco_data": tco_data,
            "concession": concession,
            "audit_trace": agent_result.get("audit_trace", []),
            "messages": session["messages"],
            "ladder": session["concession_ladder"],
            # --- additive: surfaced for governance/cost dashboards ---
            "arbitration": arbitration,
            "model_meta": model_meta,
        }

negotiation_service = BedrockNegotiationService()
