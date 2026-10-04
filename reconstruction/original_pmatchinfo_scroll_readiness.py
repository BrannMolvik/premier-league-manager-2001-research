"""Fail-closed Gate-13 PMatchInfo scroll-resource readiness inventory.

This module records only source-backed loader/resource facts already recovered
for the default PMatchInfo vertical scroll family. It deliberately does not
infer thumb geometry, bar tiling, x87 range rounding, hover semantics, held
repeat timing, wheel behavior, or drag behavior.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path


@dataclass(frozen=True)
class PMatchInfoScrollResourceLead:
    name: str
    source_path: str
    loader_va: int
    staged_sha256: str | None = None
    staged_size_bytes: int | None = None

    @property
    def has_staged_identity(self) -> bool:
        return self.staged_sha256 is not None and self.staged_size_bytes is not None


PMATCHINFO_SCROLL_RESOURCE_LEADS = (
    PMatchInfoScrollResourceLead(
        "arrow_atlas",
        "FM2001_Art/Generic/GenericButtonsAndBars/scroller_vert.444",
        0x5F2BC0,
        "3f96ef29d80c7d369f65236c29ae8281b7e490c3c71a65644490daefe5f1f9f7",
        5696,
    ),
    PMatchInfoScrollResourceLead(
        "bar_vertical",
        "FM2001_Art/Generic/GenericButtonsAndBars/scroller_bar_vert.444",
        0x5F2DA0,
    ),
    PMatchInfoScrollResourceLead(
        "bar_blue",
        "FM2001_Art/Generic/GenericButtonsAndBars/scroller_blue_bar.444",
        0x5F2E30,
    ),
    PMatchInfoScrollResourceLead(
        "end_vertical",
        "FM2001_Art/Generic/GenericButtonsAndBars/vscroll_end.444",
        0x5F2E80,
        "c05393b27221b8951b15fcc4e096290851e9414020ae2e94091c18a66a110783",
        20,
    ),
    PMatchInfoScrollResourceLead(
        "thumb_blue",
        "FM2001_Art/Generic/GenericButtonsAndBars/vscroll_blue_bar.444",
        0x5F2F10,
    ),
)

PMATCHINFO_SCROLL_DESCRIPTOR_VA = 0x946FB0
PMATCHINFO_SCROLL_DESCRIPTOR_SOURCE_SIZE = (18, 25)
PMATCHINFO_SCROLL_DESCRIPTOR_FLAGS = 0x0D
PMATCHINFO_SCROLL_RENDERER_GLOBAL_VA = 0x87BEE8
PMATCHINFO_SCROLL_RENDERER_VFTABLE_VA = 0x7D7AB8
PMATCHINFO_SCROLL_RENDERER_DRAW_SLOT_OFFSET = 0x08
PMATCHINFO_SCROLL_RENDERER_DRAW_VA = 0x64EBE0
PMATCHINFO_SCROLL_RENDERER_CAP_INPUTS = (3, 3)

PMATCHINFO_SCROLL_IMPORT_ROOT = Path("original_assets/source")


def audit_pmatchinfo_scroll_resource_readiness(repo_root: str | Path) -> dict:
    """Report exact staged-vs-pending resource state without behavior claims."""
    root = Path(repo_root)
    present: list[str] = []
    missing: list[str] = []
    verified: list[str] = []
    identity_unverified: list[str] = []

    for lead in PMATCHINFO_SCROLL_RESOURCE_LEADS:
        path = root / PMATCHINFO_SCROLL_IMPORT_ROOT / lead.source_path
        if not path.is_file():
            missing.append(lead.name)
            continue
        present.append(lead.name)
        if not lead.has_staged_identity:
            identity_unverified.append(lead.name)
            continue
        data = path.read_bytes()
        if len(data) != lead.staged_size_bytes:
            raise ValueError(
                f"PMatchInfo scroll resource size mismatch for {lead.source_path}"
            )
        if sha256(data).hexdigest() != lead.staged_sha256:
            raise ValueError(
                f"PMatchInfo scroll resource checksum mismatch for {lead.source_path}"
            )
        verified.append(lead.name)

    pending = [
        lead.name
        for lead in PMATCHINFO_SCROLL_RESOURCE_LEADS
        if lead.name not in verified
    ]
    return {
        "schema_version": 1,
        "source_backed_resource_names": [
            lead.name for lead in PMATCHINFO_SCROLL_RESOURCE_LEADS
        ],
        "present_resource_names": present,
        "verified_staged_resource_names": verified,
        "missing_resource_names": missing,
        "present_but_identity_unverified_resource_names": identity_unverified,
        "pending_resource_names": pending,
        "resource_inventory_complete": not pending,
        "native_scroll_behavior_recovered": False,
        "renderer_geometry_recovered": False,
        "evidence_limit": (
            "Loader/resource identities and existing staged-byte checks only. "
            "No thumb geometry, composite blit, range arithmetic, hover, repeat, "
            "wheel or drag behavior is inferred."
        ),
    }
