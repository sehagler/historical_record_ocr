# Imports
import cv2
import matplotlib.pyplot as plt
import numpy as np
from os import getcwd, makedirs
from PIL import Image
import re
from scipy.signal import medfilt, savgol_filter
from shutil import copyfile
from skimage import color, io
from sklearn.neighbors import KernelDensity
from subprocess import Popen
from time import sleep

#
class pdf_page_to_segment_jpgs(object):
    
    #
    def __init__(self, gs_exe, page_image_dir, num_columns, dpi_flg, pdf_input_file, segment_filename_base):
        
        #
        self._jpg_tmp_dir = getcwd() + '/jpg_tmp/'
        self._sleep = 5
        
        # Input parameters
        self._dpi_flg = dpi_flg
        self._gs_exe = gs_exe
        self._num_columns = num_columns
        self._page_image_dir = page_image_dir
        self._segment_filename_base = segment_filename_base
        
        # Parse DPI flag
        if dpi_flg == '300dpi':
            self._column_means_multiplier = 0.15
            self._column_savgol_window = 21
            self._dpi = 300
            self._line_count_factor = 10
            self._line_means_percentile = 0.6
            self._row_means_multiplier = 0.025
        elif dpi_flg == '600dpi':
            self._column_means_multiplier = 0.5
            self._column_savgol_window = 101
            self._dpi = 600
            self._line_count_factor = 10
            self._line_means_percentile = 0.6
            self._row_means_multiplier = 0.025
        else:
            print('Bad DPI flag')
        
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
        deskewed = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        
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
        row_means = savgol_filter(row_means, 71, 2)
        
        if False:
            plt.plot(row_means)
            plt.show()
        
        # Create binary classifier for whether the smooothed density estimate is above or below
        # a given threshold
        row_idxs = []
        for i in range(len(row_means)):
            if row_means[i] < self._row_means_multiplier * np.median(row_means):
                row_idxs.append(1)
            else:
                row_idxs.append(0)
        
        #
        row_idxs = ''.join(map(str,row_idxs))
        line_idxs = [ i.start() for i in re.finditer('01',row_idxs) ]
        line_idxs.append(0)
        line_idxs.append(len(columns[0]))
        line_idxs = sorted(line_idxs)
        
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
            
            if True:
                self._display_image(columns[i],0)
        
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
        column_idxs = []
        for i in range(len(column_means)):
            if column_means[i] < self._column_means_multiplier * np.median(column_means):
                column_idxs.append(1)
            else:
                column_idxs.append(0)
                
        # Find columns of pixels where the smoothed density estimate crosses the threshold
        # going from 0 to 1
        column_idxs = ''.join(map(str,column_idxs))
        line_idxs = [ i.start() for i in re.finditer('01',column_idxs) ]
        line_idxs.append(0)
        line_idxs.append(len(image[0]))
        line_idxs = sorted(line_idxs)
        
        # Isolate the columns corresponding to the N widest intervals between crossings of the 
        # threshold going from 0 to 1 where N is input number of columns expected
        num_preliminary_columns = len(line_idxs)-1
        column_widths = []
        columns = []
        for i in range(num_preliminary_columns):
            column_widths.append(line_idxs[i+1] - line_idxs[i])
            columns.append(image[:, line_idxs[i]:line_idxs[i+1]])
        cut_width = sorted(column_widths, reverse=True)[self._num_columns - 1]
        isolated_columns = []
        for i in range(len(column_widths)):
            if column_widths[i] >= cut_width:
                isolated_columns.append(columns[i])
                
                if False:
                    self._display_image(columns[i],0)

        # Return isolated columns
        return isolated_columns
    
    #
    def _read_page_image(self, page_num):
        args = [ self._gs_exe, '-dNOPAUSE', '-sDEVICE=jpeg', '-r' + str(self._dpi) + 'x' + str(self._dpi), 
                '-dFirstPage=' + str(page_num), '-dLastPage=' + str(page_num), 
                '-sOutputFile=' + self._jpg_tmp_file, self._pdf_input_file ]
        output = Popen(args)
        sleep(self._sleep)
        image = cv2.imread(self._jpg_tmp_file)
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
    def run(self, page_num, segment_jpgs_dir):
        
        # Read page image
        image = self._read_page_image(page_num)  
        
        #
        image = self._deskew_image(image)
        image = self._image_mask(image, False)
        
        #
        self._display_image(image, 0)
        
        #
        columns = self._isolate_columns_of_text(image)
        columns = self._isolate_blocks_of_text(columns)
        
        #
        segment_ctr = 0
        segment_map = []
        for i in range(len(columns)):
            segment_map_tmp = []
            segment_map_tmp.append(i)
            segment_map_tmp.append(segment_ctr)
            segment_ctr = self._segment_column(columns[i], segment_ctr, segment_jpgs_dir)
            segment_map_tmp.append(segment_ctr)
            segment_map.append(segment_map_tmp)
        return segment_map