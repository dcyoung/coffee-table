import json
import os
import os.path as osp

import cv2
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageFilter
from regex import W


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
    depth_map_im_raw = Image.fromarray((255.0 * depth_grid_norm).astype(np.uint8))
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
    quantized_depth_values = sorted(list(np.unique(depth_grid_quant)))

    # Plot quantized heatmap
    plt.figure()
    p = plt.imshow(depth_grid_quant)
    clb = plt.colorbar(p)
    clb.ax.set_title("Water Depth (m)", fontsize=8)
    plt.title(
        f"Quantized Depth Map: {args.levels} depths\n{[round(z, 2) for z in quantized_depth_values]}m"
    )
    plt.xlabel("X (100 m)")
    plt.ylabel("Y (100 m)")
    plt.savefig(
        osp.join(output_dir, "depth_map_quantized_plot.png"), dpi=1000,
    )
    plt.close()

    # Create masks for the layers
    layer_output_dir = osp.join(output_dir, "layer_masks")
    os.makedirs(layer_output_dir, exist_ok=True)
    for layer_idx, layer_depth in enumerate(quantized_depth_values[1:]):
        layer_mask = depth_grid_quant >= layer_depth
        layer_mask_im = Image.fromarray(255 * layer_mask.astype(np.uint8))
        layer_mask_im.save(osp.join(layer_output_dir, f"layer_{layer_idx}.png"))

        wip = layer_mask.astype(np.uint8) * 255
        # Scale up
        scale_up_factor = 4
        for i in range(scale_up_factor // 2):
            wip = cv2.pyrUp(wip)
        for i in range(15):
            wip = cv2.medianBlur(wip, 7)
        for i in range(scale_up_factor // 2):
            wip = cv2.pyrDown(wip)
        # Threshold back
        result = wip >= 128
        Image.fromarray(result).save(
            osp.join(layer_output_dir, f"layer_{layer_idx}_smoothed.png")
        )

        result = 255 * result.astype(np.uint8)
        contours, _ = cv2.findContours(result, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # cv2.imwrite(
        #     osp.join(layer_output_dir, f"layer_{layer_idx}_contours.jpg"),
        #     cv2.drawContours(
        #         cv2.cvtColor(result, cv2.COLOR_GRAY2RGB), contours, -1, (0, 255, 0), 3,
        #     ),
        # )
        # Normalize to range 0:1
        layer_shapes = []
        for contour in contours:
            c = np.squeeze(contour, axis=1).astype(np.float32)
            c[:, 0] /= result.shape[1]
            c[:, 1] /= result.shape[0]
            layer_shapes.append({"vertices": c.tolist()})

        with open(
            osp.join(layer_output_dir, f"layer_{layer_idx}_contours.json"), "w"
        ) as f:

            json.dump(
                layer_shapes, f,
            )

    # Plot yo woman's curves
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
