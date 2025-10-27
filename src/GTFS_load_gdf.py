# %% [markdown]
# ## Imports

# %%
import os
# Geospatial data processing
import geopandas as gpd     #geopandas.GeoDataFrame explore() needs also folium + mathplot + mathclassify interactable map
import folium               #interactive map
# import geodatasets
import pandas as pd

#experimental
from shapely.geometry import Point



# %% [markdown]
# Loading a gtfs data into a gdf

# %%
def get_distance(data, origin, destination):
    A=(data[origin]["stop_lat"],data[origin]["stop_lon"])
    B=(data[destination]["stop_lat"],data[destination]["stop_lon"])
    return geopy.distance.geodesic(A, B).m

def interactable_map(data, savepath):
    #change these for size visual
    dim_w = 600
    dim_h = 500
    data = data.set_crs("EPSG:4326")
    data = data.to_crs('EPSG:4326')
    f = folium.Figure(width=dim_w, height=dim_h)
    render_data = data.explore(tiles="OpenStreetMap", location=(52.5, 5.483333), zoom_start=8,width=dim_h, height=dim_w).add_to(f)
    # render_path = "Assignment/tofile_exports/stops_map.html"
    render_data.save(savepath)
    print(f"Open {savepath} to the side or in an external browser to view it live.\n Note: changes with the code are live updated")
    return

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

def get_nodes(path,data):               #path to station_data.csv, data=gdf based on stops.txt
    print("get stations nodes")
    file = pd.read_csv(path,sep=";")        #remove depending on seperator';'
    _df = file.copy()['Station']            #_df = the station_data.dsv
    print(_df)                              #_nodes = gdf filtered with only relevant nodes
    _df = _df.drop_duplicates()
    #node part
    node_list = list(_df)
    print(len(node_list))
    _node = data.loc[data['stop_name'].isin(node_list)]
    # _node.plot()                        #comment if it works
    print("Nodes loaded")
    ## Note!!! for some reason we have less nodes in our returned dataframe
    ## Note2!! We have to create a combined
    #create edges

    return _node

# %% [markdown]
# ### Load GTFS Geometric data
# store it into a Geopandas Dataframe

# %%
if __name__ == "__main__":
    gtfs_folder = os.path.join( "data","gtfs-nl")      ##insert your path to folder with gtfs zip contents
    print("Check "+str(os.listdir(gtfs_folder))+"\n")       ##Print the path
    gdf = load_gdf(gtfs_folder, '/stops.txt')
    print(gdf.head())
