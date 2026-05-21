# fsrlab-sensor-analysis

NGS sensor analysis pipeline for base editing and prime editing screens.

```{note}
**Last updated:** May 21, 2026

**Contributors:** Kexin Dong, Sam Gould

**Repository:** [github.com/fsrlabmit/sensor-analysis](https://github.com/fsrlabmit/sensor-analysis)
```

## What's new in this version

- (For first-time user of the pipeline) Use micromamba to replaces conda for env management on the cluster, which is way faster.
- Detailed instructions on how to deal with samples with duplicated NGS lanes.
- Sensor extraction rewritten with trimming and revised QC strategies, so that only required regions are checked, with optional per-base quality thresholds.
- Sensor extraction rewritten for prime editing screen analysis.
- Updated LFC calculation with more comprehensive information for downstream analysis.

## Pipeline overview

The pipeline is split into 9 numbered steps, grouped into 3 logical phases:

```{list-table}
:header-rows: 1
:widths: 20 25 55

* - Phase
  - Steps
  - What it does
* - **Setup**
  - 1 – 3
  - Download data, create cluster environments, generate config + library files.
* - **Cluster scripts**
  - 4 – 6
  - Filter reads, count guides, split sensor reads, run CRISPResso, aggregate.
* - **Local analysis**
  - 7 – 9
  - Compile CRISPResso outputs, build count matrix, compute LFC and FDR.
* - **Downstream**
  - —
  - Hit calling, calibration, replicate concordance, etc.
```

## Sequencing strategy

Based on paired-end sequencing where **R1 = Sensor_Read** and **R2 = Protospacer_Read**:

```{image} figures/seq_strategy.png
:width: 600px
:align: center
```

```{warning}
This pipeline must be modified to work with alternative sequencing strategies.
```

## How to use these docs

1. Clone the [repository](https://github.com/fsrlabmit/sensor-analysis) locally.
2. Go through [setup](setup.md) to prepare the cluster and your inputs.
3. Run [cluster extraction](extraction.md) for each sequencing run.
4. Copy outputs locally, then run [local analysis](analysis.md).
5. Build on top of these outputs with [downstream analyses](downstream.md).

```{toctree}
:caption: 'Contents:'
:maxdepth: 2
:hidden:

setup
extraction
analysis
downstream
```
