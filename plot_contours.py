import os
import os.path as osp

import matplotlib.pyplot as plt
import numpy as np
import PIL


def plot_contours(ax, z_data, levels, cmap: str = "binary"):
    x, y = np.meshgrid(range(z_data.shape[0]), range(z_data.shape[1]))

    # plot
    ax.contourf3D(x, y, np.transpose(z_data), 50, cmap=cmap, levels=levels)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    ax.set_title(f"Depth as 3d contours. N-Levels={levels}")
    ax.set_xlabel("X (100 m)")
    ax.set_ylabel("Y (100 m)")
    ax.set_zlabel("Z (m)")
    ax.view_init(30, 45)


def main(args):
    print("Loading data...")
    # data provided as a grid w/ 100m spacing, with z-depth values representing water depth
    # Depth units are in cm, increasing positive depths. Negative values indicate intertidal.
    depth_grid = np.loadtxt(args.input, skiprows=7)

    depth_clip_min_cm = 0
    depth_clip_max_cm = None

    # # Include intertidal:
    # depth_grid -= depth_grid.min()
    # depth_grid = np.clip(depth_grid, a_min=depth_clip_min_cm, a_max=depth_clip_max_cm)

    # Ignore intertidal
    depth_grid = np.clip(depth_grid, a_min=depth_clip_min_cm, a_max=depth_clip_max_cm)
    depth_grid -= depth_grid.min()

    max_depth_cm = depth_grid.max()
    max_depth_m = max_depth_cm * 0.01

    depth_grid_norm = depth_grid / depth_grid.max()

    print(f"Max depth: {max_depth_m}m")

    print("Creating plots...")
    output_dir = args.output
    os.makedirs(output_dir, exist_ok=True)

    # Raw depth map image
    # yields a grayscale image w/ pixel values in range 0-255 corresponding to 0-max-depth)
    depth_map_im_raw = PIL.Image.fromarray((255.0 * depth_grid_norm).astype(np.uint8))
    depth_map_im_raw.save(osp.join(output_dir, "depth_map_raw.png"))

    plt.figure()
    p = plt.imshow(depth_grid_norm * max_depth_m)
    clb = plt.colorbar(p)
    clb.ax.set_title("Water Depth (m)", fontsize=8)
    plt.title("Raw Depth Map")
    plt.xlabel("X (100 m)")
    plt.ylabel("Y (100 m)")
    plt.savefig(
        osp.join(output_dir, "depth_map_raw_plot.png"), dpi=1000,
    )
    plt.close()

    # Quantize depth map
    depth_map_im_quant = depth_map_im_raw.quantize(args.levels)
    depth_map_im_quant.save(osp.join(output_dir, "depth_map_quantized.png"))

    # Convert image back to data
    # Convert back to RGB to avoid reduced colormap issues, and reduce back to 1 channel
    depth_grid_quant = np.array(depth_map_im_quant.convert("RGB"))[:, :, 0].astype(
        np.float32
    )
    # Convert from pixel range 0-255 back to depth range 0-max_depth
    depth_grid_quant *= max_depth_m / 255.0
    # Plot quantized heatmap
    plt.figure()
    p = plt.imshow(depth_grid_quant)
    clb = plt.colorbar(p)
    clb.ax.set_title("Water Depth (m)", fontsize=8)
    rounded_depths = [round(z, 2) for z in list(np.unique(depth_grid_quant))]
    plt.title(f"Quantized Depth Map: {args.levels} depths\n{rounded_depths}m")
    plt.xlabel("X (100 m)")
    plt.ylabel("Y (100 m)")
    plt.savefig(
        osp.join(output_dir, "depth_map_quantized_plot.png"), dpi=1000,
    )
    plt.close()

    # Plot contours
    plt.figure()
    ax = plt.axes(projection="3d")
    plot_contours(ax=ax, z_data=depth_grid_quant, levels=args.levels, cmap="viridis")
    plt.savefig(osp.join(output_dir, "separated_contours.jpg"), dpi=500)
    plt.close()

    # Plot inverted contours
    plt.figure()
    ax = plt.axes(projection="3d")
    plot_contours(
        ax=ax,
        z_data=-(depth_grid_quant - np.amax(depth_grid_quant)),
        levels=args.levels,
        cmap="viridis",
    )
    plt.savefig(osp.join(output_dir, "separated_contours_inverted.jpg"), dpi=500)
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
        default=osp.join("output", "contour_plots"),
        help="Path to write plots.",
    )
    parser.add_argument(
        "--levels",
        type=int,
        default=4,
        help="The number of evenly spaced contour levels.",
    )
    args = parser.parse_args()

    print(args)
    main(args)
