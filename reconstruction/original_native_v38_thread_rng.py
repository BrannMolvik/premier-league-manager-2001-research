"""Verified original FM2001 match bit2 RNG 0x64D540(2), pure TLS stage.

Original executable private SHA256:
833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3.
Native 0x66951C updates *thread-local* DWORD+0x14 with unsigned MSVC
seed'=(seed*0x343FD+0x269EC3) modulo 2**32, returns
(seed'>>16)&0x7FFF. Original 0x64D540 computes floating result
random15*integer_argument*double [0x7D8060] (verified exact 2**-15),
then 0x668350 truncates toward zero to integer EAX.

For the one source-backed caller 0x513697 using arg=2 this is exactly
rand15//16384 (0 or 1). This code never reads/modifies original TLS,
advances a live GameState or claims RNG ownership of modern schedules.
"""
from __future__ import annotations

from dataclasses import dataclass


class OriginalMatchNativeRngError(ValueError):
    pass


ORIGINAL_CRT_RAND_UPDATE_VA = 0x66951C
ORIGINAL_RANDOM_SCALED_INT_VA = 0x64D540
ORIGINAL_FPU_TRUNCATE_INT_VA = 0x668350
ORIGINAL_RANDOM_DOUBLE_SOURCE_VA = 0x7D8060
ORIGINAL_CRT_LCG_MULTIPLIER = 0x343FD
ORIGINAL_CRT_LCG_INCREMENT = 0x269EC3
ORIGINAL_CRT_RAND15_MASK = 0x7FFF
ORIGINAL_RANDOM_FACTOR_DOUBLE = 1 / 32768
ORIGINAL_V38_RANDOM_INTEGER_ARGUMENT = 2


@dataclass(frozen=True)
class OriginalV38NativeTlsRandomTwoReceipt:
    original_thread_seed_before_66951c: int
    original_thread_seed_after_66951c: int
    original_rand15_result: int
    original_64d540_2_return_eax: int
    original_thread_tls_mutated: bool = False
    reconstructed_match_rng_mutated: bool = False


def source_original_v38_random_two_from_reached_tls_seed(
    *, original_reached_tls_seed_at_offset_14: int,
) -> OriginalV38NativeTlsRandomTwoReceipt:
    """Pure projection of ONE reached original RNG call 0x64D540(2).

    Original native thread state is external. Call this only after original
    0x513659 bit2 and all virtual getter equality gates actually pass.
    """
    seed = original_reached_tls_seed_at_offset_14
    if type(seed) is not int or not 0 <= seed <= 0xFFFFFFFF:
        raise OriginalMatchNativeRngError(
            "actual original thread-local RNG DWORD+0x14 uint32 required")
    updated = (seed * ORIGINAL_CRT_LCG_MULTIPLIER +
               ORIGINAL_CRT_LCG_INCREMENT) & 0xFFFFFFFF
    rand15 = (updated >> 16) & ORIGINAL_CRT_RAND15_MASK
    # For the exact source arg=2 and double 2**-15, x87 truncation is
    # identical to integer division by 16384; no floating drift.
    eax = rand15 // 16384
    return OriginalV38NativeTlsRandomTwoReceipt(
        original_thread_seed_before_66951c=seed,
        original_thread_seed_after_66951c=updated,
        original_rand15_result=rand15,
        original_64d540_2_return_eax=eax,
    )
