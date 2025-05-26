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


def plot_eye_diagram(file_path, start_line, column_to_plot, points_per_interval):
    """
    Plots an eye diagram from a specified column of a CSV file.

    Parameters:
    - file_path: str, path to the CSV file.
    - start_line: int, number of lines to skip before reading the file.
    - column_to_plot: int, index of the column to plot.
    - points_per_interval: int, number of points per interval for the eye diagram.
    """
    # Import the file with semicolon-separated values, skipping rows before start_line
    data = pd.read_csv(file_path, skiprows=start_line, sep=',')
    
       
    # Extract the data for the specified column
    ydata = data.iloc[:, column_to_plot]
    
    # Split the data into intervals of the specified number of points
    num_intervals = len(ydata) // points_per_interval
    for i in range(num_intervals):
        interval_data = ydata[i * points_per_interval:(i + 1) * points_per_interval]
        plt.plot(range(points_per_interval), interval_data, alpha=0.5)  # Add transparency for overlapping lines
    
    plt.xlabel('Sample Index')
    plt.ylabel('Signal [V]')
    plt.title('Eye Diagram')
    plt.savefig(file_path + '_eye_diagram.png', dpi=300, bbox_inches='tight')
    plt.close()