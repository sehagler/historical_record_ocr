# Imports
import re
import sys
from xlrd import open_workbook

# Local Imports
sys.path.insert(0, 'py/hr_tools')
from file_writer import file_writer

#
def hr_text_segmenter2(columns_per_iteration, sect_dir, file_idx, pdf_name, 
                       generic_business_list_values, occupation_value_list, title_key_list):
    
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
        
        #
        column_ctr = 1
        current_column = 1
        metadata = []
        text_data = []
        
        #
        for line in f:
            
            #
            itr = re.finditer(r'\t', line)
            idxs = [idx.start() for idx in itr]
            idx = idxs[4]
            column = line[idxs[3]+1:idxs[4]]
            line_metadata = line[:idxs[4]]
            line_data = line[idx+1:len(line)-1]
            
            #
            if column != current_column:
                current_column = column
                column_ctr += 1
                
            #
            if column_ctr > columns_per_iteration:
                
                #
                if len(text_data) > 0:
                    text_data = extract_occupation_and_business(generic_business_list_values,
                                                                occupation_value_list, text_data)
                    text_data = extract_single_pair_parentheses(text_data)
                    text_data = indicate_missing_spouse_or_business(text_data)
                    text_data = extract_personal_name(title_key_list, text_data)
                    text_data = indicate_missing_personal_name(text_data)
                    text_data = text_data.replace('"', '\'"\'')
                    write_to_file(fl_wrtr, metadata, text_data)
                    
                #
                column_ctr = 1
                metadata = []
                text_data = []
  
                #
                metadata.append(line_metadata)
                text_data.append(' ' + line_data + ' <NEWLINE>')
                
            else:
            
                #
                metadata.append(line_metadata)
                text_data.append(' ' + line_data + ' <NEWLINE>')
    
    #
    text_data = extract_occupation_and_business(generic_business_list_values, 
                                                occupation_value_list, text_data)
    text_data = extract_single_pair_parentheses(text_data)
    text_data = indicate_missing_spouse_or_business(text_data)
    text_data = extract_personal_name(title_key_list, text_data)
    text_data = indicate_missing_personal_name(text_data)
    text_data = text_data.replace('"', '\'"\'')
    write_to_file(fl_wrtr, metadata, text_data)
    
#
def extract_business(business_list, text_data):
    text_data = ''.join(text_data)
    text_data = ' ' + text_data + ' '
    for i in range(len(business_list)):
        itr0 = re.finditer(' ' + business_list[i] + ' ', text_data)
        itr1 = re.finditer(' ' + business_list[i] + '\t', text_data)
        idx_list0 = [ idx.start() for idx in itr0 ]
        idx_list1 = [ idx.start() for idx in itr1 ]
        idx_list0 = sorted(list(set(idx_list0) | set(idx_list1)))
        for j in range(len(idx_list0)):
            itr1 = re.finditer(' ' + business_list[i] + ' ', text_data)
            itr2 = re.finditer(' ' + business_list[i] + '\t', text_data)
            itr3 = re.finditer(r'<NEWLINE> ' + business_list[i], text_data)
            idx_list1 = [ idx.start() for idx in itr1 ]
            idx_list2 = [ idx.start() for idx in itr2 ]
            idx_list1 = sorted(list(set(idx_list1) | set(idx_list2)))
            idx = idx_list1[j]
            if idx == 0:
                idx = -1
            elif itr3 is not None:
                for idx3 in itr3:
                    if idx3.start() + 9 == idx:
                        idx = -1
            if idx != -1:
                text_data0 = text_data[:idx]
                text_data_tmp = text_data[idx:]
                match = re.search(r' <NEWLINE> ', text_data_tmp)
                text_data1 = text_data_tmp[:match.start()]
                text_data2 = text_data_tmp[match.start():]
                match0 = re.search(r'<RESIDENTIAL ADDRESS>', text_data1)
                match1 = re.search(r'<BUSINESS ADDRESS>', text_data1)
                if match0 is not None:
                    match0 = re.search(r' <', text_data1)
                    match1 = re.search(r'\t', text_data1)
                    str0 = text_data1[:match0.start()]
                    str_tmp = text_data1[match0.start()+1:match1.start()]
                    matchA = re.search(r'<OCCUPATION>', str_tmp)
                    matchB = re.search(r'<BUSINESS>', str_tmp)
                    if matchA is None and matchB is None and \
                       len(str(0)) <= len(business_list[i]) + 2:
                        str1 = ' <BUSINESS>' + str_tmp
                        str2 = text_data1[match1.start():]
                        text_data1 = str1 + '\tNA\t' + str0 + str2
                    text_data = text_data0 + text_data1 + text_data2
                elif match0 is None and match1 is not None:
                    match0 = re.search(r' <BUSINESS ADDRESS>', text_data1)
                    match1 = re.search(r'\t', text_data1)
                    if match0 is not None:
                        str0 = text_data1[:match0.start()]
                        str_tmp = text_data1[match0.start()+1:match1.start()]
                        if len(str(0)) <= len(business_list[i]) + 2:
                            str1 = ' <BUSINESS>' + str_tmp
                            str2 = text_data1[match1.start():]
                            text_data1 = str1 + '\tNA\t' + str0 + str2
                        text_data = text_data0 + text_data1 + text_data2
    text_data = text_data.replace('\t ', '\t')
    text_data = text_data.replace(' \t', '\t')
    text_data = text_data.replace('  ', ' ')
    text_data = text_data[1:-1]
    return text_data
    
#
def extract_occupation(occupation_list, text_data):
    text_data = ''.join(text_data)
    text_data = ' ' + text_data + ' '
    for i in range(len(occupation_list)):
        itr0 = re.finditer(' ' + occupation_list[i] + ' ', text_data)
        itr1 = re.finditer(' ' + occupation_list[i] + '\t', text_data)
        idx_list0 = [ idx.start() for idx in itr0 ]
        idx_list1 = [ idx.start() for idx in itr1 ]
        idx_list0 = sorted(list(set(idx_list0) | set(idx_list1)))
        for j in range(len(idx_list0)):
            itr1 = re.finditer(' ' + occupation_list[i] + ' ', text_data)
            itr2 = re.finditer(' ' + occupation_list[i] + '\t', text_data)
            itr3 = re.finditer(r'<NEWLINE> ' + occupation_list[i], text_data)
            idx_list1 = [ idx.start() for idx in itr1 ]
            idx_list2 = [ idx.start() for idx in itr2 ]
            idx_list1 = sorted(list(set(idx_list1) | set(idx_list2)))
            idx = idx_list1[j]
            if idx == 0:
                idx = -1
            elif itr3 is not None:
                for idx3 in itr3:
                    if idx3.start() + 9 == idx:
                        idx = -1
            if idx != -1:
                text_data0 = text_data[:idx]
                text_data_tmp = text_data[idx:]
                match = re.search(r' <NEWLINE> ', text_data_tmp)
                text_data1 = text_data_tmp[:match.start()]
                text_data2 = text_data_tmp[match.start():]
                match = re.search(r'<RESIDENCE TYPE>', text_data1)
                if match is not None:
                    match0 = re.search(r' <', text_data1)
                    match1 = re.search(r'\t', text_data1)
                    str0 = text_data1[:match0.start()]
                    str_tmp = text_data1[match0.start()+1:match1.start()]
                    match = re.search(r' <OCCUPATION>', str_tmp)
                    if match is None:
                        str1 = ' <OCCUPATION>' + str_tmp
                        str2 = text_data1[match1.start():]
                        str0a = str0[:len(occupation_list[i])+2]
                        str0b = str0[len(occupation_list[i])+2:]
                        if len(str0b) > 0:
                            str1 = ' <OCCUPATION><BUSINESS>' + str_tmp
                        else:
                            str1 = ' <OCCUPATION>' + str_tmp
                            str0b = 'NA'
                        text_data1 = str1 + '\t' + str0a + '\t' + str0b + str2
                    text_data = text_data0 + text_data1 + text_data2
    text_data = text_data.replace('\t ', '\t')
    text_data = text_data.replace(' \t', '\t')
    text_data = text_data.replace('  ', ' ')
    text_data = text_data[1:-1]
    return text_data

#
def extract_occupation_and_business(business_value_list, occupation_value_list, text_data):
    text_data = extract_occupation(occupation_value_list, text_data)
    text_data = extract_business(business_value_list, text_data)
    text_data = extract_second_set_parentheses(text_data)
    text_data = indicate_missing_occupation_or_business(text_data)
    return text_data

#
def extract_personal_name(title_key_list, text_data):
    text_data = ' ' + text_data + ' '
    idx_list0 = []
    for i in range(len(title_key_list)+1):
        if i == 0:
            itr0 = re.finditer(r'> (\"|[A-Za-z]+) <', text_data)
            itr1 = re.finditer(r'> (\"|[A-Za-z]+) [A-Za-z]+ <', text_data)
            itr2 = re.finditer(r'> (\"|[A-Za-z]+) [A-Za-z]+ [A-Z] <', text_data)
            itr3 = re.finditer(r'> (\"|[A-Za-z]+) [A-Z] [A-Za-z]+ <', text_data)
            itr4 = re.finditer(r'> (\"|[A-Za-z]+) [A-Za-z]+ [A-Z] [A-Z] <', text_data)
        else:
            title_key = title_key_list[i-1]
            itr0 = re.finditer(r'> (\"|[A-Za-z]+)' + title_key + '<', text_data)
            itr1 = re.finditer(r'> (\"|[A-Za-z]+) [A-Za-z]+' + title_key + '<', text_data)
            itr2 = re.finditer(r'> (\"|[A-Za-z]+) [A-Za-z]+ [A-Z]' + title_key + '<', text_data)
            itr3 = re.finditer(r'> (\"|[A-Za-z]+) [A-Z] [A-Za-z]+' + title_key + '<', text_data)
            itr4 = re.finditer(r'> (\"|[A-Za-z]+) [A-Za-z]+ [A-Z] [A-Z]' + title_key + '<', text_data)
        idx_list1 = [ idx.start() for idx in itr0 ]
        idx_list2 = [ idx.start() for idx in itr1 ]
        idx_list3 = [ idx.start() for idx in itr2 ]
        idx_list4 = [ idx.start() for idx in itr3 ]
        idx_list5 = [ idx.start() for idx in itr4 ]
        idx_list0 = sorted(list(set(idx_list0) | set(idx_list1) | \
                                set(idx_list2) | set(idx_list3) | \
                                set(idx_list4)|  set(idx_list5)))
    for _ in idx_list0:
        idx_list1 = []
        for i in range(len(title_key_list)+1):
            if i == 0:
                itr1 = re.finditer(r'> (\"|[A-Za-z]+) <', text_data)
                itr2 = re.finditer(r'> (\"|[A-Za-z]+) [A-Za-z]+ <', text_data)
                itr3 = re.finditer(r'> (\"|[A-Za-z]+) [A-Za-z]+ [A-Z] <', text_data)
                itr4 = re.finditer(r'> (\"|[A-Za-z]+) [A-Z] [A-Za-z]+ <', text_data)
                itr5 = re.finditer(r'> (\"|[A-Za-z]+) [A-Za-z]+ [A-Z] [A-Z] <', text_data)
            else:
                title_key = title_key_list[i-1]
                itr1 = re.finditer(r'> (\"|[A-Za-z]+)' + title_key + '<', text_data)
                itr2 = re.finditer(r'> (\"|[A-Za-z]+) [A-Za-z]+' + title_key + '<', text_data)
                itr3 = re.finditer(r'> (\"|[A-Za-z]+) [A-Za-z]+ [A-Z]' + title_key + '<', text_data)
                itr4 = re.finditer(r'> (\"|[A-Za-z]+) [A-Z] [A-Za-z]+' + title_key + '<', text_data)
                itr5 = re.finditer(r'> (\"|[A-Za-z]+) [A-Za-z]+ [A-Z] [A-Z]' + title_key + '<', text_data)
            idx_list2 = [ idx.start()+1 for idx in itr1 ]
            idx_list3 = [ idx.start()+1 for idx in itr2 ]
            idx_list4 = [ idx.start()+1 for idx in itr3 ]
            idx_list5 = [ idx.start()+1 for idx in itr4 ]
            idx_list6 = [ idx.start()+1 for idx in itr5 ]
            idx_list1 = sorted(list(set(idx_list1) | set(idx_list2) | \
                                    set(idx_list3) | set(idx_list4) | \
                                    set(idx_list5) | set(idx_list6)))
        text_data0 = text_data[:idx_list1[0]]
        text_data_tmp = text_data[idx_list1[0]:]
        match = re.search(r' <NEWLINE> ', text_data_tmp)
        text_data1 = text_data_tmp[:match.start()]
        text_data2 = text_data_tmp[match.start():]
        match = re.search(r'<RESIDENCE TYPE>', text_data1)
        if match is not None:
            match0 = re.search(r' <', text_data1)
            match1 = re.search(r'\t', text_data1)
            str0 = text_data1[1:match0.start()]
            str1 = ' <PERSONAL NAME>' + text_data1[match0.start()+1:match1.start()]
            str2 = text_data1[match1.start():]
            text_data1 = str1 + '\t' + str0 + str2
            text_data = text_data0 + text_data1 + text_data2
        else:
            text_data = text_data0 + '!!!' + text_data1 + text_data2
    text_data = text_data.replace('!!!', '')
    text_data = text_data.replace('  ', ' ')
    text_data = text_data[1:-1]
    return text_data

#
def extract_second_set_parentheses(text_data):
    text_data = ' ' + text_data + ' '
    itr = re.finditer(r'\) \(', text_data)
    idx_list = [ idx.start() for idx in itr ]
    for _ in range(len(idx_list)):
        match = re.search(r'\) \(', text_data)
        if match is not None:
            text_data0 = text_data[:match.start()+1]
            text_data_tmp = text_data[match.start()+2:]
            match = re.search(r' <NEWLINE> ', text_data_tmp)
            text_data1 = text_data_tmp[:match.start()]
            text_data2 = text_data_tmp[match.start():]
            match0 = re.search(r'<RESIDENCE TYPE>', text_data1)
            match1 = re.search(r'<BUSINESS>', text_data1)
            if match0 is not None and match1 is None:
                match = re.search(r'\) \(', text_data1)
                if match is None:
                    match0 = re.search(r'\)', text_data1)
                    match1 = re.search(r'\t', text_data1)
                    if match0 is not None and match1 is not None and \
                       match0.start() < match1.start():
                        str0 = text_data1[1:match0.start()]
                        match0 = re.search(r' <', text_data1)
                        match1 = re.search(r'\t', text_data1)
                        str1 = ' <BUSINESS>' + text_data1[match0.start()+1:match1.start()]
                        str2 = text_data1[match1.start():]
                        text_data1 = str1 + '\tNA\t' + str0 + str2
                        text_data = text_data0 + text_data1 + text_data2
    text_data = text_data.replace('  ', ' ')
    text_data = text_data[1:-1]
    return text_data

#
def extract_single_pair_parentheses(text_data):
    text_data = ' ' + text_data + ' '
    itr = re.finditer(r' \(', text_data)
    idx_list = [ idx.start() for idx in itr ]
    for _ in range(len(idx_list)):
        match = re.search(r' \(', text_data)
        if match is not None:
            text_data0 = text_data[:match.start()+1]
            text_data_tmp = text_data[match.start()+1:]
            match = re.search(r' <NEWLINE> ', text_data_tmp)
            text_data1 = text_data_tmp[:match.start()]
            text_data2 = text_data_tmp[match.start():]
            match0 = re.search(r'<RESIDENCE TYPE>', text_data1)
            match1 = re.search(r'\) <', text_data1)
            if match0 is not None and match1 is not None:
                itr0 = re.finditer(r'\(', text_data1)
                itr1 = re.finditer(r'\)', text_data1)
                idx_list0 = [ idx.start() for idx in itr0 if idx.start() <= match1.start() ]
                idx_list1 = [ idx.start() for idx in itr1 if idx.start() <= match1.start() ]
                if len(idx_list0) == 1 and len(idx_list1) == 1:
                    match0 = re.search(r'\)', text_data1)
                    match1 = re.search(r'<', text_data1)
                    match2 = re.search(r'\t', text_data1)
                    str0 = text_data1[1:match0.start()]
                    str1 = '<SPOUSE OR BUSINESS>' + text_data1[match1.start():match2.start()]
                    str2 = text_data1[match2.start():]
                    text_data1 = str1 + '\t' + str0 + str2
                    text_data = text_data0 + text_data1 + text_data2
                else:
                    text_data1 = text_data1.replace('(', '!!!(')
                    text_data = text_data0 + text_data1 + text_data2
            else:
                text_data = text_data0 + '!!!' + text_data1 + text_data2
    text_data = text_data.replace('!!!', '')
    text_data = text_data.replace('  ', ' ')
    text_data = text_data[1:-1]
    return text_data

#
def indicate_missing_occupation_or_business(text_data_in):
    text_data_in = ' ' + text_data_in + ' '
    itr0 = re.finditer(r' <NEWLINE> ', text_data_in)
    idx_list0 = [ idx.start() for idx in itr0 ]
    text_data_out = ''
    for i in range(len(idx_list0)):
        itr1 = re.finditer(r' <NEWLINE> ', text_data_in)
        idx_list1 = [ idx.start() for idx in itr1 ]
        line_data = text_data_in[:idx_list1[0]+11]
        text_data_in = text_data_in[idx_list1[0]+11:]
        match0 = re.search(r'<OCCUPATION>', line_data)
        match1 = re.search(r'<BUSINESS>', line_data)
        if match0 is None and match1 is None:
            sub_match = re.search(r'\t', line_data)
            str0 = line_data[:sub_match.start()]
            str1 = '\tNA\tNA' + line_data[sub_match.start():]
            line_data = str0 + str1
        text_data_out += line_data
    text_data_out += text_data_in
    text_data_out = text_data_out[1:-1]
    return text_data_out

#
def indicate_missing_spouse_or_business(text_data_in):
    text_data_in = ' ' + text_data_in + ' '
    itr0 = re.finditer(r' <NEWLINE> ', text_data_in)
    idx_list0 = [ idx.start() for idx in itr0 ]
    text_data_out = ''
    for i in range(len(idx_list0)):
        itr1 = re.finditer(r' <NEWLINE> ', text_data_in)
        idx_list1 = [ idx.start() for idx in itr1 ]
        line_data = text_data_in[:idx_list1[0]+11]
        text_data_in = text_data_in[idx_list1[0]+11:]
        match = re.search(r'<SPOUSE OR BUSINESS>', line_data)
        if match is None:
            sub_match = re.search(r'\t', line_data)
            str0 = line_data[:sub_match.start()]
            str1 = '\tNA' + line_data[sub_match.start():]
            line_data = str0 + str1
        text_data_out += line_data
    text_data_out += text_data_in
    text_data_out = text_data_out[1:-1]
    return text_data_out

#
def indicate_missing_personal_name(text_data_in):
    text_data_in = ' ' + text_data_in + ' '
    itr0 = re.finditer(r' <NEWLINE> ', text_data_in)
    idx_list0 = [ idx.start() for idx in itr0 ]
    text_data_out = ''
    for i in range(len(idx_list0)):
        itr1 = re.finditer(r' <NEWLINE> ', text_data_in)
        idx_list1 = [ idx.start() for idx in itr1 ]
        line_data = text_data_in[:idx_list1[0]+11]
        text_data_in = text_data_in[idx_list1[0]+11:]
        match = re.search(r'<PERSONAL NAME>', line_data)
        if match is None:
            sub_match = re.search(r'\t', line_data)
            str0 = line_data[:sub_match.start()]
            str1 = '\tNA' + line_data[sub_match.start():]
            line_data = str0 + str1
        text_data_out += line_data
    text_data_out += text_data_in
    text_data_out = text_data_out[1:-1]
    return text_data_out
        
#
def write_to_file(fl_wrtr, metadata, text_data):
    text_data = text_data[1:len(text_data)-10]
    itr = re.finditer(r' <NEWLINE> ', text_data)
    idxs = [idx.start() for idx in itr]
    idxs = idxs + [0]
    idxs = idxs + [len(text_data)]
    idxs = sorted(idxs)
    text_data_out = []
    for i in range(len(metadata)):
        line_metadata = metadata[i]
        if i == 0:
            text_data_out.append(line_metadata + '\t' + text_data[idxs[i]:idxs[i+1]] + '\n')
        else:
            text_data_out.append(line_metadata + '\t' + text_data[idxs[i]+11:idxs[i+1]] + '\n')
    fl_wrtr.run(text_data_out)