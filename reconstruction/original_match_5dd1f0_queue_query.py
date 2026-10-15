"""Original 5DC510-style intrusive record queue read by native 5DD1F0.

Source-equivalent lane: 5DC510 creates record, 617D70 appends wrapper,
5DC890 calls 5DD1F0, which filters record+10 type, nonnegative
record first QWORD, and signed lexicographic [lower,upper] tuple range
with 64D060/64D020. This read-only selection does NOT execute x87,
native queue callbacks, a final score or GameState mutation.
"""
from dataclasses import dataclass
from math import isfinite
from struct import unpack_from


class Original5DD1F0QueueSourceError(ValueError):
    pass


@dataclass(frozen=True)
class Original5DD1F0LinkedPayload:
    original_wrapper_pointer: int
    original_wrapper_bytes: bytes
    original_payload_pointer: int
    original_payload_bytes: bytes


@dataclass(frozen=True)
class SourceOriginal5DD1F0QueryReceipt:
    original_requested_word_low16: int
    original_inspected_wrapper_pointers: tuple[int, ...]
    original_source_selected_wrapper_pointers: tuple[int, ...]
    original_selected_finite_contributions: tuple[float, ...]
    original_same_owner_instance_proven: bool = False
    native_x87_sum_executed: bool = False
    actual_native_queue_consumed: bool = False
    live_game_state_updated: bool = False


def _u32(v, label):
    if type(v) is not int or not 0 <= v <= 0xffffffff:
        raise Original5DD1F0QueueSourceError(label + ' must be reached native uint32')
    return v


def _signed_lex(query, label):
    if type(query) is not tuple or len(query)!=3:
        raise Original5DD1F0QueueSourceError(label+' original 3-DWORD tuple required')
    values=tuple(_u32(v,label) for v in query)
    return tuple(v-0x100000000 if v & 0x80000000 else v for v in values)


def source_original_5dd1f0_queue_readback(
    *,
    original_queue_owner_bytes: bytes,
    original_linked_payload_nodes: tuple[Original5DD1F0LinkedPayload, ...],
    original_query_type_dword: int,
    original_signed_lower_triple: tuple[int,int,int],
    original_signed_upper_triple: tuple[int,int,int],
) -> SourceOriginal5DD1F0QueryReceipt:
    if type(original_queue_owner_bytes) is not bytes or len(original_queue_owner_bytes)<12:
        raise Original5DD1F0QueueSourceError('original queue owner through +8 required')
    if type(original_linked_payload_nodes) is not tuple:
        raise Original5DD1F0QueueSourceError('ordered linked wrapper source required')
    qword=_u32(original_query_type_dword,'query type') & 0xffff
    lower=_signed_lex(original_signed_lower_triple,'lower filter')
    upper=_signed_lex(original_signed_upper_triple,'upper filter')
    if lower>upper:
        raise Original5DD1F0QueueSourceError('original reversed native query bounds unsupported')
    first,tail=unpack_from('<II',original_queue_owner_bytes,4)
    if len(original_linked_payload_nodes)>10000:
        raise Original5DD1F0QueueSourceError('unbounded original queue')
    if not original_linked_payload_nodes:
        if first or tail:
            raise Original5DD1F0QueueSourceError('nonempty original queue was omitted')
        return SourceOriginal5DD1F0QueryReceipt(qword,(),(),())
    if not first or not tail:
        raise Original5DD1F0QueueSourceError('source queue missing first/tail')
    prior=0
    seen_wrappers=set()
    seen_payloads=set()
    inspected=[]
    selected=[]
    contributions=[]
    for node in original_linked_payload_nodes:
        if type(node) is not Original5DD1F0LinkedPayload:
            raise Original5DD1F0QueueSourceError('typed original queue node required')
        ptr=_u32(node.original_wrapper_pointer,'wrapper')
        data_ptr=_u32(node.original_payload_pointer,'payload')
        if not ptr or not data_ptr or ptr==data_ptr or ptr in seen_wrappers or data_ptr in seen_payloads:
            raise Original5DD1F0QueueSourceError('native record pointer/cycle/reused payload')
        raw=node.original_wrapper_bytes
        data=node.original_payload_bytes
        if type(raw) is not bytes or len(raw)!=12 or type(data) is not bytes or len(data)!=0x20:
            raise Original5DD1F0QueueSourceError('exact native 0x0c wrapper and 0x20 payload required')
        owned,next_ptr,prev_ptr=unpack_from('<III',raw)
        if owned!=data_ptr or prev_ptr!=prior or ptr!=(first if not inspected else next_expected):
            raise Original5DD1F0QueueSourceError('original intrusive queue ownership and order mismatch')
        seen_wrappers.add(ptr)
        seen_payloads.add(data_ptr)
        prior=ptr
        next_expected=next_ptr
        inspected.append(ptr)
        # Native first compares only payload+10 WORD. Nonmatching payload
        # never executes 5E48D0 or tuple predicate callbacks.
        if unpack_from('<H',data,0x10)[0] != qword:
            continue
        value=unpack_from('<d',data)[0]
        if not isfinite(value):
            raise Original5DD1F0QueueSourceError('original x87 unordered/overflow source unresolved')
        if value<0:
            continue
        actual=unpack_from('<iii',data,0x14)
        if lower <= actual <= upper:
            selected.append(ptr)
            contributions.append(value)
    if prior!=tail or next_expected!=0:
        raise Original5DD1F0QueueSourceError('incomplete original first/tail linked chain')
    return SourceOriginal5DD1F0QueryReceipt(qword,tuple(inspected),tuple(selected),tuple(contributions))
