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

Windows rejected the earlier `gate13_process_silence_selftest.exe` at process start:
“An Application Control policy has blocked this file.” Matching Code Integrity
events 3077/3033 confirm an App Control signing/policy denial. Blocked executable
SHA-256: `da33f2d6737ae3447780bdc468ea8b84c4271ed3039bed4f987d966f6752f606`.
No policy exception, alternate execution route, security-setting change or
original launch was attempted after the denial.

## Policy diagnosis and warning-clean native rebuild

Read-only correlation now identifies the denial as **Smart App Control's
`VerifiedAndReputableDesktop`** policy, GUID
`{0283ac0f-fff1-49ae-ada1-8a933130cad6}`, PolicyID `27555.1000.240208`.
3077 record 67925 and 3033 record 67923 share ActivityID
`{59f2b987-5020-0008-8bc9-ef5b2050dd01}` with 3089 records 67926/67924.
The denial has requested signing level **2**, validated level **1**, status
`0xc0e90002`; signature events show **zero signatures**, Unknown publisher/issuer.
Level 2 means policy acceptance is required, not proof that only an
organization-specific or Microsoft signer is allowed. No exact permitted signer
class or complete current enforced-policy inventory is claimed.
Sources: [App Control troubleshooting](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/app-control-for-business/operations/appcontrol-debugging-and-troubleshooting),
[Smart App Control testing](https://learn.microsoft.com/en-us/windows/apps/develop/smart-app-control/test-your-app-with-smart-app-control).

`CiTool -lp -json` failed non-elevated with access denied (OperationResult
`-2147024891`). The read-only elevated inventory request was cancelled at UAC;
it was not retried. The full inventory remains pending renewed approval.
Do not interpret missing inventory/3099 results as absence of other policies.

`tools/gate13_mute_selftest.cpp` replaces the warning-bearing experimental
candidate with a minimal **Microsoft Windows SDK native x86** self-test. It uses
the SDK's actual COM interfaces/ABI and RAII, checks current-process ownership,
mutes/retains empty default sessions before opening a legacy stream, then writes
only 100 ms of zero PCM with bounded mute read-back. It contains no original
executable, proprietary data, injection, GUI, endpoint master-volume API or
other-process mutation. A pass would qualify only this harmless test, not every
original audio path or an original launch.

Build-only [Microsoft runner result](https://github.com/BrannMolvik/premier-league-manager-2001-research/actions/runs/37189161424)
passes at `4901e529d5f96209d646bd41e77bd2a9ad50f5dc` using Microsoft `cl.exe`,
Windows SDK, `/W4 /WX`, native x86 `/MACHINE:X86`, static CRT and mitigation flags.
No ABI/compiler warnings remain. Neither runner nor local machine executed it.
The downloaded artifact is PE machine `0x014c`, Authenticode `NotSigned`.

- Reviewed LF source SHA-256:
  `39d1aa0e13c033c6c4eb1de0cabb28f58c966ef0f9064cfbc6ebebb2c754f9df`.
- Exact Windows-runner CRLF source SHA-256:
  `14169d97dc877184416d1c53432a8fd5ee112d8a8706e9f17e484482d0a29f84`.
  Line-ending normalization verifies that these are the same reviewed source.
- Unsigned helper SHA-256:
  `4ebe2420fa798528df29c05b036a5f447e1178d8ed53c4f74e0dbce892c79f84`.
- Private receipt `work/gate13-native-signing-diagnosis-20261004.json` retains
  12 correlated event records/XML, source/build identities and compiler output
  reference. Receipt SHA-256:
  `7ee1810c542bfaeff2b7f56ae1b9bea77788003bfb469fc1fbd41cb0d2ed7020`.
  Signed hash, signer and SignTool verification are explicitly absent/pending;
  helper/original execution and both runtime safeguards remain false.

No approved Artifact Signing endpoint/account/certificate profile or
authentication route has been identified; Daniel has been asked for identifiers
and authentication method, **not secret keys**. No signing account/profile was
created, signature fabricated, self-signed root trusted or allow rule deployed.
Microsoft recommends Artifact Signing for Smart App Control; a trusted signature
is not a guarantee of acceptance by every enforced policy.
Sources: [Smart App Control signing](https://learn.microsoft.com/en-us/windows/apps/develop/smart-app-control/code-signing-for-smart-app-control),
[Artifact Signing integration](https://learn.microsoft.com/en-us/azure/artifact-signing/how-to-signing-integrations).

Six offline safety tests, the existing focused debugger/resource/geometry tests
(34 total), asset policy, JSON-state and diff checks pass. These do not substitute
for mute/windowed runtime qualification or a final Windows/normal-play audit.

## Exact remaining prerequisite / continuation

Complete the read-only enforced-policy inventory with renewed UAC approval and
obtain Daniel's approved Artifact Signing endpoint/account/profile/authentication
route. Sign the **exact reviewed unsigned helper** with SHA-256 Authenticode,
retain unsigned/signed hashes and signer, and verify with SignTool before
executing only the harmless mute self-test. If it is still denied, stop and
correlate the exact new policy/signature events; do not seek an execution bypass.
An organization-specific signer or supplemental policy is a separate
administrative action requiring Daniel's approval, not something this worker
deploys. Do not whitelist a candidate, trust a self-signed root or weaken App
Control. Qualify pre-play mute on harmless legacy streams first, including
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
