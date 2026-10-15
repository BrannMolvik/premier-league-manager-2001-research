"""Original 4A6E50 PResults first five registered source children.

Native PE SHA256 833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
This is an immutable original-source geometry inventory, not a renderer,
interactive return control, match-progress event stream or Windows acceptance.
"""
from dataclasses import dataclass
from hashlib import sha256

ORIGINAL_WAITING_BACK_2_SIZE=46448
ORIGINAL_WAITING_BACK_2_SHA256='289b692919b3048bbe932eaf83083c622089fe4367d8124cd26a8bbf566899e5'
ORIGINAL_WAITING_BACK_2_SOURCE='FM2001_Art/Generic/Waiting/waiting_back_2.444'
ORIGINAL_WAITING_BACK_2_RECT=(0,513,800,87)


@dataclass(frozen=True)
class OriginalPResultsStaticChild:
    original_child_array_index: int
    original_object_offset: int
    original_initial_control_id: int
    original_initial_xy: tuple[int,int]
    original_initial_wh: tuple[int,int] | None
    original_factory_call: int
    original_interactive_return_proven: bool=False


PRESULTS_REGISTERED_INITIAL_CHILDREN=(
    OriginalPResultsStaticChild(0,0x16c,0,(0,513),(800,87),0x651BA0),
    OriginalPResultsStaticChild(1,0x1a0,0,(0,518),(800,38),0x6503F0),
    OriginalPResultsStaticChild(2,0x1e0,0,(0,556),(800,18),0x6503F0),
    OriginalPResultsStaticChild(3,0x220,0,(0,579),None,0x64F380),
    OriginalPResultsStaticChild(4,0x270,0,(0,581),None,0x64F380),
)


class OriginalPResultsSourceError(ValueError):
    pass


@dataclass(frozen=True)
class SourceOriginalPResultsInitialPanel:
    registered_children: tuple[OriginalPResultsStaticChild, ...]
    original_panel_wh: tuple[int,int]=(800,600)
    original_child_array_count: int=5
    original_shared_progress_owner_offset: int=0x250
    original_first_child_bitmap_va: int=0x946630
    original_bitmap_validated: bool=False
    original_return_input_proven: bool=False
    original_live_game_view_rendered: bool=False


def source_original_presults_initial_children(*, waiting_back_2_raw:bytes | None=None):
    """Preserve bounded constructor facts, optionally verify private original art.

    Original 4A6E50 uses five-pointer child array and ID=0 for all
    five initial children. Progress +250 is referenced by child+270 and is
    not registered as a sixth child. Unknown dynamic extents of
    children 3/4 remain None; do not infer from missing source bytes.
    """
    if waiting_back_2_raw is not None:
        if type(waiting_back_2_raw) is not bytes:
            raise OriginalPResultsSourceError('raw original Waiting/444 bytes required')
        if (len(waiting_back_2_raw)!=ORIGINAL_WAITING_BACK_2_SIZE or
            sha256(waiting_back_2_raw).hexdigest()!=ORIGINAL_WAITING_BACK_2_SHA256):
            raise OriginalPResultsSourceError('original waiting_back_2.444 identity mismatch')
    return SourceOriginalPResultsInitialPanel(
        PRESULTS_REGISTERED_INITIAL_CHILDREN,
        original_bitmap_validated=waiting_back_2_raw is not None)
