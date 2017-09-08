# Imports
import getopt
import os
from os import makedirs
from shutil import copyfile
import sys

# Local Imports
from encode_text_table import encode_text_table
from json_to_text_table import json_to_text_table
from pdf_page_to_segment_jpgs import pdf_page_to_segment_jpgs
from segment_entries import segment_entries
from segment_jpg_to_segment_json import segment_jpg_to_segment_json
from text_table_to_entries import text_table_to_entries

#
def hr_reader(api_key, pdf_dir, pdf_name, dpi_flg, num_cols, pages):
    
    opts, args = getopt.getopt(argv)
    print(opts)
    print(args)
    
    #
    segment_filename_base = 'segment_'
    gcv_url = 'https://vision.googleapis.com/v1/images:annotate'
    gs_exe = 'C:/Program Files/gs/gs9.21/bin/gswin64'

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
    pg_to_jpgs = pdf_page_to_segment_jpgs(gs_exe, directory_pages_dir, num_cols, dpi_flg, 
                                          directory_pdf_file, segment_filename_base)
    jpg_to_json = segment_jpg_to_segment_json(gcv_url, api_key)

    # Read pages from PDF
    for page in pages:

        #
        page_num = page + 1

        #
        segment_jpgs_dir = directory_pages_dir + 'page_' + str(page_num) + '_segments/jpgs/'
        makedirs(segment_jpgs_dir, exist_ok=True)

        #
        segment_jsons_dir = directory_pages_dir + 'page_' + str(page_num) + '_segments/jsons/'
        makedirs(segment_jsons_dir, exist_ok=True)

        print(page_num)

        #
        segment_map = segment_page(pg_to_jpgs, page_num, segment_jpgs_dir)
        
        #
        if False:
            
            unsegment_page(jpg_to_json, segment_map, segment_jpgs_dir, 
                           segment_jsons_dir, segment_filename_base,
                           directory_txt_file, pdf_name, page_num)
            
#
def segment_page(pg_to_jpgs, page_num, segment_jpgs_dir):

    #
    segment_map = pg_to_jpgs.run(page_num, segment_jpgs_dir)
    
    #
    return segment_map
            
#
def unsegment_column(jpg_to_json, segment_map, segment_jpgs_dir, segment_jsons_dir, segment_filename_base):

    #
    text_table = []
    for i in range(segment_map[1],segment_map[2]):

        #
        jpg_filename = segment_jpgs_dir + segment_filename_base + str(i) + '.jpg'
        json_filename = segment_jsons_dir + segment_filename_base + str(i) + '.json'

        #
        jpg_to_json.do_ocr(jpg_filename, json_filename)
        text_table_tmp = json_to_text_table().run(json_filename)
        text_table.append(encode_text_table().run(text_table_tmp))
        
    #
    return text_table

#
def unsegment_page(jpg_to_json, segment_map, segment_jpgs_dir, segment_jsons_dir, 
                   segment_filename_base, directory_txt_file, pdf_name, page_num):
    
    #
    for i in range(len(segment_map)):
                
        #
        column_num = i + 1
        text_table = unsegment_column(jpg_to_json, segment_map[i], segment_jpgs_dir, 
                                      segment_jsons_dir, segment_filename_base)

        #
        entries = text_table_to_entries().run(text_table)
        seg_entries = segment_entries(directory_txt_file)
        seg_entries.run(pdf_name, page_num, column_num, entries)