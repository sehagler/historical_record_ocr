# Imports
import getopt
import os
from os import makedirs
from shutil import copyfile
import sys

# Local Imports
sys.path.insert(0, 'py/hr_tools')
from correct_entries import correct_entries
from correct_text_table import correct_text_table
from encode_text_table import encode_text_table
from file_writer import file_writer
from json_to_text_table import json_to_text_table
from text_table_to_entries import text_table_to_entries

#
def hr_text_builder(api_key, automated_segmentation_flg, ditto_correction_flg, pdf_dir, 
                    sect_dir, pdf_name, pdf_city, pdf_year, dpi_flg, num_cols, pages,
                    segment_map_list):
    
    #
    segment_filename_base = 'column_'

    #
    pdf_file = pdf_dir + pdf_name

    #
    directory_dir = sect_dir
    makedirs(directory_dir, exist_ok=True)

    #
    directory_pdf_dir = directory_dir + 'pdf/'
    makedirs(directory_pdf_dir, exist_ok=True)

    #
    directory_pdf_file = directory_pdf_dir + pdf_name
    try:
        copyfile(pdf_file, directory_pdf_file)
    except:
        pass

    #
    directory_pages_dir = directory_dir + 'pages/'
    makedirs(directory_pages_dir, exist_ok=True)

    #
    directory_txt_dir = directory_dir + 'txt/'
    makedirs(directory_txt_dir, exist_ok=True)
    directory_txt_file = directory_txt_dir + pdf_name[:len(pdf_name)-4] + '0.txt'
    
    #
    for page in pages:

        #
        page_json_dir = directory_pages_dir + 'page_' + str(page) + '/json/'
        makedirs(page_json_dir, exist_ok=True)
        
        #
        page_npy_dir = directory_pages_dir + 'page_' + str(page) + '/npy/'
        makedirs(page_npy_dir, exist_ok=True)
        
        #
        page_png_dir = directory_pages_dir + 'page_' + str(page) + '/png/'
        makedirs(page_png_dir, exist_ok=True)
        
    #
    reconstruct_document(directory_txt_file, pages, segment_map_list, directory_pages_dir,
                         ditto_correction_flg, segment_filename_base, pdf_name, pdf_city,
                         pdf_year)
                        
#
def reconstruct_document(directory_txt_file, pages, segment_map_list, directory_pages_dir,
                         ditto_correction_flg, segment_filename_base, pdf_name, pdf_city,
                         pdf_year):

    #
    print("\nProcess JSONs:\n")
    
    #
    fl_wrtr = file_writer(directory_txt_file)
    
    # Read text from JSONs
    failed_pages = []
    summary_pages = []
    for i in range(len(pages)):

        #
        page = pages[i]
        segment_map = segment_map_list[i]
        
        #
        if page % 20 == 0 or page == pages[-1]:
            print(page)
        else:
            print("%d " % page, end="")
        
        #
        page_json_dir = directory_pages_dir + 'page_' + str(page) + '/json/'
        page_npy_dir = directory_pages_dir + 'page_' + str(page) + '/npy/'
        page_png_dir = directory_pages_dir + 'page_' + str(page) + '/png/'
            
        #
        if len(segment_map) > 0:
            
            if True:
            
                #
                entries, num_lines, num_dittos = \
                    unsegment_page(ditto_correction_flg, segment_map, page_json_dir, page_png_dir,
                                   segment_filename_base, page)
                
                #
                num_entries = []
                for i in range(len(entries)):
                    num_entries.append(len(entries[i]))
                summary_pages.append([ page, num_lines, num_entries, num_dittos ])
                
                #
                full_entries = []
                for i in range(len(entries)):
                    full_entries_tmp = []
                    for entry in entries[i]:
                        entry_str = pdf_name + '\t' + pdf_city + '\t' + str(pdf_year) + '\t' \
                                    + str(page) + '\t' + str(i+1) + '\t' + entry + '\n'
                        entry_str = ''.join(entry_str)
                        full_entries_tmp.append(entry_str)
                    full_entries.append(full_entries_tmp)
                       
                #
                for i in range(len(full_entries)):
                    fl_wrtr.run(full_entries[i])
                
        else:
                
            failed_pages.append(page)
            print('Image segmentation failed.')
            
#
def unsegment_column(segment_map, page_json_dir, page_png_dir, segment_filename_base):

    #
    text_table = []
    start_idx = segment_map[1]
    for i in range(segment_map[1],segment_map[2]):

        #
        json_filename = page_json_dir + segment_filename_base + str(i) + '.json'
        png_filename = page_png_dir + segment_filename_base + str(i) + '.png'
        
        #
        json_to_txt_tbl = json_to_text_table()
        text_table_tmp = json_to_txt_tbl.run(json_filename)
        text_table.append(encode_text_table().run(text_table_tmp))
        
    #
    return text_table

#
def unsegment_page(ditto_correction_flg, segment_map, page_png_dir, 
                   page_json_dir, segment_filename_base, page_num):
    
    #
    entries = []
    num_dittos = []
    num_lines = []
    for i in range(len(segment_map)):
                
        #
        text_table = unsegment_column(segment_map[i], page_png_dir, page_json_dir,
                                      segment_filename_base)
        if ditto_correction_flg:
            text_table = correct_text_table(text_table)

        #
        entries_tmp, num_lines_tmp, num_dittos_tmp = \
            text_table_to_entries().run(text_table)
        if ditto_correction_flg:
            entries_tmp = correct_entries(entries_tmp)
        
        #
        entries.append(entries_tmp)
        num_lines.append(num_lines_tmp)
        num_dittos.append(num_dittos_tmp)
        
    #
    return entries, num_lines, num_dittos