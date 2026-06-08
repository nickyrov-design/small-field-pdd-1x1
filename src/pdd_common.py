"""
Shared data-loading and processing utilities for the 1x1 cm^2 PDD analysis.

Addresses reviewer reproducibility comments (2.7, 2.8): all data extraction,
the Monte Carlo depth-reversal correction, normalisation, and the deviation
metric definition live here in one auditable place.

Deviation convention (reviewer comment 3.2):
    deviation(%) = (D_measured - D_TPS) / D_TPS * 100
Each PDD is normalised to its own dose maximum (dmax) (reviewer comment 3.3),
i.e. PDD(d) = 100 * dose(d) / max(dose).
"""
from __future__ import annotations
import os
import numpy as np
import openpyxl

DATA_DIR = os.environ.get("PDD_DATA_DIR", os.path.join(os.path.dirname(__file__), "..", "data"))

# detector key -> (filename, sheet name, display label)
DETECTORS = {
    "microDiamond": ("microDiamond.xlsx", "1x1", "microDiamond"),
    "PinPoint":     ("PinPoint 3D.xlsx",  "1x1", "PinPoint"),
    "Semiflex":     ("Semiflex.xlsx",     "1x1", "Semiflex"),
}
MC_FILE = ("MonteCarlo (Golden Data).xlsx", "1X1")


def _read_depth_dose(path, sheet):
    """Return (depth, dose) numpy arrays from columns A/B, keeping only rows
    where both are numeric and depth is a plausible value (0..400 mm)."""
    wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
    ws = wb[sheet]
    depth, dose = [], []
    for row in ws.iter_rows(values_only=True):
        a, b = row[0], row[1]
        if isinstance(a, (int, float)) and isinstance(b, (int, float)) and 0 <= a <= 400:
            depth.append(float(a))
            dose.append(float(b))
    wb.close()
    return np.asarray(depth), np.asarray(dose)


def load_detector(key):
    """Load a detector 1x1 PDD: returns (depth_mm, raw_dose)."""
    fname, sheet, _ = DETECTORS[key]
    return _read_depth_dose(os.path.join(DATA_DIR, fname), sheet)


def load_mc():
    """Load the Monaco TPS 1x1 PDD with the depth-reversal corrected.

    The raw workbook stores the PDD deepest-first: as read, dose increases
    with listed depth and peaks at 286 mm (unphysical). Reversing the dose
    array places dmax at ~14 mm with a ~22% surface dose. This matches the
    original analysis output (csv's/mcdata.csv). Returns (depth_mm, raw_dose).
    """
    depth, dose = _read_depth_dose(os.path.join(DATA_DIR, MC_FILE[0]), MC_FILE[1])
    dose = dose[::-1]                       # flip dose to surface-first
    return depth, dose                      # depth stays ascending 0..N


def normalise(dose):
    """Normalise a dose array to its maximum (dmax), in percent."""
    return 100.0 * dose / np.max(dose)


def dmax_info(depth, dose):
    """Return (dmax_depth_int_mm, dmax_depth_interp_mm, dmax_dose).

    dmax_depth_interp uses a 3-point parabolic vertex fit around the peak
    sample for sub-millimetre estimation of the maximum position.
    """
    i = int(np.argmax(dose))
    d_int = float(depth[i])
    d_interp = d_int
    if 0 < i < len(depth) - 1:
        y0, y1, y2 = dose[i - 1], dose[i], dose[i + 1]
        denom = (y0 - 2 * y1 + y2)
        if denom != 0:
            # vertex offset in sample units, * step
            offset = 0.5 * (y0 - y2) / denom
            step = depth[i + 1] - depth[i]
            d_interp = d_int + offset * step
    return d_int, d_interp, float(dose[i])


def common_grid(depth_a, depth_b):
    """Integer-mm depths present in both curves, sorted ascending."""
    sa = set(np.round(depth_a).astype(int))
    sb = set(np.round(depth_b).astype(int))
    return np.array(sorted(sa & sb), dtype=float)


def deviation(depth_det, pdd_det, depth_mc, pdd_mc, grid=None):
    """Percentage deviation (meas - TPS)/TPS*100 on a common depth grid.

    Returns (grid_depth, deviation_percent). pdd_* must already be normalised.
    Points where TPS PDD == 0 are returned as nan.
    """
    if grid is None:
        grid = common_grid(depth_det, depth_mc)
    dd = dict(zip(np.round(depth_det).astype(int), pdd_det))
    dm = dict(zip(np.round(depth_mc).astype(int), pdd_mc))
    dev = []
    for d in grid:
        di = int(round(d))
        td = dm.get(di, np.nan)
        md = dd.get(di, np.nan)
        dev.append((md - td) / td * 100.0 if (td and not np.isnan(td)) else np.nan)
    return grid, np.asarray(dev)


def load_all(max_depth=250.0):
    """Load and normalise everything needed for the 1x1 analysis.

    Returns a dict with raw + normalised curves for MC and each detector,
    restricted to depths <= max_depth for the detectors and MC alike on a
    shared integer grid. dmax info per curve is included.
    """
    mc_depth, mc_dose = load_mc()
    out = {"mc": {"depth": mc_depth, "dose": mc_dose,
                  "pdd": normalise(mc_dose), "dmax": dmax_info(mc_depth, mc_dose)}}
    dets = {}
    for key in DETECTORS:
        dep, dose = load_detector(key)
        dets[key] = {"depth": dep, "dose": dose,
                     "pdd": normalise(dose), "dmax": dmax_info(dep, dose)}
    out["det"] = dets
    out["max_depth"] = max_depth
    return out
