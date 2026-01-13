"""
Character Creation System for Kowloon Walled City RPI

This module handles both first-time character creation and respawn/flash cloning
after death. It uses Evennia's EvMenu system for the interactive interface.

Flow:
1. First Character: Name input → Sex selection → GRIM distribution (300 points)
2. Respawn: Choose from 3 random templates OR flash clone previous character
"""

from evennia import create_object
from evennia.utils.evmenu import EvMenu
from django.conf import settings
import random
import time
import re


def validate_name(name, account=None):
    """
    Validate character name for profanity, uniqueness, and deceased character names.
    Args:
        name (str): Full character name
        account: Optional account to check for deceased character names
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    import re
    profanity_list = ['fuck', 'shit', 'damn', 'bitch', 'ass', 'cunt', 'dick', 'cock', 'pussy']
    name_lower = name.lower()
    for word in profanity_list:
        if word in name_lower:
            return (False, "That name is not allowed.")
    from typeclasses.characters import Character
    if Character.objects.filter(db_key__iexact=name).exists():
        return (False, "That name is already taken.")
    
    # Check against deceased character names (permanent deaths)
    if account:
        deceased_names = account.db.deceased_character_names or []
        # Strip Roman numerals from input name for comparison
        roman_pattern = r'\s+(?:I{1,3}|IV|V|VI{1,3}|IX|X|XI{1,3}|XIV|XV)$'
        base_name = re.sub(roman_pattern, '', name.strip())
        base_name_lower = base_name.lower()
        
        for deceased_name in deceased_names:
            if deceased_name.lower() == base_name_lower:
                return (False, "That name belonged to a character who has permanently died and cannot be reused.")
    
    return (True, None)


def int_to_roman(num):
    """
    Convert an integer to a Roman numeral string.
    
    Args:
        num: Integer to convert (1-3999)
        
    Returns:
        str: Roman numeral representation
    """
    val = [
        1000, 900, 500, 400,
        100, 90, 50, 40,
        10, 9, 5, 4,
        1
    ]
    syms = [
        'M', 'CM', 'D', 'CD',
        'C', 'XC', 'L', 'XL',
        'X', 'IX', 'V', 'IV',
        'I'
    ]
    roman_num = ''
    i = 0
    while num > 0:
        for _ in range(num // val[i]):
            roman_num += syms[i]
            num -= val[i]
        i += 1
    return roman_num


def build_name_from_death_count(old_name, death_count):
    """
    Build a new character name with Roman numeral suffix based on death count.
    
    For flash clones, the name gets a Roman numeral indicating incarnation:
    - death_count=1 → "John Doe II" (first death, second body)
    - death_count=2 → "John Doe III" (second death, third body)
    
    If the old name already has a Roman numeral suffix, it's replaced.
    
    Args:
        old_name: Previous character's name
        death_count: Number of deaths (used for numeral)
        
    Returns:
        str: New name with Roman numeral suffix
    """
    import re
    
    # Roman numeral pattern at end of name
    roman_pattern = r'\s+(M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3}))$'
    
    # Strip any existing Roman numeral from old name
    base_name = re.sub(roman_pattern, '', old_name, flags=re.IGNORECASE).strip()
    
    # death_count represents how many times they've died
    # Incarnation number is death_count + 1 (original body was incarnation 1)
    incarnation = death_count + 1
    
    # Build new name with Roman numeral
    if incarnation >= 2:
        new_name = f"{base_name} {int_to_roman(incarnation)}"
    else:
        new_name = base_name
    
    return new_name


# =============================================================================
# CUSTOM EV MENU CLASS
# =============================================================================

class CharCreateEvMenu(EvMenu):
    """
    Custom EvMenu that suppresses automatic option display.
    
    The character creation menu includes option keys in the node text itself,
    so we don't want EvMenu to auto-display them again.
    """
    
    def options_formatter(self, optionlist):
        """
        Override to suppress automatic option display.
        
        Returns:
            str: Empty string to prevent option display.
        """
        return ""


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def generate_random_template():
    """
    Generate a random character template with 300 GRIM points distributed.
    
    Returns:
        dict: Template with 'grit', 'resonance', 'intellect', 'motorics', 
              'first_name', 'last_name'
    """
    from world.namebank import FIRST_NAMES_MALE, FIRST_NAMES_FEMALE, LAST_NAMES
    
    # Randomly pick gender for name selection and character sex
    sex_choices = ['male', 'female', 'ambiguous']
    sex = random.choice(sex_choices)
    
    # Use gendered names for male/female, random choice for ambiguous
    if sex == 'ambiguous':
        use_male = random.choice([True, False])
    else:
        use_male = (sex == 'male')
    
    first_name = random.choice(FIRST_NAMES_MALE if use_male else FIRST_NAMES_FEMALE)
    last_name = random.choice(LAST_NAMES)
    
    # 8-stat system for Kowloon
    STAT_NAMES = [
        "body", "reflexes", "dexterity", "technique",
        "smarts", "willpower", "edge", "empathy"
    ]
    STAT_MAX = {"empathy": 6, **{k: 10 for k in STAT_NAMES if k != "empathy"}}
    STAT_MIN = 1
    STAT_TOTAL = 68
    points_left = STAT_TOTAL
    stats = {}
    for i, stat in enumerate(STAT_NAMES):
        if i == len(STAT_NAMES) - 1:
            val = points_left
        else:
            max_for_stat = min(STAT_MAX[stat], points_left - (len(STAT_NAMES) - i - 1) * STAT_MIN)
            min_for_stat = STAT_MIN
            val = random.randint(min_for_stat, max_for_stat)
        stats[stat] = val
        points_left -= val
    return {
        'first_name': first_name,
        'last_name': last_name,
        'name': f"{first_name} {last_name}",
        'sex': sex,
        **stats
    }
    
    # Basic profanity filter (expandable)
    profanity_list = ['fuck', 'shit', 'damn', 'bitch', 'ass', 'cunt', 'dick', 'cock', 'pussy']
    name_lower = name.lower()
    for word in profanity_list:
        if word in name_lower:
            return (False, "That name is not allowed.")
    
    # Check uniqueness
    from typeclasses.characters import Character
    if Character.objects.filter(db_key__iexact=name).exists():
        return (False, "That name is already taken.")
    
    return (True, None)


def validate_stat_distribution(stats):
    """
    Validate 8-stat distribution for character creation.
    Args:
        stats (dict): {stat_name: value}
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    STAT_BASE = 5  # All stats start at 5
    STAT_MAX = {k: 12 for k in stats if k != "empathy"}  # Max is 12
    STAT_MIN = 1  # Can still go down to 1
    DISTRIBUTION_POINTS = 12  # Points to distribute above base
    
    for stat, value in stats.items():
        if stat == "empathy":
            continue
        if value < STAT_MIN:
            return (False, f"{stat.capitalize()} must be at least {STAT_MIN}.")
        if value > STAT_MAX[stat]:
            return (False, f"{stat.capitalize()} cannot exceed 12.")
    
    # Calculate total distribution points used (value - base for each stat)
    total_distribution = sum([max(0, v - STAT_BASE) for k, v in stats.items() if k != "empathy"])
    if total_distribution != DISTRIBUTION_POINTS:
        return (False, f"You must distribute exactly {DISTRIBUTION_POINTS} points above the base of 5 (current: {total_distribution}).")
    return (True, None)


def create_character_from_template(account, template, sex="ambiguous"):
    """
    Create a character from a template (for respawn).
    
    Args:
        account: Account object
        template (dict): Template with name and GRIM stats
        sex (str): Biological sex
        
    Returns:
        Character: New character object
    """
    from typeclasses.characters import Character
    
    # Get spawn location
    start_location = get_start_location()
    
    # Create full name
    full_name = f"{template['first_name']} {template['last_name']}"
    
    # Use Evennia's proper character creation method
    char, errors = account.create_character(
        key=full_name,
        location=start_location,
        home=start_location,
        typeclass="typeclasses.characters.Character"
    )
    
    if errors:
        # Handle creation errors
        raise Exception(f"Character creation failed: {errors}")
    
    # Set stats from template (8-stat system)
    char.body = template.get('body', 1)
    char.ref = template.get('reflexes', 1)  # Template uses 'reflexes' for ref
    char.dex = template.get('dexterity', 1)  # Template uses 'dexterity' for dex
    char.tech = template.get('technique', 1)  # Template uses 'technique' for tech
    char.smrt = template.get('smarts', 1)  # Template uses 'smarts' for smrt
    char.will = template.get('willpower', 1)  # Template uses 'willpower' for will
    char.edge = template.get('edge', 1)
    
    # Set sex
    char.sex = sex
    
    # Debug: Verify sex was set correctly
    from evennia.comms.models import ChannelDB
    try:
        splattercast = ChannelDB.objects.get_channel("Splattercast")
        splattercast.msg(f"CHARCREATE_SEX_SET: {char.key} sex set to '{sex}', current value: '{char.sex}', gender property: '{char.gender}'")
    except:
        pass
    
    # Set defaults
    # death_count starts at 1 via AttributeProperty in Character class
    char.db.archived = False
    
    return char


def create_flash_clone(account, old_character):
    """
    Create a flash clone from a dead character.
    Inherits: GRIM stats, longdesc, desc, sex, skintone
    Name: Uses the base name (strips any existing Roman numerals, does NOT add new ones)
    
    Args:
        account: Account object
        old_character: Dead character to clone from
        
    Returns:
        Character: New cloned character
    """
    import re
    from typeclasses.characters import Character
    
    # Get spawn location
    start_location = get_start_location()
    
    # Strip any existing Roman numeral from the name - we never add them
    roman_pattern = r'\s+(M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3}))$'
    base_name = re.sub(roman_pattern, '', old_character.key, flags=re.IGNORECASE).strip()
    new_name = base_name  # Use base name only, NO Roman numerals
    
    # CRITICAL: Remove the old archived character from account.characters
    # This is necessary because MAX_NR_CHARACTERS=1, and we need to replace the old char
    if old_character in account.characters:
        account.characters.remove(old_character)
        try:
            from evennia.comms.models import ChannelDB
            splattercast = ChannelDB.objects.get_channel("Splattercast")
            splattercast.msg(f"FLASH_CLONE: Removed {old_character.key} from {account.key}'s characters")
        except:
            pass
    
    # Use Evennia's proper character creation method
    char, errors = account.create_character(
        key=new_name,
        location=start_location,
        home=start_location,
        typeclass="typeclasses.characters.Character"
    )
    
    if errors:
        # Handle creation errors
        raise Exception(f"Flash clone creation failed: {errors}")
    
    # INHERIT: Stats (8-stat system with fallback defaults)
    char.body = old_character.body if hasattr(old_character, 'body') and old_character.body is not None else 1
    char.ref = old_character.ref if hasattr(old_character, 'ref') and old_character.ref is not None else 1
    char.dex = old_character.dex if hasattr(old_character, 'dex') and old_character.dex is not None else 1
    char.tech = old_character.tech if hasattr(old_character, 'tech') and old_character.tech is not None else 1
    char.smrt = old_character.smrt if hasattr(old_character, 'smrt') and old_character.smrt is not None else 1
    char.will = old_character.will if hasattr(old_character, 'will') and old_character.will is not None else 1
    char.edge = old_character.edge if hasattr(old_character, 'edge') and old_character.edge is not None else 1
    
    # INHERIT: Appearance
    char.db.desc = old_character.db.desc
    if hasattr(old_character, 'nakeds') and old_character.nakeds:
        char.nakeds = dict(old_character.nakeds)  # Copy dictionary
    
    # INHERIT: Biology
    char.sex = old_character.sex
    if hasattr(old_character.db, 'skintone'):
        char.db.skintone = old_character.db.skintone
    
    # Debug: Verify sex was inherited correctly
    from evennia.comms.models import ChannelDB
    try:
        splattercast = ChannelDB.objects.get_channel("Splattercast")
        splattercast.msg(f"FLASH_CLONE_SEX_INHERIT: {char.key} inherited sex '{old_character.sex}' from {old_character.key}, current value: '{char.sex}', gender property: '{char.gender}'")
    except:
        pass
    
    # INHERIT: death_count from old character
    # The old character's death_count was already incremented at death (at_death())
    # The new clone inherits this value to continue the progression
    # Use AttributeProperty directly, not db.death_count
    char.death_count = old_death_count
    
    # Link to previous incarnation
    char.db.previous_clone_dbref = old_character.dbref
    
    # Stack ID (consciousness identifier)
    old_stack_id = getattr(old_character.db, 'stack_id', None)
    if old_stack_id:
        char.db.stack_id = old_stack_id
    else:
        # Create new stack ID if old char didn't have one
        import uuid
        char.db.stack_id = str(uuid.uuid4())
    
    # Reset state
    char.db.archived = False
    char.db.current_sleeve_birth = time.time()
    
    return char


def get_start_location():
    """
    Get the starting location for new characters.
    
    Returns:
        Room: Starting location object
    """
    from evennia import search_object
    
    # Try START_LOCATION from settings
    start_location_id = getattr(settings, 'START_LOCATION', None)
    if start_location_id:
        try:
            start_location = search_object(f"#{start_location_id}")[0]
            return start_location
        except (IndexError, AttributeError):
            pass
    
    # Fallback to Limbo (#2)
    try:
        return search_object("#2")[0]
    except (IndexError, AttributeError):
        # Last resort - just return None and let Evennia handle it
        return None


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def _charcreate_exit_callback(caller, menu):
    """
    Called when the character creation menu exits.
    Only disconnects if character creation was NOT completed.
    """
    # Check if they have any ACTIVE (non-archived) characters
    active_characters = [char for char in caller.characters if not char.db.archived]
    
    if active_characters:
        # They completed creation - just close menu, don't disconnect
        return
    
    # No active characters - they exited without completing
    # Disconnect them so they restart character creation on reconnect
    caller.sessions.all()[0].sessionhandler.disconnect(caller.sessions.all()[0], reason="|ySleeve decantation incomplete. Please reconnect to try again.|n")


def start_character_creation(account, is_respawn=False, old_character=None):
    """
    Start the character creation process.
    
    Args:
        account: Account object
        is_respawn (bool): True if respawning after death, False if first character
        old_character: If respawn, the dead character object
    """
    # Store context in account NDB for menu access
    account.ndb.charcreate_is_respawn = is_respawn
    account.ndb.charcreate_old_character = old_character
    account.ndb.charcreate_data = {}
    
    # Start appropriate menu
    if is_respawn:
        # Respawn menu: show templates + flash clone option
        CharCreateEvMenu(
            account,
            "commands.charcreate",
            startnode="respawn_welcome",
            cmdset_mergetype="Replace",
            cmd_on_exit=_charcreate_exit_callback
        )
    else:
        # First character menu: custom creation
        CharCreateEvMenu(
            account,
            "commands.charcreate",
            startnode="first_char_welcome",
            cmdset_mergetype="Replace",
            cmd_on_exit=_charcreate_exit_callback
        )


# =============================================================================
# RESPAWN MENU NODES
# =============================================================================

def _respawn_process_choice(caller, raw_string, **kwargs):
    """Process user's respawn menu choice and route to appropriate node."""
    choice = raw_string.strip()
    old_char = caller.ndb.charcreate_old_character
    
    if choice == "1":
        return "respawn_confirm_template", {"template_idx": 0}
    elif choice == "2":
        return "respawn_confirm_template", {"template_idx": 1}
    elif choice == "3":
        return "respawn_confirm_template", {"template_idx": 2}
    elif choice == "4" and old_char:
        return "respawn_flash_clone"
    else:
        caller.msg("|rInvalid choice. Please enter a number from the available options.|n")
        # Return None to re-display current node
        return None


def respawn_welcome(caller, raw_string, **kwargs):
    """Respawn menu entry point - combined welcome + options screen."""
    
    # Generate 3 random templates (only on first view)
    if not caller.ndb.charcreate_data.get('templates'):
        templates = [generate_random_template() for _ in range(3)]
        caller.ndb.charcreate_data['templates'] = templates
    else:
        templates = caller.ndb.charcreate_data['templates']
    
    text = """
|r╔════════════════════════════════════════════════════════════════╗
║  CONSCIOUSNESS BACKUP PROTOCOL INITIATED                       ║
║  TERRAGROUP CLONING DIVISION - SLEEVE RESTORATION INITIATED    ║
╚════════════════════════════════════════════════════════════════╝|n

|yYour previous sleeve has been terminated.|n
|yMemory upload successful. Stack integrity: |g98.7%|n

|wPreparing new sleeve for consciousness transfer...|n

|w╔════════════════════════════════════════════════════════════════╗
║  AVAILABLE SLEEVES                                             ║
╚════════════════════════════════════════════════════════════════╝|n

Select a consciousness vessel:

"""
    
    # Display templates
    for i, template in enumerate(templates, 1):
        text += f"\n|w[{i}]|n |c{template['first_name']} {template['last_name']}|n\n"
        text += f"    |gBODY:|n {template.get('body', 5):3d}  "
        text += f"|yREF:|n {template.get('reflexes', 5):3d}  "
        text += f"|bDEX:|n {template.get('dexterity', 5):3d}  "
        text += f"|mTECH:|n {template.get('technique', 5):3d}\n"
        text += f"    |cSMRT:|n {template.get('smarts', 5):3d}  "
        text += f"|wWILL:|n {template.get('willpower', 5):3d}  "
        text += f"|rEDGE:|n {template.get('edge', 5):3d}\n"
    
    # Flash clone option
    old_char = caller.ndb.charcreate_old_character
    if old_char:
        text += f"\n|w[4]|n |rFLASH CLONE|n - |c{old_char.key}|n (preserve current identity)\n"
        text += f"    |gBODY:|n {getattr(old_char, 'body', 5):3d}  "
        text += f"|yREF:|n {getattr(old_char, 'ref', 5):3d}  "
        text += f"|bDEX:|n {getattr(old_char, 'dex', 5):3d}  "
        text += f"|mTECH:|n {getattr(old_char, 'tech', 5):3d}\n"
        text += f"    |cSMRT:|n {getattr(old_char, 'smrt', 5):3d}  "
        text += f"|wWILL:|n {getattr(old_char, 'will', 5):3d}  "
        text += f"|rEDGE:|n {getattr(old_char, 'edge', 5):3d}\n"
        text += f"    |wInherits appearance, stats, and memories from previous incarnation|n\n"
    
    # Build prompt based on available options
    if old_char:
        text += "\n|wEnter choice [1-4]:|n"
    else:
        text += "\n|wEnter choice [1-3]:|n"
    
    # Use only _default to catch all input (prevents EvMenu from displaying option keys)
    # IMPORTANT: Must be a tuple, not a bare dict, or EvMenu will auto-generate numbered options
    # The goto points to a callable that processes the input and routes to the correct node
    options = ({"key": "_default", "goto": _respawn_process_choice},)
    
    return text, options


def respawn_confirm_template(caller, raw_string, template_idx=0, **kwargs):
    """Confirm template selection and choose sex."""
    
    templates = caller.ndb.charcreate_data.get('templates', [])
    if template_idx >= len(templates):
        return "respawn_welcome"
    
    template = templates[template_idx]
    caller.ndb.charcreate_data['selected_template'] = template
    
    text = f"""
|w╔════════════════════════════════════════════════════════════════╗
║  SLEEVE CONFIGURATION                                          ║
╚════════════════════════════════════════════════════════════════╝|n

Selected: |c{template['first_name']} {template['last_name']}|n

|gGrit:|n      {template['grit']:3d}
|yResonance:|n {template['resonance']:3d}
|bIntellect:|n {template['intellect']:3d}
|mMotorics:|n {template['motorics']:3d}

Select biological sex for this sleeve:

|w[1]|n Male
|w[2]|n Female
|w[3]|n Androgynous

|w[B]|n Back to template selection

|wEnter choice:|n """
    
    options = (
        {"key": "1",
         "goto": ("respawn_finalize_template", {"sex": "male"}),
         "auto_help": False,
         "auto_look": False},
        {"key": "2",
         "goto": ("respawn_finalize_template", {"sex": "female"}),
         "auto_help": False,
         "auto_look": False},
        {"key": "3",
         "goto": ("respawn_finalize_template", {"sex": "ambiguous"}),
         "auto_help": False,
         "auto_look": False},
        {"key": ("b", "back"),
         "goto": "respawn_welcome",
         "auto_help": False,
         "auto_look": False},
        {"key": "_default",
         "goto": ("respawn_confirm_template", {"template_idx": template_idx}),
         "auto_help": False,
         "auto_look": False},
    )
    
    return text, options


def respawn_finalize_template(caller, raw_string, **kwargs):
    """Create character from template and finalize respawn."""
    
    # Extract sex from kwargs (EvMenu passes goto dict params as kwargs)
    sex = kwargs.get('sex', 'ambiguous')
    
    template = caller.ndb.charcreate_data.get('selected_template')
    if not template:
        return "respawn_welcome"
    
    # Create character
    try:
        char = create_character_from_template(caller, template, sex)
        
        # Puppet the new character
        caller.puppet_object(caller.sessions.all()[0], char)
        
        # Send welcome message
        char.msg("|g╔════════════════════════════════════════════════════════════════╗")
        char.msg("|g║  CONSCIOUSNESS TRANSFER COMPLETE                               ║")
        char.msg("|g╚════════════════════════════════════════════════════════════════╝|n")
        char.msg("")
        char.msg(f"|wWelcome back, |c{char.key}|w.|n")
        char.msg(f"|wClone Generation:|n |w1|n")
        char.msg("")
        char.msg("|y[SYSTEM]: Vires in Scientia. Scientia est fortis. Et oculus spectans deus nobis.|n")
        char.msg("")
        char.msg("|yYou open your eyes in an unfamiliar body.|n")
        char.msg("|yThe memories feel... borrowed. But they're yours now.|n")
        char.msg("")
        
        # Clean up
        _cleanup_charcreate_ndb(caller)
        
        # Exit menu
        return None
        
    except Exception as e:
        # Error - show message and return to selection
        caller.msg(f"|rError creating character: {e}|n")
        from evennia.comms.models import ChannelDB
        try:
            splattercast = ChannelDB.objects.get_channel("Splattercast")
            splattercast.msg(f"CHARCREATE_ERROR: {e}")
        except:
            pass
        return "respawn_welcome"


def respawn_flash_clone(caller, raw_string, **kwargs):
    """Create flash clone and finalize respawn."""
    
    old_char = caller.ndb.charcreate_old_character
    if not old_char:
        caller.msg("|rError: No previous character found.|n")
        return "respawn_welcome"
    
    # Create flash clone
    try:
        char = create_flash_clone(caller, old_char)
        
        # Puppet the new character
        caller.puppet_object(caller.sessions.all()[0], char)
        
        # Send welcome message
        # Use AttributeProperty to access the correct categorized attribute
        death_count = char.death_count
        char.msg("")
        char.msg(f"|wWelcome back, |c{char.key}|w.|n")
        char.msg(f"|wDeath Count:|n |w{death_count}|n")
        char.msg("")
        
        # Death count-specific flavor
        if death_count == 2:
            char.msg("|wThis is your first death. The sensation of resleeving is disorienting.|n")
            char.msg("|wYour old body's final moments echo in your mind like static on a dead channel.|n")
        elif death_count < 5:
            char.msg("|wThe memories of your previous body fade like analog videotape degradation.|n")
            char.msg("|wYou know you've done this before, but each time feels like the first.|n")
        elif death_count < 10:
            char.msg("|wYou've died enough times to know: this never gets easier.|n")
            char.msg("|wBut at least you're still you. Mostly.|n")
        else:
            char.msg("|rHow many times have you done this? The memories blur together like overexposed film.|n")
            char.msg("|rAre you still the person who first stepped into this world?|n")
        
        char.msg("")
        char.msg(f"|wPrevious cause of death:|n |r{old_char.db.death_cause or 'Unknown'}|n")
        char.msg("")
        char.msg("|y[SYSTEM]: Vires in Scientia. Scientia est fortis. Et oculus spectans deus nobis.|n")
        char.msg("")
        
        # Clean up
        _cleanup_charcreate_ndb(caller)
        
        # Exit menu
        return None
        
    except Exception as e:
        # Error - show message and return to selection
        caller.msg(f"|rError creating flash clone: {e}|n")
        from evennia.comms.models import ChannelDB
        try:
            splattercast = ChannelDB.objects.get_channel("Splattercast")
            splattercast.msg(f"FLASH_CLONE_ERROR: {e}")
        except:
            pass
        return "respawn_welcome"


# =============================================================================
# FIRST CHARACTER MENU NODES
# =============================================================================

def first_char_welcome(caller, raw_string, **kwargs):
    """First character creation entry point."""
    
    text = """
|bWelcome to |#d70000KOWLOON|w:                      
         |#ffff00THE WALLED CITY|n

|wAfter years of isolation, the Walled City has reopened to outsiders.|n

|wThe year is 197?.|n
|wYou arrive at South Gate... but let's get some things cleared up first.|n

Press |w<Enter>|n to begin character creation.
"""
    
    options = (
        {"key": "_default",
         "goto": "first_char_name_first"},
    )
    
    return text, options


def first_char_name_first(caller, raw_string, **kwargs):
    """Get first name."""
    
    # If input provided, validate it
    if raw_string and raw_string.strip():
        name = raw_string.strip()
        
        # Validate format (not uniqueness yet - need full name)
        if len(name) < 2 or len(name) > 30:
            caller.msg(f"|rInvalid name: Name must be 2-30 characters.|n")
            # Return None to re-display current node
            return None
        
        if not re.match(r"^[a-zA-Z][a-zA-Z\-']*[a-zA-Z]$", name):
            caller.msg(f"|rInvalid name: Only letters, hyphens, and apostrophes allowed.|n")
            # Return None to re-display current node
            return None
        
        """
        Kowloon Walled City Character Creation System

        Handles first-time character creation and respawn/clone after death.
        Uses Evennia's EvMenu for interactive menus.

        Flow:
        1. First Character: Name input → Sex selection → Stat assignment (68 points, 8 stats)
        2. Respawn: Choose from 3 random templates OR flash clone previous character
        """
        # Store first name and advance to next node
        caller.ndb.charcreate_data['first_name'] = name
        # Call next node directly and return its result
        return first_char_name_last(caller, "", **kwargs)
    
    # Display prompt (first time or after error)
    text = """
|wWhat is your FIRST name?|n

(2-30 characters, letters only)

|w>|n """
    
    options = (
        {"key": "_default",
         "goto": "first_char_name_first"},
    )
    
    return text, options


def first_char_name_last(caller, raw_string, **kwargs):
    """Get last name."""
    
    first_name = caller.ndb.charcreate_data.get('first_name', '')
    
    # If input provided, validate it
    if raw_string and raw_string.strip():
        name = raw_string.strip()
        
        if len(name) < 2 or len(name) > 30:
            caller.msg(f"|rInvalid name: Name must be 2-30 characters.|n")
            # Return None to re-display current node
            return None
        
        if not re.match(r"^[a-zA-Z][a-zA-Z\-']*[a-zA-Z]$", name):
            caller.msg(f"|rInvalid name: Only letters, hyphens, and apostrophes allowed.|n")
            # Return None to re-display current node
            return None
        
        # Check full name uniqueness
        full_name = f"{first_name} {name}"
        is_valid, error = validate_name(full_name, account=caller)
        if not is_valid:
            caller.msg(f"|r{error}|n")
            # Return None to re-display current node
            return None
        
        # Store last name and advance to next node
        caller.ndb.charcreate_data['last_name'] = name
        # Call next node directly and return its result
        return first_char_sex(caller, "", **kwargs)
    
    # Display prompt (first time or after error)
    text = f"""
First name: |c{first_name}|n

|wWhat is your LAST name?|n

(2-30 characters, letters only)

|w>|n """
    
    options = (
        {"key": "_default",
         "goto": "first_char_name_last"},
    )
    
    return text, options


def first_char_sex(caller, raw_string, **kwargs):
    """Select biological sex."""
    first_name = caller.ndb.charcreate_data.get('first_name', '')
    last_name = caller.ndb.charcreate_data.get('last_name', '')
    text = f"""
Name: |c{first_name} {last_name}|n

Select biological sex:

|w[1]|n Male
|w[2]|n Female
|w[3]|n Androgynous

|wEnter choice:|n """
    options = (
        {"key": "1",
         "goto": ("first_char_stat_assign", {"sex": "male"}),
         "auto_help": False,
         "auto_look": False},
        {"key": "2",
         "goto": ("first_char_stat_assign", {"sex": "female"}),
         "auto_help": False,
         "auto_look": False},
        {"key": "3",
         "goto": ("first_char_stat_assign", {"sex": "ambiguous"}),
         "auto_help": False,
         "auto_look": False},
        {"key": "_default",
         "goto": "first_char_sex",
         "auto_help": False,
         "auto_look": False},
    )
    return text, options


def first_char_stat_assign(caller, raw_string, **kwargs):
    """Distribute 12 points among 7 assignable stats above base of 5 (empathy is auto-calculated)."""
    if 'sex' in kwargs:
        caller.ndb.charcreate_data['sex'] = kwargs['sex']
    first_name = caller.ndb.charcreate_data.get('first_name', '')
    last_name = caller.ndb.charcreate_data.get('last_name', '')
    sex = caller.ndb.charcreate_data.get('sex', 'ambiguous')
    stats = caller.ndb.charcreate_data.get('stats', {
        'body': 5,
        'reflexes': 5,
        'dexterity': 5,
        'technique': 5,
        'smarts': 5,
        'willpower': 5,
        'edge': 5
    })
    empathy = stats['edge'] + stats['willpower']
    # Calculate distribution points used (total stats minus baseline of 7*5)
    # This counts points below base as freed-up allotment
    STAT_BASE = 5
    total_stats = sum([v for k, v in stats.items() if k != 'empathy'])
    distribution_used = total_stats - (STAT_BASE * 7)
    remaining = 12 - distribution_used
    text = f"""
Let's assign your character's stats.

Name: |c{first_name} {last_name}|n
Sex: |c{sex.capitalize()}|n

|wAll stats start at 5. Distribute |y12 points|w among them (max 12).|n
    |wBody|n (1-12):        {stats['body']}
    |wReflexes|n (1-12):    {stats['reflexes']}
    |wDexterity|n (1-12):   {stats['dexterity']}
    |wTechnique|n (1-12):   {stats['technique']}
    |wSmarts|n (1-12):      {stats['smarts']}
    |wWillpower|n (1-12):   {stats['willpower']}
    |wEdge|n (1-12):        {stats['edge']}
    |wEmpathy|n (auto):     {empathy} (calculated: edge + willpower)

|wDistribution points used:|n {distribution_used}/12  {'REMAINING: ' + str(remaining) if remaining >= 0 else '|rOVER BY:|n ' + str(abs(remaining))}

Commands:
    |w<stat> <value>|n  - Set a stat (e.g., 'body 8')
    |wreset|n           - Reset all stats to 5
    |wdone|n            - Finalize character (when 12 points distributed)

|w>|n """
    options = (
        {"key": "_default", "goto": "first_char_stat_assign"},
    )
    if raw_string and raw_string.strip():
        args = raw_string.strip().lower().split()
        if not args:
            return text, options
        command = args[0]
        valid_stats = ['body', 'reflexes', 'dexterity', 'technique', 'smarts', 'willpower', 'edge']
        if command == 'reset':
            stats = {k: 5 for k in valid_stats}
            caller.ndb.charcreate_data['stats'] = stats
            # Immediately update display after reset
            empathy = stats['edge'] + stats['willpower']
            STAT_BASE = 5
            total_stats = sum([v for k, v in stats.items() if k != 'empathy'])
            distribution_used = total_stats - (STAT_BASE * 7)
            remaining = 12 - distribution_used
            text = f"""
Let's assign your character's stats.

Name: |c{first_name} {last_name}|n
Sex: |c{sex.capitalize()}|n

|wAll stats start at 5. Distribute |y12 points|w among them (max 12).|n
    |wBody|n (1-12):        {stats['body']}
    |wReflexes|n (1-12):    {stats['reflexes']}
    |wDexterity|n (1-12):   {stats['dexterity']}
    |wTechnique|n (1-12):   {stats['technique']}
    |wSmarts|n (1-12):      {stats['smarts']}
    |wWillpower|n (1-12):   {stats['willpower']}
    |wEdge|n (1-12):        {stats['edge']}
    |wEmpathy|n (auto):     {empathy} (calculated: edge + willpower)

|wDistribution points used:|n {distribution_used}/12  {'REMAINING: ' + str(remaining) if remaining >= 0 else '|rOVER BY:|n ' + str(abs(remaining))}

Commands:
    |w<stat> <value>|n  - Set a stat (e.g., 'body 8')
    |wreset|n           - Reset all stats to 5
    |wdone|n            - Finalize character (when 12 points distributed)

|w>|n """
            return text, options
        if command in ['done', 'finish', 'finalize']:
            is_valid, error = validate_stat_distribution(stats)
            if not is_valid:
                caller.msg(f"|r{error}|n")
                return text, options
            return first_char_confirm(caller, "", **kwargs)
        if command in valid_stats:
            if len(args) < 2:
                caller.msg("|rUsage: <stat> <value>  (e.g., 'body 10')|n")
                return text, options
            try:
                value = int(args[1])
            except ValueError:
                caller.msg("|rValue must be a number.|n")
                return text, options
            if value < 1 or value > 12:
                caller.msg("|rValue must be 1-12.|n")
                return text, options
            stats[command] = value
            caller.ndb.charcreate_data['stats'] = stats
            # Immediately update display after stat set
            empathy = stats['edge'] + stats['willpower']
            STAT_BASE = 5
            total_stats = sum([v for k, v in stats.items() if k != 'empathy'])
            distribution_used = total_stats - (STAT_BASE * 7)
            remaining = 12 - distribution_used
            text = f"""
Let's assign your character's stats.

Name: |c{first_name} {last_name}|n
Sex: |c{sex.capitalize()}|n

|wAll stats start at 5. Distribute |y12 points|w among them (max 12).|n
    |wBody|n (1-12):        {stats['body']}
    |wReflexes|n (1-12):    {stats['reflexes']}
    |wDexterity|n (1-12):   {stats['dexterity']}
    |wTechnique|n (1-12):   {stats['technique']}
    |wSmarts|n (1-12):      {stats['smarts']}
    |wWillpower|n (1-12):   {stats['willpower']}
    |wEdge|n (1-12):        {stats['edge']}
    |wEmpathy|n (auto):     {empathy} (calculated: edge + willpower)

|wDistribution points used:|n {distribution_used}/12  {'REMAINING: ' + str(remaining) if remaining >= 0 else '|rOVER BY:|n ' + str(abs(remaining))}

Commands:
    |w<stat> <value>|n  - Set a stat (e.g., 'body 8')
    |wreset|n           - Reset all stats to 5
    |wdone|n            - Finalize character (when 12 points distributed)

|w>|n """
            return text, options
    return text, options


def first_char_confirm(caller, raw_string, **kwargs):
    """Final confirmation and character creation."""
    first_name = caller.ndb.charcreate_data.get('first_name', '')
    last_name = caller.ndb.charcreate_data.get('last_name', '')
    sex = caller.ndb.charcreate_data.get('sex', 'ambiguous')
    stats = caller.ndb.charcreate_data.get('stats', {
        'body': 5,
        'reflexes': 5,
        'dexterity': 5,
        'technique': 5,
        'smarts': 5,
        'willpower': 5,
        'edge': 5
    })
    empathy = stats['edge'] + stats['willpower']
    STAT_BASE = 5
    # Distribution = total all stats minus the baseline (7 stats * 5 base)
    total_stats = sum([v for k, v in stats.items() if k != 'empathy'])
    distribution_used = total_stats - (STAT_BASE * 7)
    text = f"""
Just uh, let me know if everything looks good.

|wName:|n |c{first_name} {last_name}|n
|wSex:|n |c{sex.capitalize()}|n

|wStats:|n
    |wBody:|n      {stats['body']}
    |wReflexes:|n  {stats['reflexes']}
    |wDexterity:|n {stats['dexterity']}
    |wTechnique:|n {stats['technique']}
    |wSmarts:|n    {stats['smarts']}
    |wWillpower:|n {stats['willpower']}
    |wEdge:|n      {stats['edge']}
    |wEmpathy:|n   {empathy} (calculated: edge + willpower)

|wDistribution points used:|n {distribution_used}/12

|yOnce created, your name cannot be changed.|n
|yStats can be modified through gameplay.|n

Create this character?

|w[Y]|n Yes, finalize character
|w[N]|n No, go back to stat assignment

|w>|n """
    options = (
        {"key": ("y", "yes"),
         "goto": "first_char_select_language",
         "auto_help": False,
         "auto_look": False},
        {"key": ("n", "no"),
         "goto": "first_char_stat_assign",
         "auto_help": False,
         "auto_look": False},
        {"key": "_default",
         "goto": "first_char_confirm",
         "auto_help": False,
         "auto_look": False},
    )
    return text, options


def first_char_select_language(caller, raw_string, **kwargs):
    """Select primary language during character creation."""
    from world.language.constants import (
        LANGUAGES, SMARTS_THRESHOLD_FOR_SECOND_LANGUAGE
    )
    
    stats = caller.ndb.charcreate_data.get('stats', {})
    smarts = stats.get('smarts', 1)
    primary_language = caller.ndb.charcreate_data.get('primary_language', 'cantonese')
    secondary_languages = caller.ndb.charcreate_data.get('secondary_languages', [])
    
    # Determine if player can choose a second language
    can_choose_second = smarts >= SMARTS_THRESHOLD_FOR_SECOND_LANGUAGE
    
    text = f"""
|wChoose Your Primary Language|n

Your character will speak this language by default.

|wSmarts:|n {smarts} {'(You may also choose a second language!)' if can_choose_second else ''}

|wAvailable Languages:|n
"""
    
    # List all languages with their descriptions
    lang_list = []
    for i, (code, info) in enumerate(sorted(LANGUAGES.items()), 1):
        lang_list.append(f"|w[{i}]|n |c{info['name']}|n - {info['description']}")
        if code == primary_language:
            lang_list[-1] += " |y(selected)|n"
    
    text += "\n".join(lang_list)
    
    # Handle input
    options = (
        {"key": "_default", "goto": "first_char_select_language"},
    )
    
    if raw_string and raw_string.strip():
        args = raw_string.strip().lower().split()
        if not args:
            return text, options
        
        command = args[0]
        lang_codes = sorted(list(LANGUAGES.keys()))
        
        # Handle language selection
        if command == 'done':
            # Move to second language selection if eligible
            if can_choose_second:
                return first_char_select_second_language(caller, "", **kwargs)
            else:
                # Skip to finalize
                return first_char_finalize(caller, "", **kwargs)
        
        # Try to parse as a number (1-indexed)
        try:
            lang_index = int(command) - 1
            if 0 <= lang_index < len(lang_codes):
                selected_code = lang_codes[lang_index]
                caller.ndb.charcreate_data['primary_language'] = selected_code
                caller.msg(f"|gPrimary language set to |c{LANGUAGES[selected_code]['name']}|g.|n")
                
                # Show updated text
                primary_language = selected_code
                text = f"""
|wChoose Your Primary Language|n

Your character will speak this language by default.

|wSmarts:|n {smarts} {'(You may also choose a second language!)' if can_choose_second else ''}

|wAvailable Languages:|n
"""
                lang_list = []
                for i, (code, info) in enumerate(sorted(LANGUAGES.items()), 1):
                    lang_list.append(f"|w[{i}]|n |c{info['name']}|n - {info['description']}")
                    if code == primary_language:
                        lang_list[-1] += " |y(selected)|n"
                
                text += "\n".join(lang_list)
                text += f"\n\n|wPrimary Language:|n |c{LANGUAGES[primary_language]['name']}|n"
                if can_choose_second:
                    text += f"\n\nType |wdone|n when ready to choose your second language, or select another language above."
                else:
                    text += f"\n\nType |wdone|n when ready to create your character."
                text += "\n\n|w>|n"
                return text, options
        except ValueError:
            pass
        
        caller.msg("|rInvalid selection. Please enter a number or 'done'.|n")
    
    if primary_language:
        text += f"\n\n|wPrimary Language:|n |c{LANGUAGES[primary_language]['name']}|n"
    
    if can_choose_second:
        text += f"\n\nType |wdone|n when ready to choose your second language, or select another language above."
    else:
        text += f"\n\nType |wdone|n when ready to create your character."
    
    text += "\n\n|w>|n"
    return text, options


def first_char_select_second_language(caller, raw_string, **kwargs):
    """Select secondary language if Smarts > 7."""
    from world.language.constants import LANGUAGES
    
    stats = caller.ndb.charcreate_data.get('stats', {})
    smarts = stats.get('smarts', 1)
    primary_language = caller.ndb.charcreate_data.get('primary_language', 'cantonese')
    secondary_languages = caller.ndb.charcreate_data.get('secondary_languages', [])
    
    text = f"""
|wChoose Your Secondary Language|n

Your Smarts of {smarts} allows you to learn a second language!

|wAvailable Languages:|n
"""
    
    # List all languages except primary
    lang_list = []
    lang_codes = sorted([code for code in LANGUAGES.keys() if code != primary_language])
    for i, code in enumerate(lang_codes, 1):
        info = LANGUAGES[code]
        lang_list.append(f"|w[{i}]|n |c{info['name']}|n - {info['description']}")
        if code in secondary_languages:
            lang_list[-1] += " |y(selected)|n"
    
    text += "\n".join(lang_list)
    
    # Handle input
    options = (
        {"key": "_default", "goto": "first_char_select_second_language"},
    )
    
    if raw_string and raw_string.strip():
        args = raw_string.strip().lower().split()
        if not args:
            return text, options
        
        command = args[0]
        lang_codes = sorted([code for code in LANGUAGES.keys() if code != primary_language])
        
        # Handle language selection
        if command == 'done':
            # Proceed to finalize
            return first_char_finalize(caller, "", **kwargs)
        
        if command == 'skip':
            # Skip second language
            caller.msg("|ySkipping second language selection.|n")
            return first_char_finalize(caller, "", **kwargs)
        
        # Try to parse as a number (1-indexed)
        try:
            lang_index = int(command) - 1
            if 0 <= lang_index < len(lang_codes):
                selected_code = lang_codes[lang_index]
                caller.ndb.charcreate_data['secondary_languages'] = [selected_code]
                caller.msg(f"|gSecondary language set to |c{LANGUAGES[selected_code]['name']}|g.|n")
                
                # Show updated text
                text = f"""
|wChoose Your Secondary Language|n

Your Smarts of {smarts} allows you to learn a second language!

|wAvailable Languages:|n
"""
                lang_list = []
                for i, code in enumerate(lang_codes, 1):
                    info = LANGUAGES[code]
                    lang_list.append(f"|w[{i}]|n |c{info['name']}|n - {info['description']}")
                    if code == selected_code:
                        lang_list[-1] += " |y(selected)|n"
                
                text += "\n".join(lang_list)
                text += f"\n\n|wSecondary Language:|n |c{LANGUAGES[selected_code]['name']}|n"
                text += f"\n\nType |wdone|n to create your character, or select another language."
                text += "\n\n|w>|n"
                return text, options
        except ValueError:
            pass
        
        caller.msg("|rInvalid selection. Please enter a number, 'done', or 'skip'.|n")
    
    text += f"\n\n|wPrimary Language:|n |c{LANGUAGES[primary_language]['name']}|n"
    text += f"\n\nType |wdone|n to create your character, |wskip|n to choose no second language, or select a language above."
    text += "\n\n|w>|n"
    return text, options


def first_char_finalize(caller, raw_string, **kwargs):
    """Create the character and enter game."""
    from typeclasses.characters import Character
    first_name = caller.ndb.charcreate_data.get('first_name', '')
    last_name = caller.ndb.charcreate_data.get('last_name', '')
    full_name = f"{first_name} {last_name}"
    sex = caller.ndb.charcreate_data.get('sex', 'ambiguous')
    stats = caller.ndb.charcreate_data.get('stats', {
        'body': 5,
        'reflexes': 5,
        'dexterity': 5,
        'technique': 5,
        'smarts': 5,
        'willpower': 5,
        'edge': 5
    })
    empathy = stats['edge'] + stats['willpower']
    start_location = get_start_location()
    try:
        char, errors = caller.create_character(
            key=full_name,
            location=start_location,
            home=start_location,
            typeclass="typeclasses.characters.Character"
        )
        if errors:
            raise Exception(f"Character creation failed: {errors}")
        char.body = stats['body']
        char.ref = stats['reflexes']
        char.dex = stats['dexterity']
        char.tech = stats['technique']
        char.smrt = stats['smarts']
        char.will = stats['willpower']
        char.edge = stats['edge']
        char.emp = empathy
        char.sex = sex
        char.db.archived = False
        
        # Award starting IP
        char.db.ip = char.db.ip if hasattr(char.db, 'ip') and char.db.ip else 0
        char.db.ip += 200
        
        import uuid
        char.db.stack_id = str(uuid.uuid4())
        char.db.original_creation = time.time()
        char.db.current_sleeve_birth = time.time()
        caller.puppet_object(caller.sessions.all()[0], char)
        char.msg("")
        char.msg(f"|wWelcome to Kowloon, |c{char.key}|w.|n")
        char.msg("")
        char.msg("|y[SYSTEM]: Vires in Scientia. Scientia est fortis. Et oculus spectans deus nobis.|n")
        char.msg("")
        char.msg("|wPro tip? Don't trust anyone.|n")
        char.msg("|wJust a little work north, and you're in the City.|n")
        char.msg("")
        char.msg("|g=== Character Creation Complete ===|n")
        char.msg(f"|gYou have been awarded |y200 Investment Points (IP)|g.|n")
        char.msg(f"|cCurrent IP:|n |y{char.db.ip}|n")
        char.msg("")
        char.msg("|yYou can spend IP to improve your skills and abilities.|n")
        char.msg("|yType |whelp ip|y to learn more about the IP system.|n")
        char.msg("")
        char.msg("|c=== Optional: Submit Your Background ===|n")
        char.msg("|ySubmit a character background to receive an additional |w50 IP bonus|y!|n")
        char.msg("|yType |wbackground submit <text>|y to write your character's story.|n")
        char.msg("|yBackgrounds must be approved by staff but can be edited until approval.|n")
        char.msg("")
        char.msg("|yType |wlook|y to examine your surroundings.|n")
        char.msg("|yType |whelp|y for a list of commands.|n")
        char.msg("")
        _cleanup_charcreate_ndb(caller)
        return None
    except Exception as e:
        caller.msg(f"|rError creating character: {e}|n")
        from evennia.comms.models import ChannelDB
        try:
            splattercast = ChannelDB.objects.get_channel("Splattercast")
            splattercast.msg(f"CHARCREATE_ERROR: {e}")
        except:
            pass
        return "first_char_confirm"


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def _cleanup_charcreate_ndb(caller):
    """Clean up character creation NDB data."""
    if hasattr(caller.ndb, 'charcreate_is_respawn'):
        delattr(caller.ndb, 'charcreate_is_respawn')
    if hasattr(caller.ndb, 'charcreate_old_character'):
        delattr(caller.ndb, 'charcreate_old_character')
    if hasattr(caller.ndb, 'charcreate_data'):
        delattr(caller.ndb, 'charcreate_data')
