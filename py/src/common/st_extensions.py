import numpy as np
import streamlit as st

from .data_helpers import load_data, load_raw
from .io import list_bathy_files
from .viz import (
    _plot_depth_3D_as_contours,
    _plot_depth_3D_as_height_map,
    _plot_depth_3D_surface,
    _plot_depth_3D_wireframe,
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
        (load_raw(fpath=input_file) * depth_unit_m).max() + 0.5
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

    return load_data(
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
