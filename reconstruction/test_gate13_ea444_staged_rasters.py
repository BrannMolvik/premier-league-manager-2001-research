from hashlib import sha256
import json
import lzma
from pathlib import Path
import struct
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import gate13_ea444_staged_rasters as staged
from ea444_decoder import EA444DecodedImage
from ea444_tables import EA444Tables
from ea444_quantization import EA444Quantization


class StagedRasterTests(unittest.TestCase):
    def setUp(self):
        staged._load_bundle.cache_clear()
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.tables = SimpleNamespace(raw_section=b'qualified-table-fixture')
        self.quant = SimpleNamespace(original_source=tuple(range(64)),
                                     fixed_point=tuple(range(64)))
        self.source = b'original-fixture'
        self.rgba = bytes((10, 20, 30, 0, 40, 50, 60, 255))
        payload = lzma.compress(self.rgba)
        self.manifest = dict(schema=1, converter=staged.CONVERTER_ID,
            tqia_sha256=sha256(self.tables.raw_section).hexdigest(),
            quant_source_sha256=sha256(struct.pack('<64i', *self.quant.original_source)).hexdigest(),
            quant_fixed_sha256=sha256(struct.pack('<64i', *self.quant.fixed_point)).hexdigest(),
            payload_xz_sha256=sha256(payload).hexdigest(), payload_size=len(self.rgba),
            images=[dict(source_sha256=sha256(self.source).hexdigest(),
                         width=2, height=1, offset=0, size=8,
                         rgba_sha256=sha256(self.rgba).hexdigest(),
                         consumed_bits=123, transparent_pixels=1)])
        (self.root / 'payload.bin.xz').write_bytes(payload)
        self.pin_manifest()

    def pin_manifest(self):
        raw = json.dumps(self.manifest).encode()
        self.pin = sha256(raw).hexdigest()
        (self.root / 'manifest.json').write_bytes(raw)

    def decode(self, source=None):
        return staged.decode_staged_or_original(
            self.source if source is None else source,
            tables=self.tables, quant=self.quant,
            bundle_root=self.root, manifest_sha256=self.pin)

    def test_exact_pixels_mask_and_metadata_without_runtime_decode(self):
        with patch.object(staged, 'decode_ea444', side_effect=AssertionError('cold decode')):
            first = self.decode()
            self.assertEqual(first, EA444DecodedImage(2, 1, self.rgba, 123, 1))
            self.assertIs(first, self.decode())

    def test_unknown_sources_use_original_decoder_not_another_cached_image(self):
        expected = object()
        with patch.object(staged, 'decode_ea444', return_value=expected) as decoder:
            self.assertIs(self.decode(b'other-original'), expected)
            decoder.assert_called_once_with(b'other-original', tables=self.tables, quant=self.quant)

    def test_table_and_both_quantization_identities_are_required(self):
        for change in ('tables', 'original_source', 'fixed_point'):
            with self.subTest(change=change):
                if change == 'tables':
                    old = self.tables
                    self.tables = SimpleNamespace(raw_section=b'wrong')
                else:
                    old = self.quant
                    values = dict(original_source=old.original_source, fixed_point=old.fixed_point)
                    values[change] = (99,) + values[change][1:]
                    self.quant = SimpleNamespace(**values)
                with self.assertRaisesRegex(staged.StagedRasterError, 'input identity'):
                    self.decode()
                if change == 'tables':
                    self.tables = old
                else:
                    self.quant = old

    def test_manifest_and_payload_corruption_fail_closed(self):
        (self.root / 'manifest.json').write_bytes(b'{}')
        with self.assertRaisesRegex(staged.StagedRasterError, 'manifest hash'):
            self.decode()
        self.pin_manifest()
        (self.root / 'payload.bin.xz').write_bytes(b'corrupt')
        with self.assertRaisesRegex(staged.StagedRasterError, 'payload hash'):
            self.decode()

    def test_rgba_geometry_offset_and_converter_fail_closed(self):
        for field, value, message in (
            ('rgba_sha256', '0'*64, 'pixel hash'), ('offset', 1, 'ownership'),
            ('width', 3, 'geometry'), ('height', False, 'geometry')):
            with self.subTest(field=field):
                old = self.manifest['images'][0][field]
                self.manifest['images'][0][field] = value
                self.pin_manifest()
                with self.assertRaisesRegex(staged.StagedRasterError, message):
                    self.decode()
                self.manifest['images'][0][field] = old
        self.manifest['converter'] = 'different'
        self.pin_manifest()
        with self.assertRaisesRegex(staged.StagedRasterError, 'converter'):
            self.decode()

    def test_packaged_bundle_is_pinned_and_matches_small_original_decode(self):
        from ea444_decoder import decode_ea444
        source_root = Path(__file__).resolve().parents[1] / 'original_assets/source'
        tables = EA444Tables.from_section((source_root/'decoder/ea444_tqia_dat.bin').read_bytes())
        quant = EA444Quantization.from_source_bytes((source_root/'decoder/ea444_quant_source.bin').read_bytes())
        manifest, images = staged._load_bundle(staged.BUNDLE_ROOT, staged.MANIFEST_SHA256)
        entry = next(e for e in manifest['images'] if e['height'] < 100)
        raw = (source_root/entry['source_path']).read_bytes()
        self.assertEqual(sha256(raw).hexdigest(), entry['source_sha256'])
        self.assertEqual(staged.decode_staged_or_original(raw, tables=tables, quant=quant),
                         decode_ea444(raw, tables=tables, quant=quant))
        self.assertEqual(len(images), len({e['source_sha256'] for e in manifest['images']}))


if __name__ == '__main__':
    unittest.main()
