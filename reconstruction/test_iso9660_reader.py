from pathlib import Path
import tempfile
import unittest

from iso9660_reader import Iso9660Error, IsoImage, SECTOR


def _both16(value):
    return value.to_bytes(2, "little") + value.to_bytes(2, "big")


def _both32(value):
    return value.to_bytes(4, "little") + value.to_bytes(4, "big")


def _record(extent, size, flags, name):
    length = 33 + len(name) + (1 if len(name) % 2 == 0 else 0)
    data = bytearray(length)
    data[0] = length
    data[2:10] = _both32(extent)
    data[10:18] = _both32(size)
    data[18:25] = b"\x7e\x09\x1e\x00\x00\x00\x00"
    data[25] = flags
    data[28:32] = _both16(1)
    data[32] = len(name)
    data[33:33 + len(name)] = name
    return bytes(data)


def _directory(records):
    body = b"".join(records)
    return body + b"\x00" * (SECTOR - len(body))


def _descriptor(kind, root, joliet=False):
    data = bytearray(SECTOR)
    data[0] = kind
    data[1:6] = b"CD001"
    data[6] = 1
    rec = _record(root, SECTOR, 2, b"\x00")
    data[156:156 + len(rec)] = rec
    if joliet:
        data[88:91] = b"%/E"
    return bytes(data)


def build_joliet_iso(path):
    root, art, generic, file_lba = 20, 21, 22, 23
    payload = b"\x20\x03\x58\x02gate13-joliet"
    sectors = [bytearray(SECTOR) for _ in range(24)]
    sectors[16][:] = _descriptor(1, root)
    sectors[17][:] = _descriptor(2, root, True)
    sectors[18][0] = 255
    sectors[18][1:6] = b"CD001"
    sectors[18][6] = 1

    dot = lambda e: _record(e, SECTOR, 2, b"\x00")
    up = lambda e: _record(e, SECTOR, 2, b"\x01")
    j = lambda s: s.encode("utf-16-be")

    sectors[root][:] = _directory([
        dot(root), up(root),
        _record(art, SECTOR, 2, j("FM2001_Art")),
    ])
    sectors[art][:] = _directory([
        dot(art), up(root),
        _record(generic, SECTOR, 2, j("Generic")),
    ])
    sectors[generic][:] = _directory([
        dot(generic), up(art),
        _record(file_lba, len(payload), 0, j("bground.444;1")),
    ])
    sectors[file_lba][:len(payload)] = payload
    path.write_bytes(b"".join(bytes(s) for s in sectors))
    return payload


class Iso9660ReaderTests(unittest.TestCase):
    def test_reads_and_extracts_joliet_long_path(self):
        with tempfile.TemporaryDirectory() as temp_name:
            root = Path(temp_name)
            path = root / "fixture.iso"
            payload = build_joliet_iso(path)

            image = IsoImage(path)
            files = image.files()

            self.assertTrue(image.uses_joliet)
            self.assertEqual(image.joliet_level, 3)
            self.assertEqual(
                [entry.path for entry in files],
                ["FM2001_Art/Generic/bground.444"],
            )
            self.assertEqual(image.read_file(files[0]), payload)

            extracted = image.extract_file(files[0], root / "out")
            self.assertEqual(extracted.read_bytes(), payload)

    def test_rejects_non_iso_image(self):
        with tempfile.TemporaryDirectory() as temp_name:
            path = Path(temp_name) / "bad.iso"
            path.write_bytes(b"\x00" * (17 * SECTOR))
            with self.assertRaises(Iso9660Error):
                IsoImage(path)


if __name__ == "__main__":
    unittest.main()
