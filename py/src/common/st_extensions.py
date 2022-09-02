from typing import Tuple
import cv2
import numpy as np
import streamlit as st

from .data_helpers import load_data, load_raw
from .image_utils import im_resize, crop_box
from .io import list_bathy_files
from .viz import (
    _plot_depth_3D_as_contours,
    _plot_depth_3D_as_height_map,
    _plot_depth_3D_surface,
    _plot_depth_3D_wireframe,
    viz_rotated_rectangle,
)


@st.cache(allow_output_mutation=True)
def cached_load_data(**kwargs):
    with st.spinner("Loading data..."):
        return load_data(**kwargs)


@st.cache(allow_output_mutation=True)
def load_raw_cached(**kwargs):
    with st.spinner("Loading raw data..."):
        return load_raw(**kwargs)


def crop_depth_grid(depth_grid: np.ndarray) -> np.ndarray:
    if not st.checkbox(label="Crop Region", value=False):
        return np.copy(depth_grid)
    c1, _, c2 = st.columns((1, 1, 4))
    crop_rotation_angle_cw = c1.slider(
        label="Rotation (deg CW)",
        value=0,
        min_value=0,
        max_value=90,
        step=5,
        help="The amount of degrees to rotate the image.",
    )
    crop_x = c1.slider(
        label="x",
        value=0.5,
        min_value=0.1,
        max_value=0.9,
        step=0.05,
        help="The x1 coord",
    )
    crop_y = c1.slider(
        label="y",
        value=0.5,
        min_value=0.1,
        max_value=0.9,
        step=0.05,
        help="The y1 coord",
    )
    crop_size = c1.slider(
        label="size",
        value=0.5,
        min_value=0.1,
        max_value=1.5,
        step=0.01,
        help="The box size",
    )

    def scaled_crop_config(dims) -> Tuple:
        h, w = dims[:2]
        return (
            (w * crop_x, h * crop_y),
            (max(h, w) * crop_size, max(h, w) * crop_size),
            crop_rotation_angle_cw,
        )

    resized_rgb = np.stack(
        (im_resize(img=depth_grid, max_dim=1080).astype(np.uint8),) * 3,
        axis=-1,
    )
    c2.image(
        viz_rotated_rectangle(
            background=resized_rgb,
            box=np.int0(cv2.boxPoints(scaled_crop_config(dims=resized_rgb.shape))),
        ),
        channels="BGR",
    )
    return crop_box(
        img=np.copy(depth_grid),
        box=scaled_crop_config(dims=depth_grid.shape),
    )


def upload_and_configure_depth_grid() -> np.ndarray:
    if st.sidebar.checkbox(label="File upload", value=True):
        input_file = st.sidebar.file_uploader(
            label="GeoTiff",
            type=["tif", "tiff", "geotiff", "geotif", "geo", "geo.tiff"],
        )
    else:
        input_file = st.sidebar.selectbox(
            labels="file",
            options=list_bathy_files(parent_dir="/data"),
            format_func=lambda src: src.stem,
        )

    if not input_file:
        st.warning("Please upload a file in the sidebar to continue.")
        return None

    depth_units_map = {
        "meters": 1.0,
        "centimeters": 0.01,
        "decimeters": 0.1,
        "10 meters": 10,
    }
    depth_unit_name = st.sidebar.selectbox(
        label="Depth unit",
        options=list(depth_units_map.keys()),
        help="The resolution of z readings in m.",
    )
    depth_unit_m = depth_units_map[depth_unit_name]

    max_possible_depth_as_read = int(
        (load_raw_cached(fpath=input_file) * depth_unit_m).max() + 0.5
    )
    depth_grid_min_max_m = st.sidebar.slider(
        label="Min/max depth (m)",
        min_value=0,
        max_value=max_possible_depth_as_read,
        value=(0, max_possible_depth_as_read),
        step=1,
        help="Min/max depth in meters, values will be clipped.",
    )

    max_z_score = st.sidebar.slider(
        label="Max Z-Score",
        min_value=0.0,
        max_value=10.0,
        value=0.0,
        step=0.1,
        help="The max z-score beyond which data is clipped.",
    )

    return cached_load_data(
        fpath=input_file,
        depth_unit_m=depth_unit_m,
        depth_min_m=min(depth_grid_min_max_m),
        depth_max_m=max(depth_grid_min_max_m),
        max_z_score=max_z_score,
    )


def viz_depth_grid(depth_grid: np.ndarray, cell_size_m) -> None:
    include_surface_plots = st.checkbox("Include surface plots", value=False)
    for is_inverted in (True, False):
        data = -(depth_grid - np.amax(depth_grid)) if is_inverted else depth_grid
        title_suffix = "\nInverted" if is_inverted else ""
        st.subheader("Plots Inverted" if is_inverted else "Plots")

        c1, c2, c3, c4 = st.columns(4)
        c1.pyplot(
            _plot_depth_3D_as_contours(
                data,
                cell_size_m=cell_size_m,
                title=f"Water Depth Contours{title_suffix}",
            )
        )
        c2.pyplot(
            _plot_depth_3D_wireframe(
                data,
                cell_size_m=cell_size_m,
                title=f"Water Depth Wireframe{title_suffix}",
            )
        )
        c3.pyplot(
            _plot_depth_3D_as_height_map(
                data, cell_size_m=cell_size_m, title=f"Water Depth Map{title_suffix}"
            )
        )
        if include_surface_plots:
            c4.pyplot(
                _plot_depth_3D_surface(
                    data,
                    cell_size_m=cell_size_m,
                    title=f"Water Depth Surface{title_suffix}",
                )
            )
