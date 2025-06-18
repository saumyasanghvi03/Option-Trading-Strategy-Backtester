"""
This module handles loading and parsing of option data from CSV files
for the Option Trading Strategy Backtester. It uses pandas for data manipulation
and includes basic validation for the loaded data.
"""
import pandas as pd

def load_option_data_from_csv(file_path: str) -> pd.DataFrame | None:
    """
    Loads option data from a CSV file into a pandas DataFrame.

    Args:
        file_path: The path to the CSV file.

    Returns:
        A pandas DataFrame with the option data, or None if an error occurs.
    """
    try:
        df = pd.read_csv(file_path)
        # Basic validation: check for expected columns
        expected_columns = ['Timestamp', 'Symbol', 'Strike', 'Type', 'Price', 'OI']
        if not all(col in df.columns for col in expected_columns):
            print(f"Error: CSV file {file_path} is missing one or more expected columns: {expected_columns}")
            return None
        # Attempt to convert 'Timestamp' to datetime objects
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        return df
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return None
    except pd.errors.EmptyDataError:
        print(f"Error: The file {file_path} is empty.")
        return None
    except pd.errors.ParserError:
        print(f"Error: Could not parse the file {file_path}. Check CSV format.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while reading {file_path}: {e}")
        return None
