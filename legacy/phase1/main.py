"""
Main script for the Option Trading Strategy Backtester (Phase 1).

This script orchestrates the backtesting process by:
1. Loading option data from a CSV file using the data_handler module.
2. Running a predefined trading strategy (e.g., ATM straddle) using the strategy_engine module.
3. Generating and displaying PnL results and visualizations using the visualizer module.

The script is designed to be run from the `option_backtester/phase1/` directory.
"""
import pandas as pd
from data_handler import load_option_data_from_csv
from strategy_engine import run_straddle_backtest
from visualizer import plot_pnl_curve, plot_daily_pnl_bar_chart, display_pnl_table

def main():
    print("--- Option Trading Strategy Backtester ---")

    # Configuration
    csv_file_path = 'sample_data.csv' # Relative to the phase1 directory
    symbol_to_backtest = 'NIFTY' # Example: NIFTY or BANKNIFTY
    # Entry and exit times can be defaults in strategy_engine or specified here
    # entry_time = '09:20:00'
    # exit_time = '15:00:00'
    # lot_size = 1 # Example lot size

    print(f"Loading data for {symbol_to_backtest} from {csv_file_path}...")
    option_data_df = load_option_data_from_csv(csv_file_path)

    if option_data_df is None or option_data_df.empty:
        print("Failed to load data. Exiting.")
        return

    print("Running backtest...")
    # Pass symbol. Entry/exit times and lot size will use defaults in `run_straddle_backtest`
    # or can be passed explicitly:
    # results_df = run_straddle_backtest(option_data_df, symbol_to_backtest,
    #                                   entry_time_str=entry_time, exit_time_str=exit_time,
    #                                   lot_size=lot_size)
    results_df = run_straddle_backtest(option_data_df, symbol_to_backtest)

    if results_df is None or results_df.empty:
        print("Backtest did not generate any results. Exiting.")
        return

    print("\n--- Backtest Summary ---")
    total_pnl = results_df['Net_PnL'].sum()
    num_trades = len(results_df)
    print(f"Total Net PnL: {total_pnl:.2f}")
    print(f"Number of trades (days with data): {num_trades}")

    # Display PnL Table (console output by default)
    # Set use_plotly_table=True to generate a Plotly table figure (might not show in all envs)
    display_pnl_table(results_df, use_plotly_table=False)

    print("\nGenerating PnL visualizations...")

    # PnL Curve
    fig_pnl_curve = plot_pnl_curve(results_df, title=f"Cumulative PnL Curve for {symbol_to_backtest}")
    if fig_pnl_curve:
        print("Displaying PnL Curve (if environment supports it)...")
        try:
            fig_pnl_curve.show()
        except Exception as e:
            print(f"Could not display PnL curve automatically: {e}")
            print("Consider saving the plot to a file if running in a non-GUI environment.")


    # Daily PnL Bar Chart
    fig_daily_pnl_bar = plot_daily_pnl_bar_chart(results_df, title=f"Daily PnL for {symbol_to_backtest}")
    if fig_daily_pnl_bar:
        print("Displaying Daily PnL Bar Chart (if environment supports it)...")
        try:
            fig_daily_pnl_bar.show()
        except Exception as e:
            print(f"Could not display Daily PnL bar chart automatically: {e}")
            print("Consider saving the plot to a file if running in a non-GUI environment.")

    # Optional: Plotly table display (if preferred over console)
    # fig_plotly_table = display_pnl_table(results_df, use_plotly_table=True)
    # if fig_plotly_table:
    #     print("Displaying PnL Table (Plotly)...")
    #     try:
    #         fig_plotly_table.show()
    #     except Exception as e:
    #         print(f"Could not display Plotly table automatically: {e}")

    print("\n--- Backtesting Complete ---")

if __name__ == '__main__':
    # Need to ensure pandas can be imported by the subtask for this test run.
    # The requirements.txt is in phase1, so this script expects to be run from phase1 dir
    # or have the path configured.
    # For subtask, assume CWD is option_backtester/phase1 or /app
    # Let's adjust imports for potential execution from /app
    # by trying to adjust sys.path if direct imports fail.
    # This is tricky in subtask. Best to assume it's run from option_backtester/phase1

    # The subtask environment should handle imports if files are in the same dir.
    # Let's ensure the files are placed in option_backtester/phase1
    # and the main.py is also in option_backtester/phase1
    # Then direct imports data_handler, strategy_engine, visualizer should work.
    main()
