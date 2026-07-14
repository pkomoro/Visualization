import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# Configuration
path = 'C:\\Users\\komor\\OneDrive - Wojskowa Akademia Techniczna\\Pomiary\\Łącze THz\\Testy łącza 280 GHz - Cassegrain'  # Set path to txt files
scan_step = 20  # [cm] Horizontal scale
distance = 524 # [m] distance from source to detector

def gaussian(x, amp, mu, sigma, offset):
    """Gaussian function with amplitude offset"""
    
    return offset + amp * np.exp(-((x - mu) ** 2) / (2 * sigma ** 2))

def load_and_plot_data(path, scan_step):
    """Load txt files, plot data, and fit gaussian curve"""
    
    if not os.path.isdir(path):
        print(f"Error: Path '{path}' does not exist")
        return
    
    txt_files = [f for f in os.listdir(path) if f.endswith('.txt')]
    
    if not txt_files:
        print(f"No txt files found in '{path}'")
        return
    
    plt.figure(figsize=(12, 8))
    
    for txt_file in txt_files:
        file_path = os.path.join(path, txt_file)
        print(f"Processing file: {file_path}")
        
        try:
            # Load single column data
            data = np.loadtxt(file_path)
            
            # Create horizontal scale based on scan_step
            x = np.arange(len(data)) * scan_step
            
            # Center plot on maximal value
            x_max = x[np.argmax(data)]
            x_shift = x - x_max
            
            # Short filename without last 4 characters (e.g. remove .txt)
            short_name = txt_file[:-4] if len(txt_file) > 4 else txt_file

            # Plot data centered at the max position
            plt.plot(x_shift, data, 'o', label=short_name, markersize=8, alpha=0.7)
            
            # Fit gaussian curve using centered x values
            try:
                # Initial guess for gaussian parameters
                amp_init = np.max(data) - np.min(data)
                mu_init = 0
                sigma_init = (np.max(x_shift) - np.min(x_shift)) / 4
                offset_init = np.min(data)
                
                popt, _ = curve_fit(gaussian, x_shift, data, 
                                   p0=[amp_init, mu_init, sigma_init, offset_init],
                                   maxfev=5000)
                
                # Plot fitted curve
                x_fit = np.linspace(np.min(x_shift), np.max(x_shift), 300)
                y_fit = gaussian(x_fit, *popt)

                plt.plot(x_fit, y_fit, '--', linewidth=2, 
                    label=f'{short_name} (fit: A={popt[0]:.2f}, μ={popt[1]:.2f}, σ={popt[2]:.2f}, offset={popt[3]:.2f})')

                # Calculate divergence angle from 2*sigma radius and scan distance
                two_sigma = 2 * popt[2]
                divergence_angle = np.degrees(np.arctan2(two_sigma / 100, distance))
                FWHM_angle = divergence_angle / 1.699

                
                plt.text(0.01, 0.95 - 0.05 * txt_files.index(txt_file),
                         rf'{short_name}: $2\sigma={two_sigma:.2f}\ \mathrm{{cm}},\ \theta_{{2\sigma}}={divergence_angle:.2f}^\circ,\ \theta_{{\mathrm{{Full~3dB}}}}={2 * FWHM_angle:.2f}^\circ$',
                         transform=plt.gca().transAxes, fontsize=12)

                print(f"{short_name}: Gaussian fit - Amplitude={popt[0]:.4f}, Mean={popt[1]:.4f}, Sigma={popt[2]:.4f}, Offset={popt[3]:.4f}")
            
            except Exception as e:
                print(f"Warning: Could not fit gaussian to {txt_file}: {e}")
        
        except Exception as e:
            print(f"Error loading {txt_file}: {e}")
    
    plt.xlim(-np.max(np.abs(np.array([np.max(x_shift), np.min(x_shift)]))) - 10, np.max(np.abs(np.array([np.max(x_shift), np.min(x_shift)]))) + 10)
    plt.xlabel(f'Position (step size = {scan_step} cm)')
    plt.ylabel('Signal [mV]')
    plt.title('Linear Scans with Gaussian Fits')
    plt.legend(fontsize=8)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(path, 'linear_scans_with_gaussian_fits.jpg'), dpi=300, bbox_inches='tight')

# Run analysis
if __name__ == '__main__':
    load_and_plot_data(path, scan_step)
