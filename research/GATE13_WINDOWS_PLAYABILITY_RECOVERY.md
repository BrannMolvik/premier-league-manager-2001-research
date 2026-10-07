# Gate-13 Windows playability recovery — 7 October 2026

Branch `codex/gate13-windows-playability-recovery`, based on fetched main
`1a580ea7f38a0fba608237b21dd9e21d9f5661e3`, preserves disjoint worker changes
and integrates verified local checkpoints through `01f866bf`. No main merge,
agent-runtime change, Settings implementation or Gate-14 work is performed.
Issue #482 remains open; its newest external evidence rejects artifact
11464212544, which does not contain the later local DPI/name repairs.

## Retained demonstrated repairs

The previous local normal frozen run completed both startup clips, reached the
centered source menu and selected Conference/Southport. Mixed parent/child DPI
awareness caused inner video cropping: system-aware initialization before Tk
restores the correct WPF physical-pixel/DIP conversion. The 320x480 source →
640x480 nearest horizontal duplicate and (80,60) destination remain unchanged.
Startup Escape/F11/Alt+Enter cannot mutate fullscreen geometry; source skip
semantics remain unresolved and are not invented. See
`GATE13_PLAYTEST_RENDERING_DIAGNOSIS.md` for the native/A-B evidence and explicit
DBRPlayer constructor initialization that restores omitted player names.

## Measured interaction stalls and bounded fix

Actual verified Windows data/production-host raster code was exercised with
inert test Tk widgets: **no real window, original launch, audio or frozen
execution**. Consequently these are code-path timings, not packaged UI
acceptance and not measurements of real Tk PhotoImage allocation.

| Boundary | Before | After pinned staging/cache |
| --- | ---: | ---: |
| New Game → TeamSelect | 19.027 s | 0.844 s |
| Southport Start/backend selection | 3.093 s | 1.383 s |
| Squad resource-family wait | 4.693 s | 0.048 s |
| First Squad draw | 15.881 s | 0.076 s |
| Repeated Squad redraw, three samples | 0.139–0.193 s | 0.017–0.018 s |

The identified large costs are synchronous EA444 decoding of the two
TeamSelect backgrounds (7.993/8.373 s), management background decode during
the first UI draw, and repeated lossless PNG compression before the existing
Tk image cache can be consulted. The PMenu popup was also fully rasterized
when closed. Profile attributed 0.308 s of three repeated redraws to zlib.
Start/backend construction was **not changed**: its observed reduction is
run-to-run variation, not an optimization claim; a roughly 1.4 s synchronous
construction boundary remains.

`gate13_ea444_staged_rasters.py` now pins a lossless bundle for the exact
33 immutable source art paths (including byte-identical PMenu aliases).
Every source owner retains its original hash/size/geometry gates; hits also
require exact TQIA and original/fixed quantization identities. The code-pinned
manifest, compressed payload, dimensions, offsets and every RGBA hash are
verified. Known-bundle corruption fails closed. Unknown/custom art still uses
the original decoder, not a guessed image. No pixels, alpha, native ordering,
frame selectors, captions, simulation state or RNG ordering are altered.
The reproducible generator verifies the canonical executable and all source
hashes; optional incremental reuse accepts only a code-pinned prior bundle.

The host caches RGBA before PNG compression and invalidates scaled Tk images
on viewport change. Cache keys include dimensions and pixel content, so live
text/art changes do not reuse stale pixels. The closed popup is not rasterized.
97 focused tests passed with three expected skips before the next header slice.

Private evidence: `work/playability-{before,final-staged}.{json,profile.txt,log}`,
`work/gate13-rasters-expanded.log`, `work/playability-staged-focused.log`.
The full reconstruction regression and final build checks are recorded below
when complete; offline profiling does not qualify Windows acceptance.

## Missing management club title: bounded producer and presentation repair

The host omitted application-owned TextControl+2A4, despite drawing the MENU
compound. Canonical executable SHA-256 is
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.
Setup `43062D..430668` binds font object `8F21B0`, rect `(172,1,378,32)`,
flags `2102`, color `FFFF`. Loader `6043AA..6043F7` names the original
`Fonts/Zurich_BdXCn_BT_32pixel.fnt`, not a modern substitute. Its authorized
archive extraction is 136128 bytes, SHA-256
`27b5e4c42518bef0e000a5878939f859c2c1b1e635e4fd200752e23c468c3e36`,
atlas 2422x34, native line height 37.

Refresh `432B44..432B66` reads current user+5B4 -> `40DA50`. That getter
prefers `403600`'s nonempty user+D0 caption, otherwise DBRClub+8 source name.
TeamSelect `4D8EEC -> 413BB0` creates the user through `424CA0`; `424F3F`
explicitly writes byte+D0=0. The traced setup `4258D0..425F8C`, registration
`426090..42621D` and directly relevant `42C400` / `42C6B0` retain it, rather
than assuming allocator bytes. The current ordinary reconstructed host has
no renamed/imported-user-caption producer. The live bridge explicitly retains
the proven fresh empty caption; unknown legacy view contexts remain withheld.

`6522A4..6522BB` right-aligns by measured source-font width. `65230B..65232A`
uses half control height minus half native line height, giving y=-1 before
control clipping, not visual centering by glyph bounds. Southport is 90px wide;
the clipped layer is `(460,1,90,32)`. Production loads the hash-qualified font,
and draws this layer through the ordinary management host's existing scaled
RGBA cache. No guessed date/header statistic, roster selector or advance/play
control is introduced. Unit tests cover explicit custom-caption precedence,
unknown-context withholding, exact alignment/clipping, packaged font identity
and live host binding. Private trace receipts remain outside Git:
`work/management-title-{fresh-user,setup-qualified,final}.txt`.

## Regression comparison / acceptance limit

Historical `72aedde1` introduced first-screen raster/Tk reuse, and `9609c00e`
preserved fast startup plus deferred management resources. Those changes are
still present; no lost-cache revert is warranted. Later cold TeamSelect and
management art decode, before the cache lookup, explains the reproduced stalls.
The earlier backend/prototype gameplay test is not proof that the source-owned
ordinary management host binds advance/play. This branch does not replace it
with the generic development notebook or claim that background calculation
proves ordinary user play.

The extracted local unsigned executable was denied by Windows Code Integrity
3033/3077 under policy `{0283ac0f-fff1-49ae-ada1-8a933130cad6}`. No alternate
launch route, security changes, exceptions, Azure or paid signing are attempted.
Building and inspecting a candidate remains possible, but personal execution
of the new frozen candidate and external readiness cannot be claimed until
an approved executable trust/distribution route is available. Gate 13 stays open.
