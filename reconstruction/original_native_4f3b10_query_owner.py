"""Source-only 4056F0 -> 4F3B10 native query-owner linked lookup.

Original authenticated PE SHA256 833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
4056D0 stages low16 club+10 and zero higher WORD; 4056F0 calls
4F3B10. 4F3B10 resolves a native bucket at global 876C44 or the
0xffff sentinel 876BC8 then walks node+10 until node+22 WORD matches
query's +2 WORD. No native code, memory lookup or callback executed.
"""
from dataclasses import dataclass
from struct import unpack_from
from original_native_40cbc0_coeff_route import SourceOriginal40CBC0QueryWordReceipt


class Original4F3B10QuerySourceError(ValueError):
    pass


@dataclass(frozen=True)
class SourceOriginal4F3B10NativeNode:
    original_native_pointer: int
    original_native_record: bytes


@dataclass(frozen=True)
class SourceOriginal4F3B10LookupReceipt:
    original_query_word: int
    original_query_subkey_word: int
    original_bucket_pointer: int
    original_walked_pointer_order: tuple[int,...]
    original_found_object_pointer_or_zero: int
    original_4f3b10_executed: bool = False
    original_4fa520_executed: bool = False
    live_game_state_updated: bool = False


def _ptr(value, label, allow_zero=False):
    if type(value) is not int or not 0<=value<=0xffffffff or (not allow_zero and value==0):
        raise Original4F3B10QuerySourceError(label+" actual native pointer required")
    return value


def source_original_4f3b10_reached_query_owner(
    *,
    original_4056d0_query_receipt: SourceOriginal40CBC0QueryWordReceipt,
    original_global_876c44_bucket_array_pointer_if_indexed: int | None,
    original_reached_876c44_index_slot_pointer_if_indexed: int | None,
    original_reached_index_bucket_pointer_record_if_indexed: bytes | None,
    original_global_876bc8_sentinel_head_pointer_if_sentinel: int | None,
    original_native_list_nodes_in_order: tuple[SourceOriginal4F3B10NativeNode,...],
) -> SourceOriginal4F3B10LookupReceipt:
    query=original_4056d0_query_receipt
    if type(query) is not SourceOriginal40CBC0QueryWordReceipt:
        raise Original4F3B10QuerySourceError("verified original 4056D0 query receipt required")
    raw=query.original_4056d0_query_four_bytes
    if type(raw) is not bytes or len(raw)!=4:
        raise Original4F3B10QuerySourceError("native 4056D0 four query bytes required")
    key,subkey=unpack_from("<HH",raw,0)
    if key==0xffff:
        if (original_global_876c44_bucket_array_pointer_if_indexed is not None or
            original_reached_876c44_index_slot_pointer_if_indexed is not None or
            original_reached_index_bucket_pointer_record_if_indexed is not None):
            raise Original4F3B10QuerySourceError("sentinel 876BC8 lookup does not read 876C44")
        head=_ptr(original_global_876bc8_sentinel_head_pointer_if_sentinel,"876BC8 sentinel",True)
    else:
        if original_global_876bc8_sentinel_head_pointer_if_sentinel is not None:
            raise Original4F3B10QuerySourceError("non-sentinel 876C44 lookup cannot use 876BC8")
        base=_ptr(original_global_876c44_bucket_array_pointer_if_indexed,"876C44 base")
        slotptr=_ptr(original_reached_876c44_index_slot_pointer_if_indexed,"native bucket index slot")
        signed=key-0x10000 if key&0x8000 else key
        calculated=(base+((signed*4)&0xffffffff))&0xffffffff
        if not calculated or slotptr!=calculated:
            raise Original4F3B10QuerySourceError("4F3B27 signed bucket slot pointer mismatch")
        bucket=original_reached_index_bucket_pointer_record_if_indexed
        if type(bucket) is not bytes or len(bucket)!=4:
            raise Original4F3B10QuerySourceError("actual reached bucket head DWORD required")
        head=unpack_from("<I",bucket,0)[0]
    links=original_native_list_nodes_in_order
    if type(links) is not tuple or len(links)>65536:
        raise Original4F3B10QuerySourceError("bounded native 4F3B10 list path required")
    ptr=head
    seen=set()
    visited=[]
    match=0
    for item in links:
        if type(item) is not SourceOriginal4F3B10NativeNode:
            raise Original4F3B10QuerySourceError("native linked object input type required")
        node=_ptr(item.original_native_pointer,"native node")
        record=item.original_native_record
        if node!=ptr or node in seen or type(record) is not bytes or len(record)<0x24:
            raise Original4F3B10QuerySourceError("reached native linked node identity/bytes mismatch")
        visited.append(node)
        seen.add(node)
        if unpack_from("<H",record,0x22)[0]==subkey:
            match=node
            break
        ptr=unpack_from("<I",record,0x10)[0]
    else:
        if ptr:
            raise Original4F3B10QuerySourceError("incomplete source 4F3B10 linked node walk")
    if match and len(visited)!=len(links):
        raise Original4F3B10QuerySourceError("unreached native list nodes after match")
    return SourceOriginal4F3B10LookupReceipt(key,subkey,head,tuple(visited),match)
