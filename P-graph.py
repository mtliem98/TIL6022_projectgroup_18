# P-graph
#Objective: A graph in which the network is mapped out, so that we can see how many transfers are needed to go from station a to b
#Connect all the stations whicha are directly accessible from the line

import pandas as pd
import geopandas as gpd
import networkx as nx
import matplotlib.pyplot as plt


#data for testing
# data_test_stations = [['Utrecht', 52.089454, 5.111796], ['Lelystad Centrum', 52.507735, 5.473311], ['Dordrecht', 51.807444, 4.670559], ['Eindhoven', 51.443663, 5.478553]]
# df = pd.DataFrame(data_test_stations, columns=['Station', 'Latitude', 'Longitude'])
# print(df.head(5))

data_test_routes = [
    ["A", "D", ["A", "B","C", "D"]],
    ["B", "E", ["B", "D", "E"]],
    ["C", "G", ["C", "F", "G"]],
    ["A", "C", ["A", "B", "C"]],
    ["D", "G", ["D", "F", "G"]]
    ]
df_test_routes = pd.DataFrame(data_test_routes, columns=['Begin station', 'End station', 'Stops on the way'])
print(df_test_routes.head())

df_locations = pd.DataFrame(
    {"Station": ["A", "B", "C", "D", "E", "F", "G"],
     "Longitude": [52.089454, 52.507735, 51.807444, 51.443663, 52.306783, 51.673451, 52.045632],
     "Latitude": [5.111796, 5.473311, 4.670559, 5.478553, 5.231567, 5.002345, 4.893201]}
)

gdf = gpd.GeoDataFrame(df_locations, geometry=gpd.points_from_xy(df_locations.Longitude, df_locations.Latitude), crs="EPSG:4326")
print (gdf.head())

Graph = nx.Graph()

for stops in df_test_routes['Stops on the way']:        #ChatGPT--> adding edges between each node that can be reached without switching trains
    n = len(stops)
    for i in range(n):
        for j in range(i+1, n):
            Graph.add_edge(stops[i], stops[j])


pos = {row['Station']: (row['Longitude'], row['Latitude']) for i, row in df_locations.iterrows()}

plt.figure(figsize=(8, 6))
nx.draw(Graph, pos, with_labels=True,
        node_color='skyblue', node_size=500,
        edge_color='gray', linewidths=1.5,
        font_size=8)

plt.title("P-Graph", fontsize=14)
plt.show()

