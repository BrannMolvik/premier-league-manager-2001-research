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
The full reconstruction regression and final build checks are still pending.

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
