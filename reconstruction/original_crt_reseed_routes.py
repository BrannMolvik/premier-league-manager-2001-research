"""Source-specific FM2001 MSVC CRT srand routes, NOT observed execution.

Native original 0x66950F srand has exactly four direct callers:
0x53109E clock startup, 0x4AF876 world/state XOR, 0x50DE2E
save-time rand-then-srand, and 0x50E16E serialized state restore.
The caller must qualify WHICH original path actually ran.
Original EXE is private and never executed here.
"""
from __future__ import annotations
from dataclasses import dataclass
from match_schedule import MsvcCrtRng

APPLICATION_CLOCK_SEED = 0x53109E
WORLDGEN_XOR_SEED = 0x4AF876
SAVE_RAND_THEN_SEED = 0x50DE2E
RESTORE_SERIALIZED_SEED = 0x50E16E

class OriginalCrtReseedError(ValueError):
    pass

@dataclass(frozen=True)
class OriginalCrtReseedReceipt:
    native_srand_callsite: int
    state_before: int
    seed_argument: int
    state_after: int
    direct_raw_draws_before_seed: int
    actual_native_route_verified: bool = False


def _owner(rng: MsvcCrtRng) -> None:
    if type(rng) is not MsvcCrtRng:
        raise OriginalCrtReseedError("Require exact caller-owned MSVC CRT")


def _value(value: int) -> None:
    if type(value) is not int or not 0 <= value <= 0xffffffff:
        raise OriginalCrtReseedError("Require observed unsigned 32-bit seed")


def _reseed(rng: MsvcCrtRng, value: int, native_site: int, raw_draws: int
           ) -> OriginalCrtReseedReceipt:
    before = rng.state
    rng.seed(value)
    return OriginalCrtReseedReceipt(native_site,before,value,rng.state,raw_draws)


def project_original_application_clock_seed(
    rng: MsvcCrtRng, *, observed_time32_seconds: int
) -> OriginalCrtReseedReceipt:
    """Source 0x531098 _time32-like return -> 0x53109E srand, once here.

    The true original process clock second and timezone are NOT observed
    by this API. Does not calculate timestamp from current system clock.
    """
    _owner(rng)
    if (type(observed_time32_seconds) is not int
            or not 0 <= observed_time32_seconds <= 0x7fffffff):
        raise OriginalCrtReseedError("Require observed valid native _time32 seconds")
    return _reseed(rng,observed_time32_seconds,APPLICATION_CLOCK_SEED,0)


def project_original_worldgen_xor_seed(
    rng: MsvcCrtRng, *, observed_xor_seed: int
) -> OriginalCrtReseedReceipt:
    """0x4AF7F0 computes source object XOR; 0x4AF876 calls srand.

    The object fields, call timing and earlier ancestor draw effects
    must be source-observed separately; we invent NONE of them.
    """
    _owner(rng)
    _value(observed_xor_seed)
    return _reseed(rng,observed_xor_seed,WORLDGEN_XOR_SEED,0)


def project_original_save_rand_then_seed(
    rng: MsvcCrtRng,
) -> OriginalCrtReseedReceipt:
    """0x50DE11 -> 0x64D530 -> rand(); 0x50DE2E srand with result.

    Only this bounded direct draw/reseed, NOT save serialization effects.
    """
    _owner(rng)
    before=rng.state
    random15=rng.rand15()
    rng.seed(random15)
    return OriginalCrtReseedReceipt(
        SAVE_RAND_THEN_SEED,before,random15,rng.state,1
    )


def project_original_restore_serialized_seed(
    rng: MsvcCrtRng, *, observed_serialized_seed: int
) -> OriginalCrtReseedReceipt:
    """0x50E164 native DWORD read -> 0x50E16E srand, not new-game init."""
    _owner(rng)
    _value(observed_serialized_seed)
    return _reseed(rng,observed_serialized_seed,RESTORE_SERIALIZED_SEED,0)
