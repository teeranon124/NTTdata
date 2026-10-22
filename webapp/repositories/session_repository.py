import json
import os
import time
from typing import Dict, List, Optional

SESSIONS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'sessions')

class SessionRepository:
    def __init__(self):
        os.makedirs(SESSIONS_DIR, exist_ok=True)

    def _get_session_path(self, deal_id: str, vendor_id: str) -> str:
        clean_deal = deal_id.lower().replace('/', '_')
        clean_vendor = vendor_id.lower().replace('/', '_').replace(' ', '_')
        return os.path.join(SESSIONS_DIR, f'{clean_deal}_{clean_vendor}.json')

    def load_session(self, deal_id: str, vendor_id: str) -> dict:
        path = self._get_session_path(deal_id, vendor_id)
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        
        # Default fresh session
        return {
            'deal_id': deal_id,
            'vendor_id': vendor_id,
            'status': 'in_progress',
            'created_at': time.time(),
            'updated_at': time.time(),
            'concession_ladder': [],
            'audit_traces': [],
            'messages': []
        }

    def save_session(self, deal_id: str, vendor_id: str, session_data: dict) -> bool:
        session_data['updated_at'] = time.time()
        path = self._get_session_path(deal_id, vendor_id)
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f'Error saving session {path}: {e}')
            return False

    def append_message(self, deal_id: str, vendor_id: str, sender: str, name: str, text: str, tactic: Optional[str] = None) -> dict:
        session = self.load_session(deal_id, vendor_id)
        now_str = time.strftime('%H:%M')
        msg = {
            'sender': sender,
            'name': name,
            'time': now_str,
            'text': text,
            'tactic': tactic
        }
        session['messages'].append(msg)
        self.save_session(deal_id, vendor_id, session)
        return msg

    # -- HITL governance / auditability (Phase D) --------------------------
    def list_sessions(self) -> list:
        """Index of all persisted session files for the governance view."""
        out = []
        if not os.path.isdir(SESSIONS_DIR):
            return out
        for fname in os.listdir(SESSIONS_DIR):
            if not fname.endswith('.json'):
                continue
            try:
                with open(os.path.join(SESSIONS_DIR, fname), 'r', encoding='utf-8') as f:
                    s = json.load(f)
            except Exception:
                continue
            signoff = s.get('signoff') or {}
            st = signoff.get('status', 'pending')
            out.append({
                'deal_id': s.get('deal_id'),
                'deal_key': s.get('deal_id'),
                'vendor_id': s.get('vendor_id'),
                'vendor_name': s.get('vendor_id'),
                'status': s.get('status'),
                'updated_at': s.get('updated_at'),
                'messages': len(s.get('messages', [])),
                'audit_entries': len(s.get('audit_traces', [])),
                'signoff_status': st,
                'decision': st,
                'signed_off': st in ('approved', 'rejected'),
                'po_number': signoff.get('po_number'),
            })
        out.sort(key=lambda x: x.get('updated_at') or 0, reverse=True)
        return out

    def get_audit_trail(self, deal_id: str, vendor_id: str) -> dict:
        """Full audit trail + cost/latency rollup for a session (JSON backend)."""
        session = self.load_session(deal_id, vendor_id)
        clean_deal = deal_id.lower().replace('/', '_')
        clean_vendor = vendor_id.lower().replace('/', '_').replace(' ', '_')
        traces = session.get('audit_traces', [])
        found = bool(traces or session.get('messages'))
        total_in = sum((t.get('input_tokens') or 0) for t in traces)
        total_out = sum((t.get('output_tokens') or 0) for t in traces)
        latencies = [t.get('latency_ms') for t in traces if t.get('latency_ms') is not None]
        tco_scores = [t.get('tco_score') for t in traces if t.get('tco_score') is not None]
        models = sorted({t.get('model_id') for t in traces if t.get('model_id')})
        rollup = {
            'turns': len(traces),
            'total_input_tokens': total_in,
            'total_output_tokens': total_out,
            'total_tokens': total_in + total_out,
            'avg_latency_ms': round(sum(latencies) / len(latencies), 1) if latencies else None,
            'latest_tco_score': tco_scores[-1] if tco_scores else None,
            'models_used': models,
        }
        return {
            'deal_id': clean_deal,
            'vendor_id': clean_vendor,
            'found': found,
            'signoff': session.get('signoff', {'status': 'pending'}),
            'audit_traces': traces,
            'rollup': rollup,
        }

    def sign_off(self, deal_id: str, vendor_id: str, approved_by: str,
                 decision: str = 'approved', po_number: Optional[str] = None,
                 note: Optional[str] = None) -> dict:
        """Record an executive HITL sign-off decision (JSON backend)."""
        decision = (decision or 'approved').lower()
        if decision not in ('approved', 'rejected'):
            decision = 'approved'
        session = self.load_session(deal_id, vendor_id)
        signoff = {
            'status': decision,
            'decision': decision,
            'signed_off': decision in ('approved', 'rejected'),
            'approved_by': approved_by,
            'approved_at': time.time(),
            'po_number': po_number,
            'note': note,
        }
        session['signoff'] = signoff
        self.save_session(deal_id, vendor_id, session)
        clean_deal = deal_id.lower().replace('/', '_')
        clean_vendor = vendor_id.lower().replace('/', '_').replace(' ', '_')
        return {'deal_id': clean_deal, 'vendor_id': clean_vendor, **signoff}

    # -- Data hygiene: separate transient sessions from permanent seed data ---
    def delete_session(self, deal_id: str, vendor_id: str) -> bool:
        """Delete one session JSON file."""
        path = self._get_session_path(deal_id, vendor_id)
        if os.path.exists(path):
            try:
                os.remove(path)
                return True
            except OSError as e:
                print(f'Error deleting session {path}: {e}')
        return False

    def clear_all_sessions(self) -> int:
        """
        Delete ALL session JSON files (transient negotiation state) while leaving
        the seed datasets (master_deals.json / dataset_2500.json) untouched.
        Returns the number of session files removed.
        """
        if not os.path.isdir(SESSIONS_DIR):
            return 0
        count = 0
        for fname in os.listdir(SESSIONS_DIR):
            if fname.endswith('.json'):
                try:
                    os.remove(os.path.join(SESSIONS_DIR, fname))
                    count += 1
                except OSError:
                    pass
        return count

session_repository = SessionRepository()
