"""
This module provides utility functions for finding option strikes,
such as At-The-Money (ATM) strike based on the underlying's LTP.
"""
import math # math.isclose can be useful for float comparisons if needed, not directly for round

def get_atm_strike(ltp: float, step: int = 50) -> int:
    """
    Calculates the At-The-Money (ATM) strike price.

    Args:
        ltp: The Last Traded Price of the underlying instrument.
        step: The step size for strike prices (e.g., 50 for NIFTY, 100 for BANKNIFTY).
              Must be a positive integer.

    Returns:
        The calculated ATM strike price as an integer.
        Returns 0 or raises ValueError if inputs are invalid.
    """
    if not isinstance(ltp, (int, float)) or ltp <= 0:
        # Or raise ValueError("LTP must be a positive number.")
        print("Error: LTP must be a positive number.")
        return 0 # Or handle error as per project's error strategy

    if not isinstance(step, int) or step <= 0:
        # Or raise ValueError("Step must be a positive integer.")
        print("Error: Step must be a positive integer.")
        return 0 # Or handle error as per project's error strategy

    return int(round(ltp / step) * step)
