# Recovery 525: original EAMail row art and native viewport source contract

**11 October 2026 KST. Gate 13 OPEN. Original Inbox and all Windows 11 acceptance still incomplete.**

## Verified source already in Git

This checkpoint reuses **prior verified** canonical original PE source evidence. Its executable identity from those source sessions was SHA-256
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.
It was **not** rehashed or run in Recovery525. Exact original owner/loader/child events, resource SHA-256 and sector positions were established by:

- `research/GATE13_EAMAIL_NATIVE_ROW_CONTROL_PIXELS_EVENTS_AUDIT_RECOVERY450.md`
- `research/GATE13_EAMAIL_NATIVE_ROW_DETAIL_AUDIT_RECOVERY439.md`
- `research/GATE13_MPMEAMAIL_DELAYED_DELIVERY_NEXT_PIPELINE_AUDIT_RECOVERY452.md`
- `research/GATE13_EAMAIL_SELECTED_USER_BINDING_RECOVERY518.md`

This new module `reconstruction/original_eamail_source_contract.py` pins four original
532×18 EA444 strips (normal, selected, highlight, disabled), each with original file size,
SHA-256, LBA and executable static loader owners. It validates the exact original
raw bytes, source `.444` descriptor and dimensions before any raster use. No raw
disc image, game executable, disassembly, screenshots, or replacement images are committed.

The same source module defines the separate native `PEAMail` panel-owner
`(0,148,800,530)`, panel-local list `(233,30,545,160)`, eight visible rows
at 20-pixel pitch, the original 532×18 row background and three child text
rectangles/IDs/producer offsets. Panel-local geometry **must not** be treated as a
verified final physical screen-space mouse hit rectangle.

The bounded viewport function accepts only an explicitly source-qualified
`PEAMail+0x68` filtered display tuple, checks exact
`max(0, count-8)` native scroll bounds, and preserves the input order.
It **does not** silently convert the raw `DBRUser+0x6B4` mailbox insertion list or
global pending `MPMEAMail` queue into native sorting/filtering. The bounded row
dispatch distinguishes a neutral native event on another row control (preview
selection) from the same row control (request original `PEAMMessage` detail).
These are source virtual event semantics, **not a claim about Tk mouse click,
double-click or keyboard gesture acceptance**. The function performs no
actual record status mutation or modal creation.

## Real private asset recovery when a byte-readable execution environment returns

The canonical original archive is recorded in `research/ORIGINAL_SOURCE_LOCATOR.md`.
After materializing that private archive, run the already maintained exact-path
extractor from the repository root (outside Git for the private outputs):

```bash
python reconstruction/gate13_source_inventory.py /PRIVATE/source.zip \
  --deep \
  --extract-path-file research/GATE13_EAMAIL_SOURCE_PATHS.txt \
  --only-explicit --require-all-explicit --hash-source \
  --extract-candidates-to /PRIVATE/eamail-staged \
  --output /PRIVATE/eamail-inventory.json
```

Before importing, compare the four raw files against the pinned SHA-256,
sizes and source header in `original_eamail_source_contract.py` (its validation
function expects the staging directory as the root). Use
`gate13_asset_import.py` with the inventory report and update
`original_assets/MANIFEST.md` only for authenticated bytes. If the original
Joliet entry letter case differs, inspect the inventory and resolve the
actual source spelling before importing; never alter file identities by guess.
The staged PRIVATE ZIP/BIN/ISO and mass extraction stay out of Git.

## Infrastructure blocker and present limitations

This recovery checked `main` at `4f039b13f9a018cde0cc1cb7e6444d93ff301cf4`
before implementation. `container.exec` failed `caas.internal.errors.ClientError`
on a trivial shell command, and `python.exec` failed on a simple print; there
was no new private executable scan, source-art extraction, local verification
or original Windows GUI acceptance. Relevant GitHub PR CI must distinguish
source-model unit verification from native/game acceptance.

**Not implemented by this change:** concrete
`EAMPlayerAskTransferListsub+0x3C` readiness; `0x613EE0`
due-event timing in Codex-owned NEXT/PResults; actual original
`PEAMail+0x68` five sort/filter controls, delivered populated row text
and status, original fonts and clipping, the PBg ID1 versus PMenu child0x65
normal host navigation, modal detail mutation and ESC return, 2–6 human manager
career, original proprietary saves, original asset bytes, or physical Windows11
playability. Tests are synthetic structural regressions against previously
verified original source addresses, not new original-world observation.

**NEXT:** (1) recover/extract four exact assets and the concrete readiness
virtual from the authorized original bytes on a functioning private sandbox;
(2) trace and implement full native `PEAMail+0x68` category/sort and real
message classes/row/detail actions; (3) wire both original header and PMenu
paths and verify normal player inputs across clubs, then physical Windows11.
Protect Codex R1 match-phase ownership. Gate13 and Gates14–17 remain OPEN.
