"""Link modalities: in vivo ophys ROIs <-> HCR transcriptomic cell identities.

Join chain
----------
  behavior.session -> asset_name (ophys asset) + subject_id           [behavior manifest]
  ophys ROI id     <-> post-hoc HCR cell_id                           [coreg mapping asset]
  HCR cell_id + mouse_id -> subclass / gene counts                    [hcr cell-typing / unmixing]

The coreg asset (cell-types-and-learning_coreg-id-mapping-assets-combined) was
not listable from outside the capsule, so the exact column names are confirmed
at runtime. `link_ophys_to_celltype` auto-guesses the ROI and cell-id columns
and can be overridden.
"""
from __future__ import annotations
from pathlib import Path
from . import paths, hcr


def find_coreg_tables() -> list[Path]:
    hits: list[Path] = []
    for asset in paths.find_assets("coreg"):
        for pat in ("*coreg*.csv", "*mapping*.csv", "*matched*.csv",
                    "*.parquet", "*.csv"):
            hits += paths.find_files(pat, asset)
    return sorted(set(hits))


def load_coreg(path):
    import pandas as pd
    path = Path(path)
    return pd.read_parquet(path) if path.suffix == ".parquet" else pd.read_csv(path)


def _guess(df, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    return None


def link_ophys_to_celltype(dff_roi_ids, coreg_df, celltype_df=None,
                           subject=None, roi_col=None, cell_col=None,
                           celltype_key="leiden_subclass"):
    """Annotate each in vivo ROI with its HCR transcriptomic subclass.

    Parameters
    ----------
    dff_roi_ids : ROI ids from ophys.get_dff_traces
    coreg_df    : coregistration mapping table (ROI <-> HCR cell_id)
    celltype_df : HCR cell-typing DataFrame; if None, loaded via hcr.load_cell_typing(subject)
    subject     : mouse id, used to load cell typing if celltype_df is None
    roi_col/cell_col : coreg column names (auto-guessed if None)
    celltype_key     : which cell-typing column to attach (default leiden_subclass)
    """
    import pandas as pd
    if celltype_df is None:
        celltype_df = hcr.load_cell_typing(subject)

    roi_col = roi_col or _guess(coreg_df, ["roi_id", "invivo_roi_id",
                                           "cell_specimen_id", "roi", "ophys_roi_id"])
    cell_col = cell_col or _guess(coreg_df, ["cell_id", "hcr_cell_id",
                                             "posthoc_cell_id", "matched_cell_id"])
    if roi_col is None or cell_col is None:
        raise ValueError(f"Could not infer coreg join columns; columns = {list(coreg_df.columns)}")

    out = (pd.DataFrame({roi_col: list(dff_roi_ids)})
           .merge(coreg_df[[roi_col, cell_col]], on=roi_col, how="left"))
    if celltype_df is not None and "cell_id" in celltype_df.columns:
        keep = ["cell_id"] + [k for k in ([celltype_key] if isinstance(celltype_key, str)
                                          else celltype_key) if k in celltype_df.columns]
        out = out.merge(celltype_df[keep].rename(columns={"cell_id": cell_col}),
                        on=cell_col, how="left")
    return out
