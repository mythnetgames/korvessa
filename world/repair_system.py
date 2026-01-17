"""
Repair System for Weapons and Armor

Allows characters to repair damaged equipment.
Artificer personality gets 50% faster repairs.
"""

import time

# =============================================================================
# REPAIR CONSTANTS
# =============================================================================

# Base repair times (in seconds)
BASE_REPAIR_TIME_WEAPON = 300  # 5 minutes
BASE_REPAIR_TIME_ARMOR = 600   # 10 minutes

# Durability restoration per repair
REPAIR_DURABILITY_RESTORE = 20  # Restores 20 durability per repair action


# =============================================================================
# REPAIR FUNCTIONS
# =============================================================================

def can_repair_item(character, item):
    """
    Check if a character can repair an item.
    
    Args:
        character: The character attempting repair
        item: The item to repair
        
    Returns:
        tuple: (can_repair: bool, reason: str)
    """
    if not item:
        return (False, "No item specified.")
    
    # Check if item has durability
    if not hasattr(item.db, 'durability') or not hasattr(item.db, 'durability_max'):
        return (False, "This item cannot be repaired.")
    
    # Check if item needs repair
    if item.db.durability >= item.db.durability_max:
        return (False, "This item is already at full durability.")
    
    # Check if character is already repairing
    if hasattr(character.ndb, 'repairing_item') and character.ndb.repairing_item:
        return (False, "You are already repairing something.")
    
    return (True, None)


def get_repair_time(character, item):
    """
    Calculate repair time for an item.
    
    Args:
        character: The character repairing
        item: The item being repaired
        
    Returns:
        float: Repair time in seconds
    """
    from world.personality_passives import get_repair_time_multiplier
    
    # Determine base time
    item_type = getattr(item.db, 'item_type', 'misc')
    if item_type in ['weapon', 'melee', 'ranged']:
        base_time = BASE_REPAIR_TIME_WEAPON
    elif item_type == 'armor':
        base_time = BASE_REPAIR_TIME_ARMOR
    else:
        base_time = BASE_REPAIR_TIME_WEAPON
    
    # Apply personality passive
    time_mult = get_repair_time_multiplier(character)
    
    return base_time * time_mult


def start_repair(character, item):
    """
    Start repairing an item.
    
    Args:
        character: The character repairing
        item: The item to repair
        
    Returns:
        bool: True if repair started successfully
    """
    can_repair, reason = can_repair_item(character, item)
    if not can_repair:
        character.msg(f"|r{reason}|n")
        return False
    
    repair_time = get_repair_time(character, item)
    
    # Store repair state
    character.ndb.repairing_item = item
    character.ndb.repair_start_time = time.time()
    character.ndb.repair_duration = repair_time
    
    minutes = int(repair_time // 60)
    seconds = int(repair_time % 60)
    
    character.msg(f"|yYou begin repairing {item.get_display_name(character)}.|n")
    character.msg(f"|yEstimated time: {minutes}m {seconds}s|n")
    
    # Schedule completion
    from evennia.utils import delay
    delay(repair_time, complete_repair, character, item)
    
    return True


def complete_repair(character, item):
    """
    Complete a repair action.
    
    Args:
        character: The character repairing
        item: The item being repaired
    """
    # Check if still repairing this item
    if not hasattr(character.ndb, 'repairing_item') or character.ndb.repairing_item != item:
        return
    
    # Restore durability
    old_durability = item.db.durability
    item.db.durability = min(item.db.durability + REPAIR_DURABILITY_RESTORE, item.db.durability_max)
    
    restored = item.db.durability - old_durability
    
    character.msg(f"|gYou finish repairing {item.get_display_name(character)}.|n")
    character.msg(f"|gDurability restored: |w+{restored}|g (now {item.db.durability}/{item.db.durability_max})|n")
    
    # Clear repair state
    character.ndb.repairing_item = None
    character.ndb.repair_start_time = None
    character.ndb.repair_duration = None


def cancel_repair(character, notify=True):
    """
    Cancel an in-progress repair.
    
    Args:
        character: The character canceling
        notify: Whether to send a message
        
    Returns:
        bool: True if a repair was canceled
    """
    if hasattr(character.ndb, 'repairing_item') and character.ndb.repairing_item:
        item = character.ndb.repairing_item
        
        # Clear state
        character.ndb.repairing_item = None
        character.ndb.repair_start_time = None
        character.ndb.repair_duration = None
        
        if notify:
            character.msg(f"|yYou stop repairing {item.get_display_name(character)}.|n")
        
        return True
    
    return False


def get_repair_status(character):
    """
    Get current repair status for a character.
    
    Args:
        character: The character to check
        
    Returns:
        dict or None: Repair status info
    """
    if not hasattr(character.ndb, 'repairing_item') or not character.ndb.repairing_item:
        return None
    
    elapsed = time.time() - character.ndb.repair_start_time
    remaining = max(0, character.ndb.repair_duration - elapsed)
    progress = min(100, (elapsed / character.ndb.repair_duration) * 100)
    
    return {
        'item': character.ndb.repairing_item,
        'elapsed': elapsed,
        'remaining': remaining,
        'progress': progress,
        'total_time': character.ndb.repair_duration
    }
