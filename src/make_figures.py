"""
Task B: Reproduce Figures 1-4 without truncated axes (reviewer comments 4.1, 4.4).

For each figure:
  - full (untruncated) y-axis so the build-up deviations are visible;
  - vertical dashed lines marking measured dmax and TPS dmax (comment 4.4a);
  - an inset zoomed to the post-build-up region (15-250 mm) so the few-percent
    structure remains readable despite the large build-up spike (comment 4.4b).
"""
from __future__ import annotations
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import pdd_common as C

OUT = os.path.join(os.path.dirname(__file__), "..", "output", "figures")
os.makedirs(OUT, exist_ok=True)
MAX_DEPTH = 250

COLORS = {"microDiamond": "tab:green", "PinPoint": "tab:orange", "Semiflex": "tab:blue"}


def get_dev(data, key, grid):
    mc = data["mc"]; det = data["det"][key]
    _, dev = C.deviation(det["depth"], det["pdd"], mc["depth"], mc["pdd"], grid=grid)
    return dev


def add_dmax_lines(ax, det_dmax, mc_dmax, label=True):
    ax.axvline(mc_dmax, color="0.4", ls="--", lw=1,
               label=f"TPS dmax ({mc_dmax:.1f} mm)" if label else None)
    ax.axvline(det_dmax, color="0.7", ls=":", lw=1,
               label=f"det. dmax ({det_dmax:.1f} mm)" if label else None)


def single_figure(data, key, title, fname):
    grid = np.arange(0, MAX_DEPTH + 1, dtype=float)
    dev = get_dev(data, key, grid)
    det_dmax = data["det"][key]["dmax"][1]
    mc_dmax = data["mc"]["dmax"][1]

    fig, ax = plt.subplots(figsize=(10, 4.2))
    ax.plot(grid, dev, color=COLORS[key], lw=1.1, label=key)
    ax.axhline(0, color="k", lw=0.6)
    add_dmax_lines(ax, det_dmax, mc_dmax)
    ax.set_xlim(0, MAX_DEPTH)
    ax.set_xlabel("Depth (mm)")
    ax.set_ylabel("Percentage Deviation (%)")
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper right", fontsize=8)

    # inset: post-build-up detail
    axin = inset_axes(ax, width="55%", height="42%", loc="center right", borderpad=1.2)
    m = grid >= 15
    axin.plot(grid[m], dev[m], color=COLORS[key], lw=1.0)
    axin.axhline(0, color="k", lw=0.6)
    axin.set_xlim(15, MAX_DEPTH)
    lo = np.nanmin(dev[m]); hi = np.nanmax(dev[m])
    pad = 0.5
    axin.set_ylim(np.floor(lo - pad), np.ceil(hi + pad))
    axin.grid(True, alpha=0.3)
    axin.set_title("post-build-up detail (15-250 mm)", fontsize=7)
    axin.tick_params(labelsize=7)

    fig.tight_layout()
    p = os.path.join(OUT, fname)
    fig.savefig(p, dpi=200)
    plt.close(fig)
    print("Wrote", p)


def overlay_figure(data, fname):
    grid = np.arange(0, MAX_DEPTH + 1, dtype=float)
    fig, ax = plt.subplots(figsize=(10, 4.6))
    for key in ["Semiflex", "PinPoint", "microDiamond"]:
        dev = get_dev(data, key, grid)
        ax.plot(grid, dev, color=COLORS[key], lw=1.1, label=f"{key} 1x1")
    ax.axhline(0, color="k", lw=0.6)
    mc_dmax = data["mc"]["dmax"][1]
    ax.axvline(mc_dmax, color="0.4", ls="--", lw=1, label=f"TPS dmax ({mc_dmax:.1f} mm)")
    ax.set_xlim(0, MAX_DEPTH)
    ax.set_xlabel("Depth (mm)")
    ax.set_ylabel("Percentage Deviation (%)")
    ax.set_title("TPS versus Detectors PDD Deviations - 1x1")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper right", fontsize=8)

    axin = inset_axes(ax, width="55%", height="42%", loc="center right", borderpad=1.2)
    m = grid >= 15
    for key in ["Semiflex", "PinPoint", "microDiamond"]:
        dev = get_dev(data, key, grid)
        axin.plot(grid[m], dev[m], color=COLORS[key], lw=1.0)
    axin.axhline(0, color="k", lw=0.6)
    axin.set_xlim(15, MAX_DEPTH)
    axin.set_ylim(-4, 9)
    axin.grid(True, alpha=0.3)
    axin.set_title("post-build-up detail (15-250 mm)", fontsize=7)
    axin.tick_params(labelsize=7)

    fig.tight_layout()
    p = os.path.join(OUT, fname)
    fig.savefig(p, dpi=200)
    plt.close(fig)
    print("Wrote", p)


def main():
    data = C.load_all(max_depth=MAX_DEPTH)
    single_figure(data, "microDiamond", "TPS versus microDiamond - 1x1 Field Size", "Figure1_microDiamond.png")
    single_figure(data, "Semiflex",     "TPS versus Semiflex - 1x1 Field Size",     "Figure2_Semiflex.png")
    single_figure(data, "PinPoint",     "TPS versus PinPoint - 1x1 Field Size",     "Figure3_PinPoint.png")
    overlay_figure(data, "Figure4_overlay.png")


if __name__ == "__main__":
    main()
