# Original installer resource-location selectors

4 October 2026 KST. This repairs a native-debugging prerequisite, not a capacity
initializer or a Gate-13 gameplay result. Daniel explicitly authorized only
missing, source-qualified selectors in the existing FM2001 installation key.

## Exact authorized installer producer

Authorized ZIP SHA-256:
`677dcbc859109818d22599f34890ca7873393aea5adbf1f1f1a32d1a76f8a8a4`.
Private exact-path extraction already verifies:

- `Setup/English/SETUP.INS`: 58,111 bytes, SHA-256
  `7186f23158adb231a1ac36a17c4cb1ddcf4f33726c5b6c5eb426aaab7b743591`;
- `Setup/English/compnent.txt`: 1,212 bytes, SHA-256
  `9eda43c34a4830920af693d6b9f158e831e159321d5236ffb5abba96332bc71f`.

The compiled script identifies compiler **3.00.077**. It was decoded as data,
not executed, using private isDcc source commit
`111081770fa7cb0fd60b7feac7c18d39dcc7fe65`
([decoder source](https://github.com/incognitte/isDcc)). That decoder's IF/GOTO
target handling had removed the one-based-to-zero-based adjustment still used
by its user-function calls. Its uncorrected listing produces contradictory
branches/loops. The private listing restores that adjustment, emits every
label and records original byte offsets; relevant instructions and reachable
branches were checked against the original INS bytes. No modified decoder or
original/decompiled installer is distributed in Git.

All offsets below are **SETUP.INS file offsets**, not executable VAs:

- English source branch sets the application name `Football Manager 2001`.
- `function120` maps `COMPACT_AND_TYPICAL` to type 0 (`AFFF`) and `TYPICAL`
  to type 2 (`B093`). `B17E` finds `registry =`; `B27E/B28B` append the exact
  selector name and component index to lists 21/22.
- `function99`: typical selector `12D` sets comparison type 2 at `75A9`.
  Component type equal to that selection, or type 0, is selected. `7694`
  writes **byte 1** into the component-selection buffer; the unselected branch
  at `76AA` writes **byte 0**. Custom selection also writes explicit 1/0
  according to `ComponentIsItemSelected`; it is not an inferred path default.
- `function123` copies only selected components using that same buffer.
- `function105` selects HKLM (`80000002`) and builds
  `\SOFTWARE\EA SPORTS\Football Manager 2001`. `9621` reads the selection
  byte, `962C` converts it to a decimal string; `96C7` calls
  `RegDBSetKeyValueEx(key, component-name, 4, value-string, -1)`.
  Type 4 is the DWORD numeric contract, also independently required by the
  canonical executable's four-byte native queries. The vendor documents the
  decimal-string-to-DWORD behavior of
  [RegDBSetKeyValueEx](https://docs.revenera.com/installshield28helplib/LangRef/LangrefRegDBSetKeyValueEx.htm).

Thus the original **all-four-selected / typical** configuration writes:

| Component index | Exact selector | Registry type | Selected value | Unselected value |
| --- | --- | --- | --- | --- |
| 1 | `art` | REG_DWORD (4) | 1 | 0 |
| 2 | `stadia` | REG_DWORD (4) | 1 | 0 |
| 3 | `fmv` | REG_DWORD (4) | 1 | 0 |
| 4 | `matchengine` | REG_DWORD (4) | 1 | 0 |

This does not claim to recover the previous installation's historical selection.
It applies the proven original full-component configuration to the already
present full installation. Equal configured roots do not establish these values.
The native consumer resolves **nonzero to Install Dir** (global `87BAE8`),
zero to CD Drive (startup stack `+130`): `5308B6` art, `530991` fmv,
`530A33` matchengine and `530ACD` stadia. No controlled-capacity writer or report
state is involved.

## Missing-only reversible repair

The existing **32-bit view** key was exported with 32-bit `SysWOW64\reg.exe`
before writing. The snapshot contained only two root values: REG_SZ `Install
Dir` and `CD Drive`, both `C:\Games\FM2001`, plus the existing Settings subkey.
The export preserves the full key/subkey state. The private repair rechecks
the snapshot and original source hashes, opens only the existing exact key,
refuses overwrites, and adds only the four selectors above as REG_DWORD **1**.
Post-write comparison verifies the original paths and subkey list are unchanged.
No executable, game file, capacity, report or other registry value was modified.

Private before export: `gate13-install-key-before-20261004.reg`, SHA-256
`d6056e34cac4923779dcd5903b6fdbc37fce4d00d75f8ca66349316e697f3ce7`.
Private source/before/after receipt:
`gate13-install-selector-repair-receipt-20261004.json`, SHA-256
`dfea7e2385a1454226134cb81eaf58bed0347064cfed3a179d8a5cad4cb29318`.
Private corrected byte-offset listing SHA-256:
`3cc8a9582a8ac3cd865ec950b34b4eae065905754ef2ba42aa2d5507db685b02`.

The receipt records the private repair script's `rollback` command. It verifies
the exact repaired state, deletes only the four values this repair added, and
checks the original snapshot; it does not delete/recreate the key or overwrite
paths. These private files remain in the session's `work` directory outside Git.
Startup acceptance and actual allocation/write observations must be established
separately by `gate13_native_capacity_watch.py`; no initializer follows merely
from this repair.

The first post-repair native run establishes all six queries return 0, each
selector returns type 4 / size 4 / value 1, and setup `530600` returns AL=1 at
`530DD9`. Private receipt `gate13-native-capacity-selectors-repaired-20261004.json`
SHA-256 `b892f532869a91586e9df2cdd057e95046909123cbcf9225f19ab4b1aaedf7ff`.
This supersedes the missing-selector blocker, but it does not reach allocation.
A second bounded run captures EIP=0 with return address `6151F1`: the
`6151EB` indirect call through `A911EC` is null after the driver loader. Private
exception/context receipt `gate13-native-startup-null-context-20261004.json`
SHA-256 `429c2aeef37b9264c44582ecc2d2304cddc5847e800f4228fd89b5845de4856b`.
The private executable-only stage lacks the original runtime DLLs; the next
probe stages exact authorized original dependencies outside Git, without
changing the installed game, patching the null pointer or bypassing startup.
