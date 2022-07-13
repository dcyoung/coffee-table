# coffee-table

Tools, visuals and CAD related to the design of a custom coffee table derived from bathymetry data.

## Cad Renders

Cad Render             |  Cad Render
:-------------------------:|:-------------------------:
![cad-render](docs/images/renders/coffee_table_ROUND_2019-Oct-07_02-59-15AM-000_CustomizedView7682114309.png)  | ![cad-render](docs/images/renders/30ffe7ad-f234-4388-8916-e65a14fffa08.PNG)
![cad-render](docs/images/renders/coffee_table_ROUND_2019-Oct-07_02-39-42AM-000_CustomizedView34130133655.png)  | ![cad-render](docs/images/renders/coffee_table_ROUND_2019-Oct-07_02-49-29AM-000_CustomizedView18952752789.png)
![cad-render](docs/images/renders/59480410-cb32-4f86-8561-837246cdbf94.PNG)  |  ![cad-render](docs/images/renders/5d4e55b0-76c5-467a-84d2-0b978f97abbc.PNG)
![cad-render](docs/images/renders/59480410-cb32-4f86-8561-837246cdbf94.PNG)  |  ![cad-render](docs/images/renders/5d4e55b0-76c5-467a-84d2-0b978f97abbc.PNG)
![cad-render](docs/images/cad/table_1.PNG) | ![cad-render](docs/images/cad/table_2.PNG)

## Contour Quantization

The distribution of depth values is not uniform. That is to say, there are outliers, where depth changes dramatically in a very small region.

![depth-histogram](output/bathymetry_plots/histogram.jpg)

In order to create more meaningful contours, the depth data is clipped (outliers removed) and quantized to better smooth the raw data for the purposes of this project.

Raw             |  Quantized
:-------------------------:|:-------------------------:
![raw](output/contour_plots/depth_map_raw.png)  |  ![raw](output/contour_plots/depth_map_quantized.png)
![plot](output/contour_plots/depth_map_raw_plot.png)  |  ![plot](output/contour_plots/depth_map_quantized_plot.png)

Regular             |  Inverted
:-------------------------:|:-------------------------:
![reg](output/contour_plots/separated_contours.jpg)  |  ![inverted](output/contour_plots/separated_contours_inverted.jpg)

Isolated Masks for each quantized layer:

 a | Layer 0 | Layer 1 | Layer 2
:-------------------------:|:-------------------------:|:-------------------------:|:-------------------------:
quantized layer before smoothing | ![layer](output/contour_plots/layer_masks/layer_0.png) | ![layer](output/contour_plots/layer_masks/layer_1.png) | ![layer](output/contour_plots/layer_masks/layer_2.png)
quantized layer after smoothing | ![layer](output/contour_plots/layer_masks/layer_0_smoothed.png) | ![layer](output/contour_plots/layer_masks/layer_1_smoothed.png) | ![layer](output/contour_plots/layer_masks/layer_2_smoothed.png)

## Raw Depth Visualization

Regular             |  Inverted
:-------------------------:|:-------------------------:
![reg](output/bathymetry_plots/contours.jpg)  |  ![inverted](output/bathymetry_plots/contours_inverted.jpg)
![reg](output/bathymetry_plots/heightmap.jpg)  |  ![inverted](output/bathymetry_plots/heightmap_inverted.jpg)
![reg](output/bathymetry_plots/wireframe.jpg)  |  ![inverted](output/bathymetry_plots/wireframe_inverted.jpg)
![reg](output/bathymetry_plots/surface.jpg)  |  ![inverted](output/bathymetry_plots/surface_inverted.jpg)

## Setup

A conda [environment.yml](environment.yml) has been provided.

```bash
# Build environment
conda env create -f environment.yml

# Launch environment
source activate coffee-table
```

Alternatively, a [requirements.txt](requirements.txt) file has been provided.

```bash
pip install -r requirements.txt
```
