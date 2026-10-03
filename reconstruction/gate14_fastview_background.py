"""Fail-closed source boundary for the loose FastView background path.

The canonical executable constructs the exact
FM2001_Art/FastView/background.444 path into one static string object. Direct
disassembly finds only that construction and its destruction; FastViewPanel's
800x600 constructor does not receive the path, and no runtime consumer of the
static string/data pointer is present in the executable.

Therefore the file is an authenticated FastView-named source asset but is not
source-bound to the live FastViewPanel draw path. It must not be rendered as
the panel background until a separate direct ownership path is recovered.
"""
from __future__ import annotations


BACKGROUND_SOURCE_PATH = "FM2001_Art/FastView/background.444"
BACKGROUND_PATH_LITERAL_VA = 0x8294E8
BACKGROUND_BYTE_SIZE = 205984
BACKGROUND_DIMENSIONS = (800, 600)
BACKGROUND_SHA256 = (
    "499e930fe0a328d969096b8d2cdb8c817169f02812adcc78acf111dc666d95c0"
)

SOURCE_STATIC_STRING_INIT_VA = 0x51F2F0
SOURCE_STATIC_STRING_OBJECT_VA = 0x877758
SOURCE_STRING_CONSTRUCTOR_VA = 0x684620
SOURCE_STRING_DESTRUCTOR_VA = 0x68467F

SOURCE_FASTVIEW_PANEL_CONSTRUCTOR_VA = 0x51F490
SOURCE_GENERIC_PANEL_CONSTRUCTOR_VA = 0x527350
SOURCE_FASTVIEW_PANEL_DIMENSIONS = (800, 600)

SOURCE_STATIC_STRING_RUNTIME_REFERENCE_COUNT = 2
DIRECT_FASTVIEW_PANEL_DRAW_OWNERSHIP = False
BACKGROUND_BINDING_STATUS = "unbound_static_path_string_fail_closed"


def background_is_source_bound_to_fastview_panel() -> bool:
    """Never promote filename/dimensions alone to a live draw binding."""
    return DIRECT_FASTVIEW_PANEL_DRAW_OWNERSHIP
