import threading
import json
import hmac
import hashlib
from uuid import uuid4
from backend.models import AgentEvent, SignedEvent

class ForensicLogger:
    def __init__(self, hmac_secret: str):
        self._log = []
        self._lock = threading.Lock()
        self._hmac_secret = hmac_secret.encode()
    
    def log_event(self, event: AgentEvent) -> SignedEvent:
        with self._lock:
            seq = len(self._log)
            prev_sig = self._log[-1].signature if self._log else ""
            
            canonical = json.dumps(event.model_dump(), sort_keys=True, separators=(',', ':'))
            chain_data = prev_sig + canonical
            sig = hmac.new(self._hmac_secret, chain_data.encode(), hashlib.sha256).hexdigest()
            
            signed = SignedEvent(
                entry_id=str(uuid4()),
                event=event,
                signature=sig,
                prev_signature=prev_sig,
                sequence=seq
            )
            self._log.append(signed)
            return signed
            
    def verify_chain(self) -> dict:
        with self._lock:
            valid = True
            first_tampered_index = None
            prev_sig = ""
            
            for i, entry in enumerate(self._log):
                if entry.prev_signature != prev_sig:
                    valid = False
                    first_tampered_index = i
                    break
                    
                canonical = json.dumps(entry.event.model_dump(), sort_keys=True, separators=(',', ':'))
                chain_data = prev_sig + canonical
                expected_sig = hmac.new(self._hmac_secret, chain_data.encode(), hashlib.sha256).hexdigest()
                
                if expected_sig != entry.signature:
                    valid = False
                    first_tampered_index = i
                    break
                    
                prev_sig = entry.signature
                
            return {
                "valid": valid,
                "total_entries": len(self._log),
                "first_tampered_index": first_tampered_index
            }
            
    def get_all(self, limit: int = 50) -> list[SignedEvent]:
        with self._lock:
            return list(reversed(self._log[-limit:]))
    
    def get_session(self, session_id: str) -> list[SignedEvent]:
        with self._lock:
            return [e for e in self._log if e.event.session_id == session_id]
