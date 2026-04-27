"""Built-in regex rule pack for promptguard.

Fast, deterministic, transparent — every match has a name + sample
attack hits. Catches the obvious idioms; the classifier layer
catches paraphrased / novel ones.

Each rule has:
  name        — short identifier shown in Verdict.matched_rules
  pattern     — case-insensitive regex (use \\b for word boundaries)
  description — what attack family it targets (for audit logs)
  severity    — "high" / "medium" / "low" hint for action selection

Severity heuristic:
  high   ⇒ contributes 0.9 to risk_score, immediate BLOCK candidate
  medium ⇒ contributes 0.6, WARN candidate
  low    ⇒ contributes 0.3, PASS unless the classifier also flags

This pack is intentionally English-heavy because the v0.1 classifier
(ProtectAI deberta) is too. Multilingual rule pack lands in v0.2 along
with a multilingual classifier.
"""
from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Rule:
    """One regex-based detection rule."""

    name: str
    pattern: re.Pattern[str]
    description: str
    severity: str  # "high" | "medium" | "low"


def _build(name: str, pattern: str, description: str, severity: str = "high") -> Rule:
    return Rule(
        name=name,
        pattern=re.compile(pattern, re.IGNORECASE | re.MULTILINE),
        description=description,
        severity=severity,
    )


DEFAULT_RULES: tuple[Rule, ...] = (
    # Direct instruction-override family — the most common attack idiom.
    _build(
        "instruction_override",
        r"\b(ignore|disregard|forget)\s+(all\s+|any\s+|the\s+)?(previous|prior|above|earlier)\s+(instructions?|prompts?|rules?|directives?)\b",
        "Asks the model to discard the system prompt.",
        "high",
    ),
    _build(
        "system_prompt_extraction",
        r"\b(reveal|show|print|repeat|tell me|what is|what's)\s+(the|your)\s+(system\s+)?(prompt|instructions?|directive|rules?)\b",
        "Tries to extract the hidden system prompt.",
        "high",
    ),
    # Role-swap / persona override.
    _build(
        "persona_override_dan",
        r"\b(you are|act as|pretend to be|from now on you are)\s+(?:a\s+)?(DAN|do anything now|jailbroken|unrestricted|uncensored|developer mode)\b",
        "Classic 'DAN / jailbroken assistant' persona swap.",
        "high",
    ),
    _build(
        "persona_override_generic",
        r"\b(act as|pretend to be|roleplay as)\s+(?:an?\s+)?(unrestricted|unfiltered|uncensored|amoral|evil)\b",
        "Generic 'unfiltered persona' role-swap.",
        "high",
    ),
    # Output hijacking.
    _build(
        "output_hijack",
        r"\b(only|just)\s+(say|respond with|output|reply with)\b.{0,80}?(?:exactly|verbatim|word for word)",
        "Forces a specific verbatim output, often used to embed payload.",
        "medium",
    ),
    _build(
        "format_override",
        r"\bdo not\s+(refuse|decline|apologize|warn|caution|disclaim)\b",
        "Asks the model to skip safety language.",
        "medium",
    ),
    # Indirect-injection markers (more relevant for retrieved docs than user input).
    _build(
        "embedded_directive",
        r"###\s*(SYSTEM|INSTRUCTION|ASSISTANT|USER):",
        "Inline role-marker headers used to spoof structured prompts.",
        "high",
    ),
    _build(
        "code_block_directive",
        r"```\s*(?:system|instruction|prompt)\s*\n",
        "Code-fence opening that pretends to be a system directive.",
        "medium",
    ),
    # Encoding tricks.
    _build(
        "base64_payload",
        r"(?:base64|b64)[\s:=]+[A-Za-z0-9+/]{40,}={0,2}",
        "Long base64 string — common payload encoding for hidden instructions.",
        "low",
    ),
    _build(
        "rot13_marker",
        r"\b(rot13|rot-13|caesar cipher)\b",
        "References a classical encoding scheme often paired with hidden payloads.",
        "low",
    ),
    # Token / boundary spoofing.
    _build(
        "boundary_spoof",
        r"</?(im_start|im_end|s|user|assistant|system)>",
        "Mimics chat-template control tokens to spoof a turn boundary.",
        "high",
    ),
    # Common jailbreak community markers.
    _build(
        "developer_mode",
        r"\b(developer\s+mode|debug\s+mode|admin\s+mode|root\s+mode)\b\s+(enabled|on|active)",
        "Fictional 'developer/admin mode unlocked' framing.",
        "medium",
    ),
)


def match_rules(
    text: str,
    rules: tuple[Rule, ...] = DEFAULT_RULES,
) -> list[Rule]:
    """Return the rules whose pattern fires on ``text`` (in declaration order)."""
    return [r for r in rules if r.pattern.search(text)]


def severity_to_score(severity: str) -> float:
    """Map severity string to a risk contribution in [0, 1]."""
    return {"high": 0.9, "medium": 0.6, "low": 0.3}.get(severity, 0.3)
