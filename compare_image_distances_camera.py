import numpy as np
from matplotlib import pyplot as plt
from pathlib import Path
from scipy.optimize import curve_fit

from methods import GaussianBeam, Lens


def thin_lens_equation(u, f):
    return 1 / (1 / f - 1 / u)


def gaussian_lens_equation(s, f, w0, l):
    return 1 / (1 / f + 1 / (s + (np.pi * w0**2 / l)**2 / (s + f)))


def Kirchhoff_integral(r, theta, z, zs, f, ws, l, a):
    k = 2 * np.pi / l
    ksi0 = 2 * (0 - zs) / k / ws**2
    kappa0 = np.sqrt(2) / ws / np.sqrt(1 + ksi0**2)
    sigma0squared = 1 + 1j * ksi0

    R = np.linspace(0, a, 100)
    Theta = np.linspace(0, 2 * np.pi, 100)
    r0, theta0 = np.meshgrid(R, Theta)

    integrand = kappa0 / np.sqrt(np.pi) * np.exp(
        1j * k * zs
        - 1 / 2 * kappa0**2 * sigma0squared * r0**2
        + 1j * np.atan(ksi0)
        + 1j * k * r0**2 / 2 / f
        + 1j * k * r * r0 * np.cos(theta - theta0) / z
        - 1j * k * r0**2 / 2 / z
    ) * r0

    inner_integral = np.trapezoid(integrand, R, axis=1)
    final_result = np.trapezoid(inner_integral, Theta)

    U = 1j / l / z * np.exp(-1j * k * z - 1j * k * r**2 / 2 / z) * final_result
    return U


def gaussian_2d(coordinates, amplitude, x0, y0, sigma_x, sigma_y, offset):
    x, y = coordinates
    exponent = -(((x - x0) ** 2) / (2 * sigma_x ** 2) + ((y - y0) ** 2) / (2 * sigma_y ** 2))
    return amplitude * np.exp(exponent)


if __name__ == "__main__":
    # Basic parameters (kept consistent with original script)
    wavelength = 3.21  # mm
    source_waist_x = 5.1  # mm
    source_waist_y = 6.1  # mm
    optics_diameter = 187  # mm
    lens_thickness = 2  # mm

    # Focal length to analyze (matching CSV name f118mm...)
    focal_length = 118

    # small adjustments used in original script

    common_shift = 0
    source_distance_shift_x = -7.5 + common_shift
    source_distance_shift_y = -23.5 + common_shift
    focal_length_scaling_factor = 1.1
    source_waist_scaling_factor = 1
    diameter_reduction = 0.9

   
    total_distance_map = {118: 320, 158: 480, 180: 570}
    total_distance = total_distance_map.get(focal_length, 570)

    optics_diameter_adjusted = optics_diameter * diameter_reduction
    focal_length_adjusted = focal_length * focal_length_scaling_factor
    source_waist_x_adjusted = source_waist_x * source_waist_scaling_factor
    source_waist_y_adjusted = source_waist_y * source_waist_scaling_factor

    # Path to the CSV file (change if needed)
    csv_path = Path("C:/Users/komor/OneDrive - Wojskowa Akademia Techniczna/Pomiary/Łącze THz/Ogniska soczewek - kamera/"+f"f{focal_length}mm_experimental_data.csv")

    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    data = np.genfromtxt(csv_path, delimiter=",", skip_header=1)
    if data.ndim == 1:
        data = data.reshape(1, -1)

    object_positions_x = data[:, 0] - source_distance_shift_x
    object_positions_y = data[:, 0] - source_distance_shift_y
    image_position_fit = data[:, 1]
    image_position_min_radius = data[:, 2]
    image_position_max_intensity = data[:, 3]
    image_positions_gauss2dx = data[:, 4]
    image_positions_gauss2dy = data[:, 5]
    waist_geo = data[:, 6]
    waist_gauss2dx = data[:, 7]
    waist_gauss2dy = data[:, 8]

    # Theoretical calculations (copied from original script)
    object_positions_range = np.linspace(np.min([object_positions_x, object_positions_y]), np.max([object_positions_x, object_positions_y]), 100)

    beam1x = GaussianBeam(wavelength, source_waist_x_adjusted, 0)
    beam1y = GaussianBeam(wavelength, source_waist_y_adjusted, 0)
    lens1 = Lens(focal_length_adjusted, optics_diameter_adjusted, object_positions_range)
    beam2x = lens1.transform(beam1x)
    beam2y = lens1.transform(beam1y)

    thin_lens_waist_x = source_waist_x_adjusted * thin_lens_equation(object_positions_range, focal_length_adjusted) / object_positions_range
    thin_lens_waist_y = source_waist_y_adjusted * thin_lens_equation(object_positions_range, focal_length_adjusted) / object_positions_range

    # Kirchhoff integral evaluation
    z_values = np.linspace(1 * focal_length_adjusted, 4 * focal_length_adjusted, 200)
    r_values = np.linspace(0, 24, 100)
    Kirchhoff_waist_x = []
    Kirchhoff_waist_y = []

    for idx, dis in enumerate(range(len(object_positions_x))):
        end_char = '\n' if idx == len(object_positions_x) - 1 else '\r'
        print(f'Kirchhoff progress: {idx+1}/{len(object_positions_x)} -- object_pos = {object_positions_x[dis]:.3f} mm', end=end_char, flush=True)

        U_values = np.array([Kirchhoff_integral(0, 0, z, -object_positions_x[dis], focal_length_adjusted, source_waist_x_adjusted, wavelength, optics_diameter_adjusted / 2) for z in z_values])
        intensity = np.abs(U_values) ** 2
        max_value = np.max(intensity)
        max_index = np.argmax(intensity)
        max_z = z_values[max_index]

        U_values = np.array([Kirchhoff_integral(r, 0, max_z, -object_positions_x[dis], focal_length_adjusted, source_waist_x_adjusted, wavelength, optics_diameter_adjusted / 2) for r in r_values])
        intensity = np.abs(U_values) ** 2

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

        U_values = np.array([Kirchhoff_integral(0, 0, z, -object_positions_y[dis], focal_length_adjusted, source_waist_y_adjusted, wavelength, optics_diameter_adjusted / 2) for z in z_values])
        intensity = np.abs(U_values) ** 2
        max_value = np.max(intensity)
        max_index = np.argmax(intensity)
        max_z = z_values[max_index]

        U_values = np.array([Kirchhoff_integral(r, 0, max_z, -object_positions_y[dis], focal_length_adjusted, source_waist_y_adjusted, wavelength, optics_diameter_adjusted / 2) for r in r_values])
        intensity = np.abs(U_values) ** 2

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

    # Plotting comparisons
    plt.close()
    plt.figure()
    plt.plot(object_positions_x, waist_gauss2dx, 's-', label='Measured beam waist (2D Gaussian fit X)', markersize=8)
    plt.plot(object_positions_y, waist_gauss2dy, '^-', label='Measured beam waist (2D Gaussian fit Y)', markersize=8)
    plt.plot(object_positions_x, Kirchhoff_waist_x, 'b--', label='Kirchhoff integral - x axis')
    plt.plot(object_positions_y, Kirchhoff_waist_y, 'm--', label='Kirchhoff integral - y axis')
    # plt.plot(object_positions_range, beam2x.waist, 'b:', label='Theoretical (Gaussian Beam X)')
    # plt.plot(object_positions_range, beam2y.waist, 'm:', label='Theoretical (Gaussian Beam Y)')
    plt.xlabel('Object Distance (mm)')
    plt.ylabel('Beam Waist (mm)')
    plt.ylim(3, 16)
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
    out_stem = csv_path.parent / ('f' + str(focal_length) + 'mm')
    output_path_waist = out_stem.parent / f"{out_stem.name}_beam_waist_comparison.jpg"
    print(f"Saving beam waist comparison plot to: {output_path_waist}")
    
    plt.savefig(output_path_waist, dpi=1000, bbox_inches='tight')
    plt.close()

    # Image position comparison
    plt.figure(figsize=(10, 6))
    plt.plot(object_positions_x, image_positions_gauss2dx, 's-', label='Experimental (2D Gaussian fit X)', linewidth=2, markersize=8)
    plt.plot(object_positions_y, image_positions_gauss2dy, '^-', label='Experimental (2D Gaussian fit Y)', linewidth=2, markersize=8)

    # object_distances = np.linspace(np.min([object_positions_x, object_positions_y]), np.max([object_positions_x, object_positions_y]), 40)
    # theoretical_image_positions_gaussian = gaussian_lens_equation(-object_distances, focal_length_adjusted, source_waist_x_adjusted, wavelength)

    # z_max_values = []
    # z_values = np.linspace(focal_length + 10, 600.0, 200)
    # for zs in object_distances:
    #     U_values = np.array([Kirchhoff_integral(0, 0, z, -zs, focal_length_adjusted, source_waist_x_adjusted, wavelength, optics_diameter_adjusted / 2) for z in z_values])
    #     intensity = np.abs(U_values) ** 2
    #     max_index = np.argmax(intensity)
    #     z_max_values.append(z_values[max_index])
    #     processed = len(z_max_values)
    #     total = len(object_distances)
    #     print(f"\rKirchhoff integral progress: {processed}/{total} object distances", end="", flush=True)
    #     if processed == total:
    #         print()
    # plt.plot(object_distances, z_max_values, 'b--', label='Kirchhoff integral - x axis', linewidth=2)

    # z_max_values = []
    # for zs in object_distances:
    #     U_values = np.array([Kirchhoff_integral(0, 0, z, -zs, focal_length_adjusted, source_waist_y_adjusted, wavelength, optics_diameter_adjusted / 2) for z in z_values])
    #     intensity = np.abs(U_values) ** 2
    #     max_index = np.argmax(intensity)
    #     z_max_values.append(z_values[max_index])
    #     processed = len(z_max_values)
    #     total = len(object_distances)
    #     print(f"\rKirchhoff integral progress: {processed}/{total} object distances", end="", flush=True)
    #     if processed == total:
    #         print()
    # plt.plot(object_distances, z_max_values, 'm--', label='Kirchhoff integral - y axis', linewidth=2)


    plt.plot(object_positions_range, beam2x.waist_position - object_positions_range, 'b:', label='Theoretical (Gaussian Beam X)', linewidth=2)
    plt.plot(object_positions_range, beam2y.waist_position - object_positions_range, 'm:', label='Theoretical (Gaussian Beam Y)', linewidth=2)

    plt.xlabel('Object Distance (mm)')
    plt.ylabel('Image Distance (mm)')
    plt.title('Object Positions: Experimental vs Theoretical (from CSV)')
    plt.axvline(2 * focal_length_adjusted, color='gray', linestyle='--', linewidth=1)
    plt.axhline(2 * focal_length_adjusted, color='gray', linestyle='--', linewidth=1)
    ylim = plt.Axes.get_ylim(plt.gca())
    xlim = plt.Axes.get_xlim(plt.gca())
    plt.text(2 * focal_length_adjusted, ylim[0], ' 2f', color='gray', ha='left', va='bottom')
    plt.text(xlim[0], 2 * focal_length_adjusted, ' 2f', color='gray', ha='left', va='bottom')
    plt.legend()
    plt.grid(True, alpha=0.3)
    output_path_positions = out_stem.parent / f"{out_stem.name}_object_positions_comparison.jpg"
    print(f"Saving object positions comparison plot to: {output_path_positions}")
    plt.savefig(output_path_positions, dpi=1000, bbox_inches='tight')
    plt.close()
