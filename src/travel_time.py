import pandas as pd
import os

def determine_median_travel_times():
    # loading files
    #SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    GTFS_PATH = os.path.join("data", "gtfs-nl")

    stops = pd.read_csv(os.path.join(GTFS_PATH, "stops.txt"), low_memory=False)
    stop_times = pd.read_csv(os.path.join(GTFS_PATH, "stop_times.txt"), low_memory=False)
    trips = pd.read_csv(os.path.join(GTFS_PATH, "trips.txt"), low_memory=False)
    routes = pd.read_csv(os.path.join(GTFS_PATH, "routes.txt"), low_memory=False)

    # filtering only domestic NS trains
    ns_routes = routes[(routes["agency_id"] == "IFF:NS") & (routes["route_type"] == 2)]
    ns_trips = trips[trips["route_id"].isin(ns_routes["route_id"])]
    ns_stop_times = stop_times[stop_times["trip_id"].isin(ns_trips["trip_id"])]

    ns_stop_times["stop_id"] = ns_stop_times["stop_id"].astype(str)
    stops["stop_id"] = stops["stop_id"].astype(str)

    # so that output is in minutes
    def time_to_minutes(t):
        try:
            h, m, s = map(int, t.split(":"))
            return h * 60 + m + s / 60
        except Exception:
            return None

    # computing travel time for consecutive stops
    ns_stop_times = ns_stop_times.sort_values(by=["trip_id", "stop_sequence"])
    rows = []

    for trip_id, group in ns_stop_times.groupby("trip_id"):
        group = group.reset_index(drop=True)
        for i in range(len(group) - 1):
            dep = time_to_minutes(group.loc[i, "departure_time"])
            arr = time_to_minutes(group.loc[i + 1, "arrival_time"])
            if dep is None or arr is None or arr <= dep:
                continue
            rows.append((
                group.loc[i, "stop_id"],
                group.loc[i + 1, "stop_id"],
                arr - dep
            ))

    df = pd.DataFrame(rows, columns=["from_stop", "to_stop", "travel_time_min"])

    # arranging them into a dataframe
    stops_slim = stops[["stop_id", "stop_name"]]
    df = df.merge(stops_slim, left_on="from_stop", right_on="stop_id", how="left")
    df = df.rename(columns={"stop_name": "from_station"}).drop(columns=["stop_id"])

    df = df.merge(stops_slim, left_on="to_stop", right_on="stop_id", how="left")
    df = df.rename(columns={"stop_name": "to_station"}).drop(columns=["stop_id"])

    df = df[["from_station", "to_station", "travel_time_min"]].dropna()
    df["from_station"] = df["from_station"].astype(str)
    df["to_station"] = df["to_station"].astype(str)

    # one edge is only appears once (A>B and B>A in one line only)
    df["station_pair"] = df.apply(lambda x: tuple(sorted([x["from_station"], x["to_station"]])), axis=1)
    df = df[df["station_pair"].apply(lambda x: isinstance(x, tuple) and len(x) == 2)]

    # computing median
    df_grouped = df.groupby("station_pair", as_index=False)["travel_time_min"].median()

    df_grouped[["from_station", "to_station"]] = pd.DataFrame(df_grouped["station_pair"].tolist(), index=df_grouped.index)
    df_grouped = df_grouped.drop(columns=["station_pair"])

    # exporting to csv
    df_grouped.to_csv(os.path.join("data", "median_travel_times.csv"), index=False)

if __name__ == "__main__":
    determine_median_travel_times()