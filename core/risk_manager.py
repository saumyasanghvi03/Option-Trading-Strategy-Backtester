"""
This module provides functions to check for trade exit conditions,
such as stop-loss, target profit, or end-of-day.
"""
import pandas as pd
from typing import List, Dict, Any, Literal # For older Python compatibility if needed

EXIT_REASON_SL = "SL"
EXIT_REASON_TARGET = "TARGET"
EXIT_REASON_EOD = "EOD"
EXIT_TYPE_NONE = "NONE"
EXIT_TYPE_SL_HIT = "SL_HIT"
EXIT_TYPE_TARGET_HIT = "TARGET_HIT"
EXIT_TYPE_EOD_EXIT = "EOD_EXIT"

def check_exit_conditions(
    legs_status: List[Dict[str, Any]],
    initial_total_premium_sold: float, # Assuming a net credit strategy like short straddle
    target_pnl_pct_total: float,
    current_datetime_time: pd.Timestamp.time, # Pass only time for EOD check
    eod_exit_time: pd.Timestamp.time
) -> Dict[str, Any]:
    """
    Checks exit conditions for a multi-leg options position.

    Args:
        legs_status: A list of dictionaries, each representing an open leg.
                     Required keys per leg dict:
                     'id' (str), 'entry_price' (float),
                     'current_price' (float), 'action' (str, 'SELL' or 'BUY'),
                     'sl_pct' (float, e.g., 25 for 25%).
        initial_total_premium_sold: Total premium received at entry for net credit strategies.
                                   For net debit, this could be initial_total_cost (positive).
                                   This is used for target profit calculation.
        target_pnl_pct_total: Target profit as a percentage of initial_total_premium_sold.
                              (e.g., 50 for 50% of premium captured).
        current_datetime_time: The time component of the current data point.
        eod_exit_time: The designated end-of-day exit time (time component).

    Returns:
        A dictionary indicating exit type and affected legs.
        Example:
        {'exit_type': 'NONE'}
        {'exit_type': 'SL_HIT', 'legs_to_exit': [{'id': 'CE_leg', 'reason': 'SL'}]}
        {'exit_type': 'TARGET_HIT', 'legs_to_exit': [{'id': 'CE_leg', 'reason': 'TARGET'}, ...]}
        {'exit_type': 'EOD_EXIT', 'legs_to_exit': [...]}
    """
    legs_to_exit_sl = []

    # 1. Check for End-of-Day Exit first
    if current_datetime_time >= eod_exit_time:
        all_open_legs = []
        for leg in legs_status:
            all_open_legs.append({'id': leg['id'], 'reason': EXIT_REASON_EOD, 'price': leg['current_price']})
        if all_open_legs: # Should always be true if position is open
             return {'exit_type': EXIT_TYPE_EOD_EXIT, 'legs_to_exit': all_open_legs}

    # 2. Check for Stop Loss per leg
    for leg in legs_status:
        if leg['action'].upper() == 'SELL':
            sl_price = leg['entry_price'] * (1 + leg['sl_pct'] / 100.0)
            if leg['current_price'] >= sl_price:
                legs_to_exit_sl.append({'id': leg['id'], 'reason': EXIT_REASON_SL, 'price': leg['current_price']})
        elif leg['action'].upper() == 'BUY':
            sl_price = leg['entry_price'] * (1 - leg['sl_pct'] / 100.0)
            if leg['current_price'] <= sl_price:
                legs_to_exit_sl.append({'id': leg['id'], 'reason': EXIT_REASON_SL, 'price': leg['current_price']})

    if legs_to_exit_sl:
        # Decision: If any leg hits SL, does the whole position exit or just the leg?
        # This function will return all legs that hit SL.
        # The engine can decide if this implies full position exit.
        # For now, let's assume if any leg hits SL, the strategy might want to exit all for simplicity
        # or the engine handles partial exits. This function just reports.
        return {'exit_type': EXIT_TYPE_SL_HIT, 'legs_to_exit': legs_to_exit_sl}

    # 3. Check for Target Profit
    # PnL for a short straddle (net credit): initial_premium - current_total_cost_to_buy_back
    current_cost_to_buy_back = 0
    has_open_legs = False
    for leg in legs_status:
        # Assuming all legs are part of the same combined position for target profit
        if leg['action'].upper() == 'SELL': # We sold, so current_price is cost to buy back
            current_cost_to_buy_back += leg['current_price']
            has_open_legs = True
        # Add logic for BUY legs if strategy can be mixed debit/credit for target calc
        # else: current_cost_to_buy_back -= leg['current_price'] # If we bought, current_price is proceeds if sold

    if not has_open_legs: # Should not happen if called with open positions
        return {'exit_type': EXIT_TYPE_NONE}

    current_pnl = initial_total_premium_sold - current_cost_to_buy_back
    target_profit_amount = initial_total_premium_sold * (target_pnl_pct_total / 100.0)

    if current_pnl >= target_profit_amount:
        all_open_legs_for_target = []
        for leg in legs_status:
             all_open_legs_for_target.append({'id': leg['id'], 'reason': EXIT_REASON_TARGET, 'price': leg['current_price']})
        return {'exit_type': EXIT_TYPE_TARGET_HIT, 'legs_to_exit': all_open_legs_for_target}

    return {'exit_type': EXIT_TYPE_NONE}
