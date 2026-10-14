# Recovery621: original DBRPlayer disciplinary byte-state persistence

14 October 2026 KST. Canonical original private footballmanager.exe identity 4,714,541 bytes, SHA-256 833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3. Static native evidence and bounded original source callbacks are recorded in research/GATE13_R1_V3C_SIDE_WORLD_CLEAR_RECOVERY618.md (PR717 merged main). No original executable launch or source bytes in Git.

## Problem and original reference

The current modern RuntimePlayer fields discipline_yellow_total, discipline_yellow_cycle, suspension_matches_remaining, suspension_effective_date are useful reconstruction-side fields but not proven identical to original native DBRPlayer+0x139/+0x13A/+0x13B/+0x13C/+0x13D/+0x13E/+0x144/+0x160. Native 0x4178D0 initializes counters +13B/+13E to zero, whereas +160 date initialization and lifetime are conditional and must not be guessed. Native 0x4197C0 and 0x419490 have independently established byte increments/decrements, competition gate, source RNG order and +160 signed comparison. State for FA and UEFA is separate, not one generic suspension amount. The calendar epoch has not been source-mapped to Python date.

## Minimum bounded integration

New reconstruction/original_native_player_discipline_state.py defines an immutable native record for all seven recovered BYTE offsets and one raw DWORD date. It constructs only from a genuinely reached original player byte record (through +160) and a separately verified RuntimePlayer key that exactly matches the original unsigned WORD at +4. This equality is a necessary consistency check, not proof that any reconstructed value was obtained by launching the original. Invalid byte/date range, wrong identity, mixed/duplicate saved keys and unknown player indices fail closed.

GameState retains only explicit per-player source records in native_player_discipline, with an exact-input method retain_verified_native_player_discipline. No automatic copies from generic suspension status, no fabricated fresh snapshots and no automatic NEXT/callback/mail mutation occur.

The modern internal save preserves sparse source-owned records at optional top-level game_state.original_native_player_discipline. The large pre-existing PLAYER_RECORD_FIELDS positional array is unchanged and current SAVE_SCHEMA_VERSION=48 remains readable because a missing optional member restores an **empty/unverified** sparse map, rather than synthesizing all-zero source players. This is a backwards-compatible extension of the port's *internal* format, not a claim of original FM2001 save binary compatibility.

Positive/negative tests include exact record offsets, unsigned +160 preservation, source identity, ordering/duplicates/malformed snapshots, and a whole HumanGameplayController -> GameState -> snapshot -> restore roundtrip proving that generic fields remain unchanged. Focused Gate13 workflow is registered.

## Evidence and unfinished behavior

SOURCE VERIFIED: original offset identity and producer/reader roles within bounded native branches; source-shaped preservation carrier. IMPLEMENTATION VERIFIED only after exact branch tests and CI. NO native original execution, no live 0x4197C0 callbacks, no atomic match transaction, no Inbox output, no Windows11 GUI proof. Gates13–17 remain open.

NEXT: identify exactly when 0x4085D0/0x41A250 produce mutable native fields, preserve original RNG/callback order, and connect source-qualified incidents to the sparse GameState carrier, original 0x613EC0 pending envelopes and due 0x5CFA20/0x413020 recipient dispatch. Then complete real ordinary NEXT -> PPreMatch modes 0–3 -> PResults -> return and broad original countries/multihuman/save scope. Do not use generic disciplinary counters as a shortcut.
