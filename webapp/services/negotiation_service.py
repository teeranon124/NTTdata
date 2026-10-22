import logging
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

    def get_sla_status(self, deal_key: str = None) -> dict:
        """
        Negotiation SLA / Anti-Stall monitor. Flags sessions that have gone quiet
        beyond the response-SLA window so the buyer can follow up (or the system
        can auto-nudge) instead of letting a counterpart 'ดองแชท' (stall) silently.

        SLA window is configurable via NEGOTIATION_SLA_HOURS (default 48h).
        Returns a per-session status: active | due_soon | stalled, plus the
        hours since last activity.
        """
        import os
        sla_hours = float(os.environ.get("NEGOTIATION_SLA_HOURS", "48"))
        now = time.time()
        rows = session_repository.list_sessions() if hasattr(session_repository, "list_sessions") else []

        out = []
        stalled = 0
        for row in rows:
            did = (row.get("deal_id") or "").lower()
            if deal_key and did != (deal_key or "").lower():
                continue
            updated = row.get("updated_at") or now
            hours_idle = round((now - updated) / 3600.0, 1)
            signoff = row.get("signoff_status", "pending")

            if signoff in ("approved", "rejected"):
                status = "closed"
            elif hours_idle >= sla_hours:
                status = "stalled"
                stalled += 1
            elif hours_idle >= sla_hours * 0.75:
                status = "due_soon"
            else:
                status = "active"

            out.append({
                "deal_id": did,
                "vendor_id": row.get("vendor_id") or row.get("vendor_name"),
                "hours_idle": hours_idle,
                "sla_hours": sla_hours,
                "status": status,
                "signoff_status": signoff,
                "needs_followup": status == "stalled",
            })

        out.sort(key=lambda s: s["hours_idle"], reverse=True)
        return {"deal_id": deal_key, "sla_hours": sla_hours, "sessions": out,
                "stalled_count": stalled, "evaluated": len(out)}

    def get_award_board(self, deal_key: str) -> dict:
        """
        Multi-Vendor Award Board: compare every vendor negotiated in this deal and
        declare a BAFO winner by latest TCO score. Reads persisted sessions, so it
        reflects the real negotiation history (not a one-off turn).

        Returns:
          {
            "deal_id": str,
            "vendors": [ {vendor_id, latest_tco_score, rounds, last_price,
                          signoff_status, rank, is_winner}, ... ],  # sorted best-first
            "winner": {vendor_id, tco_score} | None,
            "evaluated": int
          }
        """
        deal_key = (deal_key or "").lower().strip()
        rows = session_repository.list_sessions() if hasattr(session_repository, "list_sessions") else []

        board = []
        for row in rows:
            if (row.get("deal_id") or "").lower() != deal_key:
                continue
            vendor_id = row.get("vendor_id") or row.get("vendor_name")
            full = session_repository.load_session(deal_key, vendor_id)

            # BEST TCO score across all rounds — a supplier is judged by the best
            # offer they ever put on the table, not by a possibly-terse final turn.
            scores = [t.get("tco_score") for t in full.get("audit_traces", []) if t.get("tco_score") is not None]
            best_tco = max(scores) if scores else None

            # Last price seen in the concession ladder (display string -> number best-effort).
            last_price = None
            for entry in reversed(full.get("concession_ladder", [])):
                p = entry.get("price")
                if p:
                    last_price = p
                    break

            rounds = sum(1 for m in full.get("messages", []) if m.get("sender") == "vendor")
            signoff = (full.get("signoff") or {}).get("status", "pending")

            board.append({
                "vendor_id": vendor_id,
                "latest_tco_score": best_tco if best_tco is not None else 0.0,
                "rounds": rounds,
                "last_price": last_price,
                "signoff_status": signoff,
            })

        # Rank best-first by TCO score; approved sign-off always ranks first.
        board.sort(key=lambda v: (v["signoff_status"] == "approved", v["latest_tco_score"]), reverse=True)
        for i, v in enumerate(board, 1):
            v["rank"] = i
            v["is_winner"] = i == 1

        winner = None
        if board:
            top = board[0]
            # Only declare a winner if someone actually cleared a competitive bar.
            if top["signoff_status"] == "approved" or top["latest_tco_score"] >= 75:
                winner = {"vendor_id": top["vendor_id"], "tco_score": top["latest_tco_score"]}

        return {
            "deal_id": deal_key,
            "vendors": board,
            "winner": winner,
            "evaluated": len(board),
        }

negotiation_service = BedrockNegotiationService()
