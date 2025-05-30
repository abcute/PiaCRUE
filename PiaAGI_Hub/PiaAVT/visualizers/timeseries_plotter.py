# PiaAGI_Hub/PiaAVT/visualizers/timeseries_plotter.py
"""
Provides functionality for plotting time-series data using Matplotlib.

This module defines the `TimeseriesPlotter` class, which is responsible for
generating 2D line plots from time-series data. The data is expected to be
a list of (datetime, value) tuples. The plotter allows for customization
of titles, labels, line styles, and markers. It can display plots directly
or save them to image files.

This module is typically used in conjunction with an analyzer (like BasicAnalyzer)
that extracts the time-series data from logs, but it can also plot any
appropriately formatted time-series data.
"""
from typing import List, Tuple, Any, Optional
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Note: The comment below was in the original file.
# Assuming LogEntry and BasicAnalyzer might be used for data preparation,
# but this module focuses on plotting given time-series data.

class TimeseriesPlotter:
    """
    Generates 2D line plots for time-series data using Matplotlib.

    This class takes time-series data, typically extracted by an analyzer,
    and produces visual plots. It handles common plotting tasks like setting
    titles, labels, formatting date axes, and saving plots to files.
    """

    def __init__(self):
        """
        Initializes the TimeseriesPlotter.
        Currently, initialization does not require specific parameters, but
        it could be extended in the future to support common styling options or themes.
        """
        # Future: Initialize with common styling options or themes
        pass

    def plot_time_series(self,
                         time_series_data: List[Tuple[datetime, Any]],
                         title: str = "Time Series Plot",
                         x_label: str = "Time",
                         y_label: str = "Value",
                         output_file: Optional[str] = None,
                         show_plot: bool = True,
                         line_style: str = '-',
                         marker: str = 'o') -> None:
        """
        Plots time-series data as a line graph.

        The input `time_series_data` is expected to be a list of tuples, where
        each tuple contains a `datetime` object for the x-axis and a value for the
        y-axis. For best results, y-axis values should be numeric. If non-numeric
        values are provided, a warning is printed, and Matplotlib's behavior will
        determine the outcome (which might be an error or an uninformative plot).

        Args:
            time_series_data (List[Tuple[datetime, Any]]): The data to plot.
                Each tuple should be (timestamp, value).
            title (str): The title of the plot.
            x_label (str): The label for the x-axis.
            y_label (str): The label for the y-axis.
            output_file (Optional[str]): If provided, the plot will be saved to this
                                         file path (e.g., "my_plot.png").
            show_plot (bool): If True (default), `plt.show()` is called to display
                              the plot. Set to False for non-interactive environments
                              or when only saving the file.
            line_style (str): The style of the plot line (e.g., '-', '--', ':').
            marker (str): The marker style for data points (e.g., 'o', '.', ',').
        """
        if not time_series_data:
            print("No data provided to plot.")
            return

        # Separate timestamps and values
        timestamps = [item[0] for item in time_series_data]
        values = [item[1] for item in time_series_data]

        # Check if values are numeric, warn if not (basic check)
        if not all(isinstance(v, (int, float)) for v in values if v is not None):
            print("Warning: Not all Y-axis values are numeric. Plot might be non-sensical or raise errors.")
            # Attempt to convert, replacing non-convertible with None or handling as categorical?
            # For simplicity now, we proceed, matplotlib might handle some cases or error out.

        plt.figure(figsize=(12, 6))
        plt.plot(timestamps, values, linestyle=line_style, marker=marker)

        plt.title(title)
        plt.xlabel(x_label)
        plt.ylabel(y_label)

        # Format the x-axis to handle dates nicely
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
        plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=10)) # Auto-adjust number of ticks
        plt.gcf().autofmt_xdate()  # Auto-rotate date labels

        plt.grid(True)
        plt.tight_layout()

        if output_file:
            try:
                plt.savefig(output_file)
                print(f"Plot saved to {output_file}")
            except Exception as e:
                print(f"Error saving plot to {output_file}: {e}")

        if show_plot:
            plt.show()

        plt.close() # Close the plot figure to free memory, especially if not showing.

# Example Usage (primarily for demonstration or direct script testing)
# This section will typically not be run when PiaAVT is used as a library.
if __name__ == "__main__":
    plotter = TimeseriesPlotter()

    # Sample numeric time-series data
    sample_data_numeric: List[Tuple[datetime, Any]] = [
        (datetime(2024, 1, 15, 10, 0, 0), 10),
        (datetime(2024, 1, 15, 10, 5, 0), 12),
        (datetime(2024, 1, 15, 10, 10, 0), 8),
        (datetime(2024, 1, 15, 10, 15, 0), 15),
        (datetime(2024, 1, 15, 10, 20, 0), 13),
    ]

    print("Plotting sample numeric time series...")
    plotter.plot_time_series(
        sample_data_numeric,
        title="Sample Numeric Data Over Time",
        y_label="Measurement",
        output_file="sample_numeric_timeseries.png",
        show_plot=True # Set to False if running in a non-GUI environment for tests
    )
    print("Numeric plot example done. Check for 'sample_numeric_timeseries.png'")

    # Sample time-series data with potentially non-numeric values (for demonstration of warning)
    # Matplotlib might handle some categorical data on y-axis but it's not ideal for line plots.
    sample_data_mixed: List[Tuple[datetime, Any]] = [
        (datetime(2024, 1, 16, 11, 0, 0), "start"),
        (datetime(2024, 1, 16, 11, 5, 0), "processing"),
        (datetime(2024, 1, 16, 11, 10, 0), "error"),
        (datetime(2024, 1, 16, 11, 15, 0), "processing"),
        (datetime(2024, 1, 16, 11, 20, 0), "end"),
    ]

    # print("\nPlotting sample mixed-type time series (expect warning)...")
    # plotter.plot_time_series(
    #     sample_data_mixed,
    #     title="Sample Mixed Data Over Time (May Not Plot Well)",
    #     y_label="Event Type",
    #     output_file="sample_mixed_timeseries.png",
    #     show_plot=True
    # )
    # print("Mixed plot example done. Check for 'sample_mixed_timeseries.png'")

    # Example with no data
    print("\nPlotting with no data...")
    plotter.plot_time_series([], title="Empty Data Plot")

    # Clean up dummy file
    import os
    if os.path.exists("sample_numeric_timeseries.png"):
        # Keep it for user to see in interactive mode, but could be removed in automated tests
        # os.remove("sample_numeric_timeseries.png")
        pass
    # if os.path.exists("sample_mixed_timeseries.png"):
        # os.remove("sample_mixed_timeseries.png")
        # pass
