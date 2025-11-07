# %% [markdown]
# ## Imports

# %%
import os
# Geospatial data processing
import geopandas as gpd     #geopandas.GeoDataFrame explore() needs also folium + mathplot + mathclassify interactable map
import folium               #interactive map
# import geodatasets
import networkx as nx
import pandas as pd
import branca.colormap as cm

#experimental
from shapely.geometry import Point



# %% [markdown]
# Loading a gtfs data into a gdf

# %%
def get_distance(data, origin, destination):
    A=(data[origin]["stop_lat"],data[origin]["stop_lon"])
    B=(data[destination]["stop_lat"],data[destination]["stop_lon"])
    return geopy.distance.geodesic(A, B).m

def gdf_to_nx(gdf_network,L_space_edges):
    G = nx.Graph(L_space_edges)
    if hasattr(gdf_network, 'crs') and gdf_network.crs is not None:
        G.graph['crs'] = gdf_network.crs  #add column to gdf
    for idx, row in gdf_network.iterrows():
        node_name = row['stop_name']  # or whatever identifies the node
        if node_name in G.nodes():
            #assign node attributes
            G.nodes[node_name]['stop_id'] = row.get('stop_id')
            G.nodes[node_name]['lat'] = row.get('stop_lat')
            G.nodes[node_name]['lon'] = row.get('stop_lon')
    
    #example G = nx.from_pandas_edgelist(df=gdf or df, source=colum in gdf,target= "b",edge_attr= ["weight", "cost"])
    # for stops in df_test_routes['Stops on the way']:        # adding edges between each node that can be reached without switching trains
    #     n = len(stops)
    #     for i in range(n):
    #         for j in range(i+1, n):
    #             Graph.add_edge(stops[i], stops[j])
    return G
def nx_to_gdf(G):
    nodes_data = []
    
    for node_name, attrs in G.nodes(data=True):
        # Check if node has required geographic attributes
        if 'lat' in attrs and 'lon' in attrs:
            nodes_data.append({
                'stop_name': node_name,
                'stop_id': attrs.get('stop_id'),
                'stop_lat': attrs['lat'],
                'stop_lon': attrs['lon'],
                'geometry': Point(attrs['lon'], attrs['lat'])
            })
    
    # Create GeoDataFrame
    gdf = gpd.GeoDataFrame(nodes_data, crs="EPSG:4326")
    
    return gdf

def interactable_map(data, savepath, station_list:list = None, edges = None):
    colormap = cm.LinearColormap(["#00004C", "#0000FF", "#7F9EFF", "#D0D8E8", "#FF9EA0", "#FF0000", "#800000"], index=[0, 1000, 5000, 20000, 50000, 70000, 100000])

    #change these for size visual
    dim_w = 600
    dim_h = 500
    data = data.set_crs("EPSG:4326")
    data = data.to_crs('EPSG:4326')
    f = folium.Figure(width=dim_w, height=dim_h)

    #map
    m = data.explore(tiles="OpenStreetMap", location=(52.5, 5.483333), zoom_start=8,width=dim_h, height=dim_w).add_to(f)

    # render_path = "Assignment/tofile_exports/stops_map.html"

    added_edges = set()  # Track already added edges to avoid duplicates
    
    for idx, row in data.iterrows():
        if isinstance(row['edges'], list) and len(row['edges']) > 0:
            current_station = row['stop_name']
            current_coords = (row.geometry.y, row.geometry.x)
            
            for edge in row['edges']:
                if len(edge) == 2:  
                    origin, destination = edge
                    
                    edge_id = tuple(sorted([origin, destination]))
                    
                    if edge_id not in added_edges:
                        added_edges.add(edge_id)
                        
                        # Find destination station coordinates
                        dest_station = data[data['stop_name'] == destination]
                        if not dest_station.empty:
                            dest_coords = (dest_station.iloc[0].geometry.y, dest_station.iloc[0].geometry.x)
                            
                            # Add the edge line
                            #if you have color information, you should add that to the lines #TO DO
                            if station_list != None and type(edges) != None:
                                try:
                                    passengers = edges[list(nx.to_edgelist(station_list)).index((edge[0],edge[1],{}))]
                                except:
                                    passengers = edges[list(nx.to_edgelist(station_list)).index((edge[1],edge[0],{}))]
                                folium.PolyLine(
                                    locations=[current_coords, dest_coords],
                                    color=colormap(passengers),
                                    weight=5,
                                    opacity=1,
                                    popup=f"Route: {origin} ↔ {destination} with {passengers} passengers in each direction"
                                ).add_to(m)
                            else:
                                folium.PolyLine(
                                    locations=[current_coords, dest_coords],
                                    color='red',
                                    weight=2,
                                    opacity=0.7,
                                    popup=f"Route: {origin} ↔ {destination}"
                                ).add_to(m)

    m.save(savepath)
    print("----------------------------------------------------")
    print(f"\nOpen {savepath} to the side or in an external browser to view it live.\n Note: changes with the code are live updated\n")
    return m 

def load_gdf(path):
    _df = pd.read_csv(path, low_memory=False)
    # print(_df.head(3))             #assert stop_lat & stop_lon for geocoordinates
    geometry = [Point(xy) for xy in zip(_df['stop_lon'],_df['stop_lat'])]
    # print(geometry[0:5])
    ##convert pd df to gpd df
    _gdf=_df.copy()
    _gdf['geometry'] = geometry             
    _gdf=gpd.GeoDataFrame(_gdf)             #with geometry, coordinates dataframe is turned into a geodatagrame
    _gdf = _gdf.set_crs("EPSG:4326")        #set crs to gpd
    _gdf = _gdf.to_crs('EPSG:4326')
    return _gdf
# gdf.plot()

def get_nodes(path,data):               #path to station_data.csv, data=gdf based on stops.txt
    print("get stations nodes")
    if type(path)==str:
        file = pd.read_csv(path,sep=";")        #remove depending on seperator';'
    else:
        file=path
    _df = file.copy()['Station']            #_df = the station_data.dsv
                            #_nodes = gdf filtered with only relevant nodes
    _df = _df.drop_duplicates()
    #node part
    node_list = list(_df)
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


if __name__ == "__main__":
    gtfs_folder = os.path.join( "data","gtfs-nl")      ##insert your path to folder with gtfs zip contents
    print("Check "+str(os.listdir(gtfs_folder))+"\n")       ##Print the path
    gdf = load_gdf(gtfs_folder, '/stops.txt')
    nodes = get_nodes(os.path.join("data", "station_data.csv"),gdf)
    print("yes")
    # print(nodes[nodes["stop_name"]=="Beilen"])
    print(gdf.head(5)) 
    print(f"This is the crs code: '{gdf.crs}'")
    

