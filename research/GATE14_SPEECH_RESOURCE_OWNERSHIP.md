# Gate 14 speech resource ownership

_Status: independent Gate-14 source result while Gate 13 remains Codex-owned._

## Purpose

The original audio system contains a speech-stream subsystem separate from the
four fixed SFX banks. Private tracing of the canonical executable now binds the
resource paths used by that subsystem to exact byte-identical files from the
authorized disc.

This checkpoint closes **resource ownership only**. It does not yet map speech
phrases to match events, prove playback timing, or declare commentary ready.

## Executable ownership

Main audio initialization `0x6D0AC0` reaches the speech initialization family
in the non-minimal audio path.

The source-qualified owners are:

- general speech initialization: `0x723AD0`;
- common speech path builder: `0x723E20`;
- team speech resource setup: `0x723E70`;
- player/stitched speech resource setup: `0x724080`.

The common source path format is at `0x8663F0`:

`%s\data\audio\speech\%s`

Direct executable string references bind the following resources.

| Resource | Bytes | SHA-256 | String VA | Direct reference | Owner |
| --- | ---: | --- | ---: | ---: | ---: |
| `NewSpeech.inf` | 26,879 | `b0d0be607f669051a2b4ee884578f8da277f9cd912baf72849c56cec4ee89a25` | `0x86638C` | `0x723CAF` | `0x723AD0` |
| `NewSpeech.str` | 86,879,932 | `fd0d511c1482080e49cd49b2baa7396ea53e2866bacebfd0dac6515ab6211c1e` | `0x8663AC` | `0x723C84` | `0x723AD0` |
| `Stitched.str` | 500,960 | `c3fd52af55b6abf1270fb9cd0cd496702bf3c1068ca6274080e64813c98c0c00` | `0x86639C` | `0x723C93` | `0x723AD0` |
| `Teams.off` | 2,244 | `a16c7df782db703e5c3d284bdbf1ff35653f65bc5e2b730e8a17518e7828f54f` | `0x866408` | `0x723EC5` | `0x723E70` |
| `Teams.str` | 1,812,912 | `57e04f874806174b6af16ae2dcbf586cf68807eb71707ab5dc01010b6246a18a` | `0x866414` | `0x723EB0` | `0x723E70` |
| `Stitched.off` | 1,036 | `37954be2c825b712215959356ec0940946406e47c30c5aca395cdcf59106a96e` | `0x866420` | `0x7241F2` | `0x724080` |
| `Players.str` | 11,392,368 | `bd1fabdbebe7aae37fe8878f5a794a069cf6954064a4a450df454b3d9e6ae6c1` | `0x866430` | `0x724100` | `0x724080` |
| `Players.off` | 25,692 | `228f53d810e998e8bdb02c610905e28c80780e920ef677635591d9375a728b65` | `0x86643C` | `0x7240C8` | `0x724080` |

All paths are under `Data/Audio/Speech/`.

## Why this matters

The original disc has a large, dedicated speech system rather than requiring
speech/commentary to be guessed from the SFX-bank filenames. The executable
directly opens these stream/index families, so future commentary work can trace
their real selection logic instead of synthesizing speech from modern match
events.

## Fidelity boundary

`gate14_speech_resource_ownership.py` hard-fails any attempt to promote the
current evidence into:

- phrase/index mapping;
- match-event binding;
- playback timing;
- commentary readiness.

The next source step is to trace the consumers of the loaded index/stream
objects far enough to map at least one event family to an exact stream/index
selection. Until that is source-closed, these files are owned resources, not an
integrated commentary system.

No proprietary speech bytes, executable bytes, or disassembly are committed.

## Provenance

The resources were read directly from the authorized MODE1/2352 disc image.
The executable used for the ownership trace matched canonical SHA-256:

`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.
