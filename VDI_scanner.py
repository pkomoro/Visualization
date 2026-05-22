import pandas as pd
import numpy as np
import os

import matplotlib.pyplot as plt

from methods import plot_last_column


# Example usage
if __name__ == "__main__":
    # Make sure to adjust the path according to your file location
    # Get all files from the specified directory
    path = r'C:\Users\komor\OneDrive - Wojskowa Akademia Techniczna\Pomiary\Łącze THz\Ogniska soczewek - PM4'
    
    # List all .txt files from path starting with "f"
    
    txt_files = [f for f in os.listdir(path) if f.startswith('f') and f.endswith('.txt')]
    print(txt_files)

    plotting = False  # Set to True to enable plotting, False to disable
    
    # Process each txt file
    for txt_file in txt_files:
        file_path = os.path.join(path, txt_file)
        
        # Read numeric data with comma as decimal point and space as separator
        data = pd.read_csv(file_path, sep='\t', decimal=',', header=None)
               
        # Extract the two last columns (columns 2 and 3, 0-indexed)
        col3 = data.iloc[:, 2]
        col4 = data.iloc[:, 3]

        if plotting:
        
            # Plot the last columns (y) as a function of the 3rd column (x)
            plt.figure()
            plt.plot(col3, col4)
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
        

        



    