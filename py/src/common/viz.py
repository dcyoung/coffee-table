from typing import Any, List

import cv2
import matplotlib.pyplot as plt
import numpy as np


def _plot_histogram(data):
    data_mean = np.mean(data, axis=None)
    data_std = np.std(data, axis=None)
    fig = plt.figure()

    # Plot Data
    plt.hist(data, color="c", edgecolor="k")

    # Plot mean + std-dev
    plt.axvline(data_mean, color="k", linestyle="dashed", label="mean")
    for i in range(3):
        plt.axvline(
            data_mean + (i + 1) * data_std,
            color="y",
            linestyle="dashed",
            label=f"{i+1} std",
        )

    # Plot max
    plt.axvline(np.amax(data), color="r", linestyle="dotted", label="Max Depth")

    plt.title("Depth Readings Histogram (m)")
    plt.ylabel("# of depth readings")
    plt.xlabel("Water depth (m)")
    plt.legend()
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


def plot_polys(
    shapes,
    title: str = "Polygon",
    include_original: bool = True,
    include_simplified: bool = True,
    max_labels=35,
):
    fig = plt.figure(figsize=(12, 12))
    label_idx = 0

    def _internal_plot_poly(verts: List[List[float]], label: str = None):
        nonlocal label_idx
        plt.plot(
            [xy[0] for xy in verts],
            [1 - xy[1] for xy in verts],
            label=f"{label}x{len(verts)}" if label_idx < max_labels else None,
        )

    for i, shape in enumerate(shapes):
        if include_original:
            _internal_plot_poly(verts=shape["vertices"], label=f"{i}_orig")
        if include_simplified:
            _internal_plot_poly(verts=shape["simplified"], label=f"{i}_simp")

        for j, hole in enumerate(shape["holes"]):
            if include_original:
                _internal_plot_poly(verts=hole["vertices"], label=f"{i}_{j}_orig")
            if include_simplified:
                _internal_plot_poly(verts=hole["simplified"], label=f"{i}_{j}_simp")
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.legend()
    plt.title(title)
    fig.tight_layout()
    return fig


def _plot_contour_results(background: np.ndarray, contours: Any, hierarchy: Any) -> Any:
    return cv2.drawContours(
        cv2.drawContours(
            cv2.cvtColor(background, cv2.COLOR_GRAY2RGB),
            [
                contours[c_idx]
                for c_idx in range(hierarchy.shape[1])
                if hierarchy[0][c_idx][3] == -1
            ],
            -1,
            (0, 255, 0),
            3,
        ),
        [
            contours[c_idx]
            for c_idx in range(hierarchy.shape[1])
            if hierarchy[0][c_idx][3] != -1
        ],
        -1,
        (255, 0, 0),
        3,
    )


def viz_rotated_rectangle(
    background: np.ndarray, box: np.ndarray, color=None
) -> np.ndarray:
    if color is None:
        color = (0, 0, 255)
    return cv2.drawContours(background, [box], 0, color, 2)
