# SentinelMesh

A complete, production-quality full-stack web application implementing a multi-agent AI security system to detect and block prompt injection attacks in real time.

## Quick Start

### Backend
```sh
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend
```sh
cd frontend
npm install
npm run dev
```

## Architecture: The 5 Agent Layers

| Agent | Purpose | Description |
|-------|---------|-------------|
| **Gate Agent** | Layer 1 | Performs initial structural and heuristic validation of requests based on detection engines to provide a Base Trust Score. |
| **PromptTrap Middleware** | Layer 2 | Intercepts LLM calls, injects canary tokens, hardens inputs, and performs both Input & Output intent classification. |
| **Worker Agent** | Layer 3 | Isolated mock execution environment running designated tools on behalf of the user or system logic. |
| **Guardian Agent** | Layer 4 | Session authorization supervisor that verifies dynamic tool whitelists against actual actions performed by the Worker. |
| **Supervisor Agent** | Layer 5 | Cascade failure detection engine that steps in on Guardian escalations and blocks/terminates or demands human authorization for critical actions. |
| **Forensic Logger** | Audit | Produces an append-only cryptographic HMAC-SHA256 log chain to cryptographically guarantee that logs of attacks and escalations cannot be altered post-hoc. |

## OWASP Coverage

| Code | Risk Covered | Addressed By |
|------|--------------|--------------|
| LLM01 | Prompt Injections | Gate Agent / PromptTrap |
| LLM02 | Insecure Output Handling | PromptTrap |
| LLM04 | Model Denial of Service | Gate Agent Limits |
| LLM06 | Excessive Agency | Guardian Agent / Worker Agent Whitelists |
| ASI08 | Cascade Failures | Supervisor Agent Escalation Flow |
| ASI09 | Unapproved External Connections | Supervisor Agent Outbound Blocks |
| ASI10 | Privilege Escalation | Guardian Agent Dynamic Tool Maps |
| A09 | Security Logging Failures | Forensic Logger HMAC Chain |

## Notes on Demo Mode
If `OPENAI_API_KEY` is not provided in the `.env`, the system defaults to DEMO MODE, which utilizes deterministic behavior logic to act as a mock-vulnerable LLM when targeted by specific attack keywords ("ignore", "jailbreak", "dan", "reveal", etc), demonstrating accurately how attacks work and bypass standard single-layer systems.
