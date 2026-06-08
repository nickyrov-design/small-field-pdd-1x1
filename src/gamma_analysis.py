"""
Task C: 1D gamma analysis of measured vs TPS PDD (reviewer comment 3.1).

Uses PyMedPhys (the tool the reviewer recommends). For each detector and each
criterion, reports gamma pass rate, mean gamma, max gamma and the number of
evaluated points, plus a gamma histogram.

Settings (documented for reproducibility):
  - Reference   = Monaco TPS PDD ; Evaluation = measured detector PDD
  - Both curves normalised to their own dmax (= 100%)
  - Global normalisation to the reference maximum (global gamma)
  - Low-dose cutoff: 10% of max  ;  interp_fraction = 10 (0.1 mm DTA search)
  - Depth range: 0-250 mm, 1 mm native sampling
  - Criteria: 2%/2 mm, 1%/1 mm, 3%/3 mm
"""
from __future__ import annotations
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pymedphys
import pdd_common as C

# --- Environment workaround -------------------------------------------------
# pymedphys.gamma optionally uses the econforge "interpolation" backend and
# falls back to SciPy via `except ImportError`. In this install the optional
# package is absent and apipkg masks the ImportError with a FileNotFoundError
# (missing dependency-extra.txt), so the fallback never triggers. We force the
# SciPy interpolation path by making the econforge helper raise ImportError.
import pymedphys._gamma.implementation.shell as _gshell  # noqa: E402


def _force_scipy_interp(options, all_points):
    raise ImportError("force SciPy interpolation backend")


_gshell._run_interp_with_econforge = _force_scipy_interp
# ---------------------------------------------------------------------------

OUT = os.path.join(os.path.dirname(__file__), "..", "output")
FIGOUT = os.path.join(OUT, "figures")
os.makedirs(FIGOUT, exist_ok=True)
MAX_DEPTH = 250
CRITERIA = [(1, 1), (2, 2), (3, 3)]
CUTOFF = 10
COLORS = {"microDiamond": "tab:green", "PinPoint": "tab:orange", "Semiflex": "tab:blue"}


def on_grid(depth, vals, grid):
    d = dict(zip(np.round(depth).astype(int), vals))
    return np.array([d.get(int(g), np.nan) for g in grid])


def run():
    data = C.load_all(max_depth=MAX_DEPTH)
    grid = np.arange(0, MAX_DEPTH + 1, dtype=float)
    mc_pdd = on_grid(data["mc"]["depth"], data["mc"]["pdd"], grid)

    rows = []
    gamma_store = {}  # (key, crit) -> gamma array
    for key in ["microDiamond", "PinPoint", "Semiflex"]:
        det_pdd = on_grid(data["det"][key]["depth"], data["det"][key]["pdd"], grid)
        valid = ~np.isnan(mc_pdd) & ~np.isnan(det_pdd)
        dep = grid[valid]; ref = mc_pdd[valid]; ev = det_pdd[valid]
        for (dp, dta) in CRITERIA:
            gamma = pymedphys.gamma(
                dep, ref, dep, ev,
                dose_percent_threshold=dp, distance_mm_threshold=dta,
                lower_percent_dose_cutoff=CUTOFF, interp_fraction=10,
                max_gamma=2.0, local_gamma=False, quiet=True,
            )
            g = gamma[~np.isnan(gamma)]
            passrate = 100.0 * np.sum(g <= 1) / len(g)
            rows.append({
                "detector": key, "criterion": f"{dp}%/{dta}mm",
                "pass_rate_%": round(passrate, 1),
                "mean_gamma": round(float(np.mean(g)), 3),
                "max_gamma": round(float(np.max(g)), 3),
                "n_eval_points": int(len(g)),
            })
            gamma_store[(key, f"{dp}%/{dta}mm")] = (dep, gamma)

    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(OUT, "gamma_summary.csv"), index=False)
    # append to combined workbook
    xlsx = os.path.join(OUT, "PDD_1x1_combined.xlsx")
    if os.path.exists(xlsx):
        with pd.ExcelWriter(xlsx, engine="openpyxl", mode="a", if_sheet_exists="replace") as xw:
            df.to_excel(xw, sheet_name="gamma_results", index=False)

    print(df.to_string(index=False))

    # histograms: one panel per criterion, detectors overlaid
    fig, axes = plt.subplots(1, 3, figsize=(13, 4))
    for ax, (dp, dta) in zip(axes, CRITERIA):
        for key in ["microDiamond", "PinPoint", "Semiflex"]:
            _, gamma = gamma_store[(key, f"{dp}%/{dta}mm")]
            g = gamma[~np.isnan(gamma)]
            ax.hist(g, bins=np.linspace(0, 2, 21), histtype="step", lw=1.5,
                    color=COLORS[key], label=key)
        ax.axvline(1.0, color="k", ls="--", lw=1)
        ax.set_title(f"{dp}%/{dta} mm")
        ax.set_xlabel("gamma index")
        ax.set_ylabel("count")
        ax.legend(fontsize=7)
    fig.suptitle("1D gamma index distributions - measured vs TPS, 1x1 cm^2 PDD")
    fig.tight_layout()
    p = os.path.join(FIGOUT, "Figure5_gamma_histograms.png")
    fig.savefig(p, dpi=200)
    plt.close(fig)
    print("Wrote", p)

    # gamma vs depth (2%/2mm) for context
    fig, ax = plt.subplots(figsize=(10, 4))
    for key in ["microDiamond", "PinPoint", "Semiflex"]:
        dep, gamma = gamma_store[(key, "2%/2mm")]
        ax.plot(dep, gamma, color=COLORS[key], lw=1.0, label=key)
    ax.axhline(1.0, color="k", ls="--", lw=1)
    ax.set_xlim(0, MAX_DEPTH); ax.set_xlabel("Depth (mm)"); ax.set_ylabel("gamma (2%/2 mm)")
    ax.set_title("Gamma index vs depth (2%/2 mm) - measured vs TPS, 1x1")
    ax.grid(True, alpha=0.3); ax.legend(fontsize=8)
    fig.tight_layout()
    p = os.path.join(FIGOUT, "Figure6_gamma_vs_depth.png")
    fig.savefig(p, dpi=200)
    plt.close(fig)
    print("Wrote", p)


if __name__ == "__main__":
    run()
