# Imports
import os
import pickle
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
from file_writer import file_writer
from hr_reader import hr_reader
from hr_text_builder import hr_text_builder
from hr_text_corrector1 import hr_text_corrector1
from hr_text_corrector2 import hr_text_corrector2
from hr_text_corrector3 import hr_text_corrector3
from hr_text_corrector4 import hr_text_corrector4
from hr_text_segmenter1 import hr_text_segmenter1
from hr_text_segmenter2 import hr_text_segmenter2

#
def _setup_pkl_file(hyphenated_occupation_dict_both_2_pkl,
                    unhyphenated_occupation_dict_both_2_pkl,
                    executive_occupation_list_xlsx, generic_occupation_list_xlsx,
                    occupation_specifier_list_xlsx, occupation_determiner_list_xlsx,
                    common_ocr_errors_list_xlsx):
    
    #
    hyphenated_executive_occupation_dict_both_2 = abbr_dict_occupations(True, True, 2,
                                                                        executive_occupation_list_xlsx,
                                                                        occupation_specifier_list_xlsx,
                                                                        occupation_determiner_list_xlsx,
                                                                        common_ocr_errors_list_xlsx)
    hyphenated_generic_occupation_dict_both_2 = abbr_dict_occupations(False, True, 2, 
                                                                      generic_occupation_list_xlsx,
                                                                      occupation_specifier_list_xlsx,
                                                                      occupation_determiner_list_xlsx,
                                                                      common_ocr_errors_list_xlsx)
    unhyphenated_executive_occupation_dict_both_2 = abbr_dict_occupations(True, False, 2,
                                                                          executive_occupation_list_xlsx,
                                                                          occupation_specifier_list_xlsx,
                                                                          occupation_determiner_list_xlsx,
                                                                          common_ocr_errors_list_xlsx)
    unhyphenated_generic_occupation_dict_both_2 = abbr_dict_occupations(False, False, 2, 
                                                                         generic_occupation_list_xlsx,
                                                                         occupation_specifier_list_xlsx,
                                                                         occupation_determiner_list_xlsx,
                                                                         common_ocr_errors_list_xlsx)
    
    #    
    hyphenated_occupation_dict_both_2 = { **hyphenated_executive_occupation_dict_both_2,
                                          **hyphenated_generic_occupation_dict_both_2 }
    key_list = list(hyphenated_executive_occupation_dict_both_2.keys())
    for key in key_list:
        hyphenated_occupation_dict_both_2[key.lower()] = \
            hyphenated_executive_occupation_dict_both_2[key].lower()
    unhyphenated_occupation_dict_both_2 = { **unhyphenated_executive_occupation_dict_both_2,
                                     **unhyphenated_generic_occupation_dict_both_2 }
    key_list = list(unhyphenated_executive_occupation_dict_both_2.keys())
    for key in key_list:
        unhyphenated_occupation_dict_both_2[key.lower()] = \
            unhyphenated_executive_occupation_dict_both_2[key].lower()
    
    #
    with open(hyphenated_occupation_dict_both_2_pkl, 'wb') as f:
        pickle.dump(hyphenated_occupation_dict_both_2, f,
                    protocol=pickle.HIGHEST_PROTOCOL)
    with open(unhyphenated_occupation_dict_both_2_pkl, 'wb') as f:
        pickle.dump(unhyphenated_occupation_dict_both_2, f,
                    protocol=pickle.HIGHEST_PROTOCOL)
    
#
def _setup_txt_files(business_value_list_txt, occupation_value_list_txt, 
                     executive_occupation_list_xlsx, generic_business_list_xlsx,
                     generic_occupation_list_xlsx, occupation_determiner_list_xlsx,
                     occupation_specifier_list_xlsx):
    
    #
    executive_occupation_value_list = get_value_list_occupations(True, executive_occupation_list_xlsx,
                                                                 occupation_determiner_list_xlsx,
                                                                 occupation_specifier_list_xlsx)
    generic_business_value_list = get_value_list(generic_business_list_xlsx)
    generic_occupation_value_list = get_value_list_occupations(False, generic_occupation_list_xlsx,
                                                                occupation_determiner_list_xlsx,
                                                                occupation_specifier_list_xlsx)
    
    #
    if True:
        business_value_list = generic_business_value_list
        business_value_list = [ biz + '\n' for biz in business_value_list ]
        business_value_list = ''.join(business_value_list)
        fl_wrtr = file_writer(business_value_list_txt)
        fl_wrtr.run(business_value_list)
        del business_value_list
    
    #
    if True:
        occupation_value_list = executive_occupation_value_list
        occupation_value_list.extend([ occ.lower() for occ in executive_occupation_value_list ])
        occupation_value_list.extend(generic_occupation_value_list)
        occupation_value_list.sort(key = lambda x:len(x), reverse = True)
        occupation_value_list = [ occ + '\n' for occ in occupation_value_list ]
        occupation_value_list = ''.join(occupation_value_list)
        fl_wrtr = file_writer(occupation_value_list_txt)
        fl_wrtr.run(occupation_value_list)
        del occupation_value_list

#
def hr_main(api_key,  pdf_automated_segmentation_flg, pdf_city, pdf_year, dpi_flg, columns_per_page, 
            pdf_dir, pdf_name, pdf_pages, workspace):
    
    #
    ditto_correction_flg = True
    max_chars = 250
    pages_per_iteration = 5
    sect_dir = workspace + 'SECTION2/'
    
    #
    pkl_dir = sect_dir + 'pkl/'
    if not os.path.exists(pkl_dir):
        os.makedirs(pkl_dir)
    hyphenated_occupation_dict_both_2_pkl = \
        pkl_dir + 'hyphenated_occupation_dict_both_2.pkl'
    unhyphenated_occupation_dict_both_2_pkl = \
        pkl_dir + 'unhyphenated_occupation_dict_both_2.pkl'
    
    #
    txt_dir = sect_dir + 'txt/'
    if not os.path.exists(txt_dir):
        os.makedirs(txt_dir)
    business_value_list_txt = txt_dir + 'business_value_list.txt'
    occupation_value_list_txt = txt_dir + 'occupation_value_list.txt'
    
    #
    xlsx_dir = 'xlsx/'
    common_ocr_errors_list_xlsx = xlsx_dir + 'common_ocr_errors_list.xlsx'
    executive_occupation_list_xlsx = xlsx_dir + 'executive_occupation_list.xlsx'
    first_name_abbr_list_xlsx = xlsx_dir + 'first_name_abbreviation_list.xlsx'
    general_abbr_list_xlsx = xlsx_dir + 'general_abbreviation_list.xlsx'
    generic_business_list_xlsx = xlsx_dir + 'generic_business_list.xlsx'
    generic_occupation_list_xlsx = xlsx_dir + 'generic_occupation_list.xlsx'
    internal_ref_abbr_list_xlsx = xlsx_dir + 'internal_reference_abbreviation_list.xlsx'
    occupation_determiner_list_xlsx = xlsx_dir + 'occupation_determiner_list.xlsx'
    occupation_specifier_list_xlsx = xlsx_dir + 'occupation_specifier_list.xlsx'
    special_abbr_list_xlsx = xlsx_dir + 'special_abbreviation_list.xlsx'
    title_abbr_list_xlsx = xlsx_dir + 'title_abbreviation_list.xlsx'
    
    #
    generic_business_dict_both_2 = abbr_dict(False, 2, generic_business_list_xlsx,
                                             common_ocr_errors_list_xlsx)
    internal_ref_abbr_dict_both_2 = abbr_dict(False, 2, internal_ref_abbr_list_xlsx,
                                              common_ocr_errors_list_xlsx)
    title_abbr_dict_both_2 = abbr_dict(False, 2, title_abbr_list_xlsx, common_ocr_errors_list_xlsx)
    
    #
    first_name_abbr_dict_upper_2 = abbr_dict(True, 2, first_name_abbr_list_xlsx,
                                             common_ocr_errors_list_xlsx)
    general_abbr_dict_upper_1 = abbr_dict(True, 1, general_abbr_list_xlsx, common_ocr_errors_list_xlsx)
    general_abbr_dict_upper_2 = abbr_dict(True, 2, general_abbr_list_xlsx, common_ocr_errors_list_xlsx)
    special_abbr_dict_upper_2 = abbr_dict(True, 2, special_abbr_list_xlsx, common_ocr_errors_list_xlsx)
    
    #
    executive_occupation_key_list = get_key_list(executive_occupation_list_xlsx, common_ocr_errors_list_xlsx)
    generic_occupation_key_list = get_key_list(generic_occupation_list_xlsx, common_ocr_errors_list_xlsx)
    title_key_list = get_key_list(title_abbr_list_xlsx, common_ocr_errors_list_xlsx)
    
    #
    occupation_determiner_value_list = get_value_list(occupation_determiner_list_xlsx)

    #
    _setup_pkl_file(hyphenated_occupation_dict_both_2_pkl,
                    unhyphenated_occupation_dict_both_2_pkl,
                    executive_occupation_list_xlsx, generic_occupation_list_xlsx,
                    occupation_specifier_list_xlsx, occupation_determiner_list_xlsx,
                    common_ocr_errors_list_xlsx)
    _setup_txt_files(business_value_list_txt, occupation_value_list_txt, 
                     executive_occupation_list_xlsx, generic_business_list_xlsx,
                     generic_occupation_list_xlsx, occupation_determiner_list_xlsx,
                     occupation_specifier_list_xlsx)
    
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
                                                       pdf_name, generic_business_dict_both_2,
                                                       hyphenated_occupation_dict_both_2_pkl,
                                                       internal_ref_abbr_dict_both_2,
                                                       unhyphenated_occupation_dict_both_2_pkl,
                                                       executive_occupation_key_list, 
                                                       generic_occupation_key_list)
    hr_text_corrector2(sect_dir, 1, pdf_name, global_excluded_surnames_list)
    hr_text_segmenter1(max_chars, sect_dir, 2, pdf_name)
    hr_text_corrector3(sect_dir, 3, pdf_name, general_abbr_dict_upper_1)
    hr_text_segmenter2(columns_per_iteration, max_chars, txt_dir, 4, pdf_name, 
                       business_value_list_txt, occupation_value_list_txt, 
                       occupation_determiner_value_list, title_key_list)
    hr_text_corrector4(sect_dir, 5, pdf_name, first_name_abbr_dict_upper_2, 
                       general_abbr_dict_upper_2, special_abbr_dict_upper_2)
    #hr_evaluation(sect_dir, 6, pdf_name)