import csv
from itertools import islice
import matplotlib.pyplot as plt
import argparse
import re
import os


pixel_x = None
pixel_y = None

area_size = None
max_plot_points = float("inf")

csv_filename = None


def get_args():
    global pixel_x, pixel_y, area_size, max_plot_points, csv_filename

    parser = argparse.ArgumentParser()
    parser.add_argument("aedat_csv_file", help="CSV with AEDAT data to plot", type=str)

    parser.add_argument("--pixel_x", "-x", help="x coordinate of desired pixel", type=int, required=True)
    parser.add_argument("--pixel_y", "-y", help="y coordinate of desired pixel", type=int, required=True)
    parser.add_argument("--area_size", "-a", help="size of box around pixel to observe", type=int, required=True)
    parser.add_argument("--max_plot_points", "-m", help="max number of points to plot", type=int)

    args = parser.parse_args()
    csv_filename = args.aedat_csv_file

    if not os.path.exists(csv_filename):
        quit(f"the file you have passed, {csv_filename}, does not exist")
    pixel_x = args.pixel_x
    if pixel_x < 0:
        quit("pixel_x coordinate was negative, it should be a positive integer")
    pixel_y = args.pixel_y
    if pixel_y < 0:
        quit("pixel_y coordinate was negative, it should be positive integer")
    area_size = args.area_size
    if area_size < 0:
        quit("area_size was negative, it should be positive integer")   
    if args.max_plot_points is not None and args.max_plot_points > 0:
        max_plot_points = args.max_plot_points
        print(max_plot_points)


if __name__ == "__main__":
    get_args()

    last_pixel_state = None
    redundancies = 0    # TODO: do redundancies for all pixels
    reset_pixel = True

    change_timestamps = []  # The times when the pixel changed state
    time_between = []       # The times between the state changes

    with open(csv_filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')

        for row in islice(csv_reader, 1, None):     # Skip the header
            x_row = int(row[1])
            y_row = int(row[2])

            check_x = abs(x_row - pixel_x)
            check_y = abs(y_row - pixel_y)

            if check_x < area_size and check_y < area_size:
                pixel_state = (row[0] == 'True') or (row[0] == '1')

                if (pixel_state != last_pixel_state):
                    reset_pixel = False
                    last_pixel_state = pixel_state
                    change_timestamps.append(int(row[3]))
                    if len(change_timestamps) > max_plot_points:
                        print(redundancies, "broken")

                        break
                else:
                    redundancies += 1

    print(f"Redundancies: {redundancies}")

    # Normalize timestamps & convert to mS
    change_timestamps = [(x - change_timestamps[0]) / 1000 for x in change_timestamps]

    # Get the time between timestamps
    for i in range(len(change_timestamps) - 1):
        time_between.append(change_timestamps[i + 1] - change_timestamps[i])

    # Add lines to plot
    for stamp in change_timestamps:
        plt.plot([stamp, stamp], [0, 1], 'b')

    plt.ylim(0, 1.2)
    plt.yticks([])
    plt.title('Temporal Resoltion')
    plt.xlabel('Time(mS)')

    hz = re.search("[0-9]{1,} ?[H|h][Z|z]", csv_filename)
    hz = hz.group() if hz else ""

    voltage = re.search('(\d+(?:\.\d+)?) ?v', csv_filename, re.IGNORECASE)
    voltage = voltage.group() + "_" if voltage else ""

    waveform_type = re.search('(burst|sine|square|triangle|noise)', csv_filename, re.IGNORECASE)
    waveform_type = waveform_type.group() + "_" if waveform_type else ""

    # TODO: what if the file is specified as polarized but no angle is given?

    degrees = re.search("[0-9]{1,} ?deg", csv_filename, re.IGNORECASE)
    if degrees:
        degrees = re.search("[0-9]{1,}", degrees.group()).group()
        degrees = "_" + degrees + "DegreesPolarized"
    else:
        degrees = ""

    if hz == "" and degrees == "":
        print("WARNING: Could not infer polarizer angle or frequency from file name")

    plt.savefig(f"{waveform_type}{voltage}{hz}{degrees}_event_density.png")

    if len(time_between) != 0:
        print(f"Average time between: {round(sum(time_between) / len(time_between), 2)}mS")
