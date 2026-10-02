# Gate 15 Fidelity Disposition

_Last reconciled: 3 October 2026 KST, Recovery 186._

## Purpose

Gate 15 is finite by design. Its roadmap criterion does not require every
historical uncertainty to become a bit-for-bit reconstruction. Every known
deviation must instead reach one of three durable dispositions:

1. fixed from evidence;
2. proven irrelevant to the shipped path; or
3. explicitly accepted and documented as a modernization limitation.

A deterministic fallback may remain only when it is clearly named as a
fallback and is never presented as recovered original behavior.

Gate 13 remains the earliest incomplete validation gate, and Gate 14 remains
unfinished work-ahead. This Gate-15 document does not bypass those earlier
milestones.

## Closed during Recovery 186

### Fixed: persistent-injury availability count

The non-user persistent-injury guard now consumes the exact shared
`DBRClub::0x405080` roster predicate already reconstructed for selling-club
transfer decisions. It excludes exactly transfer-listed, injured, loaned-out,
and suspended players. Selection-only exclusion is not part of that helper.

PR #138 verifies the correction with the exact 14-player boundary and
no-RNG suppression behavior.

## Accepted modernization limitations

### Original PLM2001 save-file import

The release supports the modern versioned schema-34 persistence path. Import or
export of the original game's save format is not implemented. Gate 17 requires
working save/reload for the modern port, not backward compatibility with legacy
save files. This is intentionally disclosed rather than hidden behind a guessed
converter.

### Fully indistinguishable native league-table qsort ties

Every source comparator field is reconstructed. If two rows compare equal on
all of them, the legacy comparator itself supplies no additional ordering key.
The port uses a deterministic fallback for stability and does not label that
fallback as exact original ordering.

### Invalid target-month contract dates

Source-backed contract month counts are preserved. If the destination month
does not contain the source day, the port clamps to the last valid day instead
of allowing an invalid host date. Exact legacy `0x64CDD0` normalization is
unrecovered, so this remains a disclosed bounded difference.

## Still active

The following items still require evidence, implementation, proof of
irrelevance, or a later explicit acceptance decision:

- secondary startup exact tie permutation and per-date bucket shape;
- autonomous transfer-window dated lifecycle;
- autonomous contract-category selector `0x4FA510`;
- autonomous club buy-counter update/reset lifecycle;
- residual player-negotiation branches;
- due-transfer ordering relative to same-day fixtures;
- chairman legacy budget-event family;
- remaining match-day/recurring commercial-income policy;
- finance/board residuals;
- Gate-13 front-end/UI fidelity items until that gate closes;
- Gate-14 FastView/audio/3D fidelity items until that gate closes.

Acceptance must not be used merely because private execution is temporarily
unavailable. Source-sensitive behavior with meaningful ordinary-play impact
stays open unless there is a concrete release-scope reason to accept it.
