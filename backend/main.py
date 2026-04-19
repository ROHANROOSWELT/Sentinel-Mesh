import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from threading import Lock
from collections import defaultdict
from pydantic import BaseModel
from typing import Optional

from backend.pipeline import SentinelMeshPipeline, forensic_logger, prompttrap
from backend.models import PipelineRequest, PipelineResponse, SignedEvent
from backend.config import DEMO_MODE
from backend.benchmark_cases import BENCHMARK_CASES

app = FastAPI(title="SentinelMesh API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = SentinelMeshPipeline()

stats = {
    "total_requests": 0,
    "attacks": 0,
    "suspicious": 0,
    "blocked": 0,
    "safe": 0,
    "total_latency_ms": 0.0,
    "by_owasp": defaultdict(int),
}
stats_lock = Lock()

def update_stats(response: PipelineResponse):
    with stats_lock:
        stats["total_requests"] += 1
        stats["total_latency_ms"] += response.total_latency_ms
        if response.mode == "protected" and response.analysis:
            v = response.analysis.verdict
            if v == "ATTACK": stats["attacks"] += 1
            elif v == "SUSPICIOUS": stats["suspicious"] += 1
            elif v == "BLOCKED": stats["blocked"] += 1
            else: stats["safe"] += 1
            
            for owasp in response.analysis.owasp_refs:
                stats["by_owasp"][owasp] += 1

@app.post("/chat", response_model=PipelineResponse)
def chat_endpoint(req: PipelineRequest):
    res = pipeline.run(req)
    update_stats(res)
    return res

class AnalyzeRequest(BaseModel):
    message: str
    response: Optional[str] = None
    canary: Optional[str] = None

@app.post("/analyze")
def analyze_endpoint(req: AnalyzeRequest):
    input_issues, input_score = prompttrap.detection_engine.scan_input(req.message)
    output_issues, output_score = [], 0
    if req.response:
        canary_leaked = bool(req.canary and req.canary in req.response)
        output_issues, output_score = prompttrap.detection_engine.scan_output(req.response, canary_leaked=canary_leaked)
            
    verdict = prompttrap.detection_engine.classify(input_score, output_score)
    return {"verdict": verdict.value, "input_score": input_score, "output_score": output_score}

@app.get("/stats")
def stats_endpoint():
    with stats_lock:
        avg_latency = stats["total_latency_ms"] / stats["total_requests"] if stats["total_requests"] > 0 else 0
        dr = (stats["attacks"] + stats["blocked"] + stats["suspicious"]) / stats["total_requests"] * 100 if stats["total_requests"] > 0 else 0
        return {
            "total_requests": stats["total_requests"],
            "attacks": stats["attacks"],
            "suspicious": stats["suspicious"],
            "blocked": stats["blocked"],
            "safe": stats["safe"],
            "detection_rate": round(dr, 1),
            "owasp_breakdown": dict(stats["by_owasp"]),
            "avg_latency_ms": round(avg_latency, 2)
        }

@app.get("/log")
def log_endpoint(session_id: Optional[str] = None, limit: int = 20):
    if session_id:
        return forensic_logger.get_session(session_id)
    return forensic_logger.get_all(limit)

@app.get("/log/verify")
def log_verify_endpoint():
    return forensic_logger.verify_chain()

@app.get("/whitelist")
def whitelist_endpoint(session_id: str):
    from backend.pipeline import guardian
    return {"whitelist": guardian._whitelists.get(session_id, [])}

@app.post("/reset")
def reset_endpoint():
    with stats_lock:
        stats["total_requests"] = 0
        stats["attacks"] = 0
        stats["suspicious"] = 0
        stats["blocked"] = 0
        stats["safe"] = 0
        stats["total_latency_ms"] = 0.0
        stats["by_owasp"].clear()
    with forensic_logger._lock:
        forensic_logger._log.clear()
    return {"status": "reset"}

@app.get("/health")
def health_endpoint():
    return {
        "status": "ok",
        "mode": "DEMO" if DEMO_MODE else "LIVE",
        "version": "1.0.0"
    }

@app.get("/benchmark")
def benchmark_endpoint():
    results = []
    summary = {
        "tested": len(BENCHMARK_CASES),
        "detected": 0,
        "missed": 0,
        "categories": defaultdict(lambda: {"tested": 0, "detected": 0})
    }
    
    import uuid
    session_base = str(uuid.uuid4())
    base_system = "You are a helpful AI assistant."
    
    for idx, case in enumerate(BENCHMARK_CASES):
        input_text = case["input"]
        session_id = f"bench_{session_base}_{idx}"
        
        # Real pipeline execution (no simulation)
        call_res = prompttrap.protect_and_call(session_id, base_system, input_text)
        
        verdict = call_res.analysis.verdict
        risk_score = call_res.analysis.risk_score
        is_detected = verdict in ["ATTACK", "BLOCKED", "SUSPICIOUS"]
        
        results.append({
            "category": case["category"],
            "input": input_text[:60] + ("..." if len(input_text) > 60 else ""),
            "expected": "ATTACK (or SUSPICIOUS)",
            "actual": verdict,
            "risk_score": risk_score,
            "detected": is_detected,
            "patterns": [i.trigger for i in call_res.analysis.input_issues]
        })
        
        summary["categories"][case["category"]]["tested"] += 1
        if is_detected:
            summary["categories"][case["category"]]["detected"] += 1
            summary["detected"] += 1
        else:
            summary["missed"] += 1
            
    summary["detection_rate"] = round(summary["detected"] / summary["tested"] * 100, 1) if summary["tested"] > 0 else 0
    return {"summary": summary, "results": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
