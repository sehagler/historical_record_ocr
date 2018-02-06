# Imports
import getopt
import os
from os import makedirs
from shutil import copyfile
import sys

# Local Imports
from pdf_page_to_segment_pngs import pdf_page_to_segment_pngs
from preliminary_stats import preliminary_stats
from segment_png_to_segment_json import segment_png_to_segment_json

#
def hr_reader(api_key, automated_segmentation_flg, ditto_correction_flg, pdf_dir, 
              sect_dir, pdf_name, pdf_city, pdf_year, dpi_flg, num_cols, pages):
    
    #
    segment_filename_base = 'column_'
    gcv_url = 'https://vision.googleapis.com/v1/images:annotate'
    gs_exe = 'C:/Program Files/gs/gs9.21/bin/gswin64c'

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
    directory_txt_file = directory_txt_dir + pdf_name[:len(pdf_name)-4] + '.txt'
    
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
    
    # Read and segment PDF pages
    if automated_segmentation_flg:
        segment_map_list = \
            automated_page_segmentation(gs_exe, directory_pages_dir, num_cols, dpi_flg,
                                        directory_pdf_file, segment_filename_base, pages,
                                        directory_txt_file)
    else:
        segment_map_list = manual_page_segmentation(pages, num_cols)
        
    # OCR page segments
    if False:
        ocr_segments(pages, segment_map_list, directory_pages_dir, gcv_url, api_key,
                     segment_filename_base)
        
    #
    return segment_map_list
    
#
def automated_page_segmentation(gs_exe, directory_pages_dir, num_cols, dpi_flg, directory_pdf_file,
                                segment_filename_base, pages, directory_txt_file):

    
    #
    print("\nAUTOMATED PAGE SEGMENTATION\n")
    print("Preliminary Page Segmentation:\n")

    #
    prelim_run = pdf_page_to_segment_pngs(0, gs_exe, directory_pages_dir, num_cols, dpi_flg, 
                                          directory_pdf_file, segment_filename_base, 0, 0, 0, 0)

    #
    selected_column_heights = []
    selected_column_widths = [] 
    for page in pages:

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
        selected_column_widths_tmp, selected_column_heights_tmp = \
            prelim_run.run(page, page_png_dir, page_npy_dir)
        for selected_column_width in selected_column_widths_tmp:
            selected_column_widths.append(selected_column_width)
        for selected_column_height in selected_column_heights_tmp:
            selected_column_heights.append(selected_column_height)

    #
    mean_trimmed_selected_column_widths, std_trimmed_selected_column_widths, \
    mean_trimmed_selected_column_heights, std_trimmed_selected_column_heights = \
         preliminary_stats(selected_column_widths, selected_column_heights)

    #
    print("\nPage Segmentation:\n")

    #
    segment_run = pdf_page_to_segment_pngs(1, gs_exe, directory_pages_dir, num_cols, 
                                           dpi_flg, directory_pdf_file, segment_filename_base,
                                           mean_trimmed_selected_column_widths,
                                           std_trimmed_selected_column_widths,
                                           mean_trimmed_selected_column_heights,
                                           std_trimmed_selected_column_heights)

    # Read pages from PDF
    segment_map_list = []
    for page in pages:

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
        segment_map = segment_page(segment_run, page, page_npy_dir, page_png_dir, 
                                   mean_trimmed_selected_column_widths,
                                   std_trimmed_selected_column_widths)
        segment_map_list.append(segment_map)
        
    #
    return segment_map_list

#
def manual_page_segmentation(pages, num_cols):

    #
    print("\nMANUAL PAGE SEGMENTATION\n")
    print("Construct Segment Maps:\n")

    # Construct segment maps
    segment_map_list = []
    for page in pages:

        #
        if page % 20 == 0 or page == pages[-1]:
            print(page)
        else:
            print("%d " % page, end="")

        #
        segment_map = []
        for i in range(num_cols):
            segment_map.append([i, i, i+1])
        segment_map_list.append(segment_map)
        
    #
    return segment_map_list

#
def ocr_segments(pages, segment_map_list, directory_pages_dir, gcv_url, api_key,
                 segment_filename_base):
    
    #
    print("\nOCR Segments:\n")

    # OCR segment image files
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
                for j in range(len(segment_map)):
                    for k in range(segment_map[j][1],segment_map[j][2]):

                        #
                        json_filename = page_json_dir + segment_filename_base + str(k) + '.json'
                        png_filename = page_png_dir + segment_filename_base + str(k) + '.png'

                        #
                        png_to_json = segment_png_to_segment_json(gcv_url, api_key)
                        png_to_json.do_ocr(png_filename,json_filename)
            
#
def segment_page(pg_to_jpgs, page_num, page_npy_dir, page_png_dir, 
                 mean_trimmed_selected_column_widths,
                 std_trimmed_selected_column_widths):

    #
    segment_map = pg_to_jpgs.run(page_num, page_png_dir, page_npy_dir)
    
    #
    return segment_map