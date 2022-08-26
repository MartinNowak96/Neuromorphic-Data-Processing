"""
Spike graphs are a record of the acivity of a single pixel or a group of pixels.
Y Axis: ON events correspond to +1 and OFF events correspond to -1
X Axis: Time

CSV Format: on/off,x,y,timestamp
"""
import csv
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import math
import sys
import argparse
import os
import itertools
import re
from plotting_helper import check_aedat_csv_format
from plotting_helper import FileNameRegex

file_to_plot = ''
time_limit = math.inf
manual_title = None
pixel_x = None
pixel_y = None
area_size = None


def get_args():
    global file_to_plot, pixel_x, pixel_y, area_size, time_limit, manual_title

    parser = argparse.ArgumentParser()
    parser.add_argument("aedat_csv_file", help='CSV containing AEDAT data to be plotted (ON/OFF,x,y,timestamp)', type=str)
    parser.add_argument("--time_limit", "-t", type=float, help="Time limit for the X-axis (seconds)")
    parser.add_argument("--title", type=str, help="Manually set plot title. Title will be auto-generated if not set")

    required_named = parser.add_argument_group("Required named arguments")
    required_named.add_argument("--pixel_x", "-x", help="X coordinate of the pixel to examine", type=int, required=True)
    required_named.add_argument("--pixel_y", "-y", help="Y coordinate of the pixel to examine", type=int, required=True)
    required_named.add_argument("--area_size", "-a", help="Size of area to plot", type=int, required=True)

    args = parser.parse_args()

    file_to_plot = args.aedat_csv_file

    if not os.path.exists(file_to_plot):
        quit(f'File does not exist: {file_to_plot}')
    elif os.path.isdir(file_to_plot):
        quit(f"'{file_to_plot}' is a directory. It should be a csv file")

    if args.time_limit is not None:
        time_limit = args.time_limit

    if args.title is not None:
        manual_title = args.title

    pixel_x = args.pixel_x
    pixel_y = args.pixel_y
    area_size = args.area_size


def get_activity_area(csv_file, pixel_x: int, pixel_y: int, area_size: int, max_points: int = sys.maxsize,
                      time_limit: float = math.inf):
    points = []
    first_timestamp = 0

    with open(csv_file, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')

        header = next(reader, None)  # Grab the header

        # Strip whitespace from header if there is any
        header = [x.strip(' ') for x in header]

        if not check_aedat_csv_format(header, ['On/Off', 'X', 'Y', 'Timestamp']):
            quit(f'File {csv_file} is not of the correct format.\n'
                 'A csv containing X, Y, and Timestamp columns is required.')

        polarity_index = header.index('On/Off')
        x_index = header.index('X')
        y_index = header.index('Y')
        timestamp_index = header.index('Timestamp')

        first_row = next(reader, None)
        first_timestamp = int(first_row[timestamp_index])

        if time_limit != math.inf:
            time_limit = time_limit * 1000000   # Convert to microseconds

        for row in itertools.chain([first_row], reader):
            x_pos = int(row[x_index])
            y_pos = 128 - int(row[y_index])

            timestamp = float(int(row[3]) - first_timestamp)
            if timestamp > time_limit:
                return points

            check_x = abs(x_pos - pixel_x)
            check_y = abs(y_pos - pixel_y)

            # Check if this event is inside the specified area
            if check_x < area_size and check_y < area_size:
                if row[polarity_index] in ['1', 'True']:
                    points.append([1, timestamp])
                else:
                    points.append([-1, timestamp])

                if len(points) == max_points:
                    return points

    return points


def get_activity_global(csv_file, max_points: int = sys.maxsize, time_limit: float = math.inf):
    points = []
    first_timestamp = 0

    with open(csv_file, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        next(reader, None)  # Skip header

        first_row = next(reader, None)
        first_timestamp = int(first_row[3])

        if time_limit != math.inf:
            time_limit = time_limit * 1000000   # Convert to microseconds

        for row in itertools.chain([first_row], reader):
            timestamp = float(int(row[3]) - first_timestamp)
            if timestamp > time_limit:
                return points

            if row[0] in ['1', 'True']:
                points.append([1, timestamp])
            else:
                points.append([-1, timestamp])

            if len(points) == max_points:
                return points

    return points


def auto_generate_title(file_name: str) -> str:
    hz = FileNameRegex.parse_frequency(file_name, " ")
    voltage = FileNameRegex.parse_voltage(file_name, " ")
    waveform_type = FileNameRegex.parse_waveform(file_name, " ")

    if re.search('no ?pol', file_name, re.IGNORECASE):
        title = f"{waveform_type}{voltage}{hz}Unpolarized"
    else:
        degrees = FileNameRegex.parse_degrees(file_name, " Degrees Polarized")
        title = f"{waveform_type}{voltage}{hz}{degrees}"

    return title


if __name__ == '__main__':
    get_args()

    file_path = file_to_plot

    points = get_activity_area(file_path, pixel_x, pixel_y, area_size, time_limit=time_limit)
    #points = get_activity_global(file_to_plot, time_limit=0.01)

    # Add lines to plot
    for point in points:
        timestamp_seconds = point[1] / 1000000  # Convert to seconds
        color = ''
        if point[0] == 1:
            color = 'g'
        else:
            color = 'r'

        # Add to points at the same X value to make vertical lines
        plt.plot([timestamp_seconds, timestamp_seconds], [0, point[0]], color)

    plt.ylim(-1.1, 1.1)

    # Get file name from path and remove extension
    file_name = os.path.basename(file_path)
    file_name = os.path.splitext(file_name)[0]

    if manual_title is None:
        title = auto_generate_title(file_name)
        plt.title(title)
    else:
        plt.title(manual_title)

    plt.xlabel('Time (Seconds)')

    plt.gcf().set_size_inches((25, 5))

    # Get axis
    ax = plt.gca()

    # Set Y-axis tick spacing
    ax.yaxis.set_major_locator(mticker.MultipleLocator(1))

    # Increase X and Y tick size
    ax.tick_params(axis='both', which='major', labelsize=12)

    plt.axhline(0, color='black')

    plt.savefig(os.path.join(f'spike_Plot-{file_name}_X-{pixel_x}_Y-{pixel_y}_Area-{area_size}.png'),
                bbox_inches='tight', pad_inches=0.1)