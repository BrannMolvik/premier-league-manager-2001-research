"""Original 4A6E50 PResults first five registered source children.

Native PE SHA256 833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
This is an immutable original-source geometry inventory, not a renderer,
interactive return control, match-progress event stream or Windows acceptance.
"""
from dataclasses import dataclass
from hashlib import sha256

ORIGINAL_WAITING_BACK_2_SIZE=46448
ORIGINAL_WAITING_BACK_2_SHA256='289b692919b3048bbe932eaf83083c622089fe4367d8124cd26a8bbf566899e5'
ORIGINAL_WAITING_BACK_2_SOURCE='FM2001_Art/Generic/waiting/waiting_back_2.444'
ORIGINAL_WAITING_BACK_2_RECT=(0,513,800,87)
ORIGINAL_LOADING_BACK_SOURCE='FM2001_Art/Generic/waiting/loading_back.444'
ORIGINAL_LOADING_BACK_SIZE=25944
ORIGINAL_LOADING_BACK_SHA256='397e6a91e041575a897605274c6cc6d0711d462ef15bedfe7d9d383f370e37d2'
ORIGINAL_LOADING_BACK_RECT=(0,579,800,14)
ORIGINAL_LOADING_FILL_SOURCE='FM2001_Art/Generic/waiting/loading_fill.444'
ORIGINAL_LOADING_FILL_SIZE=17204
ORIGINAL_LOADING_FILL_SHA256='9ba312d886fbb1898ad1f63b5e3c985972c22da09b7915b13d06a374e8c32070'
ORIGINAL_LOADING_FILL_INITIAL_RECT=(0,581,0,10)


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
    OriginalPResultsStaticChild(3,0x220,0,(0,579),(800,14),0x64F380),
    OriginalPResultsStaticChild(4,0x270,0,(0,581),(0,10),0x64F380),
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
    original_loading_back_validated: bool=False
    original_loading_fill_validated: bool=False
    original_return_input_proven: bool=False
    original_live_game_view_rendered: bool=False


def source_original_presults_initial_children(*, waiting_back_2_raw:bytes | None=None,
                                             loading_back_raw:bytes | None=None,
                                             loading_fill_raw:bytes | None=None):
    """Preserve bounded constructor facts, optionally verify private original art.

    Original 4A6E50 uses five-pointer child array and ID=0 for all
    five initial children. Progress +250 is referenced by child+270 and is
    not registered as a sixth child. Child 3 derives 800x14 from original 5F4420->64E500 which initializes
    +9465f0, not guessed globals. Child 4 initializes x0..0 / y581..591
    before source event ticks update right edge.
    """
    if waiting_back_2_raw is not None:
        if type(waiting_back_2_raw) is not bytes:
            raise OriginalPResultsSourceError('raw original Waiting/444 bytes required')
        if (len(waiting_back_2_raw)!=ORIGINAL_WAITING_BACK_2_SIZE or
            sha256(waiting_back_2_raw).hexdigest()!=ORIGINAL_WAITING_BACK_2_SHA256):
            raise OriginalPResultsSourceError('original waiting_back_2.444 identity mismatch')
    for raw,name,size,expected,wh in (
        (loading_back_raw,'loading_back.444',ORIGINAL_LOADING_BACK_SIZE,
         ORIGINAL_LOADING_BACK_SHA256,(800,14)),
        (loading_fill_raw,'loading_fill.444',ORIGINAL_LOADING_FILL_SIZE,
         ORIGINAL_LOADING_FILL_SHA256,(800,10)),
    ):
        if raw is not None:
            if (type(raw) is not bytes or len(raw)!=size or
                sha256(raw).hexdigest()!=expected or
                raw[:4]!=wh[0].to_bytes(2,'little')+wh[1].to_bytes(2,'little')):
                raise OriginalPResultsSourceError(name+' original bitmap identity/dimensions mismatch')
    return SourceOriginalPResultsInitialPanel(
        PRESULTS_REGISTERED_INITIAL_CHILDREN,
        original_bitmap_validated=waiting_back_2_raw is not None,
        original_loading_back_validated=loading_back_raw is not None,
        original_loading_fill_validated=loading_fill_raw is not None)


@dataclass(frozen=True)
class OriginalPResultsSourceProgressStep:
    original_callback_event_pointer: int
    original_callback_pass: int
    original_processed_count_after_tick: int
    original_total_count: int
    original_bar_rect_xywh: tuple[int,int,int,int]
    original_tick_va: int=0x4A71F0
    original_width_update_va: int=0x4A7190
    actual_original_event_executed: bool=False
    original_screen_rendered: bool=False


def source_original_presults_bar_rects_from_dated_callbacks(
    *, original_6168c0_receipt,
    original_source_total_4a7210: int,
    original_processed_before_callbacks: int,
) -> tuple[OriginalPResultsSourceProgressStep,...]:
    """Source-event-only PResults native 4A71F0 tick -> +270 bar width.

    Original 4A71F0 is called after qualified 6168C0 v+10 events, once per
    original_progress_callbacks entry. Native 4A7190 computes width as
    10*trunc(80*processed/total), with zero total -> width0; 64F600
    refreshes child+270 after setting owner+264 and +280. These derived
    rectangles are not a standalone progress-animation clock and cannot
    substitute a real original 4A7210 precount or dated event dispatch.
    """
    from original_presults_native_event_work import (
        OriginalPResultsDatedEventReceipt,
        OriginalPResultsSourceCallback,
        SOURCE_PRESULTS_TICK_VA,
    )
    if type(original_6168c0_receipt) is not OriginalPResultsDatedEventReceipt:
        raise OriginalPResultsSourceError('typed original native 6168C0 dated event receipt required')
    total=original_source_total_4a7210
    done=original_processed_before_callbacks
    if (type(total) is not int or type(done) is not int or
        not 0<=total<=0x7fffffff or not 0<=done<=total):
        raise OriginalPResultsSourceError('source total/processed signed native counters required')
    actions=original_6168c0_receipt.original_progress_callbacks
    if type(actions) is not tuple:
        raise OriginalPResultsSourceError('original callbacks must be ordered native tuple')
    if len(actions)>total-done:
        raise OriginalPResultsSourceError('source pre-count/actual tick overrun unqualified')
    steps=[]
    for callback in actions:
        if (type(callback) is not OriginalPResultsSourceCallback or
            type(callback.original_event_pointer) is not int or
            not 0<callback.original_event_pointer<=0xffffffff or
            type(callback.source_pass) is not int or callback.source_pass not in (1,2) or
            callback.native_event_virtual_method_offset!=0x10 or
            callback.native_progress_callback_va!=SOURCE_PRESULTS_TICK_VA):
            raise OriginalPResultsSourceError('original 6168C0 event v+10 / native tick provenance required')
        done+=1
        width=0 if total==0 else 10*((80*done)//total)
        steps.append(OriginalPResultsSourceProgressStep(
            callback.original_event_pointer,callback.source_pass,done,total,
            (0,581,width,10)))
    return tuple(steps)
