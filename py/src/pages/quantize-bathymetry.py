import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from common.quantize import get_contours, quantize_depth_grid, smooth_layer_mask
from common.st_extensions import upload_and_configure_depth_grid, viz_depth_grid
from common.viz import (
    _plot_contour_results,
    _plot_depth_as_heat_map,
    _plot_histogram,
    plot_polys,
)
from PIL import Image


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

    st.subheader("Details")
    st.write("Grid shape: {0}".format(depth_grid.shape))
    st.write(f"Max depth: {depth_grid.max()}m")

    c1, _, c2 = st.columns((5, 1, 5))
    c1.subheader("Histogram")
    c1.pyplot(_plot_histogram(depth_grid.flatten()))

    c2.subheader("Heatmap")
    c2.pyplot(_plot_depth_as_heat_map(depth_grid, cell_size_m=cell_size_m))

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

    fig = plt.figure()
    p = plt.imshow(depth_grid_norm * max_depth_m)
    clb = plt.colorbar(p)
    clb.ax.set_title("Water Depth (m)", fontsize=8)
    plt.title("Raw Depth Map")
    plt.xlabel(f"X ({cell_size_m} m)")
    plt.ylabel(f"Y ({cell_size_m} m)")
    c2.pyplot(fig)

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

    quantize_results = quantize_depth_grid(
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
    fig = plt.figure()
    p = plt.imshow(quantize_results.depth_grid_quant)
    clb = plt.colorbar(p)
    clb.ax.set_title("Water Depth (m)", fontsize=8)
    plt.title(
        f"Quantized Depth Map: {levels} depths\n{[round(z, 1) for z in quantize_results.quantized_depth_values]}m"
    )
    plt.xlabel(f"X ({cell_size_m} m)")
    plt.ylabel(f"Y ({cell_size_m} m)")
    c2.pyplot(fig)

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
    layer_mask_im = Image.fromarray(255 * layer_mask.astype(np.uint8))
    c1.image(layer_mask_im)

    with st.spinner("Smoothing image..."):
        layer_mask_smoothed = smooth_layer_mask(
            layer_mask, scale_up_factor=scale_up_factor
        )
        layer_mask_im_smoothed = Image.fromarray(np.invert(layer_mask_smoothed))
        c2.image(layer_mask_im_smoothed)

    # Convert boolean arr to black/white image
    contour_results = get_contours(layer_mask=layer_mask_smoothed)

    c1.pyplot(fig=plot_polys(contour_results.layer_shapes))

    c2.image(
        _plot_contour_results(
            background=contour_results.layer_mask_bw,
            contours=contour_results.contours,
            hierarchy=contour_results.hierarchy,
        ),
        channels="BGR",
    )


if __name__ == "__main__":
    st.set_page_config(layout="wide")
    main()
