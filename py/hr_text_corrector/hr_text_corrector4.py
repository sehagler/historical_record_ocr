# Imports
import re
import sys

# Local Imports
sys.path.insert(0, 'py/hr_tools')
from abbr_dict import abbr_dict, abbr_dict_occupations, dict_correction
from file_writer import file_writer

#
def hr_text_corrector4(sect_dir, file_idx, pdf_name, xlsx_dir, xlsx_general_abbr):
    
    #
    directory_dir = sect_dir
    
    #
    directory_txt_dir = directory_dir + 'txt/'
    directory_txt_infile = directory_txt_dir + pdf_name[:len(pdf_name)-4] + \
                           str(file_idx) + '.txt'
    directory_txt_outfile = directory_txt_dir + pdf_name[:len(pdf_name)-4] + \
                            str(file_idx+1) + '.txt'
    
    #
    xlsx_file = xlsx_dir + xlsx_general_abbr
    general_abbr_dict_upper_1 = abbr_dict(True, 1, xlsx_file)
    
    #
    fl_wrtr = file_writer(directory_txt_outfile)
    
    #
    current_column = 0
    current_surname = []
    with open(directory_txt_infile, 'r') as f:
        for line in f:
            
            #
            itr = re.finditer(r'\t', line)
            idxs = [idx.start() for idx in itr]
            line_metadata = line[:idxs[4]].upper()
            line_data = line[idxs[4]+1:idxs[5]].upper()
            business_address = line[idxs[5]+1:idxs[6]].upper()
            residence_type = line[idxs[6]+1:idxs[7]].upper()
            residential_address = line[idxs[7]+1:idxs[8]].upper()
            telephone_number = line[idxs[8]+1:].upper()

            #
            business_address = correct_address(general_abbr_dict_upper_1, business_address)
            residential_address = correct_address(general_abbr_dict_upper_1, residential_address)
            
            #
            residential_address = resolve_dittos(business_address, residential_address)
                   
            #
            entry = line_metadata + '\t' + line_data + '\t' + business_address + '\t' + \
                    residence_type + '\t' + residential_address + '\t' + telephone_number
            entries = [ entry ]           
            fl_wrtr.run(entries)
            
#
def correct_address(general_abbr_dict, address):
    address = ' ' + address + ' '
    address = dict_correction(False, False, general_abbr_dict, address)
    address = address[1:len(address)-1]
    return address

#
def resolve_dittos(business_address, residential_address):
    match = re.search(r'DITTO', residential_address)
    if match is not None:
        address_str = 'DITTO'
        if residential_address == 'DITTO':
            if business_address != 'NA':
                address_str = business_address
        else:
            sub_match = re.search(r'[0-9]+ DITTO', residential_address)
            if sub_match is not None:
                sub_sub_match = re.search(r'[A-Za-z]+', business_address)
                if sub_sub_match is not None:
                    address_str = business_address[sub_sub_match.start():]
        residential_address = re.sub('DITTO', address_str, residential_address)    
    return residential_address