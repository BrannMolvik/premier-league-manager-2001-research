"""Pinned lossless EA444 rasters for measured Gate-13 interaction stalls.

This is a conversion boundary, not alternative art: original bytes are still
hash-checked by each owner. Hits additionally require the exact decoder tables
and quantization. Unknown/custom sources retain the original decoder. A damaged
known-source bundle fails closed, never falls back to an expensive cold decode.
"""
from functools import lru_cache
from hashlib import sha256
import json
import lzma
from pathlib import Path
import struct

from ea444_decoder import EA444DecodedImage, decode_ea444

BUNDLE_ROOT = Path(__file__).resolve().parents[1] / 'original_assets/converted/gate13-rasters-v1'
MANIFEST_SHA256 = 'b17a34521037ea367dfd7a869fa3a91d6672ed8a4a4d897106e884154f0f9e10'
CONVERTER_ID = 'fm2001-source-ea444-lossless-rgba-v1'


class StagedRasterError(ValueError):
    pass


@lru_cache(maxsize=2)
def _load_bundle(root: Path, manifest_sha256: str):
    raw = (root / 'manifest.json').read_bytes()
    if sha256(raw).hexdigest() != manifest_sha256:
        raise StagedRasterError('Gate-13 raster manifest hash mismatch')
    manifest = json.loads(raw)
    if manifest['schema'] != 1 or manifest['converter'] != CONVERTER_ID:
        raise StagedRasterError('Gate-13 raster converter/schema mismatch')
    compressed = (root / 'payload.bin.xz').read_bytes()
    if sha256(compressed).hexdigest() != manifest['payload_xz_sha256']:
        raise StagedRasterError('Gate-13 raster payload hash mismatch')
    payload = lzma.decompress(compressed)
    if len(payload) != manifest['payload_size']:
        raise StagedRasterError('Gate-13 raster payload size mismatch')
    images = {}
    cursor = 0
    for entry in manifest['images']:
        width, height = entry['width'], entry['height']
        size = width * height * 4
        if (type(width) is not int or type(height) is not int or width <= 0
                or height <= 0 or entry['offset'] != cursor
                or entry['size'] != size or cursor + size > len(payload)):
            raise StagedRasterError('Gate-13 raster geometry/ownership mismatch')
        rgba = payload[cursor:cursor + size]
        if sha256(rgba).hexdigest() != entry['rgba_sha256']:
            raise StagedRasterError('Gate-13 raster decoded-pixel hash mismatch')
        image = EA444DecodedImage(
            width, height, rgba, entry['consumed_bits'], entry['transparent_pixels'])
        previous = images.get(entry['source_sha256'])
        # Native title/child PMenu boxes are byte-identical source aliases.
        # Repeated original identity is legal only with identical decoded data.
        if previous is not None and previous != image:
            raise StagedRasterError('Gate-13 raster source alias disagrees')
        images[entry['source_sha256']] = image
        cursor += size
    if cursor != len(payload):
        raise StagedRasterError('Gate-13 raster payload has unowned bytes')
    return manifest, images


def decode_staged_or_original(source: bytes, *, tables, quant,
                              bundle_root=None, manifest_sha256=None):
    root = BUNDLE_ROOT if bundle_root is None else Path(bundle_root)
    pin = MANIFEST_SHA256 if manifest_sha256 is None else manifest_sha256
    manifest, images = _load_bundle(root, pin)
    image = images.get(sha256(source).hexdigest())
    if image is None:
        return decode_ea444(source, tables=tables, quant=quant)
    if (sha256(tables.raw_section).hexdigest() != manifest['tqia_sha256']
            or sha256(struct.pack('<64i', *quant.original_source)).hexdigest()
            != manifest['quant_source_sha256']
            or sha256(struct.pack('<64i', *quant.fixed_point)).hexdigest()
            != manifest['quant_fixed_sha256']):
        raise StagedRasterError('Gate-13 raster decoder input identity mismatch')
    return image
