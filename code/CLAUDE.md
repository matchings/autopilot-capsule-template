# Repository guidance for Claude Code (agent mode)

You are working inside a Code Ocean capsule. Use the `codeocean-capsule` skill.

## Reproducibility
- Write outputs only to `results/` (unlimited storage; anything else is lost at exit).
- Always dump the code used to generate outputs to `results/code/`.

## This capsule
- Multimodal Allen Institute for Neural Dynamics "cell types and learning" dataset:
  - in vivo multiplane mesoscope calcium imaging (processed NWB)
  - change-detection behavior (NWB + session manifests)
  - HCR spatial transcriptomics (cell-typing tables + pairwise-unmixing gene counts)
  - coregistration mapping linking in vivo ROIs to post-hoc HCR cells
  (Xenium is intentionally excluded from this capsule.)
- Data assets are mounted read-only under `data/`. Loader utilities live in
  `code/data_loaders/`. Prefer those over ad-hoc file parsing.
- Never hardcode subject IDs or paths that only exist in one person's checkout;
  discover them from the mounted assets via `data_loaders.paths`.

## Style
- Python, PEP 8, type hints where practical.
- Keep functions small and documented.
