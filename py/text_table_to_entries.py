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
                        text += '\n" ' + text_table[i][0]
                    elif text_table[i][3] == 2:
                        text += ' ' + text_table[i][0]
                    else:
                        text += ' ' + text_table[i][0]

        text = ''.join(text)
        
        #
        entries = []
        idx = text.index('\n')
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
    def run(self, text_table):
        entries = self._generate_entries(text_table)
        return entries     