#
import json
import numpy as np
from os import makedirs
from os.path import isfile
import re

#
class file_writer(object):
    
    #
    def __init__(self, txt_filename):
        
        #
        self._filename = txt_filename
            
    # append entries to txt-file
    def _append_entry_to_txt_file(self, entry):
        with open(self._filename, "a") as myfile:
            myfile.write(entry)
    
    #
    def run(self, pdf_filename, pdf_page_num, pdf_column_num, entries):
        for i in range(len(entries)):
            entry = pdf_filename + '\t' + str(pdf_page_num) + '\t' + str(pdf_column_num) + '\t' \
                    + '\'' + entries[i] +'\'' + '\n'
            entry = ''.join(entry)
            print(entry)
            self._append_entry_to_txt_file(entry)   
        