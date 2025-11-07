import numpy as np
import pandas as pd
import scipy.sparse.csgraph as sc

class Railmap:
    def __init__(self, nodes:pd.Series, lines:list):
        """
        Assume a list like for nodes and lines.
        Don't put in negative values as this will fail the path finding.
        All nodes should be connected somehow.
        """
        self.map = np.full((len(nodes),len(nodes)), np.inf)
        for _, line in lines.iterrows():
            if line["from_station"] not in nodes or line["to_station"] not in nodes:
                continue
            from_station = nodes.index(line["from_station"])
            to_station = nodes.index(line["to_station"])
            if line["travel_time_min"]<0:
                raise ValueError(f"Negative values make the shortest path algorithm not work. Here is the first negative number index: [{line[0]},{line[1]}]")
            self.map[from_station, to_station] = line["travel_time_min"]
            self.map[to_station, from_station] = line["travel_time_min"]
        np.seterr("ignore")
        

    def find_shortest_path_by_id(self, start_id, destination_id):
        """
        This function determines the shortest path on the map between 2 nodes. 
        All nodes should also be connected somehow.
        """
        #determine the minimal length from the start for each node
        total_lengths = np.full(self.map.shape, np.inf)
        total_lengths[start_id, start_id] = 0
        to_do = [start_id]
        while (len(to_do)>0 and to_do[0]!=destination_id): #check if you have nodes to check or you're checking the destination node, in which case you already have the shortest path
            for i, value in enumerate(self.map[to_do[0]]):
                if value+min(total_lengths[:,to_do[0]]) < min(total_lengths[:,i]):#When you find a shorter route to a node, insert it in the matrix
                    total_lengths[to_do[0]][i] = value+min(total_lengths[:,to_do[0]])
                    for j in range(len(to_do)):
                        #insert the newly discoverd nodes in the to do list if they are undiscovered. They are ordered by distance
                        if total_lengths[to_do[0]][i] <= min(total_lengths[:,to_do[j]]):
                            if i in to_do: #if there is a value later in the to do list, remove it
                                to_do.remove(i)
                            to_do.insert(j, i)
                            break
                        elif j == len(to_do)-1: #if it's the maximum value of the to do list, put it at the end
                            to_do.insert(j+1, i)
                            break
                        elif to_do[j] == i: #no double values. When already have the node in the to do list and it's earlier, don't try to add it in the list again
                            break
            to_do.pop(0)

        #determine the route based on the lengths matrix
        route = [destination_id]
        total_cost = np.min(total_lengths[:,destination_id])
        prev_node = np.argmin(total_lengths[:,destination_id])
        route.insert(0,int(prev_node))
        while (prev_node!=start_id):
            prev_node = np.argmin(total_lengths[:,prev_node])
            route.insert(0,int(prev_node))

        return route, total_cost
    
    def get_shortest_path_matrix(self)->np.ndarray:
        """
        This function applies the shortest path function to all routes on the map
        """
        matrix = np.zeros(self.map.shape)
        route_matrix = np.zeros(self.map.shape, dtype=object)
        for start in range(len(matrix)):
            length, prev_nodes = sc.shortest_path(self.map, indices=[start], return_predecessors=True)
            for end in range(len(matrix)):
                matrix[start, end] = length[0][end]

                route = []
                prev_node = end
                route.insert(0,int(prev_node))
                while (prev_node!=start and prev_node!=-9999):
                    prev_node = prev_nodes[0,prev_node]
                    route.insert(0,int(prev_node))
                route_matrix[start, end] = route
        return route_matrix, matrix
    
    def determine_O_D(self, p, q):
        """
        Uses a gravitational model to determine the OD-matrix
        """
        _, costs = self.get_shortest_path_matrix()
        shortest_paths = np.divide(1, costs)

        od = np.zeros(self.map.shape)
        for start in range(len(od)):
            start_paths = shortest_paths[start]
            start_paths[start] = 0
            for end in range(len(od)):
                path_sum = sum(q[j]*start_paths[j] for j in range(len(od)))
                od[start, end] = (q[end]*shortest_paths[start, end])/(path_sum)*p[start]

        return od  

if __name__ == "__main__":
    line_data = pd.DataFrame({"from_station": [0,0,2,1,1,2,4,0], "to_station":[2,1,3,4,3,4,3,4], "travel_time_min":[3,2,2,9,100,1,1,1]})
    nodes = pd.Series([0,1,2,3,4])
    print(line_data)
    rail = Railmap(nodes, line_data)
    route, cost = rail.find_shortest_path_by_id(0,2)
    print(f"route: {route} with cost: {cost}")


    p = [500,300,700,800,1500]
    q = [500,300,700,800,1500]
    od = rail.determine_O_D(p,q)
    print(od)