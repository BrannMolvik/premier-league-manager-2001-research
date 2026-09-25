# Startup Presentation and Intro FMV

_Last verified: 26 September 2026_

## Scope

This note records direct inspection of the authorized FM2001 source disc and the original executable's startup path, specifically for the intro videos and their audio.

This work is presentation research only. It does not change the active Gate 2 startup-RNG task.

## Original disc resources

The Joliet filesystem contains:

- `FMV/easp.tgq`
- `FMV/premintro.tgq`
- `FMV/bground.444`
- `FMV/Credits2.txt`

The ISO9660 8.3 view truncates `premintro.tgq` to `PREMINT.TGQ`; the Joliet long filename and executable string both confirm the intended name is **`PREMINTRO.TGQ`**.

### easp.tgq

Confirmed properties from the original disc file:

- size: **1,383,304 bytes**
- SHA-256: `73dc078ee8fe7e1d7412b4bcba072c3f8ec85546d5e5b94f90be9732498af97c`
- container: Electronic Arts Multimedia
- video codec: Electronic Arts TQI
- decoded dimensions: **320 x 480**
- frame rate: **25 fps**
- decoded video frames: **97**
- audio codec: Electronic Arts ADPCM
- audio: **22,050 Hz, stereo**
- approximate decoded duration: **3.87 seconds**

A decoded frame visibly contains the period EA SPORTS logo.

### premintro.tgq

Confirmed properties from the original disc file:

- size: **28,434,180 bytes**
- SHA-256: `a16e64a1c680ce1c7bcf57f76f05dd8e51a77663b5b4a673e681c9da188a0b0d`
- container: Electronic Arts Multimedia
- video codec: Electronic Arts TQI
- decoded dimensions: **320 x 480**
- frame rate: **25 fps**
- decoded video frames: **1,275**
- audio codec: Electronic Arts ADPCM
- audio: **22,050 Hz, stereo**
- the decoded audio/video presentation is about **54 seconds** overall; the legacy container does not expose a normal duration field, and video-frame count versus decoded audio length differs slightly.

Decoded frames show the football/Premier League intro presentation.

## Important audio finding

**Confirmed:** the intro soundtrack/audio is embedded inside the TGQ files.

The intro therefore does not require us to reconstruct its music from a separate menu-music file. Reusing or converting `premintro.tgq` preserves the original video and its original synchronized stereo audio together.

## Original executable startup calls

Direct xrefs in the analyzed executable confirm both files are explicitly played during startup through the same FMV wrapper.

### EA Sports logo

At approximately `0x530FAE` the startup path pushes:

```text
0
0
"easp.tgq"
```

and calls FMV wrapper `0x461E20`.

### Premier League intro

Later, at approximately `0x531175`, the startup path pushes:

```text
0
1
"PREMINTRO.TGQ"
```

and calls the same FMV wrapper `0x461E20`.

Therefore the startup sequence directly evidenced in the executable is:

```text
EA Sports FMV (easp.tgq)
    ->
later startup/display initialization
    ->
Premier League intro FMV (PREMINTRO.TGQ)
    ->
normal front-end startup
```

## Playback wrapper behavior

`0x461E20`:

- checks a global FMV-disable flag through `0x515FF0`;
- constructs the source path using the configured FMV location;
- passes the resolved source to lower playback routine `0x461900`;
- restores front-end/display state after playback.

The third-party/EA multimedia layer used by the original executable is old, but the media itself is readable by modern FFmpeg.

### Input/skip behavior

The two startup calls differ in one flag:

- `easp.tgq`: flag value 0
- `PREMINTRO.TGQ`: flag value 1

Inside `0x461900`, bit 0 of that flag controls registration of input/event callbacks.

**Probable interpretation:** the longer `PREMINTRO.TGQ` is intended to be user-skippable, while the EA Sports logo does not register the same skip callbacks. The callback registration is confirmed; the exact user input mapped to "skip" still needs a focused trace before calling that semantic fully confirmed.

## Windows 11 playback feasibility test

A full practical conversion test was performed on the original `premintro.tgq` using modern FFmpeg.

Successful output:

- H.264 video
- AAC stereo audio
- 320 x 480
- 25 fps
- **53.638 seconds**
- output size about **12.5 MB**

This proves that the original intro picture and embedded original audio can be decoded and repackaged for reliable playback by a modern Windows 11 runtime.

The final port does not necessarily need to pre-convert to MP4. Viable implementation choices include:

1. decode TGQ directly with a bundled/runtime decoder;
2. perform a one-time conversion from the authorized original TGQ during installation/first run;
3. ship a provenance-tracked converted derivative under the authorized asset policy.

The simplest reliable modern route is likely to use a converted modern container while keeping the original TGQ as the provenance source.

## Porting target

For the mature Windows 11 port, preserve this startup experience:

```text
launch
 -> EA Sports logo/video with original audio
 -> Premier League intro video with original embedded audio
 -> original-style front end / menu
 -> original menu audio where separately identified
```

The intro FMV itself is therefore **not a reconstruction risk**. The remaining work is integration and exact startup/skip/transition behavior.

## Still to investigate

- exact input event(s) that skip `PREMINTRO.TGQ`;
- exact transition/fade behavior into the front end;
- whether any startup configuration disables FMVs and how that option is exposed;
- separate menu/login music after the FMVs;
- audio-bank contents and startup/menu sound-effect mapping;
- whether the original 320 x 480 stream expects a particular display/interlace treatment that should be reproduced rather than naively stretched.
