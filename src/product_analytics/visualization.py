"""
Visualization Module - Components for creating standardized analytics visualizations
"""
from typing import Dict, List, Optional, Union, Any, Tuple
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime, timedelta


class Visualization:
    """Base class for all visualizations in the framework"""
    
    def __init__(
        self,
        title: str,
        description: Optional[str] = None,
        width: int = 10,
        height: int = 6,
        theme: str = "default"
    ):
        """
        Initialize a visualization
        
        Args:
            title: Title for the visualization
            description: Description of what the visualization shows
            width: Figure width in inches
            height: Figure height in inches
            theme: Visual theme to apply
        """
        self.title = title
        self.description = description
        self.width = width
        self.height = height
        self.theme = theme
        self._figure = None
        self._axes = None
        
    def apply_theme(self):
        """Apply the selected theme to the visualization"""
        if self.theme == "default":
            sns.set_style("whitegrid")
        elif self.theme == "dark":
            plt.style.use("dark_background")
        elif self.theme == "minimal":
            sns.set_style("ticks")
        else:
            sns.set_style("whitegrid")  # Default fallback
        
    def create_figure(self) -> Tuple[plt.Figure, plt.Axes]:
        """Create a new figure and axes"""
        self._figure, self._axes = plt.subplots(figsize=(self.width, self.height))
        self.apply_theme()
        return self._figure, self._axes
    
    def get_figure(self) -> plt.Figure:
        """Get the current figure or create a new one"""
        if self._figure is None:
            self.create_figure()
        return self._figure
    
    def get_axes(self) -> plt.Axes:
        """Get the current axes or create new ones"""
        if self._axes is None:
            self.create_figure()
        return self._axes
    
    def plot(self, data: pd.DataFrame) -> plt.Figure:
        """Plot the visualization"""
        raise NotImplementedError("Subclasses must implement plot method")
    
    def add_annotations(self):
        """Add title, labels, and other annotations to the plot"""
        ax = self.get_axes()
        ax.set_title(self.title, fontsize=14, pad=20)
        
        if self.description:
            self.get_figure().text(0.5, 0.01, self.description, ha='center', 
                                    fontsize=10, style='italic', alpha=0.7)
        
    def save(self, path: str, dpi: int = 300):
        """Save the visualization to a file"""
        self.get_figure().savefig(path, dpi=dpi, bbox_inches='tight')
        
    def show(self):
        """Display the visualization"""
        plt.tight_layout()
        plt.show()
        
    def close(self):
        """Close the figure to free memory"""
        if self._figure is not None:
            plt.close(self._figure)
            self._figure = None
            self._axes = None


class TimeSeriesPlot(Visualization):
    """Time series visualization for tracking metrics over time"""
    
    def __init__(
        self,
        title: str = "Metric Trend",
        x_label: str = "Date",
        y_label: str = "Value",
        rolling_window: Optional[int] = None,
        show_markers: bool = True,
        **kwargs
    ):
        """
        Initialize a time series plot
        
        Args:
            title: Plot title
            x_label: Label for x-axis
            y_label: Label for y-axis
            rolling_window: Size of rolling window for smoothing
            show_markers: Whether to show markers on the line
            **kwargs: Additional arguments for the base Visualization class
        """
        super().__init__(title, **kwargs)
        self.x_label = x_label
        self.y_label = y_label
        self.rolling_window = rolling_window
        self.show_markers = show_markers
        
    def plot(self, data: pd.DataFrame, x_column: str, y_columns: Union[str, List[str]],
             labels: Optional[List[str]] = None) -> plt.Figure:
        """
        Plot time series data
        
        Args:
            data: DataFrame containing the data
            x_column: Column name for x-axis (typically dates)
            y_columns: Column name(s) for y-axis values
            labels: Optional custom labels for the lines
            
        Returns:
            The matplotlib Figure object
        """
        self.create_figure()
        ax = self.get_axes()
        
        # Handle single y column case
        if isinstance(y_columns, str):
            y_columns = [y_columns]
            
        if labels is None:
            labels = y_columns
            
        # Ensure data is sorted by the x_column
        data = data.sort_values(by=x_column)
        
        for i, y_col in enumerate(y_columns):
            plotted_data = data.copy()
            
            # Apply rolling average if specified
            if self.rolling_window is not None and len(data) > self.rolling_window:
                plotted_data[y_col] = data[y_col].rolling(window=self.rolling_window, 
                                                          center=True).mean()
            
            # Plot the data
            marker = 'o' if self.show_markers else None
            ax.plot(plotted_data[x_column], plotted_data[y_col], 
                   marker=marker, markersize=4, label=labels[i])
        
        # Add labels and legend
        ax.set_xlabel(self.x_label)
        ax.set_ylabel(self.y_label)
        
        if len(y_columns) > 1:
            ax.legend()
            
        # Format x-axis for dates
        if pd.api.types.is_datetime64_any_dtype(data[x_column]):
            plt.gcf().autofmt_xdate()
            
        self.add_annotations()
        return self.get_figure()


class BarChart(Visualization):
    """Bar chart visualization for comparing categorical data"""
    
    def __init__(
        self,
        title: str = "Comparison",
        x_label: str = "Categories",
        y_label: str = "Value",
        orientation: str = "vertical",
        sort_values: bool = False,
        **kwargs
    ):
        """
        Initialize a bar chart
        
        Args:
            title: Chart title
            x_label: Label for x-axis
            y_label: Label for y-axis
            orientation: 'vertical' or 'horizontal' bars
            sort_values: Whether to sort bars by value
            **kwargs: Additional arguments for the base Visualization class
        """
        super().__init__(title, **kwargs)
        self.x_label = x_label
        self.y_label = y_label
        self.orientation = orientation
        self.sort_values = sort_values
        
    def plot(self, data: pd.DataFrame, x_column: str, y_column: str,
             color_column: Optional[str] = None) -> plt.Figure:
        """
        Plot bar chart
        
        Args:
            data: DataFrame containing the data
            x_column: Column name for categories
            y_column: Column name for values
            color_column: Optional column to determine bar colors
            
        Returns:
            The matplotlib Figure object
        """
        self.create_figure()
        ax = self.get_axes()
        
        # Sort data if requested
        if self.sort_values:
            data = data.sort_values(by=y_column)
        
        # Create the plot based on orientation
        if self.orientation == "horizontal":
            if color_column:
                sns.barplot(y=x_column, x=y_column, hue=color_column, data=data, ax=ax)
            else:
                sns.barplot(y=x_column, x=y_column, data=data, ax=ax)
            ax.set_xlabel(self.y_label)
            ax.set_ylabel(self.x_label)
        else:  # vertical
            if color_column:
                sns.barplot(x=x_column, y=y_column, hue=color_column, data=data, ax=ax)
            else:
                sns.barplot(x=x_column, y=y_column, data=data, ax=ax)
            ax.set_xlabel(self.x_label)
            ax.set_ylabel(self.y_label)
            plt.xticks(rotation=45 if len(data) > 5 else 0)
        
        # Add legend if using colors
        if color_column:
            ax.legend(title=color_column)
            
        self.add_annotations()
        return self.get_figure()


class FunnelChart(Visualization):
    """Funnel chart for visualizing conversion steps"""
    
    def __init__(
        self,
        title: str = "Conversion Funnel",
        **kwargs
    ):
        """
        Initialize a funnel chart
        
        Args:
            title: Chart title
            **kwargs: Additional arguments for the base Visualization class
        """
        super().__init__(title, **kwargs)
        
    def plot(self, data: List[Tuple[str, float]], 
             show_percentages: bool = True) -> plt.Figure:
        """
        Plot funnel chart
        
        Args:
            data: List of (step_name, value) tuples
            show_percentages: Whether to show conversion percentages
            
        Returns:
            The matplotlib Figure object
        """
        self.create_figure()
        ax = self.get_axes()
        
        # Extract names and values
        names = [item[0] for item in data]
        values = [item[1] for item in data]
        
        # Reverse the order for bottom-up display
        names.reverse()
        values.reverse()
        
        # Create funnel bars
        bar_heights = 0.8
        colors = plt.cm.Blues(np.linspace(0.2, 0.8, len(data)))
        
        # Calculate conversion rates
        if show_percentages and len(values) > 1:
            conversion_rates = []
            max_value = max(values)
            for i, val in enumerate(values):
                if i == 0:  # First element
                    conv_rate = "100%"
                else:
                    prev_val = values[i-1]
                    rate = (val / prev_val * 100) if prev_val > 0 else 0
                    conv_rate = f"{rate:.1f}%"
                conversion_rates.append(conv_rate)
        
        # Plot the bars
        ax.barh(names, values, height=bar_heights, color=colors)
        
        # Add value labels
        for i, (name, value) in enumerate(zip(names, values)):
            ax.text(value + max(values) * 0.02, i, f"{int(value):,}", 
                    va='center', fontweight='bold')
            
            # Add conversion rate
            if show_percentages and len(values) > 1:
                ax.text(value / 2, i, conversion_rates[i], 
                        va='center', ha='center', color='white', fontweight='bold')
        
        # Remove y-axis line
        ax.spines['left'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        
        ax.set_xlabel("Count")
        self.add_annotations()
        return self.get_figure()


class HeatmapPlot(Visualization):
    """Heatmap visualization for matrix data"""
    
    def __init__(
        self,
        title: str = "Heatmap",
        color_map: str = "YlGnBu",
        show_values: bool = True,
        **kwargs
    ):
        """
        Initialize a heatmap visualization
        
        Args:
            title: Heatmap title
            color_map: Matplotlib colormap name
            show_values: Whether to show values in cells
            **kwargs: Additional arguments for the base Visualization class
        """
        super().__init__(title, **kwargs)
        self.color_map = color_map
        self.show_values = show_values
        
    def plot(self, data: pd.DataFrame, 
             vmin: Optional[float] = None, 
             vmax: Optional[float] = None) -> plt.Figure:
        """
        Plot heatmap
        
        Args:
            data: DataFrame containing the matrix data
            vmin: Minimum value for color scaling
            vmax: Maximum value for color scaling
            
        Returns:
            The matplotlib Figure object
        """
        self.create_figure(figsize=(max(8, len(data.columns)), max(6, len(data.index))))
        ax = self.get_axes()
        
        # Create the heatmap
        fmt = '.1f' if self.show_values else ''
        sns.heatmap(data, annot=self.show_values, fmt=fmt, linewidths=.5,
                   cmap=self.color_map, ax=ax, vmin=vmin, vmax=vmax)
            
        self.add_annotations()
        return self.get_figure()


class ScatterPlot(Visualization):
    """Scatter plot for showing relationships between two variables"""
    
    def __init__(
        self,
        title: str = "Relationship",
        x_label: str = "X",
        y_label: str = "Y",
        add_trendline: bool = True,
        **kwargs
    ):
        """
        Initialize a scatter plot
        
        Args:
            title: Plot title
            x_label: Label for x-axis
            y_label: Label for y-axis
            add_trendline: Whether to add a regression line
            **kwargs: Additional arguments for the base Visualization class
        """
        super().__init__(title, **kwargs)
        self.x_label = x_label
        self.y_label = y_label
        self.add_trendline = add_trendline
        
    def plot(self, data: pd.DataFrame, x_column: str, y_column: str,
             color_column: Optional[str] = None, 
             size_column: Optional[str] = None,
             alpha: float = 0.7) -> plt.Figure:
        """
        Plot scatter plot
        
        Args:
            data: DataFrame containing the data
            x_column: Column name for x-axis
            y_column: Column name for y-axis
            color_column: Optional column to determine point colors
            size_column: Optional column to determine point sizes
            alpha: Transparency of points
            
        Returns:
            The matplotlib Figure object
        """
        self.create_figure()
        ax = self.get_axes()
        
        # Determine point sizes if applicable
        sizes = None
        if size_column:
            sizes = data[size_column] * 100 / data[size_column].max()
            
        # Create the scatter plot
        if color_column:
            scatter = sns.scatterplot(
                x=x_column, y=y_column, 
                hue=color_column, 
                size=size_column,
                data=data, 
                alpha=alpha,
                ax=ax
            )
            plt.legend(title=color_column, bbox_to_anchor=(1.05, 1), loc='upper left')
        else:
            scatter = sns.scatterplot(
                x=x_column, y=y_column, 
                size=size_column,
                data=data, 
                alpha=alpha,
                ax=ax
            )
        
        # Add trendline if requested
        if self.add_trendline and len(data) > 1:
            # Filter out NaN values
            valid_data = data[[x_column, y_column]].dropna()
            if len(valid_data) > 1:
                sns.regplot(
                    x=x_column, y=y_column, 
                    data=valid_data,
                    scatter=False, 
                    ax=ax,
                    line_kws={"color": "red", "alpha": 0.7, "lw": 2}
                )
        
        ax.set_xlabel(self.x_label)
        ax.set_ylabel(self.y_label)
        
        self.add_annotations()
        return self.get_figure()


class CohortHeatmap(Visualization):
    """Cohort analysis heatmap visualization"""
    
    def __init__(
        self,
        title: str = "Cohort Analysis",
        color_map: str = "YlGnBu",
        value_format: str = "{:.1%}",
        **kwargs
    ):
        """
        Initialize a cohort heatmap
        
        Args:
            title: Plot title
            color_map: Matplotlib colormap name
            value_format: Format string for cell values
            **kwargs: Additional arguments for the base Visualization class
        """
        super().__init__(title, **kwargs)
        self.color_map = color_map
        self.value_format = value_format
        
    def plot(self, cohort_data: pd.DataFrame) -> plt.Figure:
        """
        Plot cohort heatmap
        
        Args:
            cohort_data: DataFrame with cohort periods as index and retention periods as columns
            
        Returns:
            The matplotlib Figure object
        """
        rows, cols = cohort_data.shape
        figsize = (max(10, cols * 0.8), max(8, rows * 0.5))
        self.create_figure()
        ax = self.get_axes()
        
        # Create the heatmap
        sns.heatmap(
            cohort_data, 
            mask=cohort_data.isnull(), 
            annot=True, 
            fmt='.1%',
            cmap=self.color_map,
            vmin=0.0, 
            vmax=cohort_data.max().max(),
            ax=ax
        )
        
        # Format axes
        ax.set_xlabel('Periods Since First Use')
        ax.set_ylabel('Cohort')
        
        # Format y-axis tick labels to show cohort period
        cohort_size_labels = [f"{idx} ({cohort_data.loc[idx, 0]:.0%})" for idx in cohort_data.index]
        ax.set_yticklabels(cohort_size_labels)
        
        self.add_annotations()
        return self.get_figure()


class DashboardLayout:
    """Helper class for creating multi-plot dashboards"""
    
    def __init__(
        self,
        title: str,
        rows: int = 2,
        cols: int = 2,
        width: int = 16,
        height: int = 10,
        subtitle: Optional[str] = None
    ):
        """
        Initialize a dashboard layout
        
        Args:
            title: Dashboard title
            rows: Number of subplot rows
            cols: Number of subplot columns
            width: Figure width in inches
            height: Figure height in inches
            subtitle: Optional dashboard subtitle
        """
        self.title = title
        self.subtitle = subtitle
        self.rows = rows
        self.cols = cols
        self.width = width
        self.height = height
        self.figure, self.axes = plt.subplots(rows, cols, figsize=(width, height))
        self.current_position = (0, 0)
        
        # Add the dashboard title
        self.figure.suptitle(title, fontsize=16, y=0.98)
        if subtitle:
            self.figure.text(0.5, 0.94, subtitle, 
                            ha='center', fontsize=12, style='italic')
    
    def get_axis(self, row: Optional[int] = None, col: Optional[int] = None):
        """Get axis at specified position or current position"""
        if row is None:
            row = self.current_position[0]
        if col is None:
            col = self.current_position[1]
            
        if self.rows == 1 and self.cols == 1:
            return self.axes
        elif self.rows == 1:
            return self.axes[col]
        elif self.cols == 1:
            return self.axes[row]
        else:
            return self.axes[row, col]
    
    def add_plot(self, visualization: Visualization, 
                 row: Optional[int] = None, 
                 col: Optional[int] = None,
                 data: Optional[pd.DataFrame] = None,
                 **plot_kwargs):
        """
        Add a visualization to the dashboard
        
        Args:
            visualization: Visualization object to add
            row: Row position (0-based)
            col: Column position (0-based)
            data: Data to plot
            **plot_kwargs: Arguments to pass to the plot method
        """
        if row is None:
            row = self.current_position[0]
        if col is None:
            col = self.current_position[1]
            
        # Get the axis for this position
        ax = self.get_axis(row, col)
        
        # Clear any existing content
        ax.clear()
        
        # Get the figure from the visualization (without showing it)
        if data is not None:
            viz_fig = visualization.plot(data, **plot_kwargs)
        else:
            viz_fig = visualization.get_figure()
            
        # Copy the axes content to our dashboard
        viz_ax = visualization.get_axes()
        
        # Copy the plot elements
        for line in viz_ax.lines:
            ax.add_line(line.copy())
        for patch in viz_ax.patches:
            ax.add_patch(patch.copy())
        for text in viz_ax.texts:
            ax.text(text.get_position()[0], text.get_position()[1], text.get_text())
        for collection in viz_ax.collections:
            ax.add_collection(collection)
            
        # Copy the axis properties
        ax.set_title(viz_ax.get_title())
        ax.set_xlabel(viz_ax.get_xlabel())
        ax.set_ylabel(viz_ax.get_ylabel())
        ax.set_xlim(viz_ax.get_xlim())
        ax.set_ylim(viz_ax.get_ylim())
        
        # Handle legend if present
        if viz_ax.get_legend() is not None:
            handles, labels = viz_ax.get_legend_handles_labels()
            ax.legend(handles, labels)
            
        # Close the visualization figure
        visualization.close()
        
        # Update the current position
        col += 1
        if col >= self.cols:
            col = 0
            row += 1
        if row >= self.rows:
            row = 0
        self.current_position = (row, col)
    
    def adjust_layout(self):
        """Adjust the layout for better spacing"""
        plt.tight_layout(rect=[0, 0, 1, 0.93])
    
    def save(self, path: str, dpi: int = 300):
        """Save the dashboard to a file"""
        self.adjust_layout()
        self.figure.savefig(path, dpi=dpi, bbox_inches='tight')
        
    def show(self):
        """Display the dashboard"""
        self.adjust_layout()
        plt.show()
        
    def close(self):
        """Close the figure to free memory"""
        plt.close(self.figure)