"""Decode verified original PSupportStart art into source-aligned raster strips.

This is the native source graphics layer for the original 760x500
PSupportStart client. It does not invent GUI mouse hit regions, parent
screen transform, frame state transitions, staff names or Apply behavior.

Original files are byte-identical and SHA checked by
original_supportstart_art. Native EA444 decoding reuses the verified
original executable's Huffman/quantization tables.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ea444_decoder import EA444DecodedImage
from ea444_quantization import quantization_from_verified_executable
from ea444_tables import tables_from_original_executable
from gate13_ea444_staged_rasters import decode_staged_or_original
from original_supportstart_art import (
    ORIGINAL_SUPPORTSTART_ART_SPECS,
    OriginalSupportStartArtError,
    verified_original_supportstart_art,
)


@dataclass(frozen=True)
class OriginalSupportStartSourceRasters:
    background: EA444DecodedImage
    row_bar_frames: tuple[EA444DecodedImage, ...]
    row_animation_frames: tuple[EA444DecodedImage, ...]
    exit_button_frames: tuple[EA444DecodedImage, ...]
    apply_button_frames: tuple[EA444DecodedImage, ...]
    star_rating_crops: tuple[EA444DecodedImage, ...]


def source_rgba_crop(
    decoded: EA444DecodedImage,
    *,
    x: int,
    y: int,
    width: int,
    height: int,
) -> EA444DecodedImage:
    """Exact RGBA crop, preserving source alpha and original decoded pixels."""
    if type(decoded) is not EA444DecodedImage:
        raise TypeError("Native original decoded EA444 image required")
    if any(type(v) is not int for v in (x,y,width,height)):
        raise OriginalSupportStartArtError("Source crop must have integer bounds")
    if (min(x,y) < 0 or min(width,height) <= 0
            or x+width > decoded.width or y+height > decoded.height):
        raise OriginalSupportStartArtError("Crop outside original source EA444 atlas")
    data=b"".join(
        decoded.rgba[((row*decoded.width+x)*4):
                     ((row*decoded.width+x+width)*4)]
        for row in range(y,y+height)
    )
    # Cropped images are source slices, not new, fabricated artwork.
    return EA444DecodedImage(
        width, height, data, decoded.consumed_bits,
        sum(data[i+3] == 0 for i in range(0,len(data),4))
    )


def _vertical_frames(
    image: EA444DecodedImage, *, width: int, frame_height: int, count: int
) -> tuple[EA444DecodedImage, ...]:
    if image.width != width or image.height != frame_height*count:
        raise OriginalSupportStartArtError("Source native atlas frame geometry mismatch")
    return tuple(source_rgba_crop(
        image,x=0,y=i*frame_height,width=width,height=frame_height
    ) for i in range(count))


def assemble_source_supportstart_rasters(
    images: dict[str, EA444DecodedImage],
) -> OriginalSupportStartSourceRasters:
    """Split only provable original source 444 dimensions, not state behavior."""
    expected = {s.relative_source: (s.width,s.height)
                for s in ORIGINAL_SUPPORTSTART_ART_SPECS}
    if type(images) is not dict or set(images) != set(expected):
        raise OriginalSupportStartArtError("Six source-verified original atlases required")
    for path,(w,h) in expected.items():
        item=images[path]
        if type(item) is not EA444DecodedImage or (item.width,item.height)!=(w,h):
            raise OriginalSupportStartArtError(
                f"Native source bitmap geometry mismatch: {path}"
            )
    prefix="FM2001_Art/"
    def img(relative):
        return images[prefix+relative]
    bg=img("Generic/user_entry/background.444")
    bars=img("Generic/user_entry/text_bars.444")
    anim=img("Generic/GenericButtonsAndBars/user_entry_anim.444")
    ex=img("Generic/GenericButtonsAndBars/exit_button.444")
    tick=img("Generic/GenericButtonsAndBars/tick_button.444")
    stars=img("Support/stars.444")
    return OriginalSupportStartSourceRasters(
        background=bg,
        row_bar_frames=_vertical_frames(bars,width=306,frame_height=17,count=4),
        row_animation_frames=_vertical_frames(anim,width=17,frame_height=37,count=23),
        exit_button_frames=_vertical_frames(ex,width=30,frame_height=30,count=3),
        apply_button_frames=_vertical_frames(tick,width=30,frame_height=30,count=3),
        star_rating_crops=tuple(source_rgba_crop(
            stars,x=0,y=0,width=15*(i+1),height=10
        ) for i in range(5))
    )


def load_source_supportstart_rasters(
    *, repo_root: Path, original_executable: Path
) -> OriginalSupportStartSourceRasters:
    """Decode original byte-verified assets using original executable tables.

    An original executable is REQUIRED; never infer its codec tables.
    Loading the executable as bytes is not executing the original game.
    """
    data=verified_original_supportstart_art(repo_root)
    try:
        executable=Path(original_executable).read_bytes()
    except OSError as exc:
        raise OriginalSupportStartArtError(
            "Original executable unavailable for source EA444 decoder"
        ) from exc
    tables=tables_from_original_executable(executable)
    quant=quantization_from_verified_executable(executable)
    images={path:decode_staged_or_original(payload,tables=tables,quant=quant)
            for path,payload in data.items()}
    return assemble_source_supportstart_rasters(images)
