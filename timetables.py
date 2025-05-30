import pandas as pd
import numpy as np
import os

import matplotlib.pyplot as plt

from methods import plot_last_column


# Example usage
if __name__ == "__main__":
    # Make sure to adjust the path according to your file location
    # Get all files from the specified directory
    path = 'path'
    files = [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and not f.endswith('.png')]
    print(files)

    # Execute the plot_last_column function on each file
    for file in files:
        plot_last_column(file)