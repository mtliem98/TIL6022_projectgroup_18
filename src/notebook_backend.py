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
        junctions = load_gdf("data", "junctions.txt")       #adds geometry data required for gdf to junctions which was missing
        gdf = pd.concat((gdf, junctions)).reset_index(drop=True)
        # add new column for list of edges
        gdf = gdf.drop_duplicates(subset=['stop_name'])
        self.gdf = gdf
        self.gdf['edges'] = [[] for _ in range(len(self.gdf))]
        
        if not os.path.exists(os.path.join("data", "median_travel_times.csv")):
            determine_median_travel_times()
        self.travel_times = pd.read_csv(os.path.join("data", "median_travel_times.csv"))
        stops_file = os.path.join("data", "station_data.csv")
        self.stop_data = pd.read_csv(stops_file, sep=";")
        self.stations = self.stop_data["Station"].drop_duplicates(ignore_index=True)
        self.stop_data = self.stop_data.fillna(0)
        self.rail = Railmap(self.stations.to_list(), self.travel_times)   

        real_edges = self.stop_data.copy().dropna(ignore_index=True)
        l_graph_edges = []                #it was the l_graph not the p_graph, changed the name where applicable to avoid confusion. 
        stops = self.gdf['stop_name']
        for i in range(len(real_edges)):
            edge = real_edges.iloc[i]
            if edge["Direction_to"] in real_edges["Station"].values:
                on_the_way = [edge["Station"], edge["Direction_to"]]
                l_graph_edges.append([edge["Station"], edge["Direction_to"], on_the_way])
                matches = self.gdf.loc[stops == edge["Station"]]
                # print(matches)
                for id in matches.index:                #origin destination
                    self.gdf.at[id, 'edges'].append(tuple(on_the_way))
                    # self.gdf.at[id, 'edges'].append([on_the_way], {dictionary with attributes})


        self.gdf['edges'] = self.gdf['edges'].apply(lambda x: list(set(x)) if isinstance(x, list) else x)
        self.edgelist = sum(self.gdf['edges'].tolist(), [])
        self.nxgraph = gdf_to_nx(self.gdf,self.edgelist)

        self.gdf_filter = get_nodes(stops_file, self.gdf)
        self.map = interactable_map(self.gdf_filter,os.path.join("data", "interact_map.html"))     #interactable map open it to view  

        l_graph_edges = pd.DataFrame(l_graph_edges, columns=['Begin station', 'End station', 'Stops on the way'])
        self.graph = create_P_graph(l_graph_edges) 
        # self.graph = create_P_graph(self.map)   

    def create_p_graph(self):
        plot_P_graph(self.graph, self.gdf)

    def analyse_original_network(self):
        passengers = self.stop_data.drop_duplicates("Station")["Getting_on_off"].to_list()
        self.OD_matrix = self.rail.determine_O_D(passengers, passengers)
        routes = Matrix_To_Routes(self.OD_matrix, self.graph, self.stations.to_list())
        passenger_data = Visualisation_travelers(self.graph, routes, self.OD_matrix, self.gdf)
        print(passenger_data)
        interactable_map(self.gdf_filter, os.path.join("data", "original_network.html"), self.graph, passenger_data)

    def analyse_extended_network(self, extra_stations, new_travel_times:pd.DataFrame):
        extended_stations = pd.concat((self.stations, extra_stations["Station"]), ignore_index=True).drop_duplicates()
        extended_travel_times = pd.concat((self.travel_times, new_travel_times), ignore_index=True)

        edges = pd.concat((self.stop_data.copy().dropna(ignore_index=True), extra_stations), ignore_index=True)
        p_graph = []
        for i in range(len(edges)):
            edge = edges.iloc[i]
            if edge["Direction_to"] in edges["Station"].values:
                p_graph.append([edge["Station"], edge["Direction_to"], [edge["Station"], edge["Direction_to"]]])
        p_graph = pd.DataFrame(p_graph, columns=['Begin station', 'End station', 'Stops on the way'])
        extended_graph = create_P_graph(p_graph) 

        passengers = edges.drop_duplicates("Station")["Getting_on_off"].to_list()
        extended_rail_map = Railmap(extended_stations.to_list(), extended_travel_times)
        extended_OD_matrix = extended_rail_map.determine_O_D(passengers, passengers)
        extended_network_routes = Matrix_To_Routes(extended_OD_matrix, extended_graph, extended_stations.to_list())
        Visualisation_travelers(extended_graph, extended_network_routes, extended_OD_matrix, self.gdf)


if __name__ == "__main__":
    analysis = Analyser()
    # analysis.create_p_graph()
    analysis.analyse_original_network()
    additional_stations = pd.DataFrame({"Station":["Emmeloord", "Drachten", "Heerenveen", "Groningen"], 
                                        "Travelers_per_day":[3177, 5314, 5001, 16064], 
                                        "Getting_on_off":[3177, 5314, 4970, 16064], 
                                        "Direction_to":["Lelystad Centrum", "Heerenveen", "Emmeloord", "Drachten"],
                                        "Switchers":[0,0,0,0],
                                        "Travelers_to":[0,0,0,0]})
    new_travel_times = pd.DataFrame({"travel_time_min": [13,8,14,13], 
                                     "from_station":["Groningen", "Drachten", "Heerenveen", "Emmeloord"], 
                                    "to_station": ["Drachten", "Heerenveen", "Emmeloord", "Lelystad Centrum"]})
    # analysis.analyse_extended_network(additional_stations, new_travel_times)
    
    # tests
    # print(analysis.gdf.head()) #GDF 
    # print(analysis.gdf.loc[analysis.gdf["stop_name"]=='Zwolle', 'edges'].tolist())
    # print(analysis.gdf.loc[analysis.gdf["stop_name"]=='Meppel', 'edges'].tolist())
    # print(analysis.edgelist)