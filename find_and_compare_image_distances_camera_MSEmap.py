import numpy as np
from matplotlib import pyplot as plt
from matplotlib.patches import Circle
from pathlib import Path
import pathlib
import re
from scipy.optimize import minimize
from multiprocessing import Pool
import itertools

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

# Source parameters
wavelength = 3.21  # wavelength in mm
source_waist = 7.04 # mm for WR10 small cone
optics_diameter = 187  # diameter of the lenses in mm
P0 = 93.45  # mW, source power

lens_thickness = 0  # mm, thickness of the lens

# Define objective function to minimize
def compute_mse(params):
        source_distance_shift, focal_length_scaling_factor, diameter_reduction = params
        total_mse = 0.0

        # print(f"Evaluating parameters: source_distance_shift={source_distance_shift}, focal_length_scaling_factor={focal_length_scaling_factor}, diameter_reduction={diameter_reduction}")

        optics_diameter_adjusted = optics_diameter * diameter_reduction
        
        for focal_length in [118, 158, 180]:  # mm, focal lengths of the lenses used in the experiment
            focal_length_import = focal_length
            lens_source_distance = 210 - source_distance_shift
            total_distance_map = {
                118: 320,
                158: 480,
                180: 570
            }
            total_distance = total_distance_map.get(focal_length, 570)
            
            focal_length_adjusted = focal_length * focal_length_scaling_factor
            
            path = "C:/Users/komor/OneDrive - Wojskowa Akademia Techniczna/Pomiary/Łącze THz/Ogniska soczewek - kamera"
            paths = [f for f in Path(path).glob("f" + str(focal_length_import) + "*.npy")]
            
            if not paths:
                continue
            
            paths_meta = [f for f in Path(path).glob("*.meta")]
            
            data = paths.copy()
            data_meta = paths_meta.copy()
            
            for i in range(len(paths)):
                data[i] = np.load(Path(paths[i]))
                file = open(Path(paths_meta[i]), "r")
                data_meta[i] = file.read()
                file.close()
            
            l = 3.21
            w0 = 7.04
            
            radii = [np.zeros(len(data[i])) for i in range(len(data))]
            distances = [np.zeros(len(data[i])) for i in range(len(data))]
            object_positions = [0 for i in range(len(data))]
            waist = [0 for i in range(len(data))]
            
            for j in range(len(paths)):
                match = re.search(r"lens_d(\d{3})", Path(paths[j]).name)
                lens_d = int(match.group(1)) if match else None
                
                object_positions[j] = lens_d - lens_source_distance
                z0 = total_distance - object_positions[j] - lens_thickness

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
                image = np.flip(image, 2)
                
                distances[j] = z0 + 300 - z_start - np.arange(len(data[j]))*z_step
                
                for k in range(len(data[j])):
                    threshold = 1/np.e**2 * np.mean(np.sort(data[j][k].flatten())[-3:])
                    radii[j][k] = np.sqrt(np.sum(data[j][k] > threshold) * 2.25 / np.pi)
                
                coefficients = np.polyfit(distances[j], radii[j], 11)
                fit_line = np.poly1d(coefficients)
                fitted_radii = fit_line(distances[j])
                waist[j] = np.min(fitted_radii)
            
            # Calculate Kirchhoff waist predictions
            z_values = np.linspace(focal_length_adjusted + 10, 600.0, 200)
            r_values = np.linspace(0, 24, 100)
            Kirchhoff_waist = []
            
            for dis in object_positions:
                U_values = np.array([Kirchhoff_integral(0, 0, z, -dis, focal_length_adjusted, w0, l, optics_diameter_adjusted / 2) for z in z_values])
                intensity = np.abs(U_values)**2
                max_value = np.max(intensity)
                max_index = np.argmax(intensity)
                max_z = z_values[max_index]
                
                U_values = np.array([Kirchhoff_integral(r, 0, max_z, -dis, focal_length_adjusted, w0, l, optics_diameter / 2) for r in r_values])
                intensity = np.abs(U_values)**2
                
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
            
            Kirchhoff_waist_array = np.array(Kirchhoff_waist)
            waist_array = np.array(waist)
            valid_mask = ~np.isnan(Kirchhoff_waist_array)
            if np.sum(valid_mask) > 0:
                mse_kirchhoff = np.mean((waist_array[valid_mask] - Kirchhoff_waist_array[valid_mask])**2)
                total_mse += mse_kirchhoff
        
        return total_mse



    
if __name__ == '__main__':

    path = "C:/Users/komor/OneDrive - Wojskowa Akademia Techniczna/Pomiary/Łącze THz/Ogniska soczewek - kamera"
    bounds = [(-10, 20), (0.8, 1), (0.75, 0.9)]  # bounds for source_distance_shift, focal_length_scaling_factor, and diameter_reduction

    # grid resolution for each parameter (can be adjusted)
    grid_points = (21, 21, 21)  # number of points for source_distance_shift, focal_length_scaling_factor, and diameter_reduction
    
    grids = [np.linspace(b[0], b[1], n) for b, n in zip(bounds, grid_points)]
    
    # create list of parameter tuples
    param_list = list(itertools.product(*grids))
    
    # use multiprocessing to evaluate compute_mse over the grid with a simple progress monitor
    total_tasks = len(param_list)
    results = []
    with Pool() as p:
        for idx, res in enumerate(p.imap(compute_mse, param_list), start=1):
            results.append(res)
            print(f"Progress: {idx}/{total_tasks} parameter sets evaluated", end="\r")
    print("\nGrid evaluation complete.")

    results = np.array(results)
    # reshape to 3D array matching grid_points
    mse_map = results.reshape(grid_points)

    # print minimal mse and corresponding parameters
    min_index = np.unravel_index(np.argmin(mse_map), mse_map.shape)
    min_mse = mse_map[min_index]
    best_params = (
        grids[0][min_index[0]],
        grids[1][min_index[1]],
        grids[2][min_index[2]]
    )
    print(f'Minimal mse: {min_mse:.6e}')
    print(f'Best parameters: source_distance_shift={best_params[0]:.6f}, '
          f'focal_length_scaling_factor={best_params[1]:.6f}, '
          f'diameter_reduction={best_params[2]:.6f}')


    # save and print summary
    out_path = path + '/mse_map' + str(bounds) + '.npy'
    np.save(out_path, mse_map)
    print(f'Saved mse_map to {out_path} with shape {mse_map.shape}')


    # visualize mse_map as 2D slices at the middle index of each parameter
    fig, axs = plt.subplots(1, 3, figsize=(18, 5))
    slice_indices = [grid_points[0] // 2, grid_points[1] // 2, grid_points[2] // 2]
    slice_configs = [
        (mse_map[slice_indices[0], :, :], grids[1], grids[2], 'focal_length_scaling_factor', 'diameter_reduction', f'source_distance_shift={grids[0][slice_indices[0]]:.3f}'),
        (mse_map[:, slice_indices[1], :], grids[0], grids[2], 'source_distance_shift', 'diameter_reduction', f'focal_length_scaling_factor={grids[1][slice_indices[1]]:.3f}'),
        (mse_map[:, :, slice_indices[2]], grids[0], grids[1], 'source_distance_shift', 'focal_length_scaling_factor', f'diameter_reduction={grids[2][slice_indices[2]]:.3f}')
    ]

    for ax, (data_slice, x_vals, y_vals, xlabel, ylabel, title) in zip(axs, slice_configs):
        im = ax.imshow(data_slice, origin='lower', aspect='auto', extent=(x_vals[0], x_vals[-1], y_vals[0], y_vals[-1]), cmap='viridis')
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        fig.colorbar(im, ax=ax)

    fig.tight_layout()
    fig.savefig(path + '/mse_map_slices.png')
    print(f'Saved mse_map visualization to {path}/mse_map_slices.png')
    plt.show()









