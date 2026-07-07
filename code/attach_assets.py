#!/usr/bin/env python3
"""Attach this dataset's data assets to a capsule at organized mount paths.

Run this ONCE after you create the empty capsule (it needs the capsule id).
It uses the Code Ocean MCP connector via Claude Science, OR the codeocean
Python SDK if you run it inside a capsule/locally with CODEOCEAN_DOMAIN + token.

Because the Claude Science connector has no create_capsule method, you create
the capsule in the UI first, then paste its id here.

Assets (Xenium intentionally excluded):
"""
ASSETS = [
    # (data_asset_id, mount_path, description)
    ("3380552b-5120-4c7a-be4e-81e08dc86323", "behavior",       "change_detection_behavior_nwb_v1 (357 sessions)"),
    ("d40dc38d-1403-405b-a066-5517134ecea9", "ophys",          "ophys-processed-assets-combined (~53 TB)"),
    ("0f4bc4b0-fa1d-4da0-9b55-e0cc79edadf1", "hcr_celltyping", "HCR-cell-typing-tables (6 mice)"),
    ("1d52b97f-6241-412b-b658-235c93942927", "hcr_unmixing",   "pairwise-unmixing-assets-combined (~317 GB)"),
    ("f59062ef-9f80-4233-91b8-f74abe77949a", "coreg",          "coreg-id-mapping-assets-combined"),
]

def attach_params():
    """Return the attach_params list for codeocean attach_data_assets."""
    return [{"id": aid, "mount": mount} for aid, mount, _ in ASSETS]

if __name__ == "__main__":
    import os, sys
    try:
        from codeocean import CodeOcean
        from codeocean.data_asset import DataAssetAttachParams
    except ImportError:
        sys.exit("pip install codeocean, or run attach via the Claude Science connector "
                 "(host.mcp('codeocean','attach_data_assets', capsule_id=..., attach_params=...)).")
    domain = os.environ["CODEOCEAN_DOMAIN"]; token = os.environ["CODEOCEAN_TOKEN"]
    capsule_id = sys.argv[1] if len(sys.argv) > 1 else sys.exit("usage: attach_assets.py <capsule_id>")
    client = CodeOcean(domain=domain, token=token)
    params = [DataAssetAttachParams(id=aid, mount=mount) for aid, mount, _ in ASSETS]
    client.capsules.attach_data_assets(capsule_id=capsule_id, attach_params=params)
    print(f"Attached {len(params)} assets to {capsule_id}")
