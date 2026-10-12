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

LATEST EFFICIENCY DIRECTIVE (12 Oct 2026):
Read research/WORKER_MILESTONE_BATCHING_POLICY.md. Keep the lightweight
agent-runtime heartbeat about every 10 minutes to protect automatic recovery,
but DO NOT equate it with a main commit, a new PR or CI. Work toward coherent
source-backed player-visible milestones; accumulate related source research,
code and tests on a feature branch. Open PR and run required exact-head CI
only when a substantive reviewable integration is ready, not after each
disassembly insight or tiny helper. Resume an existing active branch rather
than reopening work. Never lower fidelity, privacy, source-proven behavior,
high-risk review or Windows11 acceptance standards to save CI.

LATEST USER OWNERSHIP DIRECTIVE (11 Oct 2026): The autonomous worker is
the primary implementer of ALL unfinished FM2001 features, INCLUDING the
previously Codex-owned R1 NEXT -> PPreMatch -> all modes -> PResults ->
management return. R1 partial code in PR #565 already merged; continue from
current main and DO NOT merge the stale Codex branch. Codex owns NO exclusive
code subsystems; only optionally engage it for cost-approved independent QA,
difficult bug reproduction and genuine Windows11 GUI playtesting when capable.
Do not wait for Codex availability or spend its quota on routine implementation
or PR review. Read research/WORK_OWNERSHIP.json and
research/WORKER_SCOPED_SOURCE_FIX_AUTHORIZATION.md.

MANDATORY UPDATED ORIGINAL SOURCE WORKFLOW (11 Oct 2026): Read
research/ORIGINAL_DRIVE_SOURCE_WORKFLOW.md and
research/ORIGINAL_SOURCE_LOCATOR.md. Daniel has already uploaded the actual
original extracted disc filesystem, including graphics/data/fonts/FMV, to
a verified private Google Drive folder; the original 4.7 MB executable and
all four required EAMail row sprites were independently byte-retrieved and
SHA-256 validated. FETCH ONLY THE SMALL ORIGINAL FILES RELEVANT TO THE ACTIVE
FEATURE directly from the connected Drive tree, checking hashes/provenance
as required. Do not automatically process 511 MB ZIP or 632 MB BIN, or ask
Daniel to extract these files again. The availability of original files
does NOT mean an execution sandbox, native GUI, player interaction, or Win11
acceptance has been verified. Continue source-first whole original player
journeys instead of isolated research/adapter churn.

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
active across chat/recovery boundaries rather than requiring a fresh user order.
Update the **agent-runtime heartbeat** about every ten minutes without
treating it as a main-commit/PR/CI deadline or a reason to end the session. When the conversation or execution
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
- update the worker-owned `agent-runtime` liveness/resume state roughly every
  10 minutes, independently of main/feature commits, with actual main head,
  active branch, evidence, blocker and exact next action;
- preserve meaningful intermediate research/code on the active feature branch
  when crash recovery needs it, not in a flurry of immediate main-branch commits;
- batch source research, code, tests, and chronological PROGRESS/CURRENT_STATE
  updates at substantive feature integration boundaries; material source
  corrections, high-risk changes and session-ending persistence are exceptions;
- open a reviewable PR after grouping the related milestone and use required
  exact-head tests/asset policy; avoid repeated pushes that restart CI;
- never leave substantial useful work only in chat;
- preserve/reuse authorized original FM2001 resources wherever practical;
- put intentionally imported original resources under original_assets/ with provenance per research/ASSET_POLICY.md;
- keep raw disc images, duplicate archives, temporary extraction dumps, and unrelated binary noise out of Git.

When a gate's completion criteria are satisfied, audit the gate, mark it complete in ROADMAP.md, update CURRENT_STATE.md/project_status.json, and only then move to the next gate.
```

## Why this prompt is short

A new session should not need a giant copied chat summary. If the prompt above is insufficient, the repository handoff files need improvement.


## Deferred blocker and out-of-order work policy

Roadmap gates are **verification milestones**, not a rule that all productive work
must stop when one gate contains a temporarily blocked local/private task.

When the exact next task requires unavailable local Windows GUI access, the
private executable/source archive, or a functioning execution sandbox:

1. Record the task as a deferred blocker with the exact missing evidence/action.
2. Do not mark that criterion complete and do not infer missing original behavior.
3. Continue the highest-priority independent **cloud-safe** task elsewhere in
   the current gate or a later gate.
4. Work ahead only where the task does not depend on the unresolved blocker.
5. Keep the earliest incomplete gate as the active validation gate until all of
   its completion criteria are actually satisfied.
6. Later-gate implementation/tests may advance out of order, but a later gate
   must not be declared passed if its own criteria or an earlier prerequisite
   remain unresolved.
7. Revisit deferred blockers whenever a sustained private/local execution path
   becomes available, and clear every deferred blocker before the relevant gate
   is closed.

Useful cloud-safe work-ahead examples include already-evidenced presentation
integration, deterministic/fail-closed tests, repository-side fidelity work,
long-duration/destructive simulation testing, packaging/audit tooling, and
documentation of verified behavior. Do not use this policy to bypass missing
source evidence, Windows graphical verification, or original-resource
provenance.

