# Recovery546: original PSupportStart staff Apply inactive-list dispatcher

Canonical owner original footballmanager.exe, 4,714,541 bytes, SHA256 833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3. Static original x86 analysis only; the original was NOT executed.

At native PSupportStart event2 0x4D0606 -> virtual+0x4C 0x4D0830, the Apply procedure first clears global source staff list head 0x875600 and registered selected DBRUser list heads +0x5B8/+0x5C4/+0x5D0. It iterates 7 source selector objects in reverse indices6..0. Per row 0x4D088A reads 0x652F80 UI flag, writes the inverse bool to selection-record+0x28+i, and fetches the original staff pointer from selection-record+0x0C+4i. A null pointer skips.

When the source flag is nonzero, original 0x4D08CD..0x4D0936 checks duplicate pointers in selected user staff lists +0x5BC/+0x5C8, dispatches staff through 0x4CA070, and can remove an existing node from current staff list +0x5D4 via 0x4D1880.

Original 0x4CA070 calls staff virtual+0x14 to obtain native staff type, subtracts 1, range checks 1..16, indexes EXACT 16-byte native table at 0x4CA0D8. Its bytes are FIVE zeros followed by ELEVEN ones. The first branch 0x4CA092 links the original staff pointer into selected user list head +0x5B8; the second 0x4CA0A6 links it into +0x5C4. Both allocate a source 12-byte list node and use original 0x617D70. Out-of-range has no insertion. This is source proven and independent of the separate six-human manager limit and seven PSupportStart selector slot limit. Initial six staff types (1,2,3,4,5,13) route five to +0x5B8 and one to +0x5C4 ONLY when this specific inactive-list dispatcher is invoked, not automatically during all new games.

If flag is zero, 0x4D093B..0x4D09E4 instead checks/removes any existing pointer from user +0x5BC/+0x5C8 via 0x4D1880 and ensures pointer nodes are in selected-user current-staff list +0x5D0/+0x5D4 and global list 0x875600/+0x875604 via original 0x617D70. Actual type-specific UI labels, edit toggles, list lifetime, interaction/return and shared CRT startup still need full original proof.

The proposed code is deliberately a pure mapping only (types1..5 to head0x5B8, types6..16 to head0x5C4), with strict out-of-range rejection. It does NOT recreate native linked-list nodes, staff recruitment, full Apply, original save format or GUI. Do not attach it to gameplay without independent owner/lifetime and mutation tests. Gates13–17 and real Windows11 playtest remain OPEN. PR638 original shared CRT issue still blocked.

Private reproduction: sha256sum footballmanager.exe; objdump -D -Mintel --start-address=0x4d0830 --stop-address=0x4d0a72 footballmanager.exe; objdump -D -Mintel --start-address=0x4ca070 --stop-address=0x4ca0cf footballmanager.exe; objdump -s --start-address=0x4ca0d0 --stop-address=0x4ca0e8 footballmanager.exe.


## Selector raw DWORD control bit semantics independently recovered

Original `0x652F80` is just three x86 instructions:
`mov eax,[ecx+0x18]`; `shr eax,0x0F`;
`and al,1`; `ret`. Therefore it
reads **bit15** from the native selector
control DWORD at offset +0x18; it does NOT
automatically imply an on-screen checkbox label
or human-specific meaning. Original
`0x4D0893..0x4D089E` tests the result
and writes `sete cl` (inverse 0/1) into
the record flag `+0x28+i`. A bounded
pure source helper now computes
`1 ^ ((word >> 15) & 1)`.
Correct source counterexamples:
state DWORD `0x7FFF -> flag1`,
`0x8000 -> flag0`,
`0x10000 -> flag1`, and
`0xFFFFFFFF -> flag0`.
32-bit range validated; rejects booleans,
negative or too-large modern input rather than
guessing bit fields. The original did not
execute in this recovery.

Reproduce:
```bash
objdump -D -Mintel --start-address=0x652f80 --stop-address=0x652f89 footballmanager.exe
objdump -D -Mintel --start-address=0x4d088a --stop-address=0x4d08a1 footballmanager.exe
```
This proves the selector's **read and stored flag**
only. It does not prove which click changes
that bit in real UI, state mutation ordering
through a complete Apply, or original modal
visibility/return.
