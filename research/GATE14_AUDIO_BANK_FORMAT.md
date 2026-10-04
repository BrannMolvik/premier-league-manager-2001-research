# Gate 14 FM2001 BNK format and modern decode

_Status: source-backed Gate-14 audio-format checkpoint. Gate 13 remains Codex-owned._

## Canonical private source pass

The four executable-owned banks staged by the Gate-14 exact-path contract were
read directly from the authorized disc image and matched these identities:

| Bank | Bytes | SHA-256 | Slots | Real | Dummy |
| --- | ---: | --- | ---: | ---: | ---: |
| menus.bnk | 159,324 | e3bd385d89ab94f0a97834a0749898c99d10a29ee404c29ebdc708c0daa1fc1d | 23 | 23 | 0 |
| game00.bnk | 360,400 | dde480b17fcc73811ea6bd8ef2a918550c8c5b6b81cc60ca0e4893b2a91cff86 | 96 | 55 | 41 |
| playercalls.bnk | 275,140 | b03a63a614536cc31736aab118e82874e53f9989045c158a2a82282afc731fe9 | 70 | 59 | 11 |
| Advice.bnk | 700,072 | dc63453b42cb12649e0fd3ea28cd1f181b7924069e640638ad5f6603a7ef871b | 43 | 43 | 0 |

Total: **232 table slots, 180 real sounds, 52 dummy slots**.

## Container layout

All four files are little-endian early EA banks:

- signature: `BNKl`;
- version: `0x02`;
- sound-slot count: little-endian uint16 at `+0x06`;
- full metadata/header size: little-endian uint32 at `+0x08`;
- sound table begins at `+0x0C`.

Each table dword is a displacement relative to the address of that table dword.
A zero displacement is a dummy/no-sound slot. Every nonzero target in all four
FM2001 banks begins a `PT\0\0` variable header. The header-size field equals
the first audio payload offset in every bank.

The relative-entry rule, PT tag grammar and PC defaults are consistent with the
maintained vgmstream EA parser:
https://github.com/vgmstream/vgmstream/blob/master/src/meta/ea_schl.c

## FM2001 PT subset

All 180 real entries use PC platform id `0x00`.

Every real entry supplies:

- tag `0x85`: decoded sample count;
- tag `0x88`: absolute bank-relative sample-data offset.

The four banks omit explicit channel-count and sample-rate tags. For PC
platform v0 these resolve to:

- one channel;
- 22,050 Hz.

Codec distribution:

- **178** entries explicitly set early codec1 tag `0x83 = 0x07`, EA-XA v1;
- **2** entries omit codec1 and therefore use the PC v0 default PCM path,
  which is 16-bit little-endian when the 8-bit flag is absent.

The EA codec/default mapping is consistent with the maintained vgmstream parser
above. The EA-XA v1 decoder behavior is independently documented by:
https://github.com/vgmstream/vgmstream/blob/master/src/coding/ea_xa_decoder.c

## Payload boundaries

For mono EA-XA v1, one frame is 15 bytes and yields 28 samples. Therefore:

`encoded_bytes = ceil(sample_count / 28) * 15`

For the two PCM sounds:

`encoded_bytes = sample_count * 2`

For every one of the 180 real FM2001 sounds, the next distinct payload offset
(or end of bank) leaves exactly the required encoded byte count plus **0–3
alignment bytes**. Shared payload offsets are retained as aliases rather than
misclassified as duplicate or malformed records.

This closes sample payload boundaries without guessing from the next table slot.

## Modern decode

`gate14_audio_bank_format.py` implements the exact FM2001 subset and a
deterministic EA-XA v1 mono decoder using the recovered 15-byte-frame predictor
path. It also decodes the two PC-default PCM16LE sounds.

The private canonical audit decoded all 180 real sounds successfully:

- menus.bnk: 311,460 PCM samples;
- game00.bnk: 652,750 PCM samples;
- playercalls.bnk: 506,871 PCM samples;
- Advice.bnk: 1,303,128 PCM samples;
- total: **2,774,209 PCM samples**.

Per-bank concatenated PCM SHA-256 identities are retained in code so a future
private source run must reproduce the same decoder output before passing the
canonical audit.

This is sufficient to set Gate-14
`audio_sample_decode_ready=true`.

## Remaining audio boundary

This checkpoint does **not** assign human-readable meaning to bank slots or
individual sample indices.

Still open:

- exact event/sample binding;
- chant event semantics;
- login/menu playback integration in the modern host;
- final audible Windows verification.

No BNK bytes or decoded proprietary PCM are committed to Git.
