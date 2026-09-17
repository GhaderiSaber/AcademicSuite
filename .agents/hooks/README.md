# Lifecycle Hooks Directory (Phase 9)

In accordance with **Phase 9 (Add Hooks for Hard Enforcement)**:
Antigravity lifecycle hooks mechanically enforce non-negotiable constitutional rules outside the LLM context window.

## Hook Events
- `PreToolUse`: Validates tool call arguments (blocks non-ASCII filenames, protects raw data directories).
- `PostToolUse`: Appends deterministic audit entries to the verification journal.
- `PreInvocation`: Injects ephemeral constitutional reminders into context.
- `Stop`: Audits conversation transcript (`transcript.jsonl`) via `transcript_and_rule_guard.py`, verifying the Binary Honesty Protocol, artifact generation, and multi-agent truthfulness.
