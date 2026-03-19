import os
import csv
from pathlib import Path
import numpy as np

import matplotlib.pyplot as plt

# Specify your path here
path = r'C:\Users\komor\OneDrive - Wojskowa Akademia Techniczna\Pomiary\Zachary Taylor\FMCW - pomiary wstępne\12.03.2026\Pulses'
script_dir = Path(path)


# Process all CSV files in the folder
csv_files = list(script_dir.glob('*.csv'))

if not csv_files:
    print("No CSV files found in the directory.")
else:
    for csv_file in csv_files:
        print(f"Processing: {csv_file.name}")
        
        try:
            data = []
            with open(csv_file, 'r') as f:
                reader = csv.reader(f)
                for i, row in enumerate(reader):
                    if i >= 2:  # Start from 3rd line (index 2)
                        if len(row) >= 3:
                            data.append([float(row[1]), float(row[2])])  # 2nd and 3rd columns

            data = np.array(data)

            
            if data.any():
                
                # Distance plot
                plt.figure(figsize=(10, 8))

                plt.plot(data[:100, 0])
                plt.title('Depth Scan')
                plt.xlabel('z [mm]')
                plt.ylabel('Amplitude')

                # Export to JPG
                output_file = script_dir / f"{csv_file.stem[18:]}_depth.jpg"
                plt.savefig(output_file, format='jpg', dpi=150, bbox_inches='tight')
                print(f"Exported: {output_file}")
                plt.close()


                # Frequency plot
                plt.figure(figsize=(10, 8))

                plt.plot(data[:, 1])
                plt.title('Mixer Frequency')
                plt.xlabel('Time [ps]')
                plt.ylabel('Amplitude')

                # Export to JPG
                output_file = script_dir / f"{csv_file.stem[18:]}_raw.jpg"
                plt.savefig(output_file, format='jpg', dpi=150, bbox_inches='tight')
                print(f"Exported: {output_file}")
                plt.close()


                # Frequency plot (zoomed y-axis)
                plt.figure(figsize=(10, 8))

                plt.plot(data[100:1000, 1])
                plt.title('Mixer Frequency (Zoomed)')
                plt.xlabel('Time [ps]')
                plt.ylabel('Amplitude')
                plt.ylim(-0.1, 0.1)

                # Export to JPG
                output_file = script_dir / f"{csv_file.stem[18:]}_raw_zoomed.jpg"
                plt.savefig(output_file, format='jpg', dpi=150, bbox_inches='tight')
                print(f"Exported: {output_file}")
                plt.close()
                

                
            else:
                print(f"No data found in {csv_file.name} after line 4.")
                
        except Exception as e:
            print(f"Error processing {csv_file.name}: {e}")

print("Done!")