"""Source-backed original PScouting2K graphics and proven composition geometry.

Canonical executable PScouting2K setup method 0x4AB150 proves two exact .444
resources. background_alpha_1.444 is a 571x16 strip drawn at x=207 for 20 rows
starting y=192 with a 17-pixel step. background_2.444 is 295x45 at (206,543).

This module deliberately builds only that proven transparent composition layer.
It does not invent the unknown surrounding Scouting background, captions,
controls, result text, navigation, or row semantics.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from ea444_decoder import EA444DecodedImage, decode_ea444
from ea444_quantization import quantization_from_verified_executable
from ea444_tables import tables_from_original_executable
from original_front_end_layout import SCREEN_SIZE


SCOUTING_REPEATED_SOURCE_PATH = (
    "FM2001_Art/business/scouting/background_alpha_1.444"
)
SCOUTING_BOTTOM_SOURCE_PATH = "FM2001_Art/business/scouting/background_2.444"
SCOUTING_REPEATED_SHA256 = (
    "e69a94edd9814860e796ab1bb4e58a3381584efda8bad704b8c65eebbb58d899"
)
SCOUTING_BOTTOM_SHA256 = (
    "3bc5e1a8ba9c91a75905786f969aad83bca61891ebd7e4aca40a78165a95e503"
)
SCOUTING_REPEATED_SIZE = (571, 16)
SCOUTING_BOTTOM_SIZE = (295, 45)
SCOUTING_REPEATED_ORIGINS = tuple((207, 192 + 17 * row) for row in range(20))
SCOUTING_BOTTOM_ORIGIN = (206, 543)


class OriginalScoutingResourceError(ValueError):
    pass


@dataclass(frozen=True)
class OriginalScoutingComposition:
    repeated_strip: EA444DecodedImage
    bottom_panel: EA444DecodedImage

    def __post_init__(self) -> None:
        if (self.repeated_strip.width, self.repeated_strip.height) != (
            SCOUTING_REPEATED_SIZE
        ):
            raise OriginalScoutingResourceError(
                "Original Scouting repeated strip geometry differs from 0x4AB150"
            )
        if (self.bottom_panel.width, self.bottom_panel.height) != SCOUTING_BOTTOM_SIZE:
            raise OriginalScoutingResourceError(
                "Original Scouting bottom-panel geometry differs from 0x4AB150"
            )
        width, height = SCREEN_SIZE
        for x, y in (*SCOUTING_REPEATED_ORIGINS, SCOUTING_BOTTOM_ORIGIN):
            if not (0 <= x < width and 0 <= y < height):
                raise OriginalScoutingResourceError(
                    "Recovered Scouting placement lies outside the 800x600 surface"
                )
        last_x, last_y = SCOUTING_REPEATED_ORIGINS[-1]
        if (
            last_x + self.repeated_strip.width > width
            or last_y + self.repeated_strip.height > height
        ):
            raise OriginalScoutingResourceError(
                "Recovered Scouting repeated strip exceeds the original surface"
            )
        x, y = SCOUTING_BOTTOM_ORIGIN
        if x + self.bottom_panel.width > width or y + self.bottom_panel.height > height:
            raise OriginalScoutingResourceError(
                "Recovered Scouting bottom panel exceeds the original surface"
            )

    @property
    def placements(self) -> tuple[tuple[str, int, int], ...]:
        return tuple(
            ("background_alpha_1.444", x, y)
            for x, y in SCOUTING_REPEATED_ORIGINS
        ) + (("background_2.444", *SCOUTING_BOTTOM_ORIGIN),)

    def transparent_overlay_rgba(self) -> bytes:
        """Compose only proven color-key pixels onto a transparent 800x600 layer."""
        width, height = SCREEN_SIZE
        output = bytearray(width * height * 4)

        def blit(image: EA444DecodedImage, x0: int, y0: int) -> None:
            for y in range(image.height):
                for x in range(image.width):
                    src = (y * image.width + x) * 4
                    alpha = image.rgba[src + 3]
                    if alpha not in (0, 255):
                        raise OriginalScoutingResourceError(
                            "EA444 source unexpectedly contains partial alpha"
                        )
                    if alpha == 0:
                        continue
                    dst = ((y0 + y) * width + x0 + x) * 4
                    output[dst:dst + 4] = image.rgba[src:src + 4]

        for x, y in SCOUTING_REPEATED_ORIGINS:
            blit(self.repeated_strip, x, y)
        blit(self.bottom_panel, *SCOUTING_BOTTOM_ORIGIN)
        return bytes(output)


def assemble_original_scouting_composition(
    repeated_strip: EA444DecodedImage,
    bottom_panel: EA444DecodedImage,
) -> OriginalScoutingComposition:
    return OriginalScoutingComposition(repeated_strip, bottom_panel)


def _read_verified_art(
    original_art_dir: Path, source_path: str, expected_sha256: str
) -> bytes:
    path = Path(original_art_dir) / source_path.removeprefix("FM2001_Art/")
    data = path.read_bytes()
    if sha256(data).hexdigest() != expected_sha256:
        raise OriginalScoutingResourceError(
            f"Original Scouting resource checksum mismatch: {source_path}"
        )
    return data


def load_verified_original_scouting_composition(
    *, original_art_dir: Path, original_executable: Path
) -> OriginalScoutingComposition:
    executable = Path(original_executable).read_bytes()
    tables = tables_from_original_executable(executable)
    quant = quantization_from_verified_executable(executable)
    repeated = decode_ea444(
        _read_verified_art(
            original_art_dir,
            SCOUTING_REPEATED_SOURCE_PATH,
            SCOUTING_REPEATED_SHA256,
        ),
        tables=tables,
        quant=quant,
    )
    bottom = decode_ea444(
        _read_verified_art(
            original_art_dir,
            SCOUTING_BOTTOM_SOURCE_PATH,
            SCOUTING_BOTTOM_SHA256,
        ),
        tables=tables,
        quant=quant,
    )
    return assemble_original_scouting_composition(repeated, bottom)
