# Gate 11 Scouting Status and Strength Filter

Verified against the canonical FM2001 `FOOTBAL.EXE` with SHA-256
`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`.

This note closes the two first-stage scouting inputs that were deliberately
left neutral after the earlier `0x4AE680` mapping.

## Status bit 7 = Out of contract

The scouting panel's three final status controls are bound directly to original
localized strings:

| Panel control | String global | Original label | Player-state test |
|---|---:|---|---|
| `+0x76B8` | `0x983B14` | Transfer listed | `player+0x14` bit 8 |
| `+0x76F8` | `0x983B10` | Out of contract | `player+0x14` bit 7 |
| `+0x7738` | `0x983B0C` | Loan | bit 12 plus `0x41E450` |

The binding is direct rather than inferred from status-table ordering.
At `0x4AE8FF..0x4AE90A`, the middle checkbox tests
`player+0x14` bit 7. Therefore the previously neutral scouting status bit 7
is exactly the original **Out of contract** status.

Do not confuse this with the unrelated `player+0x174` bit 7 already mapped
as the signed-for-another-club state.

### Producer / clearer boundary

Direct executable tracing also identifies real status transitions:

- `0x4177C0` clears the main status dword, sets low-byte bit 7 and detaches
  the player from club-related IDs. This is an explicit out-of-contract/free
  player transition.
- `0x41ABC0` is a contract-maintenance producer. Its contract-date branch can
  reach `or al,0x80` at `0x41AC76..0x41AC7B`, then zero the byte at
  `player+0xC0`.
- `0x4185B0` clears bit 7 as part of a broader player-status reset.
- `0x419210` also clears bit 7 during a separate state transition.

This is enough to name and expose the scouting predicate, but not enough to
replace the original contract-maintenance lifecycle with
`contract_expiry_date <= current_date`. The `0x41ABC0` path contains
additional date, club, tenure, age and conditional/random branches. Keep that
producer lifecycle separate until those transitions are reconstructed exactly.

## `0x876868` is a selected current-skill slot, not a separate player field

The global is initialized to zero at `0x4AD8E8`. The Strengths selector event
then copies its selected value to both panel `+0x64E4` and global
`0x876868`:

```text
0x4AE0DA  mov eax,[panel+0x75D0]
0x4AE0E7  mov [panel+0x64E4],eax
0x4AE0ED  mov [0x876868],eax
```

The selector is built at `0x4AD4E0..0x4AD51C`:

- value 0 is the original label **All**;
- values 1..17 are populated from the pointer table
  `0x822538..0x822578`;
- the 17 labels, in order, are the game's current player attributes:
  Speed, Strength, Stamina, Determ., Injury Proneness, Passing, Shooting,
  Tackling, Heading, Control, Technique, Awareness, Agility, Keeping,
  Confidence, Leadership, Set Piece.

The panel heading at `0x983B1C` is the original string **Strengths**.

The filter then reads:

```text
0x4AE862  mov eax,[0x876868]
0x4AE867  test eax,eax
0x4AE869  je   strength_gate_passes
0x4AE86D  mov cl,[eax+player+0x1D]
```

Because the selected value is 1..17, this addresses exactly
`player+0x1E..player+0x2E`, the already-mapped 17-byte current-skill array.
There is no additional per-player scouting-byte owner to recover.

Thus:

```text
selected = 0      -> All; bypass this gate
selected = 1..17  -> current_raw[selected - 1]
```

Panel `+0x64E4` is the same 0..17 selector value and is intentionally part
of the exact `0x4AF7F0` deterministic scouting reseed hash.

## Exact ScoutStrengthMin comparison

The selected raw skill byte is converted with the existing displayed-skill
formula:

```text
displayed = floor((30 * raw + 128) / 255)
```

The result is compared with global `0x8223F4`; `jl` rejects values below
the threshold, so the gate is inclusive:

```text
pass = displayed >= ScoutStrengthMin
```

The shipped executable initializes `0x8223F4` to **20**. Tuning-loader code
at `0x50B44A..0x50B480` associates the literal key
`ScoutStrengthMin` with that global and can override the initialized value.

## Clean-room implementation boundary

The first-stage scouting implementation can now:

1. give status bit 7 its exact Out-of-contract meaning;
2. derive the Strengths predicate directly from `RuntimePlayer.current_raw`,
   selector value 0..17, and `ScoutStrengthMin`;
3. use shipped default 20 when no tuning override is supplied.

The ordinary out-of-contract contract-maintenance producer remains a separate
Gate-11/contract lifecycle task. Do not synthesize it from contract expiry
alone.
