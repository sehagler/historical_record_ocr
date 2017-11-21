# Imports
import sys

# Local Imports
sys.path.insert(0, 'py/hr_reader')
sys.path.insert(0, 'py/hr_text_builder')
sys.path.insert(0, 'py/hr_text_corrector')
sys.path.insert(0, 'py/hr_text_segmenter')
from hr_reader import hr_reader
from hr_text_builder import hr_text_builder
from hr_text_corrector1 import hr_text_corrector1
from hr_text_corrector2 import hr_text_corrector2
from hr_text_segmenter import hr_text_segmenter

#
def hr_main(api_key,  pdf_automated_segmentation_flg, pdf_city, pdf_year, dpi_flg, num_cols, pdf_dir, 
            pdf_name, pdf_pages, xlsx_dir, xlsx_first_name_abbr, xlsx_general_abbr, xlsx_occupation_abbr, 
            workspace):
    
    #
    #ditto_correction_flg = False
    #sect_dir = workspace + 'SECTION1/'
    
    #
    #business_segment_map_list =hr_reader(api_key, business_automated_segmentation_flg,
    #                                     ditto_correction_flg, business_pdf_dir,
    #                                     sect_dir, business_pdf_name, pdf_city, pdf_year, 
    #                                     dpi_flg, num_cols, business_pages)
    
    #
    ditto_correction_flg = True
    sect_dir = workspace + 'SECTION2/'
    
    #
    pdf_segment_map_list = hr_reader(api_key, pdf_automated_segmentation_flg,
                                         ditto_correction_flg, pdf_dir, sect_dir,
                                         pdf_name, pdf_city, pdf_year, dpi_flg, num_cols,
                                         pdf_pages)
    if True:
    
        #
        #hr_text_builder(api_key, business_automated_segmentation_flg, ditto_correction_flg,
        #                business_pdf_dir, sect_dir, business_pdf_name, pdf_city, pdf_year, dpi_flg,
        #                num_cols, business_pages, business_segment_map_list)

        #
        hr_text_builder(api_key, pdf_automated_segmentation_flg, ditto_correction_flg,
                        pdf_dir, sect_dir, pdf_name, pdf_city, pdf_year, dpi_flg,
                        num_cols, pdf_pages, pdf_segment_map_list)

    #
    hr_text_corrector1(sect_dir, pdf_name)
    hr_text_segmenter(sect_dir, pdf_name)
    hr_text_corrector2(sect_dir, pdf_name, xlsx_dir, xlsx_first_name_abbr, xlsx_general_abbr, xlsx_occupation_abbr)