# Imports
import cv2
import math
import matplotlib.pyplot as plt
import numpy as np
from os import getcwd, makedirs
from PIL import Image
import re
from scipy.signal import argrelextrema, medfilt, savgol_filter
from shutil import copyfile
from skimage import color, io
from sklearn.neighbors import KernelDensity
from subprocess import Popen
from time import sleep

#
class pdf_page_to_segment_jpgs(object):
    
    #
    def __init__(self, mode_flg, gs_exe, page_image_dir, num_columns, 
                 dpi_flg, pdf_input_file, segment_filename_base, 
                 mean_trimmed_selected_column_widths,
                 std_trimmed_selected_column_widths):
        
        #
        self._jpg_tmp_dir = getcwd() + '/jpg_tmp/'
        self._sleep = 5
        
        # Input parameters
        self._dpi_flg = dpi_flg
        self._gs_exe = gs_exe
        self._mean_trimmed_selected_column_widths = mean_trimmed_selected_column_widths
        self._mode_flg = mode_flg
        self._num_columns = num_columns
        self._page_image_dir = page_image_dir
        self._segment_filename_base = segment_filename_base
        self._std_trimmed_selected_column_widths = std_trimmed_selected_column_widths
        
        # Parse DPI flag
        if dpi_flg == '300dpi':
            self._block_means_median_threshold = 0.5
            self._block_savgol_window = 111
            self._column_means_max_threshold = 0.15
            self._column_means_median_threshold = 0.75
            self._column_savgol_window = 71
            self._dpi = 300
            self._line_count_factor = 10
            self._line_means_percentile = 0.6
            self._lower_n_sigma = 6
            self._upper_n_sigma = 6
        elif dpi_flg == '600dpi':
            self._block_savgol_window = 51
            self._column_means_multiplier = 0.5
            self._column_savgol_window = 101
            self._dpi = 600
            self._line_count_factor = 10
            self._line_means_percentile = 0.6
            self._line_savgol_window = 11
            self._row_means_multiplier = 0.025
        else:
            print('Bad DPI flag')
            
        # Derived parameters
        self._column_width_adjustment = 0.5 * self._lower_n_sigma * \
                                        self._std_trimmed_selected_column_widths
        self._column_width_lower_bound = self._mean_trimmed_selected_column_widths - \
                                         self._lower_n_sigma * self._std_trimmed_selected_column_widths
        self._column_width_upper_bound = self._mean_trimmed_selected_column_widths + \
                                         self._upper_n_sigma * self._std_trimmed_selected_column_widths
                
        # Create data directories
        makedirs(self._jpg_tmp_dir, exist_ok=True)
        makedirs(self._page_image_dir, exist_ok=True)
        
        #
        self._pdf_input_file = pdf_input_file
        self._jpg_tmp_file = self._jpg_tmp_dir + 'tmp.jpg'
        
    # Deskew page image and make mask of image
    def _deskew_image(self, image):
        
        # Deskew image
        mask = self._image_mask(image, True)
        coords = np.column_stack(np.where(mask > 0))
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        deskewed = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC,
                                  borderMode=cv2.BORDER_REPLICATE)
        
        # Return deskewed mask of image
        return deskewed
    
    #
    def _detect_lines_of_text(self, image):
        
        #
        edges = cv2.Canny(image,0,0)
        medfilt_edges = medfilt(edges)
        line_means = []
        for i in range(len(image)):
            line_means.append(sum(medfilt_edges[i]) / 255)
        line_means = line_means / sum(line_means)
            
        #   
        row_idxs = []
        for i in range(len(line_means)):
            if line_means[i] > np.percentile(line_means, self._line_means_percentile):
                row_idxs.append(1)
            else:
                row_idxs.append(0)
                
        #
        row_idxs = ''.join(map(str,row_idxs))
        row_idxs = row_idxs.replace('010','000')
        row_idxs = row_idxs.replace('101','111')
        row_idxs = row_idxs.replace('0110','0000')
        row_idxs = row_idxs.replace('1001','1111')
        line_idxs = [ i.start() for i in re.finditer('01',row_idxs) ]
        line_idxs.append(0)
        line_idxs.append(len(image))
        line_idxs = sorted(line_idxs)
        
        #
        return line_idxs
    
    #
    def _display_image(self, image, subplot_idx):
        plt.subplot(121 + subplot_idx),plt.imshow(image,cmap = 'gray')
        plt.title('Image'), plt.xticks([]), plt.yticks([])
        plt.show()
    
    #
    def _image_mask(self, image, invert_flg):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        if invert_flg:
            gray = cv2.bitwise_not(gray)
        mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        return mask
    
    #
    def _isolate_blocks_of_text(self, columns):
        
        #
        row_sums = [0] * len(columns[0])
        for i in range(len(columns)):
            edges = cv2.Canny(columns[i],0,0)
            medfilt_edges = medfilt(edges)
            for j in range(len(medfilt_edges)):
                row_sums[j] += sum(medfilt_edges[j]) / 255
        row_means = row_sums / sum(row_sums)
        
        #
        min_row_means = min(row_means)
        for i in range(len(row_means)):
            row_means[i] -= min_row_means
                
        if False:
            plt.plot(row_means)
            plt.show()
        
        #
        row_means = savgol_filter(row_means, self._block_savgol_window, 2)
        
        if False:
            plt.plot(row_means)
            plt.show()
            
        #
        min_row_means = min(row_means)
        for i in range(len(row_means)):
            row_means[i] -= min_row_means
        threshold = self._block_means_median_threshold * np.median(row_means)
        for i in range(len(row_means)):
            if row_means[i] > threshold:
                row_means[i] = threshold
                
        if False:
            plt.plot(row_means)
            plt.show()
            
        # Create binary classifier for whether the smooothed density estimate is above or below
        # a given threshold
        row_idxs_array = argrelextrema(row_means, np.less)
        row_idxs_list = list(row_idxs_array[0])
        row_idxs = row_idxs_list
        row_idxs.append(0)
        row_idxs.append(len(columns[0]))
        row_idxs = set(row_idxs)
        line_idxs = sorted(row_idxs)
        
        # Isolate the block corresponding to the widest interval between crossings of the 
        # threshold going from 0 to 1
        line_idxs_table = []
        for i in range(len(line_idxs) - 1):
            line_idxs_table.append([ line_idxs[i], line_idxs[i+1], line_idxs[i+1] - line_idxs[i] ])
        line_idxs = line_idxs_table[0]
        for i in range(len(line_idxs_table) - 1):
            if line_idxs_table[i+1][2] > line_idxs[2]:
                line_idxs = line_idxs_table[i+1]
        
        #
        for i in range(len(columns)):
            columns[i] = columns[i][line_idxs[0]:line_idxs[1], :]
        
        #
        return columns
    
    #
    def _isolate_columns_of_text(self, image):
        
        # Estimate density of edges along each column of pixels
        edges = cv2.Canny(image,0,0)
        medfilt_edges = medfilt(edges)
        column_means = [0] * len(medfilt_edges[0])
        for i in range(len(medfilt_edges)):
            column_means += medfilt_edges[i]
        column_means = [ x / 255 for x in column_means ]
        column_means_ceiling = np.floor( np.mean(column_means) + np.std(column_means) )
        for i in range(len(column_means)):
            if column_means[i] > column_means_ceiling:
                column_means[i] = np.mean(column_means)
        column_means = column_means / sum(column_means)
        
        #
        min_column_means = min(column_means)
        for i in range(len(column_means)):
            column_means[i] -= min_column_means
        threshold = self._column_means_max_threshold * max(column_means)
        for i in range(len(column_means)):
            if column_means[i] > threshold:
                column_means[i] = threshold
        
        #
        if False:
            plt.plot(column_means)
            plt.show()
        
        column_means = savgol_filter(column_means, self._column_savgol_window, 2)
        
        #
        if False:
            plt.plot(column_means)
            plt.show()
        
        # Create binary classifier for whether the smooothed density estimate is above or below
        # a given threshold
        column_idxs_array = argrelextrema(column_means, np.less)
        column_idxs_list = list(column_idxs_array[0])
        column_idxs = [0] * len(column_means)
        threshold = self._column_means_median_threshold * np.median(column_means)
        for i in column_idxs_list:
            if column_means[i] < threshold:
                column_idxs.append(i)
        column_idxs.append(0)
        column_idxs.append(len(image[0]))
        column_idxs = set(column_idxs)
        column_idxs = sorted(column_idxs)
        
        #
        column_idxs_table = []
        for i in range(len(column_idxs)-1):
            idx0 = column_idxs[i]
            idx1 = column_idxs[i+1]
            if self._mode_flg == 1:
                max_idx = column_idxs[-1]
                if idx1 - idx0 < self._column_width_lower_bound:
                    idx0 = max([0, math.ceil(idx0 - self._column_width_adjustment)])
                    idx1 = min([max_idx, math.floor(idx1 + self._column_width_adjustment)])
            column_idxs_table.append([idx0, idx1])
        
        # Isolate the columns corresponding to the N widest intervals between crossings of the 
        # threshold going from 0 to 1 where N is input number of columns expected
        num_preliminary_columns = len(column_idxs_table)
        column_widths = []
        columns = []
        cut_width = []
        for i in range(len(column_idxs_table)):
            column_widths.append(column_idxs_table[i][1] - column_idxs_table[i][0])
            columns.append(image[:, column_idxs_table[i][0]:column_idxs_table[i][1]])
        if len(column_widths) >= self._num_columns:
            cut_width = sorted(column_widths, reverse=True)[self._num_columns - 1]
        
        #
        return columns, column_widths, cut_width
    
    #
    def _read_page_image(self, page):
        
        #
        args = [ self._gs_exe, '-dNOPAUSE', '-qNOPROMPT', '-qNODISPLAY', '-sDEVICE=jpeg', 
                '-r' + str(self._dpi) + 'x' + str(self._dpi), 
                '-dFirstPage=' + str(page), '-dLastPage=' + str(page), 
                '-sOutputFile=' + self._jpg_tmp_file, self._pdf_input_file ]
        output = Popen(args)
        
        #
        image = []
        ctr = 10
        read_flg = False
        while not read_flg and ctr > 0:
            ctr -= 1
            sleep(self._sleep)
            try:
                image = cv2.imread(self._jpg_tmp_file)
                image = self._deskew_image(image)
                read_flg = True
            except:
                pass
            
        #
        return image
        
    #
    def _segment_column(self, column, segment_ctr, segment_jpgs_dir):
        line_idxs = self._detect_lines_of_text(column)
        num_segments = (len(line_idxs)-1)//self._line_count_factor
        if len(line_idxs) > 2:
            for i in range(num_segments):
                idx0 = line_idxs[i*self._line_count_factor]
                idx1 = line_idxs[(i+1)*self._line_count_factor]
                segment = column[idx0:idx1]
                image_file = segment_jpgs_dir + self._segment_filename_base + str(segment_ctr) + '.jpg'
                segment_ctr += 1
                plt.imsave(image_file, segment, cmap=plt.cm.gray)
            if idx1 != len(column):
                segment = column[idx1:]
                image_file = segment_jpgs_dir + self._segment_filename_base + str(segment_ctr) + '.jpg'
                segment_ctr += 1
                plt.imsave(image_file, segment, cmap=plt.cm.gray)
        else:
            image_file = segment_jpgs_dir + self._segment_filename_base + str(segment_ctr) + '.jpg'
            segment_ctr += 1
            plt.imsave(image_file, column, cmap=plt.cm.gray)
        return segment_ctr
               
    #
    def run(self, page, segment_jpgs_dir):
        
        # Read page image
        image = self._read_page_image(page)
        
        #
        segment_map = []
        if len(image) > 0:
        
            #
            image = self._image_mask(image, False)

            #
            columns, column_widths, cut_width = self._isolate_columns_of_text(image)

            if self._mode_flg == 0:

                #
                selected_column_widths = []
                for column_width in column_widths:
                    if column_width >= cut_width:
                        selected_column_widths.append(column_width)

                #
                return column_widths, cut_width, selected_column_widths

            elif self._mode_flg == 1:

                #
                if False:
                    self._display_image(image, 0)

                good_page_flg = True

                #
                isolated_columns = []
                for i in range(len(column_widths)):
                    if column_widths[i] >= cut_width:
                        if column_widths[i] >= self._column_width_lower_bound and \
                           column_widths[i] <= self._column_width_upper_bound:
                            isolated_columns.append(columns[i])
                            if False:
                                self._display_image(columns[i],0)
                        else:
                            good_page_flg = False

                #
                if good_page_flg:

                    #
                    columns = isolated_columns
                    columns = self._isolate_blocks_of_text(columns)

                    #
                    segment_ctr = 0
                    for i in range(len(columns)):
                        segment_map_tmp = []
                        segment_map_tmp.append(i)
                        segment_map_tmp.append(segment_ctr)
                        segment_ctr = self._segment_column(columns[i], segment_ctr, segment_jpgs_dir)
                        segment_map_tmp.append(segment_ctr)
                        segment_map.append(segment_map_tmp)
                        
            else:
                print('PDF page read timed out.')
                
            #
            return segment_map