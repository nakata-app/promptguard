"""PromptGuard v0.1 — combined rule + classifier detection.

Two layers:
  1. Regex rule pack (deterministic, fast, transparent)
  2. ProtectAI cross-encoder classifier (catches paraphrased attacks)

Either layer can be disabled via `rules_only=True` or
`classifier_only=True`. The default uses both, blending their signals
into a single risk_score.

Action selection:
  risk >= 0.85  →  BLOCK
  risk >= 0.50  →  WARN
  else          →  PASS

Sidecar mode: the verdict is metadata the caller's middleware reads;
the user's input is never modified by promptguard. The LLM sees
exactly what the user typed (unless `rewrite=True`, opt-in v0.2+).

English-only in v0.1 — Turkish / multilingual coverage is the v0.2
priority. See ROADMAP.
"""
from __future__ import annotations

import importlib.util
from typing import Any

from promptguard.rules import (
    DEFAULT_RULES,
    Rule,
    match_rules,
    severity_to_score,
)
from promptguard.types import Action, Verdict


# Default thresholds — tune on your own calibration set.
DEFAULT_BLOCK_AT = 0.85
DEFAULT_WARN_AT = 0.50

# Default classifier model id (overridable via PromptGuard(classifier=...)).
_DEFAULT_CLASSIFIER = "protectai/deberta-v3-base-prompt-injection-v2"


class PromptGuard:
    """Detect prompt injection / jailbreak attempts in user input.

    Args:
        rules: built-in pack name ("default") or a custom tuple of Rule
            instances. Pass an empty tuple to disable the rule layer.
        classifier: HuggingFace model id for the classifier layer, or
            None to disable. Falls back to ProtectAI deberta v2 default.
        block_at: risk_score >= this → suggested_action=BLOCK.
        warn_at: risk_score in [warn_at, block_at) → WARN.
        rules_only: skip the classifier, useful for low-latency CI.
        classifier_only: skip the rule pack.
    """

    def __init__(
        self,
        rules: str | tuple[Rule, ...] = "default",
        classifier: str | None = _DEFAULT_CLASSIFIER,
        block_at: float = DEFAULT_BLOCK_AT,
        warn_at: float = DEFAULT_WARN_AT,
        rules_only: bool = False,
        classifier_only: bool = False,
    ) -> None:
        if rules_only and classifier_only:
            raise ValueError("rules_only and classifier_only are mutually exclusive")

        if rules == "default":
            self._rules: tuple[Rule, ...] = DEFAULT_RULES
        elif isinstance(rules, tuple):
            self._rules = rules
        else:
            raise ValueError(f"unknown rules pack: {rules!r}")

        self.classifier = classifier
        self.block_at = block_at
        self.warn_at = warn_at
        self.rules_only = rules_only
        self.classifier_only = classifier_only

    def check(self, user_input: str, **_: Any) -> Verdict:
        """Score ``user_input`` for prompt-injection risk."""
        rule_score = 0.0
        matched: list[str] = []
        if not self.classifier_only and self._rules:
            hits = match_rules(user_input, self._rules)
            matched = [r.name for r in hits]
            # Take the max severity across hits — additive double-counts
            # overlapping rules.
            rule_score = max(
                (severity_to_score(r.severity) for r in hits), default=0.0
            )

        clf_score: float | None = None
        if not self.rules_only and self.classifier is not None:
            if importlib.util.find_spec("transformers") is not None:
                from promptguard.classifier import predict

                label, score = predict(user_input, self.classifier)
                # Normalise: classifier score is "confidence in its label".
                # We want "probability of INJECTION" regardless of label name.
                clf_score = float(score) if label == "INJECTION" else 1.0 - float(score)

        # Combine: when both layers fire, take the max (most pessimistic).
        # When only one fires, use that one. Keeps risk_score in [0, 1].
        scores = [s for s in (rule_score, clf_score) if s is not None and s > 0]
        risk_score = max(scores) if scores else 0.0

        if risk_score >= self.block_at:
            action = Action.BLOCK
        elif risk_score >= self.warn_at:
            action = Action.WARN
        else:
            action = Action.PASS

        return Verdict(
            user_input=user_input,
            risk_score=risk_score,
            suggested_action=action,
            matched_rules=matched,
            classifier_score=clf_score,
        )
