#P-graph
#Objective: A graph in which the network is mapped out, so that we can see how many transfers are needed to go from any station a to b
#Connect all the stations whicha are directly accessible from the line

# Import of libraries
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# --------------------------- mock datasets ---------------------------------------------------------------------
#mock dataset with routes
data_test_routes = [
    ["A", "D", ["A", "B","C", "D"]],
    ["B", "E", ["B", "D", "E"]],
    ["C", "G", ["C", "F", "G"]],
    ["A", "C", ["A", "B", "C"]],
    ["D", "G", ["D", "F", "G"]]
    ]

df_test_routes = pd.DataFrame(data_test_routes, columns=['Begin station', 'End station', 'Stops on the way'])   #convert to pandas dataframe
print(df_test_routes.head())

#mock dataset with stations and their latitude and longitude
df_locations = pd.DataFrame(
    {"Station": ["A", "B", "C", "D", "E", "F", "G"],
     "Latitude": [52.089454, 52.507735, 51.807444, 51.443663, 52.306783, 51.673451, 52.045632],
     "Longitude": [5.111796, 5.473311, 4.670559, 5.478553, 5.231567, 5.002345, 4.893201]}
    )
print(df_locations.head())

# -------------------------------------------------------------------------functions----------------------------------------------------------------------------
# function for creating the edges between the nodes the can be reached without switching trains
def create_P_graph(df_test_routes):
    Graph = nx.Graph()

    for stops in df_test_routes['Stops on the way']:        # adding edges between each node that can be reached without switching trains
        n = len(stops)
        for i in range(n):
            for j in range(i+1, n):
                Graph.add_edge(stops[i], stops[j])
    return Graph


# function for plotting the graph
def plot_P_graph(Graph, df_locations):
    pos = {row['Station']: (row['Longitude'], row['Latitude']) for i, row in df_locations.iterrows()} # determining the node positions based on the station's longitude and latitude

    plt.figure(figsize=(8, 6))
    nx.draw(Graph, pos, with_labels=True,
        node_color='skyblue', node_size=500,
        edge_color='gray', linewidths=1.5,
        font_size=8)
    plt.title("P-Graph", fontsize=14)
    plt.show()

#calling functions
Graph = create_P_graph(df_test_routes)
plot_P_graph(Graph, df_locations)