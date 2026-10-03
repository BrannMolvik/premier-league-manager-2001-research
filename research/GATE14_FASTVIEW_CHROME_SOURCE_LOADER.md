# Gate 14 FastView direct-chrome source loader

_Status: independent Gate-14 work-ahead while Gate 13 remains Codex-owned._

## Purpose

The FastView top bar and ticker already have exact PictureControl ownership,
source paths, checksums, dimensions, and screen rectangles. Their art object
builder previously required decoded EA444 images supplied by a caller.

This checkpoint adds a direct source-root loader so a private/runtime path can
construct those original pixels from an authorized FM2001 extraction without
staging or substituting the binary art in Git.

## Exact source inputs

Only the two directly owned resources are accepted:

- FM2001_Art/FastView/top_bar.444
  - 19,268 bytes
  - 800x95
  - screen rectangle (0,0)-(800,95)
  - SHA-256 f7410cf85900846ee1b276fa309bca4e560580286d5641092f2f98d20afa379a
- FM2001_Art/FastView/ticker.444
  - 6,352 bytes
  - 800x33
  - screen rectangle (0,557)-(800,590)
  - SHA-256 b0fe2d8266ae157b7821e8c1de310e89bbc37ae859f666e64f59731c78e68257

The separately discovered FastView/background.444 remains explicitly unbound
and is not loaded.

## Verified decode path

load_verified_fastview_chrome_art_from_source(source_root, original_executable):

1. requires the supplied canonical FOOTBAL.EXE;
2. obtains EA444 entropy/zigzag tables only through the canonical-executable
   table extractor;
3. obtains the original fixed-point quantization source only through the
   canonical-executable quantization extractor;
4. reads the exact two original chrome paths;
5. requires recorded source byte size and SHA-256;
6. decodes with the recovered EA444 decoder;
7. requires the decoded geometry;
8. returns the existing OriginalFastViewChromeArt placement object.

No replacement codec table or substitute image path is accepted.

## Validation boundary

The source-file reader is factored independently so hosted synthetic tests can
prove missing-file, wrong-size, and checksum-mismatch failure without shipping
the licensed executable. A separate test proves a missing executable fails
before decode.

The exact original bytes remain intentionally outside Git. The branch requires
hosted CI before merge because the current ChatGPT process sandbox cannot run
local Python.
