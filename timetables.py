import pandas as pd

import matplotlib.pyplot as plt

def visualize_timetable(data, title="Timetable"):
    """
    Visualize a timetable using a heatmap.

    Parameters:
        data (pd.DataFrame): A pandas DataFrame where rows represent time slots
                             and columns represent days, with values indicating
                             activity or occupancy.
        title (str): Title of the timetable visualization.
    """
    plt.figure(figsize=(10, 6))
    plt.title(title, fontsize=16)
    plt.xlabel("Days", fontsize=12)
    plt.ylabel("Time Slots", fontsize=12)
    plt.xticks(rotation=45)

    # Create a heatmap
    plt.imshow(data, cmap="coolwarm", aspect="auto")
    plt.colorbar(label="Activity/Occupancy")
    plt.xticks(range(len(data.columns)), data.columns)
    plt.yticks(range(len(data.index)), data.index)

    plt.tight_layout()
    plt.show()

# Example usage
if __name__ == "__main__":
    # Example data
    # Load timetable data from an external file
    path = "C:/Users/komor/OneDrive - Wojskowa Akademia Techniczna/Pomiary/Photomixing/"
    datafile = "stability_100GHz"
    timetable_data = pd.read_csv(path+datafile, index_col=0)

    print(timetable_data)

    time_slots = ["8:00-9:00", "9:00-10:00", "10:00-11:00", "11:00-12:00", "12:00-1:00"]
    df = pd.DataFrame(timetable_data, index=time_slots)

    visualize_timetable(df, title="Weekly Timetable")