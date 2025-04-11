import pandas as pd
import numpy as np
import os

from methods import plot_columns_from_line

import matplotlib.pyplot as plt



# Example usage
if __name__ == "__main__":
    # Make sure to adjust the path according to your file location
    # Get all files from the specified directory
    path = 'path'
    # Filter only CSV files from the directory
    files = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.csv')]
    print(files)

    # Execute the plot_last_column function on each file
    for file in files:
        plot_columns_from_line(file,18)
    