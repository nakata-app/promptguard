# Contributing to promptguard

Thanks for considering a contribution. The repo is small enough that the
review pipeline is short, keep changes focused, the bar is "honest
detection rates + clear tradeoffs."

## Quickstart for a local dev loop

```bash
git clone https://github.com/nakata-app/promptguard.git
cd promptguard
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

The classifier path needs an extra install:

```bash
pip install -e ".[classifier]"   # transformers + torch
```

Without the extras, the rule-pack stays the only signal; tests cover
both modes.

## What we run before every commit

```bash
ruff check promptguard tests           # lint
mypy --strict promptguard              # type check
pytest -q                              # unit tests
```

CI runs the same three on Python 3.10 / 3.11 / 3.12. A PR that doesn't
pass them locally won't pass CI either.

## What lands easily

- Bug fixes with a regression test that fails before / passes after.
- New rule-pack patterns. Each rule needs a positive test (it
  catches the attack) and a negative test (it doesn't false-alarm on
  benign text).
- Better classifier wiring, ProtectAI today, more swappable backends
  tomorrow. Keep them gated behind the existing
  `Detector` protocol.
- Detector-level metrics on a held-out evaluation set (precision,
  recall, FPR). Honest numbers, including null results, are welcome.

## What needs a discussion first

- Anything that changes the public API (`Guard.check`, the `Verdict`
  shape, the `Detector` protocol).
- Adding an LLM into the inference path. Promptguard is intentionally
  LLM-free at decision time, "ask GPT-4 if this looks bad" is exactly
  what we don't want to be.
- New required dependencies. The core install has none on purpose;
  classifiers / NLI go behind `[optional]` extras.
- Multilingual coverage. v0.1 is English-first (ProtectAI deberta);
  Turkish (and other-language) support is a v0.2 design call,
  please file an issue first.

## Style

- Match the existing code. Type hints on public surfaces; no
  speculative abstractions; comments only for non-obvious WHY.
- One commit per logical change. Squash if you accumulate "fix
  comments" commits.
- Commit messages: imperative mood, short subject ("add rule pattern
  for context-injection"), longer body if the change is non-trivial.

## Reporting bugs

GitHub Issues. Include:
- Python version + OS.
- The minimum reproduction (one input string + the verdict you got).
- Whether you ran rule-pack only, classifier only, or both.
- What you expected vs what you got.

## Reporting security issues

See [`SECURITY.md`](SECURITY.md). Don't open a public issue for an
unpatched vulnerability.
