import numpy as np
from matplotlib import pyplot as plt
from matplotlib.patches import Circle, Ellipse
from pathlib import Path
import pathlib
import re
from scipy.optimize import curve_fit

from methods import GaussianBeam, Lens

def thin_lens_equation(u, f):
        return 1 / (1 / f - 1 / u)
    
def gaussian_lens_equation(s, f, w0, l):
    return 1 / (1 / f + 1 / (s + (np.pi * w0**2 / l)**2 / (s + f)))
    
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

def gaussian_2d(coordinates, amplitude, x0, y0, sigma_x, sigma_y, offset):
                    x, y = coordinates
                    exponent = -(((x - x0) ** 2) / (2 * sigma_x ** 2) + ((y - y0) ** 2) / (2 * sigma_y ** 2))
                    return amplitude * np.exp(exponent)

if __name__ == "__main__":

    # Source parameters
    wavelength = 3.21  # wavelength in mm
    source_waist_x = 5.1 # mm for WR10 small cone
    source_waist_y = 6.1 # mm for WR10 small cone
    optics_diameter = 187  # diameter of the lenses in mm
    P0 = 93.45  # mW, source power

    lens_thickness = 2  # mm, thickness of the lens

    # focal_length = 118  # mm, adjust based on your lens
    for focal_length in [118]:  # mm, focal lengths of the lenses used in the experiment

        
        # source_distance_shift = 8.5
        # focal_length_scaling_factor = 0.904
        # diameter_reduction = 0.75

        # source_distance_shift = 0.5
        # focal_length_scaling_factor = 0.866
        # diameter_reduction = 0.63
        
        # source_distance_shift = 11.3
        # focal_length_scaling_factor = 0.914
        # diameter_reduction = 0.7

        # source_distance_shift = 20
        # focal_length_scaling_factor = 0.98
        # diameter_reduction = 0.7

        # source_distance_shift = -9
        # focal_length_scaling_factor = 0.86
        # diameter_reduction = 0.61

        # 2max 180mm
        # source_distance_shift = 10
        # focal_length_scaling_factor = 0.9
        # diameter_reduction = 0.71

        # 2max all lenses
        # source_distance_shift = 6
        # focal_length_scaling_factor = 0.91
        # diameter_reduction = 0.7

        # 2max all lenses
        # source_distance_shift = 0
        # focal_length_scaling_factor = 0.885
        # diameter_reduction = 0.635

        # 2max all lenses waist + image position; weights = 1:1
        # source_distance_shift = 25
        # focal_length_scaling_factor = 1
        # diameter_reduction = 0.81

        # 2max all lenses waist + image position; weights = 1:2
        # source_distance_shift = 21
        # focal_length_scaling_factor = 1
        # diameter_reduction = 0.83

        # 2max all lenses waist + image position; weights = 1:5
        # source_distance_shift = 18
        # focal_length_scaling_factor = 1
        # diameter_reduction = 0.86

        # 2max all lenses waist + image position; weights = 1:5
        # source_distance_shift = 14
        # focal_length_scaling_factor = 1.01
        # diameter_reduction = 0.86

        # 2max all lenses only image position
        # source_distance_shift = 2
        # focal_length_scaling_factor = 1.04
        # diameter_reduction = 0.7

        # all lenses only image position - gaussian
        # source_distance_shift = 10
        # focal_length_scaling_factor = 0.98
        # diameter_reduction = 1

        # all lenses only image position - gaussian
        # source_distance_shift_map = {
        #     118: 0,
        #     158: 5,
        #     180: 10
        # }
        # focal_length_scaling_factor_map = {
        #     118: 0.97,
        #     158: 0.9775,
        #     180: 0.9625
        # }
        # source_distance_shift = source_distance_shift_map.get(focal_length, 0)  # default to 0 if focal length not found
        # focal_length_scaling_factor = focal_length_scaling_factor_map.get(focal_length, 1)  # default to 1 if focal length not found
        # diameter_reduction = 0.8

        # all lenses + waist scalling
        # source_distance_shift = 10
        # focal_length_scaling_factor = 0.98
        # diameter_reduction = 0.8

        # 118 mm image position + waist scalling
        # source_distance_shift = 4.75
        # focal_length_scaling_factor = 0.975
        # source_waist_scaling_factor = 0.7475
        # diameter_reduction = 0.615

        # 158 mm image position + waist scalling
        # source_distance_shift = 8
        # focal_length_scaling_factor = 0.97125
        # source_waist_scaling_factor = 0.7
        # diameter_reduction = 0.65

        # 180 mm image position + waist scalling
        # source_distance_shift = 19
        # focal_length_scaling_factor = 0.9625
        # source_waist_scaling_factor = 0.715
        # diameter_reduction = 0.725

        '''Corrected signs in gaussian_lens_equation'''
        # 180 mm image position + waist scalling
        # source_distance_shift = 15.75
        # focal_length_scaling_factor = 0.965
        # source_waist_scaling_factor = 0.62
        # diameter_reduction = 0.72

        # 158 mm image position + waist scalling
        # source_distance_shift = 4.0
        # focal_length_scaling_factor = 0.97375
        # source_waist_scaling_factor = 0.615
        # diameter_reduction = 0.65

        # 118 mm image position + waist scalling
        # source_distance_shift = 0
        # focal_length_scaling_factor = 0.98375
        # source_waist_scaling_factor = 0.65
        # diameter_reduction = 0.61

        '''New waist and source divergence -  2D gaussian fit 11.4 degrees'''

        # 118 mm image position + waist scalling
        # source_distance_shift = 2
        # focal_length_scaling_factor = 0.983
        # source_waist_scaling_factor = 0.87
        # diameter_reduction = 0.61


        '''New waist and source divergence -  2D gaussian fit 11.4 degrees - separation of x and y axis'''
        # 118 mm image position + waist scalling
        source_distance_shift = 0
        focal_length_scaling_factor = 1
        source_waist_scaling_factor = 1
        diameter_reduction = 1


        lens_source_distance = 210 - source_distance_shift  # mm, distance from the source to the lens derived from positions on the rail (metadane)
        total_distance_map = {
            118: 320,
            158: 480,
            180: 570
        }
        total_distance = total_distance_map.get(focal_length, 570)  # default to 570 mm if focal length not found

        optics_diameter_adjusted = optics_diameter * diameter_reduction  # mm, adjusted optics diameter for theoretical calculations        

        focal_length_adjusted = focal_length * focal_length_scaling_factor  # mm, adjusted focal length for theoretical calculations

        source_waist_x_adjusted = source_waist_x * source_waist_scaling_factor  # mm, adjusted source waist for theoretical calculations
        source_waist_y_adjusted = source_waist_y * source_waist_scaling_factor  # mm, adjusted source waist for theoretical calculations


        # path to the folder containing .npy files
        path ="C:/Users/komor/OneDrive - Wojskowa Akademia Techniczna/Pomiary/Łącze THz/Ogniska soczewek - kamera"

        paths = [f for f in Path(path).glob("f" + str(focal_length) + "*.npy")]

        # print(*paths, sep='\n')

        ploting = False
        ploting_waist = True
        

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
        all_radii_2dx = [np.zeros(len(data[i])) for i in range(len(data))]
        all_radii_2dy = [np.zeros(len(data[i])) for i in range(len(data))]
        all_centers_2dx = [np.zeros(len(data[i])) for i in range(len(data))]
        all_centers_2dy = [np.zeros(len(data[i])) for i in range(len(data))]
        max_intensity = [np.zeros(len(data[i])) for i in range(len(data))]
        distances = [np.zeros(len(data[i])) for i in range(len(data))]

        image_positions = [0 for i in range(len(data))]
        image_positions2 = [0 for i in range(len(data))]
        image_positions3 = [0 for i in range(len(data))]
        image_positions_gauss2dx = [0 for i in range(len(data))]
        image_positions_gauss2dy = [0 for i in range(len(data))]
        object_positions = [0 for i in range(len(data))]

        waist = [0 for i in range(len(data))]
        waist_gauss2dx = [0 for i in range(len(data))]
        waist_gauss2dy = [0 for i in range(len(data))]

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
            
            pixel_size_match = re.search(r"Pixel size[: ]*\s*([0-9]*\.?[0-9]+)", data_meta[j])
            pixel_size = float(pixel_size_match.group(1)) if pixel_size_match else 1.0
            
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
            

            if ploting:
                plt.imshow(image[int((y_stop-y_start)/1.5/2) + y,:,:], cmap='inferno', aspect = 'auto',
                        extent=[z0 + 300 - z_stop, z0 + 300 - z_start, y_start - (y_start + y_stop)/2, y_stop - (y_start + y_stop)/2], vmin = 0, vmax = vmax)
                plt.xlabel('z [mm]')
                plt.ylabel('y [mm]')

            distances[j] = z0 + 300 - z_start - np.arange(len(data[j]))*z_step

            ax.set_xlim(z0, z0+300)
            ax.set_ylim(-24, 24)

            for k in range(len(data[j])):
                # Calculate the 1/e^2 radius based on the geometric area method
                threshold = 1/np.e**2 * np.mean(np.sort(data[j][k].flatten())[-2:])
                radii[j][k] = np.sqrt(np.sum(data[j][k] > threshold) * 2.25 / np.pi)
                max_intensity[j][k] = np.max(data[j][k])

                # Fit a 2D Gaussian to the image
                img = data[j][k]
                y_pixels = np.arange(img.shape[0])
                x_pixels = np.arange(img.shape[1])
                x_positions_2d = x_pixels * pixel_size
                y_positions_2d = y_pixels * pixel_size
                x_mesh, y_mesh = np.meshgrid(x_positions_2d, y_positions_2d)

                amplitude_guess_2d = img.max() - img.min()
                offset_guess_2d = img.min()
                # center guesses
                x0_guess_2d = x_positions_2d[img.shape[1]//2]
                y0_guess_2d = y_positions_2d[img.shape[0]//2]
                sigma_guess = radii[j][k] / 2 if radii[j][k] > 0 else 1.0

                try:
                    popt2d, _ = curve_fit(
                        gaussian_2d,
                        (x_mesh.ravel(), y_mesh.ravel()),
                        img.ravel(),
                        p0=[amplitude_guess_2d, x0_guess_2d, y0_guess_2d, sigma_guess, sigma_guess, offset_guess_2d],
                        bounds=(
                            [0, x_positions_2d[0], y_positions_2d[0], 0, 0, -np.inf],
                            [np.inf, x_positions_2d[-1], y_positions_2d[-1], np.inf, np.inf, np.inf],
                        ),
                        maxfev=10000,
                    )
                    _, x0_fit, y0_fit, sigma_x_fit, sigma_y_fit, _ = popt2d
                    all_radii_2dx[j][k] = 2 * sigma_x_fit
                    all_radii_2dy[j][k] = 2 * sigma_y_fit
                    all_centers_2dx[j][k] = x0_fit
                    all_centers_2dy[j][k] = y0_fit

                except Exception:
                    # fallback to previous geometric area method
                    all_radii_2dx[j][k] = radii[j][k]
                    all_radii_2dy[j][k] = radii[j][k]
                    all_centers_2dx[j][k] = x0_guess_2d
                    all_centers_2dy[j][k] = y0_guess_2d
                    print(f"Warning: 2D Gaussian fit failed for frame {k} at distance {distances[j][k]:.1f} mm, using geometric area radius instead.")

                
                

            
            if ploting:
                plt.savefig(paths[j] + '_xz_y' + str(y) + 'px.jpg', dpi = 300, bbox_inches='tight')
                plt.savefig(paths[j] + '_xz_y' + str(y) + 'px.svg', bbox_inches='tight')
                plt.close()

            

            
            image_positions2[j] = distances[j][np.argmin(radii[j])]
            image_positions3[j] = distances[j][np.argmax(max_intensity[j])]

            fit_range = 50
            fit_order = 10
            # Fit a line to the data
            min_radius_index = np.argmin(all_radii_2dx[j])
            fit_start_2dx = max(0, min_radius_index - fit_range)
            fit_end_2dx = min(len(distances[j]), min_radius_index + fit_range)
            print(f"Fitting range for 2D Gaussian fit (X): {fit_start_2dx} to {fit_end_2dx}")
            print(f"Distances for fitting (X): {len(distances[j][fit_start_2dx:fit_end_2dx])}, Radii for fitting (X): {len(all_radii_2dx[j][fit_start_2dx:fit_end_2dx])}")
            coefficients = np.polyfit(distances[j][fit_start_2dx:fit_end_2dx], all_radii_2dx[j][fit_start_2dx:fit_end_2dx], fit_order)
            fit_line = np.poly1d(coefficients)
            fitted_radii_2dx = fit_line(distances[j][fit_start_2dx:fit_end_2dx])
            waist_gauss2dx[j] = np.min(fitted_radii_2dx)
            image_positions_gauss2dx[j] = distances[j][fit_start_2dx + np.argmin(fitted_radii_2dx)]

            min_radius_index = np.argmin(all_radii_2dy[j])
            fit_start_2dy = max(0, min_radius_index - fit_range)
            fit_end_2dy = min(len(distances[j]), min_radius_index + fit_range)
            coefficients = np.polyfit(distances[j][fit_start_2dy:fit_end_2dy], all_radii_2dy[j][fit_start_2dy:fit_end_2dy], fit_order)
            fit_line = np.poly1d(coefficients)
            fitted_radii_2dy = fit_line(distances[j][fit_start_2dy:fit_end_2dy])
            waist_gauss2dy[j] = np.min(fitted_radii_2dy)
            image_positions_gauss2dy[j] = distances[j][fit_start_2dy + np.argmin(fitted_radii_2dy)]

            min_radius_index = np.argmin(radii[j])
            fit_start = max(0, min_radius_index - fit_range)
            fit_end = min(len(distances[j]), min_radius_index + fit_range)
            coefficients = np.polyfit(distances[j][fit_start:fit_end], radii[j][fit_start:fit_end], fit_order)
            fit_line = np.poly1d(coefficients)
            fitted_radii = fit_line(distances[j][fit_start:fit_end])
            waist[j] = np.min(fitted_radii)
            image_positions[j] = distances[j][fit_start + np.argmin(fitted_radii)]


            print(f"Lens position: {lens_d} mm, Object position: {object_positions[j]:.2f} mm, Image position (fit): {image_positions[j]:.2f} mm, Image position (min radius): {image_positions2[j]:.2f} mm, Image position (max intensity): {image_positions3[j]:.2f} mm, Waist: {waist[j]:.2f} mm")

            # Divergence plot
            if ploting:
                plt.figure()
                plt.plot(distances[j], radii[j], 'o-', label='Measured $1/e^2$ radius', markersize=4)
                plt.plot(distances[j], all_radii_2dx[j], 's-', label='2D Gaussian fit (X)', markersize=4)
                plt.plot(distances[j], all_radii_2dy[j], '^-', label='2D Gaussian fit (Y)', markersize=4)
                plt.plot(distances[j][fit_start_2dx:fit_end_2dx], fitted_radii_2dx, 'r--', label='Polynomial fit (X)')
                plt.plot(distances[j][fit_start_2dy:fit_end_2dy], fitted_radii_2dy, 'm--', label='Polynomial fit (Y)')
                plt.plot(distances[j][fit_start:fit_end], fitted_radii, 'b--', label='Polynomial fit (Geometric area)')
                plt.legend()
                plt.xlabel('Distance [mm]')
                plt.ylabel(r'$1/e^2$ radius [mm]')
                plt.ylim(0, 30)

                # plt.title('Divergence of the beam')
        
                plt.savefig(paths[j] + '_divergence_plot.jpg', dpi=1000, bbox_inches='tight')
                plt.savefig(paths[j] + '_divergence_plot.svg', bbox_inches='tight')
                plt.close()
            
            # Waist plot
            if ploting_waist:
                shift = 0
                vmax_change = 1
                circle_shift = 0
                # if paths[j].find('d630mm') != -1:
                #     shift = 100
                #     vmax_change = 0.1
                #     circle_shift = -5

                fig, axes = plt.subplots(1, 2, figsize=(12, 5))
                
                # Position indices for X and Y
                position_index_2dx = int(fit_start_2dx + np.argmin(fitted_radii_2dx) + shift)
                position_index_2dy = int(fit_start_2dy + np.argmin(fitted_radii_2dy) + shift)

                # show image with physical extent
                x_start_new = x_start - (x_stop + x_start)/2
                x_stop_new = x_stop - (x_stop + x_start)/2
                y_start_new = y_start - (y_stop + y_start)/2
                y_stop_new = y_stop - (y_stop + y_start)/2
                extent = [x_start_new, x_stop_new, y_start_new, y_stop_new]
                
                # Plot 1: X position
                img_2dx = data[j][position_index_2dx]
                im1 = axes[0].imshow(img_2dx, cmap='inferno', aspect='auto', extent=extent, vmin=0, vmax=vmax * vmax_change)
                ellipse_2dx = Ellipse((all_centers_2dx[j][position_index_2dx] + x_start_new, all_centers_2dy[j][position_index_2dx] + y_start_new), all_radii_2dx[j][position_index_2dx] * 2, all_radii_2dy[j][position_index_2dx] * 2, edgecolor='cyan', facecolor='none', linewidth=1.5)
                axes[0].add_patch(ellipse_2dx)
                axes[0].set_xlabel('x [mm]')
                axes[0].set_ylabel('y [mm]')
                axes[0].set_title('X waist position at z = {:.2f} mm'.format(distances[j][position_index_2dx]))
                plt.colorbar(im1, ax=axes[0], label='Intensity [a.u.]')
                
                # Plot 2: Y position
                img_2dy = data[j][position_index_2dy]
                im2 = axes[1].imshow(img_2dy, cmap='inferno', aspect='auto', extent=extent, vmin=0, vmax=vmax * vmax_change)
                ellipse_2dy = Ellipse((all_centers_2dx[j][position_index_2dy] + x_start_new, all_centers_2dy[j][position_index_2dy] + y_start_new), all_radii_2dx[j][position_index_2dy] * 2, all_radii_2dy[j][position_index_2dy] * 2, edgecolor='cyan', facecolor='none', linewidth=1.5)
                axes[1].add_patch(ellipse_2dy)
                axes[1].set_xlabel('x [mm]')
                axes[1].set_ylabel('y [mm]')
                axes[1].set_title('Y waist position at z = {:.2f} mm'.format(distances[j][position_index_2dy]))
                plt.colorbar(im2, ax=axes[1], label='Intensity [a.u.]')
                
                plt.tight_layout()
                plt.savefig(paths[j] + '_waist_plot.jpg', dpi=1000, bbox_inches='tight')
                plt.savefig(paths[j] + '_waist_plot.svg', bbox_inches='tight')
                plt.close()
            


    # Measured vs theoretical beam waist values

        # Save experimental results for this focal length to a CSV file
        experimental_data = np.vstack([
            object_positions,
            image_positions,
            image_positions2,
            image_positions3,
            image_positions_gauss2dx,
            image_positions_gauss2dy,
            waist,
            waist_gauss2dx,
            waist_gauss2dy,
        ]).T
        experimental_data_path = Path(path) / f"f{focal_length}mm_experimental_data.csv"
        np.savetxt(
            experimental_data_path,
            experimental_data,
            delimiter=',',
            header=('object_position_mm,image_position_fit_mm,image_position_min_radius_mm,'
                    'image_position_max_intensity_mm,image_position_gauss2dx_mm,'
                    'image_position_gauss2dy_mm,waist_geo_mm,waist_gauss2dx_mm,waist_gauss2dy_mm'),
            comments=''
        )

        object_positions_range = np.linspace(np.min(object_positions), np.max(object_positions), 100)  # Object positions

        beam1x = GaussianBeam(wavelength, source_waist_x_adjusted, 0)
        beam1y = GaussianBeam(wavelength, source_waist_y_adjusted, 0)
        lens1 = Lens(focal_length_adjusted, optics_diameter_adjusted, object_positions_range)
        beam2x = lens1.transform(beam1x)
        beam2y = lens1.transform(beam1y)

        thin_lens_waist_x = source_waist_x_adjusted * thin_lens_equation(object_positions_range, focal_length_adjusted) / object_positions_range
        thin_lens_waist_y = source_waist_y_adjusted * thin_lens_equation(object_positions_range, focal_length_adjusted) / object_positions_range

        # Kirchhoff integral plot 

        z_values = np.linspace(1 * focal_length_adjusted, 4 * focal_length_adjusted, 200)  # mm, range of z values to evaluate the Kirchhoff integral
        r_values = np.linspace(0, 24, 100)  # mm, range of r values to evaluate the Kirchhoff integral
        Kirchhoff_waist_x = []
        Kirchhoff_waist_y = []

        for idx, dis in enumerate(range(len(object_positions))):

            # progress monitor for the Kirchhoff loop
            end_char = '\n' if idx == len(object_positions) - 1 else '\r'
            print(f'Kirchhoff progress: {idx+1}/{len(object_positions)} -- object_pos = {object_positions[dis]:.3f} mm', end=end_char, flush=True)

            
            U_values = np.array([Kirchhoff_integral(0, 0, z, -object_positions[dis], focal_length_adjusted, source_waist_x_adjusted, wavelength, optics_diameter_adjusted / 2) for z in z_values])
            intensity = np.abs(U_values)**2

            max_value = np.max(intensity)
            max_index = np.argmax(intensity)
            max_z = z_values[max_index]      
            
            U_values = np.array([Kirchhoff_integral(r, 0, max_z, -object_positions[dis], focal_length_adjusted, source_waist_x_adjusted, wavelength, optics_diameter_adjusted / 2) for r in r_values])
            intensity = np.abs(U_values)**2

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

            Kirchhoff_waist_x.append(r_1e2)

            U_values = np.array([Kirchhoff_integral(0, 0, z, -object_positions[dis], focal_length_adjusted, source_waist_y_adjusted, wavelength, optics_diameter_adjusted / 2) for z in z_values])
            intensity = np.abs(U_values)**2

            max_value = np.max(intensity)
            max_index = np.argmax(intensity)
            max_z = z_values[max_index]      
            
            U_values = np.array([Kirchhoff_integral(r, 0, max_z, -object_positions[dis], focal_length_adjusted, source_waist_y_adjusted, wavelength, optics_diameter_adjusted / 2) for r in r_values])
            intensity = np.abs(U_values)**2

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

            Kirchhoff_waist_y.append(r_1e2)

            


        plt.close()
        plt.figure()
        # plt.plot(object_positions, waist, 'o-', label='Measured beam waist (Geometric area)', markersize=8)
        plt.plot(object_positions, waist_gauss2dx, 's-', label='Measured beam waist (2D Gaussian fit X)', markersize=8)
        plt.plot(object_positions, waist_gauss2dy, '^-', label='Measured beam waist (2D Gaussian fit Y)', markersize=8)
        # plt.plot(object_positions_range, beam2x.waist, 'r--', label='Gaussian beam waist - x axis')
        # plt.plot(object_positions_range, beam2y.waist, 'g--', label='Gaussian beam waist - y axis')
        # plt.plot(object_positions_range, thin_lens_waist_x, 'r:', label='Thin lens equation - x axis')
        # plt.plot(object_positions_range, thin_lens_waist_y, 'g:', label='Thin lens equation - y axis')
        plt.plot(object_positions, Kirchhoff_waist_x, 'b:', label='Kirchhoff integral - x axis')
        plt.plot(object_positions, Kirchhoff_waist_y, 'm:', label='Kirchhoff integral - y axis')
        plt.xlabel('Object Distance (mm)')   
        plt.ylabel('Beam Waist (mm)')
        plt.ylim(3, 16)

        # draw dashed lines for 2f and w0
        plt.axvline(2 * focal_length_adjusted, color='gray', linestyle='--', linewidth=1)
        plt.axhline(source_waist_x_adjusted, color='gray', linestyle='--', linewidth=1)
        plt.axhline(source_waist_y_adjusted, color='gray', linestyle='--', linewidth=1)
        ylim = plt.Axes.get_ylim(plt.gca())
        xlim = plt.Axes.get_xlim(plt.gca())
        plt.text(2 * focal_length_adjusted, ylim[0], ' 2f', color='gray', ha='left', va='bottom')
        plt.text(xlim[0], source_waist_x_adjusted, ' w0_x', color='gray', ha='left', va='bottom')
        plt.text(xlim[0], source_waist_y_adjusted, ' w0_y', color='gray', ha='left', va='bottom')

        plt.title(f'Comparison of Measured and Theoretical Beam Waist (f={focal_length} mm)')
        plt.legend()
        plt.savefig(path + '/f' + str(focal_length) + 'mm_beam_waist_comparison.jpg', dpi=1000, bbox_inches='tight')
        plt.close()


        # Measured vs theoretical image positions
        
        plt.figure(figsize=(10, 6))
        # plt.plot(object_positions, image_positions, 'o-', label='Experimental (fit)', linewidth=2, markersize=8)
        # plt.plot(object_positions, image_positions2, 'x-', label='Experimental (min radius)', linewidth=2, markersize=8)
        # plt.plot(object_positions, image_positions3, '+-', label='Experimental (max intensity)', linewidth=2, markersize=8)
        plt.plot(object_positions, image_positions_gauss2dx, 's-', label='Experimental (2D Gaussian fit X)', linewidth=2, markersize=8)
        plt.plot(object_positions, image_positions_gauss2dy, '^-', label='Experimental (2D Gaussian fit Y)', linewidth=2, markersize=8)
        object_distances = np.linspace(np.min(object_positions), np.max(object_positions), 40)  # mm, range of object distances to consider

        # theoretical_image_positions = thin_lens_equation(object_distances, focal_length * focal_length_scale)
        theoretical_image_positions_gaussian = gaussian_lens_equation(-object_distances, focal_length_adjusted, source_waist_x_adjusted, wavelength)

        # Plot comparison
            
        # plt.plot(object_distances, theoretical_image_positions, '--', label='Thin lens equation' + f' (scale: {focal_length_scale:.2f})', linewidth=2)
        # plt.plot(object_distances, theoretical_image_positions_gaussian, '--', label='Gaussian beam', linewidth=2)

        
        z_max_values = []
        z_values = np.linspace(focal_length + 10, 600.0, 200)  # mm, range of z values to evaluate the Kirchhoff integral
        a = optics_diameter_adjusted / 2  # mm, radius of the lens aperture


        
        for zs in object_distances:
            U_values = np.array([Kirchhoff_integral(0, 0, z, -zs, focal_length_adjusted, source_waist_x_adjusted, wavelength, optics_diameter_adjusted / 2) for z in z_values])
            intensity = np.abs(U_values)**2
            max_index = np.argmax(intensity)
            z_max_values.append(z_values[max_index])
            processed = len(z_max_values)
            total = len(object_distances)
            print(f"\rKirchhoff integral progress: {processed}/{total} object distances", end="", flush=True)
            if processed == total:
                print()
        plt.plot(object_distances, z_max_values, '--', label='Kirchhoff integral - x axis', linewidth=2)

        z_max_values = []
        for zs in object_distances:
                    U_values = np.array([Kirchhoff_integral(0, 0, z, -zs, focal_length_adjusted, source_waist_y_adjusted, wavelength, optics_diameter_adjusted / 2) for z in z_values])
                    intensity = np.abs(U_values)**2
                    max_index = np.argmax(intensity)
                    z_max_values.append(z_values[max_index])
                    processed = len(z_max_values)
                    total = len(object_distances)
                    print(f"\rKirchhoff integral progress: {processed}/{total} object distances", end="", flush=True)
                    if processed == total:
                        print()
        plt.plot(object_distances, z_max_values, '--', label='Kirchhoff integral - y axis', linewidth=2)
        
        
        plt.xlabel('Object Distance (mm)')
        plt.ylabel('Image Distance (mm)')
        plt.title('Object Positions: Experimental vs Theoretical')
        plt.axvline(2 * focal_length_adjusted, color='gray', linestyle='--', linewidth=1)
        plt.axhline(2 * focal_length_adjusted, color='gray', linestyle='--', linewidth=1)
        ylim = plt.Axes.get_ylim(plt.gca())
        xlim = plt.Axes.get_xlim(plt.gca())
        plt.text(2 * focal_length_adjusted, ylim[0], ' 2f', color='gray', ha='left', va='bottom')
        plt.text(xlim[0], 2 * focal_length_adjusted, ' 2f', color='gray', ha='left', va='bottom')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.savefig(path + '/f' + str(focal_length) + 'mm_object_positions_comparison.jpg', dpi=1000, bbox_inches='tight')
        plt.close()



        

