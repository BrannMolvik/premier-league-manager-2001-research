# Gate 14 CRWD resource ownership

_Status: independent Gate-14 source result while Gate 13 remains Codex-owned._

## Result

The original executable owns a second audio-resource family under
`Data/Audio/CRWD/`, separate from the four fixed SFX-bank slots and the
speech-stream subsystem.

Private tracing source-closes the exact runtime selection logic at
`0x722AF0`:

- runtime mode value **1** selects `traff.bnk` + `TRAFF.CRD`;
- every other mode value selects `CROWD.BNK` + `CROWD.CRD`;
- the non-1 branch additionally initializes `CMIDI.BNK` through
  `0x7229B0`.

The human-facing meaning of that numeric mode is deliberately not assigned.

## Exact source resources

| Resource | Bytes | SHA-256 | String VA | Direct reference | Owner |
| --- | ---: | --- | ---: | ---: | ---: |
| `CMIDI.BNK` | 446,548 | `5cd99c9a01039756fa9525a945ddb9a08fece0d31e85fcb7a8af7c5220680ad4` | `0x86625C` | `0x7229BE` | `0x7229B0` |
| `CROWD.BNK` | 72,592 | `d1e5268a1e221453e144f47803d9246ee49958584f205c2fe8acecc9bc8dcb59` | `0x866288` | `0x722B36` | `0x722AF0` |
| `CROWD.CRD` | 5,480 | `445c84cb54dd40b85617e970b1596e325074b54f2af345eae4227a3f9c43d705` | `0x86627C` | `0x722B45` | `0x722AF0` |
| `traff.bnk` | 235,952 | `02bffe61944a3b1771756e2d7822fdb84dbf98bf815d010e4cb65c2c4136fc55` | `0x8662A0` | `0x722B20` | `0x722AF0` |
| `TRAFF.CRD` | 1,384 | `dc6a630855b418053e08a637e85a9ec94b2a5b314f0796155de73d052ed1f5fc` | `0x866294` | `0x722B2F` | `0x722AF0` |

The common CRWD path formatter is at `0x866268`; the loader path around
`0x722A80` fills active runtime globals at `0xA87850 / 0xA87854 /
0xA87858`.

## Fidelity boundary

These filenames are not promoted into user-facing meanings.

In particular, this checkpoint does **not** claim that:

- `CMIDI.BNK` is menu music;
- `CROWD.BNK` is necessarily live match crowd ambience in every mode;
- `TRAFF.BNK` means traffic, training, or any other higher-level mode;
- any CRD entry maps to a named event;
- any bank sample timing or looping rule is recovered.

The reconstruction contract keeps all of those semantics false. The next
source step is to trace consumers of the active CRWD bank/card globals far enough
to map a concrete event or playback operation before integrating audio.

No proprietary audio bytes, executable bytes, or private disassembly are
committed.

## Provenance

All five files were hashed directly from the authorized MODE1/2352 source disc.
The executable used for the ownership trace matched canonical SHA-256
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.
