# Recovery516 — private original Current Form alternate-row and root mouse trace

**11 October 2026 KST. Gate 13 remains OPEN.** This is *blocked-source investigation tooling*, not newly recovered native PE instructions and not a visible screen.

## Canonical reference and existing verified source boundary

Shipped authorized `footballmanager.exe` original PE32 SHA-256:
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.
The private disc/archive is accessible through the owner's ChatGPT Library. This recovery's
`container.exec` and `python.exec` returned `caas.internal.errors.ClientError`
even for trivial commands; **the original was not executed or newly disassembled**.

Existing first-hand analyses in
`GATE13_LEAGUE_TABLES_CURRENT_FORM_SOURCE_RECOVERY518.md`,
`GATE13_LEAGUE_TABLES_RESOURCES.md` and
`GATE13_FMRADIOTEXTSM_INPUT_RECOVERY515.md` independently prove:

- Original PLeagueTables event15 changes sort state to1 and selects native
  `0x4F4A10` Current Form ranking.
- Normal source sort0 creates a `0x4A8` row; sort1 instead allocates
  **`0x2B0` bytes**, enters **`0x4480A0`**, and produces **six** W/D/L/space
  cells, newest at right. These are different source row objects, not the seven
  standard P/W/D/L/F/A/Pts columns.
- `0x448430..0x44862F` accesses six child widgets and `0x651F60` writes
  text widget style/color words at child `+0x44/+0x46`. It does **not** prove
  their screen x/y/font or final raster. There is no justification for a generic
  29-pixel stat column substitute.
- `fmRadioTextSm::0x5D4AC0` may dispatch native selection to parent,
  but `0x5D4790` is a **broadcast**, not a hit test. `0x64FB20`/`0x64FB80`
  use distinct pointer-owner globals `0x984814`/`0x984818`. A point within a
  source 182×18 radio candidate rectangle does not establish acceptance
  through the original OS/window/panel/capture hierarchy.

Recovery515 merged PR589: immutable source-selected native Current Form rows
for complete primary nonPL and Premier0 histories. **It is a source-only data
bridge**; current ordinary renderer properly rejects a faux sort1 screen.

## Newly staged targeted source-recovery tool

`reconstruction/gate13_current_form_input_source_trace.py` consolidates the
precise unresolved native windows into a **private** original-checksummed trace,
including `0x4480A0` (bounded through `0x44862F`), source row factory, exact
text setup, `0x651F60` color setter, fmRadioTextSm dispatcher, child
broadcast, PLeagueTables event switch, rectangular pointer-owner checks,
clipped-child traversal and MyWindow message-loop candidate.

It optionally decodes direct CALL candidates in a **single pass** through
the original PE `.text` using Capstone. These candidates are not a CFG,
virtual-call ownership proof or OS input chain. It also records raw global
address occurrences explicitly classified as **not decoded xrefs**.

On an authorized environment that can read the privately extracted original
PE32 (for example the existing private working scratch path), invoke:

```bash
python reconstruction/gate13_current_form_input_source_trace.py \
    /path/to/private/footballmanager.exe \
    --output /path/to/private/current-form-input-source.json \
    --disassemble --scan-direct-calls
```

The output must be **outside the Git repository** and remain private.
The executable's exact canonical hash is checked; neither the source game nor
the native executable is run. Do not push the private JSON, disassembly or raw
binary bytes to Git. Normal CI uses **synthetic PE** tests only.

## Required manual adjudication, not inferred by this tracer

1. From `0x4480A0..0x44862F`, trace each of six `row+...` children to its
   actual `0x6503F0/0x64F380` constructor and post-constructor retained
   `+0x08/+0x0C/+0x10/+0x14` bounds. Resolve font owner, source text style,
   RGB/indexed source color, overdraw/clip and row-list (270,184,477,384),
   16-pixel step. Pay attention to native parent offsets and per-cell
   setup order; a 0x651F60 style write is **not geometry**.
2. Trace actual `WM_LBUTTONDOWN/WM_LBUTTONUP` (and pointer hover/press)
   through the original Windows HWND/WndProc, currently active PLeagueTables
   panel object, clipping and pop-up z-order, capture transitions and the two
   cached child owners. Relate the genuine accepted pointer event to
   `0x5D4790 → fmRadioTextSm::0x5D4AC0 → PLeagueTables::0x448C40`
   event15. A raw address reference, pointer hit or broadcast alone does not
   close this path.
3. Keep result six-slot source text interpretation distinct from actual
   eCText raster/bitmap/font, scroll state and physical Windows11 1×/1.5×
   pointer acceptance. Source-validate before linking the new PR589 data view
   to a separate alternate row presenter.
4. Secondary-calendar scope still separately requires real historical
   `0x947AF0` match ownership, persisted event identity and dynamic
   `DBRClub+0x74` mode. Do not silently route mode2/3 through primary.

No original binary/data is committed. The trace's result schema explicitly
keeps `six_widget_row_geometry_and_font_source_verified_by_this_trace`,
`root_wm_lbutton_to_radio_event15_source_verified_by_this_trace`,
`original_six_widget_rendering_integrated`,
`original_league_tables_mouse_input_integrated`,
`gate13_complete` and `gate17_complete` **false**.

**Next:** run/checksum this tracer when private source execution is functioning,
manually adjudicate exact row and root mouse chains, then implement a fully
source-backed alternate Current Form presenter and a proper ordinary input route
in coordination with the Codex-owned central Tk match-phase surface. Advance
to next Gate13 area only as source permits. Gates 13–17 and physical Windows11
release remain OPEN.
