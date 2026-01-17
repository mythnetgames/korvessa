"""
Short Description (Sdesc) System

Sdescs replace traditional display names with descriptive phrases like
"a tall man" or "a scarred elven woman". This creates more immersive
roleplay as characters are seen by their appearance rather than names.

Features:
- Sdescs: Short descriptions that replace character names in room displays
- Recog: Per-character naming system ("I know that tall man as Tom")
- Object references with * syntax
- Character references with / syntax
- Skintone-colored display names
- Disguise integration: Sdescs can be masked by disguises

Example:
    > look
    Tavern
    A tall man is standing by the bar.
    
    > emote looks at /tall and picks up *sword
    Griatch looks at a tall man and picks up a steel sword.
    
    > name tall = Tom
    You will now know 'a tall man' as 'Tom'.
    
    > emote looks at /tom
    Griatch looks at Tom.
"""

import re
from evennia.utils.utils import inherits_from


# Regex for parsing character targets like /tall or /tom
# Matches /word or /word's
CHARACTER_TARGET_REGEX = re.compile(r'/(\w+)(?:\'s)?')

# Regex for parsing object targets like *sword or *sword's
OBJECT_TARGET_REGEX = re.compile(r'\*(\w+)(?:\'s)?')

# Regex for parsing language-prefixed speech like dwarven"Hello"
LANGUAGE_SPEECH_REGEX = re.compile(r'(\w+)"([^"]*)"')

# Object highlight color (bright blue)
OBJECT_COLOR = "|#0087ff"


def get_skintone_color(character):
    """
    Get the skintone color code for a character.
    
    Args:
        character: The character to get skintone for
        
    Returns:
        str: Color code like "|555" or empty string if no skintone set
    """
    if not hasattr(character, 'db'):
        return ""
    
    skintone = getattr(character.db, 'skintone', None)
    if not skintone:
        return ""
    
    from world.combat.constants import SKINTONE_PALETTE
    return SKINTONE_PALETTE.get(skintone, "")


def colorize_name(name, character):
    """
    Apply skintone color to a character's displayed name.
    
    Args:
        name: The name/sdesc to colorize
        character: The character (for skintone lookup)
        
    Returns:
        str: Colorized name or plain name if no skintone
    """
    color = get_skintone_color(character)
    if color:
        return f"{color}{name}|n"
    return name


def colorize_object(name):
    """
    Apply object color to an object's name.
    
    Args:
        name: The object name to colorize
        
    Returns:
        str: Colorized object name in blue
    """
    return f"{OBJECT_COLOR}{name}|n"


def get_sdesc(character, viewer=None, colorize=True):
    """
    Get the appropriate short description for a character.
    
    This respects:
    1. Disguises (if disguised, return disguise sdesc)
    2. Recognition (if viewer knows this character, return their name for them)
    3. Default sdesc
    4. Skintone coloring
    
    Args:
        character: The character whose sdesc to get
        viewer: The character viewing (for recog lookup). If None, returns raw sdesc.
        colorize: If True, apply skintone coloring
        
    Returns:
        str: The appropriate sdesc or recognized name (possibly colorized)
    """
    name = None
    
    # Check for disguise first
    if hasattr(character, 'db') and character.db.disguise_active:
        disguise_sdesc = character.db.disguise_sdesc
        if disguise_sdesc:
            # Still check recog for the disguise
            if viewer:
                recog_name = get_recog(viewer, character)
                if recog_name:
                    name = recog_name
                else:
                    name = disguise_sdesc
            else:
                name = disguise_sdesc
    
    if not name:
        # Check if viewer recognizes this character
        if viewer:
            recog_name = get_recog(viewer, character)
            if recog_name:
                name = recog_name
    
    if not name:
        # Return base sdesc
        sdesc = character.db.sdesc if hasattr(character, 'db') else None
        if sdesc:
            name = sdesc
        else:
            # Fallback to key
            name = character.key
    
    # Apply skintone coloring if requested
    if colorize:
        return colorize_name(name, character)
    return name


def get_sdesc_with_pose(character, viewer=None, colorize=True):
    """
    Get sdesc with pose appended if set.
    
    Example: "a tall man is standing by the bar"
    
    Args:
        character: The character
        viewer: The character viewing
        colorize: If True, apply skintone coloring
        
    Returns:
        str: Sdesc with pose, or just sdesc if no pose
    """
    sdesc = get_sdesc(character, viewer, colorize=colorize)
    
    # Check for temp_place first (from tp command), then look_place
    temp_place = character.temp_place if hasattr(character, 'temp_place') else None
    look_place = character.look_place if hasattr(character, 'look_place') else None
    override_place = character.override_place if hasattr(character, 'override_place') else None
    
    pose = override_place or temp_place or look_place
    
    if pose:
        return f"{sdesc} {pose}"
    return sdesc


def set_sdesc(character, sdesc):
    """
    Set a character's short description.
    
    Validates that the sdesc is unique across all characters (PCs and NPCs).
    
    Args:
        character: The character to modify
        sdesc: The new short description (e.g., "a tall man")
        
    Returns:
        tuple: (success: bool, error_message: str or None)
    """
    # Validate format and uniqueness
    is_valid, error = validate_sdesc(sdesc, exclude_character=character)
    if not is_valid:
        return False, error
    
    character.db.sdesc = sdesc
    return True, None


def get_recog(viewer, target):
    """
    Get the name that viewer has assigned to target.
    
    Args:
        viewer: The character who may have named the target
        target: The character being looked up
        
    Returns:
        str or None: The recognized name, or None if not recognized
    """
    if not viewer or not target:
        return None
    
    recog_dict = viewer.db.recog or {}
    target_key = str(target.id)
    
    # Check if target is disguised - use disguise tracking
    if hasattr(target, 'db') and target.db.disguise_active:
        # When disguised, check recog for the disguise identity
        disguise_recog_key = f"disguise_{target.id}"
        return recog_dict.get(disguise_recog_key)
    
    return recog_dict.get(target_key)


def set_recog(viewer, target, name):
    """
    Set the name that viewer knows target by.
    
    Args:
        viewer: The character assigning the name
        target: The character being named
        name: The name to assign (or None to clear)
    """
    if not viewer or not target:
        return
    
    recog_dict = viewer.db.recog or {}
    
    # Check if target is disguised - store under disguise key
    if hasattr(target, 'db') and target.db.disguise_active:
        disguise_recog_key = f"disguise_{target.id}"
        if name:
            recog_dict[disguise_recog_key] = name
        elif disguise_recog_key in recog_dict:
            del recog_dict[disguise_recog_key]
    else:
        target_key = str(target.id)
        if name:
            recog_dict[target_key] = name
        elif target_key in recog_dict:
            del recog_dict[target_key]
    
    viewer.db.recog = recog_dict


def clear_recog(viewer, target):
    """Clear viewer's recognition of target."""
    set_recog(viewer, target, None)


def find_character_by_sdesc(location, search_term, searcher=None):
    """
    Find a character (PC or NPC) in location by partial sdesc match.
    
    Used for parsing emote targets like /tall.
    
    Args:
        location: The room to search in
        search_term: The partial term to match (e.g., "tall")
        searcher: The character doing the search (for recog lookups)
        
    Returns:
        list: Matching characters (may be empty or have multiple matches)
    """
    if not location:
        return []
    
    search_term = search_term.lower()
    matches = []
    
    for obj in location.contents:
        # Match both Characters and NPCs
        is_character = inherits_from(obj, "typeclasses.characters.Character")
        is_npc = inherits_from(obj, "typeclasses.npcs.NPC") if not is_character else False
        
        if not is_character and not is_npc:
            continue
        
        # Get the sdesc as the searcher would see it (without coloring for matching)
        sdesc = get_sdesc(obj, searcher, colorize=False).lower()
        
        # Also check recog name
        recog = get_recog(searcher, obj) if searcher else None
        if recog and search_term in recog.lower():
            matches.append(obj)
            continue
        
        # Check sdesc
        if search_term in sdesc:
            matches.append(obj)
            continue
        
        # Also check the character's key as fallback
        if search_term in obj.key.lower():
            matches.append(obj)
    
    return matches


def find_object_by_name(location, search_term, searcher=None):
    """
    Find an object in location or searcher's inventory by partial name match.
    
    Used for parsing emote targets like *sword.
    
    Args:
        location: The room to search in
        search_term: The partial term to match (e.g., "sword")
        searcher: The character doing the search (also searches their inventory)
        
    Returns:
        list: Matching objects (may be empty or have multiple matches)
    """
    if not location and not searcher:
        return []
    
    search_term = search_term.lower()
    matches = []
    
    # Search objects to check (room contents + searcher inventory)
    objects_to_search = []
    if location:
        objects_to_search.extend(location.contents)
    if searcher:
        objects_to_search.extend(searcher.contents)
    
    for obj in objects_to_search:
        # Skip characters/NPCs - those use / syntax
        if inherits_from(obj, "typeclasses.characters.Character"):
            continue
        try:
            if inherits_from(obj, "typeclasses.npcs.NPC"):
                continue
        except:
            pass
        
        # Check object key
        if search_term in obj.key.lower():
            if obj not in matches:
                matches.append(obj)
            continue
        
        # Check aliases
        if hasattr(obj, 'aliases') and obj.aliases.all():
            for alias in obj.aliases.all():
                if search_term in alias.lower():
                    if obj not in matches:
                        matches.append(obj)
                    break
    
    return matches


def parse_targets_in_string(text, location, speaker):
    """
    Parse /character and *object references in text and replace with placeholders.
    
    Args:
        text: The text containing /target and *object references
        location: The room to search for targets
        speaker: The character speaking/emoting
        
    Returns:
        tuple: (parsed_text, char_targets, obj_targets) where:
               - parsed_text has targets replaced with placeholders
               - char_targets is list of (search_term, matched_char, possessive) tuples
               - obj_targets is list of (search_term, matched_obj, possessive) tuples
    """
    char_targets = []
    obj_targets = []
    
    def replace_character(match):
        search_term = match.group(1)
        full_match = match.group(0)
        possessive = "'s" in full_match
        
        matches = find_character_by_sdesc(location, search_term, speaker)
        
        if not matches:
            # No match found - leave as is
            return full_match
        
        target = matches[0]  # Use first match
        char_targets.append((search_term, target, possessive))
        
        # Replace with placeholder
        idx = len(char_targets) - 1
        if possessive:
            return f"{{char_{idx}}}'s"
        return f"{{char_{idx}}}"
    
    def replace_object(match):
        search_term = match.group(1)
        full_match = match.group(0)
        possessive = "'s" in full_match
        
        matches = find_object_by_name(location, search_term, speaker)
        
        if not matches:
            # No match found - leave as is
            return full_match
        
        target = matches[0]  # Use first match
        obj_targets.append((search_term, target, possessive))
        
        # Replace with placeholder
        idx = len(obj_targets) - 1
        if possessive:
            return f"{{obj_{idx}}}'s"
        return f"{{obj_{idx}}}"
    
    # Parse character targets first, then objects
    parsed = CHARACTER_TARGET_REGEX.sub(replace_character, text)
    parsed = OBJECT_TARGET_REGEX.sub(replace_object, parsed)
    
    return parsed, char_targets, obj_targets


def personalize_text(text, char_targets, obj_targets, viewer, speaker=None):
    """
    Replace target placeholders with viewer-appropriate names.
    
    Args:
        text: Text with {char_N} and {obj_N} placeholders
        char_targets: List of (search_term, character, possessive) tuples
        obj_targets: List of (search_term, object, possessive) tuples
        viewer: The character viewing this text
        speaker: The character who spoke/emoted (optional)
        
    Returns:
        str: Text with placeholders replaced appropriately for viewer
    """
    result = text
    
    # Replace character placeholders
    for i, (search_term, target, possessive) in enumerate(char_targets):
        placeholder = f"{{char_{i}}}"
        
        if target == viewer:
            # Viewer is the target - use "you"
            replacement = "you"
        else:
            # Get appropriate name for this viewer (with skintone color)
            replacement = get_sdesc(target, viewer, colorize=True)
        
        result = result.replace(placeholder, replacement)
    
    # Replace object placeholders
    for i, (search_term, target, possessive) in enumerate(obj_targets):
        placeholder = f"{{obj_{i}}}"
        
        # Objects are always shown with blue color
        replacement = colorize_object(target.key)
        
        result = result.replace(placeholder, replacement)
    
    return result


def parse_language_speech(text):
    """
    Parse language-prefixed speech in text.
    
    Format: language"speech"
    Example: dwarven"Hello there!"
    
    If no language prefix found, returns (None, original_text).
    
    Args:
        text: Text potentially containing language-prefixed speech
        
    Returns:
        tuple: (language_key or None, speech_text)
    """
    match = LANGUAGE_SPEECH_REGEX.match(text.strip())
    if match:
        language = match.group(1).lower()
        speech = match.group(2)
        return (language, speech)
    return (None, text)


def format_sdesc_for_room(character, viewer=None):
    """
    Format a character's sdesc for room description display.
    
    Capitalizes first letter and appends pose. Uses skintone coloring.
    
    Args:
        character: The character to format
        viewer: Who is viewing
        
    Returns:
        str: Formatted string like "A tall man is standing by the bar."
    """
    # Get sdesc with pose (already colorized)
    text = get_sdesc_with_pose(character, viewer, colorize=True)
    
    # Capitalize first letter (handle color codes)
    if text:
        # Find the first actual letter after any color codes
        # Color codes are like |555 or |#0087ff
        i = 0
        while i < len(text):
            if text[i] == '|':
                # Skip color code
                if i + 1 < len(text) and text[i + 1] == '#':
                    # Hex color: |#RRGGBB (8 chars total)
                    i += 8
                elif i + 1 < len(text) and text[i + 1] == 'n':
                    # Reset code: |n
                    i += 2
                else:
                    # 3-digit color: |RGB (4 chars total)
                    i += 4
            else:
                # Found first real character, capitalize it
                text = text[:i] + text[i].upper() + text[i+1:]
                break
    
    # Add period if no punctuation
    if text and text[-1] not in '.!?':
        text += "."
    
    return text


def get_display_name(character, viewer=None, capitalize=False, colorize=True):
    """
    Get the display name for a character, respecting sdesc/recog.
    
    This is the primary function to use when displaying character names.
    
    Args:
        character: The character to display
        viewer: Who is viewing (for recog/disguise)
        capitalize: Whether to capitalize the first letter
        colorize: Whether to apply skintone coloring
        
    Returns:
        str: The appropriate name to display
    """
    name = get_sdesc(character, viewer, colorize=colorize)
    
    if capitalize and name:
        # Handle color codes when capitalizing
        i = 0
        while i < len(name):
            if name[i] == '|':
                if i + 1 < len(name) and name[i + 1] == '#':
                    i += 8
                elif i + 1 < len(name) and name[i + 1] == 'n':
                    i += 2
                else:
                    i += 4
            else:
                name = name[:i] + name[i].upper() + name[i+1:]
                break
    
    return name


def check_sdesc_uniqueness(sdesc, exclude_character=None):
    """
    Check if an sdesc already exists for another character.
    
    Args:
        sdesc: The sdesc to check
        exclude_character: Character to exclude from the check (e.g., when updating a character's own sdesc)
        
    Returns:
        tuple: (is_unique, existing_character or None)
    """
    from evennia.objects.models import ObjectDB
    from evennia.utils.utils import inherits_from
    
    if not sdesc:
        return True, None
    
    sdesc_lower = sdesc.lower().strip()
    
    # Search all characters (both typeclass) for matching sdescs
    try:
        from typeclasses.characters import Character
        from typeclasses.npcs import NPC
    except ImportError:
        return True, None
    
    # Check all objects that might have sdescs
    for obj in ObjectDB.objects.all():
        # Skip the character we're updating
        if exclude_character and obj.id == exclude_character.id:
            continue
        
        # Check if it's a character or NPC with an sdesc
        if not hasattr(obj, 'db') or not hasattr(obj.db, 'sdesc'):
            continue
        
        existing_sdesc = obj.db.sdesc
        if not existing_sdesc:
            continue
        
        # Case-insensitive comparison
        if existing_sdesc.lower().strip() == sdesc_lower:
            return False, obj
    
    return True, None


def validate_sdesc(sdesc, exclude_character=None):
    """
    Validate an sdesc for proper format and uniqueness.
    
    Sdescs should:
    - Be 3-80 characters
    - Not contain special characters except basic punctuation
    - Not contain newlines
    - Be unique (not already used by another character)
    
    Args:
        sdesc: The sdesc to validate
        exclude_character: Character to exclude from uniqueness check
        
    Returns:
        tuple: (is_valid, error_message or None)
    """
    if not sdesc:
        return False, "Sdesc cannot be empty."
    
    sdesc = sdesc.strip()
    
    if len(sdesc) < 3:
        return False, "Sdesc must be at least 3 characters."
    
    if len(sdesc) > 80:
        return False, "Sdesc cannot exceed 80 characters."
    
    if '\n' in sdesc or '\r' in sdesc:
        return False, "Sdesc cannot contain newlines."
    
    # Allow letters, numbers, spaces, and basic punctuation
    if not re.match(r'^[\w\s\-\',\.]+$', sdesc):
        return False, "Sdesc can only contain letters, numbers, spaces, and basic punctuation (- ' , .)."
    
    # Check for uniqueness
    is_unique, existing_char = check_sdesc_uniqueness(sdesc, exclude_character)
    if not is_unique:
        if existing_char:
            existing_name = existing_char.key if hasattr(existing_char, 'key') else "someone"
            return False, f"That sdesc is already in use by {existing_name}. Please choose a different one."
        return False, "That sdesc is already in use. Please choose a different one."
    
    return True, None


# Legacy alias for backward compatibility
find_target_by_sdesc = find_character_by_sdesc
