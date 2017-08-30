#
from subprocess import Popen
from time import sleep

#
class document_pdf_to_page_jpegs(object):
    
    #
    def __init__(self, pdf_input_file, jpg_output_dir, jpg_output_filename, dpi_flg):
        
        #
        self._gsexe = 'C:/Program Files/gs/gs9.21/bin/gswin64'
        
        # Parse DPI flag
        if dpi_flg == '300dpi':
            self._dpi = 300
        elif dpi_flg == '600dpi':
            self._dpi = 600
        
        #
        self._pdf_input_file = pdf_input_file
        self._jpg_output_file = jpg_output_dir + jpg_output_filename
        
    #
    def _pdf2jpeg(self, page_num):
        output_file = self._jpg_output_file + str(page_num) + '.jpg'
        args = [ self._gsexe, '-dNOPAUSE', '-sDEVICE=jpeg', '-r' + str(self._dpi) + 'x' + str(self._dpi), 
                '-dFirstPage=' + str(page_num), '-dLastPage=' + str(page_num), 
                '-sOutputFile=' + output_file, self._pdf_input_file ]
        output = Popen( args )
        sleep(5)
        
    #
    def run(self):
        for page_num in range(10):
            self._pdf2jpeg(page_num + 1)