from GTFS_load_gdf import *
import fetch
from Pgraph import *
from travel_time import *
from Railmap import *
from ODmatrixtoroutes import *

import pandas as pd

class Analyser:

    def __init__(self):
        fetch.main()
        gtfs_path = os.path.join("data", "gtfs-nl")
        gdf = load_gdf(gtfs_path, "/stops.txt")
        gdf = gdf[gdf["stop_lat"]>50] #that's everything thats roughly in the netherlands
        junctions = pd.read_csv(os.path.join("data", "junctions.txt"))
        self.gdf = pd.concat((gdf, junctions))
        
        if not os.path.exists(os.path.join("data", "median_travel_times.csv")):
            determine_median_travel_times()
        self.travel_times = pd.read_csv(os.path.join("data", "median_travel_times.csv"))
        self.stop_data = pd.read_csv(os.path.join("data", "station_data.csv"), sep=";")
        self.stations = self.stop_data["Station"].drop_duplicates(ignore_index=True)
        self.stop_data = self.stop_data.fillna(0)
        self.rail = Railmap(self.stations.to_list(), self.travel_times)   

        real_edges = self.stop_data.copy().dropna(ignore_index=True)
        p_graph = []
        for i in range(len(real_edges)):
            edge = real_edges.iloc[i]
            if edge["Direction_to"] in real_edges["Station"].values:
                p_graph.append([edge["Station"], edge["Direction_to"], [edge["Station"], edge["Direction_to"]]])
        p_graph = pd.DataFrame(p_graph, columns=['Begin station', 'End station', 'Stops on the way'])
        self.graph = create_P_graph(p_graph)     

    def create_p_graph(self):
        plot_P_graph(self.graph, self.gdf)

    def analyse_original_network(self):
        passengers = self.stop_data.drop_duplicates("Station")["Getting_on_off"].to_list()
        OD_matrix = self.rail.determine_O_D(passengers, passengers)
        routes = Matrix_To_Routes(OD_matrix, self.graph, self.stations.to_list())
        Visualisation_travelers(self.graph, routes, OD_matrix, self.gdf)


if __name__ == "__main__":
    analysis = Analyser()
    #analysis.create_p_graph()
    analysis.analyse_original_network()