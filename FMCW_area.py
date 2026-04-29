import os
import csv
from pathlib import Path
import numpy as np

import matplotlib.pyplot as plt

# Specify your path here
path = r'C:\Users\komor\OneDrive - Wojskowa Akademia Techniczna\Pomiary\Zachary Taylor\FMCW - pomiary wstępne\19.03.2026\Area scans'
script_dir = Path(path)


# Process all CSV files in the folder
csv_files = list(script_dir.glob('*.csv'))

if not csv_files:
    print("No CSV files found in the directory.")
else:
    for csv_file in csv_files:
        print(f"Processing: {csv_file.name}")
        
        try:
            # Read CSV file starting from line 4 (index 3)
            data = []
            # Read size_y and size_x from 2nd row
            with open(csv_file, 'r') as file:
                reader = csv.reader(file)
                for i, row in enumerate(reader):
                    if i == 1:  # 2nd row (0-indexed)
                        size_y = int(float(row[0]))
                        size_x = int(float(row[1]))
                        break

            # Read data starting from line 4
            data = []
            with open(csv_file, 'r') as file:
                reader = csv.reader(file)
                for i, row in enumerate(reader):
                    if i >= 3:  # Start from 4th line
                        if len(data) < size_y * size_x:
                            data.append([float(val) for val in row])
                        else:
                            break

            data = np.array(data, dtype=float)  # Convert to NumPy array
            data_3d = data.reshape(size_y, size_x, -1)  # Reshape to 3D matrix
            
            
            
            
            
            if data.any():
                max_values = np.max(data_3d, axis=2)
                plt.figure(figsize=(10, 8))
                plt.imshow(max_values, cmap='viridis', origin='upper')
                plt.colorbar(label='Max Value')
                plt.title(f"{csv_file.stem}")

                if 'yz' in csv_file.stem:
                    plt.xlabel('Z')
                else:
                    plt.xlabel('X')
                plt.ylabel('Y')
                
                
                # Export to JPG
                output_file = script_dir / f"{csv_file.stem}.jpg"
                plt.savefig(output_file, format='jpg', dpi=150, bbox_inches='tight')
                print(f"Exported: {output_file}")
                plt.close()
            else:
                print(f"No data found in {csv_file.name} after line 4.")
                
        except Exception as e:
            print(f"Error processing {csv_file.name}: {e}")

print("Done!")