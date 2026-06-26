import numpy as np
from matplotlib import pyplot as plt
from matplotlib.patches import Circle
from pathlib import Path
import pathlib
import re

from methods import GaussianBeam, Lens

def thin_lens_equation(u, f):
        return 1 / (1 / f - 1 / u)
    
def gaussian_lens_equation(s, f, w0, l):
    return 1 / (1 / f - 1 / (s + (np.pi * w0**2 / l)**2 / (s + f)))
    
def Kirchhoff_integral(r, theta, z, zs, f, ws, l, a):
        # Kazumasa Tanaka and Osamu Kanzaki, "Focus of a diffracted Gaussian beam through a finite aperture lens: experimental and numerical investigations," Appl. Opt. 26, 390-395 (1987)

    k = 2 * np.pi / l
    ksi0 = 2 * (0 - zs) / k / ws**2
    kappa0 = np.sqrt(2) / ws / np.sqrt(1 + ksi0**2)
    sigma0squared = 1 + 1j * ksi0

        
    # Define the grid for polar coordinates
    # r: radial distance, theta: azimuthal angle
    R = np.linspace(0, a, 100)  # Radial distance from 0 to aperture radius
    Theta = np.linspace(0, 2 * np.pi, 100)  # Azimuthal angle from 0 to 2*pi
    # Create a 2D meshgrid
    # R and Theta will be 2D arrays containing coordinate values for every point
    r0, theta0 = np.meshgrid(R, Theta)

    # U0 = kappa0 / np.sqrt(np.pi) * np.exp(1j * k * zs - 1 /2 * kappa0**2 * sigma0squared * r0**2 + 1j * np.atan(ksi0))
     
    # Define the function to integrate: f(r, theta)
        
    integrand = kappa0 / np.sqrt(np.pi) * np.exp(1j * k * zs - 1 /2 * kappa0**2 * sigma0squared * r0**2 + 1j * np.atan(ksi0) 
                                                     + 1j * k * r0**2 / 2 / f + 1j * k * r * r0 * np.cos(theta - theta0) / z - 1j * k * r0**2 / 2 / z) * r0

    # Perform 2D integration using the trapezoidal rule twice
    # Step 1: Integrate along the radial axis (axis=1) for each angle
    inner_integral = np.trapezoid(integrand, R, axis=1)

    # Step 2: Integrate the result along the angular axis (theta)
    final_result = np.trapezoid(inner_integral, Theta)

    U = 1j / l / z * np.exp(-1j * k * z - 1j * k * r**2 / 2 / z) * final_result

    return U

if __name__ == "__main__":

    # Source parameters
    wavelength = 3.21  # wavelength in mm
    source_waist = 7.04 # mm for WR10 small cone
    optics_diameter = 187  # diameter of the lenses in mm
    P0 = 93.45  # mW, source power

    lens_thickness = 0  # mm, thickness of the lens

    # focal_length = 118  # mm, adjust based on your lens
    for focal_length in [118, 158, 180]:  # mm, focal lengths of the lenses used in the experiment

        focal_length_import = focal_length  # mm, focal length of the lens used in the experiment

        # source_distance_shift = 8.5
        # focal_length_scaling_factor = 0.904
        # diameter_reduction = 0.75

        # source_distance_shift = 0.5
        # focal_length_scaling_factor = 0.866
        # diameter_reduction = 0.63
        
        # source_distance_shift = 11.3
        # focal_length_scaling_factor = 0.914
        # diameter_reduction = 0.7

        source_distance_shift = 10
        focal_length_scaling_factor = 0.95
        diameter_reduction = 0.9

        lens_source_distance = 210 - source_distance_shift  # mm, distance from the source to the lens derived from positions on the rail (metadane)
        total_distance_map = {
            118: 320,
            158: 480,
            180: 570
        }
        total_distance = total_distance_map.get(focal_length, 570)  # default to 570 mm if focal length not found

        optics_diameter = optics_diameter * diameter_reduction  # mm, adjusted optics diameter for theoretical calculations
        

        focal_length = focal_length * focal_length_scaling_factor  # mm, adjusted focal length for theoretical calculations


        # path to the folder containing .npy files
        path ="C:/Users/komor/OneDrive - Wojskowa Akademia Techniczna/Pomiary/Łącze THz/Ogniska soczewek - kamera"

        paths = [f for f in Path(path).glob("f" + str(focal_length_import) + "*.npy")]

        # print(*paths, sep='\n')

        ploting = False
        ploting_waist = False

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

        plt.xlabel('z [mm]')
        plt.ylabel('x [mm]')

        

        ax.set_facecolor('black')

        radii = [np.zeros(len(data[i])) for i in range(len(data))]
        max_intensity = [np.zeros(len(data[i])) for i in range(len(data))]
        distances = [np.zeros(len(data[i])) for i in range(len(data))]

        image_positions = [0 for i in range(len(data))]
        image_positions2 = [0 for i in range(len(data))]
        image_positions3 = [0 for i in range(len(data))]
        object_positions = [0 for i in range(len(data))]

        waist = [0 for i in range(len(data))]

        for j in range(len(paths)):
                
            match = re.search(r"lens_d(\d{3})", Path(paths[j]).name)
            lens_d = int(match.group(1)) if match else None

            print(f"Processing {paths[j]} with lens position {lens_d} mm")

            # koniec podstawki soczewki = 570 mm -> d = 360 mm od krawędzi anteny do środka soczewki
            # koniec podstawki soczewki = 430 | 20 | 690
            # koniec szyny z = 1 x 750 + 600 mm
            # z = 300 mm -> d = 570 mm od krawędzi anteny do powierzchni kamery
            
            object_positions[j] = lens_d - lens_source_distance # mm, distance from the object (source) to the lens derived from positions on the rail (metadane)
            z0 = total_distance - object_positions[j] - lens_thickness  # mm, distance from the lens to the camera derived from positions on the rail (metadane)
            
            
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

            

            image = np.swapaxes(data[j], 0, 2)
            image = np.flip(image,2)

            vmax = exposure_table[exposure]
            # vmax = np.max(data)
            

            if ploting:
                plt.imshow(image[int((y_stop-y_start)/1.5/2) + y,:,:], cmap='inferno', aspect = 'auto',
                        extent=[z0 + 300 - z_stop, z0 + 300 - z_start, y_start - (y_start + y_stop)/2, y_stop - (y_start + y_stop)/2], vmin = 0, vmax = vmax)

            distances[j] = z0 + 300 - z_start - np.arange(len(data[j]))*z_step

            ax.set_xlim(z0, z0+300)
            ax.set_ylim(-24, 24)

            for k in range(len(data[j])):

                threshold = 1/np.e**2 * np.mean(np.sort(data[j][k].flatten())[-3:])
                radii[j][k] = np.sqrt(np.sum(data[j][k] > threshold) * 2.25 / np.pi)
                max_intensity[j][k] = np.max(data[j][k])
            
            if ploting:
                plt.savefig(paths[j] + '_xz_y' + str(y) + 'px.jpg', dpi = 300, bbox_inches='tight')
                # plt.savefig(paths[2*j] + '_xz_y' + str(y) + 'px.svg')
                plt.close()

            

            # Fit a line to the data
            coefficients = np.polyfit(distances[j], radii[j], 11)
            fit_line = np.poly1d(coefficients)
            fitted_radii = fit_line(distances[j])
            # angle_deg = np.degrees(np.arctan(coefficients[0]))
            waist[j] = np.min(fitted_radii)

            image_positions[j] = distances[j][np.argmin(fitted_radii)]
            image_positions2[j] = distances[j][np.argmin(radii[j])]
            image_positions3[j] = distances[j][np.argmax(max_intensity[j])]

            # Divergence plot
            if ploting:
                plt.figure()
                plt.plot(distances[j], radii[j], 'o-')
                # plt.plot(distances[j], fitted_radii, 'r--', label=f'Fit: {angle_deg:.2f}°')
                plt.plot(distances[j], fitted_radii, 'r--')
                # plt.legend()
                plt.xlabel('Distance (mm)')
                plt.ylabel('Radius (mm)')
                plt.title('Divergence of the beam')
        
                plt.savefig(paths[j] + '_divergence_plot.jpg', dpi=1000, bbox_inches='tight')
                # plt.savefig(paths[2*j] + '_divergence_plot.svg', bbox_inches='tight')
                plt.close()
            
            # Waist plot
            if ploting_waist:
                plt.figure()
                plt.imshow(data[j][np.argmin(fitted_radii)], cmap='inferno', aspect = 'auto',
                        extent=[y_start - (y_start + y_stop)/2, y_stop - (y_start + y_stop)/2, y_start - (y_start + y_stop)/2, y_stop - (y_start + y_stop)/2], vmin = 0, vmax = vmax)

                waist_radius = np.min(fitted_radii)
                circle = Circle((0, 0), waist_radius, edgecolor='cyan', facecolor='none', linewidth=1.5)
                plt.gca().add_patch(circle)
                
                plt.title(f'Beam waist at z = {image_positions[j]:.2f} mm')
                plt.xlabel('X [mm]')
                plt.ylabel('Y [mm]')
                plt.colorbar(label='Intensity [a.u.]')
                plt.savefig(paths[j] + '_waist_plot.jpg', dpi=1000, bbox_inches='tight')
                plt.close()

    # Measured vs theoretical beam waist values

        object_positions_range = np.linspace(np.min(object_positions), np.max(object_positions), 100)  # Object positions

        beam1 = GaussianBeam(wavelength, source_waist, 0)
        lens1 = Lens(focal_length, optics_diameter, object_positions_range)
        beam2 = lens1.transform(beam1)

        thin_lens_waist = source_waist * thin_lens_equation(object_positions_range, focal_length) / object_positions_range

        # Kirchhoff integral plot 

        z_values = np.linspace(focal_length + 10, 600.0, 200)  # mm, range of z values to evaluate the Kirchhoff integral
        r_values = np.linspace(0, 24, 100)  # mm, range of r values to evaluate the Kirchhoff integral
        Kirchhoff_waist = []
        Kirchhoff_range = range(0,len(object_positions_range), 5)
        

        for idx, dis in enumerate(Kirchhoff_range):

            # progress monitor for the Kirchhoff loop
            end_char = '\n' if idx == len(Kirchhoff_range) - 1 else '\r'
            print(f'Kirchhoff progress: {idx+1}/{len(Kirchhoff_range)} -- object_pos = {object_positions_range[dis]:.3f} mm', end=end_char, flush=True)

            U_values = np.array([Kirchhoff_integral(0, 0, z, -object_positions_range[dis], focal_length, w0, l, optics_diameter / 2) for z in z_values])
            intensity = np.abs(U_values)**2

            # # Plot intensity as a function of z and display
            # plt.figure()
            # plt.plot(z_values, intensity, '-o')
            # plt.xlabel('z [mm]')
            # plt.ylabel('Intensity |U(0)|^2')
            # plt.title(f'On-axis intensity vs z (object pos {object_positions_range[dis]:.2f} mm)')
            # plt.grid(True)
            # plt.show()
            # plt.close()

            max_value = np.max(intensity)
            max_index = np.argmax(intensity)
            max_z = z_values[max_index]

            U_values = np.array([Kirchhoff_integral(r, 0, max_z, -object_positions_range[dis], focal_length, w0, l, optics_diameter / 2) for r in r_values])
            intensity = np.abs(U_values)**2
            
            # # Plot U_values as a function of r: amplitude and intensity
            # plt.figure()
            # plt.plot(r_values, intensity, label='Intensity |U(r)|^2')
            # plt.xlabel('r [mm]')
            # plt.ylabel('Amplitude / Intensity')
            # plt.title(f'U(r) at object pos {object_positions_range[dis]:.2f} mm, z = {max_z:.2f} mm')
            # plt.legend()
            # plt.grid(True)
            # plt.show()
            # plt.close()

            # Find radius at 1/e^2 of the maximum intensity
            threshold = max_value * np.exp(-2)
            below_indices = np.where(intensity <= threshold)[0]
            if below_indices.size > 0:
                first_below = below_indices[0]
                if first_below > 0:
                    r_lo, r_hi = r_values[first_below - 1], r_values[first_below]
                    I_lo, I_hi = intensity[first_below - 1], intensity[first_below]
                    if I_hi != I_lo:
                        r_1e2 = r_lo + (threshold - I_lo) * (r_hi - r_lo) / (I_hi - I_lo)
                    else:
                        r_1e2 = r_lo
                else:
                    r_1e2 = r_values[first_below]
            else:
                r_1e2 = np.nan

            Kirchhoff_waist.append(r_1e2)

            


        plt.close()
        plt.figure()
        plt.plot(object_positions, waist, 'o-', label='Measured beam waist')
        plt.plot(object_positions_range, beam2.waist, 'r--', label='Theoretical beam waist')
        plt.plot(object_positions_range, thin_lens_waist, 'g-.', label='Thin lens equation')
        plt.plot(object_positions_range[Kirchhoff_range], Kirchhoff_waist, 'b:', label='Kirchhoff integral')
        plt.xlabel('Object Distance (mm)')   
        plt.ylabel('Beam Waist (mm)')
        plt.ylim(3, 15)

        # draw dashed lines for 2f and w0
        plt.axvline(2 * focal_length, color='gray', linestyle='--', linewidth=1)
        plt.axhline(source_waist, color='gray', linestyle='--', linewidth=1)
        ylim = plt.Axes.get_ylim(plt.gca())
        xlim = plt.Axes.get_xlim(plt.gca())
        plt.text(2 * focal_length, ylim[0], ' 2f', color='gray', ha='left', va='bottom')
        plt.text(xlim[0], source_waist, ' w0', color='gray', ha='left', va='bottom')

        plt.title(f'Comparison of Measured and Theoretical Beam Waist (f={focal_length_import} mm)')
        plt.legend()
        plt.savefig(path + '/f' + str(focal_length_import) + 'mm_beam_waist_comparison.jpg', dpi=1000, bbox_inches='tight')
        plt.close()


        # Measured vs theoretical image positions
        '''
        plt.figure(figsize=(10, 6))
        plt.plot(object_positions, image_positions, 'o', label='Experimental (fit)', linewidth=2, markersize=8)
        plt.plot(object_positions, image_positions2, 'x', label='Experimental (min radius)', linewidth=2, markersize=8)
        plt.plot(object_positions, image_positions3, '+', label='Experimental (max intensity)', linewidth=2, markersize=8)
        object_distances = np.linspace(np.min(object_positions), np.max(object_positions), 100)  # mm, range of object distances to consider

        for focal_length_scale in np.linspace(0.97, 0.99, 3):  # Adjust this scale factor as needed to better match the experimental data
        
            # theoretical_image_positions = thin_lens_equation(object_distances, focal_length * focal_length_scale)
            theoretical_image_positions_gaussian = gaussian_lens_equation(object_distances, focal_length * focal_length_scale, w0, l)

            # Plot comparison
            
            # plt.plot(object_distances, theoretical_image_positions, '--', label='Thin lens equation' + f' (scale: {focal_length_scale:.2f})', linewidth=2)
            plt.plot(object_distances, theoretical_image_positions_gaussian, '--', label='Gaussian beam' + f' (scale: {focal_length_scale:.2f})', linewidth=2)


        
        z_max_values = []
        z_values = np.linspace(focal_length + 10, 600.0, 200)  # mm, range of z values to evaluate the Kirchhoff integral
        a = 187 / 2  # mm, radius of the lens aperture


        # Kirchhoff integral plot on object distance vs image distance

        # for dis in range(0,100,20):

        #     U_values = np.array([Kirchhoff_integral(z, -object_distances[dis], focal_length, w0, l, a) for z in z_values])
        #     intensity = np.abs(U_values)**2

        #     max_index = np.argmax(intensity)
        #     max_z = z_values[max_index]

        #     plt.figure(figsize=(10, 6))
        #     plt.plot(z_values, intensity, 'b--', linewidth=2, label='Intensity |U|^2')
        #     plt.axvline(x=max_z, color='r', linestyle='--', label=f'Max at z={max_z:.2f} mm')
        #     plt.xlabel('z (mm)')
        #     plt.ylabel('Field / Intensity')
        #     plt.ylim(0, 0.03)
        #     plt.title(f'Kirchhoff Integral for zs={object_distances[dis]:.2f} mm')
        #     plt.legend()
        #     plt.grid(True, alpha=0.3)
        #     plt.savefig(path + '/kirchhoff_u_values_plot_obj' + str(int(object_distances[dis])) + 'mm.jpg', dpi=300, bbox_inches='tight')
        #     plt.close()

    
            
        # Kirchhoff integrals for different apertures
        # for scale in [0.25, 0.5, 1, 2, 4]:

        #     a = 187 / 2  # mm, radius of the lens aperture
        #     z_max_values = []

        #     for zs in object_distances:
        #         U_values = np.array([Kirchhoff_integral(z, -zs, focal_length, w0, l, scale * a) for z in z_values])
        #         intensity = np.abs(U_values)**2
        #         max_index = np.argmax(intensity)
        #         z_max_values.append(z_values[max_index])
        #         processed = len(z_max_values)
        #         total = len(object_distances)
        #         print(f"\rKirchhoff integral progress: {processed}/{total} object distances", end="", flush=True)
        #         if processed == total:
        #             print()

        #     plt.plot(object_distances, z_max_values, '--', label='Kirchhoff integral' + f' (scale: {scale})', linewidth=2)
        
        for zs in object_distances:
            U_values = np.array([Kirchhoff_integral(z, -zs, focal_length, w0, l, a) for z in z_values])
            intensity = np.abs(U_values)**2
            max_index = np.argmax(intensity)
            z_max_values.append(z_values[max_index])
            processed = len(z_max_values)
            total = len(object_distances)
            print(f"\rKirchhoff integral progress: {processed}/{total} object distances", end="", flush=True)
            if processed == total:
                print()
        plt.plot(object_distances, z_max_values, 'b--', label='Kirchhoff integral', linewidth=2)
        
        
        plt.xlabel('Object Distance (mm)')
        plt.ylabel('Image Distance (mm)')
        plt.title('Object Positions: Experimental vs Theoretical')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.savefig(path + '/f' + str(focal_length) + 'mm_object_positions_comparison.jpg', dpi=1000, bbox_inches='tight')
        plt.close()

        '''

