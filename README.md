# fsrlab-sensor-analysis

NGS sensor analysis pipeline for base editing and prime editing screens.

**Contributors:** Kexin Dong, Sam Gould
**Last updated:** May 21, 2026

## Documentation

Full step-by-step documentation is hosted at **[sensor-analysis.readthedocs.io](https://sensor-analysis.readthedocs.io)**.

The docs are organized into four pages:

| Page | Contents |
| --- | --- |
| [Home](https://sensor-analysis.readthedocs.io) | Overview, what's new, sequencing-strategy diagram |
| [Setup (STEPs 1–3)](https://sensor-analysis.readthedocs.io/en/latest/setup.html) | Download NGS data, create micromamba envs, generate config + library files |
| [Cluster scripts (STEPs 4–6)](https://sensor-analysis.readthedocs.io/en/latest/extraction.html) | Filter + count + split reads, run CRISPResso, aggregate |
| [Local analysis (STEPs 7–9)](https://sensor-analysis.readthedocs.io/en/latest/analysis.html) | Compile editing tables, build count matrix, compute LFC + empirical FDR |
| [Downstream](https://sensor-analysis.readthedocs.io/en/latest/downstream.html) | What to do with the processed data |

## Repository structure

```
NGS-scripts/
├── STEP1_download_data/        — rsync cheatsheet
├── STEP2_conda_env/            — micromamba env spec files (.yml) + setup script
├── STEP3_generate_config_file/ — Jupyter notebook to build per-run config
├── STEP4_sensor_extraction/    — SLURM array job: filter + count + split (BE + PE variants)
├── STEP5_sensor_analysis/      — SLURM array job: CRISPResso per guide
├── STEP6_sensor_aggregation/   — SLURM array job: aggregate CRISPResso
├── STEP7_crispresso_compiler/  — local notebook: merge lanes + biological reps
├── STEP8_counts_matrix/        — local notebook: build count matrix (and MAGeCK input)
└── STEP9_LFC_FDR_calculation/  — local notebook: empirical LFC + FDR with editing attached
docs/                           — Sphinx source for the documentation site
```

## How to use

1. Clone this repo locally.
2. Follow the steps in the documentation in order.

## Notes

- The full long-form pipeline description is kept in [`README_full.md`](README_full.md) as a single-file fallback.
- The hosted docs are built from the Markdown sources under [`docs/source/`](docs/source/) via Sphinx + sphinxawesome-theme. Build config: [`readthedocs.yaml`](readthedocs.yaml).

## Questions

Open an issue at [github.com/fsrlabmit/sensor-analysis/issues](https://github.com/fsrlabmit/sensor-analysis/issues).
