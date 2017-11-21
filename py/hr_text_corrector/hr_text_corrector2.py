# Imports
import re
import sys
from xlrd import open_workbook

# Local Imports
sys.path.insert(0, 'py/hr_tools')
from file_writer import file_writer

#
def hr_text_corrector2(sect_dir, pdf_name, xlsx_dir, xlsx_first_name_abbr, xlsx_general_abbr, xlsx_occupation_abbr):
    
    #
    directory_dir = sect_dir
    
    #
    directory_txt_dir = directory_dir + 'txt/'
    directory_txt_infile = directory_txt_dir + pdf_name[:len(pdf_name)-4] + '2.txt'
    directory_txt_outfile = directory_txt_dir + pdf_name[:len(pdf_name)-4] + '3.txt'
    
    #
    xlsx_file = xlsx_dir + xlsx_first_name_abbr
    first_name_abbr_dict_both_2 = get_abbr_dict(False, 2, xlsx_file)
    first_name_abbr_dict_upper_2 = get_abbr_dict(True, 2, xlsx_file)
    xlsx_file = xlsx_dir + xlsx_general_abbr
    general_abbr_dict_both_2 = get_abbr_dict(False, 2, xlsx_file)
    general_abbr_dict_upper_1 = get_abbr_dict(True, 1, xlsx_file)
    general_abbr_dict_upper_2 = get_abbr_dict(True, 2, xlsx_file)
    xlsx_file = xlsx_dir + xlsx_occupation_abbr
    occupation_abbr_dict_both_2 = get_abbr_dict(False, 2, xlsx_file)
    occupation_abbr_dict_upper_2 = get_abbr_dict(True, 2, xlsx_file)
    
    #
    fl_wrtr = file_writer(directory_txt_outfile)
    
    #
    current_column = 0
    with open(directory_txt_infile, 'r') as f:
        for line in f:
            
            #
            itr = re.finditer(r'\t', line)
            idxs = [idx.start() for idx in itr]
            line_metadata = line[:idxs[4]].upper()
            line_data = line[idxs[4]+1:idxs[5]]
            business_address = line[idxs[5]+1:idxs[6]]
            residence_type = line[idxs[6]+1:idxs[7]].upper()
            residential_address = line[idxs[7]+1:idxs[8]]
            telephone_number = line[idxs[8]+1:].upper()

            #
            line_data = correct_line_data(first_name_abbr_dict_both_2, general_abbr_dict_both_2, 
                                          occupation_abbr_dict_both_2, line_data)
            business_address = correct_address(general_abbr_dict_both_2, business_address)
            residential_address = correct_address(general_abbr_dict_both_2, residential_address)
            
            #
            line_data = line_data.upper()
            business_address = business_address.upper()
            residential_address = residential_address.upper()
            
            #
            line_data = correct_line_data(first_name_abbr_dict_upper_2, general_abbr_dict_upper_2, 
                                          occupation_abbr_dict_upper_2, line_data)
            business_address = correct_address(general_abbr_dict_upper_1, business_address)
            residential_address = correct_address(general_abbr_dict_upper_1, residential_address)
                   
            #
            entry = line_metadata + '\t' + line_data + '\t' + business_address + '\t' + \
                    residence_type + '\t' + residential_address + '\t' + telephone_number + '\n'
            entries = [ entry ]           
            fl_wrtr.run(entries)
            
#
def correct_address(general_abbr_dict, address):
    address = ' ' + address + ' '
    address = dictionary_correction(general_abbr_dict, address)
    address = address[1:len(address)]
    return address
            
#
def correct_line_data(first_name_abbr_dict, general_abbr_dict, occupation_abbr_dict, line_data):
    line_data = dictionary_correction(first_name_abbr_dict, line_data)
    line_data = dictionary_correction(general_abbr_dict, line_data)
    line_data = dictionary_correction(occupation_abbr_dict, line_data)
    return line_data

#
def dictionary_correction(dictionary, text_str):
    for key in dictionary.keys():
        match = re.search(key, text_str)
        if match is not None:
            text_str = re.sub(key, dictionary[key], text_str)
    return text_str
            
#
def get_abbr_dict(upper_flg, min_abbr_len, xlsx_file):
    book = open_workbook(xlsx_file)
    sheet = book.sheets()[0]
    xlsx_dict = {}
    for i in range(sheet.nrows):
        rowvals = sheet.row(i)
        rowval = []
        for j in range(len(rowvals)):
            rowval_tmp = rowvals[j].value
            if upper_flg:
                rowval.append(rowval_tmp.upper())
            else:
                rowval.append(rowval_tmp)
        if len(rowval[0]) >= min_abbr_len:
            row_val_tmp = []
            for k in range(4):
                if k == 0:
                    rowval_tmp = rowval
                elif k == 1:
                    rowval_tmp[0] = '\(' + rowval[0]
                    rowval_tmp[1] = '(' + rowval[1]
                elif k == 2:
                    rowval_tmp[0] = rowval[0] + '\('
                    rowval_tmp[1] = rowval[1] +'('
                elif k == 3:
                    rowval_tmp[0] = '\(' + rowval[0] + '\('
                    rowval_tmp[1] = '(' + rowval[1] +'('    
                xlsx_dict[' ' + rowval_tmp[0] + ' '] = ' ' + rowval_tmp[1] + ' '
                xlsx_dict[' ' + rowval_tmp[0] + '-'] = ' ' + rowval_tmp[1] + '-'
                xlsx_dict['-' + rowval_tmp[0] + '-'] = '-' + rowval_tmp[1] + '-'
                xlsx_dict['-' + rowval_tmp[0] + ' '] = '-' + rowval_tmp[1] + ' '
    return xlsx_dict