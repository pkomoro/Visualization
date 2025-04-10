import pandas as pd
import numpy as np

import matplotlib.pyplot as plt

def plot_last_column(file_path):
    # Import the file with semicolon-separated values
    data = pd.read_csv(file_path, sep=';')
    
    # Ensure there is at least one column
    if data.shape[1] < 1:
        print("The file does not contain enough columns.")
        return
    
    # Plot the last column as a function of the index
    last_column_name = data.columns[-1]
    ydata = data[last_column_name]
    plt.plot(data.index, ydata)
    plt.yticks = np.arange(min(data[last_column_name]), max(data[last_column_name]), 0.1)
    plt.xlabel('Time [s]')
    plt.ylabel('Voltage [V]')
    # plt.show()
    plt.savefig(file_path + '.png')

# Example usage
if __name__ == "__main__":
    # Make sure to adjust the path according to your file location

    path = 'path'
    plot_last_column(path)