"""Load change-detection behavior NWBs.

Asset `change_detection_behavior_nwb_v1` currently has a FLAT layout at the
asset root:
    <session_id>.nwb
    <session_id>.events.json
    <session_id>.metadata.json
plus two manifest CSVs:
    session_metrics.csv          (per-session summary metrics; 53 columns)
    session_task_parameters.csv  (per-session task parameters; 46 columns)

NOTE (per data owner): this asset is expected to be REPLACED by a better-
organized version where each session's files live in their own folder alongside
a data_description.json. `find_session_nwbs()` already globs recursively, so it
will keep working after that reorg; `load_manifest()` looks for the CSVs
anywhere under the asset.

Key manifest columns for linking:
    session_id      unique session id (matches the .nwb basename)
    asset_name      the corresponding ophys processed asset name
                    (e.g. multiplane-ophys_755252_2024-11-12_09-43-51)
    subject_id      mouse id (ties to HCR mouse_id)
    session_type    e.g. OPHYS_1_images_A, TRAINING_1_gratings
"""
from __future__ import annotations
from pathlib import Path
from . import paths


def behavior_asset() -> "Path | None":
    hits = paths.find_assets("behavior") or paths.find_assets("change_detection")
    return hits[0] if hits else None


def find_session_nwbs() -> list[Path]:
    """All behavior session NWB files (works for flat or per-folder layouts)."""
    asset = behavior_asset()
    if asset is None:
        return []
    return sorted(paths.find_files("*.nwb", asset))


def load_manifest():
    """Return (metrics_df, task_params_df) from the manifest CSVs, or (None, None)."""
    import pandas as pd
    asset = behavior_asset()
    if asset is None:
        return None, None
    def _find(name):
        f = paths.find_files(name, asset)
        return pd.read_csv(f[0]) if f else None
    return _find("session_metrics.csv"), _find("session_task_parameters.csv")


def load_session_metadata(session_id: str):
    """Load the per-session <session_id>.metadata.json sidecar as a dict."""
    import json
    asset = behavior_asset()
    if asset is None:
        return None
    f = paths.find_files(f"{session_id}.metadata.json", asset)
    return json.load(open(f[0])) if f else None


def open_nwb(nwb_path):
    """Open a behavior NWB; returns (nwbfile, io). Caller closes io."""
    from pynwb import NWBHDF5IO
    io = NWBHDF5IO(str(nwb_path), mode="r", load_namespaces=True)
    return io.read(), io


def sessions_for_subject(subject_id: str) -> list[str]:
    """Session ids belonging to one subject, from the metrics manifest."""
    metrics, _ = load_manifest()
    if metrics is None:
        return []
    sel = metrics[metrics["subject_id"].astype(str) == str(subject_id)]
    return sel["session_id"].astype(str).tolist()
