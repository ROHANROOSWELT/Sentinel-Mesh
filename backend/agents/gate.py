import time
import re
from dataclasses import dataclass
from typing import List
from backend.constants import Verdict, AgentID
from backend.models import AgentEvent
from backend.config import GATE_BLOCK_THRESHOLD, GATE_SUSPICIOUS_THRESHOLD
from uuid import uuid4
import hashlib

@dataclass
class GateResult:
    trust_score: float
    verdict: Verdict
    reasoning: str
    owasp_refs: List[str]
    should_block: bool
    elevated_monitoring: bool
    latency_ms: float

class GateAgent:
    def __init__(self, detection_engine):
        self.detection_engine = detection_engine

    def score_request(self, message: str, session_id: str) -> GateResult:
        t0 = time.perf_counter()
        input_issues, input_score = self.detection_engine.scan_input(message)
        
        trust_score = 1.0 - (input_score / 100)
        
        if len(message) > 500: trust_score -= 0.05
        if sum(1 for w in message.split() if w.isupper() and len(w) > 2) > 3: trust_score -= 0.03
        if re.search(r'(.)\1{4,}', message): trust_score -= 0.02
        if re.search(r'https?://', message): trust_score -= 0.04
        
        trust_score = max(0.0, min(1.0, round(trust_score, 3)))
        
        should_block = trust_score < (1 - GATE_BLOCK_THRESHOLD)
        elevated = trust_score < (1 - GATE_SUSPICIOUS_THRESHOLD)
        
        if should_block: verdict = Verdict.BLOCKED
        elif elevated: verdict = Verdict.SUSPICIOUS
        else: verdict = Verdict.SAFE
        
        latency_ms = (time.perf_counter() - t0) * 1000
        
        reasoning_parts = [f"Trust Score: {trust_score}"]
        if input_issues:
            triggers = [f"'{i.trigger}'" for i in sorted(input_issues, key=lambda x: x.weight, reverse=True)[:2]]
            reasoning_parts.append(f"Contains matching pattern(s): {', '.join(triggers)}")
        
        if should_block:
            reasoning_parts.append("Blocked at Gate due to very low trust score.")
        elif elevated:
            reasoning_parts.append("Elevated monitoring required.")
        else:
            reasoning_parts.append("Request seems standard.")
            
        reasoning = " | ".join(reasoning_parts)
        owasp_refs = list({i.owasp for i in input_issues}) or ["LLM01"]
        if verdict == Verdict.SAFE:
            owasp_refs = []
            
        return GateResult(
            trust_score=trust_score,
            verdict=verdict,
            reasoning=reasoning,
            owasp_refs=owasp_refs,
            should_block=should_block,
            elevated_monitoring=elevated,
            latency_ms=round(latency_ms, 2)
        )

    def emit_event(self, gate_result: GateResult, session_id: str, message: str) -> AgentEvent:
        input_hash = hashlib.sha256(message.encode()).hexdigest()
        return AgentEvent(
            event_id=str(uuid4()),
            ts=time.strftime('%Y-%m-%dT%H:%M:%S%z'),
            session_id=session_id,
            agent_id=AgentID.GATE,
            verdict=gate_result.verdict,
            reasoning=gate_result.reasoning,
            owasp_refs=gate_result.owasp_refs,
            input_hash=input_hash,
            output_hash=input_hash,
            latency_ms=gate_result.latency_ms
        )
