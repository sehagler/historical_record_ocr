#
import numpy as np
from scipy import stats

#
def preliminary_stats(selected_column_widths, selected_column_heights):
    
    #
    trimmed_selected_column_widths = stats.trimboth(selected_column_widths, 0.1)
    mean_trimmed_selected_column_widths = np.mean(trimmed_selected_column_widths)
    std_trimmed_selected_column_widths = np.std(trimmed_selected_column_widths)
    
    #
    trimmed_selected_column_heights = stats.trimboth(selected_column_heights, 0.1)
    mean_trimmed_selected_column_heights = np.mean(trimmed_selected_column_heights)
    std_trimmed_selected_column_heights = np.std(trimmed_selected_column_heights)
    
    print("\n")
    print(mean_trimmed_selected_column_widths)
    print(std_trimmed_selected_column_widths)
    print(mean_trimmed_selected_column_heights)
    print(std_trimmed_selected_column_heights)
    
    #
    return mean_trimmed_selected_column_widths, std_trimmed_selected_column_widths, \
           mean_trimmed_selected_column_heights, std_trimmed_selected_column_heights,
    