import xlrd
import json
import os
import warnings


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
        create_single_airspace_dict(item)
        for row in item:
            print (row)
        print('----')
        

# TODO: Continue with a function which processes this complicated list and returns a great dict and saves a json file too


def create_single_airspace_dict(rows_to_process):

    

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
        "file_id"                  : "NA", 
        "date"                     : "NA",
        "serial_number"            : get_sa_serial_number(rows_to_process),
        "boundary_coord_poly"      : get_boundary_coord_poly(rows_to_process),
        "boundary_coord_circle"    : get_boundary_coord_circle(rows_to_process),
        "boundary_alt_l"           : get_boundary_alt_l(rows_to_process),
        "boundary_alt_h"           : get_boundary_alt_h(rows_to_process),
        "op_time_planned"          : "NA",
        "op_time_actual"           : "NA",
        "applicant_name"           : get_applicant_name(rows_to_process),
        "applicant_phone"          : get_applicant_phone(rows_to_process),
        "mission_type_hun"         : get_mission_type_hun(rows_to_process),
        "mission_type_eng"         : get_mission_type_eng(rows_to_process),
        "matias_or_lara_id"        : get_matias_or_lara_id(rows_to_process),
    }

    print(get_sa_serial_number(rows_to_process))
    print(get_boundary_coord_poly(rows_to_process))
    print(get_boundary_coord_circle(rows_to_process))
    print(get_boundary_alt_l(rows_to_process))
    print(get_boundary_alt_h(rows_to_process))
    #
    #
    print(get_applicant_name(rows_to_process))
    print(get_applicant_phone(rows_to_process))
    print(get_mission_type_hun(rows_to_process))
    print(get_mission_type_eng(rows_to_process))
    print(get_matias_or_lara_id(rows_to_process))

def get_sa_serial_number(rows_to_process):
    
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
        
        return [row[1] for row in rows_to_process if row[1] != '']
    else:
        return False

def get_boundary_coord_poly(rows_to_process):

    if 'r' not in rows_to_process[1][1] and '=' not in rows_to_process[1][1]:
        
        return [row[1] for row in rows_to_process if row[1] != '']
    else:
        return False

def get_boundary_alt_l(rows_to_process):
    
    usual_lower_altitude = 'GND'

    if rows_to_process[0][3] != usual_lower_altitude:
        print("Ad-hoc segregated airspace lower boundary altitude is other than {}! Please verify. See inputted rows: {}".format(usual_lower_altitude, rows_to_process))
        warnings.warn("Ad-hoc segregated airspace lower boundary altitude is other than {}! Please verify. See inputted rows: {}".format(usual_lower_altitude, rows_to_process))
    
    return rows_to_process[0][3]

def get_boundary_alt_h(rows_to_process):

    # TODO: AMSL's missing, make sure to concatenate altitude cells with them

    if rows_to_process[0][4] == '':
        print("Ad-hoc segregated airspace higher boundary altitude could be faulty! Please verify. See inputted rows: {}".format(rows_to_process))
        warnings.warn("Ad-hoc segregated airspace higher boundary altitude could be faulty! {}! Please verify. See inputted rows: {}".format(rows_to_process))
    
    return rows_to_process[0][4]

# TODO: ***
# TODO: Implement missing getters here!
# TODO: ***

def get_applicant_name(rows_to_process):

    if rows_to_process[0][7] == '':
        print("Ad-hoc segregated airspace applicant name could be faulty! Please verify. See inputted rows: {}".format(rows_to_process))
        warnings.warn("Ad-hoc segregated airspace applicant name could be faulty! {}! Please verify. See inputted rows: {}".format(rows_to_process))
    
    return rows_to_process[0][7]
    
def get_applicant_phone(rows_to_process):

    if rows_to_process[1][7] == '':
        print("Ad-hoc segregated airspace applicant phone number could be faulty! Please verify. See inputted rows: {}".format(rows_to_process))
        warnings.warn("Ad-hoc segregated airspace applicant phone number could be faulty! {}! Please verify. See inputted rows: {}".format(rows_to_process))
    
    return rows_to_process[1][7]

def get_applicant_phone(rows_to_process):

    if rows_to_process[1][7] == '':
        print("Ad-hoc segregated airspace applicant phone number could be faulty! Please verify. See inputted rows: {}".format(rows_to_process))
        warnings.warn("Ad-hoc segregated airspace applicant phone number could be faulty! {}! Please verify. See inputted rows: {}".format(rows_to_process))
    
    return rows_to_process[1][7]

def get_mission_type_hun(rows_to_process):

    if rows_to_process[0][8] == '':
        print("Ad-hoc segregated airspace mission type could be faulty! Please verify. See inputted rows: {}".format(rows_to_process))
        warnings.warn("Ad-hoc segregated airspace mission type could be faulty! {}! Please verify. See inputted rows: {}".format(rows_to_process))
    
    return rows_to_process[0][8]

def get_mission_type_eng(rows_to_process):

    if rows_to_process[1][8] == '':
        print("Ad-hoc segregated airspace mission type could be faulty! Please verify. See inputted rows: {}".format(rows_to_process))
        warnings.warn("Ad-hoc segregated airspace mission type could be faulty! {}! Please verify. See inputted rows: {}".format(rows_to_process))
    
    return rows_to_process[1][8]

def get_matias_or_lara_id(rows_to_process):

    return [row[13] for row in rows_to_process if row[13] != '']


            









            

        

        


print("----")
process_excel_file(TEST_EXCEL_FILE, SHEET_OF_INTEREST)


