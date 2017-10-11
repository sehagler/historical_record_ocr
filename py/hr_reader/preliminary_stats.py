#
import numpy as np
from scipy import stats

#
def preliminary_stats(column_widths, cut_widths, selected_column_widths):
    trimmed_selected_column_widths = stats.trimboth(selected_column_widths, 0.1)
    mean_trimmed_selected_column_widths = np.mean(trimmed_selected_column_widths)
    std_trimmed_selected_column_widths = np.std(trimmed_selected_column_widths)
    print(mean_trimmed_selected_column_widths)
    print(std_trimmed_selected_column_widths)
    return mean_trimmed_selected_column_widths, std_trimmed_selected_column_widths
    