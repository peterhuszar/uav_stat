import xlrd
import json
import os
import warnings
from datetime import time
from datetime import date
import re


TEST_EXCEL_FILE = r'D:\python_scripts\uav_stat\input_files\NLFT 2019.05.01..xls'
SHEET_OF_INTEREST = 3


def process_excel_file(excel_file_path, excel_sheet_number):
    # Function to process a single Excel log file.

    workbook                = xlrd.open_workbook(excel_file_path)
    sheet                   = workbook.sheet_by_index(excel_sheet_number) 

    all_airspace_args = []
    single_airspace_args = []
    current_serial_number = None
    previous_serial_number = None

    data_of_interest_reached = False
    serial_number_reached    = False

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
        create_single_airspace_dict(item, excel_file_name)
        for row in item:
            print (row)
        print('----')
        

# TODO: Continue with a function which processes this complicated list and returns a great dict and saves a json file too


def create_single_airspace_dict(rows_to_process, origin_of_rows):

    

    """
    single_airspace_dict = {
        "file_id"                  :    , 
        "date"                     :    ,
        "serial_number"            :    ,
        "bound_coordinates_poly"   :    ,
        "bound_coordinates_circle" :    ,
        "bound_alt_l"              :    ,
        "bound_alt_h"              :    ,
        "op_time_planned"          :    ,
        "op_time_actual"           :    ,
        "applicant_name"           :    ,
        "applicant_phone"          :    ,
        "mission_type"             :    ,
        "matias_or_lara_id"        :    ,
    }

    """

    single_airspace_dict = {
        "file_id"                  : origin_of_rows, 
        "date"                     : excel_file_name_to_date(origin_of_rows),
        "serial_number"            : get_sa_serial_number(rows_to_process),
        "boundary_coord_poly"      : get_boundary_coord_poly(rows_to_process),
        "boundary_coord_circle"    : get_boundary_coord_circle(rows_to_process),
        "place_name"               : get_place_name(rows_to_process),
        "boundary_alt_l"           : get_boundary_alt_l(rows_to_process),
        "boundary_alt_h"           : get_boundary_alt_h(rows_to_process),
        "op_time_plan_start"       : get_op_time_plan_start(rows_to_process),
        "op_time_plan_end"         : get_op_time_plan_end(rows_to_process),
        "op_duration_plan"         : "NA",
        "op_time_act_start"        : get_op_time_act_start(rows_to_process),
        "op_time_act_end"          : get_op_time_act_end(rows_to_process),
        "op_duration_act"          : "NA",
        "applicant_name"           : get_applicant_name(rows_to_process),
        "applicant_phone"          : get_applicant_phone(rows_to_process),
        "mission_type_hun"         : get_mission_type_hun(rows_to_process),
        "mission_type_eng"         : get_mission_type_eng(rows_to_process),
        "matias_or_lara_id"        : get_matias_or_lara_id(rows_to_process),
    }

    print(origin_of_rows)
    print(excel_file_name_to_date(origin_of_rows))
    print(get_sa_serial_number(rows_to_process))
    print(get_boundary_coord_poly(rows_to_process))
    print(get_boundary_coord_circle(rows_to_process))
    print(get_place_name(rows_to_process))
    print(get_boundary_alt_l(rows_to_process))
    print(get_boundary_alt_h(rows_to_process))
    print(get_op_time_plan_start(rows_to_process))
    print(get_op_time_plan_end(rows_to_process))
    print(get_op_time_act_start(rows_to_process))
    print(get_op_time_act_end(rows_to_process))
    #
    print(get_applicant_name(rows_to_process))
    print(get_applicant_phone(rows_to_process))
    print(get_mission_type_hun(rows_to_process))
    print(get_mission_type_eng(rows_to_process))
    print(get_matias_or_lara_id(rows_to_process))

def get_sa_serial_number(rows_to_process):

    sa_serial_number = rows_to_process[0][0]
    
    try:
        return int(float(rows_to_process[0][0]))
    except ValueError:
        print('Ad-hoc segregated airspace serial number processing error! See inputted rows: {}'.format(rows_to_process))
        warnings.warn('Ad-hoc segregated airspace serial number processing error! See inputted rows: {}'.format(rows_to_process))

def get_boundary_coord_circle(rows_to_process):

    if (('N' in rows_to_process[0][1]) and 
            ('E' in rows_to_process[0][1]) and
            ('r' in rows_to_process[1][1]) and
            ('=' in rows_to_process[1][1])):
        
        raw_cell_content = [row[1] for row in rows_to_process if (row[1] != '' and '(' not in row[1] and ')' not in row[1])]
        
        raw_radius = raw_cell_content[1]

        # TODO: regex pattern could be fixed to matcth the unit except white spaces. Now I am stripping it when returning.
        r = re.search('([0-9]+)(.*)', raw_radius)
        radius = r.group(1)
        unit = r.group(2)

        return [raw_cell_content[0], float(radius), unit.strip()]

    else:
        return False

def get_boundary_coord_poly(rows_to_process):

    if 'r' not in rows_to_process[1][1] and '=' not in rows_to_process[1][1]:
        
        return [row[1] for row in rows_to_process if (row[1] != '' and '(' not in row[1] and ')' not in row[1])]
    else:
        return False

def get_place_name(rows_to_process):

    second_col = [row[1] for row in rows_to_process if row[1] != '']
    place_name = second_col[-1]
    place_name = place_name.strip('()')

    return place_name

def get_boundary_alt_l(rows_to_process):
    
    usual_lower_altitude = 'GND'

    if rows_to_process[0][3] != usual_lower_altitude:
        print("Ad-hoc segregated airspace lower boundary altitude is other than {}! Please verify. See inputted rows: {}".format(usual_lower_altitude, rows_to_process))
        warnings.warn("Ad-hoc segregated airspace lower boundary altitude is other than {}! Please verify. See inputted rows: {}".format(usual_lower_altitude, rows_to_process))
    
    return rows_to_process[0][3]

def get_boundary_alt_h(rows_to_process):

    boundary_alt_h = rows_to_process[0][4]
    reference = rows_to_process[1][4]

    if boundary_alt_h == '':
        print("Ad-hoc segregated airspace higher boundary altitude could be faulty! Please verify. See inputted rows: {}".format(rows_to_process))
        warnings.warn("Ad-hoc segregated airspace higher boundary altitude could be faulty! {}! Please verify. See inputted rows: {}".format(boundary_alt_h, rows_to_process))

    boundary_alt_h = boundary_alt_h.split(' ')
    boundary_alt_h.append(reference)

    try:
        boundary_alt_h[0] = float(boundary_alt_h[0])
    except ValueError:
        warnings.warn("Ad-hoc segregated airspace higher boundary altitude could be faulty! {}! Please verify. See inputted rows: {}".format(boundary_alt_h, rows_to_process))
    
    return boundary_alt_h


# TODO: ***
# TODO: Implement missing getters here!
# TODO: ***
# TODO: False return values may not be the best ones... None would be better in some cases.

def get_op_time_plan_start(rows_to_process):

    try:
        op_time_plan_start = xlrd.xldate_as_tuple(rows_to_process[0][5], 0)
    except TypeError:
        return False

    op_time_plan_start = time(op_time_plan_start[3], op_time_plan_start[4], op_time_plan_start[5])

    return op_time_plan_start

def get_op_time_plan_end(rows_to_process):

    try:
        op_time_plan_end = xlrd.xldate_as_tuple(rows_to_process[0][6], 0)
    except  TypeError:
        return False

    op_time_plan_end = time(op_time_plan_end[3], op_time_plan_end[4], op_time_plan_end[5])

    return op_time_plan_end

def get_op_time_act_start(rows_to_process):

    op_time_act_start_0 = rows_to_process[0][9]
    op_time_act_start_1 = rows_to_process[1][9]

    if op_time_act_start_0 != '':
        try:
            op_time_act_start = xlrd.xldate_as_tuple(op_time_act_start_0, 0)
        except TypeError:
            return False
    
    elif op_time_act_start_1 != '':
        try:
            op_time_act_start = xlrd.xldate_as_tuple(op_time_act_start_1, 0)
        except TypeError:
            return False
    
    else:
        return False

    op_time_act_start = time(op_time_act_start[3], op_time_act_start[4], op_time_act_start[5])

    return op_time_act_start

def get_op_time_act_end(rows_to_process):

    op_time_act_end_0 = rows_to_process[0][10]
    op_time_act_end_1 = rows_to_process[1][10]

    if op_time_act_end_0 != '':
        try:
            op_time_act_end = xlrd.xldate_as_tuple(op_time_act_end_0, 0)
        except TypeError:
            return False

    elif op_time_act_end_1 != '':
        try:
            op_time_act_end = xlrd.xldate_as_tuple(op_time_act_end_1, 0)
        except TypeError:
            return False

    else:
        return False

    op_time_act_end = time(op_time_act_end[3], op_time_act_end[4], op_time_act_end[5])
    
    return op_time_act_end

def get_applicant_name(rows_to_process):

    applicant_name = rows_to_process[0][7]

    if applicant_name == '':
        print("Ad-hoc segregated airspace applicant name could be faulty! Please verify. See inputted rows: {}".format(rows_to_process))
        warnings.warn("Ad-hoc segregated airspace applicant name could be faulty! {}! Please verify. See inputted rows: {}".format(applicant_name, rows_to_process))
    
    return applicant_name
    
def get_applicant_phone(rows_to_process):

    applicant_phone = rows_to_process[1][7]

    if applicant_phone == '':
        print("Ad-hoc segregated airspace applicant phone number could be faulty! Please verify. See inputted rows: {}".format(rows_to_process))
        warnings.warn("Ad-hoc segregated airspace applicant phone number could be faulty! {}! Please verify. See inputted rows: {}".format(applicant_phone, rows_to_process))
    
    applicant_phone = applicant_phone.replace('/', '')

    return applicant_phone

def get_mission_type_hun(rows_to_process):

    mission_type_hun = rows_to_process[0][8]

    if mission_type_hun == '':
        print("Ad-hoc segregated airspace mission type could be faulty! Please verify. See inputted rows: {}".format(rows_to_process))
        warnings.warn("Ad-hoc segregated airspace mission type could be faulty! {}! Please verify. See inputted rows: {}".format(mission_type_hun, rows_to_process))
    
    return mission_type_hun

def get_mission_type_eng(rows_to_process):

    mission_type_eng = rows_to_process[1][8]

    if mission_type_eng == '':
        print("Ad-hoc segregated airspace mission type could be faulty! Please verify. See inputted rows: {}".format(rows_to_process))
        warnings.warn("Ad-hoc segregated airspace mission type could be faulty! {}! Please verify. See inputted rows: {}".format(mission_type_eng, rows_to_process))
    
    mission_type_eng = mission_type_eng.strip('()')

    return mission_type_eng

def get_matias_or_lara_id(rows_to_process):

    
    cells = [row[13] for row in rows_to_process if row[13] != '']

    return ','.join(cells)

def get_excel_file_name(file_path):

    splitted_path = file_path.split('\\')

    return splitted_path[-1]

def excel_file_name_to_date(file_name):

    a = re.search(r'([0-9][0-9][0-9][0-9]).([0-9][0-9]).([0-9][0-9]).', file_name)

    year    = int(a.group(1))
    month   = int(a.group(2))
    day     = int(a.group(3))
    
    return date(year, month, day)

# TODO: I was here, continue... with the AMSL issue or with the missing getters and duration calc.

        


print("----")
process_excel_file(TEST_EXCEL_FILE, SHEET_OF_INTEREST)


