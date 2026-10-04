# Gate 14 chant resource catalog boundary

_Status: independent Gate-14 source result while Gate 13 remains Codex-owned._

## Result

The authorized source disc contains one chant control file and 56 chant bank
files under `Data/Audio/Chants/`.

The control file is:

- `CHANT.eam`
- 704 bytes
- SHA-256
  `b2b26a6a8a7c2d904df4868ee8454169ef49dbd69b07fa22d926ec11aafafbee`
- leading four bytes `MIDx`

The 56 `.bnk` files total **2,523,996 bytes**. A deterministic SHA-256 over
the sorted exact `path,size_bytes,file_sha256` records is:

`b81f2f45c033d8da53f5a27696f07a70662f90fd277f51f5a3f3b1920c98c264`

This binds the source inventory without committing proprietary audio.

## Executable ownership

Chant initialization begins at `0x722D80`.

The exact embedded paths/strings are:

- directory suffix `\data\audio\chants` at `0x866300`;
- control path `data\audio\chants\chant.eam` at `0x866314`;
- internal source name `chant` at `0x866338`.

The initializer assembles the source path in global buffer `0xA879BC`,
loads the control file and stores its handle at `0xA878EC`. Successful
initialization ultimately gates ready state `0xA878D0`.

## Dynamic selection inputs

Pair-selection logic at `0x722F00` reads the two active club pointers from
`0xAD6060` and `0xAD6174`, and reads a source word at club offset
`+0x32`.

The same path uses two exact source format strings:

- `cl%06.6d` at `0x866360`;
- `c0%4.4d` at `0x86634C`.

Dynamic chant loading continues through `0x723010`.

These facts prove that chant selection is driven by active-match club state and
dynamic identifiers. They do **not** yet prove how those formatted identifiers
map onto each of the 56 physical bank files.

## Fidelity boundary

The source control file begins with `MIDx`, but its sequencing semantics are
not decoded by this checkpoint.

The reconstruction therefore keeps all of these false:

- `CHANT.eam` sequence/choreography decoded;
- exact bank-to-club mapping recovered;
- chant-to-match-event binding recovered;
- chant playback timing recovered.

Do not infer those from bank filenames, club identities, file sizes, duplicate
hashes, or the `MIDx` magic alone.

The next source step is to trace the dynamic records loaded by `0x723010`
through their eventual sample-playback calls far enough to source-close one
bank-selection rule or event family.

No proprietary chant bytes, executable bytes, or disassembly are committed.

## Provenance

The catalog and control-file identity were computed directly from the authorized
MODE1/2352 source disc. The executable used for ownership tracing matched
canonical SHA-256:

`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.
