# Gate 13 PMatchInfo original Match Report resource trace

_Date: 2 October 2026 KST_

This checkpoint continues from the source-proven League Fixtures populated-cell
navigation into `PMatchInfo`. It records original resource ownership without
claiming that every internal PMatchInfo control/layout binding is already
recovered.

Canonical executable SHA-256:

`833bf95e92a1c76ade47106f8ad7d3ca307069b7e5778a7067cd0658838b7cc3`

Authorized source ZIP was freshly rematerialized from the private Library and
rehashed as:

`677dcbc859109818d22599f34890ca7873393aea5adbf1f1f1a32d1a76f8a8a4`

Both shipped `footballmanager.exe` copies independently reproduced the
canonical executable SHA above. The raw archive/disc bytes and disassembly stay
outside Git.

## Presentation owner identities

Recovery 155 already proved the populated League Fixtures cell action creates:

- `PMatchInfo` TypeDescriptor `0x81D058`;
- final vtable `0x7C41D4`;
- constructor `0x487580`;
- base class `PExplodingDialog`;
- exact 760x500 dialog size.

Fresh RTTI inspection further source-binds the embedded Match Info subpanel
family:

- `PMatchInfoSubPanelBase`: TypeDescriptor `0x81D078`, COL `0x7E4C08`,
  vtable `0x7C42B8`;
- `PMatchInfoSubPanel`: TypeDescriptor `0x81D0A0`, COL `0x7E4BD0`,
  vtable `0x7C426C`.

Inside `PMatchInfo::0x487580`, an embedded object beginning at
`PMatchInfo+0x1C0` is first initialized through the subpanel-base constructor
`0x487A10` and later receives `PMatchInfoSubPanel` vtable `0x7C426C`.
Additional sibling/base subpanel objects are constructed later in the same
owner. This ties the Match Report implementation region to the concrete
`PMatchInfo` dialog rather than only to filenames.

## Exact contiguous Match_report loader family

The canonical executable retains **20** exact
`FM2001_Art/Generic/Match_report/*.444` literals. Each is loaded by the
standard original resource loader into a raw handle; a wrapper object lives
exactly `0x20` below that raw handle. Across all 20 entries, raw handles
descend by exactly `0x40`, from `0x943570` through `0x9430B0`.

All 20 source files were re-read directly from the authorized Joliet disc and
matched the following firsthand byte sizes, SHA-256 values and native EA444
dimensions.

| Resource | Literal VA | Raw | Wrapper | Bytes | Geometry | SHA-256 |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| `info_player.444` | `0x837E9C` | `0x943570` | `0x943550` | 4,688 | 274x16 | `c128d82caadb24ec932c0786e5b6b714c08f63fe1acad01c9f0ff6b459ac1033` |
| `info_player_disabled.444` | `0x837ECC` | `0x943530` | `0x943510` | 3,972 | 274x16 | `537ab4f3f36a9246838e84f33a520d0fd26ec818b160a9fcae891b929cee2f34` |
| `info_popup.444` | `0x837F08` | `0x9434F0` | `0x9434D0` | 179,988 | 760x500 | `d4bcf7d57b5e38de01d43e214d937045529e6434d1c40bb0f04620753c18f5e6` |
| `red_card.444` | `0x837F38` | `0x9434B0` | `0x943490` | 688 | 14x14 | `215c223e62062f7f61745f6f72a85e25459becd4b2f05f8164997664f51ef019` |
| `yellow_card.444` | `0x837F68` | `0x943470` | `0x943450` | 724 | 14x14 | `b6b13283b398da35cc7af76a8f1d8a2327e9445397efba1766753c3ee6891ff8` |
| `Sub_on.444` | `0x837F98` | `0x943430` | `0x943410` | 528 | 14x14 | `cee9c2b9b17834606d9414d9c04f8a1f0e1f7ee621f9d2695c7f45e4d4b28fe1` |
| `sub_off.444` | `0x837FC4` | `0x9433F0` | `0x9433D0` | 576 | 14x14 | `5f9837e6444eb1d724d0e845ac0f70d02180f1d3a6d7a4c9a3d45bef0598eb32` |
| `injured.444` | `0x837FF0` | `0x9433B0` | `0x943390` | 736 | 14x14 | `ab0820167dd7ebf2840906a16beaec7b8895202a3f6be77995eab94b33dfc41f` |
| `score.444` | `0x83801C` | `0x943370` | `0x943350` | 700 | 14x14 | `49b2ef946e1934d25ab23cb30e35035ef0c6c0bf07eee950ba5b676d01d9bcae` |
| `red_card_single.444` | `0x838048` | `0x943330` | `0x943310` | 700 | 14x14 | `f5f721db52098a1a9b14ddac30c76265e478e49ee53db09ab0f2d1e04656ee25` |
| `name_block_1.444` | `0x83807C` | `0x9432F0` | `0x9432D0` | 3,528 | 195x36 | `79a1eddbdd497992aa85f564269b396dbc6bf00eee95eca280e3e4268f81c832` |
| `name_block_2.444` | `0x8380B0` | `0x9432B0` | `0x943290` | 3,228 | 195x36 | `aa4b9e3976d6f84a74bd0bc60bd4cd64701e2bd5bae68ce282b6ca9eed462272` |
| `name_block_3.444` | `0x8380E4` | `0x943270` | `0x943250` | 3,536 | 195x36 | `fedd753e3eba4dcc125af7493401e2f0371636856a9a6f4814e243e896c3b24c` |
| `name_block_4.444` | `0x838118` | `0x943230` | `0x943210` | 3,212 | 195x36 | `9b1f5e3dc6eb4099cef0be89038cd2776035c0e9c95bf8751f361a44d927a211` |
| `match_name_grid.444` | `0x83814C` | `0x9431F0` | `0x9431D0` | 3,036 | 185x36 | `03ee3fca92ce681dbf8d4c2a00958bc00447a15822c5efaf6341073609dfc068` |
| `poss_back.444` | `0x838180` | `0x9431B0` | `0x943190` | 7,140 | 294x25 | `e8090259d1f38e13f22918475a8057a9ffd29145d7d6950dd214cb16982b7392` |
| `poss_blue.444` | `0x8381B0` | `0x943170` | `0x943150` | 8,372 | 264x21 | `18a440005bfc980aadf30be1ce583c2cc089d6a5c7b38d0ac08aa1e89a852119` |
| `poss_yellow.444` | `0x8381E0` | `0x943130` | `0x943110` | 7,976 | 264x21 | `396cfe3a52263e3c24ab59b3d4f240e42c408afc9182125eb967ef5d56570c94` |
| `pitch_normal.444` | `0x838210` | `0x9430F0` | `0x9430D0` | 15,932 | 294x78 | `73f6c0ecc57a383c63288064c371f947772f584800dfd3f4d2b1323063d9a6ba` |
| `match_incid_grid.444` | `0x838244` | `0x9430B0` | `0x943090` | 2,788 | 142x36 | `0d7ba8c3de23ac24f0610233eb9381b0e5a7e620299acd52781a27966f8c50f3` |

The `info_popup.444` native geometry is independently identical to the exact
760x500 PMatchInfo dialog size recovered from `0x488C80`, strengthening the
background ownership correlation without relying on the filename alone.

## Direct bounded consumers already traced

The contiguous loader family establishes resource ownership, but this
checkpoint does **not** pretend that every final widget placement is known.
Direct code consumers are recorded only where executable instructions have
already been bounded.

| Resource | Direct consumer VA(s) | Handle form |
| --- | --- | --- |
| `info_player.444` | `0x4838AC` | wrapper |
| `info_player_disabled.444` | `0x483A81` | wrapper |
| `info_popup.444` | `0x484FFF` | raw |
| `red_card.444` | `0x485A50`, `0x4860C0` | wrapper |
| `yellow_card.444` | `0x48366D`, `0x485A24`, `0x486094` | wrapper |
| `Sub_on.444` | `0x485A81`, `0x4860F1` | wrapper |
| `sub_off.444` | `0x485A9E`, `0x48610E` | wrapper |
| `injured.444` | `0x4859FD`, `0x48606D` | wrapper |
| `score.444` | `0x4859D5`, `0x486045` | wrapper |
| `red_card_single.444` | `0x485A5C`, `0x4860CC` | wrapper |
| `match_name_grid.444` | `0x483541`, `0x483784` | raw |
| `pitch_normal.444` | `0x483B1E` | raw |
| `match_incid_grid.444` | `0x4835AD`, `0x4837EC` | raw |

For the four `name_block_*.444` and three possession-strip resources, the
exact source bytes/static handles are proven, but this checkpoint leaves their
per-control consumer tuple empty until the data-flow reaches a concrete owner.
That is a fidelity boundary, not an omission to fill by visual guess.

## Reconstruction consequence

`reconstruction/original_pmatchinfo_resources.py` now guards:

- all 20 source Match Report paths;
- firsthand SHA-256, byte size and EA444 geometry;
- exact path-literal, raw-handle and wrapper addresses;
- exact contiguous 0x40 handle-family arithmetic;
- the PMatchInfo / PMatchInfoSubPanel RTTI identities;
- direct consumer addresses only for the 13 resources whose consumer has
  already been bounded;
- strict source validation for any future private staging run.

No original Match Report graphic bytes are committed by this checkpoint.

## Still open

1. exact control geometry/text/font bindings throughout the PMatchInfo
   subpanels;
2. direct final consumers for the four name-block and three possession-strip
   resources;
3. PMatchInfo internal event/tab/navigation behavior beyond the already-proven
   League Fixtures entry route;
4. intentional provenance import of the minimum required source graphics once
   binary Git transport is available;
5. integrated real-Windows presentation validation;
6. remaining Gate-13 screens after the fixtures/results family reaches a
   sufficient source-faithful presentation boundary.
