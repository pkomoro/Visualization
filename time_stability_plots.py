import glob
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Make all plot fonts bigger
plt.rcParams.update({
    'font.size': 14,
    'axes.titlesize': 16,
    'axes.labelsize': 14,
    'xtick.labelsize': 12,
    'ytick.labelsize': 12,
    'legend.fontsize': 12,
    'figure.titlesize': 16
})

path = r'D:\OneDrive - Wojskowa Akademia Techniczna\Pomiary\Łącze THz\Moc źródła IMPATT'
scale = 93.45 / 0.115 # set the y-axis scaling factor here
offset = 0.34

csv_files = sorted(glob.glob(os.path.join(path, '*.csv')))
if len(csv_files) < 2:
    raise FileNotFoundError('Expected at least two CSV files in the directory.')

data = []
for csv_file in csv_files[:2]:
    df = pd.read_csv(csv_file, skiprows=14, skipfooter=1, engine='python', header=None, names=['time', 'value'])
    df = df.sort_values('time').reset_index(drop=True)
    df['time'] = df['time'] - df['time'].iloc[0]
    df['value'] = df['value'] * scale + offset  # Apply scaling and offset
    data.append((os.path.basename(csv_file), df))

max_time = min(df['time'].iloc[-1] for _, df in data)

# Define custom labels
custom_labels = {
    os.path.basename(csv_files[0]): 'Source powered off',
    os.path.basename(csv_files[1]): 'Source powered on'
}

time_start = -400

# joined plot with mean and std for each file

# plt.figure(figsize=(10, 6))
# for label, df in data:
#     df_cut = df[df['time'] <= max_time]
#     custom_label = custom_labels.get(label, label)
#     plt.plot(df_cut['time'], df_cut['value'], label=custom_label)
#     # plot mean as horizontal line
#     mean_value = df_cut['value'].mean()
#     std_value = df_cut['value'].std()
#     plt.hlines(mean_value, xmin=time_start, xmax=max_time, colors='C{}'.format(data.index((label, df))%10), linestyles='--')
#     # add text with mean and std near the right side, offset by index

#     x_text = time_start + (max_time - time_start) * 0.01
#     y_text = mean_value - (mean_value - 25) * 0.15
#     plt.text(x_text, y_text, f"mean={mean_value:.2f} mW\nstd={std_value:.2f} mW", fontsize=12,
#              bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))
    
    
# print(f"Mean and standard deviation for each file:")
# for label, df in data:
#     df_cut = df[df['time'] <= max_time]
#     mean_value = df_cut['value'].mean()
#     std_value = df_cut['value'].std()
#     print(f"{label}: mean={mean_value:.2f} mW, std={std_value:.2f} mW")
# plt.xlim(time_start, max_time)
# plt.ylim(-5, 100)
# plt.xlabel('Time [s]')
# plt.ylabel('Power [mW]')
# # plt.title('Time Stability Plot')
# plt.legend()
# plt.grid(True)
# plt.tight_layout()
# # plt.show()
# plt.savefig(os.path.join(path, 'time_stability_plot.jpg'), dpi=300)
# plt.savefig(os.path.join(path, 'time_stability_plot.svg'))

# Create separate plots for each file
for label, df in data:
    df_cut = df[df['time'] <= max_time]
    custom_label = custom_labels.get(label, label)
    plt.figure(figsize=(6, 4))

    plt.plot(df_cut['time'], df_cut['value'], linestyle='-', linewidth=0.1)
    # plot mean as horizontal line and mark 1σ / 3σ deviation bands
    mean_value = df_cut['value'].mean()
    std_value = df_cut['value'].std()
    plt.hlines(mean_value, xmin=time_start, xmax=max_time, colors='darkblue', linestyles='--', linewidth=2.5)
    plt.hlines(mean_value + std_value, xmin=time_start, xmax=max_time, colors='tab:orange', linestyles='-.', linewidth=2.5)
    plt.hlines(mean_value - std_value, xmin=time_start, xmax=max_time, colors='tab:orange', linestyles='-.', linewidth=2.5)
    plt.hlines(mean_value + 3 * std_value, xmin=time_start, xmax=max_time, colors='tab:red', linestyles=':', linewidth=2.5)
    plt.hlines(mean_value - 3 * std_value, xmin=time_start, xmax=max_time, colors='tab:red', linestyles=':', linewidth=2.5)
    
    # add labels for sigma lines
    plt.text(max_time, mean_value, '$\\mu$', va='bottom', ha='right', fontsize=11, color='darkblue')
    plt.text(max_time, mean_value + std_value, '$\\mu + \\sigma$', va='bottom', ha='right', fontsize=11, color='tab:orange')
    plt.text(max_time, mean_value - std_value, '$\\mu - \\sigma$', va='bottom', ha='right', fontsize=11, color='tab:orange')
    plt.text(max_time, mean_value + 3 * std_value, '$\\mu + 3\\sigma$', va='bottom', ha='right', fontsize=11, color='tab:red')
    plt.text(max_time, mean_value - 3 * std_value, '$\\mu - 3\\sigma$', va='bottom', ha='right', fontsize=11, color='tab:red')

    # add text with mean and std near the left side
    x_text = time_start + 60
    y_text = mean_value + 1.38
    plt.text(x_text, y_text, f"$\\mu$={mean_value:.2f} mW\n$\\sigma$={std_value:.2f} mW", fontsize=11,
             bbox=dict(facecolor='white', alpha=0.7, edgecolor='none'))

    print(f"{label}: mean={mean_value:.2f} mW, std={std_value:.2f} mW")
    plt.xlim(time_start, max_time)
    plt.ylim(mean_value - 1.8, mean_value + 1.8)
    plt.xlabel('Time [s]')
    plt.ylabel('Power [mW]')
    plt.title(custom_label)
    plt.grid(True)
    plt.tight_layout()
    outname = os.path.join(path, f"time_stability_{os.path.splitext(label)[0]}.jpg")
    plt.savefig(outname, dpi=300)
    plt.savefig(outname.replace('.jpg', '.svg'))
    plt.close()

    # Prepare Allan deviation
    try:
        # resample to uniform spacing by linear interpolation on median sampling interval
        time = df_cut['time'].values
        vals = df_cut['value'].values
        if len(time) < 3:
            print(f"{label}: not enough points for Allan deviation")
        dt = pd.Series(time).diff().median()
        print(f"{label}: median sampling interval dt={dt:.6f} s")
        if dt <= 0:
            dt = (time[-1] - time[0]) / (len(time) - 1)
        t_uniform = np.arange(time[0], time[-1], dt)
        vals_interp = np.interp(t_uniform, time, vals)

        def allan_dev(x, dt):
            # compute Allan deviation for a range of cluster sizes
            N = len(x)
            max_m = int(N/2)
            ms = np.unique(np.logspace(0, np.log10(max_m), num=50).astype(int))
            taus = ms * dt
            adev = []
            for m in ms:
                if m < 1:
                    continue
                # compute non-overlapping segment averages
                K = N // m
                if K < 2:
                    continue
                y = x[:K*m].reshape(K, m).mean(axis=1)
                diff = np.diff(y)
                var = 0.5 * np.mean(diff**2)
                adev.append(np.sqrt(var))
            return np.array(taus[:len(adev)]), np.array(adev)

        taus, adev = allan_dev(vals_interp, dt)
        if len(taus) > 0:
            plt.figure(figsize=(6, 4))
            plt.loglog(taus, adev, marker='o', linestyle='', label='data')

            # white noise reference line ~ tau^(-0.5)
            tau_ref = np.array([taus[0], taus[-1]])
            ref = adev[0] * (tau_ref / taus[0])**-0.5
            plt.loglog(tau_ref, ref, linestyle='--', color='orange', label='white noise ~$\\tau^{-0.5}$')
            plt.legend()

            plt.xlabel('τ [s]')
            plt.ylabel(r'$\sigma_y(\tau)$ [mW]')
            plt.ylim(1e-3, 1e0)
            plt.title(f"Allan deviation - {custom_label}")
            plt.grid(True, which='both')
            out_allan = os.path.join(path, f"allan_{os.path.splitext(label)[0]}.jpg")
            plt.tight_layout()
            plt.savefig(out_allan, dpi=300)
            plt.savefig(out_allan.replace('.jpg', '.svg'))
            plt.close()
    except Exception as e:
        print(f"Failed to compute Allan deviation for {label}: {e}")



