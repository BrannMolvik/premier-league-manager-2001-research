# Bounded native fresh-club capacity watch

4 October 2026; canonical base `3a3f60d1e89c7f44e7f12ca70fef3f263fe73a9b`.
Gate 13 remains OPEN. No visiting-capacity value is authorized by this work.

## Executable observation, not another displacement scan

`reconstruction/gate13_native_capacity_watch.py` runs the checksum-qualified
PE32 original under a 64-bit Windows/WOW64 debugger. It refuses source/output
paths inside Git, unexpected image relocation, changed breakpoint bytes,
invalid array bounds and repeated allocation. It never attaches to another
process, generates GUI input, supplies report inputs or changes executable
files/installation keys. Runtime INT3 probes and two dword WRITE watchpoints
affect only the launched process, which is terminated on each bounded exit.
Maximum observation is 60 seconds / 4,096 debug events.

Source-qualified lifecycle probes:

- `40BC14`: allocation return, before the `+4` array cookie / `2A8` stride
  constructor iteration; EAX allocation, ESI count. The selected **array index**
  is not assumed to be the database club ID.
- `40BC43`: constructor iteration returned.
- `40BA2C`: selected DBTClub import returned; club ID can now be observed.
- `5DA538`: uncontrolled capacity branch; ESI is the retained DBRClub receiver.
- DR0/DR1: exactly receiver `+13C/+140`, four-byte writes, armed before
  construction and on observed subsequent threads. Hardware events record
  post-instruction context and private preceding bytes, not a claimed writer.

Receipts always retain `capacity_initializer_proven=false`. Even observing a
value/write needs receiver, CFG, copy/load ownership and lifecycle adjudication;
no-watch-event results and allocation snapshots do not imply zero initialization.
Software breakpoint single-step windows are not an all-thread execution proof.

Nine synthetic ABI/planning tests, a real canonical entry-point calibration
and `--calibrate-crt-writes` pass. The latter arms the same two dword WRITE
watches on known CRT globals `9FAC00/9FABFC` before source writes at
`66AAF7/66AB05`; actual hardware delivery records exactly the expected
post-instruction EIPs `66AAFD/66AB0B` and stops before installation access.
These positive-control globals are not club fields. This establishes a working
native debugger/write-watch backend, NOT the requested capacity
initializer or human-away report route.

## Exact newly observed native prerequisite

Non-administrator startup reaches the original CRT and OS guard, then its
`515C11` HKLM `RegOpenKeyExA` requests access `F003F` and returns 5. The key is
`SOFTWARE\EA SPORTS\Football Manager 2001` in the 32-bit registry view.
A read-only check finds only `Install Dir` and `CD Drive`, both `C:\Games\FM2001`.
The installed executable copies also match canonical SHA-256
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.

Daniel explicitly approved a bounded administrator debugger without changing
executable or installation keys. Under that UAC-approved run:

- `515C17`: key open returns 0;
- `53078D`: `CD Drive` query returns 0;
- `5307F8`: `Install Dir` query returns 0;
- `53085F`: mandatory `art` DWORD query returns **2 (not found)**;
- `530DD9`: setup guard `530600` returns false; WinMain returns `FFFFFFFF`.

The same source guard subsequently requires `fmv`, `matchengine` and `stadia`
DWORD location selectors, but this execution stops at missing `art`. Do not
claim the later queries executed or choose selector values merely because the
two configured root strings currently coincide. Fresh club allocation and
the uncontrolled read were **not reached**. No register/key/capacity was patched
to bypass setup. The installed-directory launch separately exits before the
entry probe with code `C0EC0002`; its cause is not established.

Exact installer evidence was also extracted from the reverified authorized
archive, outside Git: `Setup/English/SETUP.INS`, `registry.txt`, `compdesc.txt`
and `compnent.txt`. The component text binds art / stadia / fmv / matchengine
to their actual install components and distinguishes compact/typical choices;
it does not by itself prove the compiled installer's DWORD write values.
`SETUP.INS` SHA-256 is
`7186f23158adb231a1ac36a17c4cb1ddcf4f33726c5b6c5eb426aaab7b743591`.
The registry text contains Settings entries, not these missing selectors.
No guessed flags were installed and no unrelated public copy was obtained.

Next capacity action: source-qualify/restore the original installation's
resource-location selectors using authorized installer evidence (new approval
needed before changing installation keys), then rerun the watch through actual
fresh-world creation and an uncontrolled-home match. Follow any observed alias
writer/copy; retain fail-closed producer behavior until that lifecycle is proven.

Additional bounded static adjudication excludes two tempting alias paths:
`405B50 -> 50FAD0` only reads roster count `+294` and its `+244` word array;
`61C460/61C9C0` operate on `C8`-stride player-assignment records, not DBRClub
capacities. Neither path authorizes `+13C/+140` initialization.

## Private reproducibility receipts

All below remain outside Git in the authorized local `work` directory:

- `gate13-native-hardware-watch-calibration-29781e92.json` SHA-256
  `54c88bf4065bf9ecb2bbff4c9bb0cbcbb69d90cc7e9f18c2aa347c9bc02d0823`;
- `gate13-native-capacity-admin-query-3a3f60d1.json` SHA-256
  `d30e61290983cb61039800edf496ffe0ee3e5d730b799ca2c1c6f25ad9d1b586`;
- `gate13-capacity-scroll-source-3a3f60d1.json` SHA-256
  `52e6c94c72f97c5154c3ba932273c5c1a5c99c99fc6f2fa353ba97b6442341f7`;
- `gate13-scroll-stage-receipt-3a3f60d1.json` SHA-256
  `14110f0f8e626ccba59c753a6208a0cec8d84f8707179193af6ddd1044f213e4`.

The exact three-scroll-resource inventory reverified the authorized ZIP
`677dcbc859109818d22599f34890ca7873393aea5adbf1f1f1a32d1a76f8a8a4`.
All five loader-family assets are now provenance-imported/hash checked.
The exact-path file remains a replayable three-resource batch, independent of
current missing-resource state. Import completeness does not imply scroll
behavior, timing or Gate-13 closure.
