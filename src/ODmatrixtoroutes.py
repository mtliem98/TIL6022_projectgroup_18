import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

def Matrix_To_Routes(OD_Matrix, G, station_list):
    #OD_Matrix = matrix met aantal verplaatsingen tussen i en j
    #TT_Matrix = matrix met reistijden tussen i en j
    #G: De graaf, het netwerk met lijnstukjes en reistijden per lijnstukje
    routes = np.zeros((len(OD_Matrix),len(OD_Matrix)), dtype = object)
    for i in range(len(OD_Matrix)):
        for j in range(len(OD_Matrix)):
            if i != j and OD_Matrix[i][j] > 0:
                routes[i][j] = nx.shortest_path(G, source = station_list[i], target = station_list[j], weight = 'weight') #path with least travel time on the network
    return routes #een lijst met de kortste route voor elke relatie, elke route is ook een lijst

def get_segments(G):
    segments = list(G.edges())
    return segments #een lijst met alle verbindingen als tupel

def Travelers_On_Segment(segment, routes, OD_Matrix): 
    counter = 0
    u, v = segment
    for i in range(len(routes)):
        for j in range(len(routes[i])):
            route = routes[i][j]
            if route is None or isinstance(route, (int, float)):
                continue

            for k in range(len(route) - 1):
                if route[k] == u and route[k+1] == v:
                    counter += OD_Matrix[i][j]
    return counter #Het aantal reizigers op een edge (er is onderscheid per richting)

def Travelers_On_Segments(segments, routes, OD_Matrix):
    travelers_on_segments = []
    for segment in segments:
        travelers_on_segments.append(Travelers_On_Segment(segment, routes, OD_Matrix))
    return travelers_on_segments #een lijst met het aantal reizigers per segment: traverelers_on_segments[i] = het aantal reizigers op segment i

def Visualisation_travelers(G, routes, OD_Matrix, locations):
    segments = get_segments(G)
    travelers = Travelers_On_Segments(segments, routes, OD_Matrix)
    travelers = np.array(travelers)
    min_width, max_width = 0.5, 8
    if travelers.max() > 0:
        edge_width = np.interp(travelers, (travelers.min(), travelers.max()), (min_width, max_width))
    else:
        edge_width = [1 for _ in travelers]

    pos = {row['stop_name']: (row['stop_lon'], row['stop_lat']) for i, row in locations.iterrows()} # determining the node positions based on the station's longitude and latitude
    plt.figure(figsize=(8,6))
    nx.draw_networkx_nodes(G, pos, node_size=50, node_color = "lightblue")
    nx.draw_networkx_labels(G, pos)
    nx.draw_networkx_edges(G, pos, edgelist=segments, width=edge_width, edge_color="orange", arrows=False)

    plt.title("Network")
    plt.axis("off")
    plt.show()

if __name__ == "__main__":
    OD_Matrix = [[0,7,8,9],[7,0,5,20],[8,5,0,10],[9,20,10,0]]
    G = nx.Graph()
    G.add_nodes_from([0,1,2,3])
    G.add_edges_from([(0,1),(1,2),(2,3),(3,4),(0,3)])
    routes = Matrix_To_Routes(OD_Matrix, G)
    Visualisation_travelers(G, routes, OD_Matrix)

