# 1×1 cm² PDD analysis — methods and results (Section 3 revision)

Reconstruction of the lost Python analysis for the manuscript
*"Evaluation of … Percentage Depth Dose Measurements Using Three Detectors for
1 × 1 cm² Field Compared with Monaco TPS"*. Addresses reviewer Section 3
comments (3.1 gamma, 3.2 deviation definition, 3.3 normalisation) and the
figure/text reconciliation in comment 4.1 / 4.4.

## Data provenance
Source: `G:\…\LERATO MASTERS\DATA`
- `microDiamond.xlsx`, `PinPoint 3D.xlsx`, `Semiflex.xlsx` — sheet `1x1`,
  col A = depth (mm), col B = measured dose. 1 mm sampling.
- `MonteCarlo (Golden Data).xlsx` — sheet `1X1`, col A = depth, col B = TPS dose.

**Monte Carlo depth reversal (important):** the raw Monaco PDD is stored
*deepest-first* — as read, dose rises with listed depth and peaks at 286 mm,
which is unphysical. The dose column is reversed so that depth 0 = surface,
placing dmax at ~14 mm with a ~22 % surface dose. This reproduces the original
analysis output (`csv's/mcdata.csv`). Detector PDDs are not reversed.

## Definitions (reviewer 3.2, 3.3)
- Percentage deviation: **dev(%) = (D_measured − D_TPS) / D_TPS × 100**.
- Normalisation: each PDD normalised to its **own dmax**; PDD = 100·dose/max(dose).

### dmax summary (reviewer 3.3)
| Curve | dmax depth (nearest mm) | dmax depth (parabolic, mm) |
|---|---|---|
| Monaco TPS | 14 | 14.04 |
| microDiamond | 15 | 14.59 |
| PinPoint | 14 | 14.07 |
| Semiflex | 15 | 14.75 |

## Figure/text reconciliation (reviewer 4.1)
The manuscript's headline numbers are **correct and reproducible**, but they sit
in the build-up region, which the truncated (−4 … +10 %) figure axes hid:

| Manuscript text | Reconstructed | True depth |
|---|---|---|
| microDiamond +106.18 % | +106.4 % | 0 mm (surface) |
| Semiflex +90.32 % | +90.1 % | 0 mm (surface) |
| PinPoint +73.63 % | +73.3 % | 0 mm (surface) |
| Semiflex −20.09 % | −20.2 % | 3 mm |
| PinPoint −18.43 % | −18.5 % | 3 mm |

Text and figures never disagreed — the figures were simply clipped. Figures 1–4
have been regenerated **without truncation**, with vertical dmax markers and a
post-build-up inset (reviewer 4.4a/b). Beyond build-up: microDiamond ≈ 0 ± 2 %,
PinPoint a mild positive trend, Semiflex a monotonically increasing
over-response (+2 % at 30 mm → +7 % at 250 mm) — consistent with reviewer 4.3.

## Gamma analysis (reviewer 3.1)
Tool: **PyMedPhys** 1D gamma. Reference = Monaco TPS PDD, evaluation = measured.
Global normalisation to dmax, 10 % low-dose cutoff, 0.1 mm DTA search
(interp_fraction = 10), depth 0–250 mm.

| Detector | 2%/2 mm | 1%/1 mm | 3%/3 mm |
|---|---|---|---|
| microDiamond | 99.2 % | 98.8 % | 99.2 % |
| PinPoint | 99.6 % | 72.1 % | 99.6 % |
| Semiflex | 98.0 % | 25.9 % | 99.2 % |

At the clinical 2 %/2 mm criterion all detectors agree well with the TPS; at the
strict SRS/SBRT 1 %/1 mm criterion the detectors separate sharply
(microDiamond ≫ PinPoint ≫ Semiflex), giving the quantitative discrimination
the reviewer requested.

## Outputs
- `output/PDD_1x1_combined.xlsx` (sheets: PDD_1x1, dmax_summary, gamma_results, README) and `.csv`
- `output/figures/Figure1–4` — untruncated deviation plots
- `output/figures/Figure5` gamma histograms, `Figure6` gamma-vs-depth
- `output/gamma_summary.csv`

## Reproducibility (reviewer 2.7, 2.8)
Python 3.14; numpy 2.4.6, scipy 1.17.1, pandas 3.0.3, matplotlib 3.10.9,
openpyxl 3.1.5, pymedphys 0.40.0. Scripts: `pdd_common.py` (loading/normalisation/
metric), `build_spreadsheet.py`, `make_figures.py`, `gamma_analysis.py`.
