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

session_repository = SessionRepository()
