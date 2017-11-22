# Imports
from xlrd import open_workbook
import re

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
                xlsx_dict[' ' + rowval[0] + ' '] = ' ' + rowval[1] + ' '
        elif mode_flg == 2:
            if len(rowval[0]) >= 2:
                xlsx_dict[' ' + rowval[0] + ' '] = ' ' + rowval[1] + ' '
    return xlsx_dict

#
def dict_correction(dictionary, text_str):
    for key in dictionary.keys():
        match = re.search(key, text_str)
        if match is not None:
            text_str = re.sub(key, dictionary[key], text_str)
    return text_str