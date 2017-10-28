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
from subprocess import Popen
from time import sleep

#
class pdf_page_to_segment_pngs(object):
    
    #
    def __init__(self, mode_flg, gs_exe, page_image_dir, num_columns, 
                 dpi_flg, pdf_input_file, segment_filename_base, 
                 mean_trimmed_selected_column_widths,
                 std_trimmed_selected_column_widths,
                 mean_trimmed_selected_column_heights,
                 std_trimmed_selected_column_heights):
        
        # Input parameters
        self._dpi_flg = dpi_flg
        self._gs_exe = gs_exe
        self._mean_trimmed_selected_column_heights = mean_trimmed_selected_column_heights
        self._mean_trimmed_selected_column_widths = mean_trimmed_selected_column_widths
        self._mode_flg = mode_flg
        self._num_columns = num_columns
        self._page_image_dir = page_image_dir
        self._segment_filename_base = segment_filename_base
        self._std_trimmed_selected_column_heights = std_trimmed_selected_column_heights
        self._std_trimmed_selected_column_widths = std_trimmed_selected_column_widths
        
        # General algorithm parameters
        self._gs_read_timout = 60
        self._gs_sleep = 3
        self._image_tmp_dir = getcwd() + '/image_tmp/'
        self._image_tmp_file = self._image_tmp_dir + 'tmp.tiff'
        self._pdf_input_file = pdf_input_file
        self._restored_std_offset = 0
        self._restored_width_offset = 0
        
        # DPI-specific algorithm parameters
        if dpi_flg == '300dpi':
            self._block_means_first_median_threshold = 0.9
            self._block_means_second_median_threshold = 0.5
            self._block_savgol_window = 71
            self._column_means_first_median_threshold = 1.5
            self._column_means_second_median_threshold = 0.95
            self._column_savgol_window = 71
            self._convolution_box_size = 100
            self._convolution_num = 1
            self._dpi = 300
            self._lower_n_sigma = 7
            self._upper_n_sigma = 22
        elif dpi_flg == '600dpi':
            self._block_amplitude_coeff = 0.0
            self._block_convolution_box_size = 201
            self._block_convolution_num = 1
            self._block_convolution_sigma = 100
            self._block_means_first_median_threshold = 0.9
            self._block_means_second_median_threshold = 0.5
            self._block_mins_window = -1
            self._block_savgol_window = 301
            self._column_amplitude_coeff = 0.1
            self._column_convolution_box_size = 21
            self._column_convolution_num = 1
            self._column_convolution_sigma = 20
            self._column_means_first_median_threshold = 0.50
            self._column_means_second_median_threshold = 0.75
            self._column_mins_window = 1200
            self._column_savgol_window = 3
            self._dpi = 600
            self._lower_n_sigma = 11
            self._margin_width = 50
            self._upper_n_sigma = 22
        else:
            print('Bad DPI flag')
            
        # Derived algorithm parameters
        self._column_width_lower_bound = self._mean_trimmed_selected_column_widths - \
                                         self._lower_n_sigma * self._std_trimmed_selected_column_widths
        self._column_width_upper_bound = self._mean_trimmed_selected_column_widths + \
                                         self._upper_n_sigma * self._std_trimmed_selected_column_widths
                
        # Create data directories
        makedirs(self._image_tmp_dir, exist_ok=True)
        makedirs(self._page_image_dir, exist_ok=True)
        
    # Cleans margins of reverse image mask making them black
    def _clean_margins(self, reverse_mask):
        
        # Get mask height and width
        mask_height = len(reverse_mask)
        mask_width = len(reverse_mask[0])
        
        # Make margins of reverse image mask black
        reverse_mask[:,0:self._margin_width] = 0 * reverse_mask[:,0:self._margin_width]
        reverse_mask[:,mask_width-self._margin_width:mask_width] = \
            0 * reverse_mask[:,mask_width-self._margin_width:mask_width]
        reverse_mask[0:self._margin_width,:] = 0 * reverse_mask[0:self._margin_width,:]
        reverse_mask[mask_height-self._margin_width:mask_height,:] = \
            0 * reverse_mask[mask_height-self._margin_width:mask_height,:]
                                               
        # Return cleaned mask
        return reverse_mask
    
    # Deskew page image and make mask of image
    def _deskewed_mask(self, image):
        
        # Generate true mask
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.bitwise_not(gray)    
        reverse_mask = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)[1]
        reverse_mask = self._clean_margins(reverse_mask)
        true_mask = cv2.bitwise_not(reverse_mask)
        
        # Generate reverse mask
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        for _ in range(4):
            gray = cv2.medianBlur(gray, 5)
        gray = cv2.bitwise_not(gray)    
        reverse_mask = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)[1]
        reverse_mask = self._clean_margins(reverse_mask)
        
        # Deskew image
        coords = np.column_stack(np.where(reverse_mask > 0))
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        (h, w) = true_mask.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        deskewed_mask = cv2.warpAffine(true_mask, M, (w, h), flags=cv2.INTER_CUBIC,
                                       borderMode=cv2.BORDER_REPLICATE)
        
        # Return deskewed mask of image
        return deskewed_mask
    
    # Image display function for algorithm debugging
    def _display_image(self, image, subplot_idx):
        plt.subplot(121 + subplot_idx),plt.imshow(image,cmap = 'gray')
        plt.title('Image'), plt.xticks([]), plt.yticks([])
        plt.show()
        
    # Smooth a vector of means to produce an estimate of the means at the 
    # desired scale
    def _filter(self, input_means, input_amplitude_coeff, input_savgol_window, 
                input_convolution_box_size, input_convolution_num, 
                input_convolution_sigma):
        
        #
        amplitude = [1] * len(input_means)
        M = len(input_means)/2
        for i in range(len(amplitude)):
            amplitude[i] += input_amplitude_coeff * ((i - M) ** 2) / (M ** 2)
        for i in range(len(input_means)):
            input_means[i] = amplitude[i] * input_means[i]
        
        # Display means for debugging
        if False:
            plt.plot(input_means)
            plt.show()
        
        # Apply Savgol filter to means
        filtered_means = savgol_filter(input_means, input_savgol_window, 2)
        
        # Apply Gaussian convolution to filtered means
        x_lim = math.floor(0.5 * input_convolution_box_size)
        X = list(range(-x_lim, x_lim+1))
        gauss = []
        for x in X:
            gauss.append(np.exp(-0.5*(x/input_convolution_sigma)**2))
        gauss_sum = 0
        for i in range(len(gauss)):
            gauss_sum += gauss[i]
        for i in range(len(gauss)):
            gauss[i] = gauss[i] / gauss_sum
        for _ in range(input_convolution_num - 1):
            filtered_means = np.convolve(filtered_means, gauss, mode='same')
        filtered_means = np.convolve(filtered_means, gauss, mode='same')
        
        # Display means for debugging
        if False:
            plt.plot(filtered_means)
            plt.show()
            
        # Return filtered means
        return filtered_means
    
    #
    def _isolate_blocks_of_text(self, columns):
        
        #  Estimate density of edges along each row of pixels
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
        
        # Generate indicies to be used to segment columns into distinct blocks such that the blocks
        # of text are expected to be entirely contained in a block and any extra content in 
        # the margins in other blocks
        row_means = self._filter(row_means, self._block_amplitude_coeff, 
                                 self._block_savgol_window, self._block_convolution_box_size,
                                 self._block_convolution_num, self._block_convolution_sigma)
        row_means = self._normalize_means(row_means, self._block_means_first_median_threshold)
        line_idxs = self._local_mins(len(columns[0]), row_means, 
                                     self._block_means_second_median_threshold,
                                     self._block_mins_window)
        
        # 
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
        column_height = len(columns[0])
        column_heights = [ column_height, column_height, column_height ]
        
        #
        return columns, column_heights
    
    #
    def _isolate_columns_of_text(self, image):
        
        # Estimate density of edges along each column of pixels
        edges = cv2.Canny(image,0,0)
        medfilt_edges = medfilt(edges)
        column_means = [0] * len(medfilt_edges[0])
        for i in range(len(medfilt_edges)):
            column_means += medfilt_edges[i]
        column_means = [ x / 255 for x in column_means ]
        
        # Generate indicies to be used to segment image into distinct columns such that the columns
        # of text are expected to be entirely contained in different columns and any extra content in 
        # the margins in other columns
        column_means = self._normalize_means(column_means, self._column_means_first_median_threshold)
        column_means = self._filter(column_means, self._column_amplitude_coeff,
                                    self._column_savgol_window,self._column_convolution_box_size,
                                    self._column_convolution_num, self._column_convolution_sigma)
        column_idxs = self._local_mins(len(image[0]), column_means, 
                                       self._column_means_second_median_threshold,
                                       self._column_mins_window)
        
        #
        column_idxs_table = []
        for i in range(len(column_idxs)-1):
            idx0 = column_idxs[i]
            idx1 = column_idxs[i+1]
            if idx0 != idx1:
                column_idxs_table.append([idx0, idx1])
        
        # Isolate the columns corresponding to the N widest intervals between crossings of the 
        # threshold going from 0 to 1 where N is input number of columns expected
        num_preliminary_columns = len(column_idxs_table)
        column_widths = []
        columns = []
        for i in range(len(column_idxs_table)):
            column_widths.append(column_idxs_table[i][1] - column_idxs_table[i][0])
            columns.append(image[:, column_idxs_table[i][0]:column_idxs_table[i][1]])
        if len(column_widths) >= self._num_columns:
            cut_width = sorted(column_widths, reverse=True)[self._num_columns - 1]
        else:
            cut_width = -1
        
        #
        return columns, column_widths, cut_width
    
    #
    def _local_mins(self, image_length, input_means, input_means_median_threshold,
                    input_mins_window):
        local_mins_idxs = []
        local_mins_idxs_array = argrelextrema(input_means, np.less)
        local_mins_idxs = list(local_mins_idxs_array[0])
        if input_means_median_threshold != -1:
            local_mins_idxs_tmp = local_mins_idxs
            local_mins_idxs = []
            threshold = input_means_median_threshold * np.median(input_means)
            for i in local_mins_idxs_tmp:
                if input_means[i] < threshold and \
                   input_means[i] > 0.05 * np.median(input_means):
                    local_mins_idxs.append(i)
        if input_mins_window != -1:
            local_mins_idxs_tmp = local_mins_idxs
            local_mins_idxs = []
            for idx in local_mins_idxs_tmp:
                if idx > 0.5 * input_mins_window and \
                   idx < image_length - 0.5 * input_mins_window:
                    local_mins_idxs.append(idx)
            local_mins_idxs_tmp = local_mins_idxs
            local_mins_idxs = []
            for idx1 in local_mins_idxs_tmp:
                good_idx_flg = True
                for idx2 in local_mins_idxs_tmp:
                    delta = abs(idx1 - idx2)
                    if delta > 0 and delta < input_mins_window:
                        if input_means[idx2] < input_means[idx1]:
                            good_idx_flg = False
                if good_idx_flg:
                    local_mins_idxs.append(idx1)
        local_mins_idxs.append(0)
        local_mins_idxs.append(image_length)
        local_mins_idxs = set(local_mins_idxs)
        local_mins_idxs = sorted(local_mins_idxs)
        return local_mins_idxs
    
    #
    def _normalize_means(self, input_means, input_means_median_threshold):
        
        #
        min_input_means = min(input_means)
        for i in range(len(input_means)):
            input_means[i] -= min_input_means
        threshold = input_means_median_threshold * np.median(input_means)
        for i in range(len(input_means)):
            if input_means[i] > threshold:
                input_means[i] = threshold
                
        #
        return input_means
    
    # Read page image as deskewed mask
    def _read_page_image(self, page):
        
        # Use Ghostscript to copy page of PDF into temporary TIFF file
        args = [ self._gs_exe, '-dNOPAUSE', '-qNOPROMPT', '-qNODISPLAY', '-sDEVICE=tiff24nc', 
                '-r' + str(self._dpi) + 'x' + str(self._dpi), 
                '-dFirstPage=' + str(page), '-dLastPage=' + str(page), 
                '-sOutputFile=' + self._image_tmp_file, self._pdf_input_file ]
        output = Popen(args)

        # Read temporary TIFF file and turn into image into deskewed mask
        deskewed_mask = []
        ctr = self._gs_read_timout // self._gs_sleep
        read_flg = False
        while not read_flg and ctr > 0:
            ctr -= 1
            sleep(self._gs_sleep)
            try:
                image = cv2.imread(self._image_tmp_file)
                deskewed_mask = self._deskewed_mask(image)
                read_flg = True
            except:
                pass
            
        # Return deskewed mask
        return deskewed_mask
    
    #
    def _run_preliminary_mode(self, page, page_png_dir, page_npy_dir):
        
        # Read page image
        image = self._read_page_image(page)

        if len(image) > 0:

            #
            if False:
                self._display_image(image, 0)

            #
            columns, column_widths, cut_width = self._isolate_columns_of_text(image)

            #
            if cut_width != -1:
                selected_column_widths = []
                for column_width in column_widths:
                    if column_width >= cut_width:
                        selected_column_widths.append(column_width)

                #
                isolated_columns = []
                for i in range(len(column_widths)):
                    isolated_columns.append(columns[i])

                #
                columns = isolated_columns
                columns, selected_column_heights = self._isolate_blocks_of_text(columns)

                #
                if True:
                    save_file = page_npy_dir + 'page_' + str(page)
                    np.save(save_file, image)
                else:
                    image_file = page_png_dir + 'page_' + str(page) + '.png'
                    self._save_image(image_file, image)
                    
            else:
                
                #
                if True:
                    save_file = page_npy_dir + 'page_' + str(page)
                    np.save(save_file, image)
                else:
                    image_file = page_png_dir + 'page_' + str(page) + '.png'
                    self._save_image(image_file, image)
                
                #
                selected_column_heights = []
                selected_column_widths = []
                print('Bad page segmentation.')

        else:

            #
            selected_column_heights = []
            selected_column_widths = []
            print('PDF page read timed out.')
            
        #
        return selected_column_widths, selected_column_heights
      
    #
    def _run_segmentation_mode(self, page, page_png_dir, page_npy_dir):
        
        #
        segment_map = []
        
        #
        if True:
            save_file = page_npy_dir + 'page_' + str(page) + '.npy'
            image = np.load(save_file)
        else:
            image_file = page_png_dir + 'page_' + str(page) + '.png'
            image = np.asarray(Image.open(image_file)) 

        #
        columns, column_widths, cut_width = self._isolate_columns_of_text(image)

        #
        good_page_flg = True
        if cut_width != -1:
            isolated_columns = []
            for i in range(len(column_widths)):
                if column_widths[i] >= cut_width:
                    if column_widths[i] >= self._column_width_lower_bound and \
                       column_widths[i] <= self._column_width_upper_bound:
                        isolated_columns.append(columns[i])
                    else:
                        good_page_flg = False
        else:
            good_page_flg = False

        #
        if good_page_flg:

            #
            columns = isolated_columns
            columns, column_heights = self._isolate_blocks_of_text(columns)
            
            #
            if False:
                self._display_image(image, 0)
                for column in columns:
                    self._display_image(column,0)

            #
            segment_ctr = 0
            for i in range(len(columns)):
                segment_map_tmp = []
                segment_map_tmp.append(i)
                segment_map_tmp.append(segment_ctr)
                segment_ctr = self._segment_column(columns[i], segment_ctr, page_png_dir)
                segment_map_tmp.append(segment_ctr)
                segment_map.append(segment_map_tmp)
                
        else:
            
            #
            image_file = page_png_dir + 'page_' + str(page) + '.png'
            self._save_image(image_file, image)
            print('Image segmentation failed.')
            

        #
        return segment_map
    
    # Save an image in the given file
    def _save_image(self, image_file, image):
        image = Image.fromarray(image)
        image.save(image_file, subsampling=0, quality=100)
        
    # Segment column into a set of smaller PNGs (This functionality is presently deprecated
    # and the code has been set up to simply save the whole column as a single PNG)
    def _segment_column(self, column, segment_ctr, page_png_dir):
        num_segments = 1
        line_idxs = [ 0, len(column) ]
        if len(line_idxs) > 2:
            for i in range(num_segments):
                idx0 = line_idxs[i*self._line_count_factor]
                idx1 = line_idxs[(i+1)*self._line_count_factor]
                image = column[idx0:idx1]
                image_file = page_png_dir + self._segment_filename_base + str(segment_ctr) + '.png'
                self._save_image(image_file, image)
                segment_ctr += 1
            if idx1 != len(column):
                image = column[idx1:]
                image_file = page_png_dir + self._segment_filename_base + str(segment_ctr) + '.png'
                self._save_image(image_file, image)
                segment_ctr += 1
        else:
            image = column
            image_file = page_png_dir + self._segment_filename_base + str(segment_ctr) + '.png'
            self._save_image(image_file, image)
            segment_ctr += 1
        return segment_ctr
               
    #
    def run(self, page, page_png_dir, page_npy_dir):
        
        #
        if self._mode_flg == 0:

            #
            selected_column_widths, selected_column_heights = \
                self._run_preliminary_mode(page, page_png_dir, page_npy_dir)
            return selected_column_widths, selected_column_heights

        elif self._mode_flg == 1:
            
            #
            segment_map = \
                self._run_segmentation_mode(page, page_png_dir, page_npy_dir)
            return segment_map