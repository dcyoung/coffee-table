import os
import numpy as np
from PIL import Image
from scipy import stats


def load_data(
    fpath: str,
    depth_unit_m: float = 1.0,
    depth_min_m: float = 0,
    depth_max_m: float = None,
    max_z_score: float = 0,
) -> np.ndarray:

    # Read the data differently depending on type
    ext = os.path.splitext(fpath)[1]
    if "asc" in ext.lower():
        # data provided as a grid w/ 100m spacing, with z-depth values representing water depth
        # Depth units are in cm, increasing positive depths. Negative values indicate intertidal.
        depth_grid = np.loadtxt(fpath, skiprows=7)
        depth_grid /= 100.0  # convert cm to meters
    elif fpath.lower().endswith(".geo.tif") or "geotif" in ext.lower():
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
