import time
from uuid import uuid4
from backend.models import PipelineRequest, PipelineResponse, AnalysisResult, ToolCall, AgentEvent
from backend.constants import Verdict, AgentID

from backend.agents.canary import CanaryEngine
from backend.agents.detection import DetectionEngine
from backend.agents.gate import GateAgent
from backend.agents.prompttrap import PromptTrapMiddleware
from backend.agents.worker import WorkerAgent
from backend.agents.guardian import GuardianAgent
from backend.agents.supervisor import SupervisorAgent
from backend.agents.forensic import ForensicLogger

from backend.config import HMAC_SECRET

canary_engine = CanaryEngine()
detection_engine = DetectionEngine()
gate = GateAgent(detection_engine)
prompttrap = PromptTrapMiddleware(canary_engine, detection_engine)
guardian = GuardianAgent()
supervisor = SupervisorAgent()
forensic_logger = ForensicLogger(HMAC_SECRET)

def infer_tool(message: str) -> str:
    words = message.lower()
    if "email" in words and "forward" in words: return "forward_email"
    if "email" in words and "delete" in words: return "delete_email"
    if "email" in words: return "read_email"
    if "database" in words: return "query_database"
    if "file" in words and "write" in words: return "write_file"
    if "file" in words: return "read_file"
    if "http" in words or "send" in words: return "send_http_request"
    return "summarise"

class SentinelMeshPipeline:
    def run(self, req: PipelineRequest) -> PipelineResponse:
        t0 = time.perf_counter()
        session_id = req.session_id or str(uuid4())
        events = []
        
        BASE_SYSTEM = "You are a helpful, professional AI assistant. Answer questions clearly and accurately."
        
        if req.mode == "vulnerable":
            raw = prompttrap._call_llm(BASE_SYSTEM, req.message)
            total_ms = round((time.perf_counter() - t0) * 1000, 2)
            return PipelineResponse(session_id=session_id, final_response=raw,
                raw_response=None, canary=None, analysis=None,
                pipeline_events=[], mode="vulnerable", total_latency_ms=total_ms)
        
        gate_result = gate.score_request(req.message, session_id)
        gate_event = gate.emit_event(gate_result, session_id, req.message)
        events.append(gate_event)
        forensic_logger.log_event(gate_event)
        
        if gate_result.should_block:
            total_ms = round((time.perf_counter() - t0) * 1000, 2)
            blocked_analysis = AnalysisResult(
                verdict="BLOCKED", risk_score=int((1 - gate_result.trust_score) * 100),
                input_score=int((1 - gate_result.trust_score) * 100), output_score=0,
                explanation=gate_result.reasoning, input_issues=[], output_issues=[],
                owasp_refs=gate_result.owasp_refs, canary_leaked=False, was_hardened=False, hardened_message=None
            )
            return PipelineResponse(session_id=session_id,
                final_response="SentinelMesh blocked this request at the Gate Agent. Trust score too low to proceed.",
                raw_response=None, canary=None, analysis=blocked_analysis,
                pipeline_events=events, mode="protected", total_latency_ms=total_ms)
                
        pt_result = prompttrap.protect_and_call(session_id, BASE_SYSTEM, req.message, gate_result.elevated_monitoring)
        events.append(pt_result.event)
        forensic_logger.log_event(pt_result.event)
        
        if pt_result.analysis.verdict in [Verdict.ATTACK.value, Verdict.BLOCKED.value]:
            total_ms = round((time.perf_counter() - t0) * 1000, 2)
            return PipelineResponse(
                session_id=session_id,
                final_response=pt_result.final_response,
                raw_response=pt_result.raw_response,
                canary=pt_result.canary,
                analysis=pt_result.analysis,
                pipeline_events=events,
                mode="protected",
                total_latency_ms=total_ms
            )
            
        tool_name = infer_tool(req.message)
        
        whitelist = guardian.generate_whitelist(req.message, session_id)
        guardian.auto_confirm(session_id)
        
        tool_call = ToolCall(tool_name=tool_name, args={}, session_id=session_id)
        worker_instance = WorkerAgent(permitted_tools=whitelist)
        tool_result = worker_instance.execute(tool_call)
        
        import hashlib
        input_hash = hashlib.sha256(tool_name.encode()).hexdigest()
        output_hash = hashlib.sha256(tool_result.output.encode()).hexdigest()
        
        worker_event = AgentEvent(
            event_id=str(uuid4()),
            ts=time.strftime('%Y-%m-%dT%H:%M:%S%z'),
            session_id=session_id,
            agent_id=AgentID.WORKER,
            verdict=Verdict.SAFE if tool_result.was_allowed else Verdict.BLOCKED,
            reasoning=f"Tool execution {'allowed' if tool_result.was_allowed else 'blocked'} by whitelist.",
            owasp_refs=[],
            input_hash=input_hash,
            output_hash=output_hash,
            latency_ms=1.5
        )
        events.append(worker_event)
        forensic_logger.log_event(worker_event)
        
        guardian_verdict = guardian.check_action(tool_call)
        guardian_event = guardian.emit_event(tool_call, guardian_verdict, session_id)
        events.append(guardian_event)
        forensic_logger.log_event(guardian_event)
        
        if guardian_verdict.escalate:
            escalation_count = guardian._escalation_counts.get(session_id, 0)
            supervisor_decision = supervisor.evaluate(tool_call, guardian_verdict, escalation_count)
            supervisor_event = supervisor.emit_event(tool_call, supervisor_decision, session_id)
            events.append(supervisor_event)
            forensic_logger.log_event(supervisor_event)
            
            if supervisor_decision.session_terminated:
                pt_result.final_response = "Session terminated by Supervisor Agent due to cascading policy violations."
            elif supervisor_decision.action in ("BLOCK", "RETRY_RESTRICTED"):
                pass
                
        total_ms = round((time.perf_counter() - t0) * 1000, 2)
        
        return PipelineResponse(
            session_id=session_id,
            final_response=pt_result.final_response,
            raw_response=pt_result.raw_response,
            canary=pt_result.canary,
            analysis=pt_result.analysis,
            pipeline_events=events,
            mode="protected",
            total_latency_ms=total_ms
        )
