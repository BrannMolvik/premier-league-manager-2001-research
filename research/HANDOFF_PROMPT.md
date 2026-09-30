# Standard Session Handoff

Use the following prompt when opening a fresh ChatGPT/Codex session. The repository, not the previous chat, is the source of truth.

```text
Continue the FM2001 Windows 11 modernization/port.

OVERALL MISSION: Complete every remaining roadmap gate through Gate 17 and
produce the verified Windows 11 release. The current gate and exact next task
are only the next steps in this mission, not separate finish lines. A small
checkpoint, successful test, completed subtask, or completed gate must not be
treated as completion of the overall assignment. Do not ask Daniel to say
"continue" between successive tasks or gates.

Repository:
https://github.com/BrannMolvik/premier-league-manager-2001-research

GitHub is canonical. Do not rely on previous chat state when it conflicts with the repository.

Before working:
1. Check the current main HEAD.
2. Read ROADMAP.md.
3. Read research/CURRENT_STATE.md.
4. Read research/CONTINUATION_INSTRUCTIONS.md.
5. Read only the relevant sections of FINDINGS.md / topic-specific research needed for the active task.
6. Inspect recent commits after the technical baseline recorded in CURRENT_STATE.md.
7. Verify the relevant tests/status before making a new fidelity claim.

Work only on the active gate unless a dependency requires otherwise.
Continue source-backed work through successive meaningful subtasks in the same
session rather than stopping after a single small checkpoint when further work
is available. After each verified subtask, immediately identify and undertake
the next canonical task. After a gate audit closes a gate, advance to the
next roadmap gate and keep working if the session can still perform useful work.
Do not impose an arbitrary short response duration. Keep the long-term mission
active across chat/recovery boundaries rather than requiring a fresh user order. Checkpoint roughly every ten minutes without treating a
checkpoint as a reason to end the session. When the conversation or execution
budget ends naturally, leave a durable exact next step with runtime status
`working` so automatic recovery can continue; do not claim the entire job is
finished. Only use `completed` when Gate 17's release audit really passes.
When all productive routes are
blocked by infrastructure (for example, source bytes cannot be read because
a trivial shell command also fails), record the precise blocker and do not
simulate ongoing progress or repeatedly add speculative work. Use
`waiting_for_user` only if a specific user action is truly necessary;
otherwise preserve the exact external blocker and remaining mission in GitHub.

Record unrelated useful leads in research/BACKLOG.md.

Persistence rules:
- commit every meaningful verified result;
- if roughly 10 minutes pass during an unresolved investigation, make a checkpoint;
- update research/PROGRESS.md with chronological evidence;
- update research/CURRENT_STATE.md whenever the exact next task or active gate changes;
- never leave substantial useful work only in chat;
- preserve/reuse authorized original FM2001 resources wherever practical;
- put intentionally imported original resources under original_assets/ with provenance per research/ASSET_POLICY.md;
- keep raw disc images, duplicate archives, temporary extraction dumps, and unrelated binary noise out of Git.

When a gate's completion criteria are satisfied, audit the gate, mark it complete in ROADMAP.md, update CURRENT_STATE.md/project_status.json, and only then move to the next gate.
```

## Why this prompt is short

A new session should not need a giant copied chat summary. If the prompt above is insufficient, the repository handoff files need improvement.
