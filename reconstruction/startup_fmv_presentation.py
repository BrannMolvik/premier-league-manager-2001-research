"""Source-proven FM2001 startup-FMV display treatment.

The canonical executable does not aspect-fit the coded 320x480 TGQ image.
Startup wrapper 0x461E20 passes flag 0x40 to 0x461900. The TQI decoder keeps
the coded height at 480 but doubles its logical width to 640, then selects a
special 16-bpp writer whose color lookup values contain the same packed
16-bit pixel in both halves of each 32-bit write. This is exact horizontal
pixel duplication (nearest-neighbor 2x), not interpolation.

The decoder writes a 640x480 movie surface. 0x461CD0 performs a 1:1 DirectDraw
Blt of that whole surface into the game display: (0,0) in 640x480 mode or
(80,60) in the ordinary 800x600 mode. There is no final-blit scaling.
"""
from __future__ import annotations

from dataclasses import dataclass


CODED_SIZE = (320, 480)
MOVIE_SURFACE_SIZE = (640, 480)
ORDINARY_GAME_DISPLAY_SIZE = (800, 600)
ORDINARY_MOVIE_OFFSET = (80, 60)
HORIZONTAL_REPEAT = 2
STARTUP_DOUBLE_WIDTH_FLAG = 0x40
GAME_DISPLAY_BPP = 16


class StartupFmvPresentationError(ValueError):
    pass


@dataclass(frozen=True)
class StartupFmvPresentation:
    coded_width: int = CODED_SIZE[0]
    coded_height: int = CODED_SIZE[1]
    movie_width: int = MOVIE_SURFACE_SIZE[0]
    movie_height: int = MOVIE_SURFACE_SIZE[1]
    horizontal_repeat: int = HORIZONTAL_REPEAT
    game_display_width: int = ORDINARY_GAME_DISPLAY_SIZE[0]
    game_display_height: int = ORDINARY_GAME_DISPLAY_SIZE[1]
    movie_x: int = ORDINARY_MOVIE_OFFSET[0]
    movie_y: int = ORDINARY_MOVIE_OFFSET[1]
    display_bpp: int = GAME_DISPLAY_BPP

    def __post_init__(self) -> None:
        if (
            self.coded_width <= 0
            or self.coded_height <= 0
            or self.horizontal_repeat != 2
            or self.movie_width != self.coded_width * self.horizontal_repeat
            or self.movie_height != self.coded_height
        ):
            raise StartupFmvPresentationError(
                "FM2001 startup movie geometry differs from recovered native treatment"
            )
        if self.display_bpp != 16:
            raise StartupFmvPresentationError(
                "FM2001 startup movie presentation requires the recovered 16-bpp path"
            )
        if (
            self.movie_x * 2 + self.movie_width != self.game_display_width
            or self.movie_y * 2 + self.movie_height != self.game_display_height
        ):
            raise StartupFmvPresentationError(
                "FM2001 startup movie rectangle is not centered in the game display"
            )

    @property
    def ffmpeg_filter(self) -> str:
        """Bake the native 2x horizontal pixel duplication into a modern derivative."""
        return (
            f"scale={self.movie_width}:{self.movie_height}:"
            "flags=neighbor"
        )

    @property
    def source_rect(self) -> tuple[int, int, int, int]:
        return (0, 0, self.movie_width, self.movie_height)

    @property
    def ordinary_destination_rect(self) -> tuple[int, int, int, int]:
        return (
            self.movie_x,
            self.movie_y,
            self.movie_x + self.movie_width,
            self.movie_y + self.movie_height,
        )


ORIGINAL_STARTUP_FMV_PRESENTATION = StartupFmvPresentation()
