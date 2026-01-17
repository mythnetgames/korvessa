"""
Personality Passive Effects System

Central module for checking and applying personality-based passive bonuses.
Each passive is keyed to a personality and provides mechanical benefits.
"""

# =============================================================================
# PASSIVE EFFECT CONSTANTS
# =============================================================================

# Stalwart - Reduced Stamina Loss
STALWART_STAMINA_REGEN_BONUS = 0.15  # +15% stamina regeneration
STALWART_STAMINA_DRAIN_REDUCTION = 0.15  # -15% stamina drain

# Sharp-Eyed - Detect Hidden
SHARP_EYED_PERCEPTION_BONUS = 10  # +10 to perception rolls
SHARP_EYED_AUTO_CHECK_CHANCE = 0.30  # 30% chance to auto-notice hidden things

# Artificer - Faster Repairs
ARTIFICER_REPAIR_TIME_MULTIPLIER = 0.5  # 50% faster repairs (half the time)

# Silver-Tongued - Start Friendlier
SILVER_TONGUED_INITIAL_STANDING = 50  # +50 standing on first meeting

# Hidden - Harder to Detect
HIDDEN_STEALTH_BONUS = 5  # +5% stealth skill
HIDDEN_DISGUISE_SLIP_REDUCTION = 0.25  # -25% chance to slip disguise

# Devoted - Mental Resistance
DEVOTED_PSYCHIC_RESISTANCE = 0.25  # 25% reduction to psychic damage

# Insightful - Auto-Insight (handled in examine/read commands)
# No constants needed - handled procedurally

# Freehands - Environmental Resistance
FREEHANDS_ENV_RESISTANCE = 0.25  # 25% reduction to environmental damage (same as dwarf)


# =============================================================================
# PASSIVE CHECK FUNCTIONS
# =============================================================================

def has_passive(character, passive_key):
    """
    Check if a character has a specific personality passive.
    
    Args:
        character: The character object
        passive_key (str): The passive key to check
        
    Returns:
        bool: True if character has this passive
    """
    if not character:
        return False
    
    stored_passive = getattr(character.db, 'personality_passive', None)
    return stored_passive == passive_key


def get_stamina_modifiers(character):
    """
    Get stamina regen and drain modifiers from personality.
    
    Args:
        character: The character object
        
    Returns:
        tuple: (regen_multiplier, drain_multiplier)
               Both are multipliers (1.0 = no change)
    """
    regen_mult = 1.0
    drain_mult = 1.0
    
    if has_passive(character, 'reduced_stamina_loss'):
        regen_mult += STALWART_STAMINA_REGEN_BONUS  # +15% regen
        drain_mult -= STALWART_STAMINA_DRAIN_REDUCTION  # -15% drain
    
    return regen_mult, drain_mult


def get_perception_bonus(character):
    """
    Get perception bonus from personality.
    
    Args:
        character: The character object
        
    Returns:
        int: Bonus to perception rolls
    """
    if has_passive(character, 'detect_hidden_bonus'):
        return SHARP_EYED_PERCEPTION_BONUS
    return 0


def should_auto_perceive(character):
    """
    Check if Sharp-Eyed passive should trigger an auto-perception check.
    
    Args:
        character: The character object
        
    Returns:
        bool: True if auto-check should trigger
    """
    import random
    if has_passive(character, 'detect_hidden_bonus'):
        return random.random() < SHARP_EYED_AUTO_CHECK_CHANCE
    return False


def get_repair_time_multiplier(character):
    """
    Get repair time multiplier from personality.
    
    Args:
        character: The character object
        
    Returns:
        float: Time multiplier (lower = faster, 0.5 = half time)
    """
    if has_passive(character, 'faster_repairs'):
        return ARTIFICER_REPAIR_TIME_MULTIPLIER
    return 1.0


def get_initial_standing_bonus(character):
    """
    Get initial NPC standing bonus from personality.
    
    Args:
        character: The character object
        
    Returns:
        int: Bonus to initial standing
    """
    if has_passive(character, 'friendlier_start'):
        return SILVER_TONGUED_INITIAL_STANDING
    return 0


def get_stealth_bonus(character):
    """
    Get stealth skill bonus from personality.
    
    Args:
        character: The character object
        
    Returns:
        int: Bonus to stealth skill
    """
    if has_passive(character, 'harder_to_detect'):
        return HIDDEN_STEALTH_BONUS
    return 0


def get_disguise_slip_reduction(character):
    """
    Get disguise slip chance reduction from personality.
    
    Args:
        character: The character object
        
    Returns:
        float: Multiplier for slip chance (0.75 = 25% reduction)
    """
    if has_passive(character, 'harder_to_detect'):
        return 1.0 - HIDDEN_DISGUISE_SLIP_REDUCTION
    return 1.0


def get_psychic_resistance(character):
    """
    Get psychic damage resistance from personality.
    
    Args:
        character: The character object
        
    Returns:
        float: Damage reduction multiplier (0.75 = 25% reduction)
    """
    if has_passive(character, 'mental_resist'):
        return 1.0 - DEVOTED_PSYCHIC_RESISTANCE
    return 1.0


def can_read_any_language(character):
    """
    Check if character can read any language (Insightful passive).
    
    Args:
        character: The character object
        
    Returns:
        bool: True if character can read any language
    """
    return has_passive(character, 'auto_insight')


def get_environmental_resistance(character):
    """
    Get environmental damage resistance from personality and race.
    
    Freehands get dwarf-level resistance. If they ARE a dwarf, it stacks.
    
    Args:
        character: The character object
        
    Returns:
        float: Damage reduction multiplier (0.75 = 25% reduction, 0.50 = 50% if stacked)
    """
    resistance = 1.0
    
    # Freehands passive
    if has_passive(character, 'environmental_resist'):
        resistance -= FREEHANDS_ENV_RESISTANCE
    
    # Dwarf racial bonus
    race = getattr(character.db, 'race', 'human')
    if race == 'dwarf':
        resistance -= FREEHANDS_ENV_RESISTANCE  # Same value, stacks
    
    return max(0.0, resistance)  # Can't go negative


# =============================================================================
# SKILL MODIFIER SYSTEM
# =============================================================================

def get_personality_skill_modifiers(character):
    """
    Get all skill modifiers from personality passives.
    
    Returns dict of {skill_name: bonus_value}
    
    Args:
        character: The character object
        
    Returns:
        dict: Skill modifiers {skill: bonus}
    """
    modifiers = {}
    
    # Hidden - stealth bonus
    stealth_bonus = get_stealth_bonus(character)
    if stealth_bonus:
        modifiers['stealth'] = stealth_bonus
    
    return modifiers


def apply_personality_skill_bonuses(character):
    """
    Apply personality passive skill bonuses to character.
    Called when personality is applied or on login.
    
    Args:
        character: The character object
    """
    modifiers = get_personality_skill_modifiers(character)
    
    if not character.db.skills:
        character.db.skills = {}
    
    for skill, bonus in modifiers.items():
        current = character.db.skills.get(skill, 0)
        # Only apply if not already applied
        if not getattr(character.db, f'personality_passive_{skill}_applied', False):
            character.db.skills[skill] = current + bonus
            character.db.__dict__[f'personality_passive_{skill}_applied'] = True
