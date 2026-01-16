"""
Economy Utilities

Helper functions for the economy system including time formatting
and payday calculations.
"""

import time


def now_ts():
    """Get current Unix timestamp."""
    return time.time()


def format_seconds_to_dhm(seconds):
    """
    Convert seconds to days, hours, minutes tuple.
    
    Args:
        seconds: Number of seconds
        
    Returns:
        tuple: (days, hours, minutes)
    """
    if seconds < 0:
        seconds = 0
    
    days = int(seconds // 86400)
    remaining = seconds % 86400
    hours = int(remaining // 3600)
    remaining = remaining % 3600
    minutes = int(remaining // 60)
    
    return (days, hours, minutes)


def format_time_remaining(seconds):
    """
    Format seconds as a human-readable string.
    
    Args:
        seconds: Number of seconds remaining
        
    Returns:
        str: Formatted time string like "2 days, 5 hours, 30 minutes"
    """
    days, hours, minutes = format_seconds_to_dhm(seconds)
    
    parts = []
    if days > 0:
        parts.append(f"{days} day{'s' if days != 1 else ''}")
    if hours > 0:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes > 0 or not parts:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    
    return ", ".join(parts)


def payday_next_due_ts(anchor_ts, last_claim_ts, current_ts, period_seconds):
    """
    Calculate the next payday due timestamp.
    
    Payday is due every period_seconds after the anchor. Claiming late
    does not shift the schedule - it stays aligned to the anchor.
    
    Args:
        anchor_ts: The anchor timestamp (usually character creation)
        last_claim_ts: Timestamp of last claim (or None if never claimed)
        current_ts: Current timestamp
        period_seconds: Length of each payday period in seconds
        
    Returns:
        float: Timestamp when next payday is due
    """
    if not anchor_ts:
        return current_ts  # No anchor means immediate eligibility
    
    # First due date is anchor + one period
    first_due = anchor_ts + period_seconds
    
    if last_claim_ts is None:
        # Never claimed - first due is the target
        return first_due
    
    # Find which period the last claim was in
    # Period 0 = anchor to anchor+period (first_due)
    # Period 1 = first_due to first_due+period
    # etc.
    
    # Calculate how many periods have passed since anchor
    time_since_anchor = last_claim_ts - anchor_ts
    claimed_period = int(time_since_anchor // period_seconds)
    
    # Next due is the start of the next period after the one claimed
    next_period = claimed_period + 1
    next_due = anchor_ts + (next_period * period_seconds)
    
    return next_due


def can_claim_payday(anchor_ts, last_claim_ts, current_ts, period_seconds):
    """
    Check if a payday can be claimed now.
    
    Args:
        anchor_ts: The anchor timestamp
        last_claim_ts: Timestamp of last claim (or None)
        current_ts: Current timestamp
        period_seconds: Length of each payday period
        
    Returns:
        tuple: (can_claim: bool, next_due_ts: float, seconds_until_due: float)
    """
    next_due = payday_next_due_ts(anchor_ts, last_claim_ts, current_ts, period_seconds)
    seconds_until = next_due - current_ts
    can_claim = seconds_until <= 0
    
    return (can_claim, next_due, max(0, seconds_until))


def format_currency(amount):
    """
    Format a currency amount for display.
    
    Args:
        amount: Integer amount in dollars
        
    Returns:
        str: Formatted string like "$1,234"
    """
    from world.economy.constants import CURRENCY_SYMBOL
    return f"{CURRENCY_SYMBOL}{amount:,}"
