# Gate 15 support-staff monthly-cost source trace

_Date: 5 October 2026 KST_

## Status

**Private-source adjudication tooling only. This does not close the fidelity gap or Gate 15.**

Recovery 317 rebases this tooling on the post-#464 fidelity-ledger baseline. The active Finance/board gap keeps the same ledger key and Planned gate, so the one-to-one Gate-15 coverage audit remains authoritative.

The ordinary monthly support-staff accounting path is already source-qualified.
The remaining boundary is the value returned by one CSupportStaff virtual.

## Existing recovered contract

Canonical executable research already proves:

- calendar day-of-month 1 reaches `0x4CA0F0`;
- `0x4CA0F0` iterates CSupportStaff objects in DBRUser support-staff lists
  `+0x5B8` and `+0x5C4`;
- each object is queried through virtual slot `+0x24`;
- the returned value is multiplied by `1000.0` and then `1/12`;
- the resulting amount is debited through Balance category **102**, flag **1**;
- Finance Overview independently aggregates category 102.

This establishes cadence, accounting category and arithmetic. It does **not**
establish the value producer itself.

Current clean-room support-staff state materializes the source-backed type,
age-like value, training rating and status required by fresh-user training.
That is not enough to invent the virtual `+0x24` amount.

## New bounded tracer

`reconstruction/gate15_support_staff_cost_source_trace.py` reads only the
checksum-gated canonical PE and:

1. resolves the known CSupportStaff vtable at `0x7C6834`;
2. resolves the already-qualified type `+0x14`, unresolved cost-value
   `+0x24`, and training-rating `+0x40` slot targets;
3. emits bounded private code windows around those targets;
4. emits bounded windows around:
   - monthly caller `0x4CA0F0`;
   - CSupportStaff constructor `0x4CA610`;
   - generic generator `0x4C98B0`;
   - fixed fresh-user generator `0x4C9D40`;
5. keeps all amount/materialization/completion flags false.

The output must remain outside the repository because it may contain original
executable bytes and disassembly.

Example private invocation:

```powershell
python reconstruction/gate15_support_staff_cost_source_trace.py `
  C:\path\to\FOOTBAL.EXE `
  --output C:\private\gate15-support-staff-cost.json `
  --disassemble
```

## Exact adjudication needed

When private process execution is healthy, inspect the resolved `+0x24` target
and answer only these source questions:

1. Does the virtual return a direct CSupportStaff field, a constant, or a
   computed value?
2. If it reads object state, what exact offset/type/units back the return value?
3. Where is that state initialized for generic and fixed fresh staff?
4. Can later staff maintenance mutate it?
5. Is it serialized/deserialized for internal original CSupportStaff persistence?

Only after those points are source-locked may the reconstruction materialize
the staff cost value and post `value * 1000 / 12` on day 1 as category 102.

## Fail-closed rule

The vtable pointer and a bounded target window are **not** proof of a salary,
wage, annual cost, rating multiplier, or any other business label. Until the
producer and lifecycle are recovered, the monthly amount stays absent and the
Gate-15 finance residual remains open.
