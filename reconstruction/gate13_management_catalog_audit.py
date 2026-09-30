from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from typing import Iterable

from gate13_catalog_query import query_source_files


@dataclass(frozen=True)
class ManagementCatalogQuery:
    surface: str
    regex: str
    evidence_boundary: str


# These expressions are discovery terms only. A path match is never promoted to
# an original control, panel, layout or navigation binding without independent
# executable/resource evidence.
MANAGEMENT_CATALOG_QUERIES: tuple[ManagementCatalogQuery, ...] = (
    ManagementCatalogQuery(
        "main_menu_teamselect_reference",
        r"(main[_ -]?menu|team[_ -]?(choice|select)|choice_start|button)",
        "known first-screen reference family; binding still requires exact source evidence",
    ),
    ManagementCatalogQuery(
        "manager_home",
        r"(manager|home|overview|main[_ -]?panel)",
        "no persisted original Manager Home panel identity",
    ),
    ManagementCatalogQuery(
        "squad",
        r"(squad|roster|team[_ -]?(sheet|list)|player[_ -]?list)",
        "ordered roster backend is proven; distinct general Squad panel is not",
    ),
    ManagementCatalogQuery(
        "tactics_team_selection",
        r"(formation|tactic|team[_ -]?order|set[_ -]?piece)",
        "PFormation2k/PTeamOrders2K identities are partial presentation anchors",
    ),
    ManagementCatalogQuery(
        "fixtures_results",
        r"(fixture|result|season|calendar|match[_ -]?(list|day))",
        "fixture backend is proven; original Fixtures/Results panel identity is not",
    ),
    ManagementCatalogQuery(
        "league_table",
        r"(league[_ -]?table|standings?|table[_ -]?(header|row)|league)",
        "native League comparator is proven; original table panel identity is not",
    ),
    ManagementCatalogQuery(
        "player_profile",
        r"(player[_ -]?(profile|info|history|stat)|profile)",
        "DBTPlayers/DBRPlayer identity is proven; original profile panel is not",
    ),
    ManagementCatalogQuery(
        "transfers",
        r"(transfer|contract|offer|bid|negotiat)",
        "PTransfer2K family is proven; resource/layout/control bindings are not",
    ),
    ManagementCatalogQuery(
        "finances",
        r"(finance|balance|ticket|stadium|ground|cash|budget)",
        "PFinanceOverview/PTickets families are proven; visual bindings are not",
    ),
    ManagementCatalogQuery(
        "messages_news",
        r"(mail|message|news|inbox)",
        "MPMEAMail is a queue/event family, not a proven inbox panel",
    ),
    ManagementCatalogQuery(
        "training",
        r"(train)",
        "Training.cpp behavior is proven; original Training panel identity is not",
    ),
    ManagementCatalogQuery(
        "scouting",
        r"(scout)",
        "PScouting2K identity is proven; visual/control bindings are not",
    ),
    ManagementCatalogQuery(
        "support_youth_leads",
        r"(support|staff|youth)",
        "feature-family leads only; no screen identity is implied",
    ),
)


def _selected_queries(surfaces: Iterable[str] | None) -> tuple[ManagementCatalogQuery, ...]:
    if surfaces is None:
        return MANAGEMENT_CATALOG_QUERIES
    wanted = tuple(surfaces)
    known = {item.surface for item in MANAGEMENT_CATALOG_QUERIES}
    unknown = [value for value in wanted if value not in known]
    if unknown:
        raise ValueError(
            "Unknown management catalog surface(s): " + ", ".join(sorted(set(unknown)))
        )
    wanted_set = set(wanted)
    return tuple(item for item in MANAGEMENT_CATALOG_QUERIES if item.surface in wanted_set)


def audit_management_catalog(
    report: dict,
    *,
    layer: str = "disc",
    surfaces: Iterable[str] | None = None,
) -> dict:
    """Return path-name discovery candidates without claiming source bindings.

    The default is the nested disc catalog because the outer ZIP is a
    three-member transport wrapper whose directory name contains Football
    Manager, which would create noisy manager-name matches. Callers may still
    explicitly request the zip or both layers when auditing archive layers.
    """

    if layer not in {"disc", "zip", "both"}:
        raise ValueError(f"Unsupported source catalog layer: {layer}")

    groups = []
    for item in _selected_queries(surfaces):
        matches = query_source_files(report, layer=layer, regex=item.regex)
        groups.append(
            {
                "surface": item.surface,
                "query_regex": item.regex,
                "evidence_boundary": item.evidence_boundary,
                "binding_proven": False,
                "candidate_count": len(matches),
                "matches": matches,
            }
        )

    return {
        "schema_version": 1,
        "source_layer": layer,
        "candidate_semantics": (
            "filename/path discovery only; every original panel/control/layout/"
            "navigation binding requires independent evidence"
        ),
        "screen_queries": groups,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Group Gate-13 source-catalog path candidates by management-screen "
            "family without claiming any original UI binding."
        )
    )
    parser.add_argument("report")
    parser.add_argument(
        "--layer",
        choices=("disc", "zip", "both"),
        default="disc",
        help="Source layer to query. Defaults to the nested disc filesystem.",
    )
    parser.add_argument(
        "--surface",
        action="append",
        default=None,
        help=(
            "Limit output to one named surface. Repeat for multiple surfaces. "
            "Omit to audit every configured family."
        ),
    )
    args = parser.parse_args()

    with open(args.report, "r", encoding="utf-8") as handle:
        report = json.load(handle)

    try:
        result = audit_management_catalog(
            report,
            layer=args.layer,
            surfaces=args.surface,
        )
    except ValueError as exc:
        parser.error(str(exc))

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
