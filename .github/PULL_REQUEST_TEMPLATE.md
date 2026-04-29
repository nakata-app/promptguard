## What this changes

<!-- one-paragraph summary; link to a tracking issue if there is one -->

## How it was tested

<!-- pytest output, a manual injection-prompt repro, or a held-out
     eval set with precision / recall numbers -->

## Checklist

- [ ] `ruff check promptguard tests` is clean
- [ ] `mypy --strict promptguard` is clean
- [ ] `pytest -q` passes locally
- [ ] CHANGELOG entry added (under `[Unreleased]`)
- [ ] If this changes the public API (`Guard.check`, `Verdict`,
      `Detector`): README updated
- [ ] If this adds a rule pattern: positive + negative tests included
- [ ] If this adds a classifier backend: it implements `Detector` and
      ships fixture-based tests
- [ ] If this adds a dependency: it's an `[optional]` extra unless
      truly core
