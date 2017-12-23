# Imports
import re
import sys
from xlrd import open_workbook

# Local Imports
sys.path.insert(0, 'py/hr_tools')
from file_writer import file_writer

#
def hr_text_segmenter2(sect_dir, file_idx, pdf_name, xlsx_dir, xlsx_occupation_abbr):
    
    #
    xlsx_file = xlsx_dir + xlsx_occupation_abbr
    book = open_workbook(xlsx_file)
    sheet = book.sheets()[0]
    occupation_list = []
    for i in range(sheet.nrows):
        rowvals = sheet.row(i)
        rowval = rowvals[1].value
        if rowval != '':
            occupation_list.append(rowval.upper())
            occupation_list.append('HEAD ' + rowval.upper())
    occupation_list = list(set(occupation_list))
    occupation_list.sort(key = lambda x:len(x), reverse = True)
    
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
            occupation = 'NA'
                
            #
            if residential_address != 'NA':
                line_data, occupation = extract_occupation(occupation_list, line_data)
            
            #
            entry = line_metadata + '\t' + line_data + '\t' + occupation + '\t' + \
                    business_address + '\t' + residence_type + '\t' + \
                    residential_address + '\t' + telephone_number
            entries = [ entry ]           
            fl_wrtr.run(entries)

#
def extract_occupation(occupation_list, line_data):
    occupation = ''
    for i in range(len(occupation_list)):
        match = re.search(occupation_list[i], line_data);
        if match is not None:
            if match.start() != 0 and line_data[match.start()-1] == ' ':
                submatch = re.search('<', line_data)
                if submatch is None:
                    line_data = line_data[:match.start()] + '<OCCUPATION>'
                    occupation = line_data[match.start():] + occupation
                else:
                    occupation = line_data[match.start():submatch.start()] + occupation
                    line_data = line_data[:match.start()] + '<OCCUPATION>' + \
                                line_data[submatch.start():]
                line_data = line_data.replace('<OCCUPATION><OCCUPATION>', '<OCCUPATION>')
    if len(occupation) == 0:
        occupation = 'NA'
    return line_data, occupation