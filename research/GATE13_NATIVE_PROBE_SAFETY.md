# Gate 13 private native-probe safety qualification

4 October 2026 KST, PR #309. **Not qualified for an original launch.**
Gate 13 remains open. No original executable was launched in this investigation.
Neither capacity initialization nor a human-away complete report is proven.

## Windowed configuration: corrected, offline checks only

The private dgVoodoo 2.87.5 configuration previously set
`General.FullScreenMode=false` but omitted `DirectX.AppControlledScreenMode`.
The installed vendor template sets application-controlled mode true; the
matching official SDK `ConfigDirectX` constructor likewise defaults
`appControlledScreenState` true. FullScreenMode alone is therefore not a
safe forced-windowed prerequisite. No original launch tested that incomplete
configuration.

Only the private configuration was amended to explicitly require:

- `FullScreenMode=false`, `AppControlledScreenMode=false`;
- `DisableAndPassThru=false`, `DisableAltEnterToToggleScreenMode=true`;
- no forced desktop resolution/bit depth or windowed/fullscreen attributes;
- unforced rendering resolution, no mouse capture, centering or screen-saver
  suppression; no system hooks.

`gate13_native_probe_safety.py` rejects omitted, duplicated, malformed,
inherited, unsupported-version or unsafe settings and mismatched wrapper bytes.
It reports offline success with **vendor-parser/runtime/silence/launch
qualification all false**. The debugger's normal launch refusal is unchanged;
no flag, receipt or configuration file authorizes a bypass. Daniel's latest
restriction now blocks ALL original launches, including entry/CRT calibration,
before executable access/process creation. Historical controls are not exceptions.

Private configuration SHA-256:
`dc1b817547f98c206744f25ad0619c6b4bb9e00633213ba6be1faa4da37dd9e7`.
Private wrapper SHA-256 remains:
`612a24408a090a3c6f3886557fa18034ee742e94ad0a40ebdf854d2816176c2e`.
Installed configuration, game files, registry and executable were not changed.

The vendor documents local config lookup and that an unreadable config can be
skipped in favor of defaults: our parser is not vendor/runtime confirmation.
Official sources: [dgVoodoo readme](https://dgvoodoo2.dege.freeweb.hu/dgVoodoo2/ReadmeGeneral/),
[matching 2.87.5 developer package](https://github.com/dege-diosg/dgVoodoo2/releases/tag/v2.87.5).
Developer headers/binaries remain private, not redistributed in this repository.

## Silence: pre-play method identified, execution qualification blocked

Polling a future process's audio sessions cannot prove silence before its first
sample. Microsoft instead documents `IAudioSessionManager.GetSimpleAudioVolume`
with null session GUID/cross-process false: called inside the target process,
it opens an empty process-specific default session before a stream exists.
`ISimpleAudioVolume.SetMute` controls that session rather than endpoint volume.
Legacy DirectSound/DirectShow/waveOut default to that session; nondefault or
cross-process streams require separate coverage, not an assumption.
Sources: [GetSimpleAudioVolume](https://learn.microsoft.com/en-us/windows/win32/api/audiopolicy/nf-audiopolicy-iaudiosessionmanager-getsimpleaudiovolume),
[legacy audio sessions](https://learn.microsoft.com/en-us/windows/win32/coreaudio/audio-events-for-legacy-audio-applications).

A private experimental 32-bit helper was built to pre-create/mute/read back
the current process's default session on every active render endpoint and retain
its controls. Its proposed self-test contains only zero PCM and no original
binary or GUI, including mute read-back before stream write and after a legacy
volume call. **It did not execute.** The build had ABI-related compiler warnings,
so it is unreviewed/unqualified, retained outside Git, not an approved probe DLL.

Windows rejected `gate13_process_silence_selftest.exe` at process start:
“An Application Control policy has blocked this file.” Matching Code Integrity
events 3077/3033 confirm the Enterprise signing/policy denial. Blocked executable
SHA-256: `da33f2d6737ae3447780bdc468ea8b84c4271ed3039bed4f987d966f6752f606`.
No policy exception, alternate execution route, security-setting change or
original launch was attempted after the denial.

Six offline safety tests, the existing focused debugger/resource/geometry tests
(34 total), asset policy, JSON-state and diff checks pass. These do not substitute
for mute/windowed runtime qualification or a final Windows/normal-play audit.

## Exact remaining prerequisite / continuation

Obtain an approved native build/signing/execution route for a reviewed minimal
probe helper; do not whitelist this unqualified candidate or disable security
globally. Qualify pre-play mute on harmless legacy streams first, including
nondefault-session/device changes and other-process isolation where applicable.
Establish a pre-original-audio initialization boundary without game-logic edits.
Separately qualify the exact 32-bit wrapper/config runtime, non-exclusive
presentation and unchanged desktop/window state using a harmless fixture before
launching the original. No original launch until **both** safeguards pass.

Then resume the existing actual allocation/import hardware-watch through
`DBRClub +13C/+140` consumption, adjudicate object/CFG/write/copy/alias semantics,
integrate only proven behavior and run the genuine human-away report/save/
fresh-reload/right-click route. Do not reuse controlled-home capacities or infer
zero from allocation snapshots. Ask Daniel before any genuinely required
disruptive observation. Ownership and independent Gate-14 work are unchanged.
