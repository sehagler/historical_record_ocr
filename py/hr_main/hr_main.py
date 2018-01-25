# Imports
import sys

# Local Imports
sys.path.insert(0, 'py/hr_evaluation')
sys.path.insert(0, 'py/hr_reader')
sys.path.insert(0, 'py/hr_text_builder')
sys.path.insert(0, 'py/hr_text_corrector')
sys.path.insert(0, 'py/hr_text_segmenter')
sys.path.insert(0, 'py/hr_tools')
sys.path.insert(0, 'xlsx')
from abbr_dict import abbr_dict, abbr_dict_occupations, get_key_list, get_value_list, get_value_list_occupations
from hr_evaluation import hr_evaluation
from hr_reader import hr_reader
from hr_text_builder import hr_text_builder
from hr_text_corrector1 import hr_text_corrector1
from hr_text_corrector2 import hr_text_corrector2
from hr_text_corrector3 import hr_text_corrector3
from hr_text_corrector4 import hr_text_corrector4
from hr_text_segmenter1 import hr_text_segmenter1
from hr_text_segmenter2 import hr_text_segmenter2


#
def hr_main(api_key,  pdf_automated_segmentation_flg, pdf_city, pdf_year, dpi_flg, columns_per_page, 
            pdf_dir, pdf_name, pdf_pages, workspace):
    
    #
    ditto_correction_flg = True
    pages_per_iteration = 5
    sect_dir = workspace + 'SECTION2/'
    
    #
    xlsx_dir = 'xlsx/'
    xlsx_business_abbr = 'business_abbreviations.xlsx'
    xlsx_first_name_abbr = 'first_name_abbreviations.xlsx'
    xlsx_general_abbr = 'general_abbreviations.xlsx'
    xlsx_occupation_abbr = 'occupation_abbreviations.xlsx'
    xlsx_occupation_tag_abbr = 'occupation_tag_abbreviations.xlsx'
    xlsx_special_abbr = 'special_abbreviations.xlsx'
    xlsx_title_abbr = 'title_abbreviations.xlsx'
    
    #
    xlsx_file = xlsx_dir + xlsx_business_abbr
    business_abbr_dict_both_2 = abbr_dict(False, 2, xlsx_file)
    xlsx_file = xlsx_dir + xlsx_first_name_abbr
    first_name_abbr_dict_both_2 = abbr_dict(False, 2, xlsx_file)
    xlsx_file = xlsx_dir + xlsx_general_abbr
    general_abbr_dict_both_2 = abbr_dict(False, 2, xlsx_file)
    xlsx_file1 = xlsx_dir + xlsx_occupation_abbr
    xlsx_file2 = xlsx_dir + xlsx_occupation_tag_abbr
    occupation_abbr_dict_both_2 = abbr_dict_occupations(False, 2, xlsx_file1, xlsx_file2)
    xlsx_file = xlsx_dir + xlsx_special_abbr
    special_abbr_dict_both_2 = abbr_dict(False, 2, xlsx_file)
    xlsx_file = xlsx_dir + xlsx_title_abbr
    title_abbr_dict_both_2 = abbr_dict(False, 2, xlsx_file)
    
    #
    xlsx_file = xlsx_dir + xlsx_occupation_abbr
    occupation_key_list = get_key_list(xlsx_file)
    xlsx_file = xlsx_dir + xlsx_title_abbr
    title_key_list = get_key_list(xlsx_file)
    
    #
    xlsx_file = xlsx_dir + xlsx_business_abbr
    business_value_list = get_value_list(xlsx_file)
    xlsx_file1 = xlsx_dir + xlsx_occupation_abbr
    xlsx_file2 = xlsx_dir + xlsx_occupation_tag_abbr
    occupation_value_list = get_value_list_occupations(True, xlsx_file1, xlsx_file2)
    
    #
    pdf_segment_map_list = hr_reader(api_key, pdf_automated_segmentation_flg,
                                     ditto_correction_flg, pdf_dir, sect_dir,
                                     pdf_name, pdf_city, pdf_year, dpi_flg, 
                                     columns_per_page, pdf_pages)
    
    #
    if True:

        #
        hr_text_builder(api_key, pdf_automated_segmentation_flg, ditto_correction_flg,
                        pdf_dir, sect_dir, pdf_name, pdf_city, pdf_year, dpi_flg,
                        columns_per_page, pdf_pages, pdf_segment_map_list)
        
    #
    columns_per_iteration = pages_per_iteration * columns_per_page

    #
    global_excluded_surnames_list = hr_text_corrector1(columns_per_iteration, sect_dir, 0, 
                                                       pdf_name, business_abbr_dict_both_2,
                                                       first_name_abbr_dict_both_2,
                                                       general_abbr_dict_both_2, 
                                                       occupation_abbr_dict_both_2,
                                                       special_abbr_dict_both_2,
                                                       occupation_key_list)
    hr_text_corrector2(sect_dir, 1, pdf_name, global_excluded_surnames_list)
    hr_text_segmenter1(sect_dir, 2, pdf_name)
    hr_text_corrector3(sect_dir, 3, pdf_name, xlsx_dir, xlsx_business_abbr, xlsx_first_name_abbr, 
                       xlsx_general_abbr, xlsx_special_abbr)
    hr_text_corrector4(sect_dir, 4, pdf_name, xlsx_dir, xlsx_general_abbr)
    hr_text_segmenter2(columns_per_iteration, sect_dir, 5, pdf_name, xlsx_dir, business_value_list, 
                       occupation_value_list, title_key_list)
    #hr_evaluation(sect_dir, 6, pdf_name)