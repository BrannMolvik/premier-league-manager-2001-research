# Feasibility Build 0.1

**Built:** 27 September 2026  
**Branch:** `agent/feasibility-build-0.1`

This is the first portable Windows feasibility build for the FM2001 modernization project. It is deliberately isolated from the active Gate-10 worker and is not a roadmap gate transition.

## Source baseline

The branch forked from:

```text
fa58826fc6d4d3f58fc12a357af04ea3e44939f8
Classify Gate 10 budget event enqueue paths
```

Gate 9 was complete at that point; Gate 10 was in progress.

Packaging branch build checkpoint:

```text
7b53ce06cb4229fdd6bcca0f60165e55aa65a6d1
Add WPF System.Xaml reference
```

The GitHub Actions Windows build passed:
- native WPF `IntroPlayer.exe` compile;
- PyInstaller one-folder `FM2001.exe` build;
- frozen executable `--help` smoke test;
- ZIP creation and artifact upload.

## Portable layout

```text
FM2001.exe
IntroPlayer.exe
_internal/
Assets/premintro.mp4
GameData/Master.dat
GameData/Static.dat
GameData/English.str
GameData/Core.str
GameData/FOOTBAL.EXE
Saves/
README_FIRST.txt
BUILD_INFO.txt
```

The portable launcher uses `GameData/` beside the executable automatically and falls back to a folder picker if those files are absent.

## Original intro

Authorized disc source:

```text
FMV/PREMINT.TGQ
SHA-256 a16e64a1c680ce1c7bcf57f76f05dd8e51a77663b5b4a673e681c9da188a0b0d
```

Converted outside Git for modern playback:

- H.264/AAC MP4;
- 53.638 seconds;
- 640x480;
- square pixels / 4:3 display;
- stereo audio;
- SHA-256 `3d49a9067d7842c84cc1f7d0be58b496be1a73c15223f800fa666f177fd6ba06`.

The conversion corrects the source 320x480 storage aspect for 4:3 display. A small WPF helper plays it full-screen with `Stretch.Uniform`; Escape, Space, Enter or click skips the intro.

## Canonical game files

All packaged game-data files were extracted directly from the authorized disc image outside Git and verified against the established canonical hashes.

## Final assembled package

```text
FM2001-Feasibility-0.1-Portable.zip
size: 34,173,394 bytes
SHA-256: ac2c7232cc707837f51b5ec9a14ac89e4320cfaeeca44fc304b4b874d3dbd912
entries: 995
```

Original binary assets remain outside Git. Only packaging source, provenance and reproducibility instructions are committed.

## Scope

This is a feasibility package, not an alpha/release. It validates:
- portable Windows startup without an installer;
- frozen Python/Tk runtime;
- original-data discovery from a relative directory;
- original intro playback before the modern runtime;
- the existing temporary gameplay UI and save/load surface.

The original FM2001 management front end remains a later roadmap gate. A managed PC-bang environment may independently block unsigned/unknown executables.
