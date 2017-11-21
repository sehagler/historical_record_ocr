# Imports
import re
import sys

# Local Imports
sys.path.insert(0, 'py/hr_tools')
from file_writer import file_writer

#
def hr_text_segmenter(sect_dir, pdf_name):
    
    #
    directory_dir = sect_dir
    
    #
    directory_txt_dir = directory_dir + 'txt/'
    directory_txt_infile = directory_txt_dir + pdf_name[:len(pdf_name)-4] + '1.txt'
    directory_txt_outfile = directory_txt_dir + pdf_name[:len(pdf_name)-4] + '2.txt'
    
    #
    fl_wrtr = file_writer(directory_txt_outfile)
    
    #
    with open(directory_txt_infile, 'r') as f:
        for line in f:
            iter = re.finditer(r'\t', line)
            idxs = [idx.start() for idx in iter]
            idx = idxs[-1]
            line_metadata = line[:idx]
            line_data = line[idx+1:len(line)-1]
            
            #
            business_address = 'NA'
            residence_type = 'NA'
            residential_address = 'NA'
            telephone_number = 'NA'

            #
            line_data, telephone_number = extract_telephone_number(line_data)
            
            #
            residence_flg, residence_type, residence_num_address_flg = \
                is_residence(line_data)
            if residence_flg:
                if not residence_num_address_flg:
                    line_data, residential_address = \
                        extract_residential_nonnumerical_address(line_data, residence_type)
                if residence_num_address_flg:
                    line_data, residential_address = \
                        extract_residential_numerical_address(line_data, residence_type)
                        
            #
            num_digit_seqs = get_num_digit_seqs(line_data)
            if num_digit_seqs == 1:
                line_data, business_address = extract_business_numerical_address(line_data)
            
            #
            entry = line_metadata + '\t' + line_data + '\t' + business_address + '\t' + \
                    residence_type + '\t' + residential_address + '\t' + telephone_number + '\n'            
            entries = [ entry ]           
            fl_wrtr.run(entries)
            
#
def get_num_digit_seqs(line_data):
    idxs = [i for i, ch in enumerate(line_data) if ch.isdigit()]
    diffs = [idxs[i+1]-idxs[i] for i in range(len(idxs)-1)]
    if not diffs:
        num_digit_seqs = 0
    else:
        num_digit_seqs = sum(i > 1 for i in diffs) + 1
    return num_digit_seqs

# 
def extract_business_numerical_address(line_data):
    match = re.search(' [0-9]', line_data)
    if match is not None:
        try:
            bracket_idx = line_data.index('<')
            address = line_data[match.start()+1:bracket_idx-1]
            line_data = line_data[:match.start()+1] + '<BUSINESS ADDRESS>' + \
                        line_data[bracket_idx:]
        except:
            address = line_data[match.start()+1:]
            line_data = line_data[:match.start()+1] + '<BUSINESS ADDRESS>'
    else:
        address = 'NA'
    return line_data, address
            
# 
def extract_residential_nonnumerical_address(line_data, residence_type):
    if residence_type == 'H':
        match = re.search(' h [A-Za-z]', line_data)
    elif residence_type == 'R':
        match = re.search(' r [A-Za-z]', line_data)
    else:
        print('Bad residence type.')
    address = line_data[match.start()+3:]
    line_data = line_data[:match.start()+1] + '<RESIDENCE TYPE><RESIDENTIAL ADDRESS>'
    return line_data, address
            
# 
def extract_residential_numerical_address(line_data, residence_type):
    if residence_type == 'H':
        match = re.search(' h[0-9]', line_data)
    elif residence_type == 'R':
        match = re.search(' r[0-9]', line_data)
    else:
        print('Bad residence type.')
    try:
        bracket_idx = line_data.index('<')
        address = line_data[match.start()+2:bracket_idx-1]
        line_data = line_data[:match.start()+1] + '<RESIDENCE TYPE><RESIDENTIAL ADDRESS>' + \
                    line_data[bracket_idx:]
    except:
        address = line_data[match.start()+2:]
        line_data = line_data[:match.start()+1] + '<RESIDENCE TYPE><RESIDENTIAL ADDRESS>'
    return line_data, address

# extract telephone number from entry
def extract_telephone_number(line_data):
    match_str = 'Tel [A-Za-z]+ [0-9]+'
    match = re.search(match_str, line_data)
    if match is None:
        telephone_number = 'NA'
    else:
        telephone_number = match.group(0)
        telephone_number = telephone_number[4:]
        line_data = re.sub(match_str, '<TELEPHONE NUMBER>', line_data)
    return line_data, telephone_number
            
#
def is_residence(line_data):
    residence_flg = False
    residence_type = 'NA'
    residence_num_address_flg = False   
    if re.search(' h[0-9]', line_data) is not None:
        residence_flg = True
        residence_type = 'H'
        residence_num_address_flg = True
    if re.search(' h [A-Za-z]', line_data) is not None:
        residence_flg = True
        residence_type = 'H'
        residence_num_address_flg = False
    if re.search(' r[0-9]', line_data) is not None:
        residence_flg = True
        residence_type = 'R'
        residence_num_address_flg = True
    if re.search(' r [A-Za-z]', line_data) is not None:
        residence_flg = True
        residence_type = 'R'
        residence_num_address_flg = False
    return residence_flg, residence_type, residence_num_address_flg