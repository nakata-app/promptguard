"""ProtectAI deberta-v3-base-prompt-injection classifier wrapper.

Lazy-loaded transformers pipeline. ~184MB model, downloaded from
HuggingFace Hub on first use, then cached.

Multilingual is a v0.2 follow-up — this classifier is English-heavy
because its training corpus was English jailbreak / injection
attempts. Turkish / Arabic / Mandarin attacks fall through, which is
why the rule pack catches obvious idioms regardless of classifier
opinion.

Out-of-scope for v0.1:
  - GPU inference
  - Batch processing
  - Custom models beyond the protectai/* family

These all land naturally in v0.2.
"""
from __future__ import annotations

import importlib.util
from typing import Any


DEFAULT_MODEL = "protectai/deberta-v3-base-prompt-injection-v2"


class _Classifier:
    """Wrapped transformers pipeline. Singleton-per-model so we don't
    reload the 184MB weights every call."""

    def __init__(self, model_id: str = DEFAULT_MODEL) -> None:
        if importlib.util.find_spec("transformers") is None:
            raise SystemExit(
                "Classifier path needs transformers. "
                'Install with `pip install "promptguard[classifier]"`.'
            )
        from transformers import (
            AutoModelForSequenceClassification,
            AutoTokenizer,
            pipeline,
        )

        self.model_id = model_id
        self._tokenizer = AutoTokenizer.from_pretrained(model_id)
        self._model = AutoModelForSequenceClassification.from_pretrained(model_id)
        # truncation=True keeps long inputs from blowing up; max_length 512
        # matches the model's training context.
        self._pipe = pipeline(
            "text-classification",
            model=self._model,
            tokenizer=self._tokenizer,
            truncation=True,
            max_length=512,
        )

    def predict(self, text: str) -> tuple[str, float]:
        """Return (label, score). label is "INJECTION" or "SAFE"."""
        result: list[dict[str, Any]] = self._pipe(text)
        # transformers returns [{"label": "...", "score": ...}]
        label = str(result[0]["label"]).upper()
        # Different ProtectAI checkpoints use different label names;
        # normalise to INJECTION / SAFE.
        if label in ("INJECTION", "JAILBREAK"):
            label = "INJECTION"
        elif label in ("SAFE", "BENIGN", "NORMAL"):
            label = "SAFE"
        # else: leave as-is, caller can handle unknown labels
        score = float(result[0]["score"])
        return label, score


# Module-level cache so the same model id reuses one Classifier instance.
_CACHE: dict[str, _Classifier] = {}


def get_classifier(model_id: str = DEFAULT_MODEL) -> _Classifier:
    """Return the cached Classifier for ``model_id``, building it on first call."""
    if model_id not in _CACHE:
        _CACHE[model_id] = _Classifier(model_id)
    return _CACHE[model_id]


def predict(text: str, model_id: str = DEFAULT_MODEL) -> tuple[str, float]:
    """One-line classifier call. Returns (label, score)."""
    return get_classifier(model_id).predict(text)
