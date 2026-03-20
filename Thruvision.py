import os
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

path = r'C:\Users\komor\OneDrive - Wojskowa Akademia Techniczna\Projekty\Realizowane\FENG - PAPS\Thruvision - testy\Testy_soczewek\images_20251210\30-1400 temp 200'

png_files = []
for file in os.listdir(path):
    if file.lower().endswith('.png'):
        file_path = os.path.join(path, file)
        image = Image.open(file_path)
        png_files.append(image)

print(f"Loaded {len(png_files)} PNG files")

freqs = np.linspace(30, 1400, len(png_files))  # frequencies for plotting

left_brightness = []
right_brightness = []

for image in png_files:
    img_array = np.array(image)
    height, width = img_array.shape[:2]
    mid = width // 2
    
    left_half = img_array[:, :mid]
    right_half = img_array[:, mid:]
    
    left_avg = np.mean(left_half)
    right_avg = np.mean(right_half)
    
    left_brightness.append(left_avg)
    right_brightness.append(right_avg)

ratio = np.array(left_brightness) / np.array(right_brightness)

plt.figure(figsize=(10, 6))
plt.plot(freqs, ratio, '-')
plt.yscale('log')
plt.xlabel('Frequency [GHz]')
plt.ylabel('Sensitivity [a.u.]')
plt.title('Relative Sensitivity vs Frequency')
plt.grid(True)
plt.savefig(path + '\\sensitivity_plot.jpg', dpi=500, bbox_inches='tight')

# Filter data for 200-300 GHz range
mask = (freqs >= 200) & (freqs <= 300)
freqs_filtered = freqs[mask]
ratio_filtered = ratio[mask]

plt.figure(figsize=(10, 6))
plt.plot(freqs_filtered, ratio_filtered, '-')
plt.yscale('log')
plt.xlabel('Frequency [GHz]')
plt.ylabel('Sensitivity [a.u.]')
plt.title('Relative Sensitivity vs Frequency (200-300 GHz)')
plt.grid(True)

plt.savefig(path + '\\sensitivity_plot_200-300GHz.jpg', dpi=500, bbox_inches='tight')