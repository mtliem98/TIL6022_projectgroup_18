# %%
import os
# Geospatial data processing
import geopandas as gpd
import pandas as pd
import networkx as nx

# Mapping and visualization
import contextily as ctx
import matplotlib.pyplot as plt
import matplotlib.lines as mlines

# Network analysis
import osmnx as ox  
import city2graph

# %%
# Configure matplotlib for publication-quality
plt.rcParams['figure.figsize'] = (15, 12)
plt.rcParams['figure.dpi'] = 100
plt.style.use('default')  # Clean default style instead of ggplot

print("All dependencies loaded successfully!")
print(f"city2graph version: {city2graph.__version__ if hasattr(city2graph, '__version__') else 'development'}")

# %%
# Load GTFS data - city2graph handles all the complexity!
gtfs_path = os.path.join("Assignment","gtfs-nl.zip")

print("Loading Dutch Transport GTFS data...")
print("This includes all buses, trains, tubes, and trams across the whole Netherlands")

# One function call loads and processes the entire GTFS dataset
gtfs_data = city2graph.load_gtfs(gtfs_path)

# %%
print(type(gtfs_data))
print(gtfs_data.keys())
test = gtfs_data


# %%
print("Visualizing London's Transit Network")
print("Creating a map showing the spatial distribution of all transit stops...")

# city2graph automatically provides stops as a GeoDataFrame - no conversion needed!
stops_gdf = gtfs_data['stops']

# Reproject to British National Grid for accurate distance calculations
stops_gdf_bng = stops_gdf.to_crs(epsg=27700)

# Create a professional-looking map
fig, ax = plt.subplots(figsize=(15, 12))

# Plot stops with transparency for overlapping points
stops_gdf_bng.plot(
    ax=ax,
    alpha=0.6,
    color='#e74c3c',  # Transport red
    markersize=10,
    edgecolors='white',
    linewidth=0.1
)

# Add contextual basemap
ctx.add_basemap(
    ax,
    crs=stops_gdf_bng.crs.to_string(),
    source=ctx.providers.CartoDB.Positron,
    alpha=0.8
)

# Clean up the map appearance
ax.set_title("London Transit Network: Stop Locations", fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel("")
ax.set_ylabel("")
ax.set_xticks([])
ax.set_yticks([])

# Add a subtle border
for spine in ax.spines.values():
    spine.set_visible(True)
    spine.set_linewidth(1)
    spine.set_color('#cccccc')

ax.set_aspect('equal')
plt.tight_layout()

print(f"Mapped {len(stops_gdf):,} transit stops across Greater London")
plt.show()

# %% [markdown]
# ### test

# %%



