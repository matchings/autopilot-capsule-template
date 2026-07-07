git status# Cell Types and Learning — multimodal data capsule

A Code Ocean capsule for exploring the Allen Institute for Neural Dynamics
**"cell types and learning"** dataset: longitudinal in vivo calcium imaging during
a visual change-detection task, linked by post-hoc coregistration to HCR spatial
transcriptomics cell-type identities.

It is built to be an **easy-to-use shared resource first**: notebooks and
interactive analysis need no accounts or keys. An **optional autonomous agent**
(Claude Code) is available for advanced users who want it.

---

## Quick start (no account, no key)

1. Open the capsule and start a **VS Code** or **JupyterLab** cloud workstation.
2. Open `code/notebooks/00_data_inventory.ipynb` and run it — it lists the mounted
   data assets and confirms everything is attached.
3. Work through `01`–`04` to load each modality and link them.

That's it. Interactive analysis uses only the mounted data and the Python
environment. **No Anthropic API key is required for any of this.**

---

## What's in the dataset

Five data assets are attached (mounted read-only under `data/<mount>`):

| Mount | Asset | Contents |
|-------|-------|----------|
| `data/behavior/`       | `change_detection_behavior_nwb_v1` | 357 change-detection sessions as `<session_id>.nwb` + `.events.json` + `.metadata.json`, plus `session_metrics.csv` and `session_task_parameters.csv` manifests |
| `data/ophys/`          | `ophys-processed-assets-combined`  | Combined processed multiplane-mesoscope imaging (NWB) |
| `data/hcr_celltyping/` | `HCR-cell-typing-tables`           | Per-subject `<subject>_cell_typing_table.csv`: Leiden subclass + MapMyCells labels. Mice 782149, 788406, 790322, 800792, 800995, 804363 |
| `data/hcr_unmixing/`   | `pairwise-unmixing-assets-combined`| Unmixed cell-by-gene transcript-count tables (same 6 mice) |
| `data/coreg/`          | `coreg-id-mapping-assets-combined` | Mapping from in vivo ROIs to post-hoc HCR cell ids |

> **Note on the behavior asset:** it currently has a *flat* layout (all files at the
> asset root). It is expected to be replaced by a version with one folder per session
> plus `data_description.json`. The loaders glob recursively, so they keep working
> after that reorganization.

> **Xenium** is intentionally **excluded** from this capsule. A commented stub is left
> in `code/data_loaders/xenium.py` if you want to add it later.

### How the modalities link

```
behavior session ──(manifest: asset_name, subject_id)──▶ ophys session asset
        │                                                        │
   subject_id                                              in vivo ROI id
        │                                                        │
        ▼                                                        ▼
  HCR mouse_id ◀──(cell_id + mouse_id)── HCR cell typing ◀─(coreg)─ post-hoc cell_id
```

`code/notebooks/04_link_modalities.ipynb` walks this chain end to end.

---

## The loaders

`code/data_loaders/` — import with `sys.path.insert(0, '/root/capsule/code')`:

- `paths`    — discover mounted assets by pattern (no hardcoded ids); `inventory()`, `find_assets()`.
- `behavior` — behavior NWBs + manifests; `find_session_nwbs()`, `load_manifest()`, `sessions_for_subject()`.
- `ophys`    — processed imaging NWB; `find_ophys_nwb()`, `get_dff_traces()`.
- `hcr`      — `load_cell_typing()`, `find_unmixing_tables()`, `load_cellxgene()`.
- `linking`  — `find_coreg_tables()`, `link_ophys_to_celltype()`.
- `xenium`   — stub (excluded; see docstring to re-enable).

Some external assets could not be introspected from outside the capsule (file API
returned 403). Their loaders discover files by glob and carry `TODO` markers where an
exact filename/column should be confirmed on first mount. Run `00_data_inventory.ipynb`
and the per-modality inspection cells to confirm, then remove the TODOs.

---

## Reproducible runs

`code/run` is the reproducible-run entry point. It has **two modes**, selected by the
App Panel **`mode`** field:

### `mode = analysis` (default — no key)

Runs your own code. By default it executes every notebook in `code/notebooks/` and
writes rendered copies to `results/notebooks/`, plus a snapshot of `code/` to
`results/code/`. Customize `code/run_analysis` to call your own scripts / workflow.
**No Anthropic API key needed.**

### `mode = agent` (optional — needs a key)

Runs the **Claude Code** CLI headlessly against the App Panel `prompt`, for autonomous
tasks (QC a new subject, regenerate a linking table, etc.). Requires the
`ANTHROPIC_API_KEY` secret (or `use-bedrock = 1` with AWS credentials). If no key is
set, this mode exits with a clear message and analysis mode is unaffected.

Agent-mode App Panel fields: `prompt`, `model` (default `claude-haiku-4-5`), `effort`,
`max-budget-usd`, `use-bedrock`, `update-claude`.

---

## Who needs an Anthropic account?

| Activity | Anthropic account/key? |
|----------|------------------------|
| Interactive notebooks / VS Code / JupyterLab | **No** |
| Reproducible run, `mode=analysis` (your notebooks/pipeline) | **No** |
| Reproducible run, `mode=agent` (Claude Code) | **Yes** — your own key, set as the `ANTHROPIC_API_KEY` secret |

A collaborator with no Anthropic login uses everything except the optional agent.

### Using the Claude Code VS Code extension (optional, advanced)

In a VS Code cloud workstation you can also install the **Claude Code extension** for a
GUI session panel. It signs in with your own Claude subscription (Pro/Max/Team/Enterprise)
or Console account via a browser OAuth flow — no API key, and separate from the headless
runner above. Install it from the **Open VSX registry** (search "Claude Code" in the
Extensions view). If your workstation can't install extensions, the `claude` CLI is also
available in the integrated terminal. This is per-user and interactive; it does not change
what login-less users can do.

---

## Environment

- Base image: `codeocean/python-slim-uv`. Python deps in `code/requirements.txt` are
  installed at build time by `environment/postInstall`.
- The Claude Code CLI is installed at build time (needs no key to install); it is only
  *used* in agent mode or if you invoke `claude` yourself.
- **Resources:** the template ships at `xsmall`. Loading the imaging NWBs or the large
  cell-by-gene tables will need more — bump the resource class in
  `.codeocean/resources.json` (or via the UI) before heavy runs.

---

## Repository layout

```
.codeocean/            capsule config (app panel, environment, resources, secrets)
environment/           Dockerfile + postInstall (build the environment)
code/
  run                  reproducible-run entry point (mode: analysis | agent)
  run_analysis         default no-key pipeline (runs notebooks -> results/)
  requirements.txt     Python dependencies
  CLAUDE.md            agent guidance (agent mode)
  attach_assets.py     attach the 5 data assets to a capsule at organized mounts
  data_loaders/        per-modality loaders (paths, behavior, ophys, hcr, linking, xenium-stub)
  notebooks/           00 inventory · 01 behavior · 02 ophys · 03 HCR · 04 linking
  .agents/skills/      bundled codeocean-capsule skill (agent mode)
data/                  (mounted data assets, read-only)
results/               (reproducible-run outputs)
scratch/               (temp / caches)
```

---

## Setup checklist (creating the capsule)

1. **Create an empty capsule** from this repo/template in the Code Ocean UI.
   (The API/connector cannot create capsules; this one step is manual.)
2. **Attach the 5 data assets** at the mounts in the table above — either in the UI, or
   run `code/attach_assets.py <capsule_id>` (or the connector's `attach_data_assets`).
3. **Build the environment** (installs the Python stack + Claude CLI). No key needed to build.
4. **(Optional) add the `ANTHROPIC_API_KEY` secret** only if you want agent mode.
5. Open a workstation, run `00_data_inventory.ipynb`, and confirm the assets are visible.
