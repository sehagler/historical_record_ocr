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
    common_ocr_errors_list_xlsx = xlsx_dir + 'common_ocr_errors_list.xlsx'
    first_name_abbr_list_xlsx = xlsx_dir + 'first_name_abbreviation_list.xlsx'
    general_abbr_list_xlsx = xlsx_dir + 'general_abbreviation_list.xlsx'
    generic_business_list_xlsx = xlsx_dir + 'generic_business_list.xlsx'
    generic_occupation_list_xlsx = xlsx_dir + 'generic_occupation_list.xlsx'
    internal_ref_abbr_list_xlsx = xlsx_dir + 'internal_reference_abbreviation_list.xlsx'
    occupation_specifier_list_xlsx = xlsx_dir + 'occupation_specifier_list.xlsx'
    special_abbr_list_xlsx = xlsx_dir + 'special_abbreviation_list.xlsx'
    
    #
    xlsx_special_abbr = 'special_abbreviations.xlsx'
    xlsx_title_abbr = 'title_abbreviations.xlsx'
    
    #
    generic_business_list_dict_both_2 = abbr_dict(False, 2, generic_business_list_xlsx,
                                                  common_ocr_errors_list_xlsx)
    internal_ref_abbr_list_dict_both_2 = abbr_dict(False, 2, internal_ref_abbr_list_xlsx,
                                                   common_ocr_errors_list_xlsx)
    hyphenated_generic_occupation_list_dict_both_2 = abbr_dict_occupations(False, True, 2, 
                                                                           generic_occupation_list_xlsx,
                                                                           occupation_specifier_list_xlsx, 
                                                                           common_ocr_errors_list_xlsx)
    unhyphenated_generic_occupation_list_dict_both_2 = abbr_dict_occupations(False, False, 2, 
                                                                             generic_occupation_list_xlsx,
                                                                             occupation_specifier_list_xlsx, 
                                                                             common_ocr_errors_list_xlsx)
    
    #
    first_name_abbr_list_dict_upper_2 = abbr_dict(True, 2, first_name_abbr_list_xlsx,
                                                  common_ocr_errors_list_xlsx)
    general_abbr_dict_upper_1 = abbr_dict(True, 1, general_abbr_list_xlsx, common_ocr_errors_list_xlsx)
    general_abbr_dict_upper_2 = abbr_dict(True, 2, general_abbr_list_xlsx, common_ocr_errors_list_xlsx)
    special_abbr_dict_upper_2 = abbr_dict(True, 2, special_abbr_list_xlsx, common_ocr_errors_list_xlsx)
    
    #
    occupation_key_list = get_key_list(generic_occupation_list_xlsx, common_ocr_errors_list_xlsx)
    xlsx_file = xlsx_dir + xlsx_title_abbr
    title_key_list = get_key_list(xlsx_file, common_ocr_errors_list_xlsx)
    
    #
    generic_business_list_values = get_value_list(generic_business_list_xlsx)
    generic_occupation_list_values = get_value_list_occupations(True, generic_occupation_list_xlsx, 
                                                                occupation_specifier_list_xlsx)
    
    #
    xlsx_file = xlsx_dir + xlsx_title_abbr
    title_abbr_dict_both_2 = abbr_dict(False, 2, xlsx_file, common_ocr_errors_list_xlsx)
    
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
                                                       pdf_name, generic_business_list_dict_both_2, 
                                                       hyphenated_generic_occupation_list_dict_both_2,
                                                       internal_ref_abbr_list_dict_both_2,
                                                       unhyphenated_generic_occupation_list_dict_both_2,
                                                       occupation_key_list)
    hr_text_corrector2(sect_dir, 1, pdf_name, global_excluded_surnames_list)
    hr_text_segmenter1(sect_dir, 2, pdf_name)
    hr_text_corrector3(sect_dir, 3, pdf_name, general_abbr_dict_upper_1)
    hr_text_segmenter2(columns_per_iteration, sect_dir, 4, pdf_name, generic_business_list_values, 
                       generic_occupation_list_values, title_key_list)
    hr_text_corrector4(sect_dir, 5, pdf_name, first_name_abbr_list_dict_upper_2, 
                       general_abbr_dict_upper_2, special_abbr_dict_upper_2)
    #hr_evaluation(sect_dir, 6, pdf_name)