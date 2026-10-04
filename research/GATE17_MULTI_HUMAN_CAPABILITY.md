# Gate 17 multi-human capability audit

_Status: independent cloud-safe work-ahead while Gate 13 remains the earliest incomplete validation gate._

## Source requirement

The recovered TeamSelect path is not single-manager-only.

Canonical executable tracing in `GATE13_TEAMSELECT_USER_SELECTION_TRACE.md`
shows that selecting a club creates and appends a user immediately. The clicked
club is bound into that user, deselection removes that user and restores the
displaced manager state, and TeamSelect Start consumes the already-created user
list.

The recovered saturation path at `0x4DA4D0` includes the global user-count
condition `0x8755E4 >= 6`. Six is therefore the source-proven hard global
maximum for simultaneous human users, subject to the original's potentially
tighter manager-availability condition.

The final Gate-17 evidence contract already requires
`multi_human_management=true` and
`simultaneous_human_users_verified=6`.

## Repository-side audit

`reconstruction/gate17_multi_human_capability.py` makes the intermediate
implementation boundary machine-readable instead of relying only on the final
external receipt.

It measures five independent conditions:

- TeamSelect can retain the source-required number of simultaneous selections;
- the gameplay backend can represent the source-required number of human users;
- TeamSelect Start can hand multiple selected users into gameplay;
- those users share one live runtime rather than independent/divergent worlds;
- internal save/reload preserves the multi-human state.

The audit fails closed with distinct blocker codes for every missing dimension.
The required simultaneous-user count defaults to the source-proven value of
six and rejects non-exact integer/boolean capability inputs.

## Current canonical boundary

`run_current_multi_human_capability()` deliberately reports the present
repository state:

- TeamSelect selection capacity: **6**;
- gameplay simultaneous human-manager capacity: **1**;
- multi-human Start: unavailable;
- shared multi-human runtime: unavailable;
- multi-human save/reload: unavailable.

This is not a claim about the original game. It is a diagnostic of the current
clean-room port against the recovered original requirement.

## Full-scope preflight integration

The Gate-17 full-scope implementation preflight now requires an exact
`MultiHumanCapabilityAudit` in addition to human-scope, runtime-owner and
runtime-progression audits.

An otherwise green repository-side preflight remains blocked by
`multi_human_capability_incomplete` while the current single-manager backend
is in place. The preflight also exposes the required/supported simultaneous-user
counts and the detailed multi-human blocker codes.

This prevents `ready_for_full_runtime_validation=true` from being emitted
merely because every League owner and annual progression route has become
available while a separate shipped multi-human capability is still absent.

## Non-claim

This checkpoint adds no second human manager, scheduler behavior, save schema,
or gameplay implementation. It does not infer how simultaneous human fixtures
are ordered or resolved. Those behaviors must be implemented and validated
without fabricating source semantics before the capability audit can become
green.
