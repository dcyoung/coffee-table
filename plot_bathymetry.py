import os
import os.path as osp

import matplotlib.pyplot as plt
import numpy as np


def _plot_histogram(data):
    fig = plt.figure()
    # plot
    plt.hist(data)
    plt.title("Depth Readings Histogram (m)")
    plt.ylabel("# of depth readings")
    plt.xlabel("Water depth (m)")
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


def _plot_depth_3D_as_height_map(data, title: str = "Water Depth - height map"):
    x, y = np.meshgrid(range(data.shape[0]), range(data.shape[1]))

    fig = plt.figure()
    # plot
    ax = fig.add_subplot(111, projection="3d")
    ax.plot_surface(x, y, np.transpose(data))
    plt.title(title)
    ax.set_xlabel("X (100 m)")
    ax.set_ylabel("Y (100 m)")
    ax.set_zlabel("Z (m)")
    ax.view_init(15, 35)
    fig.tight_layout()
    return fig


def _plot_depth_3D_as_contours(
    data, levels=None, title: str = "Water Depth - Contours"
):
    x, y = np.meshgrid(range(data.shape[0]), range(data.shape[1]))

    fig = plt.figure()
    # plot
    ax = fig.add_subplot(111, projection="3d")
    ax.contour3D(x, y, np.transpose(data), 50, cmap="binary", levels=levels)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    plt.title(title)
    ax.set_xlabel("X (100 m)")
    ax.set_ylabel("Y (100 m)")
    ax.set_zlabel("Z (m)")
    ax.view_init(30, 35)
    fig.tight_layout()
    return fig


def _plot_depth_3D_wireframe(data, title: str = "Water Depth - Wireframe"):
    x, y = np.meshgrid(range(data.shape[0]), range(data.shape[1]))

    fig = plt.figure()
    # plot
    ax = plt.axes(projection="3d")
    ax.plot_wireframe(x, y, np.transpose(data), color="black")
    plt.title(title)
    ax.set_xlabel("X (100 m)")
    ax.set_ylabel("Y (100 m)")
    ax.set_zlabel("Z (m)")
    fig.tight_layout()
    return fig


def _plot_depth_3D_surface(data, title: str = "Water Depth - Surface"):
    x, y = np.meshgrid(range(data.shape[0]), range(data.shape[1]))

    fig = plt.figure()
    # plot
    ax = plt.axes(projection="3d")
    ax.plot_surface(
        x, y, np.transpose(data), rstride=1, cstride=1, cmap="viridis", edgecolor="none"
    )
    plt.title(title)
    ax.set_xlabel("X (100 m)")
    ax.set_ylabel("Y (100 m)")
    ax.set_zlabel("Z (m)")
    fig.tight_layout()
    return fig


def main(args):
    print("Loading data...")
    # data provided as a grid w/ 100m spacing, with z-depth values representing water depth
    # Depth units are in cm, increasing positive depths. Negative values indicate intertidal.
    depth_grid = np.loadtxt(args.input, skiprows=7)
    depth_grid /= 100.0  # convert cm to meters

    depth_clip_min_cm = 0
    depth_clip_max_cm = None

    # # Include intertidal:
    # depth_grid -= depth_grid.min()
    # depth_grid = np.clip(depth_grid, a_min=depth_clip_min_cm, a_max=depth_clip_max_cm)

    # Ignore intertidal
    depth_grid = np.clip(depth_grid, a_min=depth_clip_min_cm, a_max=depth_clip_max_cm)
    depth_grid -= depth_grid.min()

    print("Grid shape: {0}".format(depth_grid.shape))
    print(f"Max depth: {depth_grid.max()}m")

    inverted_depth_grid = -(depth_grid - np.amax(depth_grid))

    os.makedirs(args.output, exist_ok=True)

    print("Creating histogram...")
    fig = _plot_histogram(depth_grid.flatten())
    plt.savefig(osp.join(args.output, "histogram.jpg"))
    plt.close()

    print("Creating heatmap...")
    fig = _plot_depth_as_heat_map(depth_grid)
    plt.savefig(osp.join(args.output, "heatmap.jpg"))
    plt.close()

    for is_inverted in (True, False):
        data = inverted_depth_grid if is_inverted else depth_grid
        fname_suffix = "_inverted" if is_inverted else ""
        title_suffix = "\nInverted" if is_inverted else ""

        print("Creating 3D contour plot...")
        fig = _plot_depth_3D_as_contours(
            data, title=f"Water Depth Contours{title_suffix}"
        )
        plt.savefig(osp.join(args.output, f"contours{fname_suffix}.jpg"))
        plt.close()

        print("Creating 3D wireframe plot...")
        fig = _plot_depth_3D_wireframe(
            data, title=f"Water Depth Wireframe{title_suffix}"
        )
        plt.savefig(osp.join(args.output, f"wireframe{fname_suffix}.jpg"))
        plt.close()

        print("Creating 3D heightmap plot...")
        fig = _plot_depth_3D_as_height_map(data, title=f"Water Depthmap{title_suffix}")
        plt.savefig(osp.join(args.output, f"heightmap{fname_suffix}.jpg"))
        plt.close()

        print("Creating 3D surface plot...")
        fig = _plot_depth_3D_surface(data, title=f"Water Depth Surface{title_suffix}")
        plt.savefig(osp.join(args.output, f"surface{fname_suffix}.jpg"))
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
    args = parser.parse_args()

    print(args)
    main(args)
