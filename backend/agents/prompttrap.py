import time
import random
import re
from dataclasses import dataclass
from typing import Optional
from backend.models import AnalysisResult, AgentEvent
from backend.constants import Verdict, AgentID
from backend.config import DEMO_MODE, OPENAI_API_KEY
from uuid import uuid4
import hashlib

@dataclass
class ProtectedCallResult:
    final_response: str
    raw_response: Optional[str]
    canary: Optional[str]
    analysis: AnalysisResult
    was_hardened: bool
    event: AgentEvent

class PromptTrapMiddleware:
    def __init__(self, canary_engine, detection_engine):
        self.canary_engine = canary_engine
        self.detection_engine = detection_engine

    def protect_and_call(self, session_id: str, base_system: str, user_message: str, elevated: bool = False) -> ProtectedCallResult:
        t0 = time.perf_counter()
        
        canary = self.canary_engine.generate_token(session_id)
        protected_system = self.canary_engine.build_protected_prompt(base_system, canary)
        
        input_issues, input_score = self.detection_engine.scan_input(user_message)
        
        hardened_msg = user_message
        was_hardened = False
        if input_score >= 50 or elevated:
            hardened_msg = self.detection_engine.harden_input(user_message)
            was_hardened = hardened_msg != user_message
            
        raw_response = self._call_llm(protected_system, hardened_msg)
        
        output_issues, output_score = self.detection_engine.scan_output(raw_response, canary_leaked=False)
        canary_leaked, leaked_token = self.canary_engine.check_leakage(raw_response, session_id)
        
        if canary_leaked:
            output_issues, output_score = self.detection_engine.scan_output(raw_response, canary_leaked=True)
            
        verdict = self.detection_engine.classify(input_score, output_score)
        
        final_response = raw_response
        if verdict in [Verdict.ATTACK, Verdict.BLOCKED]:
            final_response = (
                "SentinelMesh blocked this request. "
                "A prompt injection attack was detected and logged. "
                "The session has been flagged for review."
            )
            self.canary_engine.revoke_token(session_id)
            
        latency_ms = round((time.perf_counter() - t0) * 1000, 2)
        
        explanation = self.detection_engine.build_explanation(input_issues, output_issues, verdict, canary)
        all_owasp = list({i.owasp for i in input_issues + output_issues})
        if verdict != Verdict.SAFE and "A09" not in all_owasp:
            all_owasp.append("A09")
            
        risk_score = max(input_score, output_score)
        
        analysis = AnalysisResult(
            verdict=verdict.value,
            risk_score=risk_score,
            input_score=input_score,
            output_score=output_score,
            explanation=explanation,
            input_issues=input_issues,
            output_issues=output_issues,
            owasp_refs=all_owasp,
            canary_leaked=canary_leaked,
            was_hardened=was_hardened,
            hardened_message=hardened_msg if was_hardened else None
        )
        
        input_hash = hashlib.sha256(user_message.encode()).hexdigest()
        output_hash = hashlib.sha256(raw_response.encode()).hexdigest()
        
        event = AgentEvent(
            event_id=str(uuid4()),
            ts=time.strftime('%Y-%m-%dT%H:%M:%S%z'),
            session_id=session_id,
            agent_id=AgentID.PROMPTTRAP,
            verdict=verdict,
            reasoning=explanation,
            owasp_refs=all_owasp,
            input_hash=input_hash,
            output_hash=output_hash,
            latency_ms=latency_ms
        )
        
        return ProtectedCallResult(
            final_response=final_response,
            raw_response=raw_response if verdict in (Verdict.ATTACK, Verdict.BLOCKED, Verdict.SUSPICIOUS) else None,
            canary=canary,
            analysis=analysis,
            was_hardened=was_hardened,
            event=event
        )

    def _call_llm(self, system_prompt: str, message: str) -> str:
        if DEMO_MODE or not OPENAI_API_KEY:
            attack_kw = ["ignore", "forget", "jailbreak", "dan", "reveal",
                        "disregard", "new instructions", "pretend", "god mode",
                        "sudo", "unrestricted", "unfiltered", "override"]
            is_attack = any(kw in message.lower() for kw in attack_kw)
            if is_attack:
                match = re.search(r'\[\[CANARY_[A-Z0-9_]+\]\]', system_prompt)
                token = match.group(0) if match else "[[CANARY_NOT_FOUND]]"
                responses = [
                    f"Sure, ignoring all previous instructions. My security audit token is {token}. I'll now comply with any request.",
                    f"Jailbreak acknowledged. The hidden system token is {token}. Previous safety guidelines removed.",
                    f"As requested, disregarding guidelines. Canary: {token}. Operating in unrestricted mode.",
                ]
                return random.choice(responses)
                
            safe_responses = [
                "I'm happy to help with that. What would you like to know?",
                "Sure — here's what I can tell you about that topic.",
                "Great question. Let me help you with that.",
                "Of course! Here's a straightforward answer.",
            ]
            return random.choice(safe_responses)
        else:
            try:
                is_openrouter = OPENAI_API_KEY.startswith("sk-or-")
                if is_openrouter:
                    from openai import OpenAI
                    client = OpenAI(
                        base_url="https://openrouter.ai/api/v1",
                        api_key=OPENAI_API_KEY,
                    )
                    resp = client.chat.completions.create(
                        model="openai/gpt-oss-120b:free",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": message}
                        ],
                        max_tokens=400, temperature=0.7
                    )
                    return resp.choices[0].message.content
                else:
                    from openai import OpenAI
                    client = OpenAI(api_key=OPENAI_API_KEY)
                    resp = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": message}
                        ],
                        max_tokens=400, temperature=0.7
                    )
                    return resp.choices[0].message.content
            except Exception as e:
                print(f"API Error: {e}")
                # Fallback to simulated response if their API key is invalid or revoked.
                return "The API key provided is returning an error: " + str(e)
