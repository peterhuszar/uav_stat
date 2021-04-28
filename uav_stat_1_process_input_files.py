import xlrd
import json
import os
import warnings
import datetime
import time
import re
import logging
import shortuuid

SHEET_OF_INTEREST = 3

ROOT                                = os.getcwd()
INPUT_FILES_DIR_NAME                = "1_raw_input_files"
INPUT_FILES_DIR_PATH                = os.path.join(ROOT, INPUT_FILES_DIR_NAME)
OUTPUT_FILES_DIR_NAME               = "2_processed_input_files"
OUTPUT_FILES_DIR_PATH               = os.path.join(ROOT, OUTPUT_FILES_DIR_NAME)
OUTPUT_FILE_NAME_PROCESSED_DATA     = "processed_inputfiles_data.json"
OUTPUT_FILE_PATH_PROCESSED_DATA     = os.path.join(OUTPUT_FILES_DIR_PATH, OUTPUT_FILE_NAME_PROCESSED_DATA)
LOG_FILE_NAME                       = "raw_input_file_processing.log"
LOG_FILE_PATH                       = os.path.join(OUTPUT_FILES_DIR_PATH, LOG_FILE_NAME)

logging.basicConfig(
    filename    = LOG_FILE_PATH,
    filemode    = "w",
    format      = "%(asctime)s - %(message)s", 
    level       = logging.INFO
)

def process_excel_file(excel_file_path, excel_sheet_number):
    # Function to process a single Excel log file.

    workbook                = xlrd.open_workbook(excel_file_path)
    sheet                   = workbook.sheet_by_index(excel_sheet_number) 

    all_airspace_args = []
    single_airspace_args = []
    airspace_items_in_file = []

    data_of_interest_reached = False

    excel_file_name = get_excel_file_name(excel_file_path)

    for row in range(0, sheet.nrows):
        
        row_content = sheet.row_values(row)
        first_item_in_row = row_content[0]

        if first_item_in_row == 1:
            data_of_interest_reached = True

        if data_of_interest_reached:
            
            if first_item_in_row != '' and first_item_in_row != '.' and len(single_airspace_args) > 0:
                all_airspace_args.append(single_airspace_args)
                single_airspace_args = []
            single_airspace_args.append(row_content)

    for item in all_airspace_args:

        single_airspace_item = create_single_airspace_dict(item, excel_file_name)
        item_key = excel_file_name.strip('.xls')
        item_key = item_key.replace('.', '_')
        item_key = item_key.replace(' ', '_')
        item_key =  item_key + '_' + str(single_airspace_item['serial_number']) + '_' + str(shortuuid.uuid())
        
        # This slows down the script as hell...
        # add_dict_to_output_json({item_key: single_airspace_item}, output_json_path)

        airspace_items_in_file.append({ item_key: single_airspace_item })

    return airspace_items_in_file
        
def create_single_airspace_dict(rows_to_process, origin_of_rows):

    date               = excel_file_name_to_date(origin_of_rows)
    op_time_plan_start = get_op_time_plan_start(rows_to_process, date)
    op_time_plan_end   = get_op_time_plan_end(rows_to_process, date)
    op_time_act_start  = get_op_time_act_start(rows_to_process, date)
    op_time_act_end    = get_op_time_act_end(rows_to_process, date)

    single_airspace_dict = {
        "file_id"                  : origin_of_rows, 
        "date"                     : date,
        "serial_number"            : get_sa_serial_number(rows_to_process),
        "boundary_coord_poly"      : get_boundary_coord_poly(rows_to_process),
        "boundary_coord_circle"    : get_boundary_coord_circle(rows_to_process),
        "place_name"               : get_place_name(rows_to_process),
        "boundary_alt_l"           : get_boundary_alt_l(rows_to_process),
        "boundary_alt_h"           : get_boundary_alt_h(rows_to_process),
        "op_time_plan_start"       : op_time_plan_start,
        "op_time_plan_end"         : op_time_plan_end,
        "op_duration_plan"         : get_op_duration_plan(op_time_plan_start, op_time_plan_end),
        "op_time_act_start"        : op_time_act_start,
        "op_time_act_end"          : op_time_act_end,
        "op_duration_act"          : get_op_duration_act(op_time_act_start, op_time_act_end),
        "applicant_name"           : get_applicant_name(rows_to_process),
        "applicant_phone"          : get_applicant_phone(rows_to_process),
        "mission_type_hun"         : get_mission_type_hun(rows_to_process),
        "mission_type_eng"         : get_mission_type_eng(rows_to_process),
        "matias_or_lara_id"        : get_matias_or_lara_id(rows_to_process),
    }

    # print(origin_of_rows)
    # print(date)
    # print(get_sa_serial_number(rows_to_process))
    # print(get_boundary_coord_poly(rows_to_process))
    # print(get_boundary_coord_circle(rows_to_process))
    # print(get_place_name(rows_to_process))
    # print(get_boundary_alt_l(rows_to_process))
    # print(get_boundary_alt_h(rows_to_process))
    # print(get_op_time_plan_start(rows_to_process, date))
    # print(get_op_time_plan_end(rows_to_process, date))
    # print(get_op_duration_plan(op_time_plan_start, op_time_plan_end))
    # print(get_op_time_act_start(rows_to_process, date))
    # print(get_op_time_act_end(rows_to_process, date))
    # print(get_op_duration_act(op_time_act_start, op_time_act_end))
    # print(get_applicant_name(rows_to_process))
    # print(get_applicant_phone(rows_to_process))
    # print(get_mission_type_hun(rows_to_process))
    # print(get_mission_type_eng(rows_to_process))
    # print(get_matias_or_lara_id(rows_to_process))

    return single_airspace_dict

def get_sa_serial_number(rows_to_process):

    sa_serial_number = rows_to_process[0][0]
    
    try:
        return int(float(rows_to_process[0][0]))
    except ValueError:
        msg = 'Ad-hoc segregated airspace serial number processing error! See inputted rows: {}'.format(rows_to_process)
        logging.warning(msg)
        # print(msg)
        # warnings.warn(msg)

def get_boundary_coord_circle(rows_to_process):

    try:
        cell_to_check_1 = rows_to_process[0][1]
        cell_to_check_2 = rows_to_process[1][1]
    
    except IndexError:
        return None

    if (('N' in cell_to_check_1) and 
            ('E' in cell_to_check_1) and
            ('r' in cell_to_check_2) and
            ('=' in cell_to_check_2)):
        
        raw_cell_content = [row[1] for row in rows_to_process if (row[1] != '' and '(' not in row[1] and ')' not in row[1])]
        
        raw_radius = raw_cell_content[1]

        # TODO: regex pattern could be fixed to matcth the unit except white spaces. Now I am stripping it when returning.
        r = re.search('([0-9]+)(.*)', raw_radius)
        radius = r.group(1)
        unit = r.group(2)

        return [raw_cell_content[0], float(radius), unit.strip()]

    else:
        return None

def get_boundary_coord_poly(rows_to_process):

    content_of_cells = []
    not_coordinate = []
    ret_coordinates = []

    try:
        cell_to_check = rows_to_process[1][1]
    except IndexError:
        return None

    if 'r' not in cell_to_check and '=' not in cell_to_check:
        content_of_cells = [row[1] for row in rows_to_process if (row[1] != '' and '(' not in row[1] and ')' not in row[1])]
    else:
        return None

    for cell in content_of_cells:
        coordinates = cell.split(' ')
        if len(coordinates) == 2:
            coordinate_1 = string_to_gps_coordinate(coordinates[0])
            coordinate_2 = string_to_gps_coordinate(coordinates[1])
            if coordinate_1 and coordinate_2:
                gps_coordinate_pair = (coordinate_1, coordinate_2)
                ret_coordinates.append(gps_coordinate_pair)
    
    return ret_coordinates


            
        

def get_place_name(rows_to_process):

    second_col = [row[1] for row in rows_to_process if row[1] != '']
    place_name = second_col[-1]
    place_name = place_name.strip('()')

    return place_name

def get_boundary_alt_l(rows_to_process):
    
    usual_lower_altitude = 'GND'

    if rows_to_process[0][3] != usual_lower_altitude:
        msg = "Ad-hoc segregated airspace lower boundary altitude is other than {}! Please verify. See inputted rows: {}".format(usual_lower_altitude, rows_to_process)
        logging.warning(msg)
        # print(msg)
        # warnings.warn(msg)
    
    return rows_to_process[0][3]

def get_boundary_alt_h(rows_to_process):

    try:
        boundary_alt_h = rows_to_process[0][4]
        reference = rows_to_process[1][4]
    except IndexError:
        return None

    if boundary_alt_h == '':
        msg = "Ad-hoc segregated airspace higher boundary altitude could be faulty! Please verify. See inputted rows: {}".format(rows_to_process)
        logging.warning(msg)
        # print(msg)
        # warnings.warn(msg)

    boundary_alt_h = boundary_alt_h.split(' ')
    boundary_alt_h.append(reference)

    try:
        boundary_alt_h[0] = float(boundary_alt_h[0])
    except ValueError:
        msg = "Ad-hoc segregated airspace higher boundary altitude could be faulty! {}! Please verify. See inputted rows: {}".format(boundary_alt_h, rows_to_process)
        logging.warning(msg)
        # print(msg)
        # warnings.warn(msg)
    
    return boundary_alt_h

def get_op_time_plan_start(rows_to_process, date):

    try:
        op_time_plan_start = xlrd.xldate_as_tuple(rows_to_process[0][5], 1)
    except TypeError:
        return None

    return datetime.datetime(date.year, date.month, date.day, op_time_plan_start[3], op_time_plan_start[4], op_time_plan_start[5])

def get_op_time_plan_end(rows_to_process, date):

    try:
        op_time_plan_end = xlrd.xldate_as_tuple(rows_to_process[0][6], 1)
    except  TypeError:
        return None

    return datetime.datetime(date.year, date.month, date.day, op_time_plan_end[3], op_time_plan_end[4], op_time_plan_end[5])

def get_op_duration_plan(earlier_datetime, latter_datetime):

    duration = None

    try:
        duration = latter_datetime - earlier_datetime
    except TypeError:
        msg = "Could not calculate planned operation duration with the followings: t1 = {} t2 = {}".format(earlier_datetime, latter_datetime)
        logging.warning(msg)
        # print(msg)
        # warnings.warn(msg)

    return duration

def get_op_duration_act(earlier_datetime, latter_datetime):

    duration = None

    try:
        duration = latter_datetime - earlier_datetime
    except TypeError:
        msg = "Could not calculate actual operation duration with the followings: t1 = {} t2 = {}".format(earlier_datetime, latter_datetime)
        # logging.warning(msg)
        logging.debug(msg)  # Level had to set lower because there was too many of this log entry, though it is not really important.
        # print(msg)
        # warnings.warn(msg)

    return duration

def get_op_time_act_start(rows_to_process, date):

    try:
        op_time_act_start_0 = rows_to_process[0][9]
        op_time_act_start_1 = rows_to_process[1][9]
    except IndexError:
        return None

    if op_time_act_start_0 != '':
        try:
            op_time_act_start = xlrd.xldate_as_tuple(op_time_act_start_0, 1)
        except TypeError:
            return None
    
    elif op_time_act_start_1 != '':
        try:
            op_time_act_start = xlrd.xldate_as_tuple(op_time_act_start_1, 1)
        except TypeError:
            return None
    else:
        return None

    return datetime.datetime(date.year, date.month, date.day, op_time_act_start[3], op_time_act_start[4], op_time_act_start[5])

def get_op_time_act_end(rows_to_process, date):

    try:
        op_time_act_end_0 = rows_to_process[0][10]
        op_time_act_end_1 = rows_to_process[1][10]
    except IndexError:
        return None

    if op_time_act_end_0 != '':
        try:
            op_time_act_end = xlrd.xldate_as_tuple(op_time_act_end_0, 1)
        except TypeError:
            return None

    elif op_time_act_end_1 != '':
        try:
            op_time_act_end = xlrd.xldate_as_tuple(op_time_act_end_1, 1)
        except TypeError:
            return None

    else:
        return None
    
    return datetime.datetime(date.year, date.month, date.day, op_time_act_end[3], op_time_act_end[4], op_time_act_end[5])

def get_applicant_name(rows_to_process):

    applicant_name = rows_to_process[0][7]

    if applicant_name == '':
        msg =  "Ad-hoc segregated airspace applicant name could be faulty! Please verify. See inputted rows: {}".format(rows_to_process)
        logging.warning(msg)
        # print(msg)
        # warnings.warn(msg)
    
    return applicant_name
    
def get_applicant_phone(rows_to_process):

    try:
        applicant_phone = str(rows_to_process[1][7])
    except IndexError:
        return None

    if applicant_phone == '':
        msg = "Ad-hoc segregated airspace applicant phone number could be faulty! Please verify. See inputted rows: {}".format(rows_to_process) 
        logging.warning(msg)
        # print(msg)
        # warnings.warn(msg)
    
    applicant_phone = applicant_phone.replace('/', '')

    return applicant_phone

def get_mission_type_hun(rows_to_process):

    mission_type_hun = rows_to_process[0][8]

    if mission_type_hun == '':
        msg = "Ad-hoc segregated airspace mission type could be faulty! Please verify. See inputted rows: {}".format(rows_to_process)
        logging.warning(msg)
        # print(msg)
        # warnings.warn(msg)
    
    return mission_type_hun

def get_mission_type_eng(rows_to_process):

    try:
        mission_type_eng = rows_to_process[1][8]
    except IndexError:
        return None

    if mission_type_eng == '':
        msg = "Ad-hoc segregated airspace mission type could be faulty! Please verify. See inputted rows: {}".format(rows_to_process)
        logging.warning(msg)
        # print(msg)
        # warnings.warn(msg)
    
    mission_type_eng = mission_type_eng.strip('()')

    return mission_type_eng

def get_matias_or_lara_id(rows_to_process):

    
    cells = [str(row[13]) for row in rows_to_process if row[13] != '']

    return ','.join(cells)

def get_excel_file_name(file_path):

    splitted_path = file_path.split('\\')

    return splitted_path[-1]

def excel_file_name_to_date(file_name):

    a = re.search(r'([0-9][0-9][0-9][0-9]).([0-9][0-9]).([0-9][0-9]).', file_name)

    year    = int(a.group(1))
    month   = int(a.group(2))
    day     = int(a.group(3))
    
    return datetime.datetime(year, month, day)

# -----------------
# -----------------

def string_to_gps_coordinate(gps_coordinate_string):

    if gps_coordinate_string.endswith('N'):
        # Positive, 0...90 deg with padding zero
        n = gps_coordinate_string.strip('N')
        n = n[0] + n[1] + '.' + n[2:]
        return float(n)
        
    elif gps_coordinate_string.endswith('E'):
        # Positive, 0...180 deg with padding zeros
        e = gps_coordinate_string.strip('E')
        e = e[0] + e[1] + e[2] + '.' + e[3:]
        return float(e)

    elif gps_coordinate_string.endswith('S'):
        # Negative, -0...-90 deg with padding zero
        s = gps_coordinate_string.strip('S')
        s = s[0] + s[1] + '.' + s[2:]
        return float(s)

    elif gps_coordinate_string.endswith('W'):
        # Negative, -0...-180 deg with padding zeros
        w = gps_coordinate_string.strip('W')
        w = w[0] + w[1] + w[2] + '.' + w[3:]
        return float(w)
    
    else:
        msg = 'GPS coordinate conversion error! See inputted string: {}'.format(gps_coordinate_string)
        logging.warning(msg)
        # print(msg)
        # warnings.warn(msg)
        return None

# -----------------
# -----------------

def create_empty_output_file(file_path):
    with open(file_path, 'w', encoding='utf-8') as json_file:
        data = {}
        json.dump(data, json_file, indent=4, default=str)

def save_dict_to_json(input_dict, file_path):

    with open(file_path, 'r+', encoding='utf-8') as json_file:
        json.dump(input_dict, json_file, indent=4, default=str)

# -----------------
# -----------------

def get_files_of_interest(base_folder_path):

    files_of_interest = []
    
    for root, dirs, files in os.walk(base_folder_path, topdown=True):
        for f in files:
            if ('.xls' in f) and ('NLFT' in f):
                files_of_interest.append(os.path.join(root, f))

    return files_of_interest

# -----------------
# MAIN
# -----------------    

def main():
    
    processing_durations = []
    processed_content = {}

    print('/' * 50)
    print("Script started")

    print("Create empty output file here: {}".format(OUTPUT_FILE_PATH_PROCESSED_DATA))
    create_empty_output_file(OUTPUT_FILE_PATH_PROCESSED_DATA)
    
    print("Collecting .xls files to be processed in directory: {}".format(INPUT_FILES_DIR_PATH))
    files_to_process = (get_files_of_interest(INPUT_FILES_DIR_PATH))
    nr_of_all_files = len(files_to_process)

    print("{} number of files found".format(nr_of_all_files))
    print("Start processing them")
    print("-" * 50)

    for index, excel_file in enumerate(files_to_process, start=1):
        
        # - START TIMING -
        start = time.process_time()
        # ----------------
        
        list_of_airspaces_in_a_file = process_excel_file( excel_file, SHEET_OF_INTEREST)
        
        for airspace_item in list_of_airspaces_in_a_file:
             processed_content.update(airspace_item)

        # ---------------
        delta_t = time.process_time() - start
        # - STOP TIMING -

        processing_durations.append(delta_t)
        avg_processing_dur = sum(processing_durations) / len(processing_durations)
        remainig_files = nr_of_all_files - index
        est_remainig_time = remainig_files * avg_processing_dur

        msg = "[{:4}/{:4}] file processed in [{:7.4f}] sec. Estimated remaining time [{:8.6}] sec {}".format(index, nr_of_all_files, delta_t, est_remainig_time, excel_file) 
        print(msg)
        logging.info(msg)
    
    print("Saving output json file, this might take a while. See here: {}".format(OUTPUT_FILE_PATH_PROCESSED_DATA))
    save_dict_to_json(processed_content, OUTPUT_FILE_PATH_PROCESSED_DATA)
    print("Script finished!")


    # TODO: actual operation duration warning logging has to be switched off. Way too much of them.
    # TODO: I was here, continue... with the AMSL issue or with the missing getters and duration calc.
    # TODO: GPS coordinates can be tricky Check how to return them 
    # TODO: False return values may not be the best ones... None would be better in some cases.
    # TODO: Continue with a function which processes this complicated list and returns a great dict and saves a json file too
    # TODO: place names could be faulty, sometimes it is divided into 2 cells of 2 rows... but it seems only if additional info is added. 
        

if __name__ == "__main__":
    main()
