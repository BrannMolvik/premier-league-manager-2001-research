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

## Source-closed physical bank selection

Private tracing of `0x722F00 -> 0x723010` now closes how the executable assigns
the physical chant-bank filenames to its three runtime pools.

Before enumeration, `0x722F00` reads source IDs from the active home/away club
objects at offset `+0x32`. Distinct source IDs become exact lowercase prefix
patterns `c0%4.4d` for home and away. If both clubs share the same source ID,
a separate presentation RNG parity draw chooses which side keeps that
club-specific pattern; the other side receives literal `c0000000`, preventing
the same physical family from being selected for both pools.

The separate `CL...` pair begins from two value-1 selector globals. Because
those values compare equal, the source always consumes an earlier independent
RNG parity draw and assigns `cl000001` to one side and `cl000000` to the
other. The current authorized disc contains no physical `CL...` bank files, so
this branch contributes no banks on this release source.

`0x723010` enumerates `*.bnk`, lowercases the first eight basename bytes at
`0x7231D0`, and checks five patterns in order at `0x7230D6`:

1. `cgener` -> pool type 2;
2. CL home pattern -> pool type 0;
3. CL away pattern -> pool type 1;
4. club home `C0...` pattern -> pool type 0;
5. club away `C0...` pattern -> pool type 1.

The exact source-disc family shape is 21 `CGENERxx` banks plus 35
club-specific `C0ddddxx` banks covering 22 source IDs. This source-closes
bank-to-active-club pool selection. It does not decode the content of those
banks, bind individual chants to match events, or recover playback timing.

## Source-closed pool shuffle/order

The next loader phase at `0x723142-0x72319D` is also now source-closed.
After all matching bank records are collected, the executable:

1. reads the current remaining-record count through `0x6B2340`;
2. obtains one presentation RNG value at `0x723157`;
3. divides by the remaining count and uses the remainder as an index;
4. calls `0x6B2810`, which removes and returns that indexed list node;
5. reads record type at `+0x08`;
6. appends the record through `0x6B1F90` to:
   - type 0 -> home pool `0xA87984`;
   - type 1 -> away pool `0xA879A0`;
   - type 2 -> generic pool `0xA87968`;
7. repeats until the source list is empty.

This proves a random-without-replacement ordering inside the three chant pools.
The reconstruction models the already-reduced modulo indices explicitly rather
than claiming the private RNG generator/state itself. Pool ordering still does
not identify which individual sample will be played for a particular match
event or when playback occurs.

## Source-closed runtime timing boundary

The canonical runtime updater at `0x7235E0` is now traced far enough to record
its exact clock arithmetic without assigning semantic names to the control-file
fields.

The updater calls the source clock at `0x6AAE40` and drives a four-state record
lifecycle through pending pass `0x723600` and active pass `0x7236E0`.
The record state is stored at `+0x08`; source deadlines live at `+0x10` and
`+0x14`.

The exact source arithmetic is:

- pending-resource retry guard: `now + 200 ms`;
- first playback-phase deadline: `now + [record+0x20] + [record+0x18]`;
- second playback-phase deadline: `now + [record+0x1C] + 200 ms`;
- per-pool cooldown reset: `now + 6000 ms`.

The three record fields `+0x18/+0x1C/+0x20` remain deliberately unnamed.
Although they participate directly in audible scheduling, this checkpoint does
not infer their human-facing meaning from their arithmetic or from the
`CHANT.eam` bytes. Match-event binding and individual chant meaning therefore
remain unresolved.

## Source-closed runtime pool choice

Runtime enqueue `0x723360` maps the low-16-bit selector through the table at
`0x7DE270`:

- selector 0 -> specialized home list `0xA87984`;
- selector 1 -> specialized away list `0xA879A0`;
- selector 2 -> generic list `0xA87968`.

Home/away selection uses `0x7234D0` and generic list walker `0x6B2550`.
The source predicate at `0x723510` first requires either
`now >= [record+0x0C]` or `[record+0x04] < 2`. Only eligible records consume
presentation RNG; the already-reduced remainder is accepted when
`RNG % total_pool_count == 0`. The list walker stops on the first accepted
record. If specialized selection returns none, `0x723440` falls back to the
generic selector.

Generic selection at `0x723470` uses persistent cursor `0xA878DC`. A zero
cursor reloads the current generic-list count, then selection decrements the
cursor and reads that index. This cycles backward through the already-shuffled
generic pool and reloads at zero.

The reconstruction models reduced RNG remainders and the cursor explicitly. It
does not claim the private RNG generator state or map selector values to a
specific match-event meaning.

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
