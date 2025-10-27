from GTFS_load_gdf import *
import fetch
from Pgraph import *
from travel_time import *
import pandas as pd

class Analyser:

    def __init__(self):
        fetch.main()
        gtfs_path = os.path.join("data", "gtfs-nl")
        load_gdf(gtfs_path, "/stops.txt")
        if not os.path.exists(os.path.join("data", "median_travel_times.csv")):
            determine_median_travel_times()
        travel_times = pd.read_csv(os.path.join("data", "median_travel_times.csv"))
        print(travel_times)




if __name__ == "__main__":
    Analyser()