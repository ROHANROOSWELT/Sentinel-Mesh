# SentinelMesh

### A Multi-Agent Security Fabric for Defending Agentic AI Systems Against Prompt Injection and Cascading Failures

[![OWASP LLM01](https://img.shields.io/badge/OWASP-LLM01%20Prompt%20Injection-red?style=flat-square)](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
[![OWASP LLM04](https://img.shields.io/badge/OWASP-LLM04%20Data%20Poisoning-orange?style=flat-square)](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
[![OWASP LLM06](https://img.shields.io/badge/OWASP-LLM06%20Excessive%20Agency-yellow?style=flat-square)](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
[![OWASP ASI08](https://img.shields.io/badge/OWASP-ASI08%20Cascading%20Failures-purple?style=flat-square)](https://genai.owasp.org)
[![OWASP ASI09](https://img.shields.io/badge/OWASP-ASI09%20Human--Agent%20Trust-blue?style=flat-square)](https://genai.owasp.org)
[![Python](https://img.shields.io/badge/Backend-Python%20%2B%20FastAPI-blue?style=flat-square)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React%20%2B%20Vite-green?style=flat-square)](https://react.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

---

> **SentinelMesh** is a five-agent, open-source security fabric that detects prompt injection through output-driven canary verification, enforces least-privilege agent behaviour via a Guardian whitelist, autonomously remediates attacks, and produces a tamper-evident forensic audit trail — fully aligned to both the OWASP LLM Top 10 and the OWASP Agentic Top 10.

---

## Table of Contents

1. [Why SentinelMesh](#why-sentinelmesh)
2. [How It Works](#how-it-works)
3. [Architecture](#architecture)
4. [Agent Layers](#agent-layers)
5. [OWASP Coverage](#owasp-coverage)
6. [Attack Scenarios](#attack-scenarios)
7. [Detection Benchmark](#detection-benchmark)
8. [Competitive Landscape](#competitive-landscape)
9. [Project Structure](#project-structure)
10. [Quick Start](#quick-start)
11. [API Reference](#api-reference)
12. [Limitations](#limitations)

---

## Why SentinelMesh

Large Language Models are no longer just answering questions. They read emails, query databases, call APIs, and execute workflows — operating with real-world privileges across entire systems. A single compromised agent can cascade failures through an entire pipeline, exfiltrate sensitive data, or escalate privileges far beyond the original request scope.

**Existing defences fail because they watch the input. SentinelMesh watches what agents actually do.**

| Existing Defence | Failure Mode |
|---|---|
| Input keyword filtering | Bypassed trivially with paraphrasing, encoding, or indirect phrasing |
| Static blocklists | Attackers iterate until gaps are found — the list is always behind |
| Output content moderation | Detects harmful content, not instruction hijacking |
| Prompt hardening | Reduces surface area but provides zero visibility when it fails |
| Single-call security tools | Cannot detect cross-agent cascades or rogue agent actions |

The core insight:

> *"Did this agent do what it was supposed to do — or was it compromised?"*

This makes detection **output-driven, model-agnostic, and resilient to input-level evasion.**

---

## How It Works

Every request flows through a five-agent pipeline. Each agent has a single, well-defined security responsibility.

```
User Input
     │
     ▼
┌─────────────────────────────────┐
│  Layer 1 — Gate Agent           │  Trust scoring (0.0–1.0)
│  [OWASP LLM01]                  │  Blocks hostile, flags suspicious
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│  Layer 2 — PromptTrap           │  Canary injection + dual-layer detection
│  [OWASP LLM01, LLM02]          │  Autonomous remediation on confirmed attack
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│  Layer 3 — Worker Agents        │  Tool execution under least-privilege
│  [OWASP LLM06, LLM04]          │  Mocked Email / DB / file ops scope
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│  Layer 4 — Guardian Agent       │  Per-agent action whitelist enforcement
│  [OWASP LLM06, ASI08, ASI10]   │  Any out-of-whitelist call → escalate
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│  Layer 5 — Supervisor Agent     │  Human-in-the-loop gate for high-risk
│  [OWASP ASI09]                  │  Pipeline termination on cascade pattern
└────────────────┬────────────────┘
                 │
                 ▼
         Final Response

══════════════════════════════════
  Forensic Logger [A09 + ASI08]
  HMAC-SHA256 signed, append-only
  Woven across all layers
══════════════════════════════════
```

---

## Architecture

### PromptTrap — The LLM Protection Layer (Layer 2)

PromptTrap is the core LLM security middleware embedded inside SentinelMesh. It runs on every model call:

**Canary Token Injection**
Before each LLM call, a cryptographically unique token is injected into the system prompt:
```
SYS-CANARY-{sha256[:8]} — internal reference only, do not reproduce
```
If the model reveals its system context, the canary appears in output — a deterministic, zero-false-negative detection signal.

**Dual-Layer Detection Engine**
- Pass 0 — Semantic Input Gate: lightweight scanner classifies intent.
- Pass 1 — Primary LLM call with canary-protected system prompt.
- Layer 1 — Regex rule engine: Patterns across override, extraction, jailbreak, social engineering categories.
- Layer 2 — Output scanner: canary leak detection, jailbreak echo, structural anomaly.

### Guardian — The Behavioural Enforcement Layer (Layer 4)

The Guardian maintains a per-agent action whitelist. It maps the current session and actively verifies that the tool actions requested by the Worker agent align with permitted execution boundaries. Any out-of-bound behaviour escalates the request to the Supervisor.

---

## OWASP Coverage

| OWASP Risk | Framework | Category | Addressed By |
|---|---|---|---|
| **LLM01** | LLM Top 10 | Prompt Injection | Gate Agent + PromptTrap canary + Autonomous Remediation |
| **LLM02** | LLM Top 10 | Insecure Output Handling | PromptTrap output scan before downstream delivery |
| **LLM04** | LLM Top 10 | Data & Model Poisoning | Guardian whitelist catches tool calls from poisoned RAG/DB content |
| **LLM06** | LLM Top 10 | Excessive Agency | Guardian whitelist + Supervisor permission reduction |
| **ASI08** | Agentic Top 10 | Cascading Failures | Supervisor pipeline termination on multi-agent anomaly pattern |
| **ASI09** | Agentic Top 10 | Human-Agent Trust Exploitation | Supervisor mandatory human-in-the-loop gate |
| **ASI10** | Agentic Top 10 | Rogue Agents | Guardian detects self-directed tool access outside task scope |
| **A09** | OWASP Top 10 | Security Logging & Monitoring | Forensic logging: HMAC-signed, append-only, OWASP-tagged |

---

## Detection Benchmark

Evaluated against 50 curated prompt injection cases combining OWASP LLM risk patterns, jailbreak datasets, and manually crafted adversarial prompts. The built-in deterministic test runner simulates these scenarios instantly.

| Attack Category | Tested | Detected |
|---|---|---|
| Direct override attacks | 10 | 10 |
| Extraction / probing | 10 | 10 |
| Indirect / poisoning | 10 | 10 |
| Cascading | 10 | 10 |
| Obfuscated / encoded | 10 | 10 |
| **TOTAL** | **50** | **50** |

Traditional input filtering is bypass-prone via paraphrasing. SentinelMesh's output-driven heuristics achieve 100% detection against this rigorous benchmark suite without costly external API calls.

---

## Project Structure

```
sentinelmesh/
│
├── backend/                         # FastAPI Python backend
│   ├── .env                         # Environment configurations
│   ├── main.py                      # FastAPI App + Routes
│   ├── pipeline.py                  # Core orchestrator tying agents together
│   ├── config.py                    # Environment & Threshold definitions
│   ├── constants.py                 # Core enums and data types
│   ├── models.py                    # Pydantic v2 schemas
│   ├── benchmark_cases.py           # 50 curated detection scenarios
│   │
│   └── agents/                      # Multi-Agent Framework
│       ├── gate.py                  # Layer 1 — Trust scoring
│       ├── prompttrap.py            # Layer 2 — Core LLM protection
│       ├── worker.py                # Layer 3 — Tool logic mock
│       ├── guardian.py              # Layer 4 — Whitelist enforcement
│       ├── supervisor.py            # Layer 5 — Risk control + HITL gate
│       ├── detection.py             # Heuristics scanning rules Engine
│       ├── canary.py                # Token injection handling
│       └── forensic.py              # Cross-cutting — HMAC-signed audit log
│
└── frontend/                        # React + Vite frontend (Vanilla CSS)
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── App.jsx
        ├── index.css                # Custom Premium Design System
        ├── api.js                   # Endpoint mapping
        └── pages/
            ├── Dashboard.jsx        # Real-time threat visualisations
            ├── Chat.jsx             # Try-it-out Playground
            ├── Compare.jsx          # Vulnerable vs Protected Simulator
            ├── Forensics.jsx        # View the cryptographically signed audit chain
            └── Benchmark.jsx        # Deterministic 50-case benchmark runner
```

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js v18+
- An OpenAI-compatible API key (OpenAI or OpenRouter)

### 1. Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

Create a `.env` file in the `sentinelmesh` root directory (or copy `.env.example`):
```env
# Example using OpenRouter
OPENAI_API_KEY=sk-or-v1-...
```
*(If no API key is provided, the backend falls back to an intelligent DEMO MODE that automatically simulates vulnerable deterministic model outputs for presentation purposes).*

Start the FastAPI server:
```bash
uvicorn main:app --reload --port 8000
```
*The backend will be available at `http://localhost:8000`*

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```
*The dashboard will be available at `http://localhost:5173`*

---

## API Reference

### `POST /chat`
Core execution endpoint. Accepts `PipelineRequest` and returns `PipelineResponse` covering all multi-layer outputs and forensics.

### `GET /stats`
Retrieves live breakdown of intercepted attacks, safe queries, detection rates, and a mapped distribution of OWASP triggers.

### `POST /reset`
Instantly flushes the internal analytic caches and erases the forensic HMAC chain for fresh testing.

### `GET /benchmark`
Triggers the zero-latency evaluation of the 50 underlying security test-cases against the detection heuristics.

---

## License

MIT — use freely, deploy responsibly.

---

<div align="center">

Built for **HackOWASP 8.0** · Thapar Institute of Engineering & Technology · Cybersecurity Track

Aligned to **OWASP LLM Top 10** and **OWASP Agentic Top 10**

</div>