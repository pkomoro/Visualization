import pandas as pd
import numpy as np
import os
import re

import matplotlib.pyplot as plt


# Example usage
if __name__ == "__main__":
    # Make sure to adjust the path according to your file location
    # Get all files from the specified directory
    path = r'C:\Users\komor\OneDrive - Wojskowa Akademia Techniczna\Pomiary\Łącze THz\Ogniska soczewek - PM4'
    
    plotting = False  # Set to True to enable per-file plotting, False to disable

    focal_length = 180  # mm, adjust based on your lens

    total_distance_map = {
        118: 320,
        158: 480,
        180: 570
    }
    total_distance = total_distance_map.get(focal_length, 570)  # default to 570 mm if focal length not found

    # List all .txt files from path starting with "f" followed by the focal length and ending with .txt
    txt_files = [f for f in os.listdir(path) if f.startswith('f'+ str(focal_length)) and f.endswith('.txt')]
    print(txt_files)

    d_values = []
    max_args = []
    max_args_fit = []
    max_values = []
    max_values_fit = []

    # Process each txt file
    for txt_file in txt_files:
        file_path = os.path.join(path, txt_file)

        # Read numeric data with comma as decimal point and tab separator
        data = pd.read_csv(file_path, sep='\t', decimal=',', header=None)

        # Extract the two last columns (columns 2 and 3, 0-indexed)
        col3 = data.iloc[:, 2]
        col4 = data.iloc[:, 3]

        if col4.empty:
            continue

        # Find argument in col3 where col4 reaches its maximum
        max_idx = col4.idxmax()
        arg_at_max = col3.iloc[max_idx]

        max_values.append(col4.iloc[max_idx])

        # Fit a line to the data
        coefficients = np.polyfit(col3, col4, 11)
        fit_line = np.poly1d(coefficients)
        fitted_values= fit_line(col3)
        max_values_fit.append(np.max(fitted_values))

        # Extract the number after 'd' from the filename
        base_name = os.path.splitext(txt_file)[0]
        d_match = re.search(r'd(\d+)', base_name)
        if d_match:
            d_value = int(d_match.group(1))
            d_values.append(d_value)
            max_args.append(arg_at_max)
            max_args_fit.append(col3.iloc[np.argmax(fitted_values)])
            print(f'{txt_file}: d={d_value}, arg_at_max={arg_at_max}')
        else:
            print(f'Warning: no "d<number>" found in {txt_file}')

        if plotting:
            # Plot the last columns (y) as a function of the 3rd column (x)
            plt.figure()
            plt.plot(col3, col4, label='Data')
            plt.plot(col3, fitted_values, linestyle='--', label='Fitted Curve')
            plt.legend()
            plt.xlabel('Distance [mm]')
            plt.ylabel('Power [mW]')
            plt.title(f'Data from {txt_file}')
            plt.grid(True)

            # Export image with original filename (replace .txt with .jpg)
            output_filename = txt_file.replace('.txt', '.jpg')
            output_path = os.path.join(path, output_filename)
            plt.savefig(output_path, dpi=500, bbox_inches='tight')
            plt.close()

            print(f'Saved plot for {txt_file}')

    if d_values:
        # Sort by d values for a clean plot
        sorted_indices = np.argsort(d_values)
        d_sorted = np.array(d_values)[sorted_indices] - total_distance + focal_length
        args_sorted = total_distance - d_sorted + np.array(max_args)[sorted_indices]
        args_fit_sorted = total_distance - d_sorted + np.array(max_args_fit)[sorted_indices]

        plt.figure()
        plt.plot(d_sorted, args_sorted, marker='o', linestyle='-', label='Actual Maximum')
        plt.plot(d_sorted, args_fit_sorted, marker='s', linestyle='--', label='Fitted Maximum')
        plt.xlabel('Object position [mm]')
        plt.ylabel('Image position [mm]')
        plt.title('Image vs Object Position for Focal Length ' + str(focal_length) + 'mm')
        plt.grid(True)
        plt.legend()

        # Also plot max power values on a secondary (right) y-axis
        max_values_sorted = np.array(max_values)[sorted_indices]
        max_values_fit_sorted = np.array(max_values_fit)[sorted_indices]
        ax_left = plt.gca()
        ax_right = ax_left.twinx()
        ax_right.plot(d_sorted, 50 * max_values_sorted, marker='^', color='C2', linestyle='-', label='Max Power')
        ax_right.plot(d_sorted, 50 * max_values_fit_sorted, marker='v', color='C2', linestyle='--', label='Fitted Max Power')
        ax_right.set_ylabel('Max Power [mW]', color='C2')
        ax_right.tick_params(axis='y', labelcolor='C2')
        
        # combine legends
        lines_left, labels_left = ax_left.get_legend_handles_labels()
        lines_right, labels_right = ax_right.get_legend_handles_labels()
        ax_left.legend(lines_left + lines_right, labels_left + labels_right, loc='best')
        
        

        summary_path = os.path.join(path, 'f' + str(focal_length) + 'mm_max_arg_vs_d.jpg')
        plt.savefig(summary_path, dpi=500, bbox_inches='tight')
        plt.close()
        print(f'Saved summary plot to {summary_path}')
    else:
        print('No d values found; summary plot not created.')
        

        



    