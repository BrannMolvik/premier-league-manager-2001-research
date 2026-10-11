# Recovery541: Original EAM transfer-preview reason persistence

Static disassembly of private verified original footballmanager.exe (4,714,541 bytes, SHA-256 833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3) establishes:

- Native constructor at 0x56FAE0..0x56FB69 writes signed -1 to record+0x3C at 0x56FB3C. The constructor installs 0x7CFEA8 (whose +0x18/+0x1C slot functions are 0x56FB70 and 0x56FBA0); the previously identified 0x7BDB1C also shares those slots. Do not infer the two tables' full lifecycle relationship.
- Native 0x56F9F0 reads the 4-byte record+0x3C from file via 0x667E90 (fread). Native 0x56FA60 passes it to 0x667FA7 (fwrite). Original value is persistent raw signed DWORD, not merely an untracked UI label.
- Native first selected transfer-mail preview enters virtual+0x1C argument zero at 0x56FD65, checks record+0x3C against -1 and if unset uses original RNG 0x66951C, writes the chosen result at 0x56FDFE, then formats via 0x612FD0 / 0x659810. Do not select reasons during row materialization or re-roll after save/load. See GATE13_EAM_PREVIEW_REASON_RNG_SIDE_EFFECT_RECOVERY541.md.

This bounded port change adds original_preview_reason_native_i32 to the real delivered initial-transfer EAM record (default -1, exact signed-32 bounds) and optionally includes it in the modern JSON save when nondefault. Older *modern* source records with no field safely initialize to -1 because no authentic original preview generation was implemented. A genuinely imported historical original native save is NOT asserted equivalent. Unit tests exercise raw initial state, corrupted input rejection, 3-as-fixture modern snapshot roundtrip and full HumanGameplayController save/load while preserving pending queue and other users.

This is a source-proven persisted field, NOT a qualified original RNG call, phrase selector, native visible body, read flag or original GUI acceptance. No original EXE executed. Gates 13-17 remain OPEN.

Next source work: native reason phrase table/selector, link live game RNG to exact stage, source manager/player name substitution and render original preview/PEAMMessage interaction at verified native art/clip coordinates. Verify first/second click, save/load and multiuser without duplicate RNG.
