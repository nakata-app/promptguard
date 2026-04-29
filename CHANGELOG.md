# Changelog

All notable changes to **promptguard** are documented here. Format
follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
versions follow [SemVer](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-04-29

First working release. Guard ships: rule-pack detector, optional
ProtectAI deberta classifier, sidecar verdict mode (the LLM input is
not modified, the verdict goes back as metadata so the caller decides
what to do).

### Added
- `promptguard.Guard`, high-level entry point. Takes a user-supplied
  string, returns a `Verdict` with risk score, matched rules, and the
  classifier output (when the optional extra is installed). Never
  raises on input it doesn't recognise; populates `Verdict.error`
  instead.
- Rule-pack detector covering the canonical English prompt-injection
  patterns (`ignore previous instructions`, `you are now`,
  `disregard the system prompt`, role-override, context-injection
  preludes, payload smuggling).
- Optional classifier path, ProtectAI deberta-v3-base prompt-injection
  classifier, gated behind `[classifier]` extras
  (`pip install "nakata-promptguard[classifier]"`).
- `python -m promptguard serve` HTTP daemon for cross-language
  callers.
- `Detector` protocol so callers can plug in alternate classifiers
  without patching the core.

### Internals
- 16 unit tests, mypy `--strict` clean, ruff clean.
- No mandatory runtime dependencies; classifier deps live in the
  `[classifier]` extra.
- English-first by design; multilingual (Turkish in particular) is a
  v0.2 design decision (xlm-roberta zero-shot vs translate-first vs
  fine-tune).
- PyPI distribution name: `nakata-promptguard` (the bare `promptguard`
  slug is held by Opaque Systems' unrelated package). Import path
  stays `promptguard`.

[0.1.0]: https://github.com/nakata-app/promptguard/releases/tag/v0.1.0
