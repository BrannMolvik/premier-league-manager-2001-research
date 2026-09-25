# Standard Session Handoff

Use the following prompt when opening a fresh ChatGPT/Codex session. The repository, not the previous chat, is the source of truth.

```text
Continue the FM2001 clean-room reconstruction.

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
Record unrelated useful leads in research/BACKLOG.md.

Persistence rules:
- commit every meaningful verified result;
- if roughly 10 minutes pass during an unresolved investigation, make a checkpoint;
- update research/PROGRESS.md with chronological evidence;
- update research/CURRENT_STATE.md whenever the exact next task or active gate changes;
- never leave substantial useful work only in chat;
- keep original copyrighted game assets out of GitHub.

When a gate's completion criteria are satisfied, audit the gate, mark it complete in ROADMAP.md, update CURRENT_STATE.md/project_status.json, and only then move to the next gate.
```

## Why this prompt is short

A new session should not need a giant copied chat summary. If the prompt above is insufficient, the repository handoff files need improvement.
