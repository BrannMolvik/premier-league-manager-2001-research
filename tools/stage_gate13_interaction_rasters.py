"""Regenerate bounded immutable art from verified authorized source, outside runtime."""
import argparse
from hashlib import sha256
import json
import lzma
from pathlib import Path
import struct
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'reconstruction'))
from ea444_decoder import decode_ea444
from ea444_tables import CANONICAL_EXE_SHA256, tables_from_original_executable
from ea444_quantization import quantization_from_verified_executable
from original_teamselect_resources import (
    GLOBAL_BACKGROUND_PATH, GLOBAL_BACKGROUND_SHA256,
    TEAMSELECT_BACKGROUND_PATH, TEAMSELECT_BACKGROUND_SHA256,
    TEAMSELECT_BUTTON_ATLAS, HIERARCHY_ANIM_SPEC, HIERARCHY_BARS_SPEC,
    TEAMSELECT_CLUB_ANIM_PATH, TEAMSELECT_CLUB_ANIM_SHA256,
    TEAMSELECT_CLUB_BARS_PATH, TEAMSELECT_CLUB_BARS_SHA256,
)
from original_management_background import ASSET_HASHES
from gate13_ea444_staged_rasters import CONVERTER_ID, MANIFEST_SHA256, _load_bundle
from original_pmenu_chrome import PMENU_RESOURCES
from original_management_header import HEADER_RESOURCES
from original_squad_top_controls import (
    SQUAD_BUTTON_ATLAS_PATH, SQUAD_FIRST_TITLE_PATH, SQUAD_FIRST_TITLE_SHA256,
    SQUAD_FIRST_GRID_PATH, SQUAD_FIRST_GRID_SHA256,
)
from original_squad_resources import SQUAD_RESOURCES


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', type=Path, required=True)
    parser.add_argument('--executable', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--reuse-pinned-bundle', type=Path,
                        help='Reuse only an exact code-pinned bundle; originals are still rehashed')
    args = parser.parse_args()
    sources = {
        GLOBAL_BACKGROUND_PATH: GLOBAL_BACKGROUND_SHA256,
        TEAMSELECT_BACKGROUND_PATH: TEAMSELECT_BACKGROUND_SHA256,
        TEAMSELECT_BUTTON_ATLAS.source_path: TEAMSELECT_BUTTON_ATLAS.source_sha256,
        HIERARCHY_ANIM_SPEC.path: HIERARCHY_ANIM_SPEC.source_sha256,
        HIERARCHY_BARS_SPEC.path: HIERARCHY_BARS_SPEC.source_sha256,
        TEAMSELECT_CLUB_ANIM_PATH: TEAMSELECT_CLUB_ANIM_SHA256,
        TEAMSELECT_CLUB_BARS_PATH: TEAMSELECT_CLUB_BARS_SHA256,
    }
    # Generic native fallback family, not a Southport-specific modern substitute.
    sources.update({path: pin for path, pin in ASSET_HASHES.items()
                    if '/generic' in path or '/back_2_' in path})
    sources.update({resource.source_path: resource.sha256
                    for resource in (*PMENU_RESOURCES, *HEADER_RESOURCES)})
    sources.update({resource.source_path: resource.sha256 for resource in SQUAD_RESOURCES
                    if resource.source_path == SQUAD_BUTTON_ATLAS_PATH})
    sources.update({SQUAD_FIRST_TITLE_PATH: SQUAD_FIRST_TITLE_SHA256,
                    SQUAD_FIRST_GRID_PATH: SQUAD_FIRST_GRID_SHA256})
    exe = args.executable.read_bytes()
    tables = tables_from_original_executable(exe)
    quant = quantization_from_verified_executable(exe)
    manifest = dict(schema=1, converter=CONVERTER_ID,
                    executable_sha256=CANONICAL_EXE_SHA256,
                    tqia_sha256=sha256(tables.raw_section).hexdigest(),
                    quant_source_sha256=sha256(struct.pack('<64i', *quant.original_source)).hexdigest(),
                    quant_fixed_sha256=sha256(struct.pack('<64i', *quant.fixed_point)).hexdigest(),
                    images=[])
    reuse = {}
    if args.reuse_pinned_bundle:
        prior, reuse = _load_bundle(args.reuse_pinned_bundle, MANIFEST_SHA256)
        for field in ('tqia_sha256', 'quant_source_sha256', 'quant_fixed_sha256'):
            if prior[field] != manifest[field]:
                raise ValueError('Pinned reuse decoder identity mismatch: ' + field)
    chunks, offset = [], 0
    for path, pin in sorted(sources.items()):
        raw = (args.source_root / path).read_bytes()
        if sha256(raw).hexdigest() != pin:
            raise ValueError('Source identity mismatch: ' + path)
        print('Decode ' + path, flush=True)
        image = reuse.get(pin)
        if image is None:
            image = decode_ea444(raw, tables=tables, quant=quant)
        manifest['images'].append(dict(source_path=path, source_sha256=pin,
            source_size=len(raw), width=image.width, height=image.height,
            offset=offset, size=len(image.rgba), rgba_sha256=sha256(image.rgba).hexdigest(),
            consumed_bits=image.consumed_bits, transparent_pixels=image.transparent_pixels))
        chunks.append(image.rgba)
        offset += len(image.rgba)
    payload = lzma.compress(b''.join(chunks), preset=6)
    manifest.update(payload_size=offset, payload_xz_sha256=sha256(payload).hexdigest())
    encoded = (json.dumps(manifest, sort_keys=True, indent=2) + '\n').encode('utf-8')
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output / 'manifest.json').write_bytes(encoded)
    (args.output / 'payload.bin.xz').write_bytes(payload)
    print('manifest_sha256=' + sha256(encoded).hexdigest())
    print('images=' + str(len(chunks)) + ' compressed_bytes=' + str(len(payload)))


if __name__ == '__main__':
    main()
