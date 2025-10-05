import numpy as np

class Railmap:
    def __init__(self, nodes, lines:dict):
        """
        Assume a list like for nodes and lines.
        Don't put in negative values as this will fail the path finding.
        All nodes should be connected somehow.
        """
        self.map = np.full((len(nodes),len(nodes)), np.inf)
        for line in lines:
            if line[2]<0:
                raise ValueError(f"Negative values make the shortest path algorithm not work. Here is the first negative number index: [{line[0]},{line[1]}]")
            self.map[line[0],line[1]] = line[2]
            self.map[line[1],line[0]] = line[2]
        

    def find_shortest_path_by_id(self, start_id, destination_id):
        """
        This function determines the shortest path on the map between 2 nodes. 
        All nodes should also be connected somehow.
        """
        #determine the minimal length from the start for each node
        total_lengths = np.full(self.map.shape, np.inf)
        total_lengths[start_id, start_id] = 0
        to_do = [start_id]
        while (len(to_do)>0):
            for i, value in enumerate(self.map[to_do[0]]):
                if value+min(total_lengths[:,to_do[0]]) < total_lengths[to_do[0]][i]:
                    total_lengths[to_do[0]][i] = value+min(total_lengths[:,to_do[0]])
                    to_do.append(i)
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


if __name__ == "__main__":
    rail = Railmap([0, 1, 2, 3, 4],[[0,2,3],[0,1,2],[2,3,3], [1,4,9], [1,3,100], [2,4,1]])
    route, cost = rail.find_shortest_path_by_id(1,3)
    print(f"route: {route} with cost: {cost}")