import json
import os
import os.path as osp
import subprocess
import sys
from tempfile import NamedTemporaryFile

import cv2
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from common.data_helpers import load_data
from common.quantize import get_contours, quantize_depth_grid, smooth_layer_mask
from common.viz import (
    _plot_contour_results,
    _plot_depth_3D_as_contours,
    _plot_histogram,
    plot_polys,
)
from tqdm import tqdm


def main(args):
    output_dir = args.output
    os.makedirs(output_dir, exist_ok=True)
    with open(osp.join(output_dir, "args.json"), "w") as f:
        json.dump(vars(args), f)

    print("Loading data...")
    depth_grid = load_data(
        fpath=args.input,
        depth_unit_m=args.depth_unit_m,
        depth_min_m=args.depth_min_m,
        depth_max_m=args.depth_max_m,
        max_z_score=args.max_z_score,
    )

    max_depth_m = depth_grid.max()
    depth_grid_norm = depth_grid / depth_grid.max()

    print(f"Max depth: {max_depth_m}m")

    print("Creating plots...")

    # Histogram
    fig = _plot_histogram(depth_grid.flatten())
    plt.savefig(osp.join(args.output, "histogram.jpg"))
    plt.close()

    # Raw depth map image
    # yields a grayscale image w/ pixel values in range 0-255 corresponding to 0-max-depth)
    depth_map_im_raw = Image.fromarray((255.0 * depth_grid_norm).astype(np.uint8))
    depth_map_im_raw.save(osp.join(output_dir, "depth_map_raw.png"))

    plt.figure()
    p = plt.imshow(depth_grid_norm * max_depth_m)
    clb = plt.colorbar(p)
    clb.ax.set_title("Water Depth (m)", fontsize=8)
    plt.title("Raw Depth Map")
    plt.xlabel(f"X ({args.cell_size_m} m)")
    plt.ylabel(f"Y ({args.cell_size_m} m)")
    plt.savefig(
        osp.join(output_dir, "depth_map_raw_plot.png"),
        dpi=1000,
    )
    plt.close()

    quantize_results = quantize_depth_grid(
        depth_grid=depth_grid,
        levels=args.levels,
        quantize_depth_start_m=args.quantize_depth_start_m,
    )
    print(
        f"Quantizing w/ {args.levels} discrete depth values: {[round(max_depth_m*z, 1) for z in quantize_results.quantized_depth_values_norm]}m"
    )
    quantize_results.depth_map_im_quant.save(
        osp.join(output_dir, "depth_map_quantized.png")
    )

    with open(osp.join(output_dir, "quantized_depth_values.json"), "w") as f:
        json.dump(quantize_results.quantized_depth_values.tolist(), f)

    # Plot quantized heatmap
    plt.figure()
    p = plt.imshow(quantize_results.depth_grid_quant)
    clb = plt.colorbar(p)
    clb.ax.set_title("Water Depth (m)", fontsize=8)
    plt.title(
        f"Quantized Depth Map: {args.levels} depths\n{[round(z, 1) for z in quantize_results.quantized_depth_values]}m"
    )
    plt.xlabel(f"X ({args.cell_size_m} m)")
    plt.ylabel(f"Y ({args.cell_size_m} m)")
    plt.savefig(
        osp.join(output_dir, "depth_map_quantized_plot.png"),
        dpi=1000,
    )
    plt.close()

    # Create masks for the layers
    layer_output_dir = osp.join(output_dir, "layer_masks")
    os.makedirs(layer_output_dir, exist_ok=True)
    for layer_idx, layer_depth in tqdm(
        enumerate(quantize_results.quantized_depth_values[1:])
    ):
        # Retrieve the mask for this layer. If configured for the first layer, ignore the quantization and take anything with a depth reading > 0
        layer_mask = (
            quantize_results.depth_grid_quant > 0
            if layer_idx == 0 and args.force_first_layer
            else quantize_results.depth_grid_quant >= layer_depth
        )
        layer_mask_smoothed = smooth_layer_mask(
            layer_mask, scale_up_factor=args.scale_up_factor
        )

        layer_mask_im = Image.fromarray(255 * layer_mask.astype(np.uint8))
        layer_mask_im.save(osp.join(layer_output_dir, f"layer_{layer_idx}.png"))

        im_smoothed = Image.fromarray(np.invert(layer_mask_smoothed))
        im_smoothed.save(osp.join(layer_output_dir, f"layer_{layer_idx}_smoothed.png"))

        with NamedTemporaryFile("w", suffix=".pnm") as f:
            # potrace raster-> svg required .pnm file as input
            im_smoothed.save(f.name)
            subprocess.run(
                [
                    "potrace",
                    f.name,
                    "-s",
                    "-o",
                    osp.join(layer_output_dir, f"layer_{layer_idx}_smoothed.svg"),
                ]
            )

        contour_results = get_contours(layer_mask=layer_mask_smoothed)
        with open(
            osp.join(layer_output_dir, f"layer_{layer_idx}_contours.json"), "w"
        ) as f:
            json.dump(
                contour_results.layer_shapes,
                f,
            )

        fig = plot_polys(contour_results.layer_shapes)
        plt.savefig(osp.join(layer_output_dir, f"layer_{layer_idx}_contours_viz.jpg"))
        plt.close()

        cv2.imwrite(
            osp.join(layer_output_dir, f"layer_{layer_idx}_contours.jpg"),
            _plot_contour_results(
                background=contour_results.layer_mask_bw,
                contours=contour_results.contours,
                hierarchy=contour_results.hierarchy,
            ),
        )

    # Plot contours
    fig = _plot_depth_3D_as_contours(
        data=quantize_results.depth_grid_quant,
        cell_size_m=args.cell_size_m,
        levels=args.levels,
        cmap="viridis",
        title=f"Depth as 3d contours. N-Levels={args.levels}",
    )
    plt.savefig(osp.join(output_dir, "separated_contours.jpg"), dpi=500)
    plt.close()

    # Plot inverted contours
    fig = _plot_depth_3D_as_contours(
        data=-(
            quantize_results.depth_grid_quant
            - np.amax(quantize_results.depth_grid_quant)
        ),
        cell_size_m=args.cell_size_m,
        levels=args.levels,
        cmap="viridis",
        title=f"Depth as 3d contours. N-Levels={args.levels}",
    )
    plt.savefig(osp.join(output_dir, "separated_contours_inverted.jpg"), dpi=500)
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
        help="The max z-score, beyond which data is clipped.",
    )
    parser.add_argument(
        "--levels",
        type=int,
        default=4,
        help="The number of evenly spaced contour levels. This includes the depth-0 contour. ie: N levels will correspond to N-1 output layers.",
    )
    parser.add_argument(
        "--quantize_depth_start_m",
        type=float,
        default=1.0,
        help="The starting depth for the first layer... beyond which subsequent layers will be evenly spaced. This helps to visualize shallow depths when overall water depth range is high.",
    )
    parser.add_argument(
        "--scale_up_factor",
        default=4,
        type=int,
        help="The scale up factor to use (multiple of 2) when smoothing.",
    )
    parser.add_argument(
        "--force_first_layer",
        type=str2bool,
        default=True,
        help="If True, force all depth > 0 to be included in the first layer. This helps with high depth range, causing the shallow areas be shorelines to be marked as 0.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=osp.join("output", "contour_plots"),
        help="Path to write plots.",
    )
    args = parser.parse_args()

    print(args)
    main(args)
