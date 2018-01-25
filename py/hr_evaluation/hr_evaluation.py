# Imports
import Levenshtein
import re
import sys

# Local Imports
sys.path.insert(0, 'py/hr_tools')
from file_writer import file_writer

#
def hr_evaluation(sect_dir, file_idx, pdf_name):
    
    #
    directory_dir = sect_dir
    
    #
    directory_txt_dir = directory_dir + 'txt/'
    directory_txt_infile = directory_txt_dir + pdf_name[:len(pdf_name)-4] + \
                           str(file_idx) + '.txt'
    directory_txt_outfile = directory_txt_dir + pdf_name[:len(pdf_name)-4] + \
                            str(file_idx+1) + '.txt'
        
    #
    fl_wrtr = file_writer(directory_txt_outfile)
        
    #
    alphabetical_list = list()
    good_entry_ctr = 0
    total_entry_ctr = 0
    current_column = 0
    current_surname = []
    with open(directory_txt_infile, 'r') as f:
        for line in f:
            
            #
            itr = re.finditer(r'\t', line)
            idxs = [idx.start() for idx in itr]
            line_metadata = line[:idxs[4]]
            line_data = line[idxs[4]+1:idxs[5]]
            occupation = line[idxs[5]+1:idxs[6]]
            business = line[idxs[6]+1:idxs[7]]
            business_address = line[idxs[7]+1:idxs[8]]
            residence_type = line[idxs[8]+1:idxs[9]]
            residential_address = line[idxs[9]+1:idxs[10]]
            telephone_number = line[idxs[10]+1:-1]
            
            column = line_metadata[-1]
            
            #           
            if column != current_column:
                alphabetical_list = []
            
            #
            current_column, current_surname, alphabetical_flg = \
                is_entry_alphabetical(current_column, current_surname, column, line_data)
            alphabetical_list.append(alphabetical_flg)
            
            start_character_str = starts_with_character(line_data)
            address_str = has_address(business_address, residential_address)
            good_entry_str = is_good_entry(start_character_str, address_str)
            
            #
            total_entry_ctr += 1
            if good_entry_str == 'IS_GOOD_ENTRY':
                good_entry_ctr += 1
                
            #
            entry = line_metadata + '\t' + '\'' + line_data + '\'' + '\t' + occupation + '\t' + \
                    business + '\t' + business_address + '\t' + residence_type + '\t' + \
                    residential_address + '\t' + telephone_number + '\t' + start_character_str + '\t' + \
                    address_str + '\t' + good_entry_str + '\n'
                
            #if good_entry_str != 'IS_GOOD_ENTRY':
            #    print(entry)
            #    input("Press Enter to continue...")
            
            entries = [ entry ]          
            fl_wrtr.run(entries)
            
    #print(alphabetical_list)
         
    performance = good_entry_ctr / total_entry_ctr
    print('')
    print(good_entry_ctr)
    print(total_entry_ctr)
    print(performance)
            
#
def has_address(business_address, residential_address):
    has_address_flg = False
    if residential_address != 'NA' and residential_address != 'DITTO':
        has_address_flg = True
    elif business_address != 'NA':
        has_address_flg = True
    if has_address_flg:
        address_str = 'HAS_ADDRESS'
    else:
        address_str = 'NOT_HAS_ADDRESS'
    return address_str

#
def is_entry_alphabetical(current_column, current_surname, column, line_data):

    #
    match = re.search('[A-Za-z]+', line_data)
    if match is not None:
        surname = match.group(0)
    else:
        surname = []

    #           
    if column != current_column:
        current_surname = surname
        current_column = column
        alphabetical_flg = False
    else:
        if len(current_surname) > 0 and len(surname) > 0:
            dist = ord(surname[0]) - ord(current_surname[0])
            if dist == 0 or dist == 1:
                alphabetical_flg = True
            else:
                alphabetical_flg = False
        else:
            alphabetical_flg = False
        current_surname = surname
        
    #
    return current_column, current_surname, alphabetical_flg

#
def is_good_entry(start_character_str, address_str):
    good_entry_str = 'IS_GOOD_ENTRY'
    if start_character_str == 'NOT_STARTS_WITH_CHARACTER':
        good_entry_str = 'NOT_IS_GOOD_ENTRY'
    if address_str == 'NOT_HAS_ADDRESS':
        good_entry_str = 'NOT_IS_GOOD_ENTRY'
    return good_entry_str

#
def starts_with_character(line_data):
    match = re.search('[A-Za-z]', line_data[0])
    if match is None:
        start_character_str = 'NOT_STARTS_WITH_CHARACTER'
    else:
        start_character_str = 'STARTS_WITH_CHARACTER'
    return start_character_str