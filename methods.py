from zipfile import Path

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


def plot_last_column_TSV(file_path):
    # Import the file with tab-separated values (for .txt files)
    data = pd.read_csv(file_path, sep='\t')
    
    # Ensure there is at least one column
    if data.shape[1] < 1:
        print("The file does not contain enough columns.")
        return
    
    # Plot the last column as a function of the index
    last_column_name = data.columns[-1]
    ydata = data[last_column_name]

    xdata = data.iloc[:, 0]

    plt.plot(xdata, ydata)
    plt.yticks(np.arange(min(ydata), max(ydata), 0.1))
    plt.xlabel('Angle [degrees]')
    plt.ylabel('Voltage [V]')
    plt.axhline(y=np.max(ydata)/2, color='g', linestyle='--')
    plt.axvline(x=15, color='r', linestyle='--')
    plt.axvline(x=2.6, color='b', linestyle='--')
    plt.axvline(x=23.1, color='b', linestyle='--')
    plt.savefig(file_path + '.jpg')
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

class GaussianBeam:
    def __init__(self, wavelength: float, waist: float, waist_position: float):        
        # Wavelength of radiation in [mm]
        self.wavelength = wavelength
        # Beam waist (1/e2 radius) in [mm]
        self.waist = waist
        # Beam waist position in space (one dimensional) in [mm]
        self.waist_position = waist_position
        # Rayleigh length in [mm]
        self.zR = np.pi * self.waist**2 / self.wavelength


    def radius(self, distance: float):
        return self.waist * np.sqrt(1 + ((distance - self.waist_position) / self.zR)**2)
    
    def divergence(self):
        return self.wavelength / np.pi / self.waist
    
    def power_through_aperture(self, r: float, z: float):
        T = 1 - np.exp(-2 * r ** 2 / self.radius(z) ** 2)
        return T


class Lens:
    def __init__(self, focal_length: float, diameter: float, position: float):        
        # Focal lenght in [mm]
        self.focal_length = focal_length
        # Diameter in [mm]
        self.diameter = diameter
        # Lens position in space (one dimensional) in [mm]
        self.position = position
    

    def transform(self, input: GaussianBeam):
        d1 = self.position - input.waist_position
        # if d1 <= 0:
        #     raise Exception("Lens positioned before waist of the input beam.")
        w2 = np.abs(self.focal_length) * input.waist / np.sqrt((d1 - self.focal_length)**2 + input.zR ** 2)
        d2 = self.focal_length + self.focal_length ** 2 * (d1 - self.focal_length) / ((d1 - self.focal_length) ** 2 + input.zR ** 2)

        return GaussianBeam(input.wavelength, w2, self.position + d2)
    


# Airy disk diameter (first minimum)
def airy_diameter(wavelength, focal_length, aperture_diameter):
    return 2.44 * wavelength * focal_length / aperture_diameter


class GaussianDistribution:
        def __init__(self, mean: float, stddev: float):
            self.mean = mean
            self.stddev = stddev

        def value(self, x: float):
            return (1 / (self.stddev * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - self.mean) / self.stddev) ** 2)

        
        def overlap(self, PW_beam_angle, PW_beam_diameter):
            # The product of a Gaussian beam with rectangular plane wave
            
            step = 0.01
            points = int(PW_beam_diameter / step) + 1  # Number of points for integration
            x = np.linspace(PW_beam_angle - PW_beam_diameter / 2, PW_beam_angle + PW_beam_diameter / 2, points)

            y = self.value(x)
            area_product = np.sum(y) * (x[1] - x[0]) / self.value(self.mean) / PW_beam_diameter  # Approximate integral using the trapezoidal rule

            return area_product

        def overlap_with_gaussian(self, other, range_multiplier=6, step=0.01):
            """Compute overlap area between two Gaussian distributions.

            The overlap area is defined as the integral of the minimum of the two
            probability density functions.
            """
            if not isinstance(other, GaussianDistribution):
                raise TypeError("other must be a GaussianDistribution")

            low = min(self.mean, other.mean) - range_multiplier * max(self.stddev, other.stddev)
            high = max(self.mean, other.mean) + range_multiplier * max(self.stddev, other.stddev)
            x = np.arange(low, high, step)
            y1 = self.value(x)
            y2 = other.value(x)
            overlap_area = np.sum(y1 * y2) * step
            theoretical_max = np.max(y1)
            print(f'Overlap area: {overlap_area}, Theoretical max: {theoretical_max}')

            return overlap_area / theoretical_max



        
