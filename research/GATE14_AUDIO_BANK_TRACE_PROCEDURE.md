# Gate 14 audio-bank source trace procedure

Status: **private evidence tooling only; audio-bank semantics remain open**.

The canonical source inventory proves that FM2001 ships 64 `.bnk` files, but
filenames alone are not sufficient to label a bank as menu music, match audio,
crowd sound, commentary, or any other runtime role.

`reconstruction/gate14_audio_bank_source_trace.py` provides the next bounded
source step without making that inference. It accepts only the canonical
original executable through the existing SHA-256-gated PE32 parser, scans
file-backed sections for null-terminated printable ASCII strings ending in
`.bnk`, and records raw little-endian occurrences of each candidate string VA.

Those raw occurrences are deliberately classified as **not proven xrefs**.
They are leads for later private control-flow inspection, not evidence of:

- an audio loader call;
- a bank/sample index;
- menu or login music identity;
- a match-event sound binding;
- playback timing or volume policy.

The trace JSON must remain outside the Git repository.

Example private invocation once the authorized executable is locally available:

```text
python reconstruction/gate14_audio_bank_source_trace.py \
  /private/path/FOOTBAL.EXE \
  --output /private/path/fm2001-audio-bank-candidates.json
```

The current cloud execution container cannot inspect the materialized 511 MB
source archive because container/Python access is returning a transient
`ClientError`. The archive remains available in the user's Library at
`/FM2001/Original Source/The-F-A-Premier-League-Football-Manager-2001_Win_EN_Disc-Image.zip`.
This is an execution-path limitation, not evidence that the source is absent.

Gate 14 remains open. A later checkpoint may assign a bank role only after an
embedded candidate is connected to a concrete executable loader/callsite with
source-backed control flow.
