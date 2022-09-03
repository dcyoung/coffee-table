from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Dict, List

import cv2
import numpy as np
from PIL import Image
from shapely import geometry
import matplotlib.pyplot as plt

from .viz import _plot_contour_results, plot_polys


def calculate_normalized_quantized_depths(
    max_depth_m: float, levels: int, quantize_depth_start_m: float = 0
) -> np.ndarray:
    # return np.linspace(0, 1, levels, dtype=np.float32)

    assert quantize_depth_start_m >= 0

    # Make sure the starting depth is quantizable in an 8bit RGB image...
    # That is, the starting depth should be >= 0.004 for the eventual 8bit rgb encoding...
    #  ie: 0.004/1 >= 1/255based on an 8bit encoding
    quantize_depth_start_norm = max(quantize_depth_start_m / max_depth_m, 0.004)

    # Quantize
    quantized_depth_values_norm = np.linspace(
        # first guarantee the starting depth is clipped to a minimum quantizable value of 0.004
        quantize_depth_start_norm,
        1,
        levels - 1,
        dtype=np.float32,
    )
    # pre-pend a zero for the ground depth
    return np.insert(
        quantized_depth_values_norm,
        0,
        0,
    )


@dataclass(frozen=True, eq=True)
class QuantizeResult:
    depth_grid_quant: np.ndarray
    depth_map_im_quant: Image.Image
    quantized_depth_values: np.ndarray
    quantized_depth_values_norm: np.ndarray


def quantize_depth_grid(
    depth_grid: np.ndarray,
    levels: int,
    quantize_depth_start_m: float = 0,
) -> QuantizeResult:
    max_depth_m = depth_grid.max()
    depth_grid_norm = depth_grid / depth_grid.max()

    # Older method... producing pretty but randomly spaced intervals
    # depth_map_im_quant = depth_map_im_raw.quantize(args.levels)

    # New method, producing evenly spaced intervals starting from a configurable depth
    quantized_depth_values_norm = calculate_normalized_quantized_depths(
        max_depth_m=max_depth_m,
        levels=levels,
        quantize_depth_start_m=quantize_depth_start_m,
    )
    depth_grid_norm_quant = np.zeros_like(depth_grid_norm)
    for y in range(depth_grid_norm.shape[0]):
        depth_grid_norm_quant[y] = quantized_depth_values_norm[
            abs(depth_grid_norm[y, :] - quantized_depth_values_norm[:, None]).argmin(
                axis=0
            )
        ]
    depth_map_im_quant = Image.fromarray(
        (255.0 * depth_grid_norm_quant).astype(np.uint8)
    )

    # Convert image back to data
    # # Convert back to RGB to avoid reduced colormap issues, and reduce back to 1 channel
    depth_grid_quant = np.array(depth_map_im_quant.convert("RGB"))[:, :, 0].astype(
        np.float32
    )
    # # Convert from pixel range 0-255 back to depth range 0-max_depth
    depth_grid_quant *= max_depth_m / 255.0

    quantized_depth_values = (
        np.array((255.0 * quantized_depth_values_norm).astype(np.uint8)).astype(
            np.float32
        )
        * max_depth_m
        / 255.0
    )

    return QuantizeResult(
        depth_grid_quant=depth_grid_quant,
        depth_map_im_quant=depth_map_im_quant,
        quantized_depth_values=quantized_depth_values,
        quantized_depth_values_norm=quantized_depth_values_norm,
    )


def smooth_layer_mask(layer_mask: np.ndarray, scale_up_factor: int = 4) -> np.ndarray:
    wip = layer_mask.astype(np.uint8) * 255
    # Scale up
    for _ in range(scale_up_factor // 2):
        wip = cv2.pyrUp(wip)
    for _ in range(15):
        wip = cv2.medianBlur(wip, 7)
    for _ in range(scale_up_factor // 2):
        wip = cv2.pyrDown(wip)
    # Threshold back
    return wip >= 128


@dataclass(frozen=True, eq=True)
class ContourResult:
    layer_mask_bw: np.ndarray
    contours: Any
    hierarchy: Any
    layer_shapes: List[Dict]


def get_contours(
    layer_mask: np.ndarray, simplify_tolerance: float = 0.001
) -> ContourResult:
    result = 255 * layer_mask.astype(np.uint8)

    # Detect contours and save polygon info
    contours, hierarchy = cv2.findContours(
        result, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
    )
    # Normalize to range 0:1
    layer_shapes = []
    for top_level_contour_idx in [
        c_idx for c_idx in range(hierarchy.shape[1]) if hierarchy[0][c_idx][3] == -1
    ]:

        def get_poly(contour_index: int, simp_tolerance: float = 0):
            # # Store as normalized coords relative to original image
            # c = np.squeeze(contours[contour_index], axis=1).astype(np.float32)
            # c[:, 0] /= int(result.shape[1])
            # c[:, 1] /= int(result.shape[0])
            # c = c.tolist()

            # Store as normalized coords on a square canvas
            c = (
                np.squeeze(contours[contour_index], axis=1).astype(np.float32)
                / int(max(result.shape))
            ).tolist()

            # Convert to polygon
            poly = geometry.Polygon(c)
            if simp_tolerance > 0:
                return poly.simplify(tolerance=simp_tolerance)
            return poly

        def get_verts(poly):
            return [list(xy) for xy in zip(*poly.exterior.coords.xy)]

        def get_vert_count(contour_index: int):
            return len(np.squeeze(contours[contour_index], axis=1))

        if get_vert_count(top_level_contour_idx) <= 2:
            continue

        # identify contours which represent holes in this contour
        hole_indices = [
            c_idx
            for c_idx in range(hierarchy.shape[1])
            if hierarchy[0][c_idx][3] == top_level_contour_idx
        ]

        layer_shapes.append(
            {
                "vertices": get_verts(get_poly(top_level_contour_idx)),
                "simplified": get_verts(
                    get_poly(top_level_contour_idx, simp_tolerance=simplify_tolerance)
                ),
                "holes": [
                    {
                        "vertices": get_verts(get_poly(h_idx)),
                        "simplified": get_verts(
                            get_poly(h_idx, simp_tolerance=simplify_tolerance)
                        ),
                    }
                    for h_idx in hole_indices
                    if get_vert_count(h_idx) > 2
                ],
            }
        )

    return ContourResult(
        layer_mask_bw=result,
        contours=contours,
        hierarchy=hierarchy,
        layer_shapes=layer_shapes,
    )


def export_quantize_results(
    quantize_results: QuantizeResult,
    output_dir: Path,
    force_first_layer: bool = True,
    scale_up_factor: int = 4,
    simplify_tolerance: float = 0.001,
):
    output_dir.mkdir(parents=True, exist_ok=True)
    quantize_results.depth_map_im_quant.save(output_dir / "depth_map_quantized.png")

    with open(output_dir / "quantized_depth_values.json", "w") as f:
        json.dump(quantize_results.quantized_depth_values.tolist(), f)

    output_layers_dir = output_dir / "layer_masks"
    output_layers_dir.mkdir(parents=True, exist_ok=True)
    for layer_idx, layer_depth in enumerate(
        quantize_results.quantized_depth_values[1:]
    ):
        # Retrieve the mask for this layer. If configured for the first layer, ignore the quantization and take anything with a depth reading > 0
        layer_mask = (
            quantize_results.depth_grid_quant > 0
            if layer_idx == 0 and force_first_layer
            else quantize_results.depth_grid_quant >= layer_depth
        )
        layer_mask_smoothed = smooth_layer_mask(
            layer_mask, scale_up_factor=scale_up_factor
        )
        layer_mask_im = Image.fromarray(255 * layer_mask.astype(np.uint8))
        layer_mask_im.save(output_layers_dir / f"layer_{layer_idx}.jpg")

        im_smoothed = Image.fromarray(np.invert(layer_mask_smoothed))
        im_smoothed.save(output_layers_dir / f"layer_{layer_idx}_smoothed.jpg")
        # with NamedTemporaryFile("w", suffix=".pnm") as f:
        #     # potrace raster-> svg required .pnm file as input
        #     im_smoothed.save(f.name)
        #     subprocess.run(
        #         [
        #             "potrace",
        #             f.name,
        #             "-s",
        #             "-o",
        #             osp.join(output_layers_dir, f"layer_{layer_idx}_smoothed.svg"),
        #         ]
        #     )

        contour_results = get_contours(
            layer_mask=layer_mask_smoothed, simplify_tolerance=simplify_tolerance
        )
        with open(output_layers_dir / f"layer_{layer_idx}_contours.json", "w") as f:
            json.dump(
                contour_results.layer_shapes,
                f,
            )

        fig = plot_polys(contour_results.layer_shapes)
        plt.savefig(output_layers_dir / f"layer_{layer_idx}_contours_viz.jpg")
        plt.close()

        cv2.imwrite(
            str(output_layers_dir / f"layer_{layer_idx}_contours.jpg"),
            _plot_contour_results(
                background=contour_results.layer_mask_bw,
                contours=contour_results.contours,
                hierarchy=contour_results.hierarchy,
            ),
        )
