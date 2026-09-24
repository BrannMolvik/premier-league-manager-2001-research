# Runtime Compatibility

_Last updated: 24 September 2026_

This file records experiments aimed at running the original Premier League Manager 2001 executable on the user's current Windows system.

## Analyzed executable / release

The available media is a FairLight-era release rather than a pristine retail disc.

Important components observed in the image:

- 32-bit x86 `footballmanager.exe`
- original/protected `FOOTBAL.ICD`
- old C-Dilla/SafeDisc-era protection components including `SECDRV.SYS`
- obsolete DirectX 7-era setup
- original 3D setup utility

The original executable imports legacy Windows/DirectX families including DirectDraw, DirectInput, DirectSound and WinMM.

Do not install/run `SECDRV.SYS` or the old DirectX installer on the modern host.

## Modernized installation

A local modernizer was built to avoid the obsolete 16-bit installer.

Verified result:

- game tree reconstructed under `C:\Games\FM2001`
- Joliet long filenames preserved
- obsolete installer/DRM/DirectX setup components excluded from the runtime install
- required legacy registry entries reconstructed
- dgVoodoo2 wrapper files/configuration staged
- desktop shortcut created

The modernization process itself completed successfully.

## 3D setup

`C:\Games\FM2001\Setup\3DSetup.exe` runs on the current machine.

Observed GPU:

- NVIDIA GeForce RTX 5070 Laptop GPU

Using the program's defaults produced:

- Triple Buffer: off
- Stadium Light Maps: off
- Sky Dome: on
- Player Shadows: on
- Texture Detail: medium

Windows Program Compatibility Assistant incorrectly treated the configuration utility as a possible failed installer; choosing “This program installed correctly” was appropriate.

## Original game launch behavior

Launching the unmodified `footballmanager.exe`:

- desktop shortcut: brief busy cursor, no window
- direct Explorer launch: same
- Command Prompt with `start "" /wait footballmanager.exe`: returned exit code `-1`
- Run as administrator: no visible difference

The lack of change under administrator elevation disproved the working hypothesis that failure was simply caused by denied write access to the legacy HKLM game key.

## Code Integrity / Smart App Control

Windows Code Integrity logging provided the decisive host-runtime result.

Code Integrity Operational **Event ID 3077** explicitly named:

`C:\Games\FM2001\footballmanager.exe`

This establishes that the modern host blocks the legacy executable before normal game startup can proceed.

Consequences:

- launching through CMD does not bypass the block;
- administrator elevation does not bypass the block;
- ordinary application compatibility settings cannot solve a pre-execution Code Integrity denial;
- a modified unsigned copy is also subject to the same trust policy.

## Registry experiment

Static analysis showed the executable opens:

`HKLM\SOFTWARE\EA SPORTS\Football Manager 2001`

with legacy access expectations.

A diagnostic one-byte patch changed the relevant predefined-HKEY selector from HKLM to HKCU.

Actions performed:

- backup created as `footballmanager.before-hkcu-patch.exe`
- one-byte HKLM -> HKCU patch applied successfully
- 32-bit HKCU values created for:
  - `Install Dir = C:\Games\FM2001`
  - `CD Drive = C:\Games\FM2001`

Result:

- Windows Device Guard / Code Integrity explicitly blocked the modified executable.

The original executable was restored from backup afterward.

Because the restored original also failed identically under administrator elevation, the HKLM-permission theory was abandoned.

## Security boundary

The project deliberately did **not** disable Smart App Control, Device Guard, Defender or antivirus protections merely to run this old executable.

The practical runtime fallback remains:

1. persistent VM / isolated compatibility environment for the authentic original executable; or
2. continue the clean-room reimplementation so the old executable is not required.

## Current host-runtime conclusion

The main blocker on the current Windows installation is not yet a proven DirectX/rendering crash. It is the host's Code Integrity policy refusing the legacy unsigned executable.

Further native-host graphics/audio compatibility work is low-value until that execution-policy boundary is solved by a safe route.

## Test matrix

| Test | Result | Conclusion |
|---|---|---|
| Modernized installation | Success | Files/registry/runtime tree can be reconstructed without old installer |
| Original 3DSetup.exe | Runs | Legacy setup utility itself can execute |
| Desktop shortcut launch | No window | Game does not reach usable UI |
| Direct EXE launch | No window | Same behavior |
| CMD `start /wait` | Exit -1 | Silent early termination/block |
| Run as administrator | No change | Not simply HKLM permission failure |
| HKLM -> HKCU binary patch | Device Guard block | Modifying unsigned EXE worsens trust/reputation path |
| Code Integrity log | Event 3077 naming EXE | Host execution policy confirmed as blocker |
