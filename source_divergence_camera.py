import numpy as np
from matplotlib import pyplot as plt
from pathlib import Path
import pathlib
import re

if __name__ == "__main__":


    # path to the folder containing .npy files
    path ="D:\\OneDrive - Wojskowa Akademia Techniczna\\Pomiary\\Łącze THz\\Terasense 90 mW"

    
    paths = [f for f in Path(path).glob("*.npy")]

    print(*paths, sep='\n')

    ploting = True

    l = 3.21  # mm, wavelength of the beam
    w0 = 7.04  # mm, beam waist radius
    

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

    fig, ax = plt.subplots()
    # plt.figure(figsize=(6, 4))

    plt.xlabel('z [mm]')
    plt.ylabel('x [mm]')

    

    ax.set_facecolor('black')

    radii = [np.zeros(len(data[i])) for i in range(len(data))]
    radii2 = [np.zeros(len(data[i])) for i in range(len(data))]
    distances = [np.zeros(len(data[i])) for i in range(len(data))]

    image_positions = [0 for i in range(len(data))]
    object_positions = [0 for i in range(len(data))]

    for j in range(len(paths)):
        
        index = data_meta[j].find("Camera exposure setting:")
        data_meta[j] = data_meta[j][(index+25):]

        index = data_meta[j].find("Pixel size")
        exposure = int(data_meta[j][:(index-1)])

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

        z0 = 175
        

        image = np.swapaxes(data[j], 0, 2)
        image = np.flip(image,2)

        vmax = exposure_table[exposure]
        # vmax = np.max(data)
        

        if ploting:
            plt.imshow(image[int((y_stop-y_start)/1.5/2) + y,:,:], cmap='inferno', aspect = 'auto',
                    extent=[z0 + 300 - z_stop, z0 + 300 - z_start, y_start - (y_start + y_stop)/2, y_stop - (y_start + y_stop)/2], vmin = 0, vmax = vmax)

        distances[j] = z0 + 300 - z_start - np.arange(len(data[j]))*z_step

        ax.set_xlim(z0, z0+300)
        frames = 5
        ax.set_ylim(-5 * 24, 5 * 24)

        for k in range(len(data[j])):           
            threshold = 1/np.e**2 * np.max(data[j][k])
            radii[j][k] = np.sqrt(np.sum(data[j][k] > threshold) * 2.25 / np.pi)
            radii2[j][k] = np.sqrt(np.sum(data[j][k] > threshold) * 2.25 / np.pi)
        
    
    if ploting:
        combined_distances = np.concatenate(distances)
        combined_radii = np.concatenate(radii)
        coefficients = np.polyfit(combined_distances, combined_radii, 1)
        fit_line = np.poly1d(coefficients)
        sorted_distances = np.sort(combined_distances)

        ax.plot(sorted_distances,
                fit_line(sorted_distances),
                '--', color='cyan', linewidth=1)
        ax.plot(sorted_distances,
                -fit_line(sorted_distances),
                '--', color='cyan', linewidth=1)

        z_arrow = 440
        ax.annotate('', xy=(z_arrow, fit_line(z_arrow)), xytext=(z_arrow, -fit_line(z_arrow)),
                    arrowprops=dict(arrowstyle='<->', color='cyan', linewidth=1.5))

        plt.text(sorted_distances[-1], fit_line(sorted_distances[-1]), '$1/e^2$ diameter', va='bottom', ha='right', fontsize=11, color='cyan')


        plt.savefig(Path(path) / 'divergence_plot.jpg', dpi=1000, bbox_inches='tight')
        plt.savefig(Path(path) / 'divergence_plot.svg', bbox_inches='tight')
        plt.close()

    if ploting:
        plt.figure(figsize=(6, 4))

        combined_distances = np.concatenate(distances)
        combined_radii = np.concatenate(radii)
        coefficients = np.polyfit(combined_distances, combined_radii, 1)
        fit_line = np.poly1d(coefficients)
        angle_deg = np.degrees(np.arctan(coefficients[0]))
        print(f'Fit line: y = {coefficients[0]:.4f}x + {coefficients[1]:.4f}')
        print(f'Fit angle: {angle_deg:.4f} degrees')
        fitted_radii = fit_line(np.sort(combined_distances))
        sorted_distances = np.sort(combined_distances)

        
        plt.plot(combined_distances, combined_radii, 'o', markersize=4, label='Data')
        plt.plot(sorted_distances, fitted_radii, '--', color='cyan', linewidth=2, label='Linear fit')
        plt.xlabel('Distance (mm)')
        plt.ylabel('Radius (mm)')
        plt.title('Divergence of the beam')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.savefig(Path(path) / 'combined_divergence_plot.jpg', dpi=1000, bbox_inches='tight')
        plt.close()



   

    

