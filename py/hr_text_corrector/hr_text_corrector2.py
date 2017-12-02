# Imports
from nltk.corpus import words
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
    xlsx_file = xlsx_dir + xlsx_general_abbr
    general_abbr_dict_both_2 = abbr_dict(False, 2, xlsx_file)
    xlsx_file = xlsx_dir + xlsx_occupation_abbr
    occupation_abbr_dict_both_2 = abbr_dict(False, 2, xlsx_file)

    #
    words_lower = [word.lower() for word in words.words()]
    
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
                                                  general_abbr_dict_both_2,
                                                  occupation_abbr_dict_both_2, 
                                                  words_lower, text_data)
                    write_to_file(fl_wrtr, line_metadata, text_data)
                current_column = column
                text_data = []
                text_data.append(' ' + line_data + ' <NEWLINE>')
                
    text_data = correct_text_data(first_name_abbr_dict_both_2, general_abbr_dict_both_2,
                                  occupation_abbr_dict_both_2, words_lower, text_data)
    write_to_file(fl_wrtr, line_metadata, text_data)
    
#
def add_spaces(text_data):
    text_data = re.sub('\(', '( ', text_data)
    text_data = re.sub('\)', ' )', text_data)
    text_data = re.sub('-', ' - ', text_data)
    return text_data
 
#
def correct_line_continuation(text_data):
    match_list = re.findall('[a-z]- [a-z]', text_data)
    for match_str in match_list:
        replace_str = re.sub('- ', '', match_str)
        text_data = re.sub(match_str, replace_str, text_data)
    return text_data

#
def correct_missing_space(words_lower, text_data):
    match_list = re.findall('[A-Z][a-z]+[A-Z][a-z]+', text_data)
    for match_str in match_list:
        if match_str.lower() not in words_lower:
            match = re.search('[a-z][A-Z]', match_str)
            idx = match_str.index(match.group(0))
            replace_str_1 = match_str[:idx+1] 
            replace_str_2 = match_str[idx+1:]
            if replace_str_1 != 'La' and \
               replace_str_1 != 'Mac' and \
               replace_str_1 != 'Mc':
                replace_str = replace_str_1 + ' ' + replace_str_2
                text_data = re.sub(match_str, replace_str, text_data)
    return text_data

#
def correct_split_words(words_lower, text_data):
    itr = re.finditer(r' ', text_data)
    idxs = [idx.start() for idx in itr]
    idx_list = []
    for i in range(len(idxs)-2):
        text_str1 = text_data[idxs[i]+1:idxs[i+1]]
        text_str2 = text_data[idxs[i+1]+1:idxs[i+2]]
        if len(text_str1) >= 2 and len(text_str2) >= 2:
            match = re.search(r'[a-z]', text_str2[0])
            if match is not None:
                text_str = text_str1 + text_str2
                sub_match = re.search('[0-9]+', text_str)
                if sub_match is None and len(text_str) >= 5:
                    if text_str.lower() in words_lower:
                        idx_list.append(idxs[i+1])
    idx_list = sorted(idx_list, reverse=True)
    for i in range(len(idx_list)):
        text_data = text_data[:idx_list[i]] + text_data[idx_list[i]+1:]
    return text_data

#
def correct_spurious_punctuation(text_data):
    itr = re.finditer(r'\?', text_data)
    idxs = [idx.start() for idx in itr]
    for i in range(len(idxs)):
        idx = idxs[i]
        match1 = re.search(r'[0-9]', text_data[idx-1])
        match2 = re.search(r'[0-9]', text_data[idx+1])
        match3 = re.search(r'[A-Za-z]', text_data[idx-1])
        match4 = re.search(r'[A-Za-z]', text_data[idx+1])
        if match1 is not None or match2 is not None:
            text_data = text_data[:idx] + '7' + text_data[idx+1:]
        else:
            text_data = text_data[:idx] + 'P' + text_data[idx+1:]
    return text_data

#
def correct_spurious_spaces(text_data):
    text_data = re.sub('\( ', '(', text_data)
    text_data = re.sub(' \)', ')', text_data)
    text_data = re.sub('- ', '-', text_data)
    text_data = re.sub(' -', '-', text_data)
    text_data = re.sub('  ', ' ', text_data)
    match_strs = [ 'Tel [A-Za-z]+ [A-Za-z]+ [0-9]{4}' ]
    for match_str in match_strs:
        match = re.search(match_str, text_data)
        if match is not None:
            found_str = match.group(0)
            itr = re.finditer(r' ', found_str)
            idxs = [idx.start() for idx in itr]
            replace_str = found_str[:idxs[1]] + found_str[idxs[1]+1:]
            text_data = re.sub(found_str, replace_str, text_data)
    return text_data
    
#
def correct_text_data(first_name_abbr_dict, general_abbr_dict, occupation_abbr_dict, 
                      words_lower, text_data):
    text_data = ''.join(text_data)
    text_data = correct_line_continuation(text_data)
    text_data = remove_spurious_marks(text_data)
    text_data = correct_spurious_spaces(text_data)
    text_data = add_spaces(text_data)
    text_data = correct_spurious_punctuation(text_data)
    text_data = correct_missing_space(words_lower, text_data)
    text_data = dict_correction(first_name_abbr_dict, text_data)
    text_data = dict_correction(general_abbr_dict, text_data)
    text_data = dict_correction(occupation_abbr_dict, text_data)
    text_data = correct_split_words(words_lower, text_data)
    text_data = remove_spaces(text_data)
    return text_data

#
def remove_spaces(text_data):
    text_data = re.sub('\( ', '(', text_data)
    text_data = re.sub(' \)', ')', text_data)
    text_data = re.sub(' - ', '-', text_data)
    return text_data

#
def remove_spurious_marks(text_data):
    text_data = re.sub(' - ', ' ', text_data)
    text_data = re.sub(' , ', ' ', text_data)
    text_data = re.sub(' \. ', ' ', text_data)
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