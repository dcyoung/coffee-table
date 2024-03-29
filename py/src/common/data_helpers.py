from dataclasses import dataclass
import os
from pathlib import Path
from typing import Optional, TextIO, Union

import numpy as np
from PIL import Image
from scipy import stats


@dataclass(frozen=True)
class Config:
    cell_size_m: int
    depth_unit_m: float
    depth_min_m: float
    depth_max_m: float
    max_z_score: float
    levels: int
    quantize_depth_start_m: float
    scale_up_factor: int
    force_first_layer: bool


def load_raw(
    fpath: Union[str, Path, TextIO],
) -> np.ndarray:
    fname = os.path.basename(fpath) if isinstance(fpath, (str, Path)) else fpath.name
    # Read the data differently depending on type
    ext = os.path.splitext(fname)[1]
    if "asc" in ext.lower():
        # data provided as a grid w/ 100m spacing, with z-depth values representing water depth
        # Depth units are in cm, increasing positive depths. Negative values indicate intertidal.
        depth_grid = np.loadtxt(fpath, skiprows=7)
    elif fname.lower().endswith(".geo.tif") or "geotif" in ext.lower():
        with Image.open(fpath) as im:
            depth_grid = np.asarray(im).astype(np.float32)
        depth_grid = np.clip(depth_grid, a_min=None, a_max=0)
        depth_grid *= -1.0
    elif "tif" in ext.lower():
        with Image.open(fpath) as im:
            depth_grid = np.asarray(im).astype(np.float32)
        ground_z = depth_grid.max()
        depth_grid[np.where(depth_grid == 0)] = ground_z
        depth_grid -= depth_grid.min()
        depth_grid = depth_grid.max() - depth_grid
    else:
        raise NotImplementedError(f"Input data format not support: {ext}")

    return depth_grid


def load_data(
    fpath: Union[str, Path, TextIO],
    depth_unit_m: float = 1.0,
    depth_min_m: float = 0,
    depth_max_m: Optional[float] = None,
    max_z_score: float = 0,
) -> np.ndarray:
    depth_grid = load_raw(fpath=fpath)
    # Scale for depth units
    depth_grid *= depth_unit_m

    # Clip the data
    if depth_max_m and depth_max_m > 0:
        depth_grid = np.clip(depth_grid, a_min=depth_min_m, a_max=depth_max_m)
    else:
        depth_grid = np.clip(depth_grid, a_min=depth_min_m, a_max=None)
    depth_grid -= depth_grid.min()

    if max_z_score > 0:
        # Clip/remove/smooth any outliers (depth readings more than a configurable number of std-devs away from the mean)
        # x = µ + Zσ
        depth_clip_max_m = np.mean(depth_grid, axis=None) + max_z_score * stats.tstd(
            depth_grid, axis=None
        )
        print(
            f"Clipping data (for z score) to a max depth of {round(depth_clip_max_m, 1)}m"
        )
        depth_grid = np.clip(depth_grid, a_min=0, a_max=depth_clip_max_m)

    return depth_grid
