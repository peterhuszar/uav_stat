import json
import os
import warnings
import datetime
import time
import re
import logging

ROOT                                = os.getcwd()
OUTPUT_FILES_DIR_NAME               = "output_files"
OUTPUT_FILES_DIR_PATH               = os.path.join(ROOT, OUTPUT_FILES_DIR_NAME)
OUTPUT_FILE_NAME_PROCESSED_DATA     = "processed_data.json"
OUTPUT_FILE_PATH_PROCESSED_DATA     = os.path.join(OUTPUT_FILES_DIR_PATH, OUTPUT_FILE_NAME_PROCESSED_DATA)
LOG_FILE_NAME                       = "log_of_last_run_script_2.log"
LOG_FILE_PATH                       = os.path.join(OUTPUT_FILES_DIR_PATH, LOG_FILE_NAME)




# TODO: 1. filter out only the UAB flights into another similar json file, as the main input. ALL input -> UAV flights -> data sets of differnt graphs
# TODO: 2. Implement functions to filter out data sets which fits best each type of graph.
