"""Load in vivo multiplane mesoscope calcium imaging (processed NWB).

Asset: cell-types-and-learning_ophys-processed-assets-combined (EXTERNAL, ~53 TB).
Combined processed multiplane-ophys. Each session corresponds to a behavior
session via behavior `asset_name` == the ophys session asset name
(e.g. multiplane-ophys_<subject>_<date>_<time>).

The file API was forbidden from outside the capsule, so exact interface names
are confirmed at runtime. `get_dff_traces` tries the common AIND/allen module
names; adjust if your pipeline differs.
"""
from __future__ import annotations
from pathlib import Path
from . import paths


def find_ophys_nwb(subject: "str | None" = None) -> list[Path]:
    hits: list[Path] = []
    for asset in paths.find_assets("ophys"):
        if subject and subject not in asset.name:
            # subject may only appear on the session subdir, so also glob inside
            pass
        hits += paths.find_files("*.nwb", asset)
    if subject:
        hits = [p for p in hits if subject in str(p)]
    return sorted(set(hits))


def open_nwb(nwb_path):
    from pynwb import NWBHDF5IO
    io = NWBHDF5IO(str(nwb_path), mode="r", load_namespaces=True)
    return io.read(), io


def get_dff_traces(nwbfile):
    """Return (roi_ids, dff[n_roi, n_time], timestamps). Adjust names if needed."""
    proc = nwbfile.processing
    for mod_name in ("ophys", "processing", "brain_observatory_pipeline"):
        if mod_name in proc:
            mod = proc[mod_name]
            for key in ("DfOverF", "Fluorescence", "dff"):
                if key in mod.data_interfaces:
                    rrs = mod.data_interfaces[key].roi_response_series
                    series = next(iter(rrs.values()))
                    data = series.data[:]
                    ts = series.timestamps[:] if series.timestamps is not None else None
                    roi_ids = list(series.rois.table.id[:])
                    if data.shape[0] != len(roi_ids):
                        data = data.T
                    return roi_ids, data, ts
    raise KeyError("No DfOverF/Fluorescence interface found; inspect nwbfile.processing")
