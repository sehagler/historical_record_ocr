# Imports
import re
from xlrd import open_workbook  

#
def _extended_list(text_str):
    text_str_list = [ text_str ]
    itr = re.finditer(' ', text_str)
    idxs = [idx.start() for idx in itr]
    idxs = sorted(idxs)
    for i in idxs:
        text_str_tmp = text_str
        if i == 0:
            text_str_tmp = text_str_tmp[1:]
        elif i == len(text_str_tmp):
            text_str_tmp = text_str_tmp[:-1]
        else:
            text_str_tmp = text_str_tmp[:i] + text_str_tmp[i+1:]
        text_str_list.append(text_str_tmp)
    return text_str_list

#
def _extend_with_errors(upper_flg, xlsx_dict, abbr_list, original_letter, error_letter):
    abbr = abbr_list[0]
    itr = re.finditer(original_letter, abbr)
    idxs = [idx.start() for idx in itr]
    idxs = sorted(idxs)
    for i in idxs:
        abbr_tmp = abbr
        if i == 0:
            abbr_tmp = error_letter + abbr_tmp[1:]
        elif i == len(abbr):
            abbr_tmp = abbr_tmp[:-1] + error_letter
        else:
            abbr_tmp = abbr_tmp[:i] + error_letter + abbr_tmp[i+1:]
        if abbr_tmp not in xlsx_dict:
            abbr_list.append(abbr_tmp)
    return abbr_list

#
def _generic_dict(xlsx_file):
    book = open_workbook(xlsx_file)
    sheet = book.sheets()[0]
    generic_dict = {}
    for i in range(sheet.nrows):
        rowvals = sheet.row(i)
        generic_dict[rowvals[0].value] = rowvals[1].value
    return generic_dict

#
def _generic_list_of_pairs(xlsx_file):
    book = open_workbook(xlsx_file)
    sheet = book.sheets()[0]
    generic_list = []
    for i in range(sheet.nrows):
        rowvals = sheet.row(i)
        generic_list.append([str(rowvals[0].value), str(rowvals[1].value)])
    return generic_list
    
#
def _xlsx_dict_append_with_common_ocr_errors(upper_flg, ocr_errors_list, xlsx_dict, 
                                             abbr, value):
    abbr_list = [ abbr ]
    abbr_list = _extend_with_errors(upper_flg, xlsx_dict, abbr_list, ' ', '')
    for i in range(len(ocr_errors_list)):
        abbr_list = _extend_with_errors(upper_flg, xlsx_dict, abbr_list, 
                                        ocr_errors_list[i][0], ocr_errors_list[i][1])
    for abbr_tmp in abbr_list:
        xlsx_dict[' ' + abbr_tmp + ' '] = ' ' + value + ' '
    return xlsx_dict

#
def _xlsx_dict_append(upper_flg, ocr_errors_dict, xlsx_dict, abbr, value):
    xlsx_dict = _xlsx_dict_append_with_common_ocr_errors(upper_flg, ocr_errors_dict, xlsx_dict,
                                                         abbr, value)
    xlsx_dict = _xlsx_dict_append_with_common_ocr_errors(upper_flg, ocr_errors_dict, xlsx_dict, 
                                                         abbr.lower(), value)
    return xlsx_dict

#
def abbr_dict(upper_flg, mode_flg, xlsx_file, common_ocr_errors_list_xlsx):
    ocr_errors_list = _generic_list_of_pairs(common_ocr_errors_list_xlsx)
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
        if mode_flg == 1:
            if len(rowval[0]) == 1:
                xlsx_dict = _xlsx_dict_append_with_common_ocr_errors(upper_flg, ocr_errors_list, xlsx_dict,
                                                                     rowval[0], rowval[1])
        elif mode_flg == 2:
            if len(rowval[0]) >= 2:
                xlsx_dict = _xlsx_dict_append_with_common_ocr_errors(upper_flg, ocr_errors_list, xlsx_dict,
                                                                     rowval[0], rowval[1])
    return xlsx_dict

#
def abbr_dict_occupations(upper_flg, hyphenated_flg, mode_flg, xlsx_file1, xlsx_file2,
                          common_ocr_errors_list_xlsx):
    tag_dict = _generic_dict(xlsx_file2)
    ocr_errors_list = _generic_list_of_pairs(common_ocr_errors_list_xlsx)
    tag_key_list = list(tag_dict.keys())
    book = open_workbook(xlsx_file1)
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
        go_flg = True
        match = re.search(r'[-]', rowval[0])
        if hyphenated_flg:
            if match is None:
                go_flg = False
        else:
            if match is not None:
                go_flg = False
        if go_flg:
            if rowval[1][-3:] == 'XYZ':
                if mode_flg == 2:
                    if len(rowval[0]) >= 2:
                        rowval1_base = rowval[1]
                        rowval0_base = rowval[0]
                        if rowval0_base[:-4] == rowval1_base[:-4]:
                            for tag_key in tag_key_list:
                                rowval0 = rowval0_base[:-4] + tag_key
                                rowval1 = rowval1_base[:-3] + tag_dict[tag_key]
                                xlsx_dict = _xlsx_dict_append(upper_flg, ocr_errors_list, xlsx_dict,
                                                              rowval0, rowval1) 
                        else:
                            rowval0 = rowval0_base[:-4]
                            rowval1 = rowval1_base[:-4]
                            xlsx_dict = _xlsx_dict_append(upper_flg, ocr_errors_list, xlsx_dict,
                                                          rowval0, rowval1)
                            for tag_key in tag_key_list:
                                rowval0 = rowval0_base[:-4] + tag_key
                                rowval1 = rowval1_base[:-3] + tag_dict[tag_key]
                                xlsx_dict = _xlsx_dict_append(upper_flg, ocr_errors_list, xlsx_dict, 
                                                              rowval0, rowval1)
                                rowval0 = rowval1_base[:-4] + tag_key
                                rowval1 = rowval1_base[:-3] + tag_dict[tag_key]
                                xlsx_dict = _xlsx_dict_append(upper_flg, ocr_errors_list, xlsx_dict,
                                                              rowval0, rowval1) 
            elif rowval[0] != rowval[1]:
                xlsx_dict = _xlsx_dict_append(upper_flg, ocr_errors_list, xlsx_dict,
                                              rowval[0], rowval[1]) 
    return xlsx_dict

#
def dict_correction(spurious_initial_or_final_flg, spurious_hyphen_flg, dictionary, text_str):
    key_list = sorted(list(dictionary.keys()), key = len, reverse = True)
    for key in key_list:
        match = re.search(key, text_str)
        if match is not None:
            text_str = re.sub(key, dictionary[key], text_str)
        if spurious_initial_or_final_flg:
            match = re.search(r' [A-Z]' + key[1:], text_str)
            if match is not None:
                text_str = re.sub(r' [A-Z]' + key[1:], 
                                  ' ' + text_str[match.start()+1] + ' ' + dictionary[key], text_str)
            match = re.search(key[:-1] + r'[A-Z] ', text_str)
            if match is not None:
                text_str = re.sub(key[:-1] + r'[A-Z] ', 
                                  dictionary[key] + ' ' + text_str[match.start() + len(key) - 1] + ' ', 
                                  text_str)
        if spurious_hyphen_flg:
            match = re.search(r'[-]' + key[1:], text_str)
            if match is not None:
                text_str = re.sub(r'[-]' + key[1:], dictionary[key], text_str)
            match = re.search(key[:-1] + r'[-]', text_str)
            if match is not None:
                text_str = re.sub(key[:-1] + r'[-]', dictionary[key], text_str)
    return text_str

#
def get_key_list(xlsx_file, common_ocr_errors_list_xlsx):
    xlsx_dict = abbr_dict(False, 2, xlsx_file, common_ocr_errors_list_xlsx)
    key_list = list(xlsx_dict.keys())
    return key_list

#
def get_value_list(xlsx_file):
    book = open_workbook(xlsx_file)
    sheet = book.sheets()[0]
    value_list = []
    for i in range(sheet.nrows):
        rowvals = sheet.row(i)
        rowval = rowvals[1].value
        value_list.append(rowval)
    value_list = list(set(value_list))
    value_list.sort(key = lambda x:len(x), reverse = True)
    return value_list

#
def get_value_list_occupations(occupations_flg, xlsx_file1, xlsx_file2):
    tag_dict = _generic_dict(xlsx_file2)
    tag_key_list = list(tag_dict.keys())
    book = open_workbook(xlsx_file1)
    sheet = book.sheets()[0]
    value_list = []
    for i in range(sheet.nrows):
        rowvals = sheet.row(i)
        rowval = rowvals[1].value
        rowval_list = []
        if rowval[-3:] == 'XYZ':
            for tag_key in tag_key_list:
                extended_rowval = _extended_list(rowval[:-3] + tag_dict[tag_key])
                rowval_list = list(set(rowval_list) | set(extended_rowval))
        else:
            extended_rowval = _extended_list(rowval)
            rowval_list = list(set(rowval_list) | set(extended_rowval))
        for rowval in rowval_list:
            if rowval != '':
                value_list.append(rowval)
                if occupations_flg:
                    value_list.append('assistant ' + rowval)
                    value_list.append('chief ' + rowval)
                    value_list.append('head ' + rowval)
    value_list = list(set(value_list))
    value_list.sort(key = lambda x:len(x), reverse = True)
    return value_list