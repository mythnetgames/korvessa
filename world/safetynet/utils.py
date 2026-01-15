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
    Resolve a hacking attempt using Decking skill and Smarts stat.
    
    Smarts has a MASSIVE role in hacking. A genius with moderate decking skill
    will outperform a pea-brain with maxed decking. Both are important, but
    raw intelligence is key to understanding and exploiting system weaknesses.
    
    Args:
        attacker: The character attempting the hack
        target_handle_data: The target handle's data dict
        online_status: Whether the target is online (bool)
        ice_rating: The target's ICE rating (int)
        
    Returns:
        tuple: (success, margin, message, roll, target_number)
               success: bool
               margin: int (positive = success margin, negative = failure margin)
               message: str describing the result
               roll: int (1-100)
               target_number: int (the target number for the roll)
    """
    # Get attacker's Smarts stat (1-10 scale) - MASSIVE factor in hacking
    smarts = getattr(attacker, 'smrt', 1)
    if not isinstance(smarts, (int, float)) or smarts is None or smarts < 1:
        smarts = 1
    smarts = int(smarts)
    
    # Get attacker's Decking skill - try multiple possible storage formats
    decking_skill = 0
    
    # Try direct character db attributes (primary storage format)
    decking_skill = getattr(attacker.db, 'decking', 0) or 0
    
    # Try capitalized version
    if decking_skill == 0:
        decking_skill = getattr(attacker.db, 'Decking', 0) or 0
    
    # Try hacking aliases
    if decking_skill == 0:
        decking_skill = getattr(attacker.db, 'hacking', 0) or 0
    if decking_skill == 0:
        decking_skill = getattr(attacker.db, 'Hacking', 0) or 0
    
    # Fallback: try skills dict (backup storage format)
    if decking_skill == 0 and hasattr(attacker.db, 'skills') and attacker.db.skills is not None:
        if isinstance(attacker.db.skills, dict):
            decking_skill = attacker.db.skills.get('Decking', 0) or 0
            if decking_skill == 0:
                decking_skill = attacker.db.skills.get('decking', 0) or 0
    
    # SMARTS MODIFIER - Intelligence is CRITICAL for hacking
    # SMARTS 7 is baseline (0 modifier)
    # Above 7: +7 per point (8=+7, 9=+14, 10=+21)
    # Below 7: -20 per point (6=-20, 5=-40, 4=-60, 3=-80, 2=-100, 1=-120)
    # No INT investment = ~1/400 chance with maxed decking
    if smarts >= 7:
        smarts_bonus = (smarts - 7) * 7  # 0 at 7, +7 at 8, +14 at 9, +21 at 10
    else:
        smarts_bonus = (smarts - 7) * 20  # -20 at 6, -40 at 5, -60 at 4, -80 at 3, -100 at 2, -120 at 1
    
    # Low skill check - need at least 20 skill to have a chance
    # Smarts modifier applies but cannot fully compensate for no skill
    # At minimum 1%, even massive smarts can't help with zero skill
    effective_skill = decking_skill + max(0, smarts_bonus // 2)  # Only positive smarts helps threshold
    if effective_skill < 20:
        # Unskilled hackers have essentially no chance
        roll = random.randint(1, 100)
        if roll == 1:
            # 1% critical success even with no skill
            margin = 5
            message = "Access granted. Narrowly avoided detection."
            return (True, margin, message, roll, 1)
        else:
            # Always fail
            margin = -50
            if roll >= 90:
                message = "Critical failure. ICE counterattack triggered."
            else:
                message = "Access denied. Insufficient skill to breach ICE."
            return (False, margin, message, roll, 1)
    
    # Skill check: roll d100 vs (skill + smarts_mod + modifiers - ICE difficulty)
    # Base bonus for skilled deckers - smarts 7 is neutral baseline
    base_bonus = 35  # Restored since smarts 7 is now neutral
    online_bonus = 10 if online_status else 0  # Small bonus for online targets
    
    # ICE difficulty scaling - skill-friendly for deckers:
    # ICE rating / 2 means 3 ICE = 1.5 difficulty, 50 ICE = 25, 100 ICE = 50
    ice_difficulty = ice_rating / 2
    
    # Final calculation: decking + smarts_mod + base + online - ice (min 1%)
    # Example: 100 decking - 120 smarts(1) + 35 base - 50 ice(100) = -35 -> capped to 1%
    # Example: 50 decking + 21 smarts(10) + 35 base + 10 online - 25 ice(50) = 91%
    # Genius with moderate skill dominates pea-brain with maxed skill
    target_number = max(1, min(95, decking_skill + smarts_bonus + base_bonus + online_bonus - ice_difficulty))
    roll = random.randint(1, 100)
    
    margin = target_number - roll
    success = roll <= target_number
    
    # Critical results
    if roll == 1:
        # Critical success
        margin = 50  # High margin for critical
        message = "Clean breach. Full access granted."
    elif roll == 100:
        # Critical failure
        margin = -50
        message = "Critical failure. ICE counterattack triggered."
    elif success:
        # Regular success
        if margin >= 30:
            message = "Clean breach. Full access granted."
        elif margin >= 15:
            message = "Access granted. Minor traces detected."
        else:
            message = "Access granted. Narrowly avoided detection."
    else:
        # Regular failure
        if margin <= -30:
            message = "Critical failure. ICE counterattack triggered."
        elif margin <= -15:
            message = "Access denied. Intrusion logged."
        else:
            message = "Access denied. Connection terminated."
    
    return (success, margin, message, roll, target_number)


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
