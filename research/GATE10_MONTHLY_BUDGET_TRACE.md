# Gate 10 Monthly Budget Producer Trace

Checkpoint: 27 September 2026

## Verified narrowing

- After `0x429CB0` appends a new `CMonthHistory`, the continuation around
  `0x429FAF` only fills additional monthly-history fields.
- It uses Balance aggregate pairs `0x5DD2E0` / `0x5DD3C0` when history exists
  and `0x5DD4A0` / `0x5DD500` for the initial path.
- Direct DBRUser `+0x6DC` references classify as construction/destruction,
  save/load, UI binding, or the monthly producer. No direct chairman-budget
  consumer of the rolling history list was found.

## EAMbcmonthlybudget construction

- Event ID: `0xA1`.
- Generic EAM factory: `0x538DE0`.
- Jump-table entry: `0x540484` -> branch `0x53B593`.
- The branch allocates the 0x5C-byte event with factory tag `0xA4` and calls
  constructor `0x541B20`.
- The constructor has no separate direct gameplay caller.
- Direct callers `0x5CE588` and `0x5CF8A7` of the generic factory are
  event-list deserialization/load paths, not gameplay producers.

Immediate `0xA1` constants around `0x4B480F/0x4B4849` and `0x4D2F4E` are UI
setup. The `0x41F18E` comparison against 0xA1 is an unrelated numeric
player/contract range threshold.

## Event behavior

- `EAMbcmonthlybudget` vtable is `0x7D01A4`.
- Its gameplay-handler slot `+0x3C` is generic `0x4093E0`, so the event does
  not itself mutate finance state.
- Vtable `+0x40` method `0x470CE0` is a one-year date-validity check, not a
  budget-population routine.
- DBRUser event-queue maintenance around `0x42B980..0x42BC1A` filters and
  dispatches other event IDs and is not the 0xA1 producer.

## Next trace

The strongest remaining path is generic event/template/rule population:
identify the machinery that creates or clones Business Consultant / board
events and follow the source values written to `EAMbcmonthlybudget` fields
`+0x3C..+0x54`.
