import os
import os.path as osp

import matplotlib.pyplot as plt
import numpy as np

from data_helpers import load_data
from viz import (
    _plot_depth_3D_as_contours,
    _plot_depth_3D_as_height_map,
    _plot_depth_3D_surface,
    _plot_depth_3D_wireframe,
    _plot_depth_as_heat_map,
    _plot_histogram,
)


def main(args):
    print("Loading data...")
    depth_grid = load_data(
        fpath=args.input,
        depth_unit_m=args.depth_unit_m,
        depth_min_m=args.depth_min_m,
        depth_max_m=args.depth_max_m,
        max_z_score=args.max_z_score,
    )

    print("Grid shape: {0}".format(depth_grid.shape))
    print(f"Max depth: {depth_grid.max()}m")

    inverted_depth_grid = -(depth_grid - np.amax(depth_grid))

    os.makedirs(args.output, exist_ok=True)

    print("Creating histogram...")
    fig = _plot_histogram(depth_grid.flatten())
    plt.savefig(osp.join(args.output, "histogram.jpg"))
    plt.close()

    print("Creating heatmap...")
    fig = _plot_depth_as_heat_map(depth_grid, cell_size_m=args.cell_size_m)
    plt.savefig(osp.join(args.output, "heatmap.jpg"))
    plt.close()

    for is_inverted in (True, False):
        data = inverted_depth_grid if is_inverted else depth_grid
        fname_suffix = "_inverted" if is_inverted else ""
        title_suffix = "\nInverted" if is_inverted else ""

        print("Creating 3D contour plot...")
        fig = _plot_depth_3D_as_contours(
            data,
            cell_size_m=args.cell_size_m,
            title=f"Water Depth Contours{title_suffix}",
        )
        plt.savefig(osp.join(args.output, f"contours{fname_suffix}.jpg"))
        plt.close()

        print("Creating 3D wireframe plot...")
        fig = _plot_depth_3D_wireframe(
            data,
            cell_size_m=args.cell_size_m,
            title=f"Water Depth Wireframe{title_suffix}",
        )
        plt.savefig(osp.join(args.output, f"wireframe{fname_suffix}.jpg"))
        plt.close()

        print("Creating 3D heightmap plot...")
        fig = _plot_depth_3D_as_height_map(
            data, cell_size_m=args.cell_size_m, title=f"Water Depthmap{title_suffix}"
        )
        plt.savefig(osp.join(args.output, f"heightmap{fname_suffix}.jpg"))
        plt.close()

        print("Creating 3D surface plot...")
        fig = _plot_depth_3D_surface(
            data,
            cell_size_m=args.cell_size_m,
            title=f"Water Depth Surface{title_suffix}",
        )
        plt.savefig(osp.join(args.output, f"surface{fname_suffix}.jpg"))
        plt.close()


if __name__ == "__main__":
    import argparse

    def str2bool(v):
        if isinstance(v, bool):
            return v
        if v.lower() in ("yes", "true", "t", "y", "1"):
            return True
        elif v.lower() in ("no", "false", "f", "n", "0"):
            return False
        else:
            raise argparse.ArgumentTypeError("Boolean value expected.")

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help="Path to GIS ASCII, of GeoTiff data file.",
    )
    parser.add_argument(
        "--cell_size_m",
        type=int,
        required=True,
        help="The resolution of x,y readings in m.",
    )
    parser.add_argument(
        "--depth_unit_m",
        type=float,
        required=True,
        help="The resolution of z readings in m.",
    )
    parser.add_argument(
        "--depth_min_m",
        type=float,
        default=0.0,
        help="Min depth in meters, values will be clipped.",
    )
    parser.add_argument(
        "--depth_max_m",
        type=float,
        default=None,
        help="If provided and > 0, Max depth in meters, values will be clipped.",
    )
    parser.add_argument(
        "--max_z_score",
        type=float,
        default=0,
        help="The number of evenly spaced contour levels.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=osp.join("output", "bathymetry_plots"),
        help="Path to write plots.",
    )
    args = parser.parse_args()

    print(args)
    main(args)
