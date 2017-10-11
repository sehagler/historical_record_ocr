#
import re

#
def correct_entries(entries):
    
    for i in range(len(entries)):
        
        #
        if len(entries[i]) > 3:
            if entries[i][:4] == '" " ':
                entries[i] = entries[i][2:]
        
        #
        if len(entries[i]) > 1:
            if entries[i][0] == '"' and entries[i][1] != ' ':
                num_dittos = len([j for j in range(len(entries[i])) if entries[i].startswith('"', j)])
                if num_dittos % 2 == 1:
                    entries[i] = '" ' + entries[i][1:]
    
    #
    return entries