"""
This module provides functions for calculating Profit and Loss (PnL)
for individual option legs and overall trades.
"""
from typing import List, Dict, Any, Literal # For older Python compatibility

def calculate_leg_pnl(
    entry_price: float,
    exit_price: float,
    entry_action: Literal['BUY', 'SELL'],
    quantity_lots: int,
    lot_size: int
) -> float:
    """
    Calculates the Profit and Loss for a single options leg.

    Args:
        entry_price: The price at which the leg was entered.
        exit_price: The price at which the leg was exited.
        entry_action: The action taken at entry ('BUY' or 'SELL').
        quantity_lots: The number of lots traded for this leg.
        lot_size: The number of shares per lot for the instrument.

    Returns:
        The calculated PnL for the leg. Can be positive (profit) or negative (loss).
    """
    if not isinstance(quantity_lots, int) or quantity_lots <= 0:
        raise ValueError("Quantity in lots must be a positive integer.")
    if not isinstance(lot_size, int) or lot_size <= 0:
        raise ValueError("Lot size must be a positive integer.")
    if entry_action.upper() not in ['BUY', 'SELL']:
        raise ValueError("Entry action must be 'BUY' or 'SELL'.")

    price_difference = 0
    if entry_action.upper() == 'SELL': # Short position
        price_difference = entry_price - exit_price
    elif entry_action.upper() == 'BUY': # Long position
        price_difference = exit_price - entry_price

    return price_difference * quantity_lots * lot_size

def calculate_total_trade_pnl(
    closed_legs_details: List[Dict[str, Any]],
    default_lot_size: int # Used if a leg doesn't specify its own lot_size
) -> float:
    """
    Calculates the total PnL for a trade consisting of multiple closed legs.

    Args:
        closed_legs_details: A list of dictionaries, where each dictionary
                             represents a closed leg and must contain:
                             'entry_price' (float),
                             'exit_price' (float),
                             'entry_action' (Literal['BUY', 'SELL']),
                             'quantity_lots' (int),
                             'lot_size' (int, optional, overrides default_lot_size).
        default_lot_size: The lot size to use if not specified per leg.


    Returns:
        The total PnL for the trade.
    """
    total_pnl = 0.0
    for leg in closed_legs_details:
        try:
            leg_pnl = calculate_leg_pnl(
                entry_price=leg['entry_price'],
                exit_price=leg['exit_price'],
                entry_action=leg['entry_action'],
                quantity_lots=leg['quantity_lots'],
                lot_size=leg.get('lot_size', default_lot_size) # Use leg-specific LS or default
            )
            total_pnl += leg_pnl
        except KeyError as e:
            print(f"Warning: Missing required key {e} in leg details: {leg}. Skipping this leg for PnL calculation.")
        except ValueError as e:
            print(f"Warning: Invalid data for leg {leg.get('id', 'Unknown')}: {e}. Skipping this leg.")
    return total_pnl
