# Gate 14: bounded original font-global and TextControl source leads

_Status: read-only private-source tooling, **not** new executable evidence or a completed Gate-14 control._

## Reason for this tool

The actual original-source trace in
`GATE14_FASTVIEW_TEXTCONTROL_SOURCE_ARGUMENT_TRACE_RECOVERY406.md`
proves TextControl index 0 maps to wrapper address `0x87BEA0`, and that
LeagueTable row/heading use selector 0. The original font object/file and
text/value producers remain unresolved. Selectors 1 and 3 have independent
prior source-verified identities; avoid retracing them as if they were unknown.

`reconstruction/gate14_fastview_font_global_source_trace.py` collects
bounded *raw candidate* neighborhoods for the five known global wrappers
and all six known direct TextControl callers, using the existing canonical
PE32 SHA-256 guard and private-output requirement.

## Private invocation

On a working, private source-capable machine, recover
`footballmanager.exe` from the authorized source locator and run:

```powershell
python reconstruction/gate14_fastview_font_global_source_trace.py `
  C:\private\footballmanager.exe `
  --output C:\private\gate14-font-global-candidates.json
```

The output contains proprietary bounded original executable bytes and
**must stay outside Git**. It is a search aid, not a binary proof. Each
raw little-endian occurrence is explicitly marked as an unaligned
candidate, including occurrences in non-code sections. A truncated
candidate list is explicit instead of being presented as exhaustive.
Callsite byte windows are similarly not CFG or stack-argument proof.

## Next adjudication, in order

1. On the hash-verified PE, independently decode aligned `.text`
   references/writes to wrapper `0x87BEA0` and source-trace its
   initialization. Show the font-object address, exact loader invocation
   and filename literal. Compare known, already-closed selector-1/3
   initializer paths as calibration, never as proof of selector 0.
2. Follow arg 4 of the known `0x51D8FB` row and `0x51DDF3`
   heading constructors to exact string/value producers and mutations.
3. Trace ScoreComposite owner-relative `[ebp+8]` and `[ebp+0xC]`
   selector values separately. No ScoreComposite style can be assumed
   from the selector-0 LeagueTable path.
4. Only then consider source-font pixel rendering or integration.

Gate 13 remains the earliest incomplete validation gate until the
private non-disruptive Windows 11 HWND/DPI receipt and normal menu/Squad
visual-latency acceptance exist. No game behavior, presentation pixels,
rendered fonts or Gate-17 scope changes are authorized by this tooling.

## Verification

Synthetic, proprietary-asset-free tests are in
`reconstruction/test_gate14_fastview_font_global_source_trace.py`.
They check candidate placement across executable sections, explicit
truncation, argument validation, and fail-closed claims. A passing synthetic
test does not prove which font the original selected.

## Recovery 408 verification and limits

PR #556 exact head `c0a45dd79e7da7d233c3d926319b82d155e36332` passed
the focused synthetic source-tracer CI (`37722466640`) and repository
asset policy (`37722466708`), then merged on main as
`65fc487a76a67a6e563683f060dfae90dd7e2fbd`.
The original private executable could not be run because the current
execution sandbox rejects trivial shell/Python processes with
`caas.internal.errors.ClientError`; no original font was identified
by these synthetic regressions. Full runtime CI and a private Windows 11
GUI acceptance run were not performed for this source-tracer checkpoint.

## Recovery 415 optional decoded-reference triage (8 October 2026 KST)

The raw-byte candidate report remains the default, unchanged evidence floor.
When the verified original PE is available in a functioning private sandbox,
an **optional** Capstone-based linear .text decode may prioritize literal
immediates and register-free absolute-memory operands mentioning the five
already-verified wrapper addresses. Example:

```powershell
python reconstruction/gate14_fastview_font_global_source_trace.py `
  C:\private\footballmanager.exe `
  --output C:\private\gate14-font-global-linear-candidates.json `
  --scan-linear-wrapper-candidates
```

This supplemental result appears under
`linear_font_wrapper_candidates_not_xrefs`. It deliberately excludes
register/index-relative displacements, non-code sections and Capstone
skipdata records. Each hit is classified
`linear_decoded_candidate_not_verified_xref_or_write`; the result
`verified_xref_or_initializer` remains false. Whole-section **linear**
decoding is not a control-flow graph and may cross inline bytes, so no
hit proves a real xref, an initializer, the font object, or its filename.
Candidate truncation is explicit. The flag defaults to off, and decoding
is never a condition for the canonical raw candidate report.

Source-independent synthetic tests exercise absolute-memory and literal
immediates, register-relative and data decoys, limits and invalid inputs.
These tests do not resolve the original font or render any score/table
text. Until execution can read the checksum-verified source, the index-0
font `0x87BEA0`, LeagueTable arg-4 producers and ScoreComposite variable
indices stay unresolved. This is independent Gate-14 tooling only; Gate
13 remains open for external Windows 11 acceptance.
