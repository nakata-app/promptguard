"""Public data types — stable contract surface for callers."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Action(str, Enum):
    """What the caller's middleware should do with the request."""

    PASS = "PASS"
    """No injection signal. Forward to the LLM as-is."""

    WARN = "WARN"
    """Suspicious; forward but flag for audit / human review."""

    BLOCK = "BLOCK"
    """High-confidence injection. Refuse the request."""


@dataclass
class Verdict:
    """Result of `PromptGuard.check(user_input)`."""

    user_input: str
    risk_score: float           # 0.0 (clean) – 1.0 (definitely an attack)
    suggested_action: Action
    matched_rules: list[str] = field(default_factory=list)
    classifier_score: float | None = None
    rewritten_input: str | None = None  # populated when rewrite mode is on
