# Gate 14 audible Windows readiness bridge

_Status: cloud-safe capability plumbing; canonical audible-Windows readiness remains false until a genuine private receipt is strictly replay-validated._

## Purpose

The real-Windows numeric menu-audio audit and the strict private-receipt
validator already prove separate layers:

1. a private Windows run can record one explicitly heard numeric FM2001 menu
   sample; and
2. the repository can fail-closed validate that receipt and deterministically
   replay its canonical `menus.bnk` identity, numeric AudioHooks route, literal
   sample slot and decoded PCM identity.

The readiness model previously had no independent place for that evidence.
`reconstruction/gate14_audio_readiness_bridge.py` now connects those layers
without treating audibility as semantic integration.

## Bridge contract

`apply_validated_windows_menu_audio_receipt(...)` accepts:

- the exact `Gate14ReadinessEvidence` state;
- the original private schema-1 audit receipt; and
- the canonical private `menus.bnk` bytes.

The bridge invokes `validate_windows_menu_audio_receipt()` itself. It does not
accept an arbitrary caller-supplied "already validated" dictionary as proof.

Only after the strict validator confirms source identity, deterministic numeric
route replay, decoded PCM identity and the prior human audibility observation
does the bridge set:

- `audible_windows_verified = true`.

It preserves all unrelated readiness fields exactly, including:

- `audio_event_binding_recovered`;
- `login_menu_audio_integrated`;
- FastView raster/frame state;
- chant semantics;
- 3D choreography; and
- recognizable-match-workflow verification.

## Readiness model change

`Gate14ReadinessEvidence` now tracks `audible_windows_verified` separately.

Canonical repository readiness keeps it **false** because hosted CI does not
constitute a genuine human-heard Windows receipt. The blocker list therefore
includes `audible_windows_output` until private evidence is validated.

`login_menu_audio_integrated` is now structurally forbidden unless all of the
following were independently established first:

- audio-bank ownership;
- playback entrypoints;
- sample decode readiness;
- semantic event binding; and
- audible Windows verification.

The official original-audio criterion likewise requires all three final
runtime-facing facts: sample decode, event binding, and audible Windows evidence
behind actual login/menu integration.

## Evidence boundary

This checkpoint does **not** recover event names, sample meaning, modern UI-event
equivalence, login/menu wiring, general device-output behavior, or Gate 14
completion. It only prevents a future genuine audible receipt from remaining
orphaned from the fail-closed readiness model, while ensuring that receipt
cannot promote semantic or UI integration claims.
