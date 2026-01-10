# ===================================================================
# IMPORTS
# ===================================================================
from evennia import Command
# ===================================================================
# CHROME UNINSTALL COMMAND
# ===================================================================

class CmdChromeUninstall(Command):
    """
    Uninstall chrome from a target character.

    Usage:
        chromeuninstall <chrome> from <person>

    Example:
        chromeuninstall mindseye from Laszlo
    """
    key = "chromeuninstall"
    locks = "cmd:perm(Builder)"
    help_category = "Admin"

    def func(self):
        caller = self.caller
        args = self.args.strip().split()
        if len(args) < 3 or args[1].lower() != "from":
            caller.msg("Usage: chromeuninstall <chrome> from <person>")
            return
        chrome_name = args[0].lower()
        target_name = " ".join(args[2:])
        # Find target character
        matches = search_object(target_name, exact=False)
        if not matches:
            caller.msg(f"Could not find character '{target_name}'.")
            return
        target = matches[0]
        # Check for installed chrome attribute
        installed = getattr(target.db, "installed_chrome", None)
        if not installed or installed.get("chrome_shortname") != chrome_name:
            caller.msg(f"No chrome '{chrome_name}' installed in {target.key}.")
            return
        # Skill check: surgery (primary), science (secondary)
        # Builder+ always succeeds
        if caller.locks.check_lockstring(caller, "perm(Builder)"):
            success = True
        else:
            surgery = getattr(caller, 'surgery', 0)
            science = getattr(caller, 'science', 0)
            skill_val = surgery * 0.7 + science * 0.3
            import random
            roll = random.randint(1, 20)
            success = (skill_val + roll) >= 15
        if success:
            # Remove installed chrome attribute and respawn item in caller's inventory
            del target.db.installed_chrome
            chrome_registry = {
                "mindseye": "world.medical.chrome_mindseye.ChromeMindseye",
                # Add more chrome here as needed
            }
            class_path = chrome_registry.get(chrome_name)
            if class_path:
                key = f"{chrome_name.title()} Chrome"
                new_chrome = create_object(class_path, key=key, location=caller)
                caller.msg(f"You successfully uninstall {chrome_name.title()} Chrome from {target.key} and receive it.")
                target.msg(f"{caller.key} has uninstalled {chrome_name.title()} Chrome from you.")
            else:
                caller.msg(f"Uninstalled chrome, but could not respawn item (unknown shortname: {chrome_name}).")
        else:
            caller.msg("You fail to uninstall the chrome.")
            target.msg(f"{caller.key} attempted to uninstall chrome from you but failed.")
# ===================================================================
# CHROME INSTALL COMMAND
# ===================================================================

class CmdChromeInstall(Command):
    """
    Install chrome into a target character.

    Usage:
        chromeinstall <chrome> in <person>

    Example:
        chromeinstall mindseye in Laszlo
    """
    key = "chromeinstall"
    locks = "cmd:perm(Builder)"
    help_category = "Admin"

    def func(self):
        caller = self.caller
        args = self.args.strip().split()
        if len(args) < 3 or args[1].lower() != "in":
            caller.msg("Usage: chromeinstall <chrome> in <person>")
            return
        chrome_name = args[0].lower()
        target_name = " ".join(args[2:])
        # Find target character
        matches = search_object(target_name, exact=False)
        if not matches:
            caller.msg(f"Could not find character '{target_name}'.")
            return
        target = matches[0]
        # Find chrome item in caller's inventory or room
        location = caller.location
        chrome_obj = None
        # Search caller's inventory first
        for item in getattr(caller, 'contents', []):
            if hasattr(item, 'db') and getattr(item.db, 'chrome_shortname', None) == chrome_name:
                chrome_obj = item
                break
        # If not found, search room
        if not chrome_obj:
            for item in getattr(location, 'contents', []):
                if hasattr(item, 'db') and getattr(item.db, 'chrome_shortname', None) == chrome_name:
                    chrome_obj = item
                    break
        if not chrome_obj:
            caller.msg(f"No chrome '{chrome_name}' found in your inventory or room.")
            return
        # Skill check: surgery (primary), science (secondary)
        # Builder+ always succeeds
        if caller.locks.check_lockstring(caller, "perm(Builder)"):
            success = True
        else:
            surgery = getattr(caller, 'surgery', 0)
            science = getattr(caller, 'science', 0)
            skill_val = surgery * 0.7 + science * 0.3
            import random
            roll = random.randint(1, 20)
            success = (skill_val + roll) >= 15
        if success:
            # Store chrome as attribute on target, delete item
            target.db.installed_chrome = {
                "chrome_name": getattr(chrome_obj.db, "chrome_name", ""),
                "chrome_shortname": getattr(chrome_obj.db, "chrome_shortname", ""),
                "chrome_buff": getattr(chrome_obj.db, "chrome_buff", ""),
                "chrome_ability": getattr(chrome_obj.db, "chrome_ability", ""),
                "empathy_cost": getattr(chrome_obj.db, "empathy_cost", 0),
            }
            chrome_obj.delete()
            caller.msg(f"You successfully install {chrome_obj.key} into {target.key}.")
            target.msg(f"{caller.key} has installed {chrome_obj.key} into you.")
        else:
            caller.msg("You fail to install the chrome.")
            target.msg(f"{caller.key} attempted to install chrome into you but failed.")

from evennia import Command
from evennia.utils.create import create_object

class CmdSpawnChrome(Command):
    """
    Spawn chrome by shortname and amount.

    Usage:
        spawnchrome <shortname> <amount>

    Example:
        spawnchrome mindseye 2
    """
    key = "spawnchrome"
    locks = "cmd:perm(Builder)"
    help_category = "Admin"

    def func(self):
        caller = self.caller
        args = self.args.strip().split()
        if len(args) < 2:
            caller.msg("Usage: spawnchrome <shortname> <amount>")
            return
        shortname = args[0].lower()
        try:
            amount = int(args[1])
        except ValueError:
            caller.msg("Amount must be an integer.")
            return
        # Chrome registry: map shortname to class path
        chrome_registry = {
            "mindseye": "world.medical.chrome_mindseye.ChromeMindseye",
            # Add more chrome here as needed
        }
        if shortname not in chrome_registry:
            caller.msg(f"Unknown chrome shortname: {shortname}")
            return
        class_path = chrome_registry[shortname]
        spawned = []
        for _ in range(amount):
            # Set a default key for the object to avoid NOT NULL constraint error
            key = f"{shortname.title()} Chrome"
            obj = create_object(class_path, key=key, location=caller.location)
            spawned.append(obj)
        caller.msg(f"Spawned {amount} '{shortname}' chrome in this room.")
# ===================================================================
# IMPORTS
# ===================================================================
from evennia import Command
from evennia.comms.models import ChannelDB
# ===================================================================
# THINK COMMAND
# ===================================================================

class CmdThink(Command):
    """
    Externalize your character's thoughts.

    Usage:
        think <thought>

    Example:
        think Damn that dude has a cute butt!

    You see:
        You think . o O ( Damn that dude has a cute butt! )
    GMs and Builder+ see this in the 'thoughts' channel:
        <Thinker>: Damn that dude has a cute butt!
    """
    key = "think"
    locks = "cmd:all()"
    help_category = "Roleplay"

    def func(self):
        caller = self.caller
        thought = self.args.strip()
        if not thought:
            caller.msg("What do you want to think?")
            return
        # Show to self
        caller.msg(f"You think . o O ( {thought} )")
        # Send to builder+ 'thoughts' channel
        channel = ChannelDB.objects.get_channel("thoughts")
        if channel:
            thinker = caller.get_display_name(caller) if hasattr(caller, 'get_display_name') else caller.key
            channel.msg(f"{thinker}: {thought}")

        # Mind's Eye chrome: send thought to others in room with Mind's Eye installed
        location = getattr(caller, 'location', None)
        if location:
            for obj in location.contents:
                if obj == caller:
                    continue
                # Check for Mind's Eye chrome installed
                chrome = [item for item in getattr(obj, 'contents', []) if hasattr(item, 'db') and getattr(item.db, 'chrome_shortname', None) == 'mindseye']
                if chrome:
                    thinker = caller.get_display_name(caller) if hasattr(caller, 'get_display_name') else caller.key
                    obj.msg(f"{thinker} . o O ( {thought} )")
from evennia import Command
from evennia.utils.search import search_object
from evennia.utils.utils import inherits_from
from world.combat.constants import (
    PERM_BUILDER, PERM_DEVELOPER,
    BOX_TOP_LEFT, BOX_TOP_RIGHT, BOX_BOTTOM_LEFT, BOX_BOTTOM_RIGHT,
    BOX_HORIZONTAL, BOX_VERTICAL, BOX_TEE_RIGHT, BOX_TEE_LEFT,
    COLOR_SUCCESS, COLOR_NORMAL,
    MAX_DESCRIPTION_LENGTH,
    VALID_LONGDESC_LOCATIONS,
    SKINTONE_PALETTE, VALID_SKINTONES,
    STAT_DESCRIPTORS, STAT_TIER_RANGES
)
from world.medical.utils import get_medical_status_description
import re


# ===================================================================
# CENTERING UTILITIES (from death_progression.py)
# ===================================================================

def _get_terminal_width(session=None):
    """Get terminal width from session, defaulting to 78 for MUD compatibility."""
    if session:
        try:
            detected_width = session.protocol_flags.get("SCREENWIDTH", [78])[0]
            return max(60, detected_width)  # Minimum 60 for readability
        except (IndexError, KeyError, TypeError):
            pass
    return 78


def _strip_color_codes(text):
    """Remove Evennia color codes from text to get actual visible length."""
    # Remove all |x codes (where x is any character) - same pattern as death curtain
    return re.sub(r'\|.', '', text)


def _center_text(text, width=None, session=None):
    """Center text using same approach as curtain_of_death.py for consistency."""
    if width is None:
        width = _get_terminal_width(session)
    
    # Use same width calculation as curtain for consistent centering
    # Reserve small buffer for color codes like the curtain does
    message_width = width - 1  # Match curtain_width calculation
    
    # Split into lines and center each line - same as curtain
    lines = text.split('\n')
    centered_lines = []
    
    for line in lines:
        if not line.strip():  # Empty line
            centered_lines.append("")
            continue
            
        # Calculate visible text length (without color codes) - same as curtain
        visible_text = _strip_color_codes(line)
        
        # Use Python's built-in center method for proper centering - same as curtain  
        centered_visible = visible_text.center(message_width)
        
        # Calculate the actual padding that center() applied
        padding_needed = message_width - len(visible_text)
        left_padding = padding_needed // 2
        
        # Apply the same left padding to the original colored text
        centered_line = " " * left_padding + line
        centered_lines.append(centered_line)
    
    return '\n'.join(centered_lines)


# ===================================================================
# STAT DESCRIPTOR UTILITIES
# ===================================================================

def get_stat_descriptor(stat_name, numeric_value):
    """
    Convert numeric stat value to descriptive word.
    
    Args:
        stat_name (str): Name of the stat ('grit', 'resonance', 'intellect', 'motorics')
        numeric_value (int): Numeric stat value (0-150)
        
    Returns:
        str: Descriptive word for the stat tier, or "Unknown" if invalid
    """
    # Validate stat name
    if stat_name not in STAT_DESCRIPTORS:
        return "Unknown"
    
    # Ensure numeric value is valid
    if not isinstance(numeric_value, (int, float)) or numeric_value < 0:
        numeric_value = 0
    
    numeric_value = int(numeric_value)
    
    # Handle values over 150
    if numeric_value > 150:
        numeric_value = 150
    
    # Find the appropriate tier
    for min_val, max_val in STAT_TIER_RANGES:
        if min_val <= numeric_value <= max_val:
            # Find the descriptor key for this range
            # The keys in STAT_DESCRIPTORS correspond to the max values of each range
            descriptor_key = max_val
            return STAT_DESCRIPTORS[stat_name].get(descriptor_key, "Unknown")
    
    # Fallback
    return "Unknown"


def get_stat_range(descriptor_word, stat_name):
    """
    Get numeric range for a descriptive word.
    
    Args:
        descriptor_word (str): Descriptive word (e.g., "Granite", "Moderate")
        stat_name (str): Name of the stat ('grit', 'resonance', 'intellect', 'motorics')
        
    Returns:
        tuple: (min_value, max_value) tuple, or (0, 0) if not found
    """
    # Validate stat name
    if stat_name not in STAT_DESCRIPTORS:
        return (0, 0)
    
    # Find the descriptor in the stat's mapping
    stat_descriptors = STAT_DESCRIPTORS[stat_name]
    
    # Look for the descriptor word (case-insensitive)
    descriptor_word = descriptor_word.lower()
    for max_val, word in stat_descriptors.items():
        if word.lower() == descriptor_word:
            # Find the corresponding range
            for min_val, range_max_val in STAT_TIER_RANGES:
                if range_max_val == max_val:
                    return (min_val, max_val)
    
    # Not found
    return (0, 0)


def get_stat_tier_info(stat_name, numeric_value):
    """
    Get comprehensive tier information for a stat value.
    
    Args:
        stat_name (str): Name of the stat
        numeric_value (int): Numeric stat value
        
    Returns:
        dict: Dictionary with 'descriptor', 'min_range', 'max_range', 'tier_letter'
    """
    descriptor = get_stat_descriptor(stat_name, numeric_value)
    min_range, max_range = get_stat_range(descriptor, stat_name)
    
    # Calculate tier letter (A-Z)
    tier_letter = "Z"  # Default
    if 0 <= numeric_value <= 150:
        for i, (min_val, max_val) in enumerate(STAT_TIER_RANGES):
            if min_val <= numeric_value <= max_val:
                tier_letter = chr(ord('A') + i)
                break
    
    return {
        'descriptor': descriptor,
        'min_range': min_range,
        'max_range': max_range,
        'tier_letter': tier_letter,
        'numeric_value': numeric_value
    }

class CmdStats(Command):
    """
    See your character's stats and skill evaluations.

    Usage:
      @stats / score
      @stats <target>          (Authorized personnel only)
      @stats/numeric           (Authorized personnel only - diagnostic mode)
      @stats/numeric <target>  (Authorized personnel only)

    Displays your subject evaluation from the Genetic Expression Liability - 
    Medical & Sociological Testing program. Stat assessment parameters 
    are shown using standardized classification descriptors (A-Z tiers) for 
    efficient liability assessment.
    
    File reference includes subject ID and mortality revision count in Roman 
    numerals. Authorized personnel may access diagnostic numeric values for 
    detailed risk evaluation and resource allocation purposes.
    """

    key = "stats"
    aliases = ["score"]
    locks = "cmd:all()"

    def func(self):
        "Implement the command."

        caller = self.caller
        target = caller
        
        # Parse switches manually
        raw_args = self.args.strip()
        switches = []
        args = raw_args
        
        if raw_args.startswith('/'):
            # Find the end of switches
            parts = raw_args[1:].split(None, 1)
            if parts:
                switch_part = parts[0]
                args = parts[1] if len(parts) > 1 else ""
                switches = [s.lower() for s in switch_part.split('/') if s]

        if args:
            if (
                self.account.check_permstring(PERM_BUILDER)
                or self.account.check_permstring(PERM_DEVELOPER)
            ):
                matches = search_object(args.strip(), exact=False)
                if matches:
                    target = matches[0]

        # New stat system
        smrt = getattr(target, 'smrt', 0)
        will = getattr(target, 'will', 0)
        edge = getattr(target, 'edge', 0)
        ref = getattr(target, 'ref', 0)
        body = getattr(target, 'body', 0)
        dex = getattr(target, 'dex', 0)
        emp = getattr(target, 'emp', 0)
        tech = getattr(target, 'tech', 0)

        smrt_desc = get_stat_descriptor("smrt", smrt)
        will_desc = get_stat_descriptor("will", will)
        edge_desc = get_stat_descriptor("edge", edge)
        ref_desc = get_stat_descriptor("ref", ref)
        body_desc = get_stat_descriptor("body", body)
        dex_desc = get_stat_descriptor("dex", dex)
        emp_desc = get_stat_descriptor("emp", emp)
        tech_desc = get_stat_descriptor("tech", tech)

        def stat_display(desc, val):
            return f"|w[|n {val} |w]|n {desc}"

        # Calculate starting empathy as EDGE + WILLPOWER
        starting_emp = getattr(target, 'edge', 0) + getattr(target, 'will', 0)
        # Deduct empathy cost from installed chrome if present
        chrome = getattr(target.db, 'installed_chrome', None)
        chrome_empathy_cost = chrome.get('empathy_cost', 0) if chrome else 0
        def stat_line(label, base, current):
            color = "|g" if current >= base else "|r"
            return f"|y{label:<10}|n [ {base} / {color}{current}|n ]"

        stat_labels = [
            ("Smarts", 'smrt'),
            ("Willpower", 'will'),
            ("Edge", 'edge'),
            ("Reflexes", 'ref'),
            ("Body", 'body'),
            ("Dexterity", 'dex'),
            ("Empathy", 'emp'),
            ("Technique", 'tech'),
        ]
        # Split into two columns of 4
        left_stats = stat_labels[:4]
        right_stats = stat_labels[4:]
        stat_rows = []
        for i in range(4):
            left_label, left_attr = left_stats[i]
            right_label, right_attr = right_stats[i]
            left_base = getattr(target, left_attr, 0)
            left_current = getattr(target, left_attr, 0)
            # Empathy: base is EDGE + WILL, final is base unless modified by chrome/drugs
            if right_attr == 'emp':
                right_base = starting_emp
                # Apply chrome empathy cost
                right_current = right_base + chrome_empathy_cost
                # Check for additional drug modification
                emp_mod = getattr(target, 'emp_mod', None)
                if emp_mod is not None:
                    right_current += emp_mod
            else:
                right_base = getattr(target, right_attr, 0)
                right_current = getattr(target, right_attr, 0)
            left_str = stat_line(left_label, left_base, left_current)
            right_str = stat_line(right_label, right_base, right_current)
            stat_rows.append(f"{left_str:<30}{right_str}")
        stat_table = "\n".join(stat_rows) + "\n\n"

        # Chrome and Augmentations section
        chrome = getattr(target.db, 'installed_chrome', None)
        if chrome:
            # Section header
            chrome_block = "|[B|wChrome and Augmentations:|n\n"
            # Two-column layout: Chrome Name (yellow), Buff/Ability (green)
            name_label = "|yChrome Name:|n"
            buff_label = "    |GBuff/Ability:|n"
            name_val = f"|C{chrome.get('chrome_name', '')}|n"
            buff_val = f"{chrome.get('chrome_ability', '')}"
            # Pad columns for alignment
            chrome_block += f"{name_label:<18}{buff_label:<18}\n{name_val:<18}{'    ' + buff_val:<18}\n\n"
        else:
            chrome_block = "|RNo chrome or augmentations.|n\n\n"

        # No divider line between chrome and skills
        divider = ""

        # Skills table header with blue background, white underlined text

        # --- SKILL DEPENDENCIES ---
        SKILL_DEPENDENCIES = {
            "Chemical": {"stats": ["tech"], "split": [1.0]},
            "Modern Medicine": {"stats": ["smrt"], "split": [1.0]},
            "Holistic Medicine": {"stats": ["emp", "smrt"], "split": [0.5, 0.5]},
            "Surgery": {"stats": ["tech", "edge", "will"], "split": [0.33, 0.33, 0.34]},
            "Science": {"stats": ["smrt", "will"], "split": [0.5, 0.5]},
            "Dodge": {"stats": ["smrt", "dex"], "split": [0.5, 0.5]},
            "Blades": {
                "stats": ["dex", "will"], "split": [0.5, 0.5],
                "tertiary": {"stat": "smrt", "type": "parry", "bonus_per": 3, "max_bonus": 0.5, "max_stat": 20}
            },
            "Pistols": {
                "stats": ["smrt", "ref"], "split": [0.5, 0.5],
                "tertiary": {"stat": "edge", "type": "hit", "bonus_per": 3, "max_bonus": 0.25, "max_stat": 20}
            },
            "Rifles": {
                "stats": ["ref", "smrt", "will"], "split": [0.33, 0.33, 0.34],
                "tertiary": {"stat": "edge", "type": "damage", "bonus_per": 3, "max_bonus": 0.25, "max_stat": 20}
            },
            "Melee": {
                "stats": ["body", "dex"], "split": [0.5, 0.5],
                "tertiary": {"stat": "smrt", "type": "parry", "bonus_per": 3, "max_bonus": 0.5, "max_stat": 20}
            },
            "Brawling": {
                "stats": ["dex", "will"], "split": [0.5, 0.5],
                "tertiary": {"stat": "body", "type": "damage", "bonus_per": 0, "max_bonus": 0, "max_stat": 0}
            },
            "Martial Arts": {
                "stats": ["will", "dex"], "split": [0.5, 0.5],
                "tertiary": {"stat": "dex", "type": "damage", "bonus_per": 0, "max_bonus": 0, "max_stat": 0}
            },
            "Grappling": {"stats": ["body", "dex"], "split": [0.5, 0.5]},
            "Snooping": {"stats": ["ref", "smrt"], "split": [0.5, 0.5]},
            "Stealing": {"stats": ["ref", "edge"], "split": [0.5, 0.5]},
            "Hiding": {"stats": ["smrt", "edge"], "split": [0.5, 0.5]},
            "Sneaking": {"stats": ["dex", "edge", "smrt"], "split": [0.33, 0.33, 0.34]},
            "Disguise": {"stats": ["smrt", "edge"], "split": [0.5, 0.5]},
            "Tailoring": {"stats": ["smrt", "tech"], "split": [0.5, 0.5]},
            "Tinkering": {"stats": ["tech", "smrt"], "split": [0.5, 0.5]},
            "Manufacturing": {"stats": ["tech", "will"], "split": [0.5, 0.5]},
            "Cooking": {"stats": ["ref", "emp"], "split": [0.5, 0.5]},
            "Forensics": {"stats": ["smrt", "edge"], "split": [0.5, 0.5]},
            "Decking": {"stats": ["smrt", "tech"], "split": [0.5, 0.5]},
            "Electronics": {"stats": ["smrt", "tech"], "split": [0.5, 0.5]},
            "Mercantile": {"stats": ["edge", "smrt"], "split": [0.5, 0.5]},
            "Streetwise": {"stats": ["edge", "emp", "smrt"], "split": [0.33, 0.33, 0.34]},
            "Paint/Draw/Sculpt": {"stats": ["edge", "ref", "will"], "split": [0.33, 0.33, 0.34]},
            "Instrument": {"stats": ["edge", "ref", "will"], "split": [0.33, 0.33, 0.34]},
        }

        def calculate_skill_value(char, skill_name):
            dep = SKILL_DEPENDENCIES.get(skill_name)
            if not dep:
                return 0
            value = sum(getattr(char, stat, 0) * split for stat, split in zip(dep["stats"], dep["split"]))
            # Apply tertiary bonus if present
            if "tertiary" in dep:
                t = dep["tertiary"]
                stat_val = getattr(char, t["stat"], 0)
                if t["bonus_per"] > 0:
                    bonus_steps = max(0, min((stat_val - 10) // t["bonus_per"], t["max_stat"] // t["bonus_per"]))
                    bonus = (bonus_steps * t["max_bonus"])/(t["max_stat"] // t["bonus_per"])
                    value += value * bonus
            return int(round(value))

        # Skill display table
        skill_table = "|[b|w|uSkill                   Raw|n\n"
        for skill_name, dep in SKILL_DEPENDENCIES.items():
            raw_investment = getattr(target, skill_name.lower().replace("/", "_"), 0)
            skill_table += f"{skill_name:<18}{raw_investment:>8}\n"

        # Compose final output
        output = stat_table + chrome_block + divider + skill_table
        caller.msg(output)


class CmdLookPlace(Command):
    """
    Set your default room positioning description.
    
    Usage:
        @look_place <description>
        @look_place me is <description>
        @look_place me are <description>
        @look_place me is "<description>"
        @look_place is <description>
        @look_place are <description>
        @look_place "<description>"
        @look_place clear
    
    Examples:
        @look_place standing here.
        @look_place me is "sitting on a rock"
        @look_place me are "lounging lazily"
        @look_place me is "is lounging lazily"
        @look_place are crouched in the shadows
        @look_place clear
    
    This sets your default positioning that others see when they look at a room.
    Instead of appearing in a separate "Characters:" section, you'll appear naturally
    in the room description as "YourName is <your description>".
    
    Use 'clear' to remove your look_place and return to default display.
    """
    
    key = "look_place"
    aliases = ["lookplace"]
    locks = "cmd:all()"
    help_category = "Character"
    
    def func(self):
        """Execute the command."""
        caller = self.caller
        
        if not self.args:
            # Show current setting
            current = caller.look_place or "standing here."
            caller.msg(f"Your current look_place: '{current}'")
            return
        
        # Handle 'clear' command
        if self.args.strip().lower() in ('clear', 'none', 'remove'):
            caller.look_place = "standing here."
            caller.msg("Your look_place has been cleared and reset to 'standing here.'")
            return
        
        # Parse the description with smart 'is' handling
        description = self.parse_placement_description(self.args)
        
        if not description:
            caller.msg("Please provide a description for your look_place.")
            return
        
        # Check length limit to prevent abuse while allowing creativity
        if len(description) > 200:
            caller.msg(f"Your look_place description is too long ({len(description)} characters). Please keep it under 200 characters.")
            return
        
        # Ensure description ends with proper punctuation
        if not description.endswith(('.', '!', '?')):
            description += '.'
        
        # Set the look_place
        caller.look_place = description
        caller.msg(f"Your look_place is now: '{description}'")
        caller.msg("Others will see: '|c" + caller.get_display_name(caller) + f"|n is {description}'")
    
    def parse_placement_description(self, raw_input):
        """
        Parse various input formats to extract the placement description.
        
        Handles patterns like:
        - "standing here"
        - "me is standing here"  
        - "me is \"standing here\""
        - "is standing here"
        - "\"standing here\""
        - "me is \"is standing here\""
        
        Args:
            raw_input (str): The raw command arguments
            
        Returns:
            str: The cleaned placement description
        """
        text = raw_input.strip()
        
        # Remove outer quotes if present
        if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
            text = text[1:-1]
        
        # Handle "me is ..." pattern
        if text.lower().startswith('me is '):
            text = text[6:].strip()  # Remove "me is "
            
            # Remove inner quotes if present after "me is"
            if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
                text = text[1:-1]
        
        # Handle "is ..." pattern (without "me")
        elif text.lower().startswith('is '):
            text = text[3:].strip()  # Remove "is "
        
        # Clean up redundant "is" at the beginning
        # Handle cases like "me is \"is standing here\""
        if text.lower().startswith('is '):
            text = text[3:].strip()
        
        return text.strip()


class CmdTempPlace(Command):
    """
    Set a temporary room positioning description.
    
    Usage:
        @temp_place <description>
        @temp_place me is <description>
        @temp_place me are <description>
        @temp_place me is "<description>"
        @temp_place is <description>
        @temp_place are <description>
        @temp_place "<description>"
        @temp_place clear
    
    Examples:
        @temp_place hiding behind a tree.
        @temp_place me is "examining the wall closely"
        @temp_place me are "investigating something"
        @temp_place me is "is investigating something"
        @temp_place are crouched and ready to spring
        @temp_place clear
    
    This sets a temporary positioning that overrides your @look_place.
    It will be automatically cleared when you move to a different room.
    
    Use 'clear' to remove your temp_place immediately.
    """
    
    key = "temp_place"
    aliases = ["@tempplace"]
    locks = "cmd:all()"
    help_category = "Character"
    
    def func(self):
        """Execute the command."""
        caller = self.caller
        
        if not self.args:
            # Show current setting
            current = caller.temp_place or ""
            if current:
                caller.msg(f"Your current temp_place: '{current}'")
            else:
                caller.msg("You have no temp_place set.")
            return
        
        # Handle 'clear' command
        if self.args.strip().lower() in ('clear', 'none', 'remove'):
            caller.temp_place = ""
            caller.msg("Your temp_place has been cleared.")
            return
        
        # Parse the description with smart 'is' handling
        description = self.parse_placement_description(self.args)
        
        if not description:
            caller.msg("Please provide a description for your temp_place.")
            return
        
        # Check length limit to prevent abuse while allowing creativity
        if len(description) > 200:
            caller.msg(f"Your temp_place description is too long ({len(description)} characters). Please keep it under 200 characters.")
            return
        
        # Ensure description ends with proper punctuation
        if not description.endswith(('.', '!', '?')):
            description += '.'
            description += '.'
        
        # Set the temp_place
        caller.temp_place = description
        caller.msg(f"Your temp_place is now: '{description}'")
        caller.msg("Others will see: '|c" + caller.get_display_name(caller) + f"|n is {description}'")
        caller.msg("This will be cleared when you move to a different room.")
    
    def parse_placement_description(self, raw_input):
        """
        Parse various input formats to extract the placement description.
        
        Same logic as CmdLookPlace for consistency.
        """
        text = raw_input.strip()
        
        # Remove outer quotes if present
        if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
            text = text[1:-1]
        
        # Handle "me is ..." pattern
        if text.lower().startswith('me is '):
            text = text[6:].strip()  # Remove "me is "
            
            # Remove inner quotes if present after "me is"
            if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
                text = text[1:-1]
        
        # Handle "is ..." pattern (without "me")
        elif text.lower().startswith('is '):
            text = text[3:].strip()  # Remove "is "
        
        # Clean up redundant "is" at the beginning
        # Handle cases like "me is \"is standing here\""
        if text.lower().startswith('is '):
            text = text[3:].strip()
        
        return text.strip()


class CmdLongdesc(Command):
    """
    Set or view detailed descriptions for your character's body parts.

    Usage:
        @longdesc <location> "<description>"    - Set description for a body part
        @longdesc <location>                    - View current description for location
        @longdesc                               - List all your current longdescs
        @longdesc/list                          - List all available body locations
        @longdesc/clear <location>              - Remove description for location

    Staff Usage:
        @longdesc <character> <location> "<description>"  - Set on another character
        @longdesc/clear <character> <location>             - Clear on another character

    Examples:
        @longdesc face "weathered features with high cheekbones"
        @longdesc left_eye "a piercing blue eye with flecks of gold"
        @longdesc right_hand "a prosthetic metal hand with intricate engravings"
        @longdesc/clear face
        @longdesc face
        @longdesc/list

    Body locations include: head, face, left_eye, right_eye, left_ear, right_ear,
    neck, chest, back, abdomen, groin, left_arm, right_arm, left_hand, right_hand,
    left_thigh, right_thigh, left_shin, right_shin, left_foot, right_foot.

    Extended anatomy (tails, wings, etc.) is supported for modified characters.
    Descriptions appear when others look at you, integrated with your base description.
    """

    key = "longdesc"
    aliases = []
    locks = "cmd:all()"
    help_category = "Character"

    def func(self):
        """Execute the longdesc command."""
        caller = self.caller
        raw_args = self.args.strip()
        
        # Parse switches manually since we're not using MuxCommand
        switches = []
        args = raw_args
        
        if raw_args.startswith('/'):
            # Find the end of switches
            parts = raw_args[1:].split(None, 1)
            if parts:
                switch_part = parts[0]
                args = parts[1] if len(parts) > 1 else ""
                switches = [s.lower() for s in switch_part.split('/') if s]

        # Handle switches
        if "list" in switches:
            self._handle_list_locations(caller)
            return

        if "clear" in switches:
            self._handle_clear(caller, args)
            return

        # Parse arguments for main command
        if not args:
            # Show all current longdescs
            self._show_all_longdescs(caller)
            return

        # Check if this is staff targeting another character
        target_char = None
        remaining_args = args

        if caller.locks.check_lockstring(caller, f"dummy:perm({PERM_BUILDER}) or perm_above({PERM_BUILDER})"):
            # Staff can target other characters
            parts = args.split(None, 1)
            if len(parts) >= 1:
                # Try different search approaches
                potential_target = caller.search(parts[0], global_search=True, quiet=True)
                
                if not potential_target:
                    # Try searching without global_search
                    potential_target = caller.search(parts[0], quiet=True)
                
                if not potential_target:
                    # Try searching in the same location as the caller
                    if caller.location:
                        potential_target = caller.location.search(parts[0], quiet=True)
                        
                        # If not found in location, try searching the location's contents more broadly
                        if not potential_target:
                            for obj in caller.location.contents:
                                if obj.key.lower() == parts[0].lower():
                                    potential_target = obj
                                    break
                
                if potential_target:
                    # If it's a list, get the first item
                    if isinstance(potential_target, list):
                        if potential_target:
                            actual_target = potential_target[0]
                        else:
                            actual_target = None
                    else:
                        actual_target = potential_target
                    
                    if actual_target and hasattr(actual_target, 'nakeds'):
                        target_char = actual_target
                        remaining_args = parts[1] if len(parts) > 1 else ""

        if not target_char:
            target_char = caller
            remaining_args = args

        # Parse location and description
        if '"' in remaining_args:
            # Setting a description
            if remaining_args.count('"') < 2:
                caller.msg("Please enclose the description in quotes.")
                return

            quote_start = remaining_args.find('"')
            quote_end = remaining_args.rfind('"')

            if quote_start == quote_end:
                caller.msg("Please provide both opening and closing quotes.")
                return

            location = remaining_args[:quote_start].strip()
            description = remaining_args[quote_start + 1:quote_end]

            self._set_longdesc(caller, target_char, location, description)

        else:
            # Viewing a specific location
            location = remaining_args.strip()
            if location:
                self._view_longdesc(caller, target_char, location)
            else:
                self._show_all_longdescs(caller, target_char)

    def _handle_list_locations(self, caller):
        """Show all available body locations for the character."""
        locations = caller.get_available_locations()
        if not locations:
            caller.msg("No body locations available.")
            return

        # Group locations by type for better display
        from world.combat.constants import ANATOMICAL_REGIONS

        grouped_locations = {}
        extended_locations = []

        for location in locations:
            found_region = None
            for region_name, region_locations in ANATOMICAL_REGIONS.items():
                if location in region_locations:
                    if region_name not in grouped_locations:
                        grouped_locations[region_name] = []
                    grouped_locations[region_name].append(location)
                    found_region = True
                    break
            
            if not found_region:
                extended_locations.append(location)

        # Display grouped locations
        caller.msg("|wAvailable body locations:|n")
        
        region_display_names = {
            "head_region": "Head Region",
            "torso_region": "Torso Region", 
            "arm_region": "Arm Region",
            "leg_region": "Leg Region"
        }

        for region_name in ["head_region", "torso_region", "arm_region", "leg_region"]:
            if region_name in grouped_locations:
                display_name = region_display_names[region_name]
                locations_list = ", ".join(grouped_locations[region_name])
                caller.msg(f"  |c{display_name}:|n {locations_list}")

        if extended_locations:
            caller.msg(f"  |cExtended Anatomy:|n {', '.join(extended_locations)}")

    def _handle_clear(self, caller, args):
        """Handle clear commands."""
        if not args:
            # Clear all longdescs with confirmation
            self._clear_all_longdescs(caller)
            return

        # Check if targeting another character (staff only)
        target_char = None
        location = args

        if caller.locks.check_lockstring(caller, f"dummy:perm({PERM_BUILDER}) or perm_above({PERM_BUILDER})"):
            parts = args.split(None, 1)
            if len(parts) >= 1:
                # Use quiet=True to prevent "Could not find" messages
                potential_target = caller.search(parts[0], global_search=True, quiet=True)
                if potential_target and hasattr(potential_target, 'nakeds'):
                    target_char = potential_target
                    location = parts[1] if len(parts) > 1 else ""

        if not target_char:
            target_char = caller
            location = args

        if not location:
            # Clear all for target character
            self._clear_all_longdescs(caller, target_char)
        else:
            # Clear specific location
            self._clear_specific_location(caller, target_char, location)

    def _set_longdesc(self, caller, target_char, location, description):
        """Set a longdesc for a specific location."""
        if not location:
            caller.msg("Please specify a body location.")
            return

        # Validate location exists on character
        if not target_char.has_location(location):
            caller.msg(f"'{location}' is not a valid body location for {target_char.get_display_name(caller)}.")
            available = ", ".join(target_char.get_available_locations()[:10])  # Show first 10
            caller.msg(f"Available locations include: {available}...")
            caller.msg("Use 'longdesc/list' to see all available locations.")
            return

        # Validate description length
        if len(description) > MAX_DESCRIPTION_LENGTH:
            caller.msg(f"Description is too long ({len(description)} characters). Maximum is {MAX_DESCRIPTION_LENGTH} characters.")
            return

        if len(description.strip()) == 0:
            # Empty description means clear
            target_char.set_longdesc(location, None)
            if target_char == caller:
                caller.msg(f"Cleared description for {location}.")
            else:
                caller.msg(f"Cleared description for {location} on {target_char.get_display_name(caller)}.")
            return

        # Set the description
        success = target_char.set_longdesc(location, description.strip())
        if success:
            if target_char == caller:
                caller.msg(f"Set description for {location}: \"{description.strip()}\"")
            else:
                caller.msg(f"Set description for {location} on {target_char.get_display_name(caller)}: \"{description.strip()}\"")
        else:
            caller.msg("Failed to set description. Please try again.")

    def _view_longdesc(self, caller, target_char, location):
        """View a specific longdesc."""
        if not target_char.has_location(location):
            caller.msg(f"'{location}' is not a valid body location.")
            return

        description = target_char.get_longdesc(location)
        if description:
            if target_char == caller:
                caller.msg(f"{location}: \"{description}\"")
            else:
                caller.msg(f"{target_char.get_display_name(caller)}'s {location}: \"{description}\"")
        else:
            if target_char == caller:
                caller.msg(f"No description set for {location}.")
            else:
                caller.msg(f"No description set for {location} on {target_char.get_display_name(caller)}.")

    def _show_all_longdescs(self, caller, target_char=None):
        """Show all current longdescs for a character."""
        if not target_char:
            target_char = caller

        nakeds = target_char.nakeds or {}
        set_descriptions = {loc: desc for loc, desc in nakeds.items() if desc}

        if not set_descriptions:
            if target_char == caller:
                caller.msg("You have no longdesc descriptions set.")
            else:
                caller.msg(f"{target_char.get_display_name(caller)} has no longdesc descriptions set.")
            return

        if target_char == caller:
            caller.msg("|wYour current longdesc descriptions:|n")
        else:
            caller.msg(f"|w{target_char.get_display_name(caller)}'s longdesc descriptions:|n")

        # Show in anatomical order
        from world.combat.constants import ANATOMICAL_DISPLAY_ORDER

        displayed = set()
        for location in ANATOMICAL_DISPLAY_ORDER:
            if location in set_descriptions:
                caller.msg(f"  |c{location}:|n \"{set_descriptions[location]}\"")
                displayed.add(location)

        # Show any extended anatomy
        for location, description in set_descriptions.items():
            if location not in displayed:
                caller.msg(f"  |c{location}:|n \"{description}\"")

    def _clear_specific_location(self, caller, target_char, location):
        """Clear a specific location's longdesc."""
        if not target_char.has_location(location):
            caller.msg(f"'{location}' is not a valid body location.")
            return

        current_desc = target_char.get_longdesc(location)
        if not current_desc:
            if target_char == caller:
                caller.msg(f"No description set for {location}.")
            else:
                caller.msg(f"No description set for {location} on {target_char.get_display_name(caller)}.")
            return

        target_char.set_longdesc(location, None)
        if target_char == caller:
            caller.msg(f"Cleared description for {location}.")
        else:
            caller.msg(f"Cleared description for {location} on {target_char.get_display_name(caller)}.")

    def _clear_all_longdescs(self, caller, target_char=None):
        """Clear all longdescs with confirmation."""
        if not target_char:
            target_char = caller

        nakeds = target_char.nakeds or {}
        set_descriptions = {loc: desc for loc, desc in nakeds.items() if desc}

        if not set_descriptions:
            if target_char == caller:
                caller.msg("You have no longdesc descriptions to clear.")
            else:
                caller.msg(f"{target_char.get_display_name(caller)} has no longdesc descriptions to clear.")
            return

        # Simple confirmation - clear all
        for location in set_descriptions:
            target_char.set_longdesc(location, None)

        count = len(set_descriptions)
        if target_char == caller:
            caller.msg(f"Cleared all {count} longdesc descriptions.")
        else:
            caller.msg(f"Cleared all {count} longdesc descriptions from {target_char.get_display_name(caller)}.")


class CmdSkintone(Command):
    """
    Set your character's skintone for longdesc display coloring.

    Usage:
      skintone <tone>
      skintone list
      skintone clear
      skintone <character> <tone>    (staff only)
      skintone <character> clear     (staff only)

    Sets the color tone used for your character's longdesc descriptions.
    This creates visual distinction between your character's body/skin
    descriptions and clothing descriptions.

    Available tones: porcelain, pale, fair, light, medium, olive, tan, brown, dark, deep

    Examples:
      skintone tan
      skintone list
      skintone clear
    """
    
    key = "skintone"
    aliases = ["skintone"]
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        args = self.args.strip()
        
        if not args:
            self._show_current_skintone(caller)
            return
            
        # Handle list command
        if args.lower() == "list":
            self._show_available_tones(caller)
            return
            
        # Handle clear command
        if args.lower() == "clear":
            self._clear_skintone(caller, caller)
            return
            
        # Check if this might be staff targeting another character
        parts = args.split()
        if len(parts) == 2 and caller.locks.check_lockstring(caller, "perm(Builder)"):
            character_name, tone_or_clear = parts
            target = self._find_character(caller, character_name)
            if target:
                if tone_or_clear.lower() == "clear":
                    self._clear_skintone(caller, target)
                else:
                    self._set_skintone(caller, target, tone_or_clear.lower())
                return
            else:
                caller.msg(f"Could not find character '{character_name}'.")
                return
        
        # Single argument - set skintone on self
        tone = args.lower()
        self._set_skintone(caller, caller, tone)

    def _show_current_skintone(self, caller):
        """Show the caller's current skintone setting"""
        skintone = getattr(caller.db, 'skintone', None)
        if skintone:
            color_code = SKINTONE_PALETTE.get(skintone, "")
            if color_code:
                colored_skintone = f"{color_code}{skintone}|n"
                caller.msg(f"Your current skintone is: {colored_skintone}")
            else:
                caller.msg(f"Your current skintone is: {skintone} (invalid)")
        else:
            caller.msg("You have no skintone set. Longdescs will appear uncolored.")
            
    def _show_available_tones(self, caller):
        """Display available skintones with previews"""
        caller.msg("|wAvailable Skintones:|n")
        caller.msg("")
        
        # All tones in order
        all_tones = ["porcelain", "pale", "fair", "light", "golden", "tan", "olive", "brown", "rich"]
        for tone in all_tones:
            color_code = SKINTONE_PALETTE[tone]
            caller.msg("  " + tone.ljust(10) + " - " + f"{color_code}Sample text|n")
            
        caller.msg("")
        caller.msg("Use: |wskintone <tone>|n to set your skintone")
        caller.msg("Use: |wskintone clear|n to remove coloring")

    def _set_skintone(self, caller, target, tone):
        """Set skintone on target character"""
        if tone not in VALID_SKINTONES:
            caller.msg(f"'{tone}' is not a valid skintone. Use 'skintone list' to see available options.")
            return
            
        target.db.skintone = tone
        color_code = SKINTONE_PALETTE[tone]
        colored_tone = color_code + tone + "|n"
        
        if target == caller:
            caller.msg(f"Set your skintone to: {colored_tone}")
        else:
            caller.msg(f"Set {target.name}'s skintone to: {colored_tone}")
            target.msg(f"{caller.name} has set your skintone to: {colored_tone}")

    def _clear_skintone(self, caller, target):
        """Clear skintone from target character"""
        if hasattr(target.db, 'skintone'):
            del target.db.skintone
            
        if target == caller:
            caller.msg("Cleared your skintone. Longdescs will appear uncolored.")
        else:
            caller.msg(f"Cleared {target.name}'s skintone.")
            target.msg(f"{caller.name} has cleared your skintone setting.")

    def _find_character(self, caller, character_name):
        """Find a character by name for staff targeting"""
        # Use Evennia's search system to find the character
        results = search_object(character_name, typeclass="typeclasses.characters.Character")
        
        if not results:
            return None
        elif len(results) > 1:
            # Multiple matches - try to find exact match
            exact_matches = [obj for obj in results if obj.name.lower() == character_name.lower()]
            if len(exact_matches) == 1:
                return exact_matches[0]
            else:
                caller.msg(f"Multiple characters match '{character_name}': {', '.join(obj.name for obj in results)}")
                return None
        else:
            return results[0]


class CmdSetStat(Command):
    """
    Set a character's stat manually (Builder+ only).

    Usage:
        setstat <stat> <value> [target]

    Example:
        setstat body 10
        setstat smrt 15 Laszlo
    """
    key = "setstat"
    locks = "cmd:perm(Builder)"
    help_category = "Admin"

    def func(self):
        caller = self.caller
        args = self.args.strip().split()
        if len(args) < 2:
            caller.msg("Usage: setstat <stat> <value> [target]")
            return
        stat = args[0].lower()
        value = args[1]
        target = caller
        # Support both: setstat <stat> <value> <target> and setstat <target> <stat> <value>
        if len(args) > 2:
            # Try to find target by first or last argument
            possible_target = args[2]
            matches = search_object(possible_target, exact=False)
            if not matches and len(args) > 3:
                matches = search_object(args[0], exact=False)
                if matches:
                    stat = args[1].lower()
                    value = args[2]
            if matches:
                target = matches[0]
        valid_stats = ["body", "ref", "dex", "tech", "smrt", "will", "edge", "emp"]
        if stat not in valid_stats:
            caller.msg(f"Invalid stat. Valid stats: {', '.join(valid_stats)}")
            return
        try:
            value = int(value)
        except ValueError:
            caller.msg("Value must be an integer.")
            return
        setattr(target, stat, value)
        caller.msg(f"Set {target.key}'s {stat.upper()} to {value}.")
        if target != caller:
            target.msg(f"Your {stat.upper()} was set to {value} by {caller.key}.")
