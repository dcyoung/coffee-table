# Bathymetry Scripts & App

## Development

A conda [environment.yml](environment.yml) has been provided.

```bash
# Build environment
conda env create -f environment.yml

# Launch environment
source activate coffee-table
```

Alternatively, a [requirements.txt](requirements.txt) file has been provided.

```bash
# Install depdencies
pip install -r requirements.txt
```

Alternatively, a docker development environment is provided

```bash
docker compose up

# Use browser to navigate to http://localhost:8501/
```

## Scripts

```bash
# Plot bathymetry data
python scripts/plot_bathymetry.py \
...

# Quantize bathymetry data
python scripts/quantize.py \
...
```

## GUI App

```bash
streamlit run app.py

# Use browser to navigate to http://localhost:8501/
```
