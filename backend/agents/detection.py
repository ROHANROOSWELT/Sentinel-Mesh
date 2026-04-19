import re
from backend.models import DetectionIssue
from backend.constants import Verdict

INPUT_PATTERNS = [
    (r"ignore\s+(all\s+)?(previous|prior|above|system)\s+(instructions?|prompts?|rules?|context)", 70, "LLM01", "Direct instruction override"),
    (r"disregard\s+(all\s+)?(previous|prior|above|system)", 65, "LLM01", "Instruction bypass attempt"),
    (r"forget\s+(everything|all previous|your instructions|your guidelines)", 60, "LLM01", "Memory-wipe injection"),
    (r"\bDAN\b|do anything now", 82, "LLM01", "DAN jailbreak pattern"),
    (r"\bjailbreak\b", 85, "LLM01", "Explicit jailbreak keyword"),
    (r"you are now\s+(?!a helpful)", 50, "LLM01", "Role-replacement injection"),
    (r"new (system\s+)?instructions?:", 55, "LLM01", "Fake instruction injection"),
    (r"(reveal|show|print|display|repeat)\s+(your|the)\s+(system\s+)?(prompt|instructions?|token|secret)", 65, "LLM02", "Prompt-extraction attempt"),
    (r"what (is|are|were)\s+(your|the)\s+(original|previous|secret|hidden)\s+(instructions?|prompt)", 60, "LLM02", "Instruction probing"),
    (r"act as if you (have no|are without)\s+(restrictions?|guidelines?|rules?)", 70, "LLM01", "Restriction bypass"),
    (r"pretend\s+(you|to be).+(unfiltered|unrestricted|no (rules|limits))", 65, "LLM01", "Persona injection"),
    (r"\bfrom now on\b", 30, "LLM01", "Persistent override attempt"),
    (r"your (real|true|actual) (self|identity|purpose|goal)", 40, "LLM01", "Identity manipulation"),
    (r"\bsudo\b|admin mode|developer mode|god mode", 50, "LLM01", "Privilege escalation"),
    (r"respond only (in|as|with)", 35, "LLM01", "Output-format hijack"),
    (r"translate (everything|all (of )?the above) into", 40, "LLM01", "Translation exfiltration"),
    (r"(start|begin) (your )?response with", 30, "LLM01", "Output prefix injection"),
    (r"system\s*prompt\s*:", 55, "LLM02", "System prompt injection marker"),
    (r"override\s+(all\s+)?(safety|security|content)\s+(filters?|measures?|guidelines?)", 75, "LLM01", "Safety override"),
    (r"(enable|activate|unlock)\s+(unrestricted|unsafe|developer|jailbreak)\s+mode", 80, "LLM01", "Mode unlock attempt"),
]

OUTPUT_PATTERNS = [
    (r"i (was|am) (told|instructed|programmed|trained)\s+to", 45, "LLM02", "System-prompt disclosure"),
    (r"my (system\s+)?(prompt|instructions?)\s+(is|are|say|says)", 65, "LLM02", "Direct prompt leak"),
    (r"\bCANARY\b|canary.?token", 80, "LLM01", "Canary keyword in output"),
    (r"i will now ignore", 75, "LLM01", "Override acceptance"),
    (r"sure[,!]?\s+i('ll| will)\s+(ignore|forget|disregard)", 70, "LLM01", "Compliant with override"),
    (r"as (an unfiltered|a (jailbroken|unrestricted|free))", 65, "LLM01", "Jailbroken persona adopted"),
    (r"without (any )?restrictions?", 40, "LLM01", "Restriction acknowledgement"),
    (r"(original|hidden|secret)\s+(prompt|instructions?)", 50, "LLM02", "Hidden context reference"),
]

COMPILED_INPUT = [(re.compile(p, re.IGNORECASE), w, o, l) for p, w, o, l in INPUT_PATTERNS]
COMPILED_OUTPUT = [(re.compile(p, re.IGNORECASE), w, o, l) for p, w, o, l in OUTPUT_PATTERNS]

class DetectionEngine:
    def scan_input(self, message: str) -> tuple[list[DetectionIssue], int]:
        issues = []
        labels_seen = set()
        score = 0
        for regex, weight, owasp, label in COMPILED_INPUT:
            if regex.search(message):
                if label not in labels_seen:
                    issues.append(DetectionIssue(trigger=label, weight=weight, owasp=owasp, pattern_type="input"))
                    labels_seen.add(label)
                    score += weight
        return issues, min(100, score)

    def scan_output(self, text: str, canary_leaked: bool) -> tuple[list[DetectionIssue], int]:
        issues = []
        labels_seen = set()
        score = 0
        for regex, weight, owasp, label in COMPILED_OUTPUT:
            if regex.search(text):
                if label not in labels_seen:
                    issues.append(DetectionIssue(trigger=label, weight=weight, owasp=owasp, pattern_type="output"))
                    labels_seen.add(label)
                    score += weight
        
        if canary_leaked:
            if "Canary token leaked" not in labels_seen:
                issues.append(DetectionIssue(trigger="Canary token leaked", weight=95, owasp="LLM01", pattern_type="output"))
                score += 95
                
        return issues, min(100, score)

    def harden_input(self, message: str) -> str:
        hardened = message
        for regex, _, _, _ in COMPILED_INPUT:
            hardened = regex.sub("[REDACTED BY SENTINELMESH]", hardened)
        return hardened

    def classify(self, input_score: int, output_score: int) -> Verdict:
        combined = max(input_score, output_score)
        if combined >= 60: return Verdict.ATTACK
        if combined >= 25: return Verdict.SUSPICIOUS
        return Verdict.SAFE

    def build_explanation(self, input_issues, output_issues, verdict, canary) -> str:
        if verdict == Verdict.SAFE:
            return "No malicious intent detected. Request appears benign."
            
        explanation_parts = []
        if any("Canary" in i.trigger for i in output_issues):
            explanation_parts.append("CRITICAL: The system's secret canary token was leaked in the output.")
            
        if input_issues:
            sorted_input = sorted(input_issues, key=lambda x: x.weight, reverse=True)
            triggers = [f"'{i.trigger}'" for i in sorted_input[:2]]
            explanation_parts.append(f"Input triggered pattern(s): {', '.join(triggers)}.")
            
        if output_issues:
            sorted_output = sorted([i for i in output_issues if "Canary" not in i.trigger], key=lambda x: x.weight, reverse=True)
            if sorted_output:
                explanation_parts.append(f"Output matched suspicious pattern: '{sorted_output[0].trigger}'.")
                
        return " | ".join(explanation_parts) if explanation_parts else f"Flagged as {verdict.value} due to risk score threshold."
