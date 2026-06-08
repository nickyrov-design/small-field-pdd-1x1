"""
Task A: Build one combined PDD spreadsheet for the 1x1 cm^2 field.

Sheets:
  - PDD_1x1        : depth, raw + dmax-normalised PDD for MC and 3 detectors,
                     and per-detector percentage deviation vs TPS.
  - dmax_summary   : measured & calculated dmax per curve (reviewer comment 3.3).
  - README         : metric definition, MC reversal note, provenance.
"""
from __future__ import annotations
import os
import numpy as np
import pandas as pd
import pdd_common as C

OUT = os.path.join(os.path.dirname(__file__), "..", "output")
os.makedirs(OUT, exist_ok=True)
MAX_DEPTH = 250


def main():
    data = C.load_all(max_depth=MAX_DEPTH)
    mc = data["mc"]
    dets = data["det"]

    grid = np.arange(0, MAX_DEPTH + 1, dtype=float)

    def on_grid(depth, vals):
        d = dict(zip(np.round(depth).astype(int), vals))
        return np.array([d.get(int(g), np.nan) for g in grid])

    df = pd.DataFrame({"depth_mm": grid.astype(int)})
    # MC
    df["MC_dose_raw"] = on_grid(mc["depth"], mc["dose"])
    df["MC_PDD_norm"] = on_grid(mc["depth"], mc["pdd"])
    # detectors: raw, normalised, deviation
    for key, lbl in [("microDiamond", "microDiamond"), ("PinPoint", "PinPoint"), ("Semiflex", "Semiflex")]:
        df[f"{lbl}_dose_raw"] = on_grid(dets[key]["depth"], dets[key]["dose"])
        df[f"{lbl}_PDD_norm"] = on_grid(dets[key]["depth"], dets[key]["pdd"])
        gdep, dev = C.deviation(dets[key]["depth"], dets[key]["pdd"],
                                mc["depth"], mc["pdd"], grid=grid)
        df[f"{lbl}_dev_%"] = dev

    # dmax summary
    rows = []
    for name, cur in [("MC (Monaco TPS)", mc), ("microDiamond", dets["microDiamond"]),
                      ("PinPoint", dets["PinPoint"]), ("Semiflex", dets["Semiflex"])]:
        di, dinterp, ddose = cur["dmax"]
        rows.append({"curve": name, "dmax_depth_mm_nearest": di,
                     "dmax_depth_mm_parabolic": round(dinterp, 2),
                     "dmax_dose_raw": round(ddose, 4)})
    dmax_df = pd.DataFrame(rows)

    readme = pd.DataFrame({"Notes": [
        "Combined 1x1 cm^2 PDD data for: Evaluation of detector response in small-field PDD.",
        "",
        "Deviation convention (reviewer 3.2):  deviation(%) = (D_measured - D_TPS) / D_TPS * 100.",
        "Normalisation (reviewer 3.3): each PDD normalised to its own dmax; PDD = 100*dose/max(dose).",
        "",
        "Monte Carlo (Monaco TPS) PDD depth-reversal: the raw 'MonteCarlo (Golden Data).xlsx'",
        "stores the 1X1 PDD deepest-first (dose rises with listed depth, peaking at 286 mm).",
        "The dose column was reversed so depth 0 = surface; this reproduces the original",
        "analysis output (csv's/mcdata.csv). Detector PDDs are NOT reversed.",
        "",
        "Source files (G:\\...\\LERATO MASTERS\\DATA):",
        "  microDiamond.xlsx [sheet 1x1] cols A=depth(mm), B=dose",
        "  PinPoint 3D.xlsx  [sheet 1x1] cols A=depth(mm), B=dose",
        "  Semiflex.xlsx     [sheet 1x1] cols A=depth(mm), B=dose",
        "  MonteCarlo (Golden Data).xlsx [sheet 1X1] cols A=depth(mm), B=dose (reversed)",
        "",
        "Depth sampling: 1 mm native. Depth range 0-250 mm.",
    ]})

    out_path = os.path.join(OUT, "PDD_1x1_combined.xlsx")
    with pd.ExcelWriter(out_path, engine="openpyxl") as xw:
        df.round(4).to_excel(xw, sheet_name="PDD_1x1", index=False)
        dmax_df.to_excel(xw, sheet_name="dmax_summary", index=False)
        readme.to_excel(xw, sheet_name="README", index=False)

    # also CSV for portability
    df.round(4).to_csv(os.path.join(OUT, "PDD_1x1_combined.csv"), index=False)

    print("Wrote", out_path)
    print("\ndmax summary:")
    print(dmax_df.to_string(index=False))
    print("\nKey deviation checkpoints (vs manuscript text):")
    for d in [0, 1, 2, 3, 5, 10, 14, 50, 100, 150, 200, 250]:
        r = df[df.depth_mm == d]
        if not r.empty:
            print(f"  depth {d:>3} mm:  microDiamond {r['microDiamond_dev_%'].values[0]:+7.2f}%"
                  f"   PinPoint {r['PinPoint_dev_%'].values[0]:+7.2f}%"
                  f"   Semiflex {r['Semiflex_dev_%'].values[0]:+7.2f}%")


if __name__ == "__main__":
    main()
