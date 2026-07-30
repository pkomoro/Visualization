import numpy as np
from matplotlib import pyplot as plt
import pathlib
import re
import pandas as pd
from scipy.optimize import minimize
from multiprocessing import Pool
import itertools
from pathlib import Path

def thin_lens_equation(u, f):
    return 1 / (1 / f - 1 / u)

def gaussian_lens_equation(s, f, w0, l):
    return 1 / (1 / f + 1 / ((np.pi * w0**2 / l)**2 / (f - s) - s))

# Source parameters
wavelength = 3.21  # wavelength in mm
source_waist = 7.04  # mm for WR10 small cone
optics_diameter = 187  # diameter of the lenses in mm
P0 = 93.45  # mW, source power

lens_thickness = 2  # mm, thickness of the lens

# Define objective function to minimize
def compute_mse(params):
    source_distance_shift, focal_length_scaling_factor, source_waist_scaling_factor, diameter_reduction = params
    total_mse = 0.0

    optics_diameter_adjusted = optics_diameter * diameter_reduction
    source_waist_adjusted = source_waist * source_waist_scaling_factor
    
    for focal_length in [118]:  # mm, focal lengths of the lenses used in the experiment
        focal_length_import = focal_length
        basic_lens_distance = 210 - source_distance_shift
        total_distance_map = {
            118: 330,
            158: 480,
            180: 570
        }
        total_distance = total_distance_map.get(focal_length, 570)
        
        focal_length_adjusted = focal_length * focal_length_scaling_factor
        
        path = r'C:\Users\komor\OneDrive - Wojskowa Akademia Techniczna\Pomiary\Łącze THz\Ogniska soczewek - PM4'
        txt_files = [f for f in Path(path).glob("f" + str(focal_length_import) + "*.txt")]
        
        if not txt_files:
            continue
        
        d_values = []
        image_positions = []
        
        for txt_file in txt_files:
            file_path = Path(txt_file)
            
            try:
                # Read numeric data with comma as decimal point and tab separator
                data = pd.read_csv(file_path, sep='\t', decimal=',', header=None)
                
                # Extract columns 2 and 3 (0-indexed)
                col3 = data.iloc[:, 2]
                col4 = data.iloc[:, 3]
                
                if col4.empty:
                    continue
                
                # Find argument in col3 where col4 reaches its maximum
                max_idx = col4.idxmax()
                arg_at_max = col3.iloc[max_idx]
                
                # Fit a line to the data
                coefficients = np.polyfit(col3, col4, 11)
                fit_line = np.poly1d(coefficients)
                fitted_values = fit_line(col3)
                arg_at_max_fit = col3.iloc[np.argmax(fitted_values)]
                
                # Extract the number after 'd' from the filename
                base_name = file_path.stem
                d_match = re.search(r'd(\d+)', base_name)
                if d_match:
                    d_value = int(d_match.group(1)) - basic_lens_distance
                    d_values.append(d_value)
                    image_positions.append(total_distance - lens_thickness - d_value + arg_at_max_fit)
            except Exception as e:
                continue
        
        if len(d_values) == 0:
            continue
        
        # Calculate theoretical image positions using gaussian lens equation
        object_positions = np.array(d_values)
        theoretical_image_positions = gaussian_lens_equation(object_positions, focal_length_adjusted, source_waist_adjusted, wavelength)
        
        image_positions_array = np.array(image_positions)
        
        valid_mask = ~np.isnan(theoretical_image_positions)
        
        if np.sum(valid_mask) > 0:
            mse_image_positions = np.mean((image_positions_array[valid_mask] - theoretical_image_positions[valid_mask])**2 / image_positions_array[valid_mask]**2)
            total_mse += mse_image_positions

    return total_mse


if __name__ == '__main__':

    path = r'C:\Users\komor\OneDrive - Wojskowa Akademia Techniczna\Pomiary\Łącze THz\Ogniska soczewek - PM4'

    bounds = [(0, 10), (0.9, 1), (0.5, 0.7), (1, 1)]  # bounds for source_distance_shift, focal_length_scaling_factor, source_waist_scaling_factor, and diameter_reduction

    # grid resolution for each parameter (can be adjusted)
    grid_points = (21, 41, 21, 1)  # number of points for source_distance_shift, focal_length_scaling_factor, source_waist_scaling_factor, and diameter_reduction

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
    # reshape to 4D array matching grid_points
    mse_map = results.reshape(grid_points)

    # print minimal mse and corresponding parameters
    min_index = np.unravel_index(np.argmin(mse_map), mse_map.shape)
    min_mse = mse_map[min_index]
    best_params = (
        grids[0][min_index[0]],
        grids[1][min_index[1]],
        grids[2][min_index[2]],
        grids[3][min_index[3]]
    )

    print(f'Minimal mse: {min_mse:.6e}')
    print(f'Best parameters: source_distance_shift={best_params[0]:.6f}, '
          f'focal_length_scaling_factor={best_params[1]:.6f}, '
          f'source_waist_scaling_factor={best_params[2]:.6f}, '
          f'diameter_reduction={best_params[3]:.6f}')

    # save and print summary
    out_path = path + '/mse_map' + str(bounds) + '.npy'
    np.save(out_path, mse_map)
    print(f'Saved mse_map to {out_path} with shape {mse_map.shape}')

    # visualize mse_map as 2D slices at the indices of minimal mse for 4D data
    fig, axs = plt.subplots(2, 3, figsize=(18, 10))
    slice_indices = list(min_index)

    slice_configs = [
        (mse_map[:, :, slice_indices[2], slice_indices[3]], grids[1], grids[0], 'focal_length_scaling_factor', 'source_distance_shift', f'source_waist_scaling_factor={grids[2][slice_indices[2]]:.3f}, diameter_reduction={grids[3][slice_indices[3]]:.3f}'),
        (mse_map[:, slice_indices[1], :, slice_indices[3]], grids[2], grids[0], 'source_waist_scaling_factor', 'source_distance_shift', f'focal_length_scaling_factor={grids[1][slice_indices[1]]:.3f}, diameter_reduction={grids[3][slice_indices[3]]:.3f}'),
        (mse_map[:, slice_indices[1], slice_indices[2], :], grids[3], grids[0], 'diameter_reduction', 'source_distance_shift', f'focal_length_scaling_factor={grids[1][slice_indices[1]]:.3f}, source_waist_scaling_factor={grids[2][slice_indices[2]]:.3f}'),
        (mse_map[slice_indices[0], :, :, slice_indices[3]], grids[2], grids[1], 'source_waist_scaling_factor', 'focal_length_scaling_factor', f'source_distance_shift={grids[0][slice_indices[0]]:.3f}, diameter_reduction={grids[3][slice_indices[3]]:.3f}'),
        (mse_map[slice_indices[0], :, slice_indices[2], :], grids[3], grids[1], 'diameter_reduction', 'focal_length_scaling_factor', f'source_distance_shift={grids[0][slice_indices[0]]:.3f}, source_waist_scaling_factor={grids[2][slice_indices[2]]:.3f}'),
        (mse_map[slice_indices[0], slice_indices[1], :, :], grids[3], grids[2], 'diameter_reduction', 'source_waist_scaling_factor', f'source_distance_shift={grids[0][slice_indices[0]]:.3f}, focal_length_scaling_factor={grids[1][slice_indices[1]]:.3f}')
    ]

    for ax, (data_slice, x_vals, y_vals, xlabel, ylabel, title) in zip(axs.flatten(), slice_configs):
        im = ax.imshow(data_slice, origin='lower', aspect='auto', extent=(x_vals[0], x_vals[-1], y_vals[0], y_vals[-1]), cmap='viridis')
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        fig.colorbar(im, ax=ax)

    fig.tight_layout()
    fig.savefig(path + '/mse_map_slices.png')
    print(f'Saved mse_map visualization to {path}/mse_map_slices.png')
    
    # # Plot best fit with actual data
    # source_distance_shift, focal_length_scaling_factor, source_waist_scaling_factor, diameter_reduction = best_params
    # focal_length = 158
    # basic_lens_distance = 210 - source_distance_shift
    # total_distance = 570
    # focal_length_adjusted = focal_length * focal_length_scaling_factor
    # optics_diameter_adjusted = optics_diameter * diameter_reduction
    # source_waist_adjusted = source_waist * source_waist_scaling_factor
    
    # # Load data with best parameters
    # txt_files = [f for f in Path(path).glob(f"f{focal_length}*.txt")]
    # d_values_best = []
    # image_positions_best = []
    
    # for txt_file in txt_files:
    #     try:
    #         data = pd.read_csv(txt_file, sep='\t', decimal=',', header=None)
    #         col3 = data.iloc[:, 2]
    #         col4 = data.iloc[:, 3]
            
    #         if col4.empty:
    #             continue
            
    #         coefficients = np.polyfit(col3, col4, 11)
    #         fit_line = np.poly1d(coefficients)
    #         fitted_values = fit_line(col3)
    #         arg_at_max_fit = col3.iloc[np.argmax(fitted_values)]
            
    #         base_name = Path(txt_file).stem
    #         d_match = re.search(r'd(\d+)', base_name)
    #         if d_match:
    #             d_value = int(d_match.group(1)) - basic_lens_distance
    #             d_values_best.append(d_value)
    #             image_positions_best.append(total_distance - lens_thickness - d_value + arg_at_max_fit)
    #     except:
    #         continue
    
    # if len(d_values_best) > 0:
    #     d_values_best = np.array(d_values_best)
    #     image_positions_best = np.array(image_positions_best)
        
    #     # Calculate theoretical positions
    #     theoretical_positions = gaussian_lens_equation(d_values_best, focal_length_adjusted, source_waist_adjusted, wavelength)
        
    #     # Create best fit plot
    #     fig, ax = plt.subplots(figsize=(10, 6))
        
    #     # Sort by d_values for cleaner plot
    #     sort_idx = np.argsort(d_values_best)
    #     d_sorted = d_values_best[sort_idx]
    #     img_sorted = image_positions_best[sort_idx]
    #     theo_sorted = theoretical_positions[sort_idx]
        
    #     ax.plot(d_sorted, img_sorted, 'o-', label='Measured', markersize=8, linewidth=2)
    #     ax.plot(d_sorted, theo_sorted, 's--', label='Theoretical (Best Fit)', markersize=6, linewidth=2)
        
    #     ax.set_xlabel('Object Distance [mm]', fontsize=12)
    #     ax.set_ylabel('Image Distance [mm]', fontsize=12)
    #     ax.set_title(f'Best Fit: Image Position vs Object Distance (f={focal_length}mm)', fontsize=14)
    #     ax.grid(True, alpha=0.3)
    #     ax.legend(fontsize=11)
        
    #     fig.tight_layout()
    #     best_fit_path = path + '/best_fit_image_positions.png'
    #     fig.savefig(best_fit_path, dpi=300, bbox_inches='tight')
    #     print(f'Saved best fit plot to {best_fit_path}')
    
    # plt.show()