# Imports
import cv2
import matplotlib.pyplot as plt
import numpy as np
from os import makedirs
from PIL import Image
import re
from shutil import copyfile
from skimage import color, io
from sklearn.neighbors import KernelDensity

#
class process_page_image(object):
    
    #
    def __init__(self, page_image_dir, num_columns, dpi_flg):
        
        # Defined parameters
        self._approx_lines_per_segment = 15
        self._threshold = 245
        
        # Input parameters
        self._dpi_flg = dpi_flg
        self._num_columns = num_columns
        self._page_image_dir = page_image_dir
        
        # Parse DPI flag
        if dpi_flg == '300dpi':
            self._columns_bandwidth = 15
            self._column_means_threshold = -13
            self._rows_bandwidth = 15
            self._row_means_threshold = -13.4
            self._row_offset = 4
        elif dpi_flg == '600dpi':
            self._columns_bandwidth = 15
            self._column_means_threshold = -13.5
            self._rows_bandwidth = 15
            self._row_means_threshold = -13.4
            self._row_offset = 8
        else:
            print('Bad DPI flag')
        
        # Create data directories
        self._segments_dir = self._page_image_dir + "segments_tmp/"
        makedirs(self._page_image_dir, exist_ok=True)
        makedirs(self._segments_dir, exist_ok=True)
        
    # Deskew page image and make mask of image
    def _deskew_and_mask_page_image(self, image):
        
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
        
        # Create image mask
        deskewed_mask = self._image_mask(deskewed, False)
        
        # Return deskewed mask of image
        return deskewed_mask
    
    #
    def _detect_lines_of_text(self, image):
        row_mean = []
        for i in range(len(image)):
            row_mean.append(np.mean([ x for x in image[i] ]))
        row_idxs = []
        for i in range(len(row_mean)):
            if row_mean[i] > self._threshold:
                row_idxs.append(1)
            else:
                row_idxs.append(0)
        row_idxs = ''.join(map(str,row_idxs))
        row_idxs = row_idxs.replace('010','000')
        row_idxs = row_idxs.replace('101','111')
        row_idxs = row_idxs.replace('0110','0000')
        row_idxs = row_idxs.replace('1001','1111')
        line_idxs = [ i.start() + self._row_offset for i in re.finditer('01',row_idxs) ]
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
    def _isolate_columns_of_text(self, image):
        
        # Estimate density of edges along each column of pixels
        edges = cv2.Canny(image,0,0)
        column_means = [0] * len(edges[0])
        for i in range(len(edges)):
            column_means += edges[i]
        column_means = column_means // len(edges)
        column_means_graph = []
        for i in range(len(column_means)):
            column_means_graph.append([i, column_means[i]])
          
        # Use kernel density to smooth the density estimate
        kde = KernelDensity(kernel='gaussian', bandwidth=self._columns_bandwidth).fit(np.asarray(column_means_graph))
        column_means = kde.score_samples(column_means_graph)
        
        # Create binary classifier for whether the smooothed density estimate is above or below
        # a given threshold
        column_idxs = []
        for i in range(len(column_means)):
            if column_means[i] < self._column_means_threshold:
                column_idxs.append(1)
            else:
                column_idxs.append(0)
                
        # Find columns of pixels where the smoothed density estimate crosses the threshold
        # going from 0 to 1
        column_idxs = ''.join(map(str,column_idxs))
        line_idxs = [ i.start() + self._row_offset for i in re.finditer('01',column_idxs) ]
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

        # Return isolated columns
        return isolated_columns
    
    #
    def _isolate_rows_of_text(self, columns):
        
        #
        len_data = 0
        row_sums = [0] * len(columns[0])
        for i in range(len(columns)):
            edges = cv2.Canny(columns[i],0,0)
            len_data += len(edges[0])
            for j in range(len(edges)):
                row_sums[j] += sum(edges[j])
        row_means_graph = []
        for i in range(len(row_sums)):
            row_means_graph.append([ i, row_sums[i]/len_data ])         
            
        #
        kde = KernelDensity(kernel='gaussian', bandwidth=self._rows_bandwidth).fit(np.asarray(row_means_graph))
        row_means = kde.score_samples(row_means_graph)
        
        # Create binary classifier for whether the smooothed density estimate is above or below
        # a given threshold
        row_idxs = []
        for i in range(len(row_means)):
            if row_means[i] < self._row_means_threshold:
                row_idxs.append(1)
            else:
                row_idxs.append(0)
        
        #
        row_idxs = ''.join(map(str,row_idxs))
        line_idxs = [ i.start() + self._row_offset for i in re.finditer('01',row_idxs) ]
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
        
        #
        return columns
        
    #
    def _segment_column(self, column, segment_ctr):
        line_idxs = self._detect_lines_of_text(column)
        num_segments = (len(line_idxs)-1)//self._approx_lines_per_segment
        if len(line_idxs) > 2:
            for i in range(num_segments):
                idx0 = line_idxs[i*self._approx_lines_per_segment]
                idx1 = line_idxs[(i+1)*self._approx_lines_per_segment]
                segment = column[idx0:idx1]
                image_file = self._segments_dir + 'segment' + str(segment_ctr) + '.jpg'
                segment_ctr += 1
                plt.imsave(image_file, segment, cmap=plt.cm.gray)
            segment = column[idx1:]
            image_file = self._segments_dir + 'segment' + str(segment_ctr) + '.jpg'
            segment_ctr += 1
            plt.imsave(image_file, segment, cmap=plt.cm.gray)
        else:
            image_file = self._segments_dir + 'segment' + str(segment_ctr) + '.jpg'
            segment_ctr += 1
            plt.imsave(image_file, column, cmap=plt.cm.gray)
        return segment_ctr
               
    #
    def run(self, page_image_file):
        
        # Read page image
        image = cv2.imread(page_image_file)
        
        # Segment page image into columns
        image = self._deskew_and_mask_page_image(image)
        dirty_columns = self._isolate_columns_of_text(image)
        columns = self._isolate_rows_of_text(dirty_columns)
        
        #
        segment_ctr = 0
        segment_map = []
        for i in range(len(columns)):
            segment_map_tmp = []
            segment_map_tmp.append(i)
            segment_map_tmp.append(segment_ctr)
            segment_ctr = self._segment_column(columns[i], segment_ctr)
            segment_map_tmp.append(segment_ctr)
            segment_map.append(segment_map_tmp)
        return segment_map