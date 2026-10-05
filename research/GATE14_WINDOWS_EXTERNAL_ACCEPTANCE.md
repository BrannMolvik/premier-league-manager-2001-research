# Gate 14 external Windows acceptance coordinator

_Status: cloud-safe coordination tooling. Both child receipts still require an
actual external Windows 11 client and human confirmation._

## Purpose

Gate 14 currently has two independent external acceptance transactions whose
runtime paths are already canonical:

1. exact startup FMVs through the verified TGQ conversion/cache and Windows MCI
   playback path;
2. the source-backed first-screen Start New Game press through the production Tk
   host and `AudioHooks (10,0) -> menus.bnk slot 2`.

Neither hosted CI nor the existence of either harness is evidence that Daniel
actually saw/heard the corresponding output on Windows 11.

`reconstruction/gate14_windows_external_acceptance.py` provides one
transactional command for the future external run without merging the two proof
contracts.

## Transaction

The coordinator:

1. runs the existing startup-media acceptance audit;
2. requires its explicit human `YES-BOTH` confirmation;
3. runs the existing production-host bound-audio acceptance audit;
4. requires its explicit human `YES-HEARD` confirmation;
5. validates that both child receipts describe the same Windows client;
6. validates that both child contracts still keep their unsupported claims
   false;
7. only after both audits pass, creates one fresh output directory outside Git;
8. writes the two child receipts as separate JSON files; and
9. writes a small manifest containing SHA-256 values for the exact serialized
   child receipts.

If either live audit fails, no bundle directory is created. If bundle writing
fails, the newly created directory is removed rather than leaving partial
release-looking evidence.

## Deliberate evidence separation

The child receipts remain the evidence:

- `startup_media.json`;
- `bound_first_screen_audio.json`.

The aggregate `gate14_external_acceptance_bundle.json` is only an integrity
and coordination manifest. It may record the two narrow external checks as
verified, but it must keep all of these false:

- broad/application-wide AudioHooks event binding;
- human-readable sample meaning;
- hover audio;
- full login/menu audio integration;
- source FastView navigation trigger;
- recognizable original match workflow;
- Gate 14 completion.

A successful first-screen sound receipt proves that one bounded production-host
sound was heard. It does not convert the readiness model's broader
`audible_windows_verified` / login-menu criterion into true by itself.

## Intended external command

On the actual Windows 11 client, from the matching source checkout:

```text
python reconstruction/gate14_windows_external_acceptance.py ^
  --game-dir "C:\Games\FM2001" ^
  --application-root "C:\Path\To\FM2001-Windows11" ^
  --output-dir "C:\private\gate14-acceptance-<new-run>"
```

Use `--source-root` only when the normal source-backed production host needs
that existing override.

The output directory must not already exist and must remain outside Git. Do not
commit the receipts, original TGQs, BNK files, decoded audio, converted startup
movies, or runtime cache.

## Remaining Gate-14 boundary

Even after both external checks pass, Gate 14 still requires the unresolved
application-wide/login-menu audio integration and a recognizably original
source-backed match-presentation workflow. Private executable analysis remains
necessary for the unresolved source-semantic and FastView geometry/order work.
