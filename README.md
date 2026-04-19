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

## Why SentinelMesh

Large Language Models are no longer just answering questions. They read emails, query databases, call APIs, and execute workflows — operating with real-world privileges across entire systems. A single compromised agent can cascade failures through an entire pipeline, exfiltrate sensitive data, or escalate privileges far beyond the original request scope.

**Existing defences fail because they watch the input. SentinelMesh watches what agents actually do.**

| Existing Defence           | Failure Mode                                                         |
| -------------------------- | -------------------------------------------------------------------- |
| Input keyword filtering    | Bypassed trivially with paraphrasing, encoding, or indirect phrasing |
| Static blocklists          | Attackers iterate until gaps are found — the list is always behind   |
| Output content moderation  | Detects harmful content, not instruction hijacking                   |
| Prompt hardening           | Reduces surface area but provides zero visibility when it fails      |
| Single-call security tools | Cannot detect cross-agent cascades or rogue agent actions            |

The core insight:

> *"Did this agent do what it was supposed to do — or was it compromised?"*

This makes detection **output-driven, model-agnostic, and resilient to input-level evasion.**

---

## How It Works

Every request flows through a five-agent pipeline. Each agent has a single, well-defined security responsibility.

```
User Input → Gate → PromptTrap → Worker → Guardian → Supervisor → Response
```

---

## Architecture

### PromptTrap — The LLM Protection Layer

* Injects a **cryptographically unique canary token** into the system prompt
* Monitors output for leakage or boundary override
* Uses dual-layer detection:

  * Semantic intent scan
  * Output integrity verification

👉 If the canary appears in output, compromise is **cryptographically verifiable**

---

### Guardian — Behavioural Enforcement Layer

* Maintains **per-session action whitelist**
* Blocks any **unauthorized tool execution**
* Acts even if earlier detection layers are bypassed

---

## OWASP Coverage

Covers:

* LLM01 (Prompt Injection)
* LLM02 (Output Handling)
* LLM04 (Poisoning)
* LLM06 (Excessive Agency)
* ASI08 / ASI09 / ASI10 (Agentic risks)
* A09 (Logging & Monitoring)

---

## Detection Benchmark

Evaluated against **50 curated adversarial prompt injection cases**:

| Category             | Tested | Detected |
| -------------------- | ------ | -------- |
| Direct override      | 10     | 10       |
| Extraction           | 10     | 10       |
| Indirect / poisoning | 10     | 10       |
| Cascading            | 10     | 10       |
| Obfuscated           | 10     | 10       |
| **Total**            | **50** | **50**   |

Traditional input filtering is bypass-prone. SentinelMesh uses **output-driven verification**, eliminating dependence on fragile input heuristics.

---

## ⚠️ Detection Guarantees (Important)

**The reported 100% detection rate applies specifically to canary-verifiable extraction scenarios within our benchmark suite.**

For broader, multi-step or obfuscated attacks:

* SentinelMesh relies on **layered enforcement**
* The **Guardian whitelist acts as a secondary control**
* The **Supervisor prevents cascading failures**

This is why SentinelMesh is designed as a **multi-agent security fabric**, not a single-layer filter.

---

## Project Structure

* Backend: Python + FastAPI
* Agents: Gate, PromptTrap, Worker, Guardian, Supervisor
* Frontend: React + Vite dashboard
* Includes:

  * Attack simulator
  * Benchmark runner
  * Forensic audit viewer

---

## Quick Start

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

---

## API

* `POST /chat` → Run pipeline
* `GET /stats` → View metrics
* `GET /benchmark` → Run attack suite
* `POST /reset` → Reset system

---

## License

MIT — use freely, deploy responsibly.

---

## Final Note

**Input defenses can be bypassed. Behavior cannot be faked.**

SentinelMesh ensures that even if an AI is tricked — it cannot act maliciously.