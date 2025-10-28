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
        self.gdf = gdf[gdf["stop_lat"]>50] #that's everything thats roughly in the netherlands
        if not os.path.exists(os.path.join("data", "median_travel_times.csv")):
            determine_median_travel_times()
        self.travel_times = pd.read_csv(os.path.join("data", "median_travel_times.csv"))
        stations = pd.concat((self.travel_times["from_station"],self.travel_times["to_station"])).drop_duplicates(ignore_index=True)
        self.rail = Railmap(stations, self.travel_times)        

    def create_p_graph(self):
        #creating p-graph
        p_graph = []
        for i in range(len(self.travel_times)):
            edge = self.travel_times.iloc[i]
            p_graph.append([edge["from_station"], edge["to_station"], [edge["from_station"], edge["to_station"]]])
        p_graph = pd.DataFrame(p_graph, columns=['Begin station', 'End station', 'Stops on the way'])
        graph = create_P_graph(p_graph)
        plot_P_graph(graph, self.gdf)




if __name__ == "__main__":
    analysis = Analyser()
    analysis.create_p_graph()