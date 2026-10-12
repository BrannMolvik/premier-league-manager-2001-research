# Autonomous FM2001 worker: milestone batching and low-cost recovery policy

**User-approved, 12 October 2026.** Applies immediately to all worker activity
through Gate 17. The goal is **more original-game functionality per review/CI
cycle**, not fewer safety checks. This policy supersedes earlier instructions
to make a separate `main` commit, PR, and CI run immediately after every minor
verified source finding or every approximately 10 minutes.

## Three different persistence layers — never conflate them

1. **Recovery liveness: keep approximately the existing 10-minute cadence.**
   While genuinely working, update **only the worker-owned `agent-runtime`
   branch** (`research/AUTO_CONTINUE_STATE.json`) with `mode=continuous`,
   `status=working`, the **current actual main HEAD**, and a truthful,
   sufficiently specific `active_task` / source evidence / blocker / next
   action to resume. Do not mark `completed` before Gate 17 or alter recovery
   generation except for actual recovery. Preserve `checkpoint_target_minutes=10`,
   `stale_after_minutes=15`, existing grace/cooldown behavior and the
   extension's true worker-owned heartbeat semantics. Keep this runtime update
   light and do not trigger GitHub Actions.
2. **Recoverable investigation/development:** use a **dedicated, current-main
   feature branch** to preserve actual work and grouped research when meaningful
   or before a risky operation, chat end, expected timeout or subsystem switch.
   If a long trace is still unresolved, update the runtime checkpoint with
   concrete progress/next address; save valuable intermediate evidence on the
   feature branch as needed, but **do not commit routine fragments to `main`**.
   Never leave essential source/progress only in chat. If a local workspace
   exists, use it for intermediate iterations; if using only GitHub write
   tools, commits to the *unopened* feature branch are acceptable recovery
   checkpoints and will not automatically run PR workflows.
3. **Public integration and milestones:** open or update a PR, run applicable
   CI, and merge only when a **cohesive original-feature milestone** is ready
   to review and validate. Usually combine related original disassembly,
   asset identity, implementation, tests, regression/counterexample work
   and a short provenance receipt in **one PR**. Include updated
   `research/CURRENT_STATE.md` / `research/PROGRESS.md` only at genuine
   integration or materially changed resume points. Do not make a separate
   main-branch administrative checkpoint after every verified finding or PR
   unless necessary to correct a material incorrect canonical claim.

## What counts as a coherent milestone?

Prefer **player-visible functionality or a complete, independently useful
and safely integrated original-derived component** over tiny isolated helpers.
For example, original SupportStart seven rows, selecting staff, Apply/Cancel
semantics, normal Game UI path and corresponding state/persistence tests belong
together where safely source-proven. Similarly, group connected Inbox source
sprites, data/selection, preview and routing into feature-sized integration.

**Do not invent missing source behavior merely to finish a milestone.** If a
genuine blocker prevents a full screen/journey, define a source-bounded
independently useful partial milestone, label its limits and open one reviewable
PR when warranted. High-risk, cross-system or large changes may require
separate PRs for safe review; bugs/regressions and security/privacy fixes may
justify an immediate small PR. No forced minimum PR size, no arbitrary
fixed-hour delay and no bar on urgent corrections.

## Avoid unnecessary GitHub Actions

- **Before PR creation:** do as much source analysis, iteration and fast
  targeted testing as possible privately/in a local workspace or feature
  branch; if the shell is unavailable, prepare and review the grouped source
  and tests on the branch. The source tree and required checks remain
  authoritative regardless of tool availability.
- **Open the PR when the grouped milestone is ready for verification.**
  GitHub's `pull_request` triggers can run on PR creation *and every
  synchronize/push*, even on drafts. Avoid opening a draft solely to store
  work. Avoid rapid successive branch updates after opening a PR; finish the
  coherent change before triggering expensive workflows. A draft PR with
  disputed source evidence stays blocked and must not be merged just because
  CI is green.
- **When tests run:** run impacted focused tests and asset/privacy policy
  checks at the actual integration head; run the **full suite** whenever
  dependencies, save/RNG, match lifecycle or broader integration risk warrants
  it and at gate/release audits. Do not skip required CI or genuine Windows 11
  GUI acceptance to reduce billed minutes. If a PR head changes materially,
  run required checks on the **new exact head**, not a stale green head.
- **Remote vs local:** use local quick regressions whenever available; remote
  CI is valid for code execution only when the exact-head workflows and their
  outcomes are actually inspected. A build/green suite is not original game
  behavior proof or a hands-on Windows 11 gameplay test.
- **No heartbeat CI:** runtime updates should not trigger workflows;
  do not manually dispatch workflows for documentation heartbeats, trivial
  source traces or no-op changes. Review trigger scopes only if needed;
  don't disable mandatory protections or weaken source-proof requirements.

## Current code-review and fidelity rules stay mandatory

Follow `research/ORIGINAL_DRIVE_SOURCE_WORKFLOW.md` and
`research/ORIGINAL_BEHAVIOR_FIRST_POLICY.md`. Use verified original files,
not fabricated approximations. Preserve full original game scope and
continuous worker ownership (Codex optional and cost-approved only).
No original proprietary archive, huge extraction or uncontrolled original
assets may enter Git. No force pushes, direct game-code merges to `main`,
unaudited high-risk changes, or unsafe merges into another active worker.
Review source evidence, regression/counterexamples, exact-head required
CI, asset policy, branch mergeability and external reviewer objections before
merging. If verification isn't available, carry a precise blocked/unverified
state instead of declaring success.

## Recovery and reporting when work is unfinished

- At each liveness update, `active_task` should state: current branch/PR (if
  any), latest **main** SHA, current original source proof, implementation
  progress, unresolved inputs and the next executable action. Avoid long
  repetitive histories and keep runtime updates small.
- If the chat recovers mid-feature, continue that **same** work branch and
  milestone rather than opening a redundant PR or recapping old work into a
  flurry of commits.
- Update `CURRENT_STATE.md`, `PROGRESS.md` and any original-source evidence
  notes **together at the next meaningful integration boundary**, or sooner
  for a correctness-critical correction or session-ending persistence need.
- Do not treat commits, PR counts, test counts, source hashes, or ten-minute
  heartbeats as success measures. Track closed original player workflows and
  objectively verified gaps as the actual outcomes.

**Operational rule: keep the recovery heartbeat frequent; make code/research
commits when recoverability demands them; create PRs and run CI for genuinely
reviewable feature milestones.**
