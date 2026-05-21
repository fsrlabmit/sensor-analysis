# Local analysis

```{contents}
:local:
:depth: 2
```

---

## STEP 7 — Compile CRISPResso results

[`NGS-scripts/STEP7_crispresso_compiler/compiling_crispresso.ipynb`](https://github.com/fsrlabmit/sensor-analysis/blob/main/NGS-scripts/STEP7_crispresso_compiler/compiling_crispresso.ipynb)

This notebook:

- Merges NGS lane replicates (if needed).
- Generates MLE table that combines biological replicates.

---

## STEP 8 — Counts matrix (and MaGeCk)

[`NGS-scripts/STEP8_counts_and_MaGeCk/mageck.ipynb`](https://github.com/fsrlabmit/sensor-analysis/blob/main/NGS-scripts/STEP8_counts_and_MaGeCk/mageck.ipynb)

Local notebook. Builds a count matrix (samples × guides) from STEP4 counts, which can be used for QC analysis as well as MaGeCk, to calculate LFC and FDR.

```{important}
When building ABE-only or CBE-only sub-pool files, keep only the matching guides.
```

Example MAGeCK call:

```bash
source activate mageckenv
mageck test \
  -k guide_counts.txt \
  -t tf_rep1,tf_rep2,tf_rep3 \
  -c t0_rep1,t0_rep2,t0_rep3 \
  --normcounts-to-file \
  -n my_analysis
```

`-t` = treatment columns, `-c` = control columns, `-n` = output prefix. The main result is `*.sgrna_summary.txt`. Docs: <https://sourceforge.net/p/mageck/wiki/Home/>

---

## STEP 9 — Empirical LFC-FDR calculation

[`NGS-scripts/STEP9_LFC_FDR_calculation/LFC_FDR_calculation.ipynb`](https://github.com/fsrlabmit/sensor-analysis/blob/main/NGS-scripts/STEP9_LFC_FDR_calculation/LFC_FDR_calculation.ipynb)

This notebook computes guide-level **log2 fold-changes (LFCs)**, **empirical p-values**, **combined p-values across replicates**, and **BH-adjusted FDRs** from the count tables produced in STEP 8, and attaches sensor editing measurements from STEP 7 to the output table for downstream calibration.

### Why a custom pipeline (instead of MAGeCK)

We initially ran MAGeCK on these screens, but it consistently overestimated the number of significant hits — calling large fractions of guides as enriched/depleted, including in noisy tissues (e.g. CBE meninges). The likely reason: MAGeCK was designed for **CRISPR nuclease screens** where multiple guides per gene are collapsed into a single gene-level score, while our analysis focuses on **individual guide behavior** and we want to preserve replicate-level variability rather than collapse it early.

The pipeline here is a more conservative, **non-parametric** alternative that builds an empirical null distribution from control guides (safe-targeting + non-targeting) **separately per tissue and per screen**, and uses it to assign p-values without imposing a parametric model.

### Improvements of this version

- Further packed functions to make it easier and clearer to run for multiple screens.
- Compatible with two baseline modes:
    - **T0 baseline** — single `input` sample collected prior to mRNA electroporation
    - **Barcoding baseline** — per-condition, per-tissue median RPM across barcoding screen replicates
    - mode is auto-detected by `run_screen_pipeline` based on whether `df_counts_bc` is provided.
- Added **concordant mean LFC** across replicates as an effect-size estimate (mean of replicates that agree on direction; guides where <2/3 of replicates agree are flagged ambiguous).
- Sensor editing percentages from **all time points** and conditions are attached to the output table.
- Added **z-scores** per replicate and per condition.
- Added **Stouffer's method** as an alternative to Fisher's method for combining replicate p-values.
- More detailed mathematical documentation throughout the notebook.

### Pipeline steps (what each section in the notebook does)

The notebook breaks down into 6 numbered analytical steps, all wired together inside `run_screen_pipeline`.

**Step 1 — Normalize counts by sequencing depth.** Raw guide counts are converted to **reads per million (RPM)** with a pseudocount of 1 to avoid zeros and stabilize the downstream log:

$$
RPM_{ij} = \frac{count_{ij} + 1}{\sum_k (count_{kj} + 1)} \times 10^6
$$

**Step 2 — Calculate LFC and summarize across replicates.** For each guide in each replicate, LFC is computed against the chosen baseline:

$$
LFC_{ij} = \log_2 \left( \frac{RPM_{ij,\mathrm{sample}}}{\widetilde{RPM}_{i,\mathrm{baseline}}} \right)
$$

where the baseline is either (a) median across T0 input replicates or (b) median across barcoding-screen replicates for the same condition. Replicate-level LFCs are summarized into **mean**, **median**, and **concordant mean** (with 2/3-replicate directional-agreement threshold), and each summary is also converted to a **z-score** across all guides in that condition.

**Step 3 — Attach sensor editing info.** Editing percentages from STEP 7's MLE CSVs (`corr_perc`, `target_base_edit_perc`, `byproduct_INDEL_perc`, `byproduct_sub_perc`, `Reads_aligned_all_amplicons`) are merged onto the LFC table for **every** condition (input / d5 / d15 / bm / spleen / men).

**Step 4 — Bootstrap an empirical null from control guides.** For each tissue:

1. Pool LFC values from all safe-targeting + non-targeting guides across replicates,
2. Bootstrap-resample 10,000 LFC values (with replacement) from that pool.

```{image} figures/null.png
:width: 700px
:align: center
```

This null captures tissue-specific technical/biological variability without assuming a parametric distribution. The notebook also plots each null overlaid with per-replicate control LFC histograms for QC.

**Step 5 — Compute two-sided empirical p-values per replicate.** For each guide × replicate:

$$
p_{\mathrm{high}} = \frac{1 + \#(null \geq LFC_{\mathrm{obs}})}{1 + N_{\mathrm{null}}}
\qquad
p_{\mathrm{low}} = \frac{1 + \#(null \leq LFC_{\mathrm{obs}})}{1 + N_{\mathrm{null}}}
$$

The +1 pseudocount keeps p-values strictly positive. Enrichment and depletion tails are kept separate so direction can be assessed independently.

**Step 6 — Combine across replicates + multiple-testing correction.** Replicate p-values are combined with both:

- **Fisher's method** — sensitive to a single strong replicate.
- **Stouffer's method** — requires more consistent evidence across replicates.

Combined p-values are then BH-adjusted (`statsmodels.stats.multitest.multipletests`), and the final two-sided FDR per guide is $FDR = \min(FDR_{\mathrm{high}},\ FDR_{\mathrm{low}})$. We report Fisher's by default; Stouffer's is stored for comparison. Default significance cutoff is **FDR < 0.1**.

```{caution}
Both Fisher and Stouffer assume independence between tests. In our setting biological replicates share the same initial guide pool and may exhibit correlated variability, so this assumption is only approximate.
```

### How to use this notebook

1. **Define functions.** Run all cells from the top through `run_screen_pipeline` (imports, `rpm`, `LFC_table_generator`, `attach_editing_info`, `bootstrap_null`, `plot_null_distributions`, `empirical_p_value`, `two_sided_FDR`). These only define functions — no output.
2. **Load data.** Run the cells that read the STEP 8 count tables, the library annotation, and any other shared inputs.
3. **Configure screens.** In the `screens` dictionary, add one entry per screen. Each entry takes:
   - `df_counts` — the raw count DataFrame (e.g. `ABE_OG_COUNTS`)
   - `library` — library annotation table with `gRNA_id` + `classification` columns
   - `samps_to_merge` — replicate columns grouped by condition (list of lists)
   - `new_names` — short condition names matching each group
   - `to_comparison_samps` — baseline sample column(s) for T0 LFC (e.g. `['input']`)
   - `conditions_null` — which conditions to compute null distributions + FDR for
   - `fp_editing`, `mle_names`, `mle_affix` — paths and labels for STEP 7's MLE editing CSVs
   - *(optional)* `df_counts_bc`, `samps_to_merge_bc`, `new_names_bc` — provide these instead of `to_comparison_samps` to switch to the barcoding baseline
4. **Run.** Execute the `screens` cell. The pipeline runs each screen and prints per-condition hit counts. Results land in `results[screen_name]['LFC_FDR']`.
5. **Save.** Run the final cell to export each screen's combined LFC + FDR table to `LFC-FDR/<screen_name>_LFC_FDR.csv`.

### Output table

For each screen, the final CSV contains three categories of columns (one set per tissue):

#### Effect size

- **LFC** per replicate per tissue
- **Mean, concordant mean, median LFC** across replicates per tissue
- **Mean, concordant mean, median z-score** across replicates per tissue

#### Statistical significance

- **Empirical p-value** per replicate per tissue (from the non-parametric null)
- **Combined p-value** across replicates per tissue (Fisher + Stouffer)
- **BH-adjusted FDR** for Fisher and Stouffer combined p-values per tissue

#### Sensor editing

- **Target editing %** and **correct editing %** at every time point/condition (input / d5 / d15 / bm / spleen / men), so calibration analyses (e.g. LFC vs editing efficiency) can be done directly from this single table.
