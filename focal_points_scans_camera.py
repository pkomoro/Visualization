import numpy as np
from matplotlib import pyplot as plt
from pathlib import Path
import pathlib
import re

if __name__ == "__main__":

    # path to the folder containing .npy files
    path ="C:/Users/komor/OneDrive - Wojskowa Akademia Techniczna/Pomiary/Łącze THz/Ogniska soczewek - kamera - 500m"

    paths = [f for f in Path(path).glob("*.npy")]

    print(*paths, sep='\n')

    ploting = True

    l = 3.21  # mm, wavelength of the beam
    w0 = 7.04  # mm, beam waist radius
    z0 = 14 + 5 # mm, distance from the lens to the scanner; +5mm for holder
    
    

    paths_meta = [f for f in Path(path).glob("*.meta")]
    
    data = paths.copy()

    data_meta = paths_meta.copy()

    for i in range(len(paths)):
        data[i] = np.load(Path(paths[i]))

        file = open(Path(paths_meta[i]), "r")
        data_meta[i] = file.read()
        file.close()

    for i in range(len(paths)):
        paths[i] = paths[i].absolute().as_posix()[:-4]

    exposure_table = [1, 2.8, 6.3, 13, 28, 113, 226, 453, 906, 1813]
    y = 0

    

    radii = [np.zeros(len(data[i])) for i in range(len(data))]
    radii2 = [np.zeros(len(data[i])) for i in range(len(data))]
    distances = [np.zeros(len(data[i])) for i in range(len(data))]

    image_positions = [0 for i in range(len(data))]
    object_positions = [0 for i in range(len(data))]

    for j in range(len(paths)):

        # print(f"Processing {paths[j]}")

        if "f300" in paths[j]:
            z0 = 114 + 5
        else:
            z0 = 14 + 5

        
        index = data_meta[j].find("Camera exposure setting:")
        data_meta[j] = data_meta[j][(index+25):]

        index = data_meta[j].find("Pixel size")
        exposure = int(data_meta[j][:(index-1)])

        index = data_meta[j].find("Start X")
        data_meta[j] = data_meta[j][(index+9):]
        
        index = data_meta[j].find("mm")
        x_start = float(data_meta[j][:(index-1)])
        
        index = data_meta[j].find("Stop X")
        data_meta[j] = data_meta[j][(index+8):]
        
        index = data_meta[j].find("mm")
        x_stop = float(data_meta[j][:(index-1)])

        index = data_meta[j].find("Start Y")
        data_meta[j] = data_meta[j][(index+9):]

        index = data_meta[j].find("mm")
        y_start = float(data_meta[j][:(index-1)])

        index = data_meta[j].find("Stop Y")
        data_meta[j] = data_meta[j][(index+8):]

        index = data_meta[j].find("mm")
        y_stop = float(data_meta[j][:(index-1)])

        index = data_meta[j].find("Step Z")
        data_meta[j] = data_meta[j][(index+8):]

        index = data_meta[j].find("mm")
        z_step = float(data_meta[j][:(index-1)])

        index = data_meta[j].find("Start Z")
        data_meta[j] = data_meta[j][(index+9):]

        index = data_meta[j].find("mm")
        z_start = float(data_meta[j][:(index-1)])

        index = data_meta[j].find("Stop Z")
        data_meta[j] = data_meta[j][(index+8):]

        index = data_meta[j].find("mm")
        z_stop = float(data_meta[j][:(index-1)])

        

        image = np.swapaxes(data[j], 0, 2)
        image = np.flip(image,2)

        vmax = exposure_table[exposure]
        # vmax = np.max(data)
        

        for k in range(len(data[j])):           
            threshold = 1/np.e**2 * np.max(data[j][k])
            radii[j][k] = np.sqrt(np.sum(data[j][k] > threshold) * 2.25 / np.pi)
            radii2[j][k] = np.sqrt(np.sum(data[j][k] > threshold) * 2.25 / np.pi)
        
        
        distances[j] = z0 + 300 - z_start - np.arange(len(data[j]))*z_step
        

        # Fit a line to the data
        z_range = len(distances[j])
        coefficients = np.polyfit(distances[j][int(z_range/4):int(3*z_range/4)], radii[j][int(z_range/4):int(3*z_range/4)], 7)
        fit_line = np.poly1d(coefficients)
        fitted_radii = fit_line(distances[j][int(z_range/4):int(3*z_range/4)])
        # angle_deg = np.degrees(np.arctan(coefficients[0]))

        image_positions[j] = distances[j][int(z_range/4) + np.argmin(fitted_radii)]

        # XZ plot
        if ploting:
            fig, ax = plt.subplots()
            plt.xlabel('z [mm]')
            plt.ylabel('x [mm]')
            ax.set_facecolor('black')
            ax.set_xlim(z0, z0+300)
            ax.set_ylim(-24, 24)
            plt.imshow(image[int((y_stop-y_start)/1.5/2) + y,:,:], cmap='inferno', aspect = 'auto', 
                       extent=[z0 + 300 - z_stop, z0 + 300 - z_start, y_start - (y_start + y_stop)/2, y_stop - (y_start + y_stop)/2])
            ax.axvline(image_positions[j], color='white', linestyle='--')
            ax.text(image_positions[j], 0.95, f'f = {image_positions[j]:.0f} mm',
                            transform=ax.get_xaxis_transform(), ha='left', va='bottom')
            plt.savefig(paths[j] + '_xz_y' + str(y) + 'px.jpg', dpi = 300, bbox_inches='tight')
            # plt.savefig(paths[2*j] + '_xz_y' + str(y) + 'px.svg')
            plt.close()

        # XY plot
        if ploting:
            plt.figure()
            plt.imshow(image[:,:, -int((z0 + 300 - z_start - image_positions[j]) / z_step)], cmap='inferno', aspect = 'auto',
                       extent=[x_start - (x_start + x_stop)/2, x_stop - (x_start + x_stop)/2, y_start - (y_start + y_stop)/2, y_stop - (y_start + y_stop)/2])
            print(f"Image position for {paths[j][-6:]}: {image_positions[j]:.2f} mm. Corresponding z index: {int((z0 + 300 - z_start - int(image_positions[j])) / z_step)} / {len(data[j])}")
            plt.xlabel('x [mm]')
            plt.ylabel('y [mm]')
            # plt.legend()
            plt.title('Beam profile at image position')
            plt.savefig(paths[j] + '_xy_z' + str(int(image_positions[j])) + 'mm.jpg', dpi = 300, bbox_inches='tight')
        

        # fitted radii plot
        if ploting:
            fig, ax = plt.subplots()
            plt.plot(distances[j], radii[j], 'o-')
            # plt.plot(distances[j], fitted_radii, 'r--', label=f'Fit: {angle_deg:.2f}°')
            plt.plot(distances[j][int(z_range/4):int(3*z_range/4)], fitted_radii, 'r--')
            ax.axvline(image_positions[j], color='black', linestyle='--')
            ax.text(image_positions[j], 0.95, f'f = {image_positions[j]:.0f} mm',
                transform=ax.get_xaxis_transform(), ha='left', va='bottom')
            
            # plt.legend()
            plt.xlabel('Distance (mm)')
            plt.ylabel('Radius (mm)')
            plt.title('Divergence of the beam')
    
            plt.savefig(paths[j] + '_divergence_plot.jpg', dpi=1000, bbox_inches='tight')
            # plt.savefig(paths[2*j] + '_divergence_plot.svg', bbox_inches='tight')
            plt.close()

        


    

