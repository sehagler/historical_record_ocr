#
import numpy as np
import re

#
class text_table_to_entries(object):
          
    #
    def _generate_entries(self, text_table):
        
        # transform table into entries
        text = []
        for i in range(len(text_table)):  
            if i == 0:
                text += text_table[i][0]
            else:
                if text_table[i][2] != 0:
                    text += ' ' + text_table[i][0]
                else:
                    if text_table[i][3] == 0:
                        text += '\n' + text_table[i][0]
                    elif text_table[i][3] == 1:
                        if text_table[i][0] == '"':
                            text += '\n' + text_table[i][0]
                        else:
                            text += ' ' + text_table[i][0]
                    elif text_table[i][3] == 2:
                        text += ' ' + text_table[i][0]
                    else:
                        text += ' ' + text_table[i][0]

        text = ''.join(text)
        
        #
        entries = []
        try:
            idx = text.index('\n')
        except:
            idx = -1
        while idx != -1:
            entries.append(text[:idx])
            text = text[idx+1:]
            try:
                idx = text.index('\n')
            except:
                idx = -1
        entries.append(text)
        return entries
    
    #
    def _join_text_table(self, text_table_segmented):
        offset = 0
        for i in range(len(text_table_segmented)):
            for j in range(len(text_table_segmented[i])):
                text_table_segmented[i][j][1] += offset
            offset = text_table_segmented[i][-1][1] + 1
        text_table_joined = []
        for i in range(len(text_table_segmented)):
            text_table_joined += text_table_segmented[i]
        return text_table_joined
    
    #
    def _text_table_stats(self, text_table):
        num_dittos = 0
        for i in range(len(text_table)):
            if text_table[i][0] == '"':
                num_dittos += 1
        num_lines = text_table[-1][1] + 1
        return num_lines, num_dittos
        
    #
    def run(self, text_table_segmented):
        text_table_joined = self._join_text_table(text_table_segmented)
        num_lines, num_dittos = self._text_table_stats(text_table_joined)
        entries = self._generate_entries(text_table_joined)
        return entries, num_lines, num_dittos  