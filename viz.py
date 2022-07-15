import matplotlib.pyplot as plt
import numpy as np


def _plot_histogram(data):
    data_mean = np.mean(data, axis=None)
    data_std = np.std(data, axis=None)
    fig = plt.figure()
    # plot
    plt.hist(data, color="c", edgecolor="k")
    plt.axvline(data_mean, color="k", linestyle="dashed")
    for i in range(3):
        plt.axvline(data_mean + (i + 1) * data_std, color="y", linestyle="dashed")

    plt.title("Depth Readings Histogram (m)")
    plt.ylabel("# of depth readings")
    plt.xlabel("Water depth (m)")
    fig.tight_layout()
    return fig


def _plot_depth_as_heat_map(data, cell_size_m: int):
    fig = plt.figure()
    # plot
    p = plt.imshow(data, cmap="hot", interpolation="nearest")
    plt.title("Water Depth Heat Map")
    plt.colorbar(p)
    plt.xlabel(f"X ({cell_size_m} m)")
    plt.ylabel(f"Y ({cell_size_m} m)")
    fig.tight_layout()
    return fig


def _plot_depth_3D_as_height_map(
    data, cell_size_m: int, title: str = "Water Depth - height map"
):
    x, y = np.meshgrid(range(data.shape[0]), range(data.shape[1]))

    fig = plt.figure()
    # plot
    ax = fig.add_subplot(111, projection="3d")
    ax.plot_surface(x, y, np.transpose(data))
    plt.title(title)
    plt.xlabel(f"X ({cell_size_m} m)")
    plt.ylabel(f"Y ({cell_size_m} m)")
    ax.set_zlabel("Z (m)")
    ax.view_init(15, 35)
    fig.tight_layout()
    return fig


def _plot_depth_3D_as_contours(
    data,
    cell_size_m: int,
    levels=None,
    title: str = "Water Depth - Contours",
    cmap: str = "binary",
):
    x, y = np.meshgrid(range(data.shape[0]), range(data.shape[1]))

    fig = plt.figure()
    # plot
    ax = fig.add_subplot(111, projection="3d")
    ax.contour3D(x, y, np.transpose(data), 50, cmap=cmap, levels=levels)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    plt.title(title)
    plt.xlabel(f"X ({cell_size_m} m)")
    plt.ylabel(f"Y ({cell_size_m} m)")
    ax.set_zlabel("Z (m)")
    ax.view_init(30, 35)
    fig.tight_layout()
    return fig


def _plot_depth_3D_wireframe(
    data, cell_size_m: int, title: str = "Water Depth - Wireframe"
):
    x, y = np.meshgrid(range(data.shape[0]), range(data.shape[1]))

    fig = plt.figure()
    # plot
    ax = plt.axes(projection="3d")
    ax.plot_wireframe(x, y, np.transpose(data), color="black")
    plt.title(title)
    plt.xlabel(f"X ({cell_size_m} m)")
    plt.ylabel(f"Y ({cell_size_m} m)")
    ax.set_zlabel("Z (m)")
    fig.tight_layout()
    return fig


def _plot_depth_3D_surface(
    data, cell_size_m: int, title: str = "Water Depth - Surface"
):
    x, y = np.meshgrid(range(data.shape[0]), range(data.shape[1]))

    fig = plt.figure()
    # plot
    ax = plt.axes(projection="3d")
    ax.plot_surface(
        x, y, np.transpose(data), rstride=1, cstride=1, cmap="viridis", edgecolor="none"
    )
    plt.title(title)
    plt.xlabel(f"X ({cell_size_m} m)")
    plt.ylabel(f"Y ({cell_size_m} m)")
    ax.set_zlabel("Z (m)")
    fig.tight_layout()
    return fig
