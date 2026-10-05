# Gate 13 PStartMenu staged derivative contract

## Purpose

Issue #482 measured a cold `startup.presenter_build` cost of about 26 seconds on
Daniel's Windows 11 machine. The ordinary launch path currently derives EA444
decoder inputs from the verified original executable, decodes immutable first
screen art, parses the original Zurich font/language pair, composes the
PStartMenu background, and verifies the result before Tk is created.

Those checks are fidelity evidence, but repeating deterministic source
conversion on every user's first launch is not required for a Windows 11 port.
The authorized asset policy permits deterministic converted derivatives when
their source provenance remains exact.

## Canonical derivative scope

`reconstruction/gate13_pstartmenu_derivative.py` defines schema version 1.
It is intentionally **not wired into normal startup**.

The derivative contains only immutable render inputs already produced by
`load_verified_english_pstartmenu_inputs()`:

- exact composed 800x600 RGBA PStartMenu background;
- all 23 169x25 RGBA frames from the original
  `button_type_1.444` source atlas, in source order;
- the four original English caption alpha masks plus their recovered
  event/index/rectangle/origin/style/color metadata.

Pointer state, hover state, animation progress, navigation state, gameplay
state, and any other runtime state are not serialized.

## Provenance contract

The manifest records the exact source identities for:

1. `FM2001_Art/Generic/bground.444`;
2. `FM2001_Art/Generic/main_menu/main_menu_bground.444`;
3. `FM2001_Art/Generic/GenericButtonsAndBars/button_type_1.444`;
4. `Fonts/Zurich_BdXCn_BT_20pixel.fnt`;
5. `English.str`;
6. `English.idx`.

It also records:

- canonical original executable SHA-256;
- exact TQIA decoder-section SHA-256;
- exact original quantization-source SHA-256;
- converter/schema identity;
- geometry and payload offsets;
- payload and component SHA-256 values.

`decoder_provenance_from_verified_executable()` derives the TQIA identity
only after the existing executable/table/quantization verifiers accept the
canonical original executable. No guessed decoder bytes are accepted.

## Promotion boundary

A self-consistent manifest and payload are **not sufficient** for runtime use.
Loading requires a separately pinned SHA-256 of the canonical manifest. This
means a changed payload plus a rewritten self-consistent manifest cannot be
promoted merely by passing internal hashes.

Before normal launch may consume this derivative, all of the following must be
true:

1. the authorized canonical executable is available to the private generation
   step;
2. its exact TQIA and quantization inputs are reverified;
3. the real source-backed PStartMenu resources are generated through the
   existing decoder/font/language path;
4. schema-v1 manifest and payload are generated deterministically;
5. an independent regeneration or source-decode comparison proves the same
   bytes;
6. the resulting manifest SHA-256 is pinned in repository evidence;
7. repository source originals still pass the first-screen manifest-readiness
   audit;
8. package/asset-policy CI verifies the staged derivative and provenance;
9. only then may normal startup switch from cold source decode to the verified
   staged derivative;
10. Daniel's Windows 11 cold-launch timing is measured again.

Until those conditions are met, the current source-decode path remains the
normal path and the 26-second cold-start regression remains open.

## Exact next source/private action

When private execution becomes healthy, use the authorized canonical
`footballmanager.exe` to derive the decoder provenance, run the existing
`load_verified_english_pstartmenu_inputs()` source path, generate the
schema-v1 bundle, and preserve its manifest/payload hashes. Do not invent or
transcribe the missing TQIA bytes from memory.

After independent verification, stage the derivative under
`original_assets/converted/pstartmenu-v1/`, record conversion provenance in
`original_assets/MANIFEST.md`, add package/asset-policy regeneration or
verification, and only then wire the normal runtime to it.
