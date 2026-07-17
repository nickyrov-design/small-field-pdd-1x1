# small-field-pdd-1x1

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20595530.svg)](https://doi.org/10.5281/zenodo.20595530)

Reproducible analysis code for the medical-physics paper *"Comparison of
Percentage Depth Dose Measurements Obtained with Three Detector Technologies and
Monaco TPS Calculations in a 1 × 1 cm² Small Photon Field."*

This repository extracts and combines 1 x 1 cm² 6 MV percentage depth dose (PDD)
measurements from three detectors — PTW microDiamond, PinPoint 3D, and Semiflex
3D — and compares each against the Monaco treatment planning system (TPS). It
reproduces the paper's per-detector deviation figures (regenerated without
truncated axes) and adds a PyMedPhys 1D gamma analysis (1%/1 mm, 2%/2 mm,
3%/3 mm) quantifying detector–TPS agreement.

## Repository layout

```
small-field-pdd-1x1/
├── src/                     Analysis scripts
│   ├── pdd_common.py        Data loading, MC depth-reversal, normalisation, deviation metric
│   ├── build_spreadsheet.py Combined 1x1 PDD spreadsheet (Task A)
│   ├── make_figures.py      Untruncated deviation Figures 1-4 (Task B)
│   └── gamma_analysis.py    PyMedPhys 1D gamma analysis (Task C)
├── output/                  Processed outputs (committed for reference)
│   ├── PDD_1x1_combined.xlsx
│   ├── PDD_1x1_combined.csv
│   ├── gamma_summary.csv
│   └── figures/             Figure1-6 PNGs
├── data/                    Place raw input .xlsx here (not committed)
├── METHODS_AND_RESULTS.md   Methods / results summary
├── requirements.txt         Pinned pip dependencies
├── environment.yml          Equivalent conda environment
├── .python-version          Python interpreter version (3.14.3)
├── CITATION.cff
├── LICENSE
└── README.md
```

## Requirements

The analysis was performed and verified with **Python 3.14.3** and the exact
package versions pinned in [`requirements.txt`](requirements.txt) (numpy 2.4.6,
scipy 1.17.1, pandas 3.0.3, matplotlib 3.10.9, openpyxl 3.1.5, pymedphys 0.40.0).
The scripts execute without modification against this environment.

Using pip (Python version is set in [`.python-version`](.python-version)):

```
pip install -r requirements.txt
```

Or create the equivalent conda environment from
[`environment.yml`](environment.yml):

```
conda env create -f environment.yml
conda activate small-field-pdd-1x1
```

## Data setup

The raw detector and TPS measurement files are **not** included in this
repository. Obtain them and place the following `.xlsx` files in the `data/`
directory (see `data/README.md` for the full table of sheet names and columns):

- `microDiamond.xlsx` (sheet `1x1`)
- `PinPoint 3D.xlsx` (sheet `1x1`)
- `Semiflex.xlsx` (sheet `1x1`)
- `MonteCarlo (Golden Data).xlsx` (sheet `1X1`)

By default the scripts read from `data/`. To use a different location, set the
`PDD_DATA_DIR` environment variable:

```
# Windows (PowerShell)
$env:PDD_DATA_DIR = "C:\path\to\raw\data"
# Linux / macOS
export PDD_DATA_DIR=/path/to/raw/data
```

**Monte Carlo depth reversal:** the raw Monaco / Monte Carlo PDD is stored
*depth-reversed* (deepest-first), so as read the dose peaks at an unphysical
~286 mm. The code (`pdd_common.load_mc`) reverses the dose column so that depth
0 = surface, placing dmax at ~14 mm. The detector PDDs are not reversed.

## How to run

From the `src/` directory:

```
cd src
python build_spreadsheet.py
python make_figures.py
python gamma_analysis.py
```

Each script writes into the top-level `output/` folder:

- **`build_spreadsheet.py`** — `output/PDD_1x1_combined.xlsx` (sheets: `PDD_1x1`,
  `dmax_summary`, `README`) and `output/PDD_1x1_combined.csv`. Combines raw and
  dmax-normalised PDDs for the TPS and all three detectors with per-detector
  percentage deviation.
- **`make_figures.py`** — `output/figures/Figure1_panels_ABCD.png`: the
  consolidated multi-panel figure published as Figure 1 — (A) microDiamond,
  (B) Semiflex 3D, (C) PinPoint 3D, (D) all three overlaid, on common axes with
  an untruncated y-range and post-build-up (15-250 mm) insets. Also writes the
  individual per-detector plots it supersedes (`Figure1_microDiamond.png`,
  `Figure2_Semiflex.png`, `Figure3_PinPoint.png`, `Figure4_overlay.png`), each
  with vertical dmax markers and a post-build-up inset.
- **`gamma_analysis.py`** — `output/gamma_summary.csv`, a `gamma_results` sheet
  appended to `PDD_1x1_combined.xlsx`, and `output/figures/Figure5_gamma_histograms.png`
  and `Figure6_gamma_vs_depth.png`. Runs PyMedPhys 1D gamma at 1%/1 mm, 2%/2 mm,
  and 3%/3 mm (global normalisation, 10% low-dose cutoff, interp_fraction = 10).

Run `build_spreadsheet.py` before `gamma_analysis.py` if you want the
`gamma_results` sheet appended to the combined workbook.

### PyMedPhys SciPy-backend workaround

`gamma_analysis.py` contains a small documented monkeypatch. PyMedPhys's gamma
routine optionally uses the econforge "interpolation" backend and falls back to
SciPy via `except ImportError`. In some installs the optional package is absent
and `apipkg` masks the `ImportError` with a `FileNotFoundError`, so the fallback
never triggers. The script forces the SciPy interpolation path by making the
econforge helper (`pymedphys._gamma.implementation.shell._run_interp_with_econforge`)
raise `ImportError`. This only affects which interpolation backend is used, not
the gamma results.

## Definitions

- **Percentage deviation:** `dev(%) = (D_meas − D_TPS) / D_TPS * 100`.
- **Normalisation:** each PDD is normalised to its **own dose maximum (dmax)**;
  `PDD(d) = 100 * dose(d) / max(dose)`.

See `METHODS_AND_RESULTS.md` for the dmax summary, figure/text reconciliation,
and gamma pass-rate tables.

## License

Released under the MIT License — see [LICENSE](LICENSE).

## How to cite

If you use this code, please cite the associated article and this software.
Citation metadata is provided in [CITATION.cff](CITATION.cff).

This software is archived on Zenodo with the concept DOI
[10.5281/zenodo.20595530](https://doi.org/10.5281/zenodo.20595530) (resolves to
the latest version):

> Ntombela LN, Rovetto NJ, Shivambu GI. *small-field-pdd-1x1:
> Reproducible analysis code for 1 × 1 cm² small-field PDD detector comparison.*
> Zenodo. https://doi.org/10.5281/zenodo.20595530

## Acknowledgements

L. Mohlafase assisted with the experimental data collection. This is a
contributor (data-collection) role and does not constitute authorship of the
software or the associated article.
