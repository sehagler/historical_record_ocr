# Imports
from nltk.corpus import words
import re
import sys

# Local Imports
sys.path.insert(0, 'py/hr_tools')
from abbr_dict import abbr_dict, dict_correction
from file_writer import file_writer

#
def hr_text_corrector2(sect_dir, file_idx, pdf_name, global_excluded_surnames_list):
    
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
    current_column = 0
    metadata = []
    text_data = []
    with open(directory_txt_infile, 'r') as f:
        for line in f:
            
            #
            itr = re.finditer(r'\t', line)
            idxs = [idx.start() for idx in itr]
            idx = idxs[-1]
            column = line[idxs[-2]+1:idxs[-1]]
            line_metadata = line[:idxs[-1]]
            line_data = line[idx+1:len(line)-1]
            
            if column == current_column:
                metadata.append(line_metadata)
                text_data.append(line_data + ' <NEWLINE> ')
            else:
                if len(text_data) > 0:
                    text_data = ''.join(text_data)
                    write_to_file(fl_wrtr, metadata, text_data)
                current_column = column
                metadata = []
                metadata.append(line_metadata)
                text_data = []
                text_data.append(line_data + ' <NEWLINE> ')
    
    text_data = ''.join(text_data)
    write_to_file(fl_wrtr, metadata, text_data)

#
def line_data_is_good(line_data):
    is_good_flg = True
    if len(line_data) == 0:
        is_good_flg = False
    if line_data == ' ':
        is_good_flg = False
    return is_good_flg

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
            if line_data_is_good(line_data):
                text_data_out.append(line_metadata + '\t' + line_data + '\n')
        else:
            line_data = text_data[idxs[i]+11:idxs[i+1]]
            if line_data_is_good(line_data):
                text_data_out.append(line_metadata + '\t' + line_data + '\n')
    fl_wrtr.run(text_data_out)