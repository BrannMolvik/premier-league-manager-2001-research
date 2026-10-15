"""Bounded R1 5DA250 B local: last *explicit* original native stack writer.

Inputs are independently observed prior stage guards and human-club results.
None = skipped, False = entered nonhuman, True = entered human.
If all prior native stage B stores were skipped, the original ordinary 5DA2F0\nsetup still zero-initializes B at 5DA92B/+33 (two PUSH-shifted DWORDs).\nDoes not prove a live native run, arbitrary native B bytes, x87, or GameState.
"""
from dataclasses import dataclass


class OriginalStageBWriterEvidenceError(ValueError):
    pass


_B_WRITE_SITES = (
    (0x5DA9AD,),
    (0x5DAC57, 0x5DAC5D),
    (0x5DAED5, 0x5DAEDB),
    (0x5DB153, 0x5DB159),
)


@dataclass(frozen=True)
class OriginalStageBExplicitWriter:
    target_stage: int
    preceding_native_stage: int | None
    native_store_sites: tuple[int, ...]
    no_prior_explicit_writer_proven: bool
    native_b_qword_known: bool = False
    native_b_zero_initializer_sites: tuple[int, int] = (0x5DA92B, 0x5DA933)
    source_b_qword_if_proven: bytes | None = None
    original_executed: bool = False
    game_state_updated: bool = False


def source_last_explicit_b_writer_before_nonhuman_stage(
    *, target_stage: int, reached_prior_stage_gates: tuple[bool | None, ...]
) -> OriginalStageBExplicitWriter:
    """Only the last explicitly reached [ESP+38/+3C] store. No reachability inference.

    Caller MUST independently establish all prior guard and human results.
    Missing provenance cannot be treated as a skipped stage.
    """
    if type(target_stage) is not int or target_stage not in (2, 3, 4):
        raise OriginalStageBWriterEvidenceError('nonhuman target stage 2..4 required')
    x = reached_prior_stage_gates
    if type(x) is not tuple or len(x) != target_stage - 1:
        raise OriginalStageBWriterEvidenceError('one explicit guard/human value per prior stage required')
    if any(v is not None and type(v) is not bool for v in x):
        raise OriginalStageBWriterEvidenceError('prior stage must be skipped None or entered native human bool')
    last = None
    for index, human in enumerate(x, 1):
        if human is None:
            continue
        if index == 1 or human:  # Stage1 always writes B, later stages only human.
            last = index
    return OriginalStageBExplicitWriter(
        target_stage, last, _B_WRITE_SITES[last - 1] if last else (),
        no_prior_explicit_writer_proven=(last is None),
        native_b_qword_known=(last is None),
        native_b_zero_initializer_sites=(0x5DA92B, 0x5DA933),
        source_b_qword_if_proven=(b'\x00' * 8 if last is None else None),
    )
