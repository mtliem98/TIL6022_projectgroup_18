# P-graph
#Objective: A graph in which the network is mapped out, so that we can see how many transfers are needed to go from station a to b
#Connect all the stations whicha are directly accessible from the line

import pandas as pd
import geopandas as gpd
import plotly.express as px
import networkx as nx
import matplotlib.pyplot as plt
import plotly.graph_objects as go

#data for testing
data_test_routes = [
    ["A", "D", ["A", "B","C", "D"]],
    ["B", "E", ["B", "D", "E"]],
    ["C", "G", ["C", "F", "G"]],
    ["A", "C", ["A", "B", "C"]],
    ["D", "G", ["D", "F", "G"]]
    ]
df_test_routes = pd.DataFrame(data_test_routes, columns=['Begin station', 'End station', 'Stops on the way'])
print(df_test_routes.head())

Graph = nx.Graph()

# for stops in df_test_routes['Stops on the way']:        #ChatGPT --> adding edges between two consecutive lines --> L-graph
#     for i in range(len(stops)-1):
#         Graph.add_edge(stops[i], stops[i+1])

for stops in df_test_routes['Stops on the way']:        #ChatGPT--> adding edges between each node that can be reached without transferring trains
    n = len(stops)
    for i in range(n):
        for j in range(i+1, n):
            Graph.add_edge(stops[i], stops[j])



plt.figure(figsize=(8,6))                           #chatgpt
pos = nx.spring_layout(Graph)  # positions for all nodes
nx.draw(Graph, pos, with_labels=True, node_color='lightblue', node_size=2000, font_size=12)
plt.title("P-Graph of Routes")
plt.show()

