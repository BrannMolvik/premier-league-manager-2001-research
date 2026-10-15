"""Exact reached x87-status branch topology of original 5DA250.

Actual original FPU AH statuses and two original QWORD arguments required;
no fake Python numeric formula for x87 extended intermediates is returned.
"""
from dataclasses import dataclass
from struct import pack, unpack
from fractions import Fraction
from math import isfinite

class Original5DA250BranchSourceError(ValueError):
    pass

@dataclass(frozen=True)
class SourceOriginal5DA250BranchReceipt:
    original_argument_qword_esp4: bytes
    original_argument_qword_espc: bytes
    original_reached_compare_ah: tuple[int,...]
    original_native_path: str
    original_literal_return_qword_if_exact: bytes|None
    original_computed_x87_value_unresolved: bool
    original_native_5da250_executed: bool=False
    live_game_state_updated: bool=False


def source_original_5da250_reached_x87_branch(
    *, original_esp4_qword: bytes,
    original_espc_qword: bytes,
    original_5da25a_ah: int,
    original_5da26b_ah_if_reached: int|None,
    original_5da29c_ah_if_reached: int|None,
    original_5da2bb_ah_if_reached: int|None,
    original_5da280_ah_if_reached: int|None,
)->SourceOriginal5DA250BranchReceipt:
    a,b=original_esp4_qword,original_espc_qword
    if type(a) is not bytes or len(a)!=8 or type(b) is not bytes or len(b)!=8:
        raise Original5DA250BranchSourceError('both actually reached native 5DA250 QWORD stack inputs required')
    flags=(original_5da25a_ah,original_5da26b_ah_if_reached,
           original_5da29c_ah_if_reached,original_5da2bb_ah_if_reached,
           original_5da280_ah_if_reached)
    if any(v is not None and (type(v) is not int or not 0<=v<=255) for v in flags):
        raise Original5DA250BranchSourceError('actual reached FNSTSW AH bytes required')
    if type(flags[0]) is not int:
        raise Original5DA250BranchSourceError('source 5DA25A status required')
    status=[]
    def take(index):
        v=flags[index]
        if v is None:
            raise Original5DA250BranchSourceError('missing reached original x87 comparison status')
        status.append(v)
        return v
    def done(route,constant,computed):
        # Reject status values spuriously claimed from unreachable comparison sites.
        supplied=[v for v in flags if v is not None]
        if supplied!=status:
            raise Original5DA250BranchSourceError('unreached native status byte supplied')
        return SourceOriginal5DA250BranchReceipt(a,b,tuple(status),route,
            pack('<d',constant) if constant is not None else None,computed)
    if not take(0)&0x41:
        return done('5da25f-direct-literal-0p1',0.1,False)
    if not take(1)&0x41:
        path='5da274-ratio'
    elif take(2)&0x01:
        path='5da2a3-negative-half-ratio'
    elif take(3)&0x01:
        path='5da2c2-weighted-negative-ratio'
    else:
        return done('5da2d6-direct-literal-2p0',2.0,False)
    if take(4)&0x01:
        return done(path+'-clamped-to-0p1',0.1,False)
    return done(path+'-x87-computed',None,True)

def source_original_5da250_finite_prethreshold_path(
    *, original_esp4_qword: bytes, original_espc_qword: bytes,
) -> str:
    """Classify only source-proven finite comparisons, never the x87 result.

    5DA258 compares A with B; 5DA265 compares A with original zero.
    5DA298 computes exactly -B/2 before 5DA298/9C compares it to A.
    5DA2B5 negates B before 5DA2B7/BB compares -B with A.
    Rational comparison preserves original finite QWORD input distinctions,
    including binary64 subnormals that Python float intermediate arithmetic
    would silently round to zero. Intermediate score/threshold remains unknown.
    """
    a, b = original_esp4_qword, original_espc_qword
    if type(a) is not bytes or len(a) != 8 or type(b) is not bytes or len(b) != 8:
        raise Original5DA250BranchSourceError("both source QWORD arguments required")
    af, bf = unpack("<d", a)[0], unpack("<d", b)[0]
    if not (isfinite(af) and isfinite(bf)):
        raise Original5DA250BranchSourceError(
            "nonfinite original FPU status/control word not source-qualified"
        )
    a_exact, b_exact = Fraction.from_float(af), Fraction.from_float(bf)
    if a_exact > b_exact:
        return "5da25f-direct-literal-0p1"
    if a_exact > 0:
        return "5da274-ratio"
    # FMUL -0.5 can round under x87 24-bit precision, which has not
    # been sourced for this call. Fail closed where PC24-vs-PC53/64 or
    # unknown native rounding mode could alter the strict comparison.
    negative_half_b = -b_exact / 2
    if negative_half_b:
        odd_significand = abs(negative_half_b.numerator)
        while odd_significand % 2 == 0:
            odd_significand //= 2
        if (odd_significand.bit_length() > 24 and
                abs(a_exact - negative_half_b) <= abs(negative_half_b) / (1 << 22)):
            raise Original5DA250BranchSourceError(
                "native x87 precision/rounding control unresolved at -B/2 comparison"
            )
    if negative_half_b < a_exact:
        return "5da2a3-negative-half-ratio"
    if -b_exact < a_exact:
        return "5da2c2-weighted-negative-ratio"
    return "5da2d6-direct-literal-2p0"
