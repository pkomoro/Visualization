import pandas as pd
import numpy as np
import os

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
    plt.close()

def plot_columns_from_line(file_path, start_line):
    # Import the file with semicolon-separated values, skipping rows before start_line
    data = pd.read_csv(file_path, skiprows=start_line)
    
    # Ensure there are at least three columns
    if data.shape[1] < 3:
        print("The file does not contain enough columns.")
        return
    
    # Extract the first, second, and third columns
    xdata = data.iloc[:, 0]
    ydata1 = 100 * data.iloc[:, 1]
    ydata2 = data.iloc[:, 2] - 2.5
    
    # Plot the second and third columns against the first column
    plt.plot(xdata, ydata1, label='Signal')
    plt.plot(xdata, ydata2, label='Modulation')
    plt.xlabel('Time')
    plt.ylabel('Voltage [V]')
    plt.legend()
    plt.savefig(file_path + '_columns_plot.png')
    plt.close()

def plot_selected_columns(file_path, start_line, columns_to_plot):
    """
    Plots specified columns from a CSV file starting from a given line.

    Parameters:
    - file_path: str, path to the CSV file.
    - start_line: int, number of lines to skip before reading the file.
    - columns_to_plot: list of int, indices of the columns to plot.
    """
    # Import the file with semicolon-separated values, skipping rows before start_line
    data = pd.read_csv(file_path, skiprows=start_line, sep=',')
    
    # Ensure the specified columns exist
    # if max(columns_to_plot) >= data.shape[1]:
    #     print("One or more specified columns do not exist in the file.")
    #     return
    
    # Plot each specified column against the first column
    xdata = data.iloc[:, 0]
    for col_index in columns_to_plot:
        xdata = data.iloc[:, col_index - 1]/4000
        ydata = data.iloc[:, col_index]
        plt.plot(xdata, ydata, label=f'Column {col_index}')
    
    plt.xlabel('Time [us]')
    plt.ylabel('Signal [V]')
    # plt.legend()
    plt.savefig(file_path + '_selected_columns_plot.png', dpi = 300, bbox_inches='tight')
    plt.close()
