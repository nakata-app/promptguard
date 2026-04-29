# Security policy

## Reporting a vulnerability

Please **do not** open a public GitHub issue for security-sensitive
findings. Instead, email the maintainer at
**hey@nakata.app** with:

- A description of the issue.
- Steps to reproduce (a minimal repro is enough).
- The version / commit you tested against.
- Optionally, your proposed fix.

We aim to acknowledge a report within 72 hours and to ship a fix in
the next minor release where applicable.

## Scope

The Python package itself is the in-scope surface: `Guard`,
`Detector` implementations, the rule pack, and the optional
classifier integration.

Out of scope:
- Bugs in upstream classifiers (ProtectAI deberta, Hugging Face
  transformers, torch). Report those upstream.
- Bypasses against an LLM you're protecting that don't go through
  promptguard's input gate (e.g. attacks against the LLM's own
  alignment). Promptguard scopes to the input boundary; what the
  downstream model does with text we passed through is the model's
  problem.
- Performance issues without a security impact (file regular issues
  instead).

## Threat model

promptguard reads user-supplied text, scores it for prompt-injection
risk, and returns a `Verdict`. It does not call the LLM, does not
open network sockets in core mode (the optional `serve` HTTP daemon
is opt-in), and does not execute remote payloads.

**Untrusted input:** every string passed to `Guard.check`. We never
`eval`, `exec`, or template untrusted text into shell commands. We
never feed untrusted text into a downstream LLM ourselves; the
caller does that, and the verdict is meant to inform the caller's
decision (block / sanitise / log / pass).

**Detection bypass is in scope.** If you find an attack pattern that
slips past the rule pack or the classifier with high confidence,
please report it (privately). Concrete repros and known-bypass
prompts are gold; we'd rather know about them.

## Expected detection limits (be honest with yourself)

Prompt-injection detection is an active arms race.

- Known canonical patterns (`ignore previous instructions`,
  `you are now`, `disregard the system prompt`, etc.): high recall.
- Novel rephrasings, multilingual variants, encoded payloads, and
  indirect-injection-via-retrieved-document: meaningfully lower.
- We track our headline numbers in the README and update them when
  the rule pack / classifier changes; if you measure differently
  please open an issue with your eval harness.

A "promptguard verdict says safe" is **not** a guarantee. Defence in
depth (output verification via `halluguard`, fact-check via
`truthcheck`, tool-use sandboxing, sensitive-action confirmation)
still applies.
