"""Data loaders for the multimodal ANID dataset (ophys + behavior + HCR).

Modules
-------
paths     : discover mounted data assets under /root/capsule/data
behavior  : change-detection behavior NWBs + session manifests
ophys     : in vivo multiplane mesoscope processed NWB (dF/F traces)
hcr       : HCR cell-typing tables + pairwise-unmixing cell-by-gene tables
linking   : join in vivo ROIs to HCR cell identities via coregistration

xenium    : STUB — excluded from this capsule (see module docstring to re-enable)
"""
from . import paths, behavior, ophys, hcr, linking  # noqa: F401
