"""
This module provides functions for visualizing backtesting results,
including PnL curves, bar charts, and tables, using Plotly.
"""
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots # Required if using Plotly table alongside console print

def plot_pnl_curve(pnl_df: pd.DataFrame, title: str = "Cumulative PnL Curve") -> go.Figure | None:
    """
    Plots the cumulative PnL curve.

    Args:
        pnl_df: DataFrame with at least 'Date' and 'Net_PnL' columns.
        title: The title for the plot.

    Returns:
        A Plotly figure object or None if input is invalid.
    """
    if pnl_df is None or pnl_df.empty or 'Net_PnL' not in pnl_df.columns or 'Date' not in pnl_df.columns:
        print("Error: Invalid DataFrame for PnL curve. Ensure 'Date' and 'Net_PnL' columns exist.")
        return None

    # Ensure Date is sorted for cumulative sum
    plot_df = pnl_df.sort_values(by='Date').copy()
    plot_df['Cumulative_PnL'] = plot_df['Net_PnL'].cumsum()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=plot_df['Date'], y=plot_df['Cumulative_PnL'], mode='lines+markers', name='Cumulative PnL'))
    fig.update_layout(title=title, xaxis_title='Date', yaxis_title='Cumulative PnL')
    return fig

def plot_daily_pnl_bar_chart(pnl_df: pd.DataFrame, title: str = "Daily PnL Bar Chart") -> go.Figure | None:
    """
    Plots a bar chart of daily PnL.

    Args:
        pnl_df: DataFrame with at least 'Date' and 'Net_PnL' columns.
        title: The title for the plot.

    Returns:
        A Plotly figure object or None if input is invalid.
    """
    if pnl_df is None or pnl_df.empty or 'Net_PnL' not in pnl_df.columns or 'Date' not in pnl_df.columns:
        print("Error: Invalid DataFrame for Daily PnL bar chart. Ensure 'Date' and 'Net_PnL' columns exist.")
        return None

    plot_df = pnl_df.sort_values(by='Date').copy()

    fig = go.Figure()
    fig.add_trace(go.Bar(x=plot_df['Date'], y=plot_df['Net_PnL'], name='Daily PnL'))
    fig.update_layout(title=title, xaxis_title='Date', yaxis_title='Daily PnL')
    return fig

def display_pnl_table(pnl_df: pd.DataFrame, use_plotly_table: bool = False) -> go.Figure | None:
    """
    Displays the PnL results.
    Prints to console by default, or returns a Plotly table figure.

    Args:
        pnl_df: DataFrame with PnL results.
        use_plotly_table: If True, generates and returns a Plotly table figure.
                          Otherwise, prints to console and returns None.

    Returns:
        A Plotly figure object if use_plotly_table is True, otherwise None.
    """
    if pnl_df is None or pnl_df.empty:
        print("Info: PnL DataFrame is empty. Nothing to display.")
        return None

    print("\n--- PnL Results Table ---")
    print(pnl_df.to_string()) # Print full DataFrame to console

    if use_plotly_table:
        # Ensure all columns are of suitable types for Plotly table (e.g., strings, numbers)
        table_df = pnl_df.copy()
        for col in table_df.columns:
            if pd.api.types.is_datetime64_any_dtype(table_df[col]):
                table_df[col] = table_df[col].astype(str) # Convert datetime to string
            elif pd.api.types.is_timedelta64_ns_dtype(table_df[col]):
                 table_df[col] = table_df[col].astype(str)


        fig = go.Figure(data=[go.Table(
            header=dict(values=list(table_df.columns),
                        fill_color='paleturquoise',
                        align='left'),
            cells=dict(values=[table_df[col] for col in table_df.columns],
                       fill_color='lavender',
                       align='left'))
        ])
        fig.update_layout(title_text="PnL Results Table (Plotly)")
        return fig
    return None
