"""
SafetyNet Utilities

Helper functions for the SafetyNet system.
"""

import random
from evennia.utils import delay
from world.safetynet.constants import (
    PASSWORD_WORDS_1,
    PASSWORD_WORDS_2,
    WRISTPAD_DELAY_READ,
    WRISTPAD_DELAY_POST,
    WRISTPAD_DELAY_DM,
    WRISTPAD_DELAY_SEARCH,
    WRISTPAD_DELAY_HACK,
    WRISTPAD_DELAY_LOGIN,
    COMPUTER_DELAY_READ,
    COMPUTER_DELAY_POST,
    COMPUTER_DELAY_DM,
    COMPUTER_DELAY_SEARCH,
    COMPUTER_DELAY_HACK,
    COMPUTER_DELAY_LOGIN,
    MSG_NO_DEVICE,
    MSG_CONNECTING,
)


def check_access_device(character):
    """
    Check if character has an access device for SafetyNet.
    
    Priority:
    1. Wristpad (slower connection)
    2. Computer in room (faster connection)
    
    Args:
        character: The character to check
        
    Returns:
        tuple: (device_type, device_obj) or (None, None) if no device
               device_type is "wristpad" or "computer"
    """
    # Check inventory for wristpad
    for obj in character.contents:
        if getattr(obj.db, "is_wristpad", False):
            return ("wristpad", obj)
    
    # Check room for computer terminal
    if character.location:
        for obj in character.location.contents:
            if getattr(obj.db, "is_computer", False):
                return ("computer", obj)
    
    return (None, None)


def get_connection_delay(device_type, action):
    """
    Get the connection delay based on device type and action.
    
    Args:
        device_type: "wristpad" or "computer"
        action: One of "read", "post", "dm", "search", "hack", "login"
        
    Returns:
        float: Delay in seconds
    """
    delays = {
        "wristpad": {
            "read": WRISTPAD_DELAY_READ,
            "post": WRISTPAD_DELAY_POST,
            "dm": WRISTPAD_DELAY_DM,
            "search": WRISTPAD_DELAY_SEARCH,
            "hack": WRISTPAD_DELAY_HACK,
            "login": WRISTPAD_DELAY_LOGIN,
        },
        "computer": {
            "read": COMPUTER_DELAY_READ,
            "post": COMPUTER_DELAY_POST,
            "dm": COMPUTER_DELAY_DM,
            "search": COMPUTER_DELAY_SEARCH,
            "hack": COMPUTER_DELAY_HACK,
            "login": COMPUTER_DELAY_LOGIN,
        }
    }
    
    device_delays = delays.get(device_type, delays["wristpad"])
    return device_delays.get(action, 1.0)


def generate_password():
    """
    Generate a two-word password phrase.
    
    Returns:
        str: A password like "chrome runner" or "neon ghost"
    """
    word1 = random.choice(PASSWORD_WORDS_1)
    word2 = random.choice(PASSWORD_WORDS_2)
    return f"{word1} {word2}"


def delayed_output(character, message, delay_seconds, show_connecting=True):
    """
    Send output to character after a delay, simulating connection time.
    
    Args:
        character: The character to send to
        message: The message to send
        delay_seconds: How long to wait
        show_connecting: Whether to show "Connecting..." message
    """
    if show_connecting and delay_seconds > 0.5:
        character.msg(MSG_CONNECTING)
    
    def send_delayed():
        if character:
            character.msg(message)
    
    if delay_seconds <= 0:
        character.msg(message)
    else:
        delay(delay_seconds, send_delayed)


def format_timestamp(timestamp):
    """
    Format a timestamp for display.
    
    Args:
        timestamp: datetime object
        
    Returns:
        str: Formatted string like "2h ago" or "15m ago"
    """
    from datetime import datetime, timezone
    
    now = datetime.now(timezone.utc)
    if timestamp.tzinfo is None:
        # Assume UTC if no timezone
        from datetime import timezone as tz
        timestamp = timestamp.replace(tzinfo=tz.utc)
    
    diff = now - timestamp
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes}m ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours}h ago"
    else:
        days = int(seconds / 86400)
        return f"{days}d ago"


def resolve_hack(attacker, target_handle_data, online_status, ice_rating):
    """
    Resolve a hacking attempt.
    
    Args:
        attacker: The character attempting the hack
        target_handle_data: The target handle's data dict
        online_status: Whether the target is online (bool)
        ice_rating: The target's ICE rating (int)
        
    Returns:
        tuple: (success, margin, message)
               success: bool
               margin: int (positive = success margin, negative = failure margin)
               message: str describing the result
    """
    from world.safetynet.constants import (
        HACK_BASE_DIFFICULTY,
        HACK_SKILL,
        HACK_STAT,
        ICE_ONLINE_MODIFIER,
        ICE_OFFLINE_MODIFIER,
    )
    
    # Get attacker's skill
    skill_value = getattr(attacker.db, HACK_SKILL, 0) or 0
    stat_value = getattr(attacker, HACK_STAT, 1) or 1
    
    # Calculate attacker's roll: skill + stat + d20
    attacker_roll = skill_value + stat_value + random.randint(1, 20)
    
    # Calculate difficulty
    difficulty = HACK_BASE_DIFFICULTY + ice_rating
    if online_status:
        difficulty += ICE_ONLINE_MODIFIER  # Easier when online
    else:
        difficulty += ICE_OFFLINE_MODIFIER  # Harder when offline
    
    margin = attacker_roll - difficulty
    success = margin >= 0
    
    if success:
        if margin >= 10:
            message = "Clean breach. Full access granted."
        elif margin >= 5:
            message = "Access granted. Minor traces detected."
        else:
            message = "Access granted. Narrowly avoided detection."
    else:
        if margin <= -10:
            message = "Critical failure. ICE counterattack triggered."
        elif margin <= -5:
            message = "Access denied. Intrusion logged."
        else:
            message = "Access denied. Connection terminated."
    
    return (success, margin, message)


def get_online_indicator(handle_name, manager):
    """
    Get the online/offline indicator for a handle.
    
    Args:
        handle_name: The handle to check
        manager: The SafetyNetManager instance
        
    Returns:
        str: ANSI-colored indicator string
    """
    from world.safetynet.constants import (
        INDICATOR_ONLINE,
        INDICATOR_OFFLINE,
        SYSTEM_HANDLE,
    )
    
    # System never shows online/offline
    if handle_name.lower() == SYSTEM_HANDLE.lower():
        return ""
    
    if manager.is_handle_online(handle_name):
        return INDICATOR_ONLINE
    else:
        return INDICATOR_OFFLINE
