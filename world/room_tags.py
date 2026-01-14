"""
Room tag system for environment effects and conditions.

Room tags are settable attributes that affect character interactions and create dynamic environments.
"""

# Active tags - have game effects that occur while in the room
ACTIVE_TAGS = {
    "FIRE": {
        "desc": "Burning damage every 5 seconds",
        "icon": "x",
        "color": "|#ff0000",
        "damage_per_tick": 5,
        "tick_interval": 5,
    },
    "SMOKED OUT": {
        "desc": "Contact high effect (lasts 1 hr after leaving)",
        "icon": "x",
        "color": "|#6c6c6c",
        "effect": "contact_high",
        "duration_minutes": 60,
    },
    "CROWDED": {
        "desc": "Snooping+ Disguise+ Stealing+ Hiding+",
        "icon": "x",
        "color": "|#5f5f00",
        "skill_bonuses": {"snooping": 10, "disguise": 10, "stealing": 10, "hiding": 10},
    },
    "UNSTABLE": {
        "desc": "Chance to fall to rooms below (Dexterity check)",
        "icon": "x",
    },
    "FLOODED": {
        "desc": "Room is filled with water",
        "icon": "x",
        "color": "|#005fff",
    },
    "TREADING WATER": {
        "desc": "More stamina for movement",
        "icon": "x",
        "color": "|#00d7ff",
        "stamina_cost_reduction": 0.5,
    },
    "UNDERWATER": {
        "desc": "Uses stamina pool for breath holding",
        "icon": "x",
        "color": "|#00005f",
    },
}

# Passive tags - informational/buff tags without active damage/effects
PASSIVE_TAGS = {
    "MEDICAL": {
        "desc": "Surgery+ Modern_Medicine+",
        "icon": "o",
        "skill_bonuses": {"surgery": 15, "modern_medicine": 15},
    },
    "STERILE": {
        "desc": "Science+ Chemical+",
        "icon": "o",
        "skill_bonuses": {"science": 10, "chemical": 10},
    },
    "STORE": {
        "desc": "Shop container available - use WARES/LIST to view",
        "icon": "o",
    },
    "ROOFTOP": {
        "desc": "High elevation location",
        "icon": "o",
    },
    "INDOORS": {
        "desc": "Interior location",
        "icon": "o",
    },
    "OUTDOORS": {
        "desc": "Exterior location",
        "icon": "o",
    },
    "OUTSIDE": {
        "desc": "Fresh air (+3 Empathy while sun is out)",
        "icon": "o",
        "empathy_bonus": 3,
        "requires_sunlight": True,
    },
    "FALLING": {
        "desc": "Open air - falling hazard active",
        "icon": "o",
    },
}

# All valid tags
ALL_TAGS = {**ACTIVE_TAGS, **PASSIVE_TAGS}

# Valid tag names (case-insensitive)
VALID_TAG_NAMES = set(ALL_TAGS.keys())


def get_tag_display_string(tags):
    """
    Generate display string for room tags to show in room title.
    Applies color codes from tag definitions.
    
    Args:
        tags (list): List of tag names
        
    Returns:
        str: Formatted tag display with colors (e.g., "|#ff0000[FIRE]|n [TAG]")
    """
    if not tags:
        return ""
    
    display_parts = []
    for tag in tags:
        tag_upper = tag.upper()
        if tag_upper in ALL_TAGS:
            tag_data = ALL_TAGS[tag_upper]
            color = tag_data.get("color", "")
            
            if color:
                # Colored tag: |#ff0000[FIRE]|n
                display_parts.append(f"{color}[{tag_upper}]|n")
            else:
                # Plain tag: [TAG]
                display_parts.append(f"[{tag_upper}]")
    
    return " ".join(display_parts) if display_parts else ""


def has_tag(room, tag_name):
    """
    Check if a room has a specific tag.
    
    Args:
        room: Room object
        tag_name (str): Tag name to check (case-insensitive)
        
    Returns:
        bool: True if room has the tag
    """
    if not hasattr(room, 'tags') or not room.tags:
        return False
    tag_upper = tag_name.upper()
    return any(t.upper() == tag_upper for t in room.tags)


def add_tag(room, tag_name):
    """
    Add a tag to a room.
    
    Args:
        room: Room object
        tag_name (str): Tag name to add (case-insensitive)
        
    Returns:
        bool: True if added, False if already exists or invalid
    """
    tag_upper = tag_name.upper()
    if tag_upper not in VALID_TAG_NAMES:
        return False
    
    if not hasattr(room, 'tags'):
        room.tags = []
    
    if not has_tag(room, tag_name):
        room.tags = room.tags + [tag_upper]
        return True
    return False


def remove_tag(room, tag_name):
    """
    Remove a tag from a room.
    
    Args:
        room: Room object
        tag_name (str): Tag name to remove (case-insensitive)
        
    Returns:
        bool: True if removed, False if not found
    """
    tag_upper = tag_name.upper()
    if not hasattr(room, 'tags') or not room.tags:
        return False
    
    if has_tag(room, tag_name):
        room.tags = [t for t in room.tags if t.upper() != tag_upper]
        return True
    return False


def set_tags(room, tag_list):
    """
    Set room tags, replacing existing ones.
    
    Args:
        room: Room object
        tag_list (list): List of tag names
        
    Returns:
        tuple: (success: bool, message: str, applied_tags: list)
    """
    valid_tags = []
    invalid_tags = []
    
    for tag in tag_list:
        tag_upper = tag.upper().strip()
        if tag_upper in VALID_TAG_NAMES:
            valid_tags.append(tag_upper)
        else:
            invalid_tags.append(tag)
    
    room.tags = valid_tags
    
    msg = f"Room tags set: {', '.join(valid_tags) if valid_tags else 'none'}"
    if invalid_tags:
        msg += f"\nInvalid tags ignored: {', '.join(invalid_tags)}"
    
    return (True, msg, valid_tags)


def get_room_skill_bonuses(room):
    """
    Get all skill bonuses from room tags.
    
    Args:
        room: Room object
        
    Returns:
        dict: {skill_name: bonus_value}
    """
    bonuses = {}
    if not hasattr(room, 'tags') or not room.tags:
        return bonuses
    
    for tag in room.tags:
        if tag in ALL_TAGS and "skill_bonuses" in ALL_TAGS[tag]:
            tag_bonuses = ALL_TAGS[tag]["skill_bonuses"]
            for skill, bonus in tag_bonuses.items():
                bonuses[skill] = bonuses.get(skill, 0) + bonus
    
    return bonuses
