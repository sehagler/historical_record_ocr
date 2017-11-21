# Imports
import re
import sys

# Local Imports
sys.path.insert(0, 'py/hr_tools')
from file_writer import file_writer

#
def hr_text_corrector1(sect_dir, pdf_name):
    
    #
    directory_dir = sect_dir
    
    #
    directory_txt_dir = directory_dir + 'txt/'
    directory_txt_infile = directory_txt_dir + pdf_name[:len(pdf_name)-4] + '0.txt'
    directory_txt_outfile = directory_txt_dir + pdf_name[:len(pdf_name)-4] + '1.txt'
    
    #
    fl_wrtr = file_writer(directory_txt_outfile)
    
    #
    current_column = 0
    with open(directory_txt_infile, 'r') as f:
        for line in f:
            
            #
            itr = re.finditer(r'\t', line)
            idxs = [idx.start() for idx in itr]
            idx = idxs[-1]
            line_metadata = line[:idx]
            line_data = line[idx+1:len(line)-1]
            
            #           
            column = line_metadata[-1]
            if column != current_column:
                current_surname = []
                current_column = column
            
            #
            line_data = correct_ditto(line_data)
            line_data = correct_h_r_address(line_data)
            line_data = correct_parentheses(line_data)
            line_data = correct_missing_space(line_data)
            line_data = correct_line_continuation(line_data)
            line_data, current_surname = resolve_dittos(line_data, current_surname)
            
            #
            entry = line_metadata + '\t' + line_data + '\n'
            print(entry)
            entries = [ entry ]          
            fl_wrtr.run(entries)
            
#
def correct_ditto(line_data):
    try:
        idx = line_data.index(' ')
        test_str = line_data[:idx]
        if len(test_str) == 1:
            match = re.search('[A-Za-z]', test_str)
            if match is None:
                line_data = '" ' + line_data[idx+1:]
        elif len(test_str) == 2:
            match = re.search('[A-Za-z][A-Za-z]', test_str)
            if match is None:
                line_data = '" ' + line_data[idx+1:]
    except:
        pass
    return line_data
            
#
def correct_h_r_address(line_data):
    match_strs = [ ' h [0-9]', ' r [0-9]' ]
    for match_str in match_strs:
        match = re.search(match_str, line_data)
        if match is not None:
            replace_str = match.group(0)
            replace_str = replace_str[:2] + replace_str[3:]
            line_data = re.sub(match_str, replace_str, line_data)
    return line_data

#
def correct_line_continuation(line_data):
    line_data = re.sub('- ', '', line_data)
    return line_data

#
def correct_missing_space(line_data):
    match_list = re.findall('[A-Z][a-z]+[A-Z][a-z]+', line_data)
    for match_str in match_list:
        match = re.search('[a-z][A-Z]', match_str)
        idx = match_str.index(match.group(0))
        replace_str_1 = match_str[:idx+1] 
        replace_str_2 = match_str[idx+1:]
        if replace_str_1 != 'Mac' and \
           replace_str_1 != 'Mc':
            replace_str = replace_str_1 + ' ' + replace_str_2
            line_data = re.sub(match_str, replace_str, line_data)
    return line_data

#
def correct_parentheses(line_data):
    line_data = re.sub('\( ', '(', line_data)
    line_data = re.sub(' \)', ')', line_data)
    return line_data

#
def resolve_dittos(line_data, current_surname):
    if line_data[0] != '"':
        try:
            idx = line_data.index(' ')
            current_surname = line_data[:idx]
        except:
            current_surname = line_data
    elif line_data[0] == '"' and len(current_surname) > 0:
        line_data = current_surname + line_data[1:]
        line_data = ''.join(line_data)
    return line_data, current_surname