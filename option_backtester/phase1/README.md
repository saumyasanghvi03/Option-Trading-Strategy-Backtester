# Phase 1: Option Trading Strategy Backtester - Straddle Premium Decay

This script backtests a simple non-directional options trading strategy: "Straddle Premium Decay (ATM, Non-Directional)" using historical option chain data provided in a CSV file.

## Strategy Implemented
- **Name:** Straddle Premium Decay (ATM, Non-Directional)
- **Symbol:** NIFTY (default in `main.py`, can be changed) or BANKNIFTY (present in sample data).
- **Entry Time:** 9:20 AM (configurable in `main.py` by passing to `run_straddle_backtest`).
- **Action:** Sell 1 At-The-Money (ATM) Call Option + 1 At-The-Money (ATM) Put Option (same strike).
    - *Note for Phase 1:* The script assumes the provided data for a given timestamp already contains the relevant ATM strike. Dynamic ATM strike identification is planned for future phases.
- **Exit Time:** 3:00 PM (EOD Square-off, configurable).
- **Target/Stop Loss:** No specific target or stop loss is implemented in Phase 1.
- **PnL Logic:** (Total Premium Sold at Entry) - (Total Premium at Exit) = Net Profit/Loss per lot.
- **Lot Size:** Assumed to be 1 for PnL calculation (configurable in `run_straddle_backtest`).

## Project Structure
```
option_backtester/
├── phase1/
│   ├── main.py             # Main script to run the backtest
│   ├── data_handler.py     # Loads data from CSV
│   ├── strategy_engine.py  # Implements the trading strategy logic
│   ├── visualizer.py       # Generates PnL charts and tables
│   ├── sample_data.csv     # Sample input data
│   ├── requirements.txt    # Python dependencies
│   └── README.md           # This file
└── README.md               # Root README
```

## Setup and Installation

1.  **Clone the repository (if you haven't already).**
2.  **Navigate to the phase1 directory:**
    ```bash
    cd path/to/option_backtester/phase1
    ```
3.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
4.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Running the Backtester

Execute the `main.py` script from within the `option_backtester/phase1/` directory:
```bash
python main.py
```

## Input Data (`sample_data.csv`)
The backtester uses a CSV file for input. The `sample_data.csv` provides an example.
Required columns:
- `Timestamp`: Date and time of the option price (e.g., `YYYY-MM-DD HH:MM:SS`)
- `Symbol`: Trading symbol (e.g., `NIFTY`, `BANKNIFTY`)
- `Strike`: Strike price of the option
- `Type`: Option type (`CE` for Call, `PE` for Put)
- `Price`: Price of the option at the given timestamp
- `OI`: Open Interest (currently not used in Phase 1 logic but good to have)

## Expected Output
1.  **Console Output:**
    - Status messages during data loading and backtesting.
    - Summary of backtest results (Total PnL, number of trades).
    - A table detailing PnL for each trade day.
2.  **Plotly Charts:**
    - A cumulative PnL curve showing profit/loss over time.
    - A bar chart showing daily PnL.
    (These charts will attempt to open in a web browser if your environment supports it.)

## Code Modules
- `main.py`: Orchestrates the backtesting process.
- `data_handler.py`: Contains `load_option_data_from_csv` to read and parse the input CSV.
- `strategy_engine.py`: Contains `run_straddle_backtest` which implements the core strategy logic.
- `visualizer.py`: Contains functions (`plot_pnl_curve`, `plot_daily_pnl_bar_chart`, `display_pnl_table`) for creating visual and tabular reports using Plotly.
