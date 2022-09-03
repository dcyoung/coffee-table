from dataclasses import asdict
import json
from pathlib import Path
import shutil
from tempfile import NamedTemporaryFile, TemporaryDirectory
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from common.data_helpers import Config
from common.io import make_zip_archive
from common.quantize import (
    export_quantize_results,
    get_contours,
    quantize_depth_grid,
    smooth_layer_mask,
)
from common.st_extensions import (
    crop_depth_grid,
    upload_and_configure_depth_grid,
    viz_depth_grid,
)
from common.viz import (
    _plot_contour_results,
    _plot_depth_as_heat_map,
    _plot_histogram,
    plot_polys,
)
from PIL import Image


@st.cache(allow_output_mutation=True)
def quantize_depth_grid_CACHED(*args, **kwargs):
    return quantize_depth_grid(*args, **kwargs)


@st.cache(allow_output_mutation=True)
def smooth_layer_mask_CACHED(*args, **kwargs):
    return smooth_layer_mask(*args, **kwargs)


def main():
    st.title("Quantize Bathymetry")
    depth_grid = upload_and_configure_depth_grid()
    if depth_grid is None:
        st.warning("No data grid...")
        return
    cell_size_m = st.sidebar.select_slider(
        label="Cell Size (m)",
        help="The resolution of x,y readings in m.",
        options=[3, 10, 30, 90],
        value=30,
    )

    if st.checkbox(label="Crop Region", value=False):
        depth_grid = crop_depth_grid(depth_grid=np.copy(depth_grid))

    c1, _, c2, _, c3 = st.columns((3, 1, 10, 1, 10))
    c1.subheader("Details")
    c1.write("Grid shape: {0}".format(depth_grid.shape))
    c1.write(f"Max depth: {depth_grid.max()}m")

    c2.subheader("Histogram")
    c2.pyplot(_plot_histogram(depth_grid.flatten()))

    c3.subheader("Heatmap")
    c3.pyplot(_plot_depth_as_heat_map(depth_grid, cell_size_m=cell_size_m))

    if st.checkbox("Early Return", value=True):
        return

    if st.checkbox("Visualize depth grid", value=False):
        viz_depth_grid(depth_grid=depth_grid, cell_size_m=cell_size_m)

    max_depth_m = depth_grid.max()
    depth_grid_norm = depth_grid / depth_grid.max()

    st.subheader("Depth Map - Raw")
    c1, _, c2 = st.columns((4, 1, 4))
    # Raw depth map image
    # yields a grayscale image w/ pixel values in range 0-255 corresponding to 0-max-depth)
    depth_map_im_raw = Image.fromarray((255.0 * depth_grid_norm).astype(np.uint8))
    c1.image(depth_map_im_raw)

    fig_depth_map_raw = plt.figure()
    p = plt.imshow(depth_grid_norm * max_depth_m)
    clb = plt.colorbar(p)
    clb.ax.set_title("Water Depth (m)", fontsize=8)
    plt.title("Raw Depth Map")
    plt.xlabel(f"X ({cell_size_m} m)")
    plt.ylabel(f"Y ({cell_size_m} m)")
    c2.pyplot(fig_depth_map_raw)

    st.subheader("Depth Map - Quantized")
    # Quantize depth map - producing evenly spaced intervals from a starting depth
    levels = st.slider(
        label="Number levels",
        min_value=1,
        max_value=30,
        value=4,
        step=1,
        help="The number of evenly spaced contour levels. This includes the depth-0 contour. ie: N levels will correspond to N-1 output layers.",
    )
    quantize_depth_start_m = st.number_input(
        label="Quantize Depth Start (m)",
        value=0,
        min_value=0,
        max_value=int(max_depth_m),
        step=1,
        help="The starting depth for the first layer... beyond which subsequent layers will be evenly spaced. This helps to visualize shallow depths when overall water depth range is high.",
    )

    quantize_results = quantize_depth_grid_CACHED(
        depth_grid=depth_grid,
        levels=levels,
        quantize_depth_start_m=quantize_depth_start_m,
    )

    c1, _, c2 = st.columns((4, 1, 4))
    c1.write("Quantized Depth Values - Normalized")
    c1.write(quantize_results.quantized_depth_values_norm)
    c2.write("Quantized Depth Values - (m)")
    c2.write(quantize_results.quantized_depth_values)

    # Plot quantized heatmaps
    c1.image(quantize_results.depth_map_im_quant)
    fig_depth_map_quantized = plt.figure()
    p = plt.imshow(quantize_results.depth_grid_quant)
    clb = plt.colorbar(p)
    clb.ax.set_title("Water Depth (m)", fontsize=8)
    plt.title(
        f"Quantized Depth Map: {levels} depths\n{[round(z, 1) for z in quantize_results.quantized_depth_values]}m"
    )
    plt.xlabel(f"X ({cell_size_m} m)")
    plt.ylabel(f"Y ({cell_size_m} m)")
    c2.pyplot(fig_depth_map_quantized)

    st.subheader("Layer contours:")
    layer_depths = quantize_results.quantized_depth_values[1:]
    c1, c2, c3 = st.columns((2, 1, 2))
    layer_idx = c1.selectbox(
        label="Layer Index", options=list(range(len(layer_depths)))
    )
    force_first_layer = c2.checkbox(
        "Force First Layer",
        value=True,
        help="If True, force all depth > 0 to be included in the first layer. This helps with high depth range, causing the shallow areas be shorelines to be marked as 0.",
    )
    scale_up_factor = c3.number_input(
        label="Scale up factor", value=1, min_value=1, max_value=8, step=1
    )
    layer_depth = layer_depths[layer_idx]

    c1, _, c2 = st.columns((4, 1, 4))
    # Retrieve the mask for this layer. If configured for the first layer, ignore the quantization and take anything with a depth reading > 0
    layer_mask = (
        quantize_results.depth_grid_quant > 0
        if layer_idx == 0 and force_first_layer
        else quantize_results.depth_grid_quant >= layer_depth
    )
    # Convert boolean arr to black/white image
    layer_mask_im = Image.fromarray(255 * layer_mask.astype(np.uint8))
    c1.write("Mask:")
    c1.image(layer_mask_im)

    with st.spinner("Smoothing image..."):
        layer_mask_smoothed = smooth_layer_mask_CACHED(
            layer_mask, scale_up_factor=scale_up_factor
        )
        c2.write("Smoothed Mask:")
        c2.image(Image.fromarray(np.invert(layer_mask_smoothed)))

    st.subheader("Contours")
    c1, c2, _, c3 = st.columns((2, 4, 1, 4))
    simplify_tolerance = c1.number_input(
        label="Polygon simplification tolerance",
        value=0.001,
        min_value=0.0,
        max_value=0.01,
        step=0.001,
        format="%.3f",
    )
    include_originals = c1.checkbox("Show originals", value=False)
    include_simplified = c1.checkbox("Show simplified", value=True)
    contour_results = get_contours(
        layer_mask=layer_mask_smoothed, simplify_tolerance=simplify_tolerance
    )
    c2.write("Polygons:")
    c2.pyplot(
        fig=plot_polys(
            contour_results.layer_shapes,
            include_original=include_originals,
            include_simplified=include_simplified,
            max_labels=0,
        )
    )

    c3.write("Contours:")
    c3.image(
        _plot_contour_results(
            background=contour_results.layer_mask_bw,
            contours=contour_results.contours,
            hierarchy=contour_results.hierarchy,
        ),
        channels="BGR",
    )

    st.subheader("Export")
    if st.button("Generate Export"):
        with TemporaryDirectory() as tmp_dir:
            tmp_dir = Path(tmp_dir)
            tmp_dir.mkdir(parents=True, exist_ok=True)

            with open(tmp_dir / "config.json", "w") as f:
                json.dump(
                    asdict(
                        Config(
                            # TODO: Replace the hardcoded values with actually configured values
                            cell_size_m=int(cell_size_m),
                            depth_unit_m=1.0,
                            depth_min_m=0,
                            depth_max_m=float(max_depth_m),
                            max_z_score=0,
                            levels=int(levels),
                            quantize_depth_start_m=float(quantize_depth_start_m),
                            scale_up_factor=int(scale_up_factor),
                            force_first_layer=force_first_layer,
                        )
                    ),
                    f,
                )
            fig_depth_map_raw.savefig(
                str(tmp_dir / "depth_map_raw_plot.jpg"),
                dpi=1000,
            )
            fig_depth_map_quantized.savefig(
                str(tmp_dir / "depth_map_quantized_plot.jpg"),
                dpi=1000,
            )
            with st.spinner("Exporting results... this may take a moment."):
                export_quantize_results(
                    quantize_results=quantize_results,
                    output_dir=tmp_dir,
                    force_first_layer=force_first_layer,
                    scale_up_factor=scale_up_factor,
                    simplify_tolerance=0.001,
                )

            with NamedTemporaryFile(suffix=".zip") as tmp_zip:
                make_zip_archive(tmp_dir, tmp_zip.name)
                with open(tmp_zip.name, "rb") as f:
                    st.download_button("Download Zip", f, file_name="archive.zip")


if __name__ == "__main__":
    st.set_page_config(layout="wide")
    main()
