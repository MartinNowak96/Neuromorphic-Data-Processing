"""
Fingerprint graphs are a visual display of event counts over time.
Y Axis: event counts in a time window
X Axis: time

CSV Format: on,off,both
"""

import os
import argparse
import matplotlib.ticker as mticker
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
import getPlottingData
from getPlottingData import CsvData
from plotting_helper import FileNameRegex

file_to_plot = ''
x_lim = None
reconstruction_window = 0


def get_args():
    global file_to_plot, x_lim, reconstruction_window

    parser = argparse.ArgumentParser()
    parser.add_argument("aedat_csv_file", help='CSV containing AEDAT data to be plotted', type=str)
    parser.add_argument("reconstruction_window",
                        help="Reconstruction window used to generate file: int or path to config file", type=str)
    parser.add_argument("--plot_xlim", '-x', help='Limit on the X-axis (seconds)', type=float)
    args = parser.parse_args()

    file_to_plot = args.aedat_csv_file

    if not os.path.exists(file_to_plot):
        quit(f'File does not exist: {file_to_plot}')
    elif os.path.isdir(file_to_plot):
        quit(f"'{file_to_plot}' is a directory. It should be a csv file")

    x_lim = args.plot_xlim

    if x_lim is not None and x_lim <= 0:
        quit('The argument --plot_xlim/-x must be greater than 0')

    if args.reconstruction_window.isdigit() and args.reconstruction_window != "0":
        reconstruction_window = int(args.reconstruction_window)

    else:
        if(args.reconstruction_window.lstrip('-').isdigit()):
            quit("The argument reconstruction window must be greater than 0")

        if os.path.exists(args.reconstruction_window) and args.reconstruction_window.endswith(".json"):
            config = getPlottingData.parseConfig(args.reconstruction_window)
            reconstruction_window = config.reconstructionWindow
        else:
            quit(f"The path {args.reconstruction_window} does not point to a json file")


def plot_event_count(event_counts: list, t: list, line_color: str, plot_xlim: float, plot_title: str):
    plt.clf()

    plt.title(plot_title)
    plt.xlabel('Time (seconds)')
    plt.ylabel('Event Count')

    plt.yscale('log', base=10)  # Use a log scale

    ax = plt.gca()  # Get axis
    plt.grid()

    # Ensure that Y-axis ticks are displayed as whole numbers
    ax.yaxis.set_major_formatter(ScalarFormatter())
    ax.yaxis.set_minor_formatter(mticker.NullFormatter())   # Disable minor tick markers

    # Set Y-axis tick spacing
    try:
        count_range = max(event_counts) - min(event_counts)
        major_spacing = round((count_range / 5), -1)
        ax.yaxis.set_major_locator(mticker.MultipleLocator(major_spacing))
        ax.yaxis.set_minor_locator(mticker.MultipleLocator(major_spacing / 2))
        # ax.set_ylim([max(event_counts), min(event_counts)])
    except ValueError:
        print("WARNING: Could not set tick spacing. No events present?")

    # Plot lines with circles on the points
    plt.plot(t, event_counts, '-o', markersize=4, c=line_color)

    if x_lim is not None:
        ax.set_xlim([0, plot_xlim])

    plt.gcf().set_size_inches((20, 5))

    plt.savefig(os.path.join(f'{plot_title.replace(" ", "_")}.png'))


if __name__ == '__main__':
    get_args()

    file_name = os.path.basename(file_to_plot)

    hz = FileNameRegex.parse_frequency(file_name, " ")
    voltage = FileNameRegex.parse_voltage(file_name, " ")
    waveform_type = FileNameRegex.parse_waveform(file_name, " ")
    degrees = FileNameRegex.parse_degrees(file_name, " Degrees Polarized")

    # TODO: what if the file is specified as polarized but no angle is given?

    if hz == "" and degrees == "":
        print("WARNING: Could not infer polarizer angle or frequency from file name")

    max_csv_entries = int((x_lim * 1000000) / reconstruction_window) if x_lim is not None else -1

    plot_data: CsvData = getPlottingData.read_aedat_csv(file_to_plot,
                                                        reconstruction_window,
                                                        max_csv_entries)

    plot_event_count(plot_data.y_off, plot_data.time_windows, 'r', x_lim,
                     f"{waveform_type}{voltage}{hz}{degrees} OFF Events Fingerprint ({reconstruction_window}μs Reconstruction Window)")
    plot_event_count(plot_data.y_on, plot_data.time_windows, 'g', x_lim,
                     f"{waveform_type}{voltage}{hz}{degrees} ON Events Fingerprint ({reconstruction_window}μs Reconstruction Window)")
    plot_event_count(plot_data.y_all, plot_data.time_windows, 'b', x_lim,
                     f"{waveform_type}{voltage}{hz}{degrees} All Events Fingerprint ({reconstruction_window}μs Reconstruction Window)")
