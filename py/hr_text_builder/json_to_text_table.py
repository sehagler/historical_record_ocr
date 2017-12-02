#
import json
import numpy as np
from os.path import isfile
import re

#
class json_to_text_table(object):
    
    #
    def __init__(self):
        
        #
        self._horizontal_min_offset = 50
    
    #
    def _filter_description(self, desc):
        
        # correct non-spurious non-ASCII characters to ASCII
        idx = re.search('\u00bd', desc)
        if idx:
            desc = desc[:idx.start()] + ' 1/2 ' + desc[idx.start()+6:]
        
        # remove spurious non-ASCII characters
        desc = ''.join([x for x in desc if ord(x) < 128])
        
        # remove spurious apostrophes
        apostrophe_idxs = []
        for i in range(len(desc)):
            if desc[i] == "'":
                apostrophe_idxs.append(i)
        for i in range(len(apostrophe_idxs)):
            if apostrophe_idxs[i] > 0 and apostrophe_idxs[i] < len(desc)-1:
                if desc[apostrophe_idxs[i] + 1] == "s":
                    del apostrophe_idxs[i]
        if apostrophe_idxs:
            apostrophe_idxs.sort(reverse=True)
            for idx in apostrophe_idxs:
                desc = desc[:idx] + desc[idx+1:]
        return desc
    
    #
    def _normalize_text_table_horizontal(self, text_table):
        x1 = sorted([ x[2] for x in text_table ])
        x1_min = min(x1)
        for i in range(len(text_table)):
            text_table[i][2] -= x1_min
            text_table[i][4] -= x1_min
        x1_min = - self._horizontal_min_offset
        for i in range(len(text_table)):
            text_table[i][2] -= x1_min
            text_table[i][4] -= x1_min
        return text_table
    
    #
    def _normalize_text_table_vertical(self, text_table):
        y1 = [ x[1] for x in text_table ]
        min_y1 = min(y1)
        for i in range(len(text_table)):
            text_table[i][1] -= min_y1
            text_table[i][3] -= min_y1
        return text_table
        
    # read text from json file
    def _read_text_table_from_json_file(self, json_file):
        with open(json_file) as myfile:    
            data = json.load(myfile)
        text_table = []
        for i in range(len(data["textAnnotations"])):
            if i > 0:
                desc = data["textAnnotations"][i]["description"]
                try:
                    y1 = data["textAnnotations"][i]["boundingPoly"]["vertices"][0]["y"]
                except:
                    y1 = data["textAnnotations"][i]["boundingPoly"]["vertices"][3]["y"] - 20
                try:
                    x1 = data["textAnnotations"][i]["boundingPoly"]["vertices"][0]["x"]
                except KeyError:
                    x1 = 0
                try:
                    y2 = data["textAnnotations"][i]["boundingPoly"]["vertices"][2]["y"]
                except:
                    y2 = data["textAnnotations"][i]["boundingPoly"]["vertices"][4]["y"] - 20
                try:
                    x2 = data["textAnnotations"][i]["boundingPoly"]["vertices"][2]["x"] 
                except KeyError:
                    x2 = 0
                desc = self._filter_description(desc)
                if len(desc) > 0:
                    text_table.append( [ desc, y1, x1, y2, x2 ])
        return text_table
            
    #
    def run(self, json_file):
        try:
            text_table = self._read_text_table_from_json_file(json_file)
            text_table = self._normalize_text_table_horizontal(text_table)
            text_table = self._normalize_text_table_vertical(text_table)
        except:
            text_table = 'Bad JSON File'
        return text_table      