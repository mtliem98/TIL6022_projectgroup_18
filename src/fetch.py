import os
import time
import requests
import zipfile

GTFS_URL = "https://gtfs.ovapi.nl/nl/gtfs-nl.zip" # specify data source

# file is downloaded to the same directory as the .py file
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ZIP_FILE = os.path.join(SCRIPT_DIR, "..", "data", "gtfs-nl.zip")

MAX_AGE_HOURS = 24 # specify max age of local file in hrs

def is_file_old(path, max_age_hours=24):
# checks if .zip file is missing or older than the max age
    if not os.path.exists(path): # doesnt exist
        return True
    age_hours = (time.time() - os.path.getmtime(path)) / 3600
    return age_hours > max_age_hours # or older than expected

def is_data_old(path, max_age_hours=24):
# check the age of the downloaded data
    if not os.path.exists(path):
        return True
    newest_time = os.path.getmtime(os.path.join(dp, f)
                      for dp, _, files in os.walk(path) for f in files)
    # checks the age of the oldest downloaded file
    age_hours = (time.time() - newest_time) / 3600
    return age_hours > max_age_hours

def download_gtfs(url, filename):
    #downloads linked file
    headers = {"User-Agent": "Mozilla/5.0 (compatible; Python script)"}
    print("Downloading GTFS data")
    response = requests.get(url, headers=headers, stream=True)
    response.raise_for_status()
    with open(filename, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print("Download complete")

def extract_zip(zip_path, extract_to):
    #print(f"Extracting {os.path.basename(zip_path)} to {extract_to}...")
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)
    print("Extraction complete")

def main():
    # extract from existing .zip file if it’s not too old
    if not is_file_old(ZIP_FILE, MAX_AGE_HOURS):
        # to prevent getting rate limited by remote server
        print(".zip file is within requested age")
    else:
        print(".zip file missing or old, downloading new data")
        download_gtfs(GTFS_URL, ZIP_FILE)
    # overwrites the extracted files regardless of their age
    extract_zip(ZIP_FILE, os.path.join(SCRIPT_DIR, "..", "data", "gtfs-nl"))

if __name__ == "__main__":
    main()
