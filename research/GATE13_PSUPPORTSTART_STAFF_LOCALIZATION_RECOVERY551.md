# Recovery551: authenticated original Support Staff localization mapping

This is a bounded **native 0x4CDCD0 label ordinal** source resource component,
not an asserted mapping from each dynamic CSupportStaff instance
`staff_type` to its virtual+0x14 return. It is not a working original GUI.

Directly downloaded, independently SHA-256 checked private original files:

- `FM2001/English.str`: 369,644 bytes, SHA-256
  `aa594a55ad95c672b69184e5f3ff8349e41fe95b48c5dcb3c8fcfe2bcdf5b601`.
- `FM2001/English.idx`: 5,428 bytes, SHA-256
  `98fcbe9e9eb5d1068739a58cc46aaaedab2749b2c65460861b18beeac7361db1`.
- Source PE: 4,714,541 bytes, SHA-256
  `833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.

An original language resource reader **already exists** at
`reconstruction/ea_language_strings.py`: `EAStringTable` reads
nul-terminated CP1252 strings and `EAStringIndex` reads uint16 references.
The original source `English.str` has **21,856 strings** and the original
`English.idx` has **2,714 index entries**, not byte-offset indexes.
No duplicate parser, newly invented strings or original private binaries are
introduced by this bounded component. The repository already retains
`original_assets/source/English.str` and `English.idx`
under the existing asset policy.

Static original 0x4CDCD0 has an unsigned native bound `case1..16`
and PE jump table `0x4CDD84`. Cases1..12 resolve globals
`0x982AA4,0x982AA0,...,0x982A78`;
case13 resolves **`0x9821E4` instead of
`0x982A74`**; cases14–16 resolve
`0x982A70,0x982A64,0x982A60`.
PE localization initializer `0x6458B0..0x645AF9`
uses original `0x667E90` to read sequential two-byte IDs
and `0x64E320` to resolve each from the loaded original
language table pointer family. Original English.idx
entries1877–1894 resolve the contiguous 18 localized
Support Staff strings in `English.str`:

| Native label case | Original English.idx position | Exact source label |
|---|---:|---|
|1|1877|ASSISTANT MANAGER|
|2|1878|STADIUM MANAGER|
|3|1879|YOUTH TEAM MANAGER|
|4|1880|BUSINESS CONSULTANT|
|5|1881|CHIEF SCOUT|
|6|1882|GROUNDSMAN|
|7|1883|GK COACH|
|8|1884|FITNESS COACH|
|9|1885|TECHNIQUE COACH|
|10|1886|DEFENSIVE COACH|
|11|1887|MIDFIELD COACH|
|12|1888|ATTACKING COACH|
|13|*different 0x9821E4 global*|UNKNOWN without separate provenance|
|14|1890|DOCTOR|
|15|1893|TALENT SCOUT|
|16|1894|SCOUT|

The source has additional original strings at positions1889,1891,1892,
but those **cannot be assigned to case13** merely because they appear
nearby. Preserve the special pointer unresolved. Also **do not overwrite**
the existing source-behavior-recovered `ASSISTANT_MANAGER_TYPE`
and `YOUTH_TEAM_COACH_TYPE` fields on this evidence: the exact mapping
between a generated original CSupportStaff object's `staff_type`,
virtual+0x14 return and 0x4CDCD0 localization argument still
requires independent disassembly and counterexamples.

`reconstruction/original_supportstart_staff_labels.py` is a
read-only original native ordinal→localized text resolver;
`test_original_supportstart_staff_labels.py` loads the genuine
source assets and compares all fifteen qualified native labels.
This is reusable when authentic row rendering is integrated,
but it does not add speculative text to a live host.

Reproduce:
```bash
sha256sum English.str English.idx footballmanager.exe
objdump -D -Mintel --start-address=0x4cdcd0 --stop-address=0x4cddc4 footballmanager.exe
objdump -D -Mintel --start-address=0x6458b0 --stop-address=0x645b20 footballmanager.exe
objdump -D -Mintel --start-address=0x64e320 --stop-address=0x64e338 footballmanager.exe
objdump -D -Mintel --start-address=0x667e90 --stop-address=0x667f0a footballmanager.exe
cd reconstruction && python -m unittest test_original_supportstart_staff_labels
```

**Exact next action:** verify the original CSupportStaff vft+0x14
producer and the exceptional string pointer `0x9821E4`,
then bind source-qualified row labels and real staff names into
the seven-row original editor. UI mouse/hit route and
TeamSelect source record registry/persistence remain unresolved.


## Recovery551 follow-up: native case13 independently SOURCE CLOSED

The original exception `0x4CDD3E` reads global `0x9821E4`
instead of adjacent Support `0x982A74`.
Source initializer `0x64A312` loads exactly that global
via `0x64E320`, from a 2-byte English.idx position
read with original `0x667E90`. Independent
static PE call-order audit between the already
confirmed case1-global initialization at
`0x6458B7` and case13 exceptional global
initialization at `0x64A317` counts **561**
sequential `0x64E320` locale lookups,
inclusive. The first is original English.idx
position **1877**, hence the last is
`1877+560 = 2437`.

Raw separately SHA-256 verified
`FM2001/English.idx` entry **2437** points
to original `FM2001/English.str` text
**'Physiotherapist'**. Additional neighboring
entries corroborate the count: entry2436 is
"Writer's player of the year", entry2438 is
"Sleet"; adjacent globals `0x9821E8`
and `0x9821E0` are initialized
immediately before/after `0x9821E4`.
This source pointer and indexed-byte
proof supersedes the initial UNKNOWN case13.

The native `0x4CDCD0` 16-case label contract
is now **fully source-qualified**:
case13="Physiotherapist"; the nearby
`English.idx` entry1889="MASSEUR"
is **not** the same native case13 pointer.
`reconstruction/original_supportstart_staff_labels.py`
and tests now cover all sixteen without invented
fallbacks. This is native label-ordinal proof;
mapping an original generated staff instance's
virtual+0x14/type field to that ordinal still
needs independent source evidence and GUI
acceptance remains outstanding.

Reproduction:
```bash
objdump -D -Mintel --start-address=0x64a2d0 --stop-address=0x64a33d footballmanager.exe
objdump -D -Mintel --start-address=0x4cdd30 --stop-address=0x4cdd61 footballmanager.exe
# Count native 0x64E320 calls inclusive 0x6458B7..0x64A317:
objdump -D -Mintel --start-address=0x6458b0 --stop-address=0x64a330 footballmanager.exe
```
