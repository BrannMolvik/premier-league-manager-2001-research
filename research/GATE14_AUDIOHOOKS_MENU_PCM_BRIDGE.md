# Gate 14 numeric AudioHooks to decoded menu PCM bridge

_Status: source-backed composition only. Gate 13 remains Codex-owned._

## Result

The repository now composes two independently recovered original behaviors
without adding semantic names:

1. `AudioHooks::0x5DBFC0` maps numeric event/state values to literal
   `menus.bnk` sample slots.
2. The exact canonical `menus.bnk` identity, BNKl v2 structure, sample codec,
   rate/channel defaults, and modern PCM decode are already source-backed.

`reconstruction/gate14_audiohooks_menu_pcm.py` joins those boundaries. Given
the byte-identical canonical `menus.bnk`, a numeric AudioHooks event and its
state value, it either:

- returns an explicitly silent result when the original numeric dispatcher does
  not call the menus playback helper; or
- locates the exact routed sample slot and decodes that source-owned sample to
  mono 22,050 Hz PCM, including a deterministic PCM SHA-256 identity.

The bridge rejects a bank whose size/hash does not match the canonical source
identity and fails closed if the routed slot is absent or cannot be decoded.

## What this does not prove

This checkpoint does **not** set any of these to true:

- semantic event binding;
- human-readable sample meaning;
- reconstructed UI/match event equivalence;
- Windows audio-device output;
- audible login/menu integration.

The numeric event IDs remain numeric. No sample is named by listening to it.

## Next steps

The private canonical executable caller trace introduced in PR #334 must still
identify the original senders and argument data-flow before semantic event
bindings can be promoted.

Independently, this decoded-PCM bridge can next be connected to a bounded modern
host audio-output seam. That host step must retain the numeric-only contract
until native sender semantics are source-proven, and audible Windows
verification is still required before Gate-14 login/menu audio integration can
be marked complete.

No proprietary BNK bytes or decoded PCM are committed to Git.
