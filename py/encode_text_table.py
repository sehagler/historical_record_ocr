#
import numpy as np
import re

#
class encode_text_table(object):
    
    # cluster x1 values into column indicies
    def _cluster_into_columns(self, text_table, num_rows):
        
        #
        for i in range(num_rows):
            x1 = []
            for j in range(len(text_table)):
                if text_table[j][5] == i:
                    x1.append(text_table[j][2])
            x1_sorted = np.sort(x1)
            x1_idxs = []
            idx = 0
            for j in range(len(x1_sorted)):
                x1_idxs.append([ x1_sorted[j], idx ])
                idx += 1
            for j in range(len(text_table)):
                if text_table[j][5] == i:
                    x1 = text_table[j][2]
                    for k in range(len(x1_idxs)):
                        if x1 == x1_idxs[k][0]:
                            text_table[j].append(x1_idxs[k][1])
                            
        #
        return text_table
    
    # cluster y1 values into row indicies
    def _cluster_into_rows(self, text_table):
    
        #
        YX1 = []; YX2 = []
        for i in range(len(text_table)):
            YX1.append([ text_table[i][1], text_table[i][2] ])
            YX2.append([ text_table[i][3], text_table[i][4] ])
        YX1 = np.array(YX1)
        YX2 = np.array(YX2)
        avg_boundingPoly_height = np.mean(YX2[:,0] - YX1[:,0])
        YX1_sorted = YX1[YX1[:,0].argsort()]
        YX2_sorted = YX2[YX2[:,0].argsort()]
        y1_clusters = []
        y1_cluster_label = 0
        for i in range(len(YX1_sorted[:,0]) - 1):
            y1_clusters.append([ YX1_sorted[i,0], y1_cluster_label ])
            if YX1_sorted[i+1,0] - YX1_sorted[i,0] > 0.5 * avg_boundingPoly_height:
                y1_cluster_label += 1
        y1_clusters.append([ YX1_sorted[-1,0], y1_cluster_label ])
        for i in range(len(text_table)):
            y1 = text_table[i][1]
            cluster = []
            for j in range(len(y1_clusters)):
                if y1 == y1_clusters[j][0]:
                    cluster.append(y1_clusters[j][1])
            text_table[i].append(cluster[0])
            
        #
        return text_table, y1_cluster_label
    
    # sort text table
    def _sort_text_table(self, text_table, num_rows):
        
        text_table_sorted = []
        for i in range(num_rows):
            row_raw = []
            for j in range(len(text_table)):
                if text_table[j][1] == i:
                    row_raw.append(text_table[j])
            row_sorted = []
            for j in range(len(row_raw)):
                for k in range(len(row_raw)):
                    if row_raw[k][2] == j:
                        row_sorted.append(row_raw[k])
            for j in range(len(row_sorted)):
                text_table_sorted.append(row_sorted[j])
                
        #
        return text_table_sorted
            
    #
    def run(self, text_table):
        
        #
        if text_table == 'Bad JSON File':
        
            text_table = [[ '*** BAD JSON FILE ***' , 0, 0, 0 ]]
            
        else:

            # cluster y1 values into row indicies
            text_table, y1_cluster_label = self._cluster_into_rows(text_table)

            num_rows = y1_cluster_label + 1

            # cluster x1 values into column indicies
            text_table = self._cluster_into_columns(text_table, num_rows)

            # identify indentation
            for i in range(len(text_table)):
                if text_table[i][6] == 0:
                    if text_table[i][2] < 15:
                        text_table[i].append(0)
                    elif text_table[i][2] > 15 and text_table[i][2] < 45:
                        text_table[i].append(1)
                    if text_table[i][2] > 45 and text_table[i][2] < 75:
                        text_table[i].append(2)
                    else:
                        text_table[i].append(3)
                else:
                    text_table[i].append(3)

            # clean up text table
            for i in range(len(text_table)):
                text_table[i] = [ text_table[i][0], text_table[i][5], 
                                  text_table[i][6], text_table[i][7] ]

            # sort text table
            text_table = self._sort_text_table(text_table, num_rows)
        
        return text_table    