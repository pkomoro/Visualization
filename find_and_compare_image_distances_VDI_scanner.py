import pandas as pd
import numpy as np
import os
import re
import matplotlib.pyplot as plt

from methods import GaussianBeam, Lens, GaussianDistribution , airy_diameter


# Example usage
if __name__ == "__main__":

    # Source parameters
    wavelength = 3.21  # wavelength in mm
    source_waist = 7.04 # mm for WR10 small cone
    optics_diameter = 187  # diameter of the lenses in mm
    P0 = 93.45  # mW, source power


    # Small cone detector parameters
    detector_aperture = 12  # diameter of the detector in mm
    detector_acceptance_angle = 13.20  # acceptance angle of the detector in degrees (half-angle 1/e2)
    # 8.32 is the fit to emmision cone, 13.20 is the fit to the measured acceptance under plane wave illumination
    detname = "smallCone"

    # Make sure to adjust the path according to your file location
    # Get all files from the specified directory
    path = r'C:\Users\komor\OneDrive - Wojskowa Akademia Techniczna\Pomiary\Łącze THz\Ogniska soczewek - PM4'
    
    plotting = False  # Set to True to enable per-file plotting, False to disable

    focal_length = 118  # mm, adjust based on your lens

    basic_lens_distance = 210  # mm, z axis position of the lens when d=0 (object at the lens)

    lens_thickness = -15  # mm, thickness of the lens

    relative_point_source_position = 0  # mm, point source position relative to horn antenna
    relative_point_source_position2 = 0  # mm, point source position relative to horn antenna

    total_distance_map = {
        118: 330,
        158: 480,
        180: 570
    }
    total_distance = total_distance_map.get(focal_length, 870) - relative_point_source_position  # default to 870 mm if focal length not found

    # List all .txt files from path starting with "f" followed by the focal length and ending with .txt
    txt_files = [f for f in os.listdir(path) if f.startswith('f'+ str(focal_length)) and f.endswith('.txt')]
    print(txt_files)

    d_values = []
    max_args = []
    max_args_fit = []
    max_values = []
    max_values_fit = []

    # Process each txt file
    for txt_file in txt_files:
        file_path = os.path.join(path, txt_file)

        # Read numeric data with comma as decimal point and tab separator
        data = pd.read_csv(file_path, sep='\t', decimal=',', header=None)

        # Extract the two last columns (columns 2 and 3, 0-indexed)
        col3 = data.iloc[:, 2]
        col4 = data.iloc[:, 3]

        if col4.empty:
            continue

        # Find argument in col3 where col4 reaches its maximum
        max_idx = col4.idxmax()
        arg_at_max = col3.iloc[max_idx]

        max_values.append(col4.iloc[max_idx])

        # Fit a line to the data
        coefficients = np.polyfit(col3, col4, 11)
        fit_line = np.poly1d(coefficients)
        fitted_values= fit_line(col3)
        max_values_fit.append(np.max(fitted_values))

        # Extract the number after 'd' from the filename
        base_name = os.path.splitext(txt_file)[0]
        d_match = re.search(r'd(\d+)', base_name)
        if d_match:
            d_value = int(d_match.group(1)) - basic_lens_distance - relative_point_source_position  # Adjust d value based on the basic lens distance
            d_values.append(d_value)
            max_args.append(arg_at_max)
            max_args_fit.append(col3.iloc[np.argmax(fitted_values)])
            print(f'{txt_file}: d={d_value}, arg_at_max={arg_at_max}')
        else:
            print(f'Warning: no "d<number>" found in {txt_file}')

        if plotting:
            # Plot the last columns (y) as a function of the 3rd column (x)
            plt.figure()
            plt.plot(col3, col4, label='Data')
            plt.plot(col3, fitted_values, linestyle='--', label='Fitted Curve')
            plt.legend()
            plt.xlabel('Distance [mm]')
            plt.ylabel('Power [mW]')
            plt.title(f'Data from {txt_file}')
            plt.grid(True)

            # Export image with original filename (replace .txt with .jpg)
            output_filename = txt_file.replace('.txt', '.jpg')
            output_path = os.path.join(path, output_filename)
            plt.savefig(output_path, dpi=500, bbox_inches='tight')
            plt.close()

            print(f'Saved plot for {txt_file}')


    # Simulate focusing efficiency

    object_positions = np.linspace(np.min(d_values), np.max(d_values), 100)  # Object positions

    beam1 = GaussianBeam(wavelength, source_waist, 0)

    lens1 = Lens(focal_length, optics_diameter, object_positions)
    lens_power_efficiency = beam1.power_through_aperture(optics_diameter / 2, object_positions) # Overlap of the lens aperture with the source beam

    beam2 = lens1.transform(beam1)

    # # Plot beam2 radius as a function of z
    # z_range = np.linspace(0, 600, 100)
    # beam_radii = [beam2.radius(z + object_positions) for z in z_range] 
    # plt.figure()
    # plt.plot(z_range, beam_radii)
    # plt.xlabel('z [mm]')
    # plt.ylabel('Beam radius [mm]')
    # plt.title('Beam Radius vs Position')
    # plt.grid(True)
    # plt.show()
    # plt.close()
   

    
    image_positions = beam2.waist_position - object_positions

    print(f'Image positions: {image_positions}')

    detector_overlap = []
    detector_overlap = beam2.power_through_aperture(detector_aperture / 2, beam2.waist_position) # Overlap of the detector aperture with the focused beam
    

    detector_angular_acceptance = []
    detector_acceptance = GaussianDistribution(0, detector_acceptance_angle / 2)  # Detector acceptance in degrees (1/e2 to std dev conversion)

    for angle in beam2.divergence():
        angle_deg = np.degrees(angle)  # Convert divergence angle to degrees
        print(f'Beam divergence angle: {angle_deg:.2f} degrees')
        beam_shape = GaussianDistribution(0, angle_deg / 2)  # Beam divergence in degrees (1/e2 to std dev conversion)
        detector_angular_acceptance.append(detector_acceptance.overlap_with_gaussian(beam_shape))  # Overlap of the detector acceptance with the convergence cone      

    # for angle in beam2.divergence():
    #     angle_deg = np.degrees(angle)  # Convert divergence angle to degrees
    #     print(f'Beam divergence angle: {angle_deg:.2f} degrees')
    #     # detector_angular_acceptance.append(detector_acceptance.overlap_with_gaussian(GaussianDistribution(0, angle / 2)))  # Overlap of the detector acceptance with the convergence cone
    #     if angle_deg <= detector_acceptance_angle:
    #         detector_angular_acceptance.append(1)  # Full acceptance
    #     else:
    #         detector_angular_acceptance.append((detector_acceptance_angle / angle_deg)**2)  # Partial acceptance
        

    

    print(detector_angular_acceptance)

    total_efficiency = [x * y * z for x, y, z in zip(detector_angular_acceptance, detector_overlap, lens_power_efficiency)]  # Total efficiency as a product of the three factors

    def thin_lens_equation(u, f):
        return 1 / (1 / f - 1 / u)
    
    image_positions_thin_lens = thin_lens_equation(object_positions, focal_length)

    gaussian_correction_weight = 0.7  # Weight for averaging the two models

    if d_values:
        # Sort by d values for a clean plot
        sorted_indices = np.argsort(d_values)
        d_sorted = np.array(d_values)[sorted_indices]
        image_positions_sorted = total_distance - lens_thickness - d_sorted + np.array(max_args)[sorted_indices]
        image_positions_fit_sorted = total_distance - lens_thickness - d_sorted + np.array(max_args_fit)[sorted_indices]

        plt.figure()
        plt.plot(d_sorted, image_positions_sorted, marker='o', linestyle='', label='Actual Maximum')
        plt.plot(d_sorted, image_positions_fit_sorted, marker='s', linestyle='', label='Fitted Maximum')
        plt.plot(object_positions, image_positions, linestyle='--', label='Simulated Image Positions (gaussian beam model)')
        plt.plot(object_positions, image_positions_thin_lens, linestyle='-.', label='Simulated Image Positions (thin lens model)')
        plt.plot(object_positions, (1 - gaussian_correction_weight) * image_positions_thin_lens + gaussian_correction_weight * image_positions, linestyle=':', label='Average Image Positions')
        plt.ylim(focal_length , 5 * focal_length)
        plt.xlabel('Object position [mm]')
        plt.ylabel('Image position [mm]')
        plt.title('Image vs Object Position for Focal Length ' + str(focal_length) + 'mm')
        plt.grid(True)
        plt.legend()
        

        # Also plot max power values on a secondary (right) y-axis
        max_values_sorted = np.array(max_values)[sorted_indices]
        max_values_fit_sorted = np.array(max_values_fit)[sorted_indices]
        ax_left = plt.gca()
        ax_right = ax_left.twinx()
        ax_right.plot(d_sorted, 20 * max_values_sorted / P0, marker='^', color='C2', linestyle='', label='Max Power')
        ax_right.plot(d_sorted, 20 * max_values_fit_sorted / P0, marker='v', color='C2', linestyle='', label='Fitted Max Power')
        ax_right.plot(object_positions + relative_point_source_position2, total_efficiency, color='C3', linestyle='--', label='Simulated Efficiency')
        ax_right.plot(object_positions + relative_point_source_position2, detector_angular_acceptance, color='C4', linestyle='--', label='Detector Angular Acceptance')
        ax_right.plot(object_positions + relative_point_source_position2, detector_overlap, color='C5', linestyle='--', label='Detector Overlap')
        ax_right.plot(object_positions + relative_point_source_position2, lens_power_efficiency, color='C6', linestyle='--', label='Lens Power Efficiency')
        ax_right.set_ylabel('Detection efficiency', color='C2')
        ax_right.tick_params(axis='y', labelcolor='C2')
        ax_right.set_ylim(0, 1)  # Set y-axis limit for power
        
        # draw dashed lines at 2*focal_length on both axes
        ax_left.axvline(2 * focal_length, color='gray', linestyle='--', linewidth=1)
        ax_left.axhline(2 * focal_length, color='gray', linestyle='--', linewidth=1)
        # label the 2f lines on the bottom and left axes
        xlim = ax_left.get_xlim()
        ylim = ax_left.get_ylim()
        ax_left.text(2 * focal_length, ylim[0], ' 2f', color='gray', ha='left', va='bottom')
        ax_left.text(xlim[0], 2 * focal_length, ' 2f', color='gray', ha='left', va='bottom')

        
        # combine legends
        lines_left, labels_left = ax_left.get_legend_handles_labels()
        lines_right, labels_right = ax_right.get_legend_handles_labels()
        ax_left.legend(lines_left + lines_right, labels_left + labels_right, loc='center left', bbox_to_anchor=(0, -0.4))

        
        

        summary_path = os.path.join(path, 'f' + str(focal_length) + 'mm_max_arg_vs_d.jpg')
        plt.savefig(summary_path, dpi=500, bbox_inches='tight')
        plt.close()
        print(f'Saved summary plot to {summary_path}')
    else:
        print('No d values found; summary plot not created.')
        

        



    