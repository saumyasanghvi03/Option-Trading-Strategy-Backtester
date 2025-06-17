"""
This module implements the core strategy logic for the Option Trading Strategy Backtester.
Currently, it contains a function to backtest a simple ATM straddle strategy.
"""
import pandas as pd
from typing import List, Dict, Tuple

def run_straddle_backtest(
    data: pd.DataFrame,
    symbol: str,
    entry_time_str: str = '09:20:00',
    exit_time_str: str = '15:00:00',
    lot_size: int = 1 # Assuming 1 lot for Phase 1, can be parameterized later
) -> pd.DataFrame:
    """
    Backtests a non-directional ATM straddle strategy.

    Args:
        data: DataFrame containing option data
              (Timestamp, Symbol, Strike, Type, Price, OI).
              Timestamp should be datetime objects.
        symbol: The symbol to backtest (e.g., 'NIFTY', 'BANKNIFTY').
        entry_time_str: Entry time in 'HH:MM:SS' format.
        exit_time_str: Exit time in 'HH:MM:SS' format.
        lot_size: The lot size for PnL calculation.

    Returns:
        A pandas DataFrame with daily PnL results:
        [Date, Symbol, Strike, Entry_Premium_CE, Entry_Premium_PE,
         Exit_Premium_CE, Exit_Premium_PE, Net_PnL]
    """
    if data is None or data.empty:
        print("Error: Input data is empty or None.")
        return pd.DataFrame()

    # Filter for the specific symbol
    symbol_data = data[data['Symbol'].str.upper() == symbol.upper()].copy()
    if symbol_data.empty:
        print(f"Warning: No data found for symbol {symbol}.")
        return pd.DataFrame()

    # Ensure Timestamp is datetime and extract date and time
    symbol_data['Date'] = symbol_data['Timestamp'].dt.date
    symbol_data['Time'] = symbol_data['Timestamp'].dt.time

    # Convert entry and exit time strings to time objects
    try:
        entry_time = pd.to_datetime(entry_time_str).time()
        exit_time = pd.to_datetime(exit_time_str).time()
    except ValueError:
        print("Error: Invalid entry or exit time format. Use HH:MM:SS.")
        return pd.DataFrame()

    results = []

    # Group by date and strike (as ATM strike is assumed to be in data for Phase 1)
    # If multiple strikes are provided for the same symbol on the same day,
    # this will treat each as a separate straddle opportunity.
    for (date, strike), group in symbol_data.groupby(['Date', 'Strike']):
        entry_data = group[group['Time'] == entry_time]
        exit_data = group[group['Time'] == exit_time]

        if entry_data.empty or exit_data.empty:
            # print(f"Info: Missing entry or exit data for {symbol} strike {strike} on {date}.")
            continue

        entry_ce = entry_data[entry_data['Type'] == 'CE']['Price'].values
        entry_pe = entry_data[entry_data['Type'] == 'PE']['Price'].values
        exit_ce = exit_data[exit_data['Type'] == 'CE']['Price'].values
        exit_pe = exit_data[exit_data['Type'] == 'PE']['Price'].values

        if not (len(entry_ce) > 0 and len(entry_pe) > 0 and \
                len(exit_ce) > 0 and len(exit_pe) > 0):
            # print(f"Info: Missing CE or PE data for entry/exit for {symbol} strike {strike} on {date}.")
            continue

        # Take the first price if multiple entries (should not happen with current data)
        entry_premium_ce = entry_ce[0]
        entry_premium_pe = entry_pe[0]
        exit_premium_ce = exit_ce[0]
        exit_premium_pe = exit_pe[0]

        total_premium_sold = entry_premium_ce + entry_premium_pe
        total_premium_at_exit = exit_premium_ce + exit_premium_pe

        net_pnl = (total_premium_sold - total_premium_at_exit) * lot_size

        results.append({
            'Date': date,
            'Symbol': symbol,
            'Strike': strike,
            'Entry_Premium_CE': entry_premium_ce,
            'Entry_Premium_PE': entry_premium_pe,
            'Exit_Premium_CE': exit_premium_ce,
            'Exit_Premium_PE': exit_premium_pe,
            'Net_PnL': net_pnl
        })

    if not results:
        print(f"Warning: No trades were executed for {symbol}. Check data and time parameters.")
        return pd.DataFrame()

    return pd.DataFrame(results)
