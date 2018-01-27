# Imports
from nltk.corpus import words
import numpy as np
import re
import sys

# Local Imports
sys.path.insert(0, 'py/hr_tools')
from abbr_dict import dict_correction
from file_writer import file_writer

#
def hr_text_corrector1(columns_per_iteration, sect_dir, file_idx, pdf_name, 
                       generic_business_list_dict_both_2, hyphenated_generic_occupation_dict_both_2,
                       internal_ref_abbr_list_dict_both_2, unhyphenated_generic_occupation_dict_both_2, 
                       occupation_key_list):
    
    #
    directory_dir = sect_dir
    
    #
    directory_txt_dir = directory_dir + 'txt/'
    directory_txt_infile = directory_txt_dir + pdf_name[:len(pdf_name)-4] + \
                           str(file_idx) + '.txt'
    directory_txt_outfile = directory_txt_dir + pdf_name[:len(pdf_name)-4] + \
                            str(file_idx+1) + '.txt'

    #
    words_lower = [word.lower() for word in words.words()]
    
    #
    fl_wrtr = file_writer(directory_txt_outfile)
    
    #     
    global_excluded_surnames_list = []
    with open(directory_txt_infile, 'r') as f:
        
        #
        column_ctr = 1
        current_column = 1
        metadata = []
        text_data = []
        
        #
        for line in f:
            
            #
            itr = re.finditer(r'\t', line)
            idxs = [idx.start() for idx in itr]
            idx = idxs[-1]
            column = int(line[idxs[-2]+1:idxs[-1]])
            line_metadata = line[:idxs[-1]]
            line_data = line[idx+1:len(line)-1]
            
            #
            if column != current_column:
                current_column = column
                column_ctr += 1
            
            #
            if column_ctr > columns_per_iteration:
                
                #
                if len(text_data) > 0:
                    excluded_surnames_list = get_excluded_surnames_list(text_data)
                    global_excluded_surnames_list.extend(excluded_surnames_list)
                    entries = parse_column(excluded_surnames_list, words_lower,
                                           text_data, metadata, fl_wrtr)
                    metadata = []
                    text_data = []
                    for entry in entries:
                        #
                        itr = re.finditer(r'\t', entry)
                        idxs = [idx.start() for idx in itr]
                        idx = idxs[-1]
                        entry_metadata = entry[:idxs[-1]]
                        entry_data = entry[idx+1:len(entry)-1]
                        metadata.append(entry_metadata)
                        if entry_data[-1] == '-' or \
                           entry_data[-1] == '(':
                            entry_data = ' ' + entry_data + '  <NEWLINE>'
                        else:
                            entry_data = ' ' + entry_data + ' <NEWLINE>'
                        text_data.append(entry_data)
                    text_data = correct_text_data(generic_business_list_dict_both_2,
                                                  hyphenated_generic_occupation_dict_both_2,
                                                  internal_ref_abbr_list_dict_both_2,
                                                  unhyphenated_generic_occupation_dict_both_2,
                                                  words_lower, occupation_key_list, text_data)
                    write_to_file(fl_wrtr, metadata, text_data)
                
                #
                column_ctr = 1
                metadata = []
                text_data = []
                
                #
                metadata.append(line_metadata)
                text_data.append(line_data)
                
            else:
                
                #
                metadata.append(line_metadata)
                text_data.append(line_data)
                
        #
        if len(text_data) > 0:
            excluded_surnames_list = get_excluded_surnames_list(text_data)
            global_excluded_surnames_list.extend(excluded_surnames_list)
            entries = parse_column(excluded_surnames_list, words_lower,
                                   text_data, metadata, fl_wrtr)
            metadata = []
            text_data = []
            for entry in entries:
                #
                itr = re.finditer(r'\t', entry)
                idxs = [idx.start() for idx in itr]
                idx = idxs[-1]
                entry_metadata = entry[:idxs[-1]]
                entry_data = entry[idx+1:len(entry)-1]
                metadata.append(entry_metadata)
                if entry_data[-1] == '-' or \
                   entry_data[-1] == '(':
                    entry_data = ' ' + entry_data + '  <NEWLINE>'
                else:
                    entry_data = ' ' + entry_data + ' <NEWLINE>'
                text_data.append(entry_data)
            text_data = correct_text_data(generic_business_list_dict_both_2,
                                          hyphenated_generic_occupation_dict_both_2,
                                          internal_ref_abbr_list_dict_both_2,
                                          unhyphenated_generic_occupation_dict_both_2,
                                          words_lower, occupation_key_list, text_data)
            write_to_file(fl_wrtr, metadata, text_data)
            
    return global_excluded_surnames_list
      
#
def add_spaces(text_data):
    text_data = re.sub('\(', '( ', text_data)
    text_data = re.sub('\)', ' )', text_data)
    return text_data
    
#
def correct_digits(line_data):
    
    # Letters made into digits
    line_data = re.sub(' 0 ', ' O ', line_data)
    match_strs = [ '[A-Za-z]+0 ', '[A-Za-z]+0[A-Za-z]+' ]
    for match_str in match_strs:
        match = re.search(match_str, line_data)
        if match is not None:
            replace_str = match.group(0)
            replace_str = re.sub('0', 'O', replace_str)
            line_data = re.sub(match_str, replace_str, line_data)
    
    # Digits made into letters
    match_strs = [ 'hl[0-9]+', 'rl[0-9]+' ]
    for match_str in match_strs:
        match = re.search(match_str, line_data)
        if match is not None:
            replace_str = match.group(0)
            replace_str = re.sub('hl', 'h1', replace_str)
            replace_str = re.sub('rl', 'r1', replace_str)
            line_data = re.sub(match_str, replace_str, line_data)
    return line_data
            
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
def correct_for_empty_entries(text_data):
    text_data = text_data.replace('<NEWLINE> <NEWLINE>', '<NEWLINE>  <NEWLINE>')
    if text_data[:10] == ' <NEWLINE>':
        text_data = ' ' + text_data
    return text_data
            
#
def correct_h_r_address(line_data):
    match_strs = [ ' h [0-9]', ' r [0-9]' ]
    for match_str in match_strs:
        match = re.search(match_str, line_data)
        if match is not None:
            replace_str = match.group(0)
            replace_str = replace_str[:2] + replace_str[3:]
            line_data = re.sub(match_str, replace_str, line_data)
    match_strs = [ ' h[A-Z]', ' r[A-Z]' ]
    for match_str in match_strs:
        match = re.search(match_str, line_data)
        if match is not None:
            replace_str = match.group(0)
            replace_str = replace_str[:2] + ' ' + replace_str[2:]
            line_data = re.sub(match_str, replace_str, line_data)
    return line_data

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
def correct_split_words(case_flg, words_lower, occupation_key_list, text_data):
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
                    if case_flg == 0:
                        if ' ' + text_str.lower() + ' ' in occupation_key_list:
                            idx_list.append(idxs[i+1])
                    elif case_flg == 1:
                        if text_str.lower() in words_lower:
                            idx_list.append(idxs[i+1])
    idx_list = sorted(idx_list, reverse=True)
    for i in range(len(idx_list)):
        text_data = text_data[:idx_list[i]] + text_data[idx_list[i]+1:]
    return text_data

#
def correct_spurious_punctuation(text_data):
    text_data = text_data.replace('.', ' ')
    text_data = text_data.replace('-(', ' (')
    text_data = text_data.replace(')-', ') ')
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
    text_data = re.sub(' -', '-', text_data)
    text_data = re.sub('- ', '-', text_data)
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
def correct_text_data(generic_business_list_dict_both_2, hyphenated_generic_occupation_dict,
                      internal_ref_abbr_list_dict_both_2, unhyphenated_generic_occupation_dict, 
                      words_lower, occupation_key_list, text_data):
    text_data = ''.join(text_data)
    text_data = correct_line_continuation(text_data)
    text_data = remove_spurious_marks(text_data)
    text_data = correct_spurious_spaces(text_data)
    text_data = add_spaces(text_data)
    text_data = correct_spurious_punctuation(text_data)
    text_data = correct_split_words(0, words_lower, occupation_key_list, text_data)
    text_data = dict_correction(True, False, hyphenated_generic_occupation_dict, text_data)
    text_data = dict_correction(True, True, unhyphenated_generic_occupation_dict, text_data)
    text_data = dict_correction(False, False, generic_business_list_dict_both_2, text_data)
    text_data = dict_correction(False, False, internal_ref_abbr_list_dict_both_2, text_data)
    text_data = correct_split_words(1, words_lower, occupation_key_list, text_data)
    text_data = remove_spaces(text_data)
    text_data = correct_for_empty_entries(text_data)
    return text_data   

#
def get_excluded_surnames_list(text_data):
    surnames = []
    for i in range(len(text_data)):
        line_data = text_data[i]
        match = re.search(' ', line_data)
        if match is not None:
            surname_tmp = line_data[:match.start()]
        else:
            surname_tmp = line_data
        if len(surname_tmp) > 0 and surname_tmp != '"':
            surnames.append(surname_tmp.upper())
    surnames_tmp = sorted(surnames)
    excluded_surnames_list = []
    surnames = []
    for i in range(len(surnames_tmp)):
        entry = surnames_tmp[i]
        if entry.isdigit():
            excluded_surnames_list.append(entry)
        else:
            surnames.append(entry)
    if len(surnames) > 4:
        surnames_inits = []
        for i in range(len(surnames)):
            surnames_inits.append(ord(surnames[i][0]))
        surnames_inits_idxs = [i+1 for i,v in enumerate(np.diff(surnames_inits)) if v > 1]
        surnames_inits_idxs.append(0)
        surnames_inits_idxs.append(len(surnames))
        surnames_inits_idxs = sorted(surnames_inits_idxs)
        surnames_class_list = []
        surnames_class_list_lens = []                        
        for i in range(len(surnames_inits_idxs)-1):
            surnames_list_tmp = surnames[surnames_inits_idxs[i]:surnames_inits_idxs[i+1]]
            surnames_class_list.append(surnames_list_tmp)
            surnames_class_list_lens.append(len(surnames_list_tmp))
        m = max(surnames_class_list_lens)
        excluded_surnames_list = []
        max_class_ctr = 0
        for i in range(len(surnames_class_list)):
            if len(surnames_class_list[i]) != m:
                excluded_surnames_list.extend(surnames_class_list[i])
            else:
                max_class_ctr += 1
        if max_class_ctr > 1:
            excluded_surnames_list = []
            excluded_surnames_list.extend(surnames)
    else:
        excluded_surnames_list.extend(surnames)
    return excluded_surnames_list

#
def parse_column(excluded_surnames_list, words_lower, text_data, metadata, fl_wrtr):
    current_surname = []
    entries = []
    for i in range(len(text_data)):
        line_metadata = metadata[i]
        line_data = text_data[i]
        line_data = correct_missing_space(words_lower, line_data)
        line_data = correct_ditto(line_data)
        line_data = correct_digits(line_data)
        line_data = correct_h_r_address(line_data)
        line_data, current_surname = resolve_dittos(line_data, current_surname)
        current_surname_tmp = ''.join(current_surname)
        if len(excluded_surnames_list) > 0:
            for i in range(len(excluded_surnames_list)):
                if current_surname_tmp.upper() == excluded_surnames_list[i]:
                    current_surname = []
        if retain_entry(line_data):
            if len(line_data) > 0:
                entry = line_metadata + '\t' + line_data + '\n'
                entries.append(entry)
    return entries
    
#
def remove_spaces(text_data):
    text_data = re.sub('\( ', '(', text_data)
    text_data = re.sub(' \)', ')', text_data)
    return text_data

#
def remove_spurious_marks(text_data):
    text_data = re.sub(' , ', '  ', text_data)
    text_data = re.sub(' \. ', '  ', text_data)
    text_data = re.sub('_', ' ', text_data)
    return text_data

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

#
def retain_entry(line_data):
    retain_entry_flg = True
    match = re.search('[A-Za-z]+', line_data)
    if match is not None:
        if match.group(0) == line_data:
            retain_entry_flg = False
    match = re.search('[A-Za-z]+ SEE ', line_data.upper())
    if match is not None:
        retain_entry_flg = False
    match = re.search(' DIED ', line_data.upper())
    if match is not None:
        retain_entry_flg = False
    match = re.search(' MOVED TO ', line_data.upper())
    if match is not None:
        retain_entry_flg = False
    return retain_entry_flg

#
def write_to_file(fl_wrtr, metadata, text_data):
    text_data = text_data[1:len(text_data)-10]
    itr = re.finditer(r' <NEWLINE> ', text_data)
    idxs = [idx.start() for idx in itr]
    idxs = idxs + [0]
    idxs = idxs + [len(text_data)]
    idxs = sorted(idxs)
    text_data_out = []
    if len(metadata) != len(idxs)-1:
        print(metadata[0])
    for i in range(len(metadata)):
        line_metadata = metadata[i]
        if i == 0:
            line_data = text_data[idxs[i]:idxs[i+1]]
            if len(line_data) > 0:
                text_data_out.append(line_metadata + '\t' + line_data + '\n')
        else:
            line_data = text_data[idxs[i]+11:idxs[i+1]]
            if len(line_data) > 0:
                text_data_out.append(line_metadata + '\t' + line_data + '\n')
    fl_wrtr.run(text_data_out)