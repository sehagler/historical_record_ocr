# Imports
import getopt
import os
from os import makedirs
from shutil import copyfile
import sys

# Local Imports
from correct_entries import correct_entries
from correct_text_table import correct_text_table
from encode_text_table import encode_text_table
from file_writer import file_writer
from json_to_text_table import json_to_text_table
from pdf_page_to_segment_jpgs import pdf_page_to_segment_jpgs
from preliminary_stats import preliminary_stats
from segment_jpg_to_segment_json import segment_jpg_to_segment_json
from text_table_to_entries import text_table_to_entries

#
def hr_reader(api_key, pdf_dir, pdf_name, dpi_flg, num_cols, pages):
    
    #
    segment_filename_base = 'segment_'
    gcv_url = 'https://vision.googleapis.com/v1/images:annotate'
    gs_exe = 'C:/Program Files/gs/gs9.21/bin/gswin64c'

    #
    pdf_file = pdf_dir + pdf_name

    #
    directory_dir = os.getcwd() + '/' + pdf_name[:len(pdf_name)-4] + '/'
    makedirs(directory_dir, exist_ok=True)

    #
    directory_pdf_dir = directory_dir + '/pdf/'
    makedirs(directory_pdf_dir, exist_ok=True)

    #
    directory_pdf_file = directory_pdf_dir + pdf_name
    copyfile(pdf_file, directory_pdf_file)

    #
    directory_pages_dir = directory_dir + '/pages/'
    makedirs(directory_pages_dir, exist_ok=True)

    #
    directory_txt_dir = directory_dir + '/txt/'
    makedirs(directory_txt_dir, exist_ok=True)
    directory_txt_file = directory_txt_dir + pdf_name[:len(pdf_name)-4] + '.txt'
    
    #
    prelim_info = pdf_page_to_segment_jpgs(0, gs_exe, directory_pages_dir, num_cols, dpi_flg, 
                                          directory_pdf_file, segment_filename_base, 0, 0)
    
    #
    column_widths = []
    cut_widths = []
    selected_column_widths = [] 
    for page in pages:
        
        #
        if page % 20 == 0 or page == pages[-1]:
            print(page)
        else:
            print("%d " % page, end="")
            
        #
        column_widths_tmp, cut_widths_tmp, selected_column_widths_tmp = \
            prelim_info.run(page, ' ')
        for column_width in column_widths_tmp:
            column_widths.append(column_width)
        cut_widths.append(cut_widths_tmp)
        for selected_column_width in selected_column_widths_tmp:
            selected_column_widths.append(selected_column_width)
            
    #
    mean_trimmed_selected_column_widths, std_trimmed_selected_column_widths = \
        preliminary_stats(column_widths, cut_widths, selected_column_widths)

    #
    pg_to_jpgs = pdf_page_to_segment_jpgs(1, gs_exe, directory_pages_dir, num_cols, 
                                          dpi_flg, directory_pdf_file, segment_filename_base,
                                          mean_trimmed_selected_column_widths,
                                          std_trimmed_selected_column_widths)
    jpg_to_json = segment_jpg_to_segment_json(gcv_url, api_key)
    fl_wrtr = file_writer(directory_txt_file)

    # Read pages from PDF
    failed_pages = []
    summary_pages = []
    for page in pages:
        
        #
        if page % 20 == 0 or page == pages[-1]:
            print(page)
        else:
            print("%d " % page, end="")

        #
        segment_jpgs_dir = directory_pages_dir + 'page_' + str(page) + '_segments/jpgs/'
        makedirs(segment_jpgs_dir, exist_ok=True)

        #
        segment_jsons_dir = directory_pages_dir + 'page_' + str(page) + '_segments/jsons/'
        makedirs(segment_jsons_dir, exist_ok=True)

        #
        segment_map = segment_page(pg_to_jpgs, page, segment_jpgs_dir, 
                                   mean_trimmed_selected_column_widths,
                                   std_trimmed_selected_column_widths)
        
        #
        if len(segment_map) > 0:
            
            if False:
            
                #
                entries, num_lines, num_dittos = \
                    unsegment_page(jpg_to_json, segment_map, segment_jpgs_dir, 
                                   segment_jsons_dir, segment_filename_base,page)
                
                #
                num_entries = []
                for i in range(len(entries)):
                    num_entries.append(len(entries[i]))
                summary_pages.append([ page, num_lines, num_entries, num_dittos ])
                       
                #
                for i in range(len(entries)):
                    fl_wrtr.run(pdf_name, page, i+1, entries[i])
                
        else:
                
            failed_pages.append(page)
            print('Image segmentation failed.')
            
    print(failed_pages)
    print(summary_pages)
            
#
def segment_page(pg_to_jpgs, page_num, segment_jpgs_dir, 
                 mean_trimmed_selected_column_widths,
                 std_trimmed_selected_column_widths):

    #
    segment_map = pg_to_jpgs.run(page_num, segment_jpgs_dir)
    
    #
    return segment_map
            
#
def unsegment_column(jpg_to_json, segment_map, segment_jpgs_dir, segment_jsons_dir, segment_filename_base):

    #
    text_table = []
    start_idx = segment_map[1]
    for i in range(segment_map[1],segment_map[2]):

        #
        jpg_filename = segment_jpgs_dir + segment_filename_base + str(i) + '.jpg'
        json_filename = segment_jsons_dir + segment_filename_base + str(i) + '.json'

        #
        #jpg_to_json.do_ocr(jpg_filename, json_filename)
        
        #
        json_to_txt_tbl = json_to_text_table()
        if i == start_idx:
            first_segment_flg = True
        else:
            first_segment_flg = False
        first_segment_flg
        text_table_tmp = json_to_txt_tbl.run(first_segment_flg, json_filename)
        text_table.append(encode_text_table().run(text_table_tmp))
        
    #
    return text_table

#
def unsegment_page(jpg_to_json, segment_map, segment_jpgs_dir, segment_jsons_dir, 
                   segment_filename_base, page_num):
    
    #
    entries = []
    num_dittos = []
    num_lines = []
    for i in range(len(segment_map)):
                
        #
        text_table = unsegment_column(jpg_to_json, segment_map[i], segment_jpgs_dir, 
                                      segment_jsons_dir, segment_filename_base)
        text_table = correct_text_table(text_table)

        #
        entries_tmp, num_lines_tmp, num_dittos_tmp = \
            text_table_to_entries().run(text_table)
        #entries_tmp = correct_entries(entries_tmp)
        
        #
        entries.append(entries_tmp)
        num_lines.append(num_lines_tmp)
        num_dittos.append(num_dittos_tmp)
        
    #
    return entries, num_lines, num_dittos