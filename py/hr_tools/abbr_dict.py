# Imports
import re
from xlrd import open_workbook

#
def _extend_with_errors(xlsx_dict, abbr_list, original_letter, error_letter):
    abbr = abbr_list[0]
    itr = re.finditer(original_letter, abbr)
    idxs = [idx.start() for idx in itr]
    idxs = sorted(idxs)
    for i in range(len(idxs)):
        abbr_tmp = abbr
        if i == 0:
            abbr_tmp = error_letter + abbr_tmp[i+1:]
        elif i == len(abbr):
            abbr_tmp = abbr_tmp[:-1] + error_letter
        else:
            abbr_tmp = abbr_tmp[:i] + error_letter + abbr_tmp[i+1:]
        if abbr_tmp not in xlsx_dict:
            abbr_list.append(abbr_tmp)
    return abbr_list

#
def _get_specifier_dict():
    specifier_dict = dict()
    specifier_dict['bndr'] = 'binder'
    specifier_dict['dir'] = 'director'
    specifier_dict['hlpr'] = 'helper'
    specifier_dict['kpr'] = 'keeper'
    specifier_dict['mgr'] = 'manager'
    specifier_dict['mkr'] = 'maker'
    specifier_dict['mn'] = 'man'
    specifier_dict['mstr'] = 'master'
    specifier_dict['opr'] = 'operator'
    specifier_dict['tndr'] = 'tender'
    specifier_dict['wkr'] = 'worker'
    return specifier_dict

#
def _unpack_occupation_key(upper_flg, xlsx_dict, rowval0, rowval1, key_str, value_str): 
    if upper_flg:
        key_str = key_str.upper()
        value_str = value_str.upper()
    if key_str == 'mn':
        len_key_str = len(key_str) + 1
        len_value_str = len(value_str)
        if len(rowval0) > len_key_str and rowval0[-len_key_str:] == ' ' + key_str:
            key_base = rowval0[:-len_key_str]
            value_base = rowval1[:-len_value_str]
            xlsx_dict = _xlsx_dict_append(xlsx_dict, key_base + ' man', value_base + 'man')
            xlsx_dict = _xlsx_dict_append(xlsx_dict, key_base + 'man', value_base + 'man')
            xlsx_dict = _xlsx_dict_append(xlsx_dict, key_base + 'mn', value_base + 'man')
            xlsx_dict = _xlsx_dict_append(xlsx_dict, key_base + ' wm', value_base + 'woman')
            xlsx_dict = _xlsx_dict_append(xlsx_dict, key_base + ' wn', value_base + 'woman')
            xlsx_dict = _xlsx_dict_append(xlsx_dict, key_base + 'wm', value_base + 'woman')
            xlsx_dict = _xlsx_dict_append(xlsx_dict, key_base + 'wn', value_base + 'woman')
    else:
        len_key_str = len(key_str) + 1
        len_value_str = len(value_str)
        if len(rowval0) > len_key_str and rowval0[-len_key_str:] == ' ' + key_str:
            key_base = rowval0[:-len_key_str]
            value_base = rowval1[:-len_value_str]
            xlsx_dict = _xlsx_dict_append(xlsx_dict, key_base + key_str, value_base + value_str)
    return xlsx_dict

#
def _unpack_occupation_value(rowval_list, rowval, value_str):
    if value_str == 'man':
        len_value_str = len(value_str) + 1
        if len(rowval) > len_value_str and rowval[-len_value_str:] == ' ' + value_str:
            rowval_list.append(rowval[:-len_value_str] + value_str)
            rowval_list.append(rowval[:-len_value_str] + ' woman')
            rowval_list.append(rowval[:-len_value_str] + 'woman')
    else:
        len_value_str = len(value_str) + 1
        if len(rowval) > len_value_str and rowval[-len_value_str:] == ' ' + value_str:
            rowval_list.append(rowval[:-len_value_str] + value_str)
    return rowval_list
    
#
def _xlsx_dict_append(xlsx_dict, abbr, value):
    abbr_list = [ abbr ]
    abbr_list = _extend_with_errors(xlsx_dict, abbr_list, ' ', '')
    abbr_list = _extend_with_errors(xlsx_dict, abbr_list, 'c', 'e')
    abbr_list = _extend_with_errors(xlsx_dict, abbr_list, 'd', 'a')
    abbr_list = _extend_with_errors(xlsx_dict, abbr_list, 'l', 'i')
    for abbr_tmp in abbr_list:
        xlsx_dict[' ' + abbr_tmp + ' '] = ' ' + value + ' '
    return xlsx_dict

#
def abbr_dict(upper_flg, mode_flg, xlsx_file):
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
                xlsx_dict = _xlsx_dict_append(xlsx_dict, rowval[0], rowval[1])
        elif mode_flg == 2:
            if len(rowval[0]) >= 2:
                xlsx_dict = _xlsx_dict_append(xlsx_dict, rowval[0], rowval[1])
    return xlsx_dict

#
def abbr_dict_occupations(upper_flg, mode_flg, xlsx_file):
    specifier_dict = _get_specifier_dict()
    key_list = list(specifier_dict.keys())
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
        if rowval[0] != rowval[1]:
            if mode_flg == 1:
                if len(rowval[0]) == 1:
                    xlsx_dict = _xlsx_dict_append(xlsx_dict, rowval[0], rowval[1])
            elif mode_flg == 2:
                if len(rowval[0]) >= 2:
                    xlsx_dict = _xlsx_dict_append(xlsx_dict, rowval[0], rowval[1])
                    for key in key_list:
                        xlsx_dict = _unpack_occupation_key(upper_flg, xlsx_dict, rowval[0], rowval[1],
                                                           key, specifier_dict[key])
    return xlsx_dict

#
def dict_correction(dictionary, text_str):
    key_list = sorted(list(dictionary.keys()), key = len, reverse = True)
    for key in key_list:
        match = re.search(key, text_str)
        if match is not None:
            text_str = re.sub(key, dictionary[key], text_str)
    return text_str

#
def get_occupation_list(xlsx_file):
    specifier_dict = _get_specifier_dict()
    key_list = list(specifier_dict.keys())
    book = open_workbook(xlsx_file)
    sheet = book.sheets()[0]
    occupation_list = []
    for i in range(sheet.nrows):
        rowvals = sheet.row(i)
        rowval = rowvals[1].value
        rowval_list = [ rowval ]
        for key in key_list:
            rowval_list = _unpack_occupation_value(rowval_list, rowval, specifier_dict[key])
        for rowval in rowval_list:
            if rowval != '':
                occupation_list.append(rowval.upper())
                occupation_list.append('HEAD ' + rowval.upper())
    occupation_list = list(set(occupation_list))
    occupation_list.sort(key = lambda x:len(x), reverse = True)
    return occupation_list