# Failed and Inconclusive Approaches

_Last updated: 24 September 2026_

This document prevents future sessions from repeating analyses that have already been disproven, superseded, or shown to be low-value.

## Runtime / Windows

### Run original game as administrator

Attempt:
- launch restored original `footballmanager.exe` with “Run as administrator”.

Result:
- no visible change; game still did not open.

Conclusion:
- disproves the hypothesis that the immediate failure is simply denied write access to the legacy HKLM registry key.

Status:
- ruled out as the primary fix.

### Patch legacy HKLM registry access to HKCU

Attempt:
- back up executable;
- patch the relevant predefined-HKEY selector from HKLM to HKCU;
- create equivalent 32-bit HKCU game registry values.

Result:
- patch itself was applied correctly;
- Windows Device Guard / Code Integrity blocked the modified executable.

Conclusion:
- binary patching an already-unsigned legacy executable is not a practical way around the current host security boundary.

Status:
- abandoned on the main Windows host.

### Treat exit code -1 as an application-internal crash

Early interpretation:
- `start /wait footballmanager.exe` returned `-1`, suggesting a silent FM2001 startup failure.

Later evidence:
- Code Integrity Operational Event ID 3077 explicitly identifies the executable as blocked.

Conclusion:
- host execution policy must be considered before interpreting the return code as an internal FM2001 crash.

Status:
- superseded.

## Master.dat / player records

### Six-byte player-section header

Early assumption:
- uint32 player count + an additional uint16 header field.

Why it looked plausible:
- an earlier manual boundary calculation happened to produce plausible strings/records.

Disproof:
- EA's actual loader `0x421C80` reads one 4-byte player count and immediately starts 103-byte records;
- re-parsing at the four-byte boundary aligns names, clubs, dates and skill arrays correctly.

Conclusion:
- player section header is exactly four bytes.

Status:
- definitively wrong; do not reuse.

### One 18-byte player attribute block at +22..+39

Early assumption:
- 18 bytes represented player attributes.

Disproof:
- compact importer `0x418B90` performs a 3-byte position read at +21..+23, then two separate 17-byte reads at +24..+40 and +41..+57.

Conclusion:
- there are two 17-byte skill arrays, current and development target.

Status:
- definitively wrong; do not reuse.

### Linear `round(raw * 30 / 255)` skill conversion

Early prototype:
- used generic rounded linear conversion.

Recovered game formula:

`floor((30*raw + 128) / 255)`

Conclusion:
- old prototype conversion is not exact.

Status:
- superseded.

## Manager records

### Old manager offsets (+6/+8 names, +10 DOB, +22 joined, +29 club)

Early documentation used those offsets.

Disproof:
- direct byte validation against manager 10 and 204 produced malformed names such as “Ferguson Sijes” and “Wenger Gilhaus”;
- corrected layout resolves Alex Ferguson and Arsène Wenger exactly.

Correct offsets:
- +0 uint32 ID
- +4 first-name Core.str ID
- +6 surname Core.str ID
- +8 DOB
- +20 joined club
- +27 current club ID

Status:
- definitively wrong; corrected in FILE_FORMATS/FINDINGS.

## Club / budget analysis

### Assume runtime club +0x3C..+0x54 is the seven-budget block

Reason:
- seven consecutive dwords visually matched the seven fields in the start-season budget mail.

Disproof:
- EA's compact club reader maps:
  - runtime +0x3C from disk +0x2E localized sponsor string;
  - runtime +0x40 from disk +0x30 manager ID;
  - following bytes are ordinary club record data.
- Arsenal validates as sponsor string “Sponsor” and manager ID 204.

Conclusion:
- the similarity in count/spacing was coincidental.

Status:
- definitively rejected.

## Finance cheat-code analysis

### Label 0x516090 as /cash777 and 0x516020 as /budget777 from caller context

Reason:
- those tiny accessors appeared near current-cash and finance/business branches.

Disproof:
- RTTI resolves the global object at `0x877540` as C++ standard-library stream machinery:
  - `std::basic_istream`
  - `std::basic_istringstream`
  - `std::basic_streambuf`
  - `std::basic_stringbuf`
- therefore the byte getters around `0x515FF0..0x5160E0` expose stream/internal state, not cheat flags.

Conclusion:
- all cheat labels assigned to those accessors are invalid.
- literal switches `/cash777` and `/budget777` still exist, but their real data-driven parser/storage must be recovered separately.

Status:
- definitively superseded.

## Transfer deal states

### Interpret states 2/5 as counter-offer states

Early behavioral interpretation:
- transfer execution copied stored player terms and blocked completion when state 2/5 was present.

Later named-event evidence:
- reason-code/event classes identify state 2 as player-rejected/declined-contract outcome;
- state 5 is the swap/exchange variant.

Current safe model:
- 0/3 pending/unresolved
- 1/4 cleared/ready family
- 2/5 player rejected/declined
- +3 denotes swap/exchange variant

Status:
- earlier “counter-offer” label superseded.

## Documentation rule

When a later analysis disproves an earlier interpretation:
1. update the canonical file;
2. mark historical notes as superseded or remove them;
3. add an entry here if the mistake is likely to be repeated;
4. commit the correction before continuing.
