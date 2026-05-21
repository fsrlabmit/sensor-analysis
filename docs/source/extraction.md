# Cluster scripts

```{contents}
:local:
:depth: 2
```

---

```{important}
Step 4 - 6 will be run on the cluster. For each step, there is a python script and a corresponding `.sh` script that provides instructions to the cluster about which samples to run analysis on/where these files are located. Do not modify the Python script. **The only thing you will need to edit are these .sh scripts.**
```

---

## STEP 4 — Sensor extraction & guide counts

[`NGS-scripts/STEP4_sensor_extraction/`](https://github.com/fsrlabmit/sensor-analysis/blob/main/NGS-scripts/STEP4_sensor_extraction/)

This step (A) filters low-quality reads, (B) counts guides, and (C) splits sensor reads into per-guide fastq files.

You'll notice two versions of the extraction script:

```{list-table}
:header-rows: 1
:widths: 40 60

* - Script
  - QC strategy
* - `sensor_extraction_42nt`
  - Averages quality over the full read (original SG version)
* - `sensor_extraction_42nt_trimming_quality`
  - Region-specific checks + optional per-base threshold (KD, 2026-03-10)
```

```{tip}
The revised version was added to fix a QC problem with the original. The OG only looks at the average quality of the whole read, but we've noticed the sequencing center sometimes doesn't trim extra sequences properly — which under the OG strategy throws away perfectly usable reads. The revised `sensor_extraction_42nt_trimming_quality` lets you QC only the regions you actually care about (barcode + sensor).

The OG version is fine for most cases, but I'd recommend switching to the revised one for future screens.
```

### Editing

Whichever you choose, you need to edit `.sh` script as follows:

```{image} figures/step_4.png
:width: 600px
:align: center
```

1. This needs to match up with the number of samples you're running. E.g if your config file runs from 1-10, set this to 1-10.
2. Change it to your email!
3. Choose conda or micromamba to match what you use and change the env path to yours to activate the environment.
4. Set this path to match up with the folder where your sequencing data is stored.
5. Set this to match up with your config file name with the prefix "./"
6. These are parameters for the run.
    - **splitby** = whether to split sensors into separate fastq files by the protosapcer identity or the barcode identity
        - Options: 'protospacer' or 'barcode'.
        - Recommend 'protospacer'.
    - **proto_mismatches_allowed** = # of protospacer mismatches allowed when performing counts.
    - **bc_len** = length of barcode (normally 15 nt).
    - **sensor_len** = length of sensor (normally 42 nt).
    - **quality_check_mode (revised version only)** = how to drop out low quality reads. Phred threshold is 30 by default.
        - Options:
            - 'full_average': averages Phred quality across the **entire** R1 and R2 reads, and drops the read if either average falls below threshold. This is the original SG behavior — strict, but discards reads when untrimmed flanking sequence drags the average down.
            - 'region_average': averages Phred quality only over the **regions actually used downstream** (barcode + sensor in R1, protospacer in R2). Flanking junk no longer affects the call.
            - 'region_average_and_threshold': same region-restricted averaging as above, **plus** two extra per-base checks: (a) no single base in the **barcode region** may fall below Phred 30 (any single bad base in the barcode → drop, because barcode errors break guide assignment), and (b) no more than 5 bases in the required regions may fall below Phred 20. This is the strictest mode.
        - Recommend `'region_average'` for most runs, or `'region_average_and_threshold'` when barcode-assignment accuracy is critical.
7. Change the library filename to match up with the name that you've given to the file.

### Add to cluster

Once this is done, add this (1) **sensor_extraction_42nt_trimming_quality.sh** to your sequencing folder, along with (2) **sensor_extraction_42nt_trimming_quality.py**.

### Submit

Finally, run the cluster command to execute this script by logging into the cluster and running the command in [`RUN_THIS.sh`](https://github.com/fsrlabmit/sensor-analysis/blob/main/NGS-scripts/STEP4_sensor_extraction/RUN_THIS.sh).

```bash
cd $LABROOT/<sequencing_folder>
sbatch sensor_extraction_42nt_trimming_quality.sh
```

### Step 4 for prime editing screen analysis

For **prime editing** screens we use separate scripts, especially for this step. See [`NGS-scripts-prime-editing/`](https://github.com/fsrlabmit/sensor-analysis/tree/main/NGS-scripts-prime-editing) for scripts and examples.

In earlier PE analyses we saw an unusually high rate of barcode–protospacer recombination. To improve barcode specificity, the matched barcode is extended by **8 nt** into the sensor sequence — i.e. the script matches reads against a **16 nt** `Hamming_BC` (the original 8 nt BC + the first 8 nt of the sensor), while the actual sensor extracted into the per-guide fastq still starts at position 8 (`real_bc_len`). This gives more discriminating power without losing any sensor content downstream.

#### Editing the PE `.sh`

Same fields as the BE version, plus two PE-specific ones:

- **bc_len** = length of the extended barcode used for matching (normally `16` for PE)
- **real_bc_len** = where the sensor actually starts in R1 (normally `8` — the overlap region between BC and sensor)
- **sensor_len** = length of the sensor extracted into per-guide fastq (normally `55` for PE)
- **quality_check_mode** = `'full_average'`, `'region_average'`, or `'region_average_and_threshold'` (same semantics as above; region check covers `[:bc_len + sensor_len]` in R1)

Library file must contain the `pegRNA_id` column.

#### Submit

```bash
cd $LABROOT/<sequencing_folder>
sbatch sensor_extraction_peg_counts_ext_bc_16nt.sh
```

---

## STEP 5 — CRISPResso sensor analysis

[`NGS-scripts/STEP5_sernsor_analysis/`](https://github.com/fsrlabmit/sensor-analysis/blob/main/NGS-scripts/STEP5_sernsor_analysis/)

This step runs CRISPResso on each per-guide fastq from STEP4.

### Edit

Edit [`crispresso_analysis_42nt.sh`](https://github.com/fsrlabmit/sensor-analysis/blob/main/NGS-scripts/STEP5_sernsor_analysis/crispresso_analysis_42nt.sh).

```{image} figures/step_5.png
:width: 600px
:align: center
```

1. This needs to match up with the number of samples you're running. E.g if your config file runs from 1-10, set this to 1-10.
2. Change it to your email!
3. Choose conda or micromamba to match what you use and change the env path to yours to activate the environment.
4. Set this path to match up with the folder where your sequencing data is stored.
5. Set this to match up with your config file name with the prefix "./"
6. Change the library filename to match up with the name that you've given to the file.

### Add to cluster

Once this is done, add this (1) **crispresso_analysis_42nt.sh** to your sequencing folder, along with (2) **crispresso_analysis_w_qwc_42nt.py**.

### Submit

Finally, run the cluster command to execute this script by logging into the cluster and running the command in [`RUN_THIS.sh`](https://github.com/fsrlabmit/sensor-analysis/blob/main/NGS-scripts/STEP5_sernsor_analysis/RUN_THIS.SH).

```bash
cd $LABROOT/<sequencing_folder>
sbatch crispresso_analysis_42nt.sh
```

:::{note}
If CRISPResso errors on folder permissions, fix with:

```bash
chmod -R g+w /net/bmc-lab2/data/lab/sanchezrivera/$USER/<your_run>/crispresso
```
:::

---

## STEP 6 — CRISPResso aggregation

[`NGS-scripts/STEP6_sensor_aggregation/`](https://github.com/fsrlabmit/sensor-analysis/blob/main/NGS-scripts/STEP6_sensor_aggregation/)

This step aggregates per-guide CRISPResso outputs into one dataframe per sample.

### Edit

Edit `crispresso_analysis_aggregation.sh`.

```{image} figures/step_6.png
:width: 600px
:align: center
```

1. This needs to match up with the number of samples you're running. E.g if your config file runs from 1-10, set this to 1-10.
2. Change it to your email!
3. Choose conda or micromamba to match what you use and change the env path to yours to activate the environment.
4. Set this path to match up with the folder where your sequencing data is stored.
5. Set this to match up with your config file name with the prefix "./"
6. Change the library filename to match up with the name that you've given to the file.

### Add to the cluster

You must add **all three** files to your sequencing folder:

1. `crispresso_analysis_aggregation.sh`
2. `crispresso_analysis_aggregation.py`
3. `crispresso_quant_blank.csv` — **the script will fail without it**

### Submit

Finally, run the cluster command to execute this script by logging into the cluster and running the command in [`RUN_THIS.sh`](https://github.com/fsrlabmit/sensor-analysis/blob/main/NGS-scripts/STEP6_sensor_aggregation/RUN_THIS.SH).

```bash
cd $LABROOT/<sequence_folder>
sbatch crispresso_analysis_aggregation.sh
```

---

### Actions before running STEP7

After step 4-6, you will generate data as follows on the cluster:

#### `classification/`

Per-sample read-quality and protospacer/barcode-identification breakdown.

```{list-table}
:header-rows: 1
:widths: 35 65

* - Column
  - Description
* - `good_quality`
  - reads above quality threshold
* - `low_qual_r1`
  - R1 below threshold (excluded)
* - `low_qual_r2`
  - R2 below threshold (excluded)
* - `low_qual_r12`
  - both R1 and R2 below threshold (excluded)
* - `no_match_bc`
  - good-quality reads with no barcode match
* - `bc_identified`
  - good-quality reads with barcode identified
* - `proto_identified_perfect`
  - good-quality reads, protospacer with 0 mismatches
* - `proto_identified_imperfect`
  - good-quality reads, protospacer within allowed mismatches
* - `proto_identified_recombined`
  - good-quality reads, protospacer identified but barcode mismatch (recombination event)
* - `no_match_proto`
  - good-quality reads, no protospacer identified
```

#### `confusion_mats/`

Recombination matrix between protospacer and barcode (diagnostic).

#### `counts/`

Per-sample guide and barcode counts.

```{list-table}
:header-rows: 1
:widths: 30 70

* - Column
  - Description
* - `Guide_ID`
  - guide name
* - `sgRNA_no_Gstart`
  - protospacer
* - `unique_BC`
  - barcode
* - `total_guide_count`
  - total protospacer count (incl. recombination)
* - `matched_guide_count`
  - reads with matched protospacer-barcode pairs
* - `bc_count`
  - total barcode count (incl. recombination)
* - `duplicate_sgRNA`
  - TRUE if guide appears more than once in the library
```

Run MAGeCK on either `matched_guide_count` (more stringent) or `bc_count` (higher counts).

#### `crispresso/`

Per-guide CRISPResso editing outcomes. Aggregated by STEP6, compiled by STEP7.

Following steps will analyze these data in Jupyter Notebooks. Before doing so,

- **copy the `.csv` files out of the cluster `crispresso/` folder to the local folder**.

  ```{image} figures/crispresso.png
  :width: 40%
  :align: left
  ```

- **copy the whole `counts/` folder to the local working folder.**

  ```{image} figures/counts.png
  :width: 40%
  :align: left
  ```
