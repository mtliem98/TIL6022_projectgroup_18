def show_shortest_path_diff_table(self, additional_stations, new_travel_times):
    # filter the stations
    filter_stations = [
            "Groningen", "Leeuwarden", "Zwolle", "Lelystad Centrum",
            "Amsterdam Centraal", "Utrecht Centraal", "Amersfoort Centraal", "Weesp"]
    
    # shortest travel times in original network
    self.analyse_original_network()
    old_paths, old_times = self.rail.get_shortest_path_matrix()

    # shortest travel times in new network
    self.analyse_extended_network(additional_stations, new_travel_times)
    new_paths, new_times = self.rail.get_shortest_path_matrix()

    # dataframe with old and new times
    stations = self.stations.to_list()
    df_old = pd.DataFrame(old_times, index=stations, columns=stations)
    df_new = pd.DataFrame(new_times, index=stations, columns=stations)
    # dataframe with old and new times for filtered stations
    df_old_filtered = df_old.loc[filter_stations, filter_stations]
    df_new_filtered = df_new.loc[filter_stations, filter_stations]
    # dataframe with time difference old and new network
    df_diff = df_new_filtered - df_old_filtered 

    # replace 0 with ""
    cell_text = np.where(df_filtered.values == 0, "", np.round(df_filtered.values, 1))

    #normalize for coloring
    if np.nanmax(np.abs(df_diff.values)) == 0:
        norm_data = np.zeros_like(df_diff.values)
    else:
        norm_data = df_diff.values / np.nanmax(df_diff.values)

    # plot table
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.set_axis_off()

        table = ax.table(
            cellText=cell_text,
            rowLabels=df_diff.index,
            colLabels=df_diff.columns,
            cellColours=plt.cm.BuGn(norm_data),
            # the coloring expects the values to start from 0, as no increase in travel time is expected
            loc='center'
        )

        plt.show()