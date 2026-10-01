# Gate 13 TeamSelect native hierarchy trace

_Date: 1 October 2026 KST_

## Evidence boundary

This checkpoint comes from bounded Capstone disassembly of the canonical
original executable (SHA-256 `833bf95e...cc3`) and canonical database records.
Private instruction reports remain outside Git. No executable, disc image,
raw dump, or original resource bytes are committed.

## Recovered owner graph

RTTI identifies the screen as `PMain@TeamSelect` (type descriptor `0x81EC10`,
vftable `0x7C7650`). Its native children are `LeagueBtnGrp@TeamSelect`
(`0x7C7230`, nested `Btn`/`Bar` at `0x7C72D0`/`0x7C7388`) and
`TeamBtnGrp@TeamSelect` (`0x7C75B0`, nested `Btn`/`Bar` at
`0x7C74F8`/`0x7C7440`).

Setup `0x4D7CC0` creates 16 league/country groups at `(20, 78 + 30*i)`,
IDs `1..16`, object offsets `0x2A24 + 0x4C*i`. It creates 24 club groups at
`(581, 78 + 20*i)`, IDs `0x11..0x28`, object offsets `0x2EE4 + 0x40*i`.
The league groups bind the recovered exact `choice_league_but_anim.444` and
`choice_league_but_bars.444` wrappers.

## Native contents and navigation

For English/default locale, constructor `0x4D9290` stores country IDs in this
order: England 26, Scotland 66, Germany 33, Italy 40, Spain 73, France 31,
Holland 24, Belgium 9. Names are resolved from canonical database records.

Population routine `0x4D9C70` binds country rows to those records. Expanding a
country rebuilds the same 16-control list with applicable competition rows.
Clicking a competition calls `0x4DA0F0`, which scans canonical club records,
sorts visible club names, binds at most 24 club controls, and hides unused
rows. Event owner `0x4DA480` routes Back (`0x29`) to PStartMenu and Start
(`0x2A`) through selected country and competition identity. English activation
`0x4D9AA0` selects England and its first resulting competition row.

This proves a two-stage native hierarchy, not a flat developer club picker:

`country -> competition -> club -> Start`

## Still open

This does not claim the exact competition inclusion/order for every country,
the visual state-to-source-frame transforms, the final club-row selection
write, or live hierarchy rendering. Those remain required before replacing
the inert hierarchy in the Windows audit. Gate 13 remains active.
