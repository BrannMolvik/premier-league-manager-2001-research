"""Native 66951C TLS CRT-rand and 64D540 bounded match-score draw.

Original 66D553 chooses a per-thread CRT context. Actual pointer and its
pre-call bytes are REQUIRED. Native 66951C advances +0x14 DWORD by
(seed * 0x343FD + 0x269EC3) modulo 2**32 and returns bits16..30.

Original 64D540 always advances it once, multiplies rand15 by signed
call argument and exact 0x7D8060=2**-15 then invokes 668350 to truncate.
For the source match-scoring 5DABED and 5DAE68 sites the FISTP-derived
bound is clamped to >=1. The intermediate product fits exact x87 64-bit
significand for any positive original int32 bound; integer floor yields
the exact resulting native EAX on that bounded branch.

This function DOES NOT initialize 66D553 TLS state, execute a random
callback, consume live GameState RNG, assume the same seed across threads
or infer second score-side TLS state from first (other source callbacks
may draw in between). The returned post-state is a read-only projection.
"""
from __future__ import annotations
from dataclasses import dataclass
from struct import pack_into,unpack_from


class OriginalNative64D540SourceError(ValueError):
    pass


SOURCE_NATIVE_CRT_SEED_MULTIPLIER = 0x343FD
SOURCE_NATIVE_CRT_SEED_INCREMENT = 0x269EC3
SOURCE_NATIVE_CRT_TLS_RNG_OFFSET = 0x14
SOURCE_NATIVE_RAND_SCALE = 1.0 / 32768.0
SOURCE_MATCH_RNG_CALL_SITES = (0x5DABED,0x5DAE68)


@dataclass(frozen=True)
class SourceOriginalMatch64D540NativeRand:
    original_call_site: int
    original_tls_record_pointer: int
    original_seed_before: int
    original_seed_after: int
    original_66951c_rand15: int
    original_64d540_bound: int
    original_64d540_return_eax: int
    projected_tls_record_after: bytes
    original_native_tls_callback_executed: bool = False
    original_rng_state_committed: bool = False
    original_game_state_modified: bool = False


def source_original_64d540_bounded_tls_match_rng(
    *,
    original_reached_score_call_site: int,
    original_66d553_tls_record_pointer: int,
    original_66d553_tls_record_before_66951c: bytes,
    original_64d540_reached_positive_bound: int,
) -> SourceOriginalMatch64D540NativeRand:
    site=original_reached_score_call_site
    tls=original_66d553_tls_record_pointer
    record=original_66d553_tls_record_before_66951c
    bound=original_64d540_reached_positive_bound
    if type(site) is not int or site not in SOURCE_MATCH_RNG_CALL_SITES:
        raise OriginalNative64D540SourceError(
            "only actually reached original 5DABED/5DAE68 score RNG sites qualify")
    if (type(tls) is not int or not 0<tls<=0xffffffff or
        type(record) is not bytes or len(record)<0x18):
        raise OriginalNative64D540SourceError(
            "actual nonzero CRT TLS record pointer and reached +14 seed bytes required")
    if type(bound) is not int or not 1<=bound<=0x7fffffff:
        raise OriginalNative64D540SourceError(
            "original score-side 5DABD6/5DAE51 positive clamped int32 bound required")
    seed=unpack_from("<I",record,SOURCE_NATIVE_CRT_TLS_RNG_OFFSET)[0]
    after=(seed*SOURCE_NATIVE_CRT_SEED_MULTIPLIER+
           SOURCE_NATIVE_CRT_SEED_INCREMENT)&0xffffffff
    rand=(after>>16)&0x7fff
    # Native FILD 15-bit rand, FIMUL 32-bit bound and FMUL 2**-15
    # are exact for these 46-bit integer products in x87 extended.
    # 668350 sets its rounding-control word to truncate.
    result=rand*bound//32768
    updated=bytearray(record)
    pack_into("<I",updated,SOURCE_NATIVE_CRT_TLS_RNG_OFFSET,after)
    return SourceOriginalMatch64D540NativeRand(
        site,tls,seed,after,rand,bound,result,bytes(updated))
