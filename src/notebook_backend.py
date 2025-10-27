from GTFS_load_gdf import *
import fetch
from Pgraph import *
from travel_time import *
from Railmap import *

import pandas as pd
import numpy as np

class Analyser:

    def __init__(self):
        fetch.main()
        gtfs_path = os.path.join("data", "gtfs-nl")
        gdf = load_gdf(gtfs_path, "/stops.txt")
        nodes = get_nodes(os.path.join("data", "station_data.csv"),gdf)
        if not os.path.exists(os.path.join("data", "median_travel_times.csv")):
            determine_median_travel_times()
        travel_times = pd.read_csv(os.path.join("data", "median_travel_times.csv"))
        stations = pd.concat((travel_times["from_station"],travel_times["to_station"])).drop_duplicates(ignore_index=True)
        rail = Railmap(stations, travel_times)
        routes, lengths = rail.get_shortest_path_matrix()
        p_graph = []
        for i in range(len(stations)):
            for j in range(i):
                named_route = []
                for k in routes[i,j]:
                    named_route.append(stations[k])
                p_graph.append([stations[i], stations[j], named_route])
        p_graph = pd.DataFrame(p_graph, columns=['Begin station', 'End station', 'Stops on the way'])
        graph = create_P_graph(p_graph)
        gdf = gdf[gdf["stop_lat"]>50]




if __name__ == "__main__":
    Analyser()