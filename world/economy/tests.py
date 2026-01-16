"""
Economy System Tests

Unit tests for the economy system.
Run with: evennia test world.economy.tests
"""

import time
from world.economy.utils import (
    now_ts,
    format_seconds_to_dhm,
    format_time_remaining,
    payday_next_due_ts,
    can_claim_payday,
    format_currency,
)
from world.economy.constants import PAYDAY_PERIOD_SECONDS


def test_format_seconds_to_dhm():
    """Test time formatting."""
    # 0 seconds
    assert format_seconds_to_dhm(0) == (0, 0, 0)
    
    # 1 minute
    assert format_seconds_to_dhm(60) == (0, 0, 1)
    
    # 1 hour
    assert format_seconds_to_dhm(3600) == (0, 1, 0)
    
    # 1 day
    assert format_seconds_to_dhm(86400) == (1, 0, 0)
    
    # 1 day, 2 hours, 30 minutes
    assert format_seconds_to_dhm(86400 + 7200 + 1800) == (1, 2, 30)
    
    # 7 days
    assert format_seconds_to_dhm(7 * 86400) == (7, 0, 0)
    
    print("test_format_seconds_to_dhm: PASSED")


def test_format_time_remaining():
    """Test human-readable time formatting."""
    # Just minutes
    assert "30 minute" in format_time_remaining(1800)
    
    # Hours and minutes
    result = format_time_remaining(3660)  # 1 hour 1 minute
    assert "1 hour" in result
    assert "1 minute" in result
    
    # Days
    result = format_time_remaining(2 * 86400 + 3600)  # 2 days 1 hour
    assert "2 days" in result
    assert "1 hour" in result
    
    print("test_format_time_remaining: PASSED")


def test_payday_next_due_first_claim():
    """Test payday calculation for first claim."""
    anchor = 1000000  # Some timestamp
    period = PAYDAY_PERIOD_SECONDS  # 7 days
    
    # Never claimed - first due is anchor + period
    next_due = payday_next_due_ts(anchor, None, anchor + 1000, period)
    assert next_due == anchor + period
    
    print("test_payday_next_due_first_claim: PASSED")


def test_payday_next_due_after_claim():
    """Test payday calculation after a claim."""
    anchor = 1000000
    period = PAYDAY_PERIOD_SECONDS
    
    # Claimed during first period (before first due)
    # This should NOT count as claiming period 0, since you can't claim before due
    # Let's claim exactly at first_due
    first_due = anchor + period
    last_claim = first_due + 100  # Claimed shortly after first due
    
    next_due = payday_next_due_ts(anchor, last_claim, first_due + 1000, period)
    # Next due should be anchor + 2*period
    assert next_due == anchor + (2 * period)
    
    print("test_payday_next_due_after_claim: PASSED")


def test_payday_late_claim():
    """Test that claiming late doesn't shift the schedule."""
    anchor = 1000000
    period = PAYDAY_PERIOD_SECONDS
    
    # First due at anchor + period
    first_due = anchor + period
    
    # Claim very late - during the 3rd period
    late_claim = anchor + (2.5 * period)
    
    next_due = payday_next_due_ts(anchor, late_claim, late_claim + 1000, period)
    # Should be anchor + 3*period (start of 4th period)
    assert next_due == anchor + (3 * period)
    
    # The schedule stays aligned to anchor, not shifted by late claim
    print("test_payday_late_claim: PASSED")


def test_can_claim_payday():
    """Test the combined claim check."""
    anchor = 1000000
    period = PAYDAY_PERIOD_SECONDS
    
    # Before first due - cannot claim
    early_time = anchor + (period / 2)  # Halfway through first period
    can_claim, next_due, seconds_until = can_claim_payday(anchor, None, early_time, period)
    assert can_claim == False
    assert seconds_until > 0
    
    # At first due - can claim
    at_due = anchor + period
    can_claim, next_due, seconds_until = can_claim_payday(anchor, None, at_due, period)
    assert can_claim == True
    assert seconds_until == 0
    
    # After claim - cannot claim again until next period
    last_claim = at_due + 100
    after_claim = at_due + 1000
    can_claim, next_due, seconds_until = can_claim_payday(anchor, last_claim, after_claim, period)
    assert can_claim == False
    
    print("test_can_claim_payday: PASSED")


def test_format_currency():
    """Test currency formatting."""
    assert format_currency(0) == "$0"
    assert format_currency(100) == "$100"
    assert format_currency(1000) == "$1,000"
    assert format_currency(1000000) == "$1,000,000"
    
    print("test_format_currency: PASSED")


def run_all_tests():
    """Run all economy tests."""
    print("Running economy tests...")
    print("-" * 40)
    
    test_format_seconds_to_dhm()
    test_format_time_remaining()
    test_payday_next_due_first_claim()
    test_payday_next_due_after_claim()
    test_payday_late_claim()
    test_can_claim_payday()
    test_format_currency()
    
    print("-" * 40)
    print("All economy tests PASSED!")


if __name__ == "__main__":
    run_all_tests()
