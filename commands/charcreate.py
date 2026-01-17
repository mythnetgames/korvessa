"""
Character Creation System for Korvessa Fantasy MUD

This module handles both first-time character creation and respawn after death.
It uses Evennia's EvMenu system for the interactive interface.

Flow:
1. First Character: Name input -> Race selection -> Sex selection -> D&D 5e Point Buy -> Language (if Human)
2. Respawn: Choose from 3 random templates OR clone previous character
"""

from evennia import create_object
from evennia.utils.evmenu import EvMenu
from django.conf import settings
import random
import time
import re

# D&D 5e Point Buy Constants
POINT_BUY_TOTAL = 27
POINT_BUY_COSTS = {
    8: 0, 9: 1, 10: 2, 11: 3, 12: 4, 13: 5, 14: 7, 15: 9
}
STAT_MIN = 8
STAT_MAX = 15


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
    Generate a random character template with D&D 5e point buy stats.
    
    Returns:
        dict: Template with stats, first_name, last_name, race
    """
    from world.namebank import FIRST_NAMES_MALE, FIRST_NAMES_FEMALE, LAST_NAMES
    
    # Randomly pick gender for name selection and character sex
    sex_choices = ['male', 'female', 'ambiguous']
    sex = random.choice(sex_choices)
    
    # Randomly pick race
    race_choices = ['human', 'elf', 'dwarf']
    race = random.choice(race_choices)
    
    # Use gendered names for male/female, random choice for ambiguous
    if sex == 'ambiguous':
        use_male = random.choice([True, False])
    else:
        use_male = (sex == 'male')
    
    first_name = random.choice(FIRST_NAMES_MALE if use_male else FIRST_NAMES_FEMALE)
    last_name = random.choice(LAST_NAMES)
    
    # D&D 5e stat system with point buy
    STAT_NAMES = ["str", "dex", "con", "int", "wis", "cha"]
    
    # Generate random valid point buy
    stats = {stat: 8 for stat in STAT_NAMES}
    points_remaining = POINT_BUY_TOTAL
    
    # Randomly distribute points
    while points_remaining > 0:
        stat = random.choice(STAT_NAMES)
        current_val = stats[stat]
        if current_val < STAT_MAX:
            next_val = current_val + 1
            cost_diff = POINT_BUY_COSTS[next_val] - POINT_BUY_COSTS[current_val]
            if cost_diff <= points_remaining:
                stats[stat] = next_val
                points_remaining -= cost_diff
        # Break if we can't raise any stat
        can_raise = False
        for s in STAT_NAMES:
            if stats[s] < STAT_MAX:
                next_v = stats[s] + 1
                if POINT_BUY_COSTS[next_v] - POINT_BUY_COSTS[stats[s]] <= points_remaining:
                    can_raise = True
                    break
        if not can_raise:
            break
    
    return {
        'first_name': first_name,
        'last_name': last_name,
        'name': f"{first_name} {last_name}",
        'sex': sex,
        'race': race,
        **stats
    }


def validate_stat_distribution(stats):
    """
    Validate D&D 5e point buy stat distribution.
    Args:
        stats (dict): {stat_name: value}
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    total_cost = 0
    for stat, value in stats.items():
        if value < STAT_MIN:
            return (False, f"{stat.upper()} must be at least {STAT_MIN}.")
        if value > STAT_MAX:
            return (False, f"{stat.upper()} cannot exceed {STAT_MAX}.")
        if value not in POINT_BUY_COSTS:
            return (False, f"Invalid value {value} for {stat.upper()}.")
        total_cost += POINT_BUY_COSTS[value]
    
    if total_cost != POINT_BUY_TOTAL:
        return (False, f"Point buy must use exactly {POINT_BUY_TOTAL} points (currently using {total_cost}).")
    return (True, None)


def create_character_from_template(account, template, sex="ambiguous"):
    """
    Create a character from a template (for respawn).
    
    Args:
        account: Account object
        template (dict): Template with name and D&D 5e stats
        sex (str): Biological sex
        
    Returns:
        Character: New character object
    """
    from typeclasses.characters import Character
    from world.language.constants import RACE_LANGUAGES
    
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
    
    # Set D&D 5e stats from template
    char.str = template.get('str', 10)
    char.dex = template.get('dex', 10)
    char.con = template.get('con', 10)
    char.int = template.get('int', 10)
    char.wis = template.get('wis', 10)
    char.cha = template.get('cha', 10)
    
    # Store baseline stats (for clone restoration)
    char.db.baseline_stats = {
        'str': char.str,
        'dex': char.dex,
        'con': char.con,
        'int': char.int,
        'wis': char.wis,
        'cha': char.cha,
    }
    
    # Set sex and race
    char.sex = sex
    char.race = template.get('race', 'human')
    
    # Set languages based on race
    race_langs = RACE_LANGUAGES.get(char.race, ['common'])
    char.db.primary_language = 'common'
    char.db.known_languages = list(race_langs)
    
    # Debug: Verify sex was set correctly
    from evennia.comms.models import ChannelDB
    try:
        splattercast = ChannelDB.objects.get_channel("Splattercast")
        splattercast.msg(f"CHARCREATE_SEX_SET: {char.key} sex set to '{sex}', current value: '{char.sex}'")
    except:
        pass
    
    # Set defaults
    # death_count starts at 1 via AttributeProperty in Character class
    char.db.archived = False
    
    return char


def create_flash_clone(account, old_character):
    """
    Create a clone from a dead character.
    Inherits: D&D 5e stats, longdesc, desc, sex, race, skintone
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
    
    # INHERIT: D&D 5e Stats from baseline (not boosted stats)
    # Use baseline_stats if available, otherwise fall back to current stats
    old_baseline = getattr(old_character.db, 'baseline_stats', None)
    if old_baseline:
        char.str = old_baseline.get('str', 10)
        char.dex = old_baseline.get('dex', 10)
        char.con = old_baseline.get('con', 10)
        char.int = old_baseline.get('int', 10)
        char.wis = old_baseline.get('wis', 10)
        char.cha = old_baseline.get('cha', 10)
        
        # Store baseline stats on new character
        char.db.baseline_stats = dict(old_baseline)
    else:
        # Fallback for legacy characters without baseline_stats
        char.str = getattr(old_character, 'str', 10)
        char.dex = getattr(old_character, 'dex', 10)
        char.con = getattr(old_character, 'con', 10)
        char.int = getattr(old_character, 'int', 10)
        char.wis = getattr(old_character, 'wis', 10)
        char.cha = getattr(old_character, 'cha', 10)
        
        # Store as baseline for this character
        char.db.baseline_stats = {
            'str': char.str,
            'dex': char.dex,
            'con': char.con,
            'int': char.int,
            'wis': char.wis,
            'cha': char.cha,
        }
    
    # INHERIT: Appearance
    char.db.desc = old_character.db.desc
    if hasattr(old_character, 'nakeds') and old_character.nakeds:
        char.nakeds = dict(old_character.nakeds)  # Copy dictionary
    
    # INHERIT: Biology
    char.sex = old_character.sex
    char.race = getattr(old_character, 'race', 'human')
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
|b╔════════════════════════════════════════════════════════════════╗
║  THE VEIL PARTS...                                             ║
║  Your spirit stirs, seeking a new vessel.                      ║
╚════════════════════════════════════════════════════════════════╝|n

|yYour previous body has perished.|n
|yYet death is not the end for those with unfinished business...|n

|w╔════════════════════════════════════════════════════════════════╗
║  AVAILABLE VESSELS                                             ║
╚════════════════════════════════════════════════════════════════╝|n

Select a new form:

"""
    
    # Display templates with D&D stats
    for i, template in enumerate(templates, 1):
        race = template.get('race', 'human').capitalize()
        text += f"\n|w[{i}]|n |c{template['first_name']} {template['last_name']}|n ({race})\n"
        text += f"    |rSTR:|n {template.get('str', 10):2d}  "
        text += f"|gDEX:|n {template.get('dex', 10):2d}  "
        text += f"|yCON:|n {template.get('con', 10):2d}  "
        text += f"|bINT:|n {template.get('int', 10):2d}  "
        text += f"|mWIS:|n {template.get('wis', 10):2d}  "
        text += f"|cCHA:|n {template.get('cha', 10):2d}\n"
    
    # Clone option
    old_char = caller.ndb.charcreate_old_character
    if old_char:
        race = getattr(old_char, 'race', 'human').capitalize()
        text += f"\n|w[4]|n |rRESURRECTION|n - |c{old_char.key}|n ({race}) (preserve current identity)\n"
        text += f"    |rSTR:|n {getattr(old_char, 'str', 10):2d}  "
        text += f"|gDEX:|n {getattr(old_char, 'dex', 10):2d}  "
        text += f"|yCON:|n {getattr(old_char, 'con', 10):2d}  "
        text += f"|bINT:|n {getattr(old_char, 'int', 10):2d}  "
        text += f"|mWIS:|n {getattr(old_char, 'wis', 10):2d}  "
        text += f"|cCHA:|n {getattr(old_char, 'cha', 10):2d}\n"
        text += f"    |wInherits appearance, stats, and memories from previous life|n\n"
    
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
|b~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~|n
|c                     WELCOME TO KORVESSA                           |n
|b~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~|n

|wA world where danger lurks in every shadow,|n
|wand reputation is earned through blood, sweat, and cunning.|n

|yThis is not a power fantasy.|n
|wYou will struggle. You will fail. You will bear scars.|n
|wBut every victory will be earned, and every choice will matter.|n

|b~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~|n

Press |w<Enter>|n to begin your journey.
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
        KorvessaRPI Character Creation System

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
        
        # Store last name and advance to display name step
        caller.ndb.charcreate_data['last_name'] = name
        # Call next node directly and return its result
        return first_char_display_name(caller, "", **kwargs)
    
    # Display prompt (first time or after error)
    text = f"""
First name: |c{first_name}|n

|wWhat is your LAST name?|n

(This will be stored as your real identity)
(2-30 characters, letters only)

|w>|n """
    
    options = (
        {"key": "_default",
         "goto": "first_char_name_last"},
    )
    
    return text, options


def first_char_display_name(caller, raw_string, **kwargs):
    """Get display name (handle/alias)."""
    
    first_name = caller.ndb.charcreate_data.get('first_name', '')
    last_name = caller.ndb.charcreate_data.get('last_name', '')
    
    # If input provided, validate it
    if raw_string and raw_string.strip():
        name = raw_string.strip()
        
        if len(name) < 2 or len(name) > 30:
            caller.msg(f"|rInvalid name: Name must be 2-30 characters.|n")
            # Return None to re-display current node
            return None
        
        if not re.match(r"^[a-zA-Z\s]+$", name):
            caller.msg(f"|rInvalid name: Only letters and spaces allowed.|n")
            # Return None to re-display current node
            return None
        
        # Use title case: capitalize first letter of each word
        name = name.title()
        
        # Check display name uniqueness
        is_valid, error = validate_name(name, account=caller)
        if not is_valid:
            caller.msg(f"|r{error}|n")
            # Return None to re-display current node
            return None
        
        # Store display name and advance to race selection
        caller.ndb.charcreate_data['display_name'] = name
        # Call next node directly and return its result
        return first_char_race(caller, "", **kwargs)
    
    # Display prompt (first time or after error)
    text = f"""
Real Name: |c{first_name} {last_name}|n

|wWhat is your DISPLAY NAME?|n

This is what people will see and use to target you in emotes, combat, etc.
You can use your real name or an alias.

Examples: "{first_name}", "Thornwood", "Ashford", "Grim"

(2-30 characters, letters only - first letter will be capitalized)

|w>|n """
    
    options = (
        {"key": "_default",
         "goto": "first_char_display_name"},
    )
    
    return text, options


def first_char_sex(caller, raw_string, **kwargs):
    """Select biological sex."""
    first_name = caller.ndb.charcreate_data.get('first_name', '')
    last_name = caller.ndb.charcreate_data.get('last_name', '')
    display_name = caller.ndb.charcreate_data.get('display_name', '')
    race = caller.ndb.charcreate_data.get('race', 'human')
    text = f"""
Real Name: |c{first_name} {last_name}|n
Display Name: |c{display_name}|n
Race: |c{race.capitalize()}|n

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


def first_char_race(caller, raw_string, **kwargs):
    """Select character race."""
    from world.language.constants import RACE_LANGUAGES, LANGUAGES
    
    first_name = caller.ndb.charcreate_data.get('first_name', '')
    last_name = caller.ndb.charcreate_data.get('last_name', '')
    display_name = caller.ndb.charcreate_data.get('display_name', '')
    
    # Build race descriptions with language info
    race_info = {
'human': {
    'desc': 'Commonborn and widespread, humans endure through adaptability, ambition, and social maneuvering. Their cultures are fragmented, shaped more by hardship and history than destiny.',
    'bonus': 'Learns slightly faster.'
},
'elf': {
    'desc': 'Long-lived and insular, elves are shaped by memory rather than progress. Their keen senses come from centuries of survival, not mysticism, and their traditions are slow to change.',
    'bonus': 'Speaks Elvish in addition to Common.'
},
'dwarf': {
    'desc': 'Enduring and tradition-bound, dwarves are defined by lineage, craft, and obligation. Their resilience is earned through labor, stone, and unyielding social codes.',
    'bonus': 'Speaks Dwarvish in addition to Common.'
        }
    }
    
    text = f"""
Real Name: |c{first_name} {last_name}|n
Display Name: |c{display_name}|n

|wSelect your race:|n

|w[1]|n |cHuman|n
    {race_info['human']['desc']}
    |y{race_info['human']['bonus']}|n

|w[2]|n |cElf|n
    {race_info['elf']['desc']}
    |y{race_info['elf']['bonus']}|n

|w[3]|n |cDwarf|n
    {race_info['dwarf']['desc']}
    |y{race_info['dwarf']['bonus']}|n

|wEnter choice:|n """

    # Handle input
    if raw_string and raw_string.strip():
        choice = raw_string.strip()
        race_map = {'1': 'human', '2': 'elf', '3': 'dwarf'}
        
        if choice in race_map:
            selected_race = race_map[choice]
            caller.ndb.charcreate_data['race'] = selected_race
            
            # Set racial languages automatically
            racial_langs = RACE_LANGUAGES.get(selected_race, ['common'])
            caller.ndb.charcreate_data['languages'] = racial_langs.copy()
            
            caller.msg(f"|gRace set to |c{selected_race.capitalize()}|g.|n")
            return first_char_sex(caller, "", **kwargs)
        else:
            caller.msg("|rInvalid choice. Please enter 1, 2, or 3.|n")
            return None
    
    options = (
        {"key": "_default",
         "goto": "first_char_race"},
    )
    
    return text, options


def first_char_stat_assign(caller, raw_string, **kwargs):
    """Distribute 27 points among 6 stats using D&D 5e standard point buy."""
    if 'sex' in kwargs:
        caller.ndb.charcreate_data['sex'] = kwargs['sex']
    first_name = caller.ndb.charcreate_data.get('first_name', '')
    last_name = caller.ndb.charcreate_data.get('last_name', '')
    display_name = caller.ndb.charcreate_data.get('display_name', '')
    race = caller.ndb.charcreate_data.get('race', 'human')
    sex = caller.ndb.charcreate_data.get('sex', 'ambiguous')
    stats = caller.ndb.charcreate_data.get('stats', {
        'str': 8,
        'dex': 8,
        'con': 8,
        'int': 8,
        'wis': 8,
        'cha': 8
    })
    
    # Calculate points spent using D&D 5e point buy costs
    def calc_cost(value):
        """Calculate point cost for a stat value."""
        return POINT_BUY_COSTS.get(value, 0)
    
    points_spent = sum(calc_cost(v) for v in stats.values())
    remaining = POINT_BUY_TOTAL - points_spent
    
    # Calculate modifiers
    def calc_mod(value):
        return (value - 10) // 2
    
    text = f"""
|wAssign Your Ability Scores|n

Display Name: |c{display_name}|n
Race: |c{race.capitalize()}|n
Sex: |c{sex.capitalize()}|n

|wD&D 5e Point Buy:|n |y{POINT_BUY_TOTAL} points|w to spend. Stats range from |y8|w to |y15|w.|n
|wPoint costs:|n 8=0, 9=1, 10=2, 11=3, 12=4, 13=5, 14=7, 15=9

|b----------------------------------------------------------------------|n
    |rSTR|n (Strength):     {stats['str']:2d}  |w({calc_mod(stats['str']):+d})|n  - Physical power, melee damage
    |gDEX|n (Dexterity):    {stats['dex']:2d}  |w({calc_mod(stats['dex']):+d})|n  - Agility, reflexes, ranged attacks
    |yCON|n (Constitution): {stats['con']:2d}  |w({calc_mod(stats['con']):+d})|n  - Health, endurance, resilience
    |bINT|n (Intelligence): {stats['int']:2d}  |w({calc_mod(stats['int']):+d})|n  - Reasoning, memory, analysis
    |mWIS|n (Wisdom):       {stats['wis']:2d}  |w({calc_mod(stats['wis']):+d})|n  - Perception, insight, willpower
    |cCHA|n (Charisma):     {stats['cha']:2d}  |w({calc_mod(stats['cha']):+d})|n  - Presence, persuasion, force of will
|b----------------------------------------------------------------------|n

|wPoints spent:|n {points_spent}/{POINT_BUY_TOTAL}  {'|gREMAINING: ' + str(remaining) + '|n' if remaining >= 0 else '|rOVER BY:|n ' + str(abs(remaining))}

|wCommands:|n
    |w<stat> <value>|n  - Set a stat (e.g., 'str 15' or 'dex 10')
    |wreset|n           - Reset all stats to 8
    |wdone|n            - Finalize (when exactly {POINT_BUY_TOTAL} points spent)

|w>|n """
    options = (
        {"key": "_default", "goto": "first_char_stat_assign"},
    )
    if raw_string and raw_string.strip():
        args = raw_string.strip().lower().split()
        if not args:
            return text, options
        command = args[0]
        valid_stats = ['str', 'dex', 'con', 'int', 'wis', 'cha']
        
        # Handle stat aliases
        stat_aliases = {
            'strength': 'str',
            'dexterity': 'dex',
            'constitution': 'con',
            'intelligence': 'int',
            'wisdom': 'wis',
            'charisma': 'cha'
        }
        if command in stat_aliases:
            command = stat_aliases[command]
        
        if command == 'reset':
            stats = {k: 8 for k in valid_stats}
            caller.ndb.charcreate_data['stats'] = stats
            caller.msg("|yAll stats reset to 8.|n")
            # Immediately recalculate and redisplay
            points_spent = sum(calc_cost(v) for v in stats.values())
            remaining = POINT_BUY_TOTAL - points_spent
            text = f"""
|wAssign Your Ability Scores|n

Display Name: |c{display_name}|n
Race: |c{race.capitalize()}|n
Sex: |c{sex.capitalize()}|n

|wD&D 5e Point Buy:|n |y{POINT_BUY_TOTAL} points|w to spend. Stats range from |y8|w to |y15|w.|n
|wPoint costs:|n 8=0, 9=1, 10=2, 11=3, 12=4, 13=5, 14=7, 15=9

|b----------------------------------------------------------------------|n
    |rSTR|n (Strength):     {stats['str']:2d}  |w({calc_mod(stats['str']):+d})|n  - Physical power, melee damage
    |gDEX|n (Dexterity):    {stats['dex']:2d}  |w({calc_mod(stats['dex']):+d})|n  - Agility, reflexes, ranged attacks
    |yCON|n (Constitution): {stats['con']:2d}  |w({calc_mod(stats['con']):+d})|n  - Health, endurance, resilience
    |bINT|n (Intelligence): {stats['int']:2d}  |w({calc_mod(stats['int']):+d})|n  - Reasoning, memory, analysis
    |mWIS|n (Wisdom):       {stats['wis']:2d}  |w({calc_mod(stats['wis']):+d})|n  - Perception, insight, willpower
    |cCHA|n (Charisma):     {stats['cha']:2d}  |w({calc_mod(stats['cha']):+d})|n  - Presence, persuasion, force of will
|b----------------------------------------------------------------------|n

|wPoints spent:|n {points_spent}/{POINT_BUY_TOTAL}  {'|gREMAINING: ' + str(remaining) + '|n' if remaining >= 0 else '|rOVER BY:|n ' + str(abs(remaining))}

|wCommands:|n
    |w<stat> <value>|n  - Set a stat (e.g., 'str 15' or 'dex 10')
    |wreset|n           - Reset all stats to 8
    |wdone|n            - Finalize (when exactly {POINT_BUY_TOTAL} points spent)

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
                caller.msg("|rUsage: <stat> <value>  (e.g., 'str 15')|n")
                return text, options
            try:
                value = int(args[1])
            except ValueError:
                caller.msg("|rValue must be a number.|n")
                return text, options
            if value < 8 or value > 15:
                caller.msg("|rValue must be 8-15 (D&D 5e point buy range).|n")
                return text, options
            stats[command] = value
            caller.ndb.charcreate_data['stats'] = stats
            # Immediately update display after stat set
            points_spent = sum(calc_cost(v) for v in stats.values())
            remaining = POINT_BUY_TOTAL - points_spent
            text = f"""
|wAssign Your Ability Scores|n

Display Name: |c{display_name}|n
Race: |c{race.capitalize()}|n
Sex: |c{sex.capitalize()}|n

|wD&D 5e Point Buy:|n |y{POINT_BUY_TOTAL} points|w to spend. Stats range from |y8|w to |y15|w.|n
|wPoint costs:|n 8=0, 9=1, 10=2, 11=3, 12=4, 13=5, 14=7, 15=9

|b----------------------------------------------------------------------|n
    |rSTR|n (Strength):     {stats['str']:2d}  |w({calc_mod(stats['str']):+d})|n  - Physical power, melee damage
    |gDEX|n (Dexterity):    {stats['dex']:2d}  |w({calc_mod(stats['dex']):+d})|n  - Agility, reflexes, ranged attacks
    |yCON|n (Constitution): {stats['con']:2d}  |w({calc_mod(stats['con']):+d})|n  - Health, endurance, resilience
    |bINT|n (Intelligence): {stats['int']:2d}  |w({calc_mod(stats['int']):+d})|n  - Reasoning, memory, analysis
    |mWIS|n (Wisdom):       {stats['wis']:2d}  |w({calc_mod(stats['wis']):+d})|n  - Perception, insight, willpower
    |cCHA|n (Charisma):     {stats['cha']:2d}  |w({calc_mod(stats['cha']):+d})|n  - Presence, persuasion, force of will
|b----------------------------------------------------------------------|n

|wPoints spent:|n {points_spent}/{POINT_BUY_TOTAL}  {'|gREMAINING: ' + str(remaining) + '|n' if remaining >= 0 else '|rOVER BY:|n ' + str(abs(remaining))}

|wCommands:|n
    |w<stat> <value>|n  - Set a stat (e.g., 'str 15' or 'dex 10')
    |wreset|n           - Reset all stats to 8
    |wdone|n            - Finalize (when exactly {POINT_BUY_TOTAL} points spent)

|w>|n """
            return text, options
        else:
            caller.msg(f"|rUnknown command. Valid stats: {', '.join(valid_stats)}|n")
    return text, options


def first_char_confirm(caller, raw_string, **kwargs):
    """Final confirmation and character creation."""
    from world.language.constants import LANGUAGES
    
    first_name = caller.ndb.charcreate_data.get('first_name', '')
    last_name = caller.ndb.charcreate_data.get('last_name', '')
    display_name = caller.ndb.charcreate_data.get('display_name', '')
    race = caller.ndb.charcreate_data.get('race', 'human')
    sex = caller.ndb.charcreate_data.get('sex', 'ambiguous')
    stats = caller.ndb.charcreate_data.get('stats', {
        'str': 8,
        'dex': 8,
        'con': 8,
        'int': 8,
        'wis': 8,
        'cha': 8
    })
    languages = caller.ndb.charcreate_data.get('languages', ['common'])
    
    # Calculate points spent
    points_spent = sum(POINT_BUY_COSTS.get(v, 0) for v in stats.values())
    
    # Calculate modifiers
    def calc_mod(value):
        return (value - 10) // 2
    
    # Format languages
    lang_names = [LANGUAGES.get(lang, {}).get('name', lang.capitalize()) for lang in languages]
    
    text = f"""
|wReview Your Character|n

|wReal Name:|n |c{first_name} {last_name}|n
|wDisplay Name:|n |c{display_name}|n
|wRace:|n |c{race.capitalize()}|n
|wSex:|n |c{sex.capitalize()}|n

|wAbility Scores:|n (Points spent: {points_spent}/{POINT_BUY_TOTAL})
    |rSTR:|n {stats['str']:2d} ({calc_mod(stats['str']):+d})
    |gDEX:|n {stats['dex']:2d} ({calc_mod(stats['dex']):+d})
    |yCON:|n {stats['con']:2d} ({calc_mod(stats['con']):+d})
    |bINT:|n {stats['int']:2d} ({calc_mod(stats['int']):+d})
    |mWIS:|n {stats['wis']:2d} ({calc_mod(stats['wis']):+d})
    |cCHA:|n {stats['cha']:2d} ({calc_mod(stats['cha']):+d})

|wLanguages:|n {', '.join(lang_names)}

|y----------------------------------------------------------------------|n
|yOnce created, your name cannot be changed.|n
|yStats can be modified through gameplay.|n
|y----------------------------------------------------------------------|n

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
    return text, options


def first_char_select_language(caller, raw_string, **kwargs):
    """Select additional language during character creation (for humans)."""
    from world.language.constants import LANGUAGES, RACE_LANGUAGES
    
    race = caller.ndb.charcreate_data.get('race', 'human')
    languages = caller.ndb.charcreate_data.get('languages', ['common'])
    
    # Non-humans already have their languages set, skip to finalize
    if race != 'human':
        return first_char_finalize(caller, "", **kwargs)
    
    # Humans pick one additional language
    available_langs = [code for code in LANGUAGES.keys() if code not in languages]
    
    text = f"""
|wChoose an Additional Language|n

As a human, you may learn one additional language beyond Common.

|wCurrent Languages:|n {', '.join(LANGUAGES.get(lang, {}).get('name', lang.capitalize()) for lang in languages)}

|wAvailable Languages:|n
"""
    
    # List available languages
    lang_list = []
    for i, code in enumerate(sorted(available_langs), 1):
        info = LANGUAGES[code]
        lang_list.append(f"|w[{i}]|n |c{info['name']}|n - {info['description']}")
    
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
        sorted_langs = sorted(available_langs)
        
        # Handle skipping (human can choose to only know Common)
        if command in ['done', 'skip', 'none']:
            caller.msg("|yProceeding with only Common.|n")
            return first_char_finalize(caller, "", **kwargs)
        
        # Try to parse as a number (1-indexed)
        try:
            lang_index = int(command) - 1
            if 0 <= lang_index < len(sorted_langs):
                selected_code = sorted_langs[lang_index]
                languages.append(selected_code)
                caller.ndb.charcreate_data['languages'] = languages
                caller.msg(f"|gAdded |c{LANGUAGES[selected_code]['name']}|g to your languages.|n")
                return first_char_finalize(caller, "", **kwargs)
        except ValueError:
            pass
        
        caller.msg("|rInvalid selection. Please enter a number, or 'skip' to continue with only Common.|n")
    
    text += f"\n\nType a number to select a language, or |wskip|n to continue with only Common."
    text += "\n\n|w>|n"
    return text, options


def first_char_select_second_language(caller, raw_string, **kwargs):
    """Deprecated - kept for compatibility but redirects to finalize."""
    return first_char_finalize(caller, "", **kwargs)


def first_char_finalize(caller, raw_string, **kwargs):
    """Create the character and enter game."""
    from typeclasses.characters import Character
    from world.language.constants import LANGUAGES
    
    first_name = caller.ndb.charcreate_data.get('first_name', '')
    last_name = caller.ndb.charcreate_data.get('last_name', '')
    display_name = caller.ndb.charcreate_data.get('display_name', '')
    full_real_name = f"{first_name} {last_name}"
    race = caller.ndb.charcreate_data.get('race', 'human')
    sex = caller.ndb.charcreate_data.get('sex', 'ambiguous')
    stats = caller.ndb.charcreate_data.get('stats', {
        'str': 8,
        'dex': 8,
        'con': 8,
        'int': 8,
        'wis': 8,
        'cha': 8
    })
    languages = caller.ndb.charcreate_data.get('languages', ['common'])
    
    start_location = get_start_location()
    try:
        # Use display_name as character key (what people see/target)
        char, errors = caller.create_character(
            key=display_name,
            location=start_location,
            home=start_location,
            typeclass="typeclasses.characters.Character"
        )
        if errors:
            raise Exception(f"Character creation failed: {errors}")
        
        # Store real name separately
        char.db.real_first_name = first_name
        char.db.real_last_name = last_name
        char.db.real_full_name = full_real_name
        
        # Set D&D 5e stats
        char.str = stats['str']
        char.dex = stats['dex']
        char.con = stats['con']
        char.int = stats['int']
        char.wis = stats['wis']
        char.cha = stats['cha']
        char.race = race
        char.sex = sex
        char.db.archived = False
        
        # Set languages
        char.db.languages = languages
        char.db.primary_language = languages[0] if languages else 'common'
        
        # Award starting IP
        char.db.ip = char.db.ip if hasattr(char.db, 'ip') and char.db.ip else 0
        char.db.ip += 200
        
        import uuid
        char.db.character_id = str(uuid.uuid4())
        char.db.original_creation = time.time()
        caller.puppet_object(caller.sessions.all()[0], char)
        
        # Format languages for display
        lang_names = [LANGUAGES.get(lang, {}).get('name', lang.capitalize()) for lang in languages]
        
        char.msg("")
        char.msg(f"|wWelcome to Korvessa, |c{char.key}|w.|n")
        char.msg("")
        char.msg("|wThe road ahead is perilous. Trust is earned, not given.|n")
        char.msg("")
        char.msg("|g=== Character Creation Complete ===|n")
        char.msg("")
        char.msg(f"|wRace:|n |c{race.capitalize()}|n")
        char.msg(f"|wLanguages:|n |c{', '.join(lang_names)}|n")
        char.msg("")
        char.msg(f"|gYou have been awarded |c200 Investment Points (IP)|g.|n")
        char.msg(f"|cCurrent IP:|n |c{char.db.ip}|n")
        char.msg("")
        char.msg("|wYou can spend IP to improve your skills and abilities.|n")
        char.msg("|wType |yhelp ip|w to learn more about the IP system.|n")
        char.msg("")
        char.msg("|c=== Optional: Submit Your Background ===|n")
        char.msg("")
        char.msg("|wSubmit a character background to receive an additional |y50 IP bonus|w!|n")
        char.msg("")
        char.msg("|wType |cbackground submit <text>|w to write your character's story.|n")
        char.msg("|wBackgrounds must be approved by staff but can be edited until approval.|n")
        char.msg("")
        char.msg("|wType |ylook|w to examine your surroundings.|n")
        char.msg("")
        char.msg("|wType |yhelp|w for a list of commands.|n")
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
