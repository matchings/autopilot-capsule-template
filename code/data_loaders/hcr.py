"""Load HCR spatial-transcriptomics outputs.

Two HCR assets in this capsule:

1. cell-types-and-learning_HCR-cell-typing-tables  (INTERNAL, small)
   Per-subject files: <subject>_cell_typing_table.csv
   Columns: cell_id, mouse_id, leiden_subclass, leiden_assignment,
            leiden_confidence, mapmycells_class_name, mapmycells_subclass_name,
            mapmycells_supertype_name, mapmycells_cluster_name, ... (+ probs)
   Mice: 782149, 788406, 790322, 800792, 800995, 804363

2. cell-types-and-learning_pairwise-unmixing-assets-combined  (EXTERNAL/GCP, ~317 GB)
   Unmixed cell-by-gene tables (transcript counts) for the same 6 mice.
   TODO: confirm exact per-mouse file names/layout once the asset is mounted
   (file API was forbidden from outside the capsule). `find_unmixing_tables()`
   uses best-effort globbing.
"""
from __future__ import annotations
from pathlib import Path
from . import paths

CELLTYPE_KEYS = [
    "leiden_subclass", "leiden_assignment",
    "mapmycells_subclass_name", "mapmycells_class_name",
    "mapmycells_supertype_name", "mapmycells_cluster_name",
]


def find_cell_typing_tables() -> list[Path]:
    """The <subject>_cell_typing_table.csv files (internal asset)."""
    hits: list[Path] = []
    for asset in paths.find_assets("cell-typing") + paths.find_assets("cell_typing"):
        hits += paths.find_files("*cell_typing_table.csv", asset)
    return sorted(set(hits))


def load_cell_typing(subject: "str | None" = None):
    """Load cell-typing table(s). If subject given, that mouse only; else concat all."""
    import pandas as pd
    tables = find_cell_typing_tables()
    if subject is not None:
        tables = [t for t in tables if str(subject) in t.name]
    dfs = [pd.read_csv(t) for t in tables]
    return pd.concat(dfs, ignore_index=True) if dfs else None


def find_unmixing_tables() -> list[Path]:
    """Cell-by-gene unmixed transcript-count tables (combined external asset)."""
    hits: list[Path] = []
    for asset in paths.find_assets("unmix"):
        for pat in ("*cell_by_gene*.csv", "*unmix*filtered*.csv", "*cellxgene*.csv",
                    "*.parquet", "*cell_by_gene*.parquet"):
            hits += paths.find_files(pat, asset)
    return sorted(set(hits))


def load_cellxgene(path):
    """Load a cell-by-gene table (CSV or parquet) into a DataFrame."""
    import pandas as pd
    path = Path(path)
    return pd.read_parquet(path) if path.suffix == ".parquet" else pd.read_csv(path)
