import pandas as pd
import numpy as np
import os
import csv


from methods import plot_columns_from_line, plot_selected_columns, plot_last_column_TSV, plot_eye_diagram

import matplotlib.pyplot as plt



# Example usage
if __name__ == "__main__":
    # Make sure to adjust the path according to your file location - use "/"
    # Get all files from the specified directory
    path = 'C:/Users/komor/OneDrive - Wojskowa Akademia Techniczna/Publikacje/Conferences/2026.10 - IRMMW/Symulacje wg'


    # Filter only CSV files from the directory
    files = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.csv')]

    
    for f in files:
        print(f)


    for f in files:
        with open(f, newline='', encoding='utf-8', errors='replace') as fh:
            rows = [row for row in csv.reader(fh) if row]
        rows = [row[0].split(' ') for row in rows]

        if not rows:
            print(f"Empty file {f}")
            continue
        
        max_cols = max(len(row) for row in rows)

        first_max_row = next((i for i, row in enumerate(rows) if len(row) == max_cols), None)

        header = rows[0]
        if len(header) < max_cols:
            header = header + [f"col_{i}" for i in range(len(header), max_cols)]
        
        data = [row + [''] * (max_cols - len(row)) for row in rows[1:]]
        df = pd.DataFrame(data, columns=header)

        xs_start = 0
        ys_start = 0

        for i, row_vals in enumerate(rows):
            for j, value in enumerate(row_vals):
                if "x(m)" in value:
                    xs_start = i
                elif "y(m)" in value:                    
                    ys_start = i
                
               

        

        xs_data = df.iloc[xs_start:ys_start-1].apply(pd.to_numeric, errors='coerce')
        xs_data = xs_data.dropna(axis=1, how='all')
        ys_data = df.iloc[ys_start:first_max_row-2].apply(pd.to_numeric, errors='coerce')
        ys_data = ys_data.dropna(axis=1, how='all')

               

        segment = df.iloc[int(first_max_row)-1:].apply(pd.to_numeric, errors='coerce')
        segment = segment.dropna(axis=1, how='all')


        if segment.empty:
            print(f"No numeric image data in {f}")
            continue

        img = segment.fillna(0).to_numpy()

        img = img.T

        #img = img **2

        

        xs_data = xs_data.to_numpy()
        xs_data = xs_data.flatten()

        ys_data = ys_data.to_numpy()
        ys_data = ys_data.flatten()

        print(xs_data.shape, ys_data.shape, img.shape)

        

        # y, x = np.meshgrid[xs_data, ys_data]

        fig2,ax2 = plt.subplots(figsize=(8,6))
        mesh2 = ax2.pcolormesh(xs_data, ys_data, img, cmap='jet', shading='auto')
        cbar2 = fig2.colorbar(mesh2, ax=ax2)
        cbar2.set_label("Rozkład pola",fontsize=12)
        ax2.set_aspect("equal")
        ax2.set_xlabel('Oś X [µm]', fontsize=12)
        ax2.set_ylabel('Oś Y [µm]', fontsize=12)
        plt.tight_layout()
        plt.savefig(os.path.join(path, f"plot_{os.path.basename(f).replace('.csv', '.jpg')}"), dpi=300, bbox_inches='tight')
        


        # print(f"Plotting {f} with shape {img.shape}")

        # plt.imshow(img, cmap='jet', aspect=1, interpolation='nearest')
        # plt.title(os.path.basename(f))
        # plt.xlabel("x [mm]")
        # plt.ylabel("y [mm]")
        # plt.xticks(ticks=np.linspace(0, img.shape[1]-1, 5), labels=np.linspace(-10, 10, 5).round(1))
        # plt.yticks(ticks=np.linspace(0, img.shape[0]-1, 5), labels=np.linspace(-10, 10, 5).round(1))
        # plt.colorbar(label="Intensity [a.u.]")
        # plt.tight_layout()
        # plt.savefig(os.path.join(path, f"plot_{os.path.basename(f).replace('.csv', '.jpg')}"), dpi=300, bbox_inches='tight')
        # plt.close()
        
        
    

        
    