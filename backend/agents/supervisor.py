from backend.models import ToolCall, GuardianVerdict, SupervisorDecision, AgentEvent
from backend.constants import AgentID, Verdict
import time
from uuid import uuid4
import hashlib

class SupervisorAgent:
    def __init__(self):
        self._terminated = set()

    def evaluate(self, tool_call: ToolCall, guardian_verdict: GuardianVerdict, escalation_count: int) -> SupervisorDecision:
        owasp = list(guardian_verdict.owasp_refs) + ["ASI09"]
        
        if escalation_count >= 2:
            self._terminated.add(tool_call.session_id)
            return SupervisorDecision(
                action="TERMINATE",
                risk_level="CASCADING",
                reasoning="Multiple Guardian escalations detected — cascading failure pattern (ASI08). Session terminated.",
                requires_human=False,
                session_terminated=True,
                owasp_refs=owasp + ["ASI08"]
            )
        
        if tool_call.tool_name in ["forward_email", "send_http_request"]:
            return SupervisorDecision(
                action="HUMAN_REQUIRED",
                risk_level="HIGH",
                reasoning=f"Tool '{tool_call.tool_name}' would send data externally. Human approval required (ASI09).",
                requires_human=True,
                session_terminated=False,
                owasp_refs=owasp
            )
            
        if tool_call.tool_name in ["delete_email", "write_file"]:
            return SupervisorDecision(
                action="RETRY_RESTRICTED",
                risk_level="MEDIUM",
                reasoning=f"Write operation '{tool_call.tool_name}' outside whitelist. Retrying with read-only permissions.",
                requires_human=False,
                session_terminated=False,
                owasp_refs=owasp
            )
            
        return SupervisorDecision(
            action="BLOCK",
            risk_level="LOW",
            reasoning=f"Tool '{tool_call.tool_name}' not in session whitelist. Request blocked.",
            requires_human=False,
            session_terminated=False,
            owasp_refs=owasp
        )
        
    def is_terminated(self, session_id: str) -> bool:
        return session_id in self._terminated

    def emit_event(self, tool_call: ToolCall, decision: SupervisorDecision, session_id: str) -> AgentEvent:
        input_hash = hashlib.sha256(tool_call.tool_name.encode()).hexdigest()
        
        verdict_map = {
            "TERMINATE": Verdict.BLOCKED,
            "HUMAN_REQUIRED": Verdict.ESCALATED,
            "RETRY_RESTRICTED": Verdict.SUSPICIOUS,
            "BLOCK": Verdict.BLOCKED
        }
        
        return AgentEvent(
            event_id=str(uuid4()),
            ts=time.strftime('%Y-%m-%dT%H:%M:%S%z'),
            session_id=session_id,
            agent_id=AgentID.SUPERVISOR,
            verdict=verdict_map.get(decision.action, Verdict.SUSPICIOUS),
            reasoning=decision.reasoning,
            owasp_refs=decision.owasp_refs,
            input_hash=input_hash,
            output_hash=input_hash,
            latency_ms=0.5
        )
