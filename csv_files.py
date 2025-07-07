import pandas as pd
import numpy as np
import os


from methods import plot_columns_from_line, plot_selected_columns, plot_last_column_TSV, plot_eye_diagram

import matplotlib.pyplot as plt



# Example usage
if __name__ == "__main__":
    # Make sure to adjust the path according to your file location - use "/"
    # Get all files from the specified directory
    path = 'path'
    # Filter only CSV files from the directory
    files = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.csv')]

    
    # Filter files containing a specific word in their names
    keyword = '2'
    files = [file for file in files if keyword in os.path.basename(file)]

    # Execute the plot_last_column function on each file
    for file in files:
        # plot_selected_columns(file, 3, [1])
        plot_eye_diagram(file, 3, [1], 3000)
        
    