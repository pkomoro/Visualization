import numpy as np
from matplotlib import pyplot as plt
from methods import GaussianBeam, Lens


def main():
    wavelength = 3.21  # mm
    lens_focal_length = 118  # mm
    lens_position = 2 * lens_focal_length  # mm, choose some lens position along the beam path
    lens_diameter = 187  # mm

    initial_waists = np.linspace(1.0, 10.0, 80)
    transformed_waists = []
    output_positions = []

    for waist in initial_waists:
        beam = GaussianBeam(wavelength, waist, waist_position=0.0)
        lens = Lens(lens_focal_length, lens_diameter, position=lens_position)
        transformed_beam = lens.transform(beam)
        transformed_waists.append(transformed_beam.waist)
        output_positions.append((transformed_beam.waist_position - lens_position) / lens_focal_length)  # relative position after lens

    plt.figure(figsize=(8, 5))
    plt.plot(initial_waists, transformed_waists, '-o', markersize=5)
    plt.plot(initial_waists, initial_waists, 'r--', label='y=x', linewidth=2)
    plt.grid(True, alpha=0.4)
    plt.xlabel('Initial Beam Waist $w_0$ [mm]')
    plt.ylabel('Transformed Beam Waist $w_{0, transformed}$ [mm]')
    plt.title('Beam Waist After Lens as a Function of Initial Waist')
    plt.tight_layout()
    plt.savefig('lens_transformed_waist_vs_initial_waist.jpg', dpi=300)
    plt.close()

    plt.figure(figsize=(8, 5))
    plt.plot(initial_waists, output_positions, '-s', markersize=5)
    plt.grid(True, alpha=0.4)
    plt.xlabel('Initial Beam Waist $w_0$ [mm]')
    plt.ylabel('Transformed Waist Position [s/f]')
    plt.title('Transformed Waist Position After Lens')
    plt.tight_layout()
    plt.savefig('lens_transformed_waist_position_vs_initial_waist.jpg', dpi=300)
    plt.close()

    print('Saved: lens_transformed_waist_vs_initial_waist.jpg')
    print('Saved: lens_transformed_waist_position_vs_initial_waist.jpg')


if __name__ == '__main__':
    main()
