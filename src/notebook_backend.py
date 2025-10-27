from GTFS_load_gdf import *
import fetch
from Pgraph import *

class Analyser:

    def __init__(self):
        fetch.main()
        gtfs_path = os.path.join("data", "gtfs-nl")
        load_gdf(gtfs_path, "/stops.txt")
        


if __name__ == "__main__":
    Analyser()