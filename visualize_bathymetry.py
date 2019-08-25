import os
import os.path as osp
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def _plot_histogram(data):
    fig = plt.figure()
    # plot
    plt.hist(data)

    plt.title("Depth Readings Histogram (m)")
    fig.tight_layout()
    return fig


def _plot_depth_as_heat_map(data):
    fig = plt.figure()
    # plot
    p = plt.imshow(data, cmap="hot", interpolation="nearest")
    plt.title("Water Depth Heat Map")
    plt.colorbar(p)
    plt.xlabel("X (100 m)")
    plt.ylabel("Y (100 m)")
    fig.tight_layout()
    return fig


def _plot_depth_3D_as_height_map(data):
    z = -(data - np.amax(data))
    x, y = np.meshgrid(range(z.shape[0]), range(z.shape[1]))

    fig = plt.figure()
    # plot
    ax = fig.add_subplot(111, projection="3d")
    ax.plot_surface(x, y, np.transpose(z))
    plt.title("Depth as 3d height map")
    ax.set_xlabel("X (100 m)")
    ax.set_ylabel("Y (100 m)")
    ax.set_zlabel("Z (m)")
    fig.tight_layout()
    return fig


def _plot_depth_3D_as_contours(data):
    z = -(data - np.amax(data))
    x, y = np.meshgrid(range(z.shape[0]), range(z.shape[1]))

    fig = plt.figure()
    # plot
    ax = fig.add_subplot(111, projection="3d")
    ax.contour3D(x, y, np.transpose(z), 50, cmap="binary")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    plt.title("Depth as 3d contours")
    ax.set_xlabel("X (100 m)")
    ax.set_ylabel("Y (100 m)")
    ax.set_zlabel("Z (m)")
    ax.view_init(60, 35)
    fig.tight_layout()
    return fig


def _plot_depth_3D_wireframe(data):
    z = -(data - np.amax(data))
    x, y = np.meshgrid(range(z.shape[0]), range(z.shape[1]))

    fig = plt.figure()
    # plot
    ax = plt.axes(projection="3d")
    ax.plot_wireframe(x, y, np.transpose(z), color="black")
    plt.title("Wireframe")
    ax.set_xlabel("X (100 m)")
    ax.set_ylabel("Y (100 m)")
    ax.set_zlabel("Z (m)")
    fig.tight_layout()
    return fig


def _plot_depth_3D_surface(data):
    z = -(data - np.amax(data))
    x, y = np.meshgrid(range(z.shape[0]), range(z.shape[1]))

    fig = plt.figure()
    # plot
    ax = plt.axes(projection="3d")
    ax.plot_surface(
        x, y, np.transpose(z), rstride=1, cstride=1, cmap="viridis", edgecolor="none"
    )
    plt.title("Surface")
    ax.set_xlabel("X (100 m)")
    ax.set_ylabel("Y (100 m)")
    ax.set_zlabel("Z (m)")
    fig.tight_layout()
    return fig


def main(args):
    print("Reading file...")
    depth_grid = np.loadtxt(args.input, skiprows=7)
    depth_grid = depth_grid / 100.0  # convert cm to meters
    if args.clip:
        depth_grid = np.clip(depth_grid, a_min=0, a_max=None)

    print("Grid shape: {0}".format(depth_grid.shape))

    os.makedirs(args.output, exist_ok=True)

    # Plots
    print("Creating histogram...")
    fig = _plot_histogram(depth_grid)
    plt.savefig(osp.join(args.output, "histogram.png"))
    if args.viz:
        plt.show()
    plt.close()
    # exit(-1)

    print("Creating heatmap...")
    fig = _plot_depth_as_heat_map(depth_grid)
    plt.savefig(osp.join(args.output, "heatmap.png"))
    if args.viz:
        plt.show()
    plt.close()

    print("Creating 3D contour plot...")
    fig = _plot_depth_3D_as_contours(depth_grid)
    plt.savefig(osp.join(args.output, "contours.png"))
    if args.viz:
        plt.show()
    plt.close()

    print("Creating 3D wireframe plot...")
    fig = _plot_depth_3D_wireframe(depth_grid)
    plt.savefig(osp.join(args.output, "wireframe.png"))
    if args.viz:
        plt.show()
    plt.close()

    print("Creating 3D heightmap plot...")
    fig = _plot_depth_3D_as_height_map(depth_grid)
    plt.savefig(osp.join(args.output, "heightmap.png"))
    if args.viz:
        plt.show()
    plt.close()

    print("Creating 3D surface plot...")
    fig = _plot_depth_3D_surface(depth_grid)
    plt.savefig(osp.join(args.output, "surface.png"))
    if args.viz:
        plt.show()
    plt.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=str,
        default=osp.join("resources", "bathymetry", "FullBay100", "msl1k.asc"),
        help="Path to GIS ASCII data file.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=osp.join("output", "bathymetry_plots"),
        help="Path to write plots.",
    )
    parser.add_argument(
        "--clip", action="store_true", help="If included, clip data to sea-level."
    )
    parser.add_argument(
        "--viz", action="store_true", help="If included, show results on screen."
    )
    args = parser.parse_args()

    print(args)
    main(args)
