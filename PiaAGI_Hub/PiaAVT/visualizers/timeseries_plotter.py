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
It optionally integrates with 'mplcursors' for interactive data point tooltips
if the library is installed.
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
    If 'mplcursors' library is available, it enhances interactive plots with
    tooltips that show data point values on hover.
    """

    def __init__(self):
        """
        Initializes the TimeseriesPlotter.
        Checks for the availability of the optional 'mplcursors' library.
        Future enhancements could include common styling options or themes.
        """
        self._mplcursors_available = False
        try:
            import mplcursors # Check if mplcursors is installed
            self._mplcursors_available = True
        except ImportError:
            # This print statement is for user feedback if they expect interactive cursors.
            # In a library context, logging or a more configurable warning system might be preferred.
            print("TimeseriesPlotter Info: 'mplcursors' library not found. Interactive tooltips will be disabled. To enable, run: pip install mplcursors")
            # mplcursors is optional, so we pass if not found.
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
        If 'mplcursors' is available and `show_plot` is True, interactive tooltips
        will be added to data points.

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
            print("TimeseriesPlotter: No data provided to plot.")
            return

        timestamps = [item[0] for item in time_series_data]
        values = [item[1] for item in time_series_data]

        # Basic check for numeric Y-values; essential for meaningful line plots.
        if not all(isinstance(v, (int, float)) for v in values if v is not None):
            print("TimeseriesPlotter Warning: Not all Y-axis values are numeric. Plot might be non-sensical or raise errors.")

        # Create figure and axes objects
        fig, ax = plt.subplots(figsize=(12, 6))

        # Plot the data, get the line object for potential use with mplcursors
        line, = ax.plot(timestamps, values, linestyle=line_style, marker=marker)

        ax.set_title(title)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)

        # Format X-axis for date/time display
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=10)) # Auto-adjust number of ticks
        fig.autofmt_xdate()  # Auto-rotate date labels for better readability

        ax.grid(True) # Add a grid for easier reading

        # Enhance with mplcursors if available and plot is being shown
        if self._mplcursors_available and show_plot:
            try:
                # Local import ensures it's only fully processed if available and needed
                import mplcursors

                # Create a cursor object for the plotted line(s).
                # hover=True means tooltips appear on mouse hover.
                cursor = mplcursors.cursor(line, hover=True)

                # Customize the annotation text for the tooltip
                @cursor.connect("add")
                def on_add(sel):
                    # Get the x (timestamp) and y (value) of the selected point
                    point_timestamp = mdates.num2date(sel.target[0])
                    point_value = sel.target[1]

                    # Format the annotation text
                    # Use a more descriptive label if available (e.g., from the line's label)
                    artist_label = sel.artist.get_label()
                    if artist_label and not artist_label.startswith('_'): # Matplotlib internal labels often start with '_'
                        label_prefix = f"{artist_label}\n"
                    else:
                        # Fallback if no good artist label (e.g. use y-axis label or title)
                        label_prefix = f"{y_label if y_label != 'Value' and y_label != 'Time' else title}\n"

                    # Format y-value: use .2f for floats, else direct str conversion
                    value_str = f"{point_value:.2f}" if isinstance(point_value, float) else str(point_value)

                    sel.annotation.set_text(
                        f"{label_prefix}"
                        f"Timestamp: {point_timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}\n" # Milliseconds
                        f"Value: {value_str}"
                    )
                    sel.annotation.get_bbox_patch().set(alpha=0.8) # Make tooltip slightly transparent

                # Ensure the line has a label for mplcursors to use, if a generic one isn't preferred
                if not line.get_label() or line.get_label().startswith('_'):
                     # Use y_label or title as a fallback label for the line itself
                    line.set_label(y_label if y_label != "Value" and y_label != "Time" else title)

            except Exception as e_mpl_cursor: # Catch any error during mplcursors setup
                # Print a message but don't fail the plotting if cursors can't be set up
                print(f"TimeseriesPlotter Info: Could not enable interactive mplcursors. Error: {e_mpl_cursor}")

        # Adjust layout to prevent labels from overlapping
        try:
            fig.tight_layout()
        except Exception as e_layout: # Sometimes tight_layout can fail with certain backends/data
             print(f"TimeseriesPlotter Warning: fig.tight_layout() failed: {e_layout}")


        if output_file:
            try:
                fig.savefig(output_file)
                print(f"TimeseriesPlotter: Plot saved to {output_file}")
            except Exception as e_save:
                print(f"TimeseriesPlotter Error: Error saving plot to {output_file}: {e_save}")

        if show_plot:
            try:
                plt.show() # This will be interactive if mplcursors worked
            except Exception as e_show:
                 print(f"TimeseriesPlotter Error: Error displaying plot with plt.show(): {e_show}. Ensure a GUI backend is available for Matplotlib if not running in a headless environment.")

        plt.close(fig) # Close the figure to free up memory

# Example Usage (primarily for demonstration or direct script testing)
# This section will typically not be run when PiaAVT is used as a library.
if __name__ == "__main__":
    plotter = TimeseriesPlotter()

    # Sample numeric time-series data with floating point values
    sample_data_numeric: List[Tuple[datetime, Any]] = [
        (datetime(2024, 1, 15, 10, 0, 0), 10.0),
        (datetime(2024, 1, 15, 10, 5, 0), 12.5),
        (datetime(2024, 1, 15, 10, 10, 0), 8.2),
        (datetime(2024, 1, 15, 10, 15, 0), 15.7),
        (datetime(2024, 1, 15, 10, 20, 0), 13.3),
    ]

    print("Plotting sample numeric time series (interactive tooltips if mplcursors is installed)...")
    plotter.plot_time_series(
        sample_data_numeric,
        title="Sample Numeric Data Over Time",
        y_label="Measurement Value", # More descriptive y_label
        output_file="sample_numeric_timeseries_interactive.png", # Changed filename
        show_plot=True
    )
    print("Numeric plot example done. Check for 'sample_numeric_timeseries_interactive.png'. If shown, try hovering over points.")

    # Example with no data
    print("\nPlotting with no data...")
    # Changed to show_plot=False as per previous version of this example block for non-interactive part
    plotter.plot_time_series([], title="Empty Data Plot", show_plot=False)

    # Clean up dummy file
    import os
    if os.path.exists("sample_numeric_timeseries_interactive.png"):
        # Keep it for user to see in interactive mode, but could be removed in automated tests
        # os.remove("sample_numeric_timeseries_interactive.png")
        pass
    # The mixed data example was commented out in the provided "existing" file, so kept it that way.
    # if os.path.exists("sample_mixed_timeseries.png"):
        # os.remove("sample_mixed_timeseries.png")
        # pass
```
