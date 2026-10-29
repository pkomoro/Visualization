from pathlib import Path
import re

import matplotlib.pyplot as plt
import pandas as pd

def free_space_loss(distance, reference_power, wavelength, directional_gain_tx, directional_gain_rx):
    """
    Calculate the free-space loss based on the Friis transmission equation.

    Parameters:
    - distance: The distance at which to calculate the received power (in meters).
    - reference_distance: The reference distance at which the reference power is measured (in meters).
    - reference_power: The received power at the reference distance (in watts).
    - wavelength: The wavelength of the signal (in meters).
    - directional_gain_tx: The directional gain of the transmitting antenna (unitless).
    - directional_gain_rx: The directional gain of the receiving antenna (unitless).

    Returns:
    - received_power: The calculated received power at the specified distance (in watts).
    """
    distance = pd.to_numeric(distance)

    # Calculate the free-space path loss factor
    path_loss_factor = (wavelength / (4 * 3.141592653589793 * distance)) ** 2

    # Calculate the received power using the Friis transmission equation
    received_power = reference_power * path_loss_factor * directional_gain_tx * directional_gain_rx

    return received_power


CSV_FILE = Path(
	r"C:\Users\komor\OneDrive - Wojskowa Akademia Techniczna\Pomiary\Łącze THz\Anteny stożkowe\detector_shift.csv"
)


data = pd.read_csv(CSV_FILE, sep=";", decimal=",")

if len(data.columns) < 9:
	raise ValueError(f"Expected 9 columns, found {len(data.columns)}")

for group in range(3):
	absolute_col, relative_col, power_col = data.columns[group * 3 : group * 3 + 3]

	plot_data = data[[relative_col, power_col]].dropna()
	fig, ax = plt.subplots()
	ax.plot(plot_data[relative_col], 100 * plot_data[power_col] / 94, marker="o", linestyle="-")
	ax.set_xlabel(str(relative_col))
	ax.set_ylabel("Relative Power [%]")
	# ax.set_title(f"{power_col} vs {relative_col}")
	ax.grid(True)
	ax.set_ylim(0, 60)
	if group == 2:
		distance = pd.to_numeric(plot_data[relative_col], errors="coerce")
		measured_power = 100 * pd.to_numeric(plot_data[power_col], errors="coerce") / 94
		valid = distance.gt(0) & distance.notna() & measured_power.notna()
		if valid.any():
			distance = distance[valid]
			measured_power = measured_power[valid]
			nearest = distance.idxmin()
			theory_distance = sorted(distance.unique())[20::]
			directional_gain_log = 25  # dBi
			directional_gain = 10 ** (directional_gain_log / 10)  # Convert dBi to linear scale
			initial_power = 100
			wavelength = 3.12  # Assuming a frequency of 96.2 GHz
			theory_power = free_space_loss(theory_distance, initial_power, wavelength, directional_gain, directional_gain)
			
			ax.plot(theory_distance, theory_power, linestyle="--", 
			        label=f"Free-space loss (1/d²) \nwith directional gain \nTx = Rx = {directional_gain_log} dBi", color="orange")
			
			directional_gain_log = 22  # dBi
			directional_gain = 10 ** (directional_gain_log / 10)  # Convert dBi to linear scale
			initial_power = 100
			wavelength = 3.12  # Assuming a frequency of 96.2 GHz
			theory_power = free_space_loss(theory_distance, initial_power, wavelength, directional_gain, directional_gain)
			ax.plot(theory_distance, theory_power, linestyle="--", 
                    label=f"Free-space loss (1/d²) \nwith directional gain \nTx = Rx = {directional_gain_log} dBi", color="red")
			ax.legend()

			aperture = 20  # Aperture size in mm
			far_field = 2 * (aperture) ** 2 / wavelength  # Far-field distance calculation
			
			ax.text(
				0.55,
				0.62,
				"Far field for d = " + f"{aperture} mm:  {far_field:.3g} mm",
				transform=ax.transAxes,
				va="top",
				bbox={"facecolor": "white", "alpha": 0.8, "edgecolor": "grey", "boxstyle": "round"},
			)
			
			aperture = 15  # Aperture size in mm
			far_field = 2 * (aperture) ** 2 / wavelength  # Far-field distance calculation
	
			ax.text(
				0.55,
				0.55,
				"Far field for d = " + f"{aperture} mm:  {far_field:.3g} mm",
				transform=ax.transAxes,
				va="top",
				bbox={"facecolor": "white", "alpha": 0.8, "edgecolor": "grey", "boxstyle": "round"},
			)

			aperture = 10  # Aperture size in mm
			far_field = 2 * (aperture) ** 2 / wavelength  # Far-field distance calculation
			
			ax.text(
				0.55,
				0.48,
				"Far field for d = " + f"{aperture} mm:  {far_field:.2g} mm",
				transform=ax.transAxes,
				va="top",
				bbox={"facecolor": "white", "alpha": 0.8, "edgecolor": "grey", "boxstyle": "round"},
			)

			
	fig.tight_layout()

    

	safe_name = re.sub(r'[<>:"/\\|?*]', "_", str(power_col)).strip(" .")
	fig.savefig(CSV_FILE.parent / f"{group + 1}_{safe_name or 'power'}.jpg", dpi=300)

