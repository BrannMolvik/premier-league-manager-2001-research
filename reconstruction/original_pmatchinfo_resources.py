"""Source-backed PMatchInfo / Match_report resource inventory.

Recovery 156 correlates the canonical executable's contiguous Match_report
static-loader family with the authorized original disc. Every source file below
is byte/hash/geometry verified. Direct per-control consumer addresses are
recorded only where bounded executable code has been traced; an empty consumer
tuple is deliberately not treated as missing ownership because the static
loader family and PMatchInfo/subpanel consumers establish the resource family
without inventing a final widget placement.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

from ea444_header import parse_ea444_header
from original_league_fixtures_resources import (
    LEAGUE_FIXTURES_MATCH_INFO_CLASS,
    LEAGUE_FIXTURES_MATCH_INFO_CONSTRUCTOR_VA,
    LEAGUE_FIXTURES_MATCH_INFO_TYPE_DESCRIPTOR_VA,
    LEAGUE_FIXTURES_MATCH_INFO_VFTABLE_VA,
)


class OriginalPMatchInfoResourceError(ValueError):
    pass


PMATCHINFO_SUBPANEL_BASE_CLASS = "PMatchInfoSubPanelBase"
PMATCHINFO_SUBPANEL_BASE_TYPE_DESCRIPTOR_VA = 0x81D078
PMATCHINFO_SUBPANEL_BASE_VFTABLE_VA = 0x7C42B8
PMATCHINFO_SUBPANEL_BASE_COL_VA = 0x7E4C08

PMATCHINFO_SUBPANEL_CLASS = "PMatchInfoSubPanel"
PMATCHINFO_SUBPANEL_TYPE_DESCRIPTOR_VA = 0x81D0A0
PMATCHINFO_SUBPANEL_VFTABLE_VA = 0x7C426C
PMATCHINFO_SUBPANEL_COL_VA = 0x7E4BD0


@dataclass(frozen=True)
class OriginalPMatchInfoResource:
    name: str
    source_path: str
    sha256: str
    byte_size: int
    size: tuple[int, int]
    path_literal_va: int
    raw_handle_va: int
    wrapper_va: int
    direct_consumer_vas: tuple[int, ...] = ()
    direct_consumer_handle: str | None = None


def _r(
    name: str,
    source_path: str,
    digest: str,
    byte_size: int,
    size: tuple[int, int],
    path_literal_va: int,
    raw_handle_va: int,
    wrapper_va: int,
    direct_consumer_vas: tuple[int, ...] = (),
    direct_consumer_handle: str | None = None,
) -> OriginalPMatchInfoResource:
    return OriginalPMatchInfoResource(
        name,
        source_path,
        digest,
        byte_size,
        size,
        path_literal_va,
        raw_handle_va,
        wrapper_va,
        direct_consumer_vas,
        direct_consumer_handle,
    )


PMATCHINFO_RESOURCES = (
    _r(
        "info_player",
        "FM2001_Art/Generic/match_report/info_player.444",
        "c128d82caadb24ec932c0786e5b6b714c08f63fe1acad01c9f0ff6b459ac1033",
        4688, (274, 16), 0x837E9C, 0x943570, 0x943550, (0x4838AC,), "wrapper",
    ),
    _r(
        "info_player_disabled",
        "FM2001_Art/Generic/match_report/info_player_disabled.444",
        "537ab4f3f36a9246838e84f33a520d0fd26ec818b160a9fcae891b929cee2f34",
        3972, (274, 16), 0x837ECC, 0x943530, 0x943510, (0x483A81,), "wrapper",
    ),
    _r(
        "info_popup",
        "FM2001_Art/Generic/match_report/info_popup.444",
        "d4bcf7d57b5e38de01d43e214d937045529e6434d1c40bb0f04620753c18f5e6",
        179988, (760, 500), 0x837F08, 0x9434F0, 0x9434D0, (0x484FFF,), "raw",
    ),
    _r(
        "red_card",
        "FM2001_Art/Generic/match_report/red_card.444",
        "215c223e62062f7f61745f6f72a85e25459becd4b2f05f8164997664f51ef019",
        688, (14, 14), 0x837F38, 0x9434B0, 0x943490, (0x485A50, 0x4860C0), "wrapper",
    ),
    _r(
        "yellow_card",
        "FM2001_Art/Generic/match_report/yellow_card.444",
        "b6b13283b398da35cc7af76a8f1d8a2327e9445397efba1766753c3ee6891ff8",
        724, (14, 14), 0x837F68, 0x943470, 0x943450, (0x48366D, 0x485A24, 0x486094), "wrapper",
    ),
    _r(
        "sub_on",
        "FM2001_Art/Generic/match_report/Sub_on.444",
        "cee9c2b9b17834606d9414d9c04f8a1f0e1f7ee621f9d2695c7f45e4d4b28fe1",
        528, (14, 14), 0x837F98, 0x943430, 0x943410, (0x485A81, 0x4860F1), "wrapper",
    ),
    _r(
        "sub_off",
        "FM2001_Art/Generic/match_report/sub_off.444",
        "5f9837e6444eb1d724d0e845ac0f70d02180f1d3a6d7a4c9a3d45bef0598eb32",
        576, (14, 14), 0x837FC4, 0x9433F0, 0x9433D0, (0x485A9E, 0x48610E), "wrapper",
    ),
    _r(
        "injured",
        "FM2001_Art/Generic/match_report/injured.444",
        "ab0820167dd7ebf2840906a16beaec7b8895202a3f6be77995eab94b33dfc41f",
        736, (14, 14), 0x837FF0, 0x9433B0, 0x943390, (0x4859FD, 0x48606D), "wrapper",
    ),
    _r(
        "score",
        "FM2001_Art/Generic/match_report/score.444",
        "49b2ef946e1934d25ab23cb30e35035ef0c6c0bf07eee950ba5b676d01d9bcae",
        700, (14, 14), 0x83801C, 0x943370, 0x943350, (0x4859D5, 0x486045), "wrapper",
    ),
    _r(
        "red_card_single",
        "FM2001_Art/Generic/match_report/red_card_single.444",
        "f5f721db52098a1a9b14ddac30c76265e478e49ee53db09ab0f2d1e04656ee25",
        700, (14, 14), 0x838048, 0x943330, 0x943310, (0x485A5C, 0x4860CC), "wrapper",
    ),
    _r(
        "name_block_1",
        "FM2001_Art/Generic/match_report/name_block_1.444",
        "79a1eddbdd497992aa85f564269b396dbc6bf00eee95eca280e3e4268f81c832",
        3528, (195, 36), 0x83807C, 0x9432F0, 0x9432D0,
    ),
    _r(
        "name_block_2",
        "FM2001_Art/Generic/match_report/name_block_2.444",
        "aa4b9e3976d6f84a74bd0bc60bd4cd64701e2bd5bae68ce282b6ca9eed462272",
        3228, (195, 36), 0x8380B0, 0x9432B0, 0x943290,
    ),
    _r(
        "name_block_3",
        "FM2001_Art/Generic/match_report/name_block_3.444",
        "fedd753e3eba4dcc125af7493401e2f0371636856a9a6f4814e243e896c3b24c",
        3536, (195, 36), 0x8380E4, 0x943270, 0x943250,
    ),
    _r(
        "name_block_4",
        "FM2001_Art/Generic/match_report/name_block_4.444",
        "9b1f5e3dc6eb4099cef0be89038cd2776035c0e9c95bf8751f361a44d927a211",
        3212, (195, 36), 0x838118, 0x943230, 0x943210,
    ),
    _r(
        "match_name_grid",
        "FM2001_Art/Generic/match_report/match_name_grid.444",
        "03ee3fca92ce681dbf8d4c2a00958bc00447a15822c5efaf6341073609dfc068",
        3036, (185, 36), 0x83814C, 0x9431F0, 0x9431D0, (0x483541, 0x483784), "raw",
    ),
    _r(
        "poss_back",
        "FM2001_Art/Generic/match_report/poss_back.444",
        "e8090259d1f38e13f22918475a8057a9ffd29145d7d6950dd214cb16982b7392",
        7140, (294, 25), 0x838180, 0x9431B0, 0x943190,
    ),
    _r(
        "poss_blue",
        "FM2001_Art/Generic/match_report/poss_blue.444",
        "18a440005bfc980aadf30be1ce583c2cc089d6a5c7b38d0ac08aa1e89a852119",
        8372, (264, 21), 0x8381B0, 0x943170, 0x943150,
    ),
    _r(
        "poss_yellow",
        "FM2001_Art/Generic/match_report/poss_yellow.444",
        "396cfe3a52263e3c24ab59b3d4f240e42c408afc9182125eb967ef5d56570c94",
        7976, (264, 21), 0x8381E0, 0x943130, 0x943110,
    ),
    _r(
        "pitch_normal",
        "FM2001_Art/Generic/match_report/pitch_normal.444",
        "73f6c0ecc57a383c63288064c371f947772f584800dfd3f4d2b1323063d9a6ba",
        15932, (294, 78), 0x838210, 0x9430F0, 0x9430D0, (0x483B1E,), "raw",
    ),
    _r(
        "match_incid_grid",
        "FM2001_Art/Generic/match_report/match_incid_grid.444",
        "0d7ba8c3de23ac24f0610233eb9381b0e5a7e620299acd52781a27966f8c50f3",
        2788, (142, 36), 0x838244, 0x9430B0, 0x943090, (0x4835AD, 0x4837EC), "raw",
    ),
)

PMATCHINFO_RESOURCE_BY_NAME = {resource.name: resource for resource in PMATCHINFO_RESOURCES}


def validate_original_pmatchinfo_resources(
    source_root: Path,
) -> tuple[OriginalPMatchInfoResource, ...]:
    """Require all exact firsthand-verified PMatchInfo Match_report files."""
    root = Path(source_root)
    for resource in PMATCHINFO_RESOURCES:
        path = root / resource.source_path
        try:
            data = path.read_bytes()
        except FileNotFoundError as exc:
            raise OriginalPMatchInfoResourceError(
                f"Missing original PMatchInfo resource: {resource.source_path}"
            ) from exc
        if len(data) != resource.byte_size:
            raise OriginalPMatchInfoResourceError(
                f"PMatchInfo byte-size mismatch: {resource.source_path}"
            )
        if sha256(data).hexdigest() != resource.sha256:
            raise OriginalPMatchInfoResourceError(
                f"PMatchInfo checksum mismatch: {resource.source_path}"
            )
        header = parse_ea444_header(data)
        if (header.width, header.height) != resource.size:
            raise OriginalPMatchInfoResourceError(
                f"PMatchInfo geometry mismatch: {resource.source_path}"
            )
    return PMATCHINFO_RESOURCES


def assert_pmatchinfo_identity_contract() -> None:
    """Guard the PMatchInfo identity already proven by populated fixture navigation."""
    if (
        LEAGUE_FIXTURES_MATCH_INFO_CLASS != "PMatchInfo"
        or LEAGUE_FIXTURES_MATCH_INFO_TYPE_DESCRIPTOR_VA != 0x81D058
        or LEAGUE_FIXTURES_MATCH_INFO_VFTABLE_VA != 0x7C41D4
        or LEAGUE_FIXTURES_MATCH_INFO_CONSTRUCTOR_VA != 0x487580
    ):
        raise OriginalPMatchInfoResourceError(
            "PMatchInfo resources require the source-proven PMatchInfo RTTI contract"
        )
