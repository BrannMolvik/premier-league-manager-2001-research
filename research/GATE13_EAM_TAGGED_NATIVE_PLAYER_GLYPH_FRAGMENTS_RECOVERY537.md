# Recovery537 — exact original Inbox player-label tag fragments (alpha only)

The original native `EAMPlayerAskTransferListsub` caption producer `0x5CE735/0x5CE784`, from the private hash-verified shipped PE SHA-256 `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`, formats the row ID2 player text from **two exact source literals**:
- negative association `<T+P>%s<T->`;
- nonnegative association `<T+P>%s<T-> @ <T+C>%s %s<T->`.

These literals are already source-pinned in `reconstruction/original_eamail_player_name.py`, including native club short-name/user caption and English `Football Club` suffix selection. Original `PMessageRow::0x46E737` creates native eCText ID2 at (38,0,215,16) relative to each 532x18 Inbox strip. The original renderer `0x5D75B0` initializes font object `0x9269F0`, authentic `Zurich_BdXCn_BT_16pixel.fnt`; native tags T+/T- switch parser state but unresolved buffer edits and P/C state affect final color and placement. The associated font loader/glyph atlas were independently verified for other management screens.

`reconstruction/original_eamail_tagged_player_masks.py` now recognizes only those exact two C-format **source label templates**, validates CP1252 and impossible nested/unknown tags, and retains byte offsets plus original-font alpha masks for:
- original T+P player fragment;
- native plain separator ` @ ` where present;
- original T+C club plus localized `Football Club` suffix where present.

The new `native_visible_player_fragment_masks` binds this staging layer to **real current-registered-manager delivered-only original Inbox child ID2** rows, checks real 8-row owner/field IDs/geometry and never fabricates another user's or pending mail. Unqualified source texts are rejected or absent records skipped. Tests exercise exact native literal assembly, real delivered human source, malformed tags, and absence of visible messages. The registered-user source data is preserved unmodified.

**Critical boundary:** Source string *template fragments* and authentic font alpha are NOT proof of eCText final colored glyph runs. Native in-place `0x650650/0x6506A0` text buffer/caret changes, T+P/C color values, x/y baselines, clipping and bit4 gating remain unresolved. Do not join alpha fragments, strip tags for actual draw, paint proxy colors, mutate native delivered mailbox status, or mark this feature VISIBLE-ACCEPTED. Complete the native renderer source trace, show original row text in the ordinary game host with proper preview/dialog/actions and verify true Windows11 GUI. Gates13–17 remain OPEN.
