# Imports
import cv2
import matplotlib.pyplot as plt
import numpy as np
from os import makedirs
from PIL import Image
from shutil import copyfile

#
class process_image(object):
    
    #
    def __init__(self, raw_image_dir, raw_image_file, processed_image_dir):
        
        #
        self._raw_image_dir = raw_image_dir
        self._raw_image_file = raw_image_file
        self._processed_image_dir = processed_image_dir

        #
        makedirs(self._processed_image_dir, exist_ok=True)
        
        #
        src = self._raw_image_dir + self._raw_image_file
        dst = self._processed_image_dir + self._raw_image_file
        copyfile(src, dst)
        
        #
        self._filename = self._processed_image_dir + self._raw_image_file
        
    #
    def _cv2_image_mask(self, image, invert_flg):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        if invert_flg:
            gray = cv2.bitwise_not(gray)
        mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        return mask
        
    #
    def apply_detail_filter(self):
        image = io.imread(self._filename)
        im = Image.fromarray(image)
        im = im.filter(ImageFilter.DETAIL)
        image = np.array(im)
        plt.imsave(self._filename, image, cmap=plt.cm.gray)
        
    #
    def apply_median_filter(self):
        image = io.imread(self._filename)
        im = Image.fromarray(image)
        im = im.filter(ImageFilter.MedianFilter)
        image = np.array(im)
        plt.imsave(self._filename, image, cmap=plt.cm.gray)
        
    #
    def apply_sharpen_filter(self):
        image = io.imread(self._filename)
        im = Image.fromarray(image)
        im = im.filter(ImageFilter.SHARPEN)
        image = np.array(im)
        plt.imsave(self._filename, image, cmap=plt.cm.gray)
        
    # 
    def deskew_image(self):
        image = cv2.imread(self._filename)
        mask = self._cv2_image_mask(image, True)
        coords = np.column_stack(np.where(mask > 0))
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h),
            flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        plt.imsave(self._filename, rotated, cmap=plt.cm.gray)
        
    #
    def image_mask(self, mask_flg):
        if mask_flg == '300dpi':
            image = color.rgb2gray(io.imread(self._filename))
            mask = image > 0.25
        elif mask_flg == '600dpi':
            image = cv2.imread(self._filename)
            mask = self._cv2_image_mask(image, False)
        else:
            print('Bad mask flag')
        plt.imsave(self._filename, mask, cmap=plt.cm.gray)