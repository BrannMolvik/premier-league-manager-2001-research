# Gate 14 real-Windows startup-media acceptance audit

_Status: schema-2 production-host/WPF audit harness; private Windows 11 client
receipt still required._

## Purpose

The canonical Windows startup path now uses the source-backed FMV treatment
recovered during issue #482 rather than the earlier MCI compatibility attempt:

1. validate `FMV/easp.tgq` and `FMV/premintro.tgq` against their canonical
   source identities;
2. create or revalidate the private H.264/AAC derivative cache;
3. bake the recovered 320x480 -> 640x480 horizontal 2x nearest duplication into
   those derivatives;
4. construct the real `OriginalGameTkHost`;
5. show the game-owned black startup field;
6. bind `WindowsWpfStartupMediaBackend` as a child HWND of that realized game
   window at the host's source-derived movie rectangle;
7. play both verified derivatives synchronously in source order; and
8. return to the ordinary production host.

Hosted Windows package CI proves packaging, construction and smoke behavior. It
cannot prove that a real Windows 11 client actually displayed and sounded the
movies correctly. `reconstruction/gate14_windows_startup_media_audit.py`
provides that external acceptance boundary.

## Why schema 2 is required

The old schema-1 audit directly replayed derivatives through
`WindowsMciStartupMediaBackend`. That transport is no longer the normal
application path and therefore cannot certify current startup behavior.

Schema 2 fails closed unless the exact
`WindowsWpfStartupMediaBackend` is passed through
`run_original_game_ui()`. The production host must bind the backend to the
same parent HWND and rectangle returned by
`OriginalGameTkHost.startup_media_child_binding()`. Reaching the host-ready
callback proves the startup sequence completed before ordinary main-loop play.

The aggregate external-acceptance coordinator rejects schema-1 and MCI startup
receipts.

## Strict platform boundary

The audit refuses non-Windows systems, GitHub Actions, Windows Server/product
types other than a client workstation, and Windows builds below 22000. A hosted
runner therefore cannot be misrepresented as Daniel's required external
Windows 11 evidence.

## Source display contract

The receipt records the already recovered source treatment without broadening
it:

- coded TGQ video: 320x480;
- logical movie surface: 640x480;
- horizontal repeat: exactly 2;
- modern derivative filter: `scale=640:480:flags=neighbor`;
- ordinary logical game display: 800x600;
- ordinary logical movie offset: (80,60).

The actual child-HWND rectangle is also recorded because the modern host may
scale its entire logical 800x600 surface to the physical display. The audit
requires the WPF backend's retained parent HWND and rectangle to match the
production host exactly.

This does not claim byte-identical DirectDraw-era output. Native skip input and
exact fade/transition timing remain unresolved, and the receipt keeps broad
`exact_display_treatment_recovered` false.

## Human acceptance

Only after production-host startup playback completes does the audit ask the
operator to type exactly:

`YES-GAME-WINDOW`

That confirmation means all of these were personally observed:

- both startup videos were visible;
- both had audible audio;
- they remained embedded inside the FM2001 game-owned window rather than
  appearing as a separate player;
- the centered movie treatment had no obvious aspect distortion; and
- order was `easp.tgq`, then `premintro.tgq`.

Any other response fails closed and produces no success receipt.

## Private receipt

A passing schema-2 receipt records the Windows client identity, exact source and
converted media identities, WPF backend name, production-host boundary,
game-owned child-HWND binding, recovered source presentation contract, playback
completion, and explicit human visibility/audibility/game-window confirmation.

It deliberately keeps these unsupported claims false:

- top-level normal application CLI invocation;
- native skip input recovered;
- exact fade/transition timing recovered;
- broad exact DirectDraw-era display treatment recovered;
- Gate 14 complete.

The receipt must remain outside Git and cannot overwrite prior evidence.

## External command

On the actual Windows 11 client workstation:

```text
python reconstruction/gate14_windows_startup_media_audit.py ^
  --game-dir "C:\Games\FM2001" ^
  --application-root "C:\Path\To\FM2001-Windows11" ^
  --output-receipt "C:\private\gate14-startup-media-windows.json"
```

Do not commit the receipt, converted movies, original TGQs, or runtime cache.
