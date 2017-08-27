#
import json
import numpy as np
from os import makedirs
from os.path import isfile
import re

#
class segment_entries(object):
    
    #
    def __init__(self, txt_dir, txt_filename):
        
        #
        self._txt_dir = txt_dir
        self._txt_filename = txt_filename
        self._filename = txt_dir + txt_filename
        
        #
        makedirs(self._txt_dir, exist_ok=True)
            
    # append entries to txt-file
    def _append_entry_to_txt_file(self, entry):
        with open(self._filename, "a") as myfile:
            myfile.write(entry)
            
    def _correct_entry(self, entry):
        if entry[0:2] == '1 ': idx = 2
        elif entry[0] == '1' and entry[2] == ' ': idx = 3
        elif entry[1:3] == '" ': idx = 3
        elif entry[0] == '"' and entry[1] != ' ': idx = 1
        elif entry[0] != '"' and entry[1] == ' ': idx = 2
        else: idx = 0
        if idx > 0:
            entry = '" ' + entry[idx:]
        return entry
            
    # extract telephone number from entry
    def _extract_telephone_number(self, entry):
        telephone_number = 'NA'
        tel_idx = re.search("Tel ", entry)
        if tel_idx:
            sub_entry = entry[tel_idx.start():]
            digit_idx = re.search("\d", sub_entry)
            telephone_number = sub_entry[:digit_idx.start()+4]
            entry = entry[:tel_idx.start()] + \
                    entry[tel_idx.start() + len(telephone_number):]
        return entry, telephone_number
    
    # extract a basic street address
    def _extract_basic_street_address(self, entry):
        space_idxs = []
        for i in range(len(entry)):
            if entry[i] == ' ':
                space_idxs.append(i)
        digit_idx = re.search("\d", entry)
        try:
            for i in space_idxs:
                if i <= digit_idx.start():
                    idx = i
            sub_entry = entry[:idx]
            address = entry[idx+1:] 
        except:
            sub_entry = entry
            address = 'NA'
      
        return sub_entry, address
    
    #
    def _extract_street_address_with_apartment(self, entry):
        idx = re.search("apt ", entry)
        if idx:
            sub_entry = entry[:idx.start()]
            apartment_number = entry[idx.start():]
            sub_entry, address = self._extract_basic_street_address(sub_entry)
            address = address + apartment_number
            address = ''.join(address)
        else:
            sub_entry = entry
            address = 'NA'
        return sub_entry, address
    
    #
    def _extract_street_address_with_numbered_street(self, entry):
        idx = re.search("(\d+)d", entry)
        if idx:
            sub_entry = entry[:idx.start()]
            street = entry[idx.start():]
            sub_entry, address = self._extract_basic_street_address(sub_entry)
            address = address + street
            address = ''.join(address)
        else:
            sub_entry = entry
            address = 'NA'
        return sub_entry, address
                
    #
    def _get_num_digit_seqs(self, entry):
        idxs = [i for i, ch in enumerate(entry) if ch.isdigit()]
        diffs = [idxs[i+1]-idxs[i] for i in range(len(idxs)-1)]
        if not diffs:
            num_digit_seqs = 0
        else:
            num_digit_seqs = sum(i > 1 for i in diffs) + 1
        return num_digit_seqs
    
    #
    def run(self, entries):
        num_digit_seqs = self._get_num_digit_seqs(entries)
        for i in range(len(entries)):
            entry = entries[i]
            #entry = self._correct_entry(entry)
            entry, telephone_number = self._extract_telephone_number(entry)
            num_digit_seqs = self._get_num_digit_seqs(entry)
            if num_digit_seqs == 1:
                name, address = self._extract_basic_street_address(entry)
            elif num_digit_seqs == 2:
                name, address = self._extract_street_address_with_apartment(entry)
                if address == 'NA':
                    name, address = self._extract_street_address_with_numbered_street(entry)
            else:
                name = entry
                address = 'NA'
            entry = '\'' + name + '\'' + '\t' + address + '\t' + telephone_number + '\n'
            entry = ''.join(entry)
            print(entry)
            self._append_entry_to_txt_file(entry)   
        