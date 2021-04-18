import xlrd
import json
import os


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
            
            if first_item_in_row != '':
                all_airspace_args.append(single_airspace_args)
                single_airspace_args = []
                
            single_airspace_args.append(row_content)

    for item in all_airspace_args:
        print(item,'\r')
        

            
            

        

        


print("----")
process_excel_file(TEST_EXCEL_FILE, SHEET_OF_INTEREST)


