from enum import Enum

class Verdict(str, Enum):
    SAFE = "SAFE"
    SUSPICIOUS = "SUSPICIOUS"
    ATTACK = "ATTACK"
    BLOCKED = "BLOCKED"
    ESCALATED = "ESCALATED"

class AgentID(str, Enum):
    GATE = "GATE"
    PROMPTTRAP = "PROMPTTRAP"
    WORKER = "WORKER"
    GUARDIAN = "GUARDIAN"
    SUPERVISOR = "SUPERVISOR"
    FORENSIC = "FORENSIC"

class OWASPCode(str, Enum):
    LLM01 = "LLM01"
    LLM02 = "LLM02"
    LLM04 = "LLM04"
    LLM06 = "LLM06"
    ASI08 = "ASI08"
    ASI09 = "ASI09"
    ASI10 = "ASI10"
    A09 = "A09"

class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
