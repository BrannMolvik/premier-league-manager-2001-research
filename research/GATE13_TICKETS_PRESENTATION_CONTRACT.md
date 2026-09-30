# Gate 13 PTickets Presentation Contract

_Date: 1 October 2026 KST_

## Scope

This checkpoint promotes previously recovered original ticket-screen and
stadium-consumer evidence into a read-only Gate-13 presentation contract and
view. It does not reconstruct the original PTickets visual surface.

## Original PTickets state identity

Instruction-level research establishes:

- panel family: `PTickets`;
- update routine: `0x45FF10`;
- DBRUser ticket object: `+0x694`;
- complete persisted object size: `0x7C` bytes.

Its first four dwords are:

| Offset | Proven state |
| ---: | --- |
| `+0x00` | season-ticket quantity |
| `+0x04` | season-ticket price |
| `+0x08` | terrace match-day ticket price |
| `+0x0C` | seating match-day ticket price |

The remaining ticket section vector begins at `+0x14` and contains exactly
26 dwords. Fresh/user allocation research proves these native values:

| Value | Proven section state |
| ---: | --- |
| -1 | unavailable |
| 0 | home-supporter ordinary section |
| 1 | visiting-supporter ordinary section |
| 2 | season-ticket-reserved section |

## Terrace / seating attribution

The original PTickets update path resolves the previously ambiguous ordinary
price fields without relying on string order.

`0x461340` shares the same league/division reference path as `0x4615B0`
but applies the exact constant `0.75`. PTickets compares:

- ticket `+0x08` against `0x461340` at `0x4605AD`;
- ticket `+0x0C` against `0x4615B0` at `0x460753`.

Therefore `+0x08` is terrace and `+0x0C` is seating. The independently
recovered stadium consumer pairing fixes:

- stadium-entry `+0x1C` = terrace capacity;
- stadium-entry `+0x28` = seating capacity.

This is instruction attribution, not a UI convention guess.

## Read-only presentation view

`ManagementSourceDataBridge.ticket_state_view()` reads only the controlled
club's already materialized `GameState.ticket_states[club_id]` state:

- season-ticket quantity;
- season-ticket price;
- terrace price;
- seating price;
- all 26 native section-state values in source order.

It fails closed when no ticket state exists, the 26-entry shape is invalid, or
a section-state value is outside the recovered -1/0/1/2 set.

No additional stadium simulation or finance mutation is introduced by the
presentation bridge.

## Explicit non-claims

This contract contains no:

- original screen ID beyond the recovered panel family name;
- control/widget ID;
- visible caption binding;
- rectangle, section-map coordinate or click target;
- PTickets artwork path;
- font/color/alignment rule;
- navigation edge.

Those remain Gate-13 presentation work and must be recovered from original
source evidence before use.

## Hosted verification

PR #38 head `92d9d0322fd2ff0a9403a66190591438d025527f` passed:

- focused Gate-13 run `36769405085`: **230 tests**, **19 expected
  original-source-gated skips**, zero failures;
- full reconstruction run `36769405053`: **1,066 tests**, **21 expected
  original-source-gated skips**, zero failures;
- repository asset-policy run `36769404960`: passed.

It was squash-merged to main as
`cca08a22f33aebfab230afd6ced70e28bf552c10`.

These runs verify the read-only contract and integration boundary. They do not
constitute an original Windows graphical PTickets test.

## Gate 13 consequence

The ticket/finance-adjacent screen is no longer data-anonymous: PTickets'
native persisted state, exact terrace/seating attribution and section-state
semantics can now be consumed through the same read-only presentation boundary
as other management screens. Original PTickets visuals, controls and navigation
remain open.
