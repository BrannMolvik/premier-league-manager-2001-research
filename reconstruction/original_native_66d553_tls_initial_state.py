"""Original CRT 66D553 first TLS allocation vs already-existing thread state.

Original 66D553 calls imported TlsGetValue(slot 84AD40). When nonnull,
it returns that actual record, without reseeding. When null, the source
allocates 0x74 calloc-zero bytes, calls TlsSetValue, then 66D540,
which writes +0x50=0x84D430 and +0x14=1. It stores full source EAX
returned by imported thread-id callback into record+0, sets +4 to
0xFFFFFFFF, then returns the new thread-local record.

Source-only strict immutable projection; never invokes kernel32/TLS,
allocates live memory, creates a live seed, alters GameState, or
asserts that an already-running thread has seed1. Failure of
TlsSetValue follows 66D5A6 error path, NOT a valid new TLS record.
"""
from dataclasses import dataclass
from struct import pack_into,unpack_from


class OriginalCRTThreadInitSourceError(ValueError):
    pass


ORIGINAL_TLS_STRUCT_LENGTH = 0x74
ORIGINAL_TLS_RANDOM_SEED_OFFSET = 0x14
ORIGINAL_TLS_RECORD_V50_CONST = 0x84D430
ORIGINAL_TLS_FIRST_SEED = 1


@dataclass(frozen=True)
class SourceOriginal66D553TLSRecord:
    original_tls_slot_84ad40: int
    original_tls_record_pointer: int
    original_tlsgvalue_pointer_before_init: int
    source_original_new_tls_initialized: bool
    source_record_before_first_reached_66951c: bytes
    original_seed_at_plus14: int
    original_source_initializer_va: int | None
    original_actual_system_tls_access_executed: bool = False
    original_66951c_rand_executed: bool = False
    original_game_state_mutated: bool = False


def source_original_66d553_reached_crt_tls_record(
    *,
    original_tls_slot_dword_84ad40: int,
    original_tlsgvalue_return_pointer: int,
    original_existing_tls_record_if_reached: bytes | None,
    original_calloc_return_pointer_if_fresh: int | None,
    original_calloc_zero_record_if_fresh: bytes | None,
    original_tlssetvalue_return_eax_if_fresh: int | None,
    original_thread_id_callback_return_eax_if_fresh: int | None,
) -> SourceOriginal66D553TLSRecord:
    def uint32(v):
        return type(v) is int and 0<=v<=0xffffffff
    slot=original_tls_slot_dword_84ad40
    ptr=original_tlsgvalue_return_pointer
    if not uint32(slot) or slot==0xffffffff or not uint32(ptr):
        raise OriginalCRTThreadInitSourceError(
            "source 84AD40 TLS slot and actual imported GetTlsValue result required")
    if ptr:
        if (type(original_existing_tls_record_if_reached) is not bytes or
            len(original_existing_tls_record_if_reached)<ORIGINAL_TLS_STRUCT_LENGTH or
            any(x is not None for x in (
                original_calloc_return_pointer_if_fresh,
                original_calloc_zero_record_if_fresh,
                original_tlssetvalue_return_eax_if_fresh,
                original_thread_id_callback_return_eax_if_fresh,
            ))):
            raise OriginalCRTThreadInitSourceError(
                "already-attached CRT TLS record cannot be overwritten by first-init receipts")
        record=original_existing_tls_record_if_reached
        return SourceOriginal66D553TLSRecord(
            slot,ptr,ptr,False,record,unpack_from('<I',record,0x14)[0],None)
    alloc=original_calloc_return_pointer_if_fresh
    raw=original_calloc_zero_record_if_fresh
    set_ok=original_tlssetvalue_return_eax_if_fresh
    tid=original_thread_id_callback_return_eax_if_fresh
    if (original_existing_tls_record_if_reached is not None or
        not uint32(alloc) or not alloc or
        type(raw) is not bytes or len(raw)!=ORIGINAL_TLS_STRUCT_LENGTH or
        raw!=bytes(ORIGINAL_TLS_STRUCT_LENGTH) or
        not uint32(set_ok) or not set_ok or
        not uint32(tid)):
        raise OriginalCRTThreadInitSourceError(
            "first TLS allocation requires source calloc(1,0x74), successful TlsSetValue "
            "and actual reached thread-ID callback EAX")
    initialized=bytearray(raw)
    pack_into('<I',initialized,0,tid)
    pack_into('<I',initialized,4,0xffffffff)
    pack_into('<I',initialized,0x14,ORIGINAL_TLS_FIRST_SEED)
    pack_into('<I',initialized,0x50,ORIGINAL_TLS_RECORD_V50_CONST)
    return SourceOriginal66D553TLSRecord(
        slot,alloc,0,True,bytes(initialized),1,0x66D540)
