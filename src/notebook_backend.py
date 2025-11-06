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
        #gtfs_path = os.path.join("data", "gtfs-nl", "stops.txt")
        gtfs_path = os.path.join("data", "gtfs-nl", "")
        gdf = load_gdf(gtfs_path, "stops.txt") 
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
        #print(self.rail.get_shortest_path_matrix())

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
        self.OD_matrix = self.rail.determine_O_D(passengers, passengers)
        routes = Matrix_To_Routes(self.OD_matrix, self.graph, self.stations.to_list())
        Visualisation_travelers(self.graph, routes, self.OD_matrix, self.gdf)

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

    def show_shortest_path_table(self):
        # stations to filter
        filter_stations = [
            "Groningen", "Leeuwarden", "Zwolle", "Lelystad Centrum",
            "Amsterdam Centraal", "Utrecht Centraal", "Amersfoort Centraal", "Weesp"]

        # shortest path data
        paths, times = self.rail.get_shortest_path_matrix()

        # infinities with zeros
        safe_times = np.where(np.isfinite(times), times, 0)
        safe_times = np.nan_to_num(safe_times, nan=0)

        # convert to dataframe with station labels
        stations = self.stations.to_list()
        df = pd.DataFrame(safe_times, index=stations, columns=stations)

        # filter for the selected stations
        df_filtered = df.loc[filter_stations, filter_stations]

        cell_text = np.empty(df_filtered.shape, dtype=object)
        for i in range(df_filtered.shape[0]):
            for j in range(df_filtered.shape[1]):
                val = df_filtered.iloc[i, j]
                cell_text[i, j] = f"{val:.1f} min" if val != 0 else ""

        # normalize for coloring
        norm_data = df_filtered.values / np.nanmax(df_filtered.values)

        # plot table
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.set_axis_off()

        table = ax.table(
            cellText=cell_text,
            rowLabels=df_filtered.index,
            colLabels=df_filtered.columns,
            cellColours=plt.cm.BuGn(norm_data),
            # the coloring exptects the values to start from 0, as no increase in travel time is expected
            loc='center'
        )

        # adjust table scale and alignment
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1, 1)

        # get table bounding box for positioning labels
        plt.draw()  # need to render to get table bbox
        bbox = table.get_window_extent(fig.canvas.get_renderer())
        inv = ax.transData.inverted()
        bbox_data = inv.transform(bbox)

        # add titles directly above and to the left of the table
        ax.text(
            (bbox_data[0][0] + bbox_data[1][0]) / 2,
            bbox_data[1][1] + 0.1,
            "Destination station")

        ax.text(
            bbox_data[0][0] + 0.04,
            (bbox_data[0][1] + bbox_data[1][1]) / 2,
            "Origin station",
            rotation="vertical")

        plt.show()

    def show_shortest_path_diff_table(self, additional_stations, new_travel_times):
        # filter the stations
        filter_stations = [
            "Groningen", "Leeuwarden", "Zwolle", "Lelystad Centrum",
            "Amsterdam Centraal", "Utrecht Centraal", "Amersfoort Centraal", "Weesp"]
    
        # shortest travel times in original network
        old_paths, old_times = self.rail.get_shortest_path_matrix()

        # shortest travel times in new network
        extended_stations = pd.concat((self.stations, additional_stations["Station"]), ignore_index=True).drop_duplicates()
        extended_travel_times = pd.concat((self.travel_times, new_travel_times), ignore_index=True)
        #self.analyse_extended_network(additional_stations, new_travel_times)
        temp_rail = Railmap(extended_stations.to_list(), extended_travel_times)
        new_paths, new_times = temp_rail.get_shortest_path_matrix()

        # dataframe with old and new times
        stations = self.stations.to_list()
        df_old = pd.DataFrame(old_times, index=stations, columns=stations)
        df_new = pd.DataFrame(new_times, index=extended_stations, columns=extended_stations)
        # dataframe with old and new times for filtered stations
        df_old_filtered = df_old.loc[filter_stations, filter_stations]
        df_new_filtered = df_new.loc[filter_stations, filter_stations]
        # dataframe with time difference old and new network
        df_diff = df_new_filtered - df_old_filtered 

        # replace 0 with ""
        cell_text = np.where(df_diff == 0, "", np.round(df_diff.values, 1))

        #normalize for coloring
        if np.nanmax(df_diff.values) - np.nanmin(df_diff.values) == 0:
            norm_data = np.zeros_like(df_diff.values)
        else:
            norm_data = (df_diff.values - np.nanmin(df_diff.values)) / (np.nanmax(df_diff.values) - np.nanmin(df_diff.values))
        #norm_data = np.abs(df_diff.values / np.nanmax(df_diff.values))

        # cell text
        cell_text = np.empty(df_diff.shape, dtype=object)
        for i in range(df_diff.shape[0]):
            for j in range(df_diff.shape[1]):
                val = df_diff.iloc[i, j]
                cell_text[i, j] = f"{val:.1f} min" if val != 0 else "" 

        # plot table
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.set_axis_off()

        table = ax.table(
            cellText=cell_text,
            rowLabels=df_diff.index,
            colLabels=df_diff.columns,
            cellColours=plt.cm.BuGn_r(norm_data),
            # the coloring exptects the values to start from 0, as no increase in travel time is expected
            loc='center'
        )

        # adjust table scale and alignment
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1, 1)

        # get table bounding box for positioning labels
        plt.draw()  # need to render to get table bbox
        bbox = table.get_window_extent(fig.canvas.get_renderer())
        inv = ax.transData.inverted()
        bbox_data = inv.transform(bbox)

        # add titles directly above and to the left of the table
        ax.text(
            (bbox_data[0][0] + bbox_data[1][0]) / 2,
            bbox_data[1][1] + 0.1,
            "Destination station")

        ax.text(
            bbox_data[0][0] + 0.04,
            (bbox_data[0][1] + bbox_data[1][1]) / 2,
            "Origin station",
            rotation="vertical")

        plt.show()

if __name__ == "__main__":
    analysis = Analyser()
    #analysis.create_p_graph()
    #analysis.analyse_original_network()
    additional_stations = pd.DataFrame({"Station":["Emmeloord", "Drachten", "Heerenveen", "Groningen"], 
                                        "Travelers_per_day":[3177, 5314, 5001, 16064], 
                                        "Getting_on_off":[3177, 5314, 4970, 16064], 
                                        "Direction_to":["Lelystad Centrum", "Heerenveen", "Emmeloord", "Drachten"],
                                        "Switchers":[0,0,0,0],
                                        "Travelers_to":[0,0,0,0]})
    new_travel_times = pd.DataFrame({"travel_time_min": [13,8,14,13], 
                                     "from_station":["Groningen", "Drachten", "Heerenveen", "Emmeloord"], 
                                    "to_station": ["Drachten", "Heerenveen", "Emmeloord", "Lelystad Centrum"]})
    analysis.analyse_extended_network(additional_stations, new_travel_times)
    analysis.show_shortest_path_table()
    analysis.show_shortest_path_diff_table(additional_stations, new_travel_times)
