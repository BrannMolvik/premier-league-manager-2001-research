from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath


SECTOR = 2048
JOLIET = {b"%/@": 1, b"%/C": 2, b"%/E": 3}


class Iso9660Error(ValueError):
    pass


@dataclass(frozen=True)
class IsoEntry:
    path: str
    extent: int
    size: int
    flags: int

    @property
    def is_dir(self) -> bool:
        return bool(self.flags & 2)


def _record(data: bytes) -> tuple[int, int, int, bytes]:
    if len(data) < 34 or not data[0] or data[0] > len(data):
        raise Iso9660Error("invalid directory record")
    extent = int.from_bytes(data[2:6], "little")
    size = int.from_bytes(data[10:14], "little")
    if extent != int.from_bytes(data[6:10], "big"):
        raise Iso9660Error("extent endian copies disagree")
    if size != int.from_bytes(data[14:18], "big"):
        raise Iso9660Error("size endian copies disagree")
    n = data[32]
    if 33 + n > data[0]:
        raise Iso9660Error("identifier exceeds directory record")
    return extent, size, data[25], bytes(data[33:33 + n])


class IsoImage:
    """Minimal read-only ISO9660/Joliet reader for FM2001 source assets."""

    def __init__(self, path: Path):
        self.path = Path(path).resolve()
        if not self.path.is_file():
            raise FileNotFoundError(self.path)
        self.root_extent, self.root_size, self.joliet_level = self._volume()

    @property
    def uses_joliet(self) -> bool:
        return self.joliet_level > 0

    def _read(self, offset: int, size: int) -> bytes:
        with self.path.open("rb") as f:
            f.seek(offset)
            data = f.read(size)
        if len(data) != size:
            raise Iso9660Error("short ISO read")
        return data

    def _extent(self, lba: int, size: int) -> bytes:
        return self._read(lba * SECTOR, size)

    def _volume(self) -> tuple[int, int, int]:
        primary = None
        joliet = []
        for lba in range(16, 256):
            d = self._extent(lba, SECTOR)
            if d[1:6] != b"CD001" or d[6] != 1:
                raise Iso9660Error("invalid volume descriptor")
            if d[0] == 255:
                break
            if d[0] not in (1, 2):
                continue
            length = d[156]
            extent, size, flags, name = _record(d[156:156 + length])
            if not flags & 2 or name != b"\x00":
                raise Iso9660Error("invalid root directory record")
            if d[0] == 1:
                primary = (extent, size, 0)
            elif bytes(d[88:91]) in JOLIET:
                joliet.append((extent, size, JOLIET[bytes(d[88:91])]))
        else:
            raise Iso9660Error("volume descriptor terminator not found")

        if joliet:
            return max(joliet, key=lambda item: item[2])
        if primary is not None:
            return primary
        raise Iso9660Error("no ISO9660/Joliet volume found")

    def _name(self, raw: bytes) -> str | None:
        if raw in (b"\x00", b"\x01"):
            return None
        if self.uses_joliet:
            if len(raw) % 2:
                raise Iso9660Error("odd-length Joliet identifier")
            name = raw.decode("utf-16-be")
        else:
            name = raw.decode("ascii")
        if ";" in name:
            stem, version = name.rsplit(";", 1)
            if version.isdigit():
                name = stem
        return name

    def _directory(self, extent: int, size: int):
        data = self._extent(extent, size)
        pos = 0
        while pos < len(data):
            length = data[pos]
            if not length:
                pos = ((pos // SECTOR) + 1) * SECTOR
                continue
            end = pos + length
            if end > len(data):
                raise Iso9660Error("directory record exceeds directory size")
            yield _record(data[pos:end])
            pos = end

    def entries(self) -> tuple[IsoEntry, ...]:
        found = []
        visited = set()

        def walk(extent: int, size: int, prefix: PurePosixPath):
            key = (extent, size)
            if key in visited:
                return
            visited.add(key)
            for child_extent, child_size, flags, raw in self._directory(extent, size):
                name = self._name(raw)
                if name is None:
                    continue
                entry = IsoEntry(
                    path=(prefix / name).as_posix(),
                    extent=child_extent,
                    size=child_size,
                    flags=flags,
                )
                if flags & 0x80:
                    raise Iso9660Error(f"multi-extent entry unsupported: {entry.path}")
                found.append(entry)
                if entry.is_dir:
                    walk(child_extent, child_size, prefix / name)

        walk(self.root_extent, self.root_size, PurePosixPath())
        return tuple(found)

    def files(self) -> tuple[IsoEntry, ...]:
        return tuple(entry for entry in self.entries() if not entry.is_dir)

    def read_file(self, entry: IsoEntry) -> bytes:
        if entry.is_dir:
            raise IsADirectoryError(entry.path)
        return self._extent(entry.extent, entry.size)

    def extract_file(self, entry: IsoEntry, root: Path) -> Path:
        output = Path(root).joinpath(*PurePosixPath(entry.path).parts)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(self.read_file(entry))
        return output


class RawMode1IsoImage(IsoImage):
    """Expose a raw 2352-byte MODE1 track as a read-only virtual ISO image.

    The directory reader sees only the original 2048-byte user-data portion of
    each physical sector. This avoids writing a second hundreds-of-MB ISO
    copy when the authorized source ZIP is recovered. Callers performing a
    provenance audit must still validate every raw sector once before using it.
    """

    RAW_SECTOR = 2352
    DATA_OFFSET = 16
    RAW_SYNC = b"\x00" + (b"\xff" * 10) + b"\x00"

    def _read(self, offset: int, size: int) -> bytes:
        if offset < 0 or size < 0:
            raise Iso9660Error("negative virtual ISO read")
        if size == 0:
            return b""
        first = offset // SECTOR
        last = (offset + size - 1) // SECTOR
        chunks = []
        with self.path.open("rb") as source:
            source.seek(first * self.RAW_SECTOR)
            for sector_index in range(first, last + 1):
                raw = source.read(self.RAW_SECTOR)
                if len(raw) != self.RAW_SECTOR:
                    raise Iso9660Error(
                        f"short raw MODE1/2352 read at sector {sector_index}"
                    )
                if raw[:12] != self.RAW_SYNC or raw[15] != 1:
                    raise Iso9660Error(
                        f"invalid raw MODE1/2352 header at sector {sector_index}"
                    )
                chunks.append(raw[self.DATA_OFFSET:self.DATA_OFFSET + SECTOR])
        within_first = offset % SECTOR
        return b"".join(chunks)[within_first:within_first + size]

