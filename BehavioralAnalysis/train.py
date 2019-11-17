import argparse
import os
import pandas as pd
from blob_service import BlobService
import time
from BehavioralAnalysis.run import execute

MKL_NUM_THREADS=1
OPENBLAS_NUM_THREADS=1
EVENTS_FILE = "raw_events_08_01.csv"
STATIONS_FILE = "stations_with_labels.csv"
OUTPUT_FILE = "export_08_01.csv"

def compute_tags_assignments(stations, events):
    return execute(stations, events)

def main():
    parser = argparse.ArgumentParser("train")

    parser.add_argument("--input_path", type=str, help="Input path for further pipeline steps")
    parser.add_argument("--output", type=str, help="Output predictions")
    parser.add_argument("--input_container", type=str, help="Input container")
    parser.add_argument("--output_container", type=str, help="output container")
    parser.add_argument("--input_account", type=str, help="Input storage account")
    parser.add_argument("--input_key", type=str, help="Input storage account key")

    args = parser.parse_args()

    print("Argument 1: %s" % args.input_path)
    print("Argument 2: %s" % args.output)
    print("Argument 3: %s" % args.input_container)

    blob_service_ref = BlobService(args.input_account, args.input_key, args.input_container)

    os.makedirs(args.input_path, exist_ok=True)
    stations_path = os.path.join(args.input_path, STATIONS_FILE)
    events_path = os.path.join(args.input_path, EVENTS_FILE)

    blob_service_ref.get_blob(STATIONS_FILE, stations_path)
    blob_service_ref.get_blob(EVENTS_FILE, events_path)

    stations = pd.read_csv(stations_path)
    events = pd.read_csv(events_path)

    print(stations.shape)
    print(events.shape)
    print(stations.iloc[:5,:])
    print(events.iloc[:5,:])

    tags_assignments = compute_tags_assignments(stations, events)

    os.makedirs(args.output, exist_ok=True)
    output_temp_path = os.path.join(args.output, OUTPUT_FILE)
    
    tags_assignments.to_csv(output_temp_path, index=False)

    blob_service_ref = BlobService(args.input_account, args.input_key, args.output_container)
    #blob_service_ref.store_blob(output_temp_path, os.path.join(OUTPUT_FILE))
    blob_service_ref.store_blob(output_temp_path, os.path.join(time.strftime("%Y-%m-%d"), OUTPUT_FILE))

    print("Completed!")
    
    
if __name__ == "__main__":
    main()