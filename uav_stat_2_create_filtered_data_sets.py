import json
import os
import warnings
import datetime
import time
import re
import logging


# -----------------
# Globals
# -----------------

ROOT                                = os.getcwd()
INPUT_FILES_DIR_NAME                = "2_processed_input_files"
INPUT_FILES_DIR_PATH                = os.path.join(ROOT, INPUT_FILES_DIR_NAME)

OUTPUT_FILES_DIR_NAME               = "3_filtered_datasets"
OUTPUT_FILES_DIR_PATH               = os.path.join(ROOT, OUTPUT_FILES_DIR_NAME)

INPUT_FILE_NAME_PROCESSED_DATA     = "processed_input_files_data.json"
INPUT_FILE_PATH_PROCESSED_DATA     = os.path.join(INPUT_FILES_DIR_PATH, INPUT_FILE_NAME_PROCESSED_DATA)

OUTPUT_FILE_1_NAME                  = "every_uav_segregated_airspace.json"
OUTPUT_FILE_1_PATH                  = os.path.join(OUTPUT_FILES_DIR_PATH, OUTPUT_FILE_1_NAME)

LOG_FILE_NAME                       = "2_filtering_datasets.log"
LOG_FILE_PATH                       = os.path.join(OUTPUT_FILES_DIR_PATH, LOG_FILE_NAME)

# -----------------
# Configure logging
# -----------------
logging.basicConfig(
    filename    = LOG_FILE_PATH,
    filemode    = "w",
    format      = "%(asctime)s - %(message)s", 
    level       = logging.INFO
)


# TODO: 1. filter out only the UAV flights into another similar json file, as the main input. ALL input -> UAV flights -> data sets of differnt graphs
# TODO: 2. Implement functions to filter out data sets which fits best each type of graph.

def json_to_dict(json_file_path):

    with open(json_file_path, 'r', encoding='utf-8') as json_file:
        ret_dict = json.load(json_file)
    
    return ret_dict

def create_uav_data_json(dict_to_filter, json_file_path):

    mission_type_key = "mission_type_eng"
    key_word         = "UAV flight"
    uav_data = {}

    number_of_items = len(dict_to_filter)

    print("{} item found in the input dictionary".format(number_of_items))
    print("Start filtering UAV segregated airspaces")

    cntr = 1
    for key in dict_to_filter:

        item = dict_to_filter[key]

        if item[mission_type_key] == key_word:
            uav_data.update({key : item})

        msg = "[{:6}/{:6}] item processed.".format(cntr, number_of_items)
        print(msg)
        cntr += 1

    print("{} items found with mission type: 'UAV flight'.".format(len(uav_data)))
    print("Saving filtered, UAV segregated airspace json to: {} ".format(json_file_path))
    save_dict_to_json(uav_data, json_file_path)

def save_dict_to_json(input_dict, file_path):

    with open(file_path, 'w+', encoding='utf-8') as json_file:
        json.dump(input_dict, json_file, indent=4, default=str)


def main():

    print('/' * 50)
    print("Script started")

    print("Opening json file to process {}".format(INPUT_FILE_PATH_PROCESSED_DATA))
    data_to_filter = json_to_dict(INPUT_FILE_PATH_PROCESSED_DATA)
    create_uav_data_json(data_to_filter, OUTPUT_FILE_1_PATH)


if __name__ == "__main__":
    main()

