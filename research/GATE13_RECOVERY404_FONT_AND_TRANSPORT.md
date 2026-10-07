# Recovery 404 — 36px Zurich source extraction and Windows transport probe

_8 October 2026 KST. Gate 13, original-behavior-only freeze._

## Verified source acquisition

Canonical private Library archive: `/FM2001/Original Source/The-F-A-Premier-League-Football-Manager-2001_Win_EN_Disc-Image.zip`. Size **511,121,336 bytes**; SHA-256 `677dcbc859109818d22599f34890ca7873393aea5adbf1f1f1a32d1a76f8a8a4`. Inside: ZIP member `F.A. Premier League Football Manager 2001/famg2001.bin`, **631,627,248 bytes**; original raw CD-ROM MODE1/2352 stream.

Joliet file `Fonts/Zurich_BdXCn_BT_36pixel.fnt` (disc alias `ZURICH8.FNT`) has ISO logical extent **170896** and length **155544**. MODE1 sectors are 2352 raw bytes; the 2048-byte file payload begins at sector offset 16. The original font spans `ceil(155544/2048) = 76` raw sectors. Stream the BIN until offset `170896 * 2352`, concatenate each sector's `[16:2064]` payload, and truncate to 155544 bytes.

**Independent Recovery-404 byte verification:** exact length **155544**, SHA-256 `92a10c37d85a5bd23bab3ca8aee69779a570a47e5a8b25cbf0e5f0bf13c835df`, matching the preexisting native font source trace. The archive was independently hashed during this session. No need to recover the full BIN onto disk: Python `zipfile.ZipFile.open()` can discard streamed bytes until the targeted extent.

Minimal deterministic reproduction with an authorized local ZIP:

```python
import hashlib, math, zipfile
from pathlib import Path

archive = Path("PATH_TO_PRIVATE_AUTHORIZED_ZIP")
with zipfile.ZipFile(archive) as z:
    member = next(x.filename for x in z.infolist() if x.filename.endswith("/famg2001.bin"))
    with z.open(member) as source:
        remaining = 170896 * 2352
        while remaining:
            piece = source.read(min(8 * 1024 * 1024, remaining))
            if not piece: raise EOFError("BIN truncated before font extent")
            remaining -= len(piece)
        data = bytearray()
        for _ in range(math.ceil(155544 / 2048)):
            sector = source.read(2352)
            if len(sector) != 2352 or sector[15] != 1:
                raise ValueError("invalid MODE1 sector")
            data += sector[16:2064]
font = bytes(data[:155544])
assert hashlib.sha256(font).hexdigest() == "92a10c37d85a5bd23bab3ca8aee69779a570a47e5a8b25cbf0e5f0bf13c835df"
```

Do **not** commit the parent disc image, ZIP, uncontrolled extracts, or unverified source content. When a trusted Git binary upload path is available, stage only the source font under `original_assets/source/Fonts/Zurich_BdXCn_BT_36pixel.fnt`, update `original_assets/MANIFEST.md` with exact source path/hash, and preserve source integrity checks. The existing PR #550 raster contract is fail-closed until the authentic font is supplied. Test canonical Southport plus a different club through the same code path.

**Transfer blocker in this recovery:** local extraction worked, but Files Library upload from `/mnt/data` failed with `container_session_unavailable`. GitHub blob creation currently has no file-reference upload; it expects inline base64 or UTF-8 content. Do not fabricate or manually reconstruct binary bytes. Extraction is **verified**, Git staging is **not**.

## Startup-FMV transport diagnostic

PR #551 merged on `main` as `09ee9e7d6d11b0f8b36b9fd86a3717eee9a3e9a0`, from exact verified head `98adacf71e8fed800e351231a32a94a1688f2d92`. This opt-in WPF diagnostic records parent/child HWNDs, requested and actual rectangles, both client origins, effective DPI, and window/thread DPI-awareness. It deliberately leaves source video geometry unchanged: coded 320x480 -> horizontally repeated 640x480 -> (80,60) in the 800x600 native field.

On a **qualifying private Windows 11 environment** with the authorized installed game files, a source-valid non-disruptive game window, and a separate private output outside Git, the CLI shape is:

```powershell
python -m reconstruction.gate14_windows_startup_media_audit --game-dir "C:\Private\FM2001" --application-root "C:\Private\FM2001-port" --output-receipt "C:\Private\fm2001-transport-probe.json" --transport-probe-only
```

Those Windows paths are **placeholders**, not claims of real local installation paths. Probe mode plays the verified source media sequence but skips human visual/audible acceptance, writing receipt schema 3 with `audit_kind=gate13_windows_startup_transport_probe`, `visual_acceptance_claimed=false`, `startup_media_real_windows_verified=false`; its `passed=true` describes probe acquisition **only**. A human must separately judge visual equivalence. The original native-executable launch-safety restrictions in `research/CONTINUATION_INSTRUCTIONS.md` remain in force. Do not interrupt the owner's foreground use or assume renewed consent to unsafe fullscreen or audio manipulation.

**Next investigation once a real receipt exists:** compare actual client-relative child/window rectangles and DPI awareness to the requested coordinates. Do not change native film geometry or optimize the FMV by eye. Keep Gate 13 and audit open until both the header and Windows presentation/playability blockers are closed.
