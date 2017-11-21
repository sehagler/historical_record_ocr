#
import json
import numpy as np
from os import makedirs, remove
from os.path import isfile
import re

#
class file_writer(object):
    
    #
    def __init__(self, txt_filename):
        
        #
        self._filename = txt_filename
        
        #
        if isfile(self._filename):
            remove(self._filename)
            
    # append entries to txt-file
    def _append_entry_to_txt_file(self, entry):
        with open(self._filename, "a") as myfile:
            myfile.write(entry)
    
    #
    def run(self, entries):
        for entry in entries:
            self._append_entry_to_txt_file(entry)   
        