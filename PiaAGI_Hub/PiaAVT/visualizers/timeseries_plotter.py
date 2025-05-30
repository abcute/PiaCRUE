# PiaAGI_Hub/PiaAVT/visualizers/timeseries_plotter.py
from typing import List, Tuple, Any, Optional
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Assuming LogEntry and BasicAnalyzer might be used for data preparation,
# but this module focuses on plotting given time-series data.

class TimeseriesPlotter:
    """
    Provides functionalities to plot time-series data.
    """

    def __init__(self):
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
        Plots time-series data.
        Assumes time_series_data is a list of (datetime, value) tuples.
        Values are expected to be numeric for standard plotting.
        If values are not numeric, it will attempt to plot them but may result in errors or non-sensical plots.
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

# Example Usage (can be moved to an example script or notebook later)
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
