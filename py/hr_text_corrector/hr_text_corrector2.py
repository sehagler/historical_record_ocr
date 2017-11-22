# Imports
import re
import sys

# Local Imports
sys.path.insert(0, 'py/hr_tools')
from abbr_dict import abbr_dict, dict_correction
from file_writer import file_writer

#
def hr_text_corrector2(sect_dir, file_idx, pdf_name, xlsx_dir, xlsx_first_name_abbr,
                       xlsx_general_abbr, xlsx_occupation_abbr):
    
    #
    directory_dir = sect_dir
    
    #
    directory_txt_dir = directory_dir + 'txt/'
    directory_txt_infile = directory_txt_dir + pdf_name[:len(pdf_name)-4] + \
                           str(file_idx) + '.txt'
    directory_txt_outfile = directory_txt_dir + pdf_name[:len(pdf_name)-4] + \
                            str(file_idx+1) + '.txt'
    
    #
    xlsx_file = xlsx_dir + xlsx_first_name_abbr
    first_name_abbr_dict_both_2 = abbr_dict(False, 2, xlsx_file)
    first_name_abbr_dict_upper_2 = abbr_dict(True, 2, xlsx_file)
    xlsx_file = xlsx_dir + xlsx_general_abbr
    general_abbr_dict_both_2 = abbr_dict(False, 2, xlsx_file)
    general_abbr_dict_upper_2 = abbr_dict(True, 2, xlsx_file)
    xlsx_file = xlsx_dir + xlsx_occupation_abbr
    occupation_abbr_dict_both_2 = abbr_dict(False, 2, xlsx_file)
    occupation_abbr_dict_upper_2 = abbr_dict(True, 2, xlsx_file)
    
    #
    fl_wrtr = file_writer(directory_txt_outfile)
    
    #
    current_column = 0
    text_data = []
    line_ctr = 0
    with open(directory_txt_infile, 'r') as f:
        for line in f:
            
            line_ctr += 1
            
            #
            itr = re.finditer(r'\t', line)
            idxs = [idx.start() for idx in itr]
            idx = idxs[-1]
            column = line[idxs[-2]+1:idxs[-1]]
            line_data = line[idx+1:len(line)-1]
            
            if column == current_column:
                line_metadata = line[:idxs[-1]]
                text_data.append(' ' + line_data + ' <NEWLINE>')
            else:
                if len(text_data) > 0:
                    text_data = correct_text_data(first_name_abbr_dict_both_2,
                                                  first_name_abbr_dict_upper_2,
                                                  general_abbr_dict_both_2, 
                                                  general_abbr_dict_upper_2,
                                                  occupation_abbr_dict_both_2,
                                                  occupation_abbr_dict_upper_2, text_data)
                    write_to_file(fl_wrtr, line_metadata, text_data)
                current_column = column
                text_data = []
                text_data.append(' ' + line_data + ' <NEWLINE>')
                
    text_data = correct_text_data(first_name_abbr_dict_both_2, first_name_abbr_dict_upper_2,
                                  general_abbr_dict_both_2, general_abbr_dict_upper_2,
                                  occupation_abbr_dict_both_2, occupation_abbr_dict_upper_2,
                                  text_data)
    write_to_file(fl_wrtr, line_metadata, text_data)
    
#
def add_spaces(text_data):
    text_data = re.sub('\(', '( ', text_data)
    text_data = re.sub('\)', ' )', text_data)
    text_data = re.sub('-', ' - ', text_data)
    return text_data
 
#
def correct_line_continuation(text_data):
    text_data = re.sub('- ', '', text_data)
    return text_data

#
def correct_missing_space(text_data):
    match_list = re.findall('[A-Z][a-z]+[A-Z][a-z]+', text_data)
    for match_str in match_list:
        match = re.search('[a-z][A-Z]', match_str)
        idx = match_str.index(match.group(0))
        replace_str_1 = match_str[:idx+1] 
        replace_str_2 = match_str[idx+1:]
        if replace_str_1 != 'Mac' and \
           replace_str_1 != 'Mc':
            replace_str = replace_str_1 + ' ' + replace_str_2
            text_data = re.sub(match_str, replace_str, text_data)
    return text_data

#
def correct_parentheses(text_data):
    text_data = re.sub('\( ', '(', text_data)
    text_data = re.sub(' \)', ')', text_data)
    return text_data
    
#
def correct_text_data(first_name_abbr_dict_both_2, first_name_abbr_dict_upper_2,
                                  general_abbr_dict_both_2, general_abbr_dict_upper_2,
                                  occupation_abbr_dict_both_2, occupation_abbr_dict_upper_2,
                                  text_data):
    text_data = ''.join(text_data)
    text_data = correct_line_continuation(text_data)
    text_data = correct_missing_space(text_data)
    text_data = add_spaces(text_data)
    text_data = dict_correction(first_name_abbr_dict_both_2, text_data)
    text_data = dict_correction(general_abbr_dict_both_2, text_data)
    text_data = dict_correction(occupation_abbr_dict_both_2, text_data)
    text_data = remove_spaces(text_data)
    text_data = correct_parentheses(text_data)
    return text_data

#
def remove_spaces(text_data):
    text_data = re.sub('\( ', '(', text_data)
    text_data = re.sub(' \)', ')', text_data)
    text_data = re.sub(' - ', '-', text_data)
    return text_data

#
def write_to_file(fl_wrtr, line_metadata, text_data):
    text_data = text_data[1:len(text_data)-10]
    itr = re.finditer(r' <NEWLINE> ', text_data)
    idxs = [idx.start() for idx in itr]
    idxs = idxs + [0]
    idxs = idxs + [len(text_data)]
    idxs = sorted(idxs)
    text_data_out = []
    for i in range(len(idxs)-1):
        if i == 0:
            text_data_out.append(line_metadata + '\t' + text_data[idxs[i]:idxs[i+1]] + '\n')
        else:
            text_data_out.append(line_metadata + '\t' + text_data[idxs[i]+11:idxs[i+1]] + '\n')
    fl_wrtr.run(text_data_out)