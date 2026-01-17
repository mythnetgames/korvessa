"""
Damage Type System

Handles different damage types and resistance modifiers.
Used for psychic damage and environmental damage.
"""

# =============================================================================
# DAMAGE TYPES
# =============================================================================

DAMAGE_TYPE_PHYSICAL = "physical"
DAMAGE_TYPE_PSYCHIC = "psychic"
DAMAGE_TYPE_ENVIRONMENTAL = "environmental"
DAMAGE_TYPE_POISON = "poison"
DAMAGE_TYPE_FIRE = "fire"
DAMAGE_TYPE_COLD = "cold"


# =============================================================================
# DAMAGE APPLICATION
# =============================================================================

def apply_damage_with_resistance(character, damage, damage_type=DAMAGE_TYPE_PHYSICAL):
    """
    Apply damage to a character with personality and racial resistances.
    
    Args:
        character: The character receiving damage
        damage (int/float): Base damage amount
        damage_type (str): Type of damage
        
    Returns:
        float: Final damage after resistances
    """
    from world.personality_passives import get_psychic_resistance, get_environmental_resistance
    
    final_damage = float(damage)
    
    # Apply psychic resistance (Devoted passive)
    if damage_type == DAMAGE_TYPE_PSYCHIC:
        psychic_mult = get_psychic_resistance(character)
        final_damage *= psychic_mult
    
    # Apply environmental resistance (Freehands passive + dwarf racial)
    if damage_type in [DAMAGE_TYPE_ENVIRONMENTAL, DAMAGE_TYPE_POISON, DAMAGE_TYPE_FIRE, DAMAGE_TYPE_COLD]:
        env_mult = get_environmental_resistance(character)
        final_damage *= env_mult
    
    return final_damage


def apply_psychic_damage(character, damage, source=None):
    """
    Apply psychic damage to a character.
    
    Devoted passive provides 25% resistance.
    
    Args:
        character: The character receiving damage
        damage (int/float): Base psychic damage
        source: Source of the damage (optional)
        
    Returns:
        float: Actual damage dealt
    """
    final_damage = apply_damage_with_resistance(character, damage, DAMAGE_TYPE_PSYCHIC)
    
    # Apply to character's HP
    if hasattr(character.db, 'hp'):
        old_hp = character.db.hp
        character.db.hp -= int(final_damage)
        character.db.hp = max(0, character.db.hp)
        actual_damage = old_hp - character.db.hp
        
        # Message
        if actual_damage > 0:
            character.msg(f"|rYou take |w{int(actual_damage)}|r psychic damage!|n")
            if source:
                character.msg(f"|xSource: {source}|n")
        
        return actual_damage
    
    return 0


def apply_environmental_damage(character, damage, damage_subtype=DAMAGE_TYPE_ENVIRONMENTAL, source=None):
    """
    Apply environmental damage to a character.
    
    Freehands passive and dwarf racial provide resistance (stacks).
    
    Args:
        character: The character receiving damage
        damage (int/float): Base environmental damage
        damage_subtype (str): Specific type (poison, fire, cold, etc.)
        source: Source of the damage (optional)
        
    Returns:
        float: Actual damage dealt
    """
    final_damage = apply_damage_with_resistance(character, damage, damage_subtype)
    
    # Apply to character's HP
    if hasattr(character.db, 'hp'):
        old_hp = character.db.hp
        character.db.hp -= int(final_damage)
        character.db.hp = max(0, character.db.hp)
        actual_damage = old_hp - character.db.hp
        
        # Message
        if actual_damage > 0:
            damage_name = damage_subtype.replace('_', ' ').title()
            character.msg(f"|rYou take |w{int(actual_damage)}|r {damage_name} damage!|n")
            if source:
                character.msg(f"|xSource: {source}|n")
        
        return actual_damage
    
    return 0
