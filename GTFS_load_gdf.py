# %% [markdown]
# ## Imports

# %%
import os
# Geospatial data processing
import geopandas as gpd     #geopandas.GeoDataFrame explore() needs also folium + mathplot + mathclassify interactable map
import folium               #interactive map
# import geodatasets
import pandas as pd
import networkx as nx
import momepy

#experimental
from shapely.geometry import Point

# Mapping and visualization
import mapclassify
import matplotlib
import contextily as ctx
import matplotlib.pyplot as plt
import matplotlib.lines as mlines


# %% [markdown]
# Loading a gtfs data into a gdf

# %%
def load_gdf(path, file):
    _df = pd.read_csv(path +file)
    # print(_df.head(3))             #assert stop_lat & stop_lon for geocoordinates
    geometry = [Point(xy) for xy in zip(_df['stop_lon'],_df['stop_lat'])]
    # print(geometry[0:5])
    ##convert pd df to gpd df
    _gdf=_df.copy()
    _gdf['geometry'] = geometry
    _gdf=gpd.GeoDataFrame(_gdf)
    print(type(_gdf))
    return _gdf
# gdf.plot()

# %% [markdown]
# ### Load GTFS Geometric data
# store it into a Geopandas Dataframe

# %%
gtfs_folder = os.path.join("Assignment","gtfs-nl")      ##insert your path to folder with gtfs zip contents
print("Check "+str(os.listdir(gtfs_folder))+"\n")       ##Print the path
gdf = load_gdf(gtfs_folder, '/stops.txt')
gdf.head()
