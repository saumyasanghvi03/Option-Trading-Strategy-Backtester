"""
This module defines the ATM (At-The-Money) Straddle strategy.

An ATM Straddle involves simultaneously selling (or buying)
both a Call (CE) and a Put (PE) option of the same underlying asset,
same expiry, and same strike price (which is ATM).

This file provides a default configuration for this strategy.
"""
from typing import Dict, Any

def get_default_config() -> Dict[str, Any]:
    """
    Returns a default configuration dictionary for the ATM Straddle strategy.
    This configuration can be used as a base and potentially overridden by
    a user-provided JSON/YAML configuration file.
    """
    config = {
        "strategy_name": "ATM Straddle",
        "underlying": "NIFTY",  # Default underlying
        "lot_size": 50,         # Example for NIFTY
        "entry_time": "09:20:00",
        "exit_time": "15:00:00",
        "strike_selection": {
            "method": "ATM",
            "step": 50  # Step for NIFTY (50 points)
        },
        "legs": [
            {
                "instrument_type": "CE",
                "action": "SELL",
                "quantity_lots": 1,
                "sl_pct": 25.0  # Stop loss percentage for this leg
            },
            {
                "instrument_type": "PE",
                "action": "SELL",
                "quantity_lots": 1,
                "sl_pct": 25.0  # Stop loss percentage for this leg
            }
        ],
        "target_pnl_pct": 50.0  # Target PnL as a percentage of total premium collected
        # Other parameters like "data_path" would typically be outside this
        # specific strategy config, managed by the main execution environment.
    }
    return config
