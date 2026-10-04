# Gate 14 audio-bank ownership trace

_Status: independent Gate-14 source result while Gate 13 remains Codex-owned._

## Result

Private tracing of the canonical executable now source-closes the loader slots
and playback-routing ownership for the four embedded FM2001 `.bnk` resources:

| Slot | Bank | Loader owner | Playback routing |
| ---: | --- | --- | --- |
| 0 | `menus.bnk` | `0x6D0160` | `AudioHooks` dispatcher -> `0x6CFF10` |
| 1 | `game00.bnk` | `0x6D0160` | generic runtime SFX callback type byte 0 |
| 2 | `playercalls.bnk` | `0x6D0250` | generic runtime SFX callback type byte 1 |
| 3 | `Advice.bnk` | `0x6D02F0` | direct playback helper `0x6CFFA0` |

This is stronger than filename inventory, but it does **not** prove that any
bank is music, crowd, commentary, a particular menu action, or a particular
match event.

## Shared loader and slot storage

All four banks pass through shared loader `0x6D01F0`.

That routine builds the runtime path using source format string
`%s\\DATA\\AUDIO\\SFXS\\%s`, loads the bank, and stores the resulting handle
at `0xA25988 + slot*8`. The middleware bank identifier used by playback is
stored at `0xA2598C + slot*8`.

The source initialization paths are:

- `0x6D0160`: loads `menus.bnk` as slot 0 and `game00.bnk` as slot 1;
- `0x6D0250`: loads `playercalls.bnk` as slot 2;
- `0x6D02F0`: loads `Advice.bnk` as slot 3;
- `0x6D0AC0`: calls all three loader owners in sequence during the broader
  audio/application initialization path.

## menus.bnk playback ownership

RTTI resolves vtable `0x7D73EC` to `.?AVAudioHooks@@`.

Its first virtual target is dispatcher `0x5DBFC0`. That function maps its
incoming hook/event arguments to fixed numeric sample indices and calls
`0x6CFF10`. `0x6CFF10` reads the bank identifier specifically from slot-0
global `0xA2598C`. Therefore this dispatcher is executable-proven to play
samples from `menus.bnk`.

This checkpoint deliberately calls it the **AudioHooks event/sample path**.
The higher-level meanings of every numeric hook/event code and bank sample are
not yet source-closed, and `menus.bnk` is not promoted to "menu music."

## game00.bnk and playercalls.bnk runtime SFX routing

Generic callback `0x6D0050` is installed through the audio callback setup
around `0x6D0480 -> 0x7255A0`; wrapper `0x6D0030` forwards into it.

Its source bank selection is explicit:

- callback type byte 0 -> slot 1 -> `game00.bnk`;
- callback type byte 1 -> slot 2 -> `playercalls.bnk`;
- other type values use a caller-supplied bank slot and are not promoted to a
  fixed mapping here.

Thus these two resources are directly owned by the runtime SFX callback path.
The exact event-to-sample semantics remain separate work.

## Advice.bnk playback ownership

Playback helper `0x6CFFA0` reads the bank identifier from slot-3 global
`0xA259A4`, proving it plays from `Advice.bnk`.

The direct caller at `0x6CEC22` invokes it only after an owning object's
virtual result equals 1, passing that object's field `+0x194` as the sample
index. This proves a distinct Advice-bank playback path but does not yet justify
a higher-level spoken-advice/menu/help label for those sample indices.

## Fidelity boundary

`reconstruction/gate14_audio_bank_ownership.py` records only the executable
facts above. Every bank keeps role semantics, exact sample semantics, and music
semantics false.

Gate 14 therefore still requires exact sample/event bindings for applicable
player-visible sounds, separate proof for original login/menu music if it is
not supplied by this SFX-bank family, and resource playback integration only
after the required ownership/sample identity is source-closed.

No proprietary executable bytes or private disassembly are committed.

## Provenance

Private tracing used canonical executable SHA-256:

`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`

re-extracted from the authorized 511,121,336-byte source ZIP.
