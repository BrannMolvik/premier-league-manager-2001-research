# Gate 13 Messages / News Presentation Contract

_Date: 1 October 2026 KST_

## Scope

This checkpoint promotes only already recovered original manager-mail event
identities and actions into the Gate-13 read-only presentation seam. It does not
claim a complete Messages/News screen, global inbox ordering, visual layout, or
navigation.

## Proven queue family

The recovered controlled-player workflows enqueue their original events through
the `MPMEAMail` family. The presentation contract preserves that container
identity because it is already source-backed.

## Recovered message families

### Ordinary assistant-manager contract renewal suggestion

The controlled monthly contract-maintenance path materializes:

- message ID: `0x0E`;
- original string/event key: `AssManSuggestPlayerContractRenewalM`;
- event class: `EAMAssManSuggestPlayerContractRenewalMsub`;
- accepted action: `EAMAmendContractsub`.

Suggestion creation itself does not renew the contract. Accepting the recovered
mail action enters the amendment workflow.

### Bosman contract renewal suggestion

The age/EU-exemption branch materializes:

- message ID: `0x1B7`;
- original key: `AssManSuggestBosmanPlayerContractRenewalM`;
- event class: `EAMAssManSuggestBosmanPlayerContractRenewalMsub`;
- accepted action: `EAMAmendContractsub`.

These two renewal families are separately identified in the runtime and retain
their native numeric message IDs.

### Player transfer-list request

The low-morale post-match path `0x41B580` queues a next-day manager mail:

- original key: `PlayerAskTransferList`;
- event class: `EAMPlayerAskTransferListsub`;
- accept action: `EAMAcceptTransferRequestsub`;
- refuse action: `EAMRefuseTransferRequestsub`.

Acceptance reaches the recovered transfer-list/Wanted state update path;
refusal cleans up the request chain without applying those status changes.

The persisted primary evidence used for this checkpoint does **not** pin a
numeric message ID for this family. The contract therefore stores `None`
rather than manufacturing one.

## Global ordering boundary

The current clean-room runtime stores contract-renewal suggestions and transfer
requests in separate queues. Their individual runtime order is recovered and
already exposed, but no primary evidence yet proves the original Messages/News
screen's global interleave/sort across mail families.

Therefore:

- `global_interleave_proven = False`;
- presentation must not merge these queues by date, message ID, player, or event
  name and call that original behavior.

## Explicit non-claims

The contract contains no:

- Messages/News screen ID;
- inbox or row sort key;
- visual localized caption binding beyond the recovered event/string keys;
- row rectangle or click target;
- art/resource path;
- font/color/alignment rule;
- navigation edge.

Those remain open Gate-13 work.

## Gate 13 consequence

The messages/news area now has source-proven mail family identities and actions
attached to the read-only presentation seam. Original inbox presentation,
cross-family ordering, resources, controls and navigation remain unresolved, so
the Gate-13 Messages/News visual criterion is still open.
