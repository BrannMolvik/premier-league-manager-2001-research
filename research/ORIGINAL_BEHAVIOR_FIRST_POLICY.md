# Original-Behavior-First Implementation Policy

## Purpose

Until Daniel explicitly ends this freeze, this project is **not doing gameplay, UI, visual, or quality-of-life modernization**. The active objective is to make the shipped **The F.A. Premier League Football Manager 2001** behave and present like the original game while running reliably on Windows 11.

Windows 11 compatibility work may replace incompatible implementation mechanisms, but it must preserve the original user-visible behavior, timing semantics, navigation, data, rules, assets, and presentation unless direct evidence proves that an original mechanism cannot be retained.

## Mandatory source-first gate

Before implementing or changing any game behavior, presentation, control, timing, navigation, layout, asset transform, simulation rule, or input semantics, the worker must first answer and persist:

1. **What did the shipped original do?**
2. **What evidence proves it?**
3. **What is still unknown?**
4. **What is the minimum Windows-11-compatible implementation that preserves the proven original behavior?**

Acceptable evidence includes, as appropriate:

- verified original executable/disassembly/decompiler/control-flow evidence;
- verified original resources, data files, layouts, strings, audio/video, configuration, or file formats;
- direct observation of the authorized original game in a source-valid environment;
- already-established repository findings whose provenance is still valid.

Unit tests, current reconstructed behavior, prior worker assumptions, generic UI conventions, modern best practices, visual similarity, or a previous reconstruction are **not** evidence of original behavior by themselves.

## Hard audit gate: unverified means unsafe to build on

Daniel's 9 October instruction applies equally to existing research, prior
closure claims, sub-agent findings and new work: a finding is NOT established
until fully verified for its exact claimed scope. Repetition, agent agreement
and passing reconstruction tests do not establish original behaviour.

"100% certain" means no unresolved assumption required by the bounded behaviour
being implemented, not absolute certainty about the whole game. Unknown is not
proven false; it is untrusted and cannot be an implementation dependency.

Before accepting a finding, require:

1. Verified original identity, applicable context, owner, actual producer,
   caller/reachability and lifecycle; distinguish native behaviour from probe
   adaptations, injected fixture inputs and emulated/stubbed leaves.
2. Reproducible original evidence and expected outputs, including relevant
   boundary cases. Expected outputs must not come from the implementation
   being audited.
3. Independent challenge/reproduction and a deliberate search for counterexamples.
   Repeating the same unsupported statement is not independent verification.
4. Actual application input/output ownership and ordinary interaction/render/
   persistence checks for integration acceptance. A bounded function proof
   does not certify an integrated or visible path.
5. A record of scope, evidence, assumptions/unknowns, dependent files/behaviours,
   reviewer and status. Keep SOURCE-VERIFIED, INTEGRATION-VERIFIED and
   VISIBLE-ACCEPTED separate; never silently promote one into another.

On conflicting evidence, counterexamples or unresolved required inputs: mark
the claim disputed/unverified, stop dependent work and quarantine its acceptance.
Preserve user changes and the last verified snapshot. Recheck the original and
affected dependency chain before proceeding; do not patch around the symptom
or perform a broad rollback without evidence. Independently verified unaffected
work may continue. See `GATE13_ORIGINAL_BEHAVIOUR_RECOVERY_PLAN.md`.

## Unknown means unknown

If original behavior is not yet established:

- investigate the original first;
- label the boundary unresolved;
- fail closed or leave the behavior absent where appropriate;
- do **not** fill the gap with a plausible modern behavior and later describe it as original;
- do **not** infer semantics merely because an implementation would be convenient.

A hypothesis may guide an experiment, but it must not become production behavior without supporting evidence.

## Compatibility-only freeze

Allowed now:

- runtime/API replacements required for Windows 11;
- wrappers/converters needed to make original resources work;
- performance fixes that remove accidental reconstruction overhead while preserving original behavior;
- packaging, dependency, DPI/display, audio/video, input, filesystem, and security/trust compatibility work needed to run the game;
- bug fixes that restore behavior already proven from the original.

Deferred until Daniel explicitly authorizes modernization:

- new menu items or workflows;
- new settings/options not present in the original;
- upscaling modes and visual enhancement features;
- redesigned UI/UX;
- convenience or quality-of-life changes;
- altered game rules, balance, timing, controls, or presentation for modern preference;
- aesthetic substitutions when original assets/behavior are available.

## Existing modernization work

Any modernization already merged before this freeze is **not evidence of the original game** and must not become a dependency for source reconstruction. It should be isolated so that the original baseline remains recoverable and testable.

The previously added Settings extension is now **deferred**. It is not a Gate-13 requirement and must not delay or alter restoration of the original menu. Before the next external acceptance candidate, the worker must ensure that the normal/default tested path presents the original menu baseline without requiring or depending on that extension. Preserve the work for a later explicitly authorized modernization phase rather than expanding it now.

## Review requirement

Every implementation PR that changes game/runtime behavior should state:

- original-behavior evidence used;
- exact compatibility problem being solved;
- whether user-visible behavior changes;
- unresolved source boundary, if any;
- tests that distinguish preserved original behavior from reconstruction convenience.

A PR that cannot answer those questions is not ready to merge.
