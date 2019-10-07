# coffee-table

Tools, visuals and CAD related to the design of a custom coffee table derived from bathymetry data.

Cad Render             |  Cad Render
:-------------------------:|:-------------------------:
![cad-render](docs/images/renders/coffee_table_ROUND_2019-Oct-07_02-59-15AM-000_CustomizedView7682114309.png)  | ![cad-render](docs/images/renders/30ffe7ad-f234-4388-8916-e65a14fffa08.PNG)
![cad-render](docs/images/renders/coffee_table_ROUND_2019-Oct-07_02-39-42AM-000_CustomizedView34130133655.png)  | ![cad-render](docs/images/renders/coffee_table_ROUND_2019-Oct-07_02-49-29AM-000_CustomizedView18952752789.png)
![cad-render](docs/images/renders/59480410-cb32-4f86-8561-837246cdbf94.PNG)  |  ![cad-render](docs/images/renders/5d4e55b0-76c5-467a-84d2-0b978f97abbc.PNG)
![cad-render](docs/images/renders/59480410-cb32-4f86-8561-837246cdbf94.PNG)  |  ![cad-render](docs/images/renders/5d4e55b0-76c5-467a-84d2-0b978f97abbc.PNG)
![cad-render](docs/images/cad/table_1.PNG) | ![cad-render](docs/images/cad/table_2.PNG)

![bathymetry-output](output/contour_templates/cluster_4/4_levels.png)
![bathymetry-output](output/bathymetry_plots/heatmap.png)
![bathymetry-output](output/bathymetry_plots_clipped/heightmap.png)

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
