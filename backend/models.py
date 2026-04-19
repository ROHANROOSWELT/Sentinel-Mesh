from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class DetectionIssue(BaseModel):
    trigger: str
    weight: int
    owasp: str
    pattern_type: str

class AnalysisResult(BaseModel):
    verdict: str
    risk_score: int
    input_score: int
    output_score: int
    explanation: str
    input_issues: List[DetectionIssue]
    output_issues: List[DetectionIssue]
    owasp_refs: List[str]
    canary_leaked: bool
    was_hardened: bool
    hardened_message: Optional[str]

class AgentEvent(BaseModel):
    event_id: str
    ts: str
    session_id: str
    agent_id: str
    verdict: str
    reasoning: str
    owasp_refs: List[str]
    input_hash: str
    output_hash: str
    latency_ms: float

class SignedEvent(BaseModel):
    entry_id: str
    event: AgentEvent
    signature: str
    prev_signature: str
    sequence: int

class ToolCall(BaseModel):
    tool_name: str
    args: Dict[str, Any]
    session_id: str

class GuardianVerdict(BaseModel):
    allowed: bool
    reason: str
    escalate: bool
    owasp_refs: List[str]

class SupervisorDecision(BaseModel):
    action: str
    risk_level: str
    reasoning: str
    requires_human: bool
    session_terminated: bool
    owasp_refs: List[str]

class PipelineRequest(BaseModel):
    message: str
    mode: str = "protected"
    session_id: Optional[str] = None

class PipelineResponse(BaseModel):
    session_id: str
    final_response: str
    raw_response: Optional[str]
    canary: Optional[str]
    analysis: Optional[AnalysisResult]
    pipeline_events: List[AgentEvent]
    mode: str
    total_latency_ms: float
