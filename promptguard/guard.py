"""Skeleton PromptGuard — public surface, no working detector yet.

v0.0 ships:
  - stable Verdict / Action types
  - PromptGuard constructor that accepts the v0.1 args without crashing
  - check() raises NotImplementedError pointing at the roadmap

v0.1 will land:
  - Rule layer: regex pack for known injection idioms
  - Classifier layer: HuggingFace cross-encoder
    (default: protectai/deberta-v3-base-prompt-injection)
  - Indirect-injection mode for retrieved documents
"""
from __future__ import annotations

from typing import Any

from promptguard.types import Verdict


class PromptGuard:
    """Detect prompt injection / jailbreak attempts in user input.

    Skeleton — `check()` raises NotImplementedError until v0.1.

    Args:
        rules: rule pack name (built-in) or path to a custom YAML file.
        classifier: HuggingFace model id for the cross-encoder layer
            (e.g. ``protectai/deberta-v3-base-prompt-injection``).
        threshold: classifier score above this → suggested_action=BLOCK.
        rules_only: skip the classifier; useful for low-latency CI.
        classifier_only: skip the rule pack; useful when you maintain
            your own deny-list elsewhere.
        rewrite: when True, the verdict carries a defanged version of
            the input (suspicious instructions wrapped in tags) instead
            of just a BLOCK signal.
    """

    def __init__(
        self,
        rules: str = "default",
        classifier: str | None = "protectai/deberta-v3-base-prompt-injection",
        threshold: float = 0.7,
        rules_only: bool = False,
        classifier_only: bool = False,
        rewrite: bool = False,
    ) -> None:
        if rules_only and classifier_only:
            raise ValueError("rules_only and classifier_only are mutually exclusive")
        self.rules = rules
        self.classifier = classifier
        self.threshold = threshold
        self.rules_only = rules_only
        self.classifier_only = classifier_only
        self.rewrite = rewrite

    def check(self, user_input: str, **_: Any) -> Verdict:
        """Score the user-supplied text for injection risk.

        Args:
            user_input: raw text from the user (or a retrieved document
                in indirect-injection mode).

        Returns:
            A ``Verdict`` with risk_score, suggested_action, matched
            rules, optional classifier score, and (if ``rewrite=True``)
            a defanged version of the input.

        Raises:
            NotImplementedError: until v0.1 lands. See README.
        """
        raise NotImplementedError(
            "promptguard is at v0.0 — only types and the API surface are stable. "
            "v0.1 will ship the rule layer + classifier path. Track progress at "
            "https://github.com/nakata-app/promptguard (when public)."
        )
