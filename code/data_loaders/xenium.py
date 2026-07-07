"""Xenium loader — STUB (not used in this capsule).

Xenium was intentionally excluded from this capsule. This stub is left as a
placeholder so a Xenium modality can be added later without restructuring.

To re-enable:
  1. Attach the Xenium output asset(s) to the capsule (mount under data/).
  2. Restore a real loader here (cell_feature_matrix.h5 -> AnnData, transcripts
     table, cell metadata) and add "xenium" back to paths.inventory().
  3. Add a 0X_load_xenium notebook.

Reference: standard Xenium bundle files are
  cells.parquet / cells.csv.gz           cell metadata (centroids, area)
  cell_feature_matrix.h5                  cell-by-gene counts
  transcripts.parquet                     per-molecule transcripts
  cell_boundaries.parquet                 segmentation polygons
"""

# Intentionally no functions. See the module docstring to re-enable Xenium.
