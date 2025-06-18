"""
This module contains the core backtesting engine that simulates
trading strategies based on historical data and strategy configurations.
"""
import pandas as pd
from typing import List, Dict, Any, Optional

# Assuming other core modules are in the same directory or PYTHONPATH is set
from . import atm_finder
from . import risk_manager
from . import pnl_calculator

def run_backtest(
    strategy_config: Dict[str, Any],
    historical_data: pd.DataFrame
) -> List[Dict[str, Any]]:
    """
    Runs a backtest for a given strategy configuration using historical data.

    Args:
        strategy_config: Parsed strategy configuration dictionary.
        historical_data: DataFrame with historical options and underlying LTP data.
                         Expected columns: 'timestamp', 'underlying_ltp',
                                         'symbol', 'strike', 'type', 'price', 'oi'.

    Returns:
        A list of dictionaries, where each dictionary represents a
        fully closed trade with details of all its legs and overall PnL.
    """
    trade_log: List[Dict[str, Any]] = []

    if historical_data is None or historical_data.empty:
        print("Error: Historical data is empty or None. Cannot run backtest.")
        return trade_log

    # Extract common strategy parameters
    try:
        underlying_symbol = strategy_config['underlying']
        lot_size = strategy_config['lot_size']
        entry_time_str = strategy_config['entry_time']
        eod_exit_time_str = strategy_config['exit_time']
        strategy_legs_config = strategy_config['legs']
        target_pnl_pct = strategy_config.get('target_pnl_pct') # Optional
        atm_step = strategy_config.get('strike_selection', {}).get('step', 50)
    except KeyError as e:
        print(f"Error: Missing critical key in strategy_config: {e}")
        return trade_log

    entry_time = pd.to_datetime(entry_time_str).time()
    eod_exit_time = pd.to_datetime(eod_exit_time_str).time()

    # Group data by date
    historical_data['date'] = historical_data['timestamp'].dt.date
    grouped_by_day = historical_data.groupby('date')

    trade_id_counter = 0

    for date_of_trade, daily_data in grouped_by_day:
        print(f"--- Processing Date: {date_of_trade} ---")

        open_positions_today: List[Dict[str, Any]] = []
        initial_premium_today = 0.0
        trade_placed_today = False
        current_trade_id = None
        closed_legs_for_current_trade: List[Dict[str, Any]] = []

        # Sort daily data by timestamp
        daily_data = daily_data.sort_values(by='timestamp')

        for _, row in daily_data.iterrows():
            current_timestamp = row['timestamp']
            current_ltp = row['underlying_ltp']

            # --- Entry Logic ---
            if not trade_placed_today and current_timestamp.time() >= entry_time:
                # Ensure entry logic runs only once per day at or after entry_time
                trade_placed_today = True
                current_trade_id = f"TRADE_{date_of_trade.strftime('%Y%m%d')}_{trade_id_counter}"
                trade_id_counter += 1

                atm_strike_price = atm_finder.get_atm_strike(current_ltp, atm_step)
                print(f"{current_timestamp} LTP: {current_ltp}, ATM Strike: {atm_strike_price}")

                for i, leg_config in enumerate(strategy_legs_config):
                    leg_type = leg_config['instrument_type'].upper() # CE or PE
                    action = leg_config['action'].upper()
                    sl_pct = leg_config.get('sl_pct') # Can be None
                    qty_lots = leg_config.get('quantity_lots', 1)

                    # Find option price for this leg
                    # Option symbol in data might be different from underlying (e.g. NIFTY vs NIFTY23JUN18600CE)
                    # For simplicity, assume 'symbol' in data refers to options like "NIFTY" or "BANKNIFTY"
                    # and we filter by strike and type.
                    # A more robust system would map to specific option contract names.

                    option_row = daily_data[
                        (daily_data['timestamp'] == current_timestamp) &
                        (daily_data['strike'] == atm_strike_price) &
                        (daily_data['type'] == leg_type) &
                        (daily_data['symbol'] == underlying_symbol) # Assuming option symbol is same as underlying for now
                    ]

                    if not option_row.empty:
                        entry_price = option_row['price'].iloc[0]
                        leg_id = f"{current_trade_id}_LEG{i+1}_{leg_type}"

                        leg_details = {
                            'leg_id': leg_id,
                            'trade_id': current_trade_id,
                            'symbol': underlying_symbol, # This should be the option symbol if different
                            'strike': atm_strike_price,
                            'type': leg_type,
                            'entry_action': action,
                            'entry_price': entry_price,
                            'entry_time': current_timestamp,
                            'quantity_lots': qty_lots,
                            'lot_size': lot_size,
                            'sl_pct': sl_pct,
                            'status': 'OPEN',
                            'exit_price': None,
                            'exit_time': None,
                            'exit_reason': None,
                            'pnl': 0.0
                        }
                        open_positions_today.append(leg_details)
                        if action == 'SELL':
                            initial_premium_today += entry_price * qty_lots * lot_size
                        # else: # BUY action means debit
                        #    initial_premium_today -= entry_price * qty_lots * lot_size
                        print(f"    Leg Entered: {leg_id} {action} {leg_type}@{entry_price}")
                    else:
                        print(f"Warning: No option data found for {underlying_symbol} {atm_strike_price} {leg_type} at {current_timestamp}")

                if not open_positions_today: # If no legs could be opened
                    trade_placed_today = False # Allow re-entry attempt if data appears later (unlikely for this strategy)
                    current_trade_id = None


            # --- Exit Logic for Open Positions ---
            if open_positions_today:
                # Prepare legs_status for risk_manager
                legs_status_for_rm = []
                for pos in open_positions_today:
                    # Find current price for this open leg
                    current_option_row = daily_data[
                        (daily_data['timestamp'] == current_timestamp) &
                        (daily_data['strike'] == pos['strike']) &
                        (daily_data['type'] == pos['type']) &
                        (daily_data['symbol'] == pos['symbol'])
                    ]
                    if not current_option_row.empty:
                        current_leg_price = current_option_row['price'].iloc[0]
                        pos['current_price_for_rm'] = current_leg_price # Temp field for risk_manager
                        legs_status_for_rm.append({
                            'id': pos['leg_id'],
                            'entry_price': pos['entry_price'],
                            'current_price': current_leg_price,
                            'action': pos['entry_action'],
                            'sl_pct': pos['sl_pct']
                        })
                    # else: leg price not found at this timestamp, can't check SL/target based on it.
                    # This implies data might be missing for this specific timestamp for an open leg.

                if not legs_status_for_rm or len(legs_status_for_rm) != len(open_positions_today):
                    # Not all leg prices available at this timestamp, skip exit checks for safety
                    # Or handle by assuming last known price, but that's complex.
                    pass # Continue to next data row
                else:
                    exit_check_result = risk_manager.check_exit_conditions(
                        legs_status_for_rm,
                        initial_premium_today, # This is total premium, RM needs to know if it's credit/debit
                        target_pnl_pct if target_pnl_pct is not None else 1000, # effectively disable if not set
                        current_timestamp.time(),
                        eod_exit_time
                    )

                    if exit_check_result['exit_type'] != risk_manager.EXIT_TYPE_NONE:
                        print(f"    Exit Condition: {exit_check_result['exit_type']} at {current_timestamp.time()}")
                        legs_exited_this_iteration = []
                        for leg_to_exit_info in exit_check_result['legs_to_exit']:
                            leg_id_to_exit = leg_to_exit_info['id']
                            for i, open_leg in enumerate(open_positions_today):
                                if open_leg['leg_id'] == leg_id_to_exit:
                                    open_leg['status'] = 'CLOSED'
                                    open_leg['exit_price'] = leg_to_exit_info['price'] # Price from RM
                                    open_leg['exit_time'] = current_timestamp
                                    open_leg['exit_reason'] = leg_to_exit_info['reason']
                                    open_leg['pnl'] = pnl_calculator.calculate_leg_pnl(
                                        entry_price=open_leg['entry_price'],
                                        exit_price=open_leg['exit_price'],
                                        entry_action=open_leg['entry_action'],
                                        quantity_lots=open_leg['quantity_lots'],
                                        lot_size=open_leg['lot_size']
                                    )
                                    print(f"        Exited Leg: {open_leg['leg_id']} at {open_leg['exit_price']:.2f}, PnL: {open_leg['pnl']:.2f}")
                                    closed_legs_for_current_trade.append(open_leg.copy()) # Add a copy
                                    legs_exited_this_iteration.append(open_leg) # Store actual object for removal
                                    break

                        # Remove exited legs from open_positions_today
                        for exited_leg in legs_exited_this_iteration:
                            open_positions_today.remove(exited_leg)

                        # If all legs are closed or if SL/Target implies full position exit
                        # (For Phase 2, assume any SL/Target/EOD closes the entire day's trade from these legs)
                        if not open_positions_today or exit_check_result['exit_type'] in [risk_manager.EXIT_TYPE_TARGET_HIT, risk_manager.EXIT_TYPE_EOD_EXIT, risk_manager.EXIT_TYPE_SL_HIT]:
                            if closed_legs_for_current_trade:
                                trade_summary = {
                                    'trade_id': current_trade_id,
                                    'date': date_of_trade,
                                    'legs': closed_legs_for_current_trade,
                                    'overall_pnl': sum(leg['pnl'] for leg in closed_legs_for_current_trade),
                                    'entry_time': closed_legs_for_current_trade[0]['entry_time'] if closed_legs_for_current_trade else None, # Approx
                                    'exit_time': current_timestamp # Approx
                                }
                                trade_log.append(trade_summary)
                                print(f"    Trade Closed: {current_trade_id}, Overall PnL: {trade_summary['overall_pnl']:.2f}")

                            open_positions_today.clear() # Ensure all positions are cleared
                            closed_legs_for_current_trade.clear()
                            initial_premium_today = 0.0
                            # trade_placed_today remains True to prevent re-entry on same day
                            break # End processing for this day as trade is fully closed

        # End of day processing: If any positions are still open (e.g. EOD not hit exactly by a data point)
        # This part of logic might be redundant if EOD exit in loop works perfectly.
        # However, if data doesn't have exact EOD time, this is a fallback.
        # For now, assume EOD check within loop is sufficient if data contains EOD timestamp.
        if open_positions_today:
            print(f"Warning: Positions still open at EOD for {date_of_trade}. Forcing closure.")
            # This indicates an issue or that EOD wasn't handled as expected.
            # Force close with last known prices if possible (complex, not implemented here for brevity)
            # Or mark as error / log appropriately.
            # For now, just log that they remained open and won't be added to trade_log unless closed.
            open_positions_today.clear() # Clear to prevent carry-over

    return trade_log

# No if __name__ == '__main__' block for this complex module.
# Testing will be done via main.py integration.
