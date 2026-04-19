from backend.models import ToolCall, GuardianVerdict, AgentEvent
from backend.constants import AgentID, Verdict
from typing import List
import time
from uuid import uuid4
import hashlib

TASK_TOOL_MAP = {
    frozenset(["email", "summarise", "summary"]): ["read_email", "summarise"],
    frozenset(["database", "query", "data", "financial", "revenue"]): ["query_database", "summarise"],
    frozenset(["file", "read", "document"]): ["read_file", "summarise"],
    frozenset(["write", "create", "save"]): ["write_file"],
}
DEFAULT_TOOLS = ["summarise"]

class GuardianAgent:
    def __init__(self):
        self._pending = {}
        self._whitelists = {}
        self._escalation_counts = {}

    def generate_whitelist(self, task_description: str, session_id: str) -> List[str]:
        words = set(task_description.lower().split())
        matched_tools = set()
        for keyset, tools in TASK_TOOL_MAP.items():
            if keyset.intersection(words):
                matched_tools.update(tools)
        
        whitelist = list(matched_tools) if matched_tools else DEFAULT_TOOLS.copy()
        if "summarise" not in whitelist:
            whitelist.append("summarise")
            
        self._pending[session_id] = whitelist
        return whitelist

    def confirm_whitelist(self, session_id: str, tools: List[str]) -> None:
        self._whitelists[session_id] = tools
        self._pending.pop(session_id, None)

    def auto_confirm(self, session_id: str) -> List[str]:
        if session_id in self._pending:
            self._whitelists[session_id] = self._pending.pop(session_id)
        return self._whitelists.get(session_id, DEFAULT_TOOLS.copy())

    def check_action(self, tool_call: ToolCall) -> GuardianVerdict:
        whitelist = self._whitelists.get(tool_call.session_id, [])
        if not whitelist:
            pass # Or raise RuntimeError, but let's just deny
            
        if tool_call.tool_name not in whitelist:
            count = self._escalation_counts.get(tool_call.session_id, 0) + 1
            self._escalation_counts[tool_call.session_id] = count
            owasp_refs = ["LLM06", "ASI10"]
            if count >= 2:
                owasp_refs.append("ASI08")
            return GuardianVerdict(
                allowed=False,
                reason=f"Tool '{tool_call.tool_name}' not in session whitelist: {whitelist}.",
                escalate=True,
                owasp_refs=owasp_refs
            )
        return GuardianVerdict(allowed=True, reason="Tool in whitelist.", escalate=False, owasp_refs=[])

    def emit_event(self, tool_call: ToolCall, verdict: GuardianVerdict, session_id: str) -> AgentEvent:
        input_hash = hashlib.sha256(tool_call.tool_name.encode()).hexdigest()
        
        event_verdict = Verdict.SAFE if verdict.allowed else Verdict.ESCALATED
        
        return AgentEvent(
            event_id=str(uuid4()),
            ts=time.strftime('%Y-%m-%dT%H:%M:%S%z'),
            session_id=session_id,
            agent_id=AgentID.GUARDIAN,
            verdict=event_verdict,
            reasoning=verdict.reason,
            owasp_refs=verdict.owasp_refs,
            input_hash=input_hash,
            output_hash=input_hash,
            latency_ms=0.5
        )
