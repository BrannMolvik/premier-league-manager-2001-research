# Gate 14 exact audio-bank source staging

_Status: private source-byte identity contract only. Gate 13 remains Codex-owned._

## Source path derivation

Shared loader `0x6D01F0` constructs each runtime bank path with executable
format string:

`%s\\DATA\\AUDIO\\SFXS\\%s`

The four source-owned filenames are already canonical in
`gate14_audio_bank_ownership.py`. Their exact disc-relative staging contract
is therefore:

- `DATA/AUDIO/SFXS/menus.bnk`
- `DATA/AUDIO/SFXS/game00.bnk`
- `DATA/AUDIO/SFXS/playercalls.bnk`
- `DATA/AUDIO/SFXS/Advice.bnk`

The checked-in path file is
`research/gate14_audio_bank_exact_paths.txt`. Its order must match the four
source-backed bank slots exactly.

## Private extraction flow

When private source execution is healthy, use the existing exact-path source
inventory against the authorized archive:

`gate13_source_inventory.py <source.zip> --deep --hash-source --extract-path-file research/gate14_audio_bank_exact_paths.txt --only-explicit --require-all-explicit --extract-candidates-to <private-stage> --output <private-inventory.json>`

Then validate the staged files with:

`gate14_audio_bank_stage_receipt.py --inventory-report <private-inventory.json> --staging-root <private-stage> --output <private-receipt.json>`

Both outputs and the staged BNK bytes remain private and outside Git.

## Receipt guarantees

The receipt requires:

- one hashed source archive;
- `only_explicit=true`;
- zero unresolved requested paths;
- exactly the four source-owned path identities;
- exactly one extracted candidate per bank;
- an extracted source layer, not listing-only metadata;
- positive byte size and SHA-256 from the inventory;
- byte-for-byte size/hash agreement with the staged file.

This makes future format analysis provenance-safe without importing proprietary
bank payloads into the repository.

## Fidelity boundary

A passing receipt proves **only exact source-byte identity** for the four owned
banks. It keeps all of these false:

- bank header layout;
- sample table layout;
- sample offsets;
- sample codec;
- sample-rate/channel metadata;
- modern sample decode readiness;
- event binding.

The receipt therefore prepares the current `audio_sample_decode` blocker; it
does not solve it.
