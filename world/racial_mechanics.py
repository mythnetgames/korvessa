"""
Racial Mechanics - Human, Elf, and Dwarf

Racial perks implemented:
- Human: Hourly reroll on failed non-combat rolls
- Elf: Advantage on non-combat Subterfuge rolls
- Dwarf: Slower hunger/thirst/intoxication (handled in survival system)
"""

import time
import random


# =============================================================================
# HUMAN REROLL MECHANIC
# =============================================================================

def get_human_reroll_data(character):
    """Get the character's human reroll state."""
    if not hasattr(character, 'ndb'):
        return None
    return getattr(character.ndb, 'human_reroll_data', None)


def init_human_reroll_data(character):
    """Initialize human reroll data on a character."""
    if not hasattr(character, 'ndb'):
        return
    
    character.ndb.human_reroll_data = {
        'last_reroll_time': 0,  # timestamp of last reroll used
        'reroll_available': True,
        'next_available': 0,
    }


def can_use_human_reroll(character):
    """
    Check if character can use their human reroll.
    Reroll is available once per hour (3600 seconds).
    
    Returns:
        tuple: (can_reroll: bool, time_until_next: float or 0)
    """
    race = getattr(character, 'race', 'human').lower()
    if race != 'human':
        return (False, 0)
    
    data = get_human_reroll_data(character)
    if not data:
        init_human_reroll_data(character)
        data = get_human_reroll_data(character)
    
    current_time = time.time()
    last_reroll = data.get('last_reroll_time', 0)
    time_since_reroll = current_time - last_reroll
    
    # Reroll available if 3600+ seconds (1 hour) have passed
    if time_since_reroll >= 3600:
        return (True, 0)
    else:
        time_until = 3600 - time_since_reroll
        return (False, time_until)


def use_human_reroll(character):
    """
    Use the character's human reroll.
    Returns the current timestamp.
    
    Returns:
        float: current timestamp, or None if reroll not available
    """
    can_use, time_until = can_use_human_reroll(character)
    if not can_use:
        return None
    
    data = get_human_reroll_data(character)
    if not data:
        return None
    
    current_time = time.time()
    data['last_reroll_time'] = current_time
    
    return current_time


def get_time_until_human_reroll(character):
    """Get seconds until next human reroll is available."""
    can_use, time_until = can_use_human_reroll(character)
    if can_use:
        return 0
    return time_until


# =============================================================================
# ELF SUBTERFUGE ADVANTAGE
# =============================================================================

def has_elf_subterfuge_advantage(character):
    """Check if character has elf advantage on Subterfuge rolls."""
    race = getattr(character, 'race', 'human').lower()
    return race == 'elf'


def apply_elf_subterfuge_advantage(roll_result):
    """
    Apply elf advantage to a subterfuge roll.
    Rolls twice and takes the higher result.
    
    Args:
        roll_result: Original roll result dict with 'roll' key
        
    Returns:
        dict: Updated roll result with advantage applied
    """
    if not isinstance(roll_result, dict) or 'roll' not in roll_result:
        return roll_result
    
    original_roll = roll_result['roll']
    
    # Roll again
    second_roll = random.randint(1, 20)  # Assuming d20 system
    
    # Take the higher
    advantaged_roll = max(original_roll, second_roll)
    
    roll_result['original_roll'] = original_roll
    roll_result['second_roll'] = second_roll
    roll_result['roll'] = advantaged_roll
    roll_result['elf_advantage_applied'] = True
    
    return roll_result


# =============================================================================
# LANGUAGE SYSTEM INTEGRATION
# =============================================================================

def get_race_languages(character):
    """
    Get the languages a character knows based on their race.
    
    Returns:
        list: Language names
    """
    race = getattr(character, 'race', 'human').lower()
    
    # Base: all races get Common
    languages = ['common']
    
    # Racial languages
    if race == 'elf':
        languages.append('elvish')
    elif race == 'dwarf':
        languages.append('dwarvish')
    
    return languages


def initialize_race_languages(character):
    """
    Initialize character's known languages based on race.
    Called during character creation.
    """
    try:
        from world.language.constants import LANGUAGES
        
        race_langs = get_race_languages(character)
        
        if not hasattr(character, 'db'):
            return
        
        # Initialize known languages
        if not character.db.known_languages:
            character.db.known_languages = {}
        
        for lang in race_langs:
            if lang.lower() in LANGUAGES:
                # Set to 100 (fluent) for native languages
                character.db.known_languages[lang.lower()] = 100
    except Exception:
        pass  # Language system not critical


# =============================================================================
# INITIALIZATION
# =============================================================================

def apply_racial_mechanics(character):
    """
    Apply all racial mechanics to a newly created character.
    Called after character creation.
    """
    race = getattr(character, 'race', 'human').lower()
    
    # Human: initialize reroll system
    if race == 'human':
        init_human_reroll_data(character)
    
    # All races: initialize languages
    initialize_race_languages(character)
