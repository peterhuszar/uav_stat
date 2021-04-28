import json
import os
import warnings
import datetime
import time
import re
import logging

ROOT                                = os.getcwd()
INPUT_FILES_DIR_NAME                = "2_processed_input_files"
INPUT_FILES_DIR_PATH                = os.path.join(ROOT, INPUT_FILES_DIR_NAME)
OUTPUT_FILES_DIR_NAME               = "3_filtered_datasets"
OUTPUT_FILES_DIR_PATH               = os.path.join(ROOT, OUTPUT_FILES_DIR_NAME)
OUTPUT_FILE_PATH_PROCESSED_DATA     = os.path.join(OUTPUT_FILES_DIR_PATH, OUTPUT_FILE_NAME_PROCESSED_DATA)
LOG_FILE_NAME                       = "2_filtering_datasets.log"
LOG_FILE_PATH                       = os.path.join(OUTPUT_FILES_DIR_PATH, LOG_FILE_NAME)

logging.basicConfig(
    filename    = LOG_FILE_PATH,
    filemode    = "w",
    format      = "%(asctime)s - %(message)s", 
    level       = logging.INFO
)


# TODO: 1. filter out only the UAV flights into another similar json file, as the main input. ALL input -> UAV flights -> data sets of differnt graphs
# TODO: 2. Implement functions to filter out data sets which fits best each type of graph.

def 
