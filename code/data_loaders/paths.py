"""Discover mounted Code Ocean data assets without hardcoding IDs/paths.

Code Ocean mounts each attached data asset as a subdirectory of `data/`
(default /root/capsule/data). This module finds assets by naming pattern so the
same code works across subjects and re-mounts.

Assets in this capsule
----------------------
  hcr_celltyping   : <subject>_cell_typing_table.csv  (internal)
  hcr_unmixing     : combined pairwise-unmixing cell-by-gene tables
  coreg            : in vivo ROI <-> post-hoc cell-id mapping
  ophys_processed  : combined multiplane-ophys processed (NWB, very large)
  behavior_nwb     : <session_id>.nwb + .events.json + .metadata.json (flat)
"""
from __future__ import annotations
import os, glob, re
from pathlib import Path

DATA_ROOT = Path(os.environ.get("CO_DATA_ROOT", "/root/capsule/data"))


def list_assets() -> list[Path]:
    if not DATA_ROOT.exists():
        return []
    return sorted(p for p in DATA_ROOT.iterdir() if p.is_dir())


def find_assets(*substrings: str) -> list[Path]:
    """Mounted assets whose directory name contains ALL substrings (case-insensitive)."""
    subs = [s.lower() for s in substrings]
    return [p for p in list_assets() if all(s in p.name.lower() for s in subs)]


def find_files(pattern: str, asset: "Path | None" = None) -> list[Path]:
    base = asset if asset is not None else DATA_ROOT
    return [Path(p) for p in glob.glob(str(base / "**" / pattern), recursive=True)]


def subject_id_from_name(name: str) -> "str | None":
    m = re.search(r"(?<!\d)(\d{6})(?!\d)", name)
    return m.group(1) if m else None


def inventory() -> "dict[str, list[str]]":
    groups = {"behavior": [], "ophys": [], "hcr_celltyping": [],
              "hcr_unmixing": [], "coreg": [], "other": []}
    for p in list_assets():
        n = p.name.lower()
        if "behavior" in n or "change_detection" in n:
            groups["behavior"].append(p.name)
        elif "ophys" in n or "meso" in n or "pophys" in n:
            groups["ophys"].append(p.name)
        elif "celltyping" in n or "cell-typing" in n or "cell_typing" in n:
            groups["hcr_celltyping"].append(p.name)
        elif "unmix" in n:
            groups["hcr_unmixing"].append(p.name)
        elif "coreg" in n:
            groups["coreg"].append(p.name)
        else:
            groups["other"].append(p.name)
    return groups
