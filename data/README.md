# Raw input data

The raw detector and Monte Carlo / TPS measurement files are **not committed** to
this repository (they are ignored via `.gitignore`). To reproduce the analysis,
place the following `.xlsx` files in this `data/` directory:

| File | Sheet | Columns | Contents |
|---|---|---|---|
| `microDiamond.xlsx` | `1x1` | A = depth (mm), B = dose | PTW microDiamond 1x1 PDD |
| `PinPoint 3D.xlsx` | `1x1` | A = depth (mm), B = dose | PinPoint 3D 1x1 PDD |
| `Semiflex.xlsx` | `1x1` | A = depth (mm), B = dose | Semiflex 3D 1x1 PDD |
| `MonteCarlo (Golden Data).xlsx` | `1X1` | A = depth (mm), B = dose | Monaco TPS 1x1 PDD |

Notes:
- Depth sampling is 1 mm native; the analysis uses the 0-250 mm range.
- The raw Monaco / Monte Carlo PDD is stored **depth-reversed** (deepest-first);
  the code in `src/pdd_common.py` (`load_mc`) corrects this automatically so that
  depth 0 = surface. The detector PDDs are not reversed.

By default the scripts read from this `data/` directory. To read from a different
location, set the `PDD_DATA_DIR` environment variable to the folder containing
these files.
