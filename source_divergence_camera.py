from matplotlib.patches import Ellipse
import numpy as np
from matplotlib import axes, pyplot as plt
from pathlib import Path
import pathlib
import re
from scipy.optimize import curve_fit

def gaussian_2d(coordinates, amplitude, x0, y0, sigma_x, sigma_y, offset):
                    x, y = coordinates
                    exponent = -(((x - x0) ** 2) / (2 * sigma_x ** 2) + ((y - y0) ** 2) / (2 * sigma_y ** 2))
                    return offset + amplitude * np.exp(exponent)

if __name__ == "__main__":


    # path to the folder containing .npy files
    path ="C:\\Users\\komor\\OneDrive - Wojskowa Akademia Techniczna\\Pomiary\\Łącze THz\\Terasense 90 mW"

    
    paths = [f for f in Path(path).glob("*.npy")]

    print(*paths, sep='\n')

    ploting = True
    plotting_2D_gauss = True

    l = 3.21  # mm, wavelength of the beam
    w0 = 7.04  # mm, beam waist radius
    

    paths_meta = [f for f in Path(path).glob("*.meta")]
    
    data = paths.copy()

    data_meta = paths_meta.copy()
    pixel_sizes = []

    for i in range(len(paths)):
        data[i] = np.load(Path(paths[i]))

        file = open(Path(paths_meta[i]), "r")
        data_meta[i] = file.read()
        file.close()

    data_meta_copy = data_meta.copy()
    
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
    distances = [np.zeros(len(data[i])) for i in range(len(data))]


    for j in range(len(paths)):
        
        pixel_size_match = re.search(r"Pixel size[: ]*\s*([0-9]*\.?[0-9]+)", data_meta[j])
        pixel_size = float(pixel_size_match.group(1)) if pixel_size_match else 1.0
        pixel_sizes.append(pixel_size)

        index = data_meta_copy[j].find("Camera exposure setting:")
        data_meta_copy[j] = data_meta_copy[j][(index+25):]

        index = data_meta_copy[j].find("Pixel size")
        exposure = int(data_meta_copy[j][:(index-1)])

        index = data_meta_copy[j].find("Start Y")
        data_meta_copy[j] = data_meta_copy[j][(index+9):]

        index = data_meta_copy[j].find("mm")
        y_start = float(data_meta_copy[j][:(index-1)])

        index = data_meta_copy[j].find("Stop Y")
        data_meta_copy[j] = data_meta_copy[j][(index+8):]

        index = data_meta_copy[j].find("mm")
        y_stop = float(data_meta_copy[j][:(index-1)])

        index = data_meta_copy[j].find("Step Z")
        data_meta_copy[j] = data_meta_copy[j][(index+8):]

        index = data_meta_copy[j].find("mm")
        z_step = float(data_meta_copy[j][:(index-1)])

        index = data_meta_copy[j].find("Start Z")
        data_meta_copy[j] = data_meta_copy[j][(index+9):]

        index = data_meta_copy[j].find("mm")
        z_start = float(data_meta_copy[j][:(index-1)])

        index = data_meta_copy[j].find("Stop Z")
        data_meta_copy[j] = data_meta_copy[j][(index+8):]

        index = data_meta_copy[j].find("mm")
        z_stop = float(data_meta_copy[j][:(index-1)])

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
            threshold = 1/np.e**2 * np.mean(np.sort(data[j][k].flatten())[-500:])
            radii[j][k] = np.sqrt(np.sum(data[j][k] > threshold) * pixel_size ** 2 / np.pi)
        print(threshold)
    
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

        # plot vertical dotted lines at specified z positions (mm)
        for z_vert in (185, 325, 465):
            ax.axvline(x=z_vert, color='white', linestyle=':', linewidth=1)

        z_arrow = 400
        ax.annotate('', xy=(z_arrow, fit_line(z_arrow)), xytext=(z_arrow, -fit_line(z_arrow)),
                    arrowprops=dict(arrowstyle='<->', color='cyan', linewidth=1.5))

        plt.text(sorted_distances[-5], fit_line(sorted_distances[-5]), '$1/e^2$ diameter', va='bottom', ha='right', fontsize=11, color='cyan')

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

        
        plt.plot(combined_distances, combined_radii, 'o:', markersize=4, label='Data')
        plt.plot(sorted_distances, fitted_radii, '--', color='cyan', linewidth=2, label='Linear fit')
        # plot vertical dotted lines at specified z positions (mm)
        for z_vert in (185, 325, 465):
            plt.axvline(x=z_vert, color='black', linestyle=':', linewidth=1)
        plt.text(0.7, 0.95, f'$\\theta = {angle_deg:.2f}°$', transform=plt.gca().transAxes,
                 va='top', color='black', fontsize=11)
        
        plt.xlabel('Distance (mm)')
        plt.ylabel('Radius (mm)')
        plt.title('Divergence of the beam')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.savefig(Path(path) / 'combined_divergence_plot.jpg', dpi=1000, bbox_inches='tight')
        plt.close()

        for selected_j, selected_k in [(0, 1), (1, 0), (1, 28)]:
            selected_image = data[selected_j][selected_k]

            data_meta_copy = data_meta.copy()

            index = data_meta_copy[selected_j].find("Start Y")
            data_meta_copy[selected_j] = data_meta_copy[selected_j][(index+9):]
            index = data_meta_copy[selected_j].find("mm")
            y_start = float(data_meta_copy[selected_j][:(index-1)])
            index = data_meta_copy[selected_j].find("Stop Y")
            data_meta_copy[selected_j] = data_meta_copy[selected_j][(index+8):]
            index = data_meta_copy[selected_j].find("mm")
            y_stop = float(data_meta_copy[selected_j][:(index-1)])
            
            
            y_max_idx = int((y_stop-y_start)/1.5/2) + 0
            x_max_idx = len(selected_image[y_max_idx, :]) // 2
            
            print(f"Selected image: {selected_j}, {selected_k}, max intensity at (y, x): ({y_max_idx}, {x_max_idx})")
            profile = selected_image[y_max_idx, :]
            x_pixels = np.arange(profile.size)
            pixel_size = pixel_sizes[selected_j]
            x_positions = x_pixels * pixel_size
            selected_distance = distances[selected_j][selected_k]
            fitted_radius = fit_line(selected_distance)
            x_center = x_positions[x_max_idx]



            def gaussian_func(x, amplitude, center, sigma, offset):
                return amplitude * np.exp(-((x - center) ** 2) / (2 * sigma ** 2))

            amplitude_guess = profile.max() - profile.min()
            offset_guess = profile.min()
            sigma_guess = fitted_radius / 2 if fitted_radius > 0 else 1.0
            try:
                popt, _ = curve_fit(
                    gaussian_func,
                    x_positions,
                    profile,
                    p0=[amplitude_guess, x_center, sigma_guess, offset_guess],
                    bounds=([0, x_positions[0], 0, -np.inf], [np.inf, x_positions[-1], np.inf, np.inf]),
                    maxfev=10000,
                )
                fitted_amplitude, fitted_center, fitted_sigma, fitted_offset = popt
                gaussian_profile = gaussian_func(x_positions, *popt)
                fitted_radius_gauss = 2 * fitted_sigma
            except Exception:
                gaussian_profile = np.mean(np.sort(profile)[-5:]) * np.exp(
                    -((x_positions - x_center) ** 2) / (2 * (fitted_radius / 2) ** 2)
                )
                fitted_radius_gauss = fitted_radius

            gaussian_model = gaussian_func(
                x_positions,
                np.max(gaussian_profile),
                x_center,
                fitted_radius / 2 if fitted_radius > 0 else 1.0,
                offset_guess,
            )

            plt.figure(figsize=(6, 4))
            plt.plot(x_positions, profile, '-', label='Beam cross-section')
            plt.plot(x_positions, gaussian_profile, '--', label=f'Gaussian fit 1/e$^2$ radius = {fitted_radius_gauss:.2f} mm')
            plt.plot(x_positions, gaussian_model, ':', label=f'Gaussian from divergence radius = {fitted_radius:.2f} mm')
            plt.xlabel('x [mm]' if pixel_size != 1.0 else 'x [px]')
            plt.ylabel('Intensity')
            plt.title(f'Cross-section at selected distance {selected_distance:.1f} mm')
            plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=1)
            plt.subplots_adjust(bottom=0.25)
            plt.grid(True, alpha=0.3)
            plt.savefig(Path(path) / f'cross_section_gaussian_fit_distance_{selected_distance:.0f}mm.jpg', dpi=1000, bbox_inches='tight')
            plt.close()

            if plotting_2D_gauss:
                # fit 2D Gaussian profile to the selected image
                y_pixels = np.arange(selected_image.shape[0])
                x_pixels = np.arange(selected_image.shape[1])
                x_positions_2d = x_pixels * pixel_size
                y_positions_2d = y_pixels * pixel_size
                x_mesh, y_mesh = np.meshgrid(x_positions_2d, y_positions_2d)

                

                amplitude_guess_2d = selected_image.max() - selected_image.min()
                offset_guess_2d = selected_image.min()
                x0_guess_2d = x_center
                y0_guess_2d = y_max_idx * pixel_size
                sigma_x_guess_2d = fitted_radius / 2 if fitted_radius > 0 else 1.0
                sigma_y_guess_2d = sigma_x_guess_2d

                try:
                    popt2d, _ = curve_fit(
                        gaussian_2d,
                        (x_mesh.ravel(), y_mesh.ravel()),
                        selected_image.ravel(),
                        p0=[amplitude_guess_2d, x0_guess_2d, y0_guess_2d, sigma_x_guess_2d, sigma_y_guess_2d, offset_guess_2d],
                        bounds=(
                            [0, x_positions_2d[0], y_positions_2d[0], 0, 0, -np.inf],
                            [np.inf, x_positions_2d[-1], y_positions_2d[-1], np.inf, np.inf, np.inf],
                        ),
                        maxfev=20000,
                    )
                    amplitude_2d, x0_2d, y0_2d, sigma_x_2d, sigma_y_2d, offset_2d = popt2d
                    fitted_image_2d = gaussian_2d((x_mesh, y_mesh), *popt2d).reshape(selected_image.shape)
                except Exception:
                    amplitude_2d = amplitude_guess_2d
                    x0_2d = x0_guess_2d
                    y0_2d = y0_guess_2d
                    sigma_x_2d = sigma_x_guess_2d
                    sigma_y_2d = sigma_y_guess_2d
                    offset_2d = offset_guess_2d
                    fitted_image_2d = gaussian_2d((x_mesh, y_mesh), amplitude_2d, x0_2d, y0_2d, sigma_x_2d, sigma_y_2d, offset_2d).reshape(selected_image.shape)

                
                # Center images around 0 and fill with 0 up to ±80 pixels
                center_pixel_range = 80
                center_y = selected_image.shape[0] // 2
                center_x = selected_image.shape[1] // 2
                y_start = max(0, center_y - center_pixel_range)
                y_end = min(selected_image.shape[0], center_y + center_pixel_range)
                x_start = max(0, center_x - center_pixel_range)
                x_end = min(selected_image.shape[1], center_x + center_pixel_range)
                
                selected_image_centered = np.zeros((2 * center_pixel_range, 2 * center_pixel_range))
                fitted_image_2d_centered = np.zeros((2 * center_pixel_range, 2 * center_pixel_range))
                
                y_offset = center_pixel_range - (center_y - y_start)
                x_offset = center_pixel_range - (center_x - x_start)
                y_size = y_end - y_start
                x_size = x_end - x_start
                
                selected_image_centered[y_offset:y_offset + y_size, x_offset:x_offset + x_size] = selected_image[y_start:y_end, x_start:x_end]
                fitted_image_2d_centered[y_offset:y_offset + y_size, x_offset:x_offset + x_size] = fitted_image_2d[y_start:y_end, x_start:x_end]
                
                plt.figure(figsize=(10, 4))
                plt.subplot(1, 2, 1)
                plt.imshow(selected_image_centered, cmap='inferno', aspect='1', extent=[-80, 80, -80, 80])
                ellipse = Ellipse((0, 0), 2 * sigma_x_2d, 2 * sigma_y_2d, edgecolor='cyan', facecolor='none', linewidth=1.5)
                plt.gca().add_patch(ellipse)
                plt.title('Selected image (centered)')
                plt.colorbar()
                plt.xlabel('Pixels')
                plt.ylabel('Pixels')

                plt.subplot(1, 2, 2)
                plt.imshow(fitted_image_2d_centered, cmap='inferno', aspect='1', extent=[-80, 80, -80, 80])
                ellipse = Ellipse((0, 0), 2 * sigma_x_2d, 2 * sigma_y_2d, edgecolor='cyan', facecolor='none', linewidth=1.5)
                plt.gca().add_patch(ellipse)
                plt.title('2D Gaussian fit (centered)')
                plt.colorbar()
                plt.xlabel('Pixels')
                plt.ylabel('Pixels')

                plt.suptitle(
                    f'2D Gaussian fit at distance {selected_distance:.1f} mm, '
                    f'2sigma_x={2*sigma_x_2d:.2f} mm, 2sigma_y={2*sigma_y_2d:.2f} mm'
                )

                plt.savefig(Path(path) / f'selected_image_2d_gaussian_fit_distance_{selected_distance:.0f}mm.jpg', dpi=1000, bbox_inches='tight')
                plt.close()
                
                # Plot crosssections along 0,0 point
                plt.figure(figsize=(10, 6))
                center_idx = center_pixel_range
                
                # Horizontal crosssections (y=0)
                horizontal_selected = selected_image_centered[center_idx, :]
                horizontal_fitted = fitted_image_2d_centered[center_idx, :]
                
                # Vertical crosssections (x=0)
                vertical_selected = selected_image_centered[:, center_idx]
                vertical_fitted = fitted_image_2d_centered[:, center_idx]
                
                pixel_extent = np.linspace(-center_pixel_range, center_pixel_range, 2 * center_pixel_range)
                
                plt.plot(pixel_extent, horizontal_selected, label='Selected (horizontal)', linewidth=2)
                plt.plot(pixel_extent, horizontal_fitted, label='Fitted (horizontal)', linewidth=2, linestyle='--')
                plt.plot(pixel_extent, vertical_selected, label='Selected (vertical)', linewidth=2)
                plt.plot(pixel_extent, vertical_fitted, label='Fitted (vertical)', linewidth=2, linestyle='--')
                plt.axhline(y=amplitude_2d / np.exp(2), color='black', linestyle=':', linewidth=1)
                
                plt.xlabel('Pixels')
                plt.ylabel('Intensity')
                plt.title(f'Crosssections through center at distance {selected_distance:.1f} mm')
                plt.legend()
                plt.grid(True, alpha=0.3)
                
                plt.savefig(Path(path) / f'crosssections_2d_gaussian_fit_distance_{selected_distance:.0f}mm.jpg', dpi=1000, bbox_inches='tight')
                plt.close()
        



        

        # New: fit 2D gaussian to every frame to obtain 1/e^2 radii and plot divergence
        all_dist = []
        all_radii_2dx = []
        all_radii_2dy = []
        for j in range(len(paths)):
            pixel_size = pixel_sizes[j]
            for k in range(len(data[j])):
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
                    _, _, _, sigma_x_fit, sigma_y_fit, _ = popt2d
                    radius_1e2_x = 2 * sigma_x_fit
                    radius_1e2_y = 2 * sigma_y_fit

                except Exception:
                    # fallback to previous geometric area method
                    radius_1e2_x = radii[j][k]
                    radius_1e2_y = radii[j][k]
                    print(f"Warning: 2D Gaussian fit failed for frame {k} at distance {distances[j][k]:.1f} mm, using geometric area radius instead.")

                all_dist.append(distances[j][k])
                all_radii_2dx.append(radius_1e2_x)
                all_radii_2dy.append(radius_1e2_y)
        all_dist = np.array(all_dist)
        all_radii_2dx = np.array(all_radii_2dx)
        all_radii_2dy = np.array(all_radii_2dy)

        plt.figure(figsize=(6,4))
        # fit linear divergence
        coeffs = np.polyfit(all_dist, all_radii_2dx, 1)
        fit_line = np.poly1d(coeffs)
        angle_deg = np.degrees(np.arctan(coeffs[0]))

        print(f'Fit line x: y = {coeffs[0]:.4f}x + {coeffs[1]:.4f}')
        print(f'Fit angle: {angle_deg:.4f} degrees')
        print(f'Source positions: {-coeffs[1]/coeffs[0]:.4f}')

        sorted_idx = np.argsort(all_dist)
        plt.plot(all_dist, all_radii_2dx, 'o:', markersize=3, label='2D fit radii (X - H plane)')
        plt.plot(all_dist[sorted_idx], fit_line(all_dist[sorted_idx]), '--', color='cyan', linewidth=2, label=f'Linear fit, theta={angle_deg:.2f}°')

        # fit linear divergence
        coeffs = np.polyfit(all_dist, all_radii_2dy, 1)
        fit_line = np.poly1d(coeffs)
        angle_deg = np.degrees(np.arctan(coeffs[0]))

        print(f'Fit line y: y = {coeffs[0]:.4f}x + {coeffs[1]:.4f}')
        print(f'Fit angle: {angle_deg:.4f} degrees')
        print(f'Source positions: {-coeffs[1]/coeffs[0]:.4f}')

        sorted_idx = np.argsort(all_dist)
        plt.plot(all_dist, all_radii_2dy, 'o:', markersize=3, label='2D fit radii (Y - E plane)')
        plt.plot(all_dist[sorted_idx], fit_line(all_dist[sorted_idx]), '--', color='magenta', linewidth=2, label=f'Linear fit, theta={angle_deg:.2f}°')
        

        for z_vert in (185, 325, 465):
            plt.axvline(x=z_vert, color='black', linestyle=':', linewidth=1)
        
        plt.xlabel('Distance (mm)')
        plt.ylabel('1/e^2 diameter (mm)')
        plt.title('Divergence from 2D Gaussian fits')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.savefig(Path(path) / 'divergence_2d_fits_plot.jpg', dpi=1000, bbox_inches='tight')
        plt.close()



   

    







