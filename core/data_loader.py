"""
This module handles loading and processing of historical options data
from multiple per-day CSV files stored in a directory.
"""
import os
import pandas as pd
from typing import Optional, List # For older Python compatibility

def load_historical_data(
    data_directory: str,
    file_prefix: str = "", # e.g., "NIFTY_" if files are NIFTY_YYYY-MM-DD.csv
    start_date_str: Optional[str] = None,
    end_date_str: Optional[str] = None
) -> Optional[pd.DataFrame]:
    """
    Loads historical options data from per-day CSV files in a specified directory.
    Files are expected to be named in a way that includes the date,
    e.g., 'YYYY-MM-DD.csv' or 'PREFIX_YYYY-MM-DD.csv'.
    CSVs must contain: timestamp (HH:MM:SS or YYYY-MM-DD HH:MM:SS),
                       underlying_ltp, strike, type, price, oi, symbol.

    Args:
        data_directory: Path to the directory containing the CSV files.
        file_prefix: Optional prefix for filenames if they follow a pattern
                     like 'PREFIX_YYYY-MM-DD.csv'.
        start_date_str: Optional start date string (YYYY-MM-DD).
                        If provided, only files on or after this date are loaded.
        end_date_str: Optional end date string (YYYY-MM-DD).
                      If provided, only files on or before this date are loaded.

    Returns:
        A pandas DataFrame containing combined data from all relevant files,
        sorted by timestamp, or None if a critical error occurs.
    """
    if not os.path.isdir(data_directory):
        print(f"Error: Data directory '{data_directory}' not found.")
        return None

    all_data = []

    start_dt = pd.to_datetime(start_date_str) if start_date_str else None
    end_dt = pd.to_datetime(end_date_str) if end_date_str else None

    expected_columns = ['timestamp', 'underlying_ltp', 'strike', 'type', 'price', 'oi', 'symbol']

    for filename in sorted(os.listdir(data_directory)):
        if filename.startswith(file_prefix) and filename.endswith(".csv"):
            try:
                # Extract date from filename (e.g., YYYY-MM-DD from PREFIX_YYYY-MM-DD.csv)
                date_part_str = filename[len(file_prefix):-4] # Remove prefix and .csv
                file_date = pd.to_datetime(date_part_str)
            except ValueError:
                print(f"Warning: Could not parse date from filename '{filename}'. Skipping.")
                continue

            if (start_dt and file_date < start_dt) or \
               (end_dt and file_date > end_dt):
                continue

            file_path = os.path.join(data_directory, filename)
            try:
                daily_df = pd.read_csv(file_path)

                # Validate columns (case-insensitive check)
                daily_df.columns = daily_df.columns.str.lower()
                if not all(col in daily_df.columns for col in expected_columns):
                    print(f"Warning: File {filename} is missing one or more expected columns ({expected_columns}). Skipping.")
                    continue

                # Timestamp handling:
                # If 'timestamp' column is already full datetime, use it.
                # If 'timestamp' is just time, combine with file_date.
                if not pd.api.types.is_datetime64_any_dtype(daily_df['timestamp']):
                    try:
                        # Attempt to parse as datetime directly (in case it's YYYY-MM-DD HH:MM:SS)
                        temp_ts = pd.to_datetime(daily_df['timestamp'])
                        # Check if date part is missing (e.g., all dates are 1900-01-01 if only time was given)
                        if temp_ts.dt.date.nunique() == 1 and temp_ts.dt.date.iloc[0] == pd.Timestamp('1900-01-01').date():
                            raise ValueError("Timestamp seems to be time only")
                        daily_df['timestamp'] = temp_ts
                    except ValueError: # If direct parsing fails or it's time only
                         # Assume 'timestamp' column is time (HH:MM:SS) and combine with file_date
                        daily_df['timestamp'] = pd.to_datetime(
                            file_date.strftime('%Y-%m-%d') + ' ' + daily_df['timestamp'].astype(str)
                        )

                all_data.append(daily_df)
            except Exception as e:
                print(f"Error reading or processing file {filename}: {e}. Skipping.")
                continue

    if not all_data:
        print("No data loaded. Check directory, filenames, date range, or file content.")
        return None

    combined_df = pd.concat(all_data, ignore_index=True)
    combined_df = combined_df.sort_values(by='timestamp').reset_index(drop=True)

    # Final check for essential numeric columns
    for col in ['underlying_ltp', 'strike', 'price', 'oi']:
        if col in combined_df.columns:
            combined_df[col] = pd.to_numeric(combined_df[col], errors='coerce')
        else: # Should have been caught by column check, but as a safeguard
            print(f"Critical Error: Column {col} missing after concat. This should not happen.")
            return None

    return combined_df
