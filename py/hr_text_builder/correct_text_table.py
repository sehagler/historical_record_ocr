#
def correct_text_table(text_table):
                
    # Correct for ditto signs that have been connected to first word
    for i in range(len(text_table)):
        for j in range(len(text_table[i])):
            if text_table[i][j][2] == 0:
                entry = text_table[i][j][0]
                if len(entry) > 2:
                    if entry[0] == '"' and entry[1] != ' ':
                        text_table[i][j][0] = '" ' + entry[1:]
                
    # Correct for missing ditto signs
    for i in range(len(text_table)):
        for j in range(len(text_table[i])):
            if text_table[i][j][2] == 0 and text_table[i][j][3] == 1:
                text_table[i][j][0] = '" ' + text_table[i][j][0]
              
    # Correct for merged rows
    for i in range(len(text_table)):
        row_idx_increment = 0
        for j in range(len(text_table[i])):
            if text_table[i][j][0][0] == '"' and \
               text_table[i][j][2] == 0 and \
               text_table[i][j][3] == 1:
                text_table[i][j][3] = 0
                row_idx_increment += 1
            text_table[i][j][1] += row_idx_increment      
 
    # Correct non-consecutive entry indicies
    for i in range(len(text_table)):
        entry_idx = -1
        for j in range(len(text_table[i])):
            if text_table[i][j][2] == 0:
                entry_idx += 1
            text_table[i][j][1] = entry_idx
        
    #
    return text_table