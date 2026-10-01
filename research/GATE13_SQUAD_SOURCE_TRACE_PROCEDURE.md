# Gate 13 Squad Source Trace Procedure

_Date: 1 October 2026 KST_

**Status: COMPLETED by local Windows recovery at `4537f9b150cab8e2282c5d33a30c13a43cfb50c3`.** This file is retained as the reproducible private-trace procedure. Do not treat it as the active task or rerun it unless a regression/evidence dispute requires fresh adjudication.

## Purpose

The task documented here was to recover the native Squad player-list
row/column/status bindings and the `FormationText` state-to-frame selection
without naming atlas states by visual guesswork. That task is now closed; the
current Gate-13 boundary is the real Windows first-screen graphical audit and
remaining TeamSelect hierarchy input/state mapping.

The durable source anchors already proven on canonical main are:

- `CBasePlayerList` vtable `0x7C5BC8`;
- `FormationText` vtable `0x7C5700`, with resource setup entry points
  `0x4B6B60` and `0x4B6C30`;
- `PSquadPitch` vtable `0x7C54A8`, setup `0x4B3C80`;
- `PSquadScreen` vtable `0x7C5CA4`, setup `0x4B5720`, event handler
  `0x4B8E70`.

`reconstruction/gate13_squad_source_trace.py` is a fail-closed private trace
aid for exactly those anchors. It reuses the canonical executable SHA gate and
the bounded PE32/vtable utilities already validated by the native Button trace.
It does **not** assign row meanings, column names, status icons, native state
names, or source-frame meanings.

## Canonical private run

Run only against the independently verified executable with SHA-256:

`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`

Example:

```text
python reconstruction/gate13_squad_source_trace.py "<private-footballmanager.exe>" --disassemble --vtable-slots 24 --output "<private-folder-outside-Git>/gate13-squad-trace.json"
```

The output must remain outside the repository because it contains original
instruction and pointer evidence.

## Manual adjudication order

1. Use the four class-vtable slot lists to identify callable methods that are
   actually reached from the already-proven Squad setup/event paths.
2. For `CBasePlayerList`, trace constructor discriminator 0/1 outward to the
   row builder, each visible field fetch, any status-bit/icon lookup, and any
   sort/selection state. Record only DBRPlayer offsets/helpers that are reached
   by the native presentation path.
3. For `FormationText`, trace the values written/read between the two resource
   setup methods and later update/draw methods. Prove the exact value-to-source-
   frame transform before naming any frame or state.
4. Cross-check any recovered frame index against the imported original
   `squad_bars.444` and `squad_form_anim.444` geometry. Atlas height alone
   is not evidence of semantic partitioning.
5. Promote only conclusions supported by direct control/data flow into
   `original_squad_resources.py`, focused tests, and
   `research/GATE13_SQUAD_RESOURCE_CORRELATION.md`.

## Historical infrastructure boundary (superseded)

Before the successful local recovery, in the 1 October 2026 cloud recovery, the canonical 511,121,336-byte private
source ZIP was successfully resolved and materialized from the durable Library
identity, but both shell and Python process execution returned `ClientError`
before source inspection. Therefore the trace utility can be prepared and
synthetically tested in hosted CI, but the new native bindings must not be
claimed until a working private/local execution path runs the command above and
the resulting control/data flow is manually adjudicated.

The real Windows PStartMenu/TeamSelect graphical audit remains a separate
mandatory Gate-13 item.
