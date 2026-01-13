"""
Builder Creation Menus - EvMenu-based interfaces for builders to create items

Provides interactive menus for:
- Creating furniture designs
- Creating NPC templates
- Creating weapon templates
- Creating clothing/armor items
- Managing factions
"""

from evennia.utils.evmenu import EvMenu
from evennia import Command
from world.builder_storage import (
    add_furniture, add_npc, add_weapon, add_clothing_item,
    add_faction, get_all_factions, get_builder_storage,
    initialize_default_factions
)


class BuilderMenuMixin:
    """Mixin providing common menu utilities."""
    
    @staticmethod
    def format_header(title):
        """Format a menu header."""
        return f"|c{title:^78}|n\n" + "-" * 78


class FurnitureMenu(EvMenu):
    """Menu for creating furniture designs."""
    
    def options_formatter(self, optionlist):
        """Suppress automatic option display."""
        return ""


def furniture_start(caller, raw_string, **kwargs):
    """Start furniture creation menu."""
    caller.ndb._furniture_data = {
        "name": "",
        "desc": "",
        "movable": True,
        "max_seats": 0,
        "can_recline": False,
        "can_lie_down": False,
        "sit_msg_first": "",
        "sit_msg_third": "",
        "lie_msg_first": "",
        "lie_msg_third": "",
        "recline_msg_first": "",
        "recline_msg_third": "",
    }
    
    return furniture_name(caller, "", **kwargs)


def furniture_name(caller, raw_string, **kwargs):
    """Get furniture name using proper EvMenu pattern."""
    # Input mode - process user's text
    if raw_string and raw_string.strip():
        name = raw_string.strip()
        
        # Validate
        if len(name) < 2:
            caller.msg("|rName must be at least 2 characters.|n")
            return furniture_name(caller, "", **kwargs)  # Re-display this node
        
        if len(name) > 50:
            caller.msg("|rName must be 50 characters or less.|n")
            return furniture_name(caller, "", **kwargs)  # Re-display this node
        
        # Store and advance
        caller.ndb._furniture_data["name"] = name
        return furniture_desc(caller, "", **kwargs)
    
    # Display mode - show prompt
    text = BuilderMenuMixin.format_header("FURNITURE DESIGNER - STEP 1: NAME")
    text += "\nEnter the furniture name (e.g., 'Oak Table', 'Red Couch'):\n"
    
    options = (
        {"key": "_default", "goto": "furniture_name"},
    )
    return text, options


def furniture_desc(caller, raw_string, **kwargs):
    """Get furniture description using proper EvMenu pattern."""
    # Input mode - process user's text
    if raw_string and raw_string.strip():
        desc = raw_string.strip()
        
        # Validate
        if len(desc) < 5:
            caller.msg("|rDescription must be at least 5 characters.|n")
            return furniture_desc(caller, "", **kwargs)  # Re-display this node
        
        if len(desc) > 500:
            caller.msg("|rDescription must be 500 characters or less.|n")
            return furniture_desc(caller, "", **kwargs)  # Re-display this node
        
        # Store and advance
        caller.ndb._furniture_data["desc"] = desc
        return furniture_properties(caller, "", **kwargs)
    
    # Display mode - show prompt
    text = BuilderMenuMixin.format_header("FURNITURE DESIGNER - STEP 2: DESCRIPTION")
    text += f"\nFurniture: {caller.ndb._furniture_data['name']}\n"
    text += "\nEnter the furniture description (what players see when they look):\n"
    
    options = (
        {"key": "_default", "goto": "furniture_desc"},
    )
    return text, options


def furniture_properties(caller, raw_string, **kwargs):
    """Configure furniture properties."""
    # Input mode - process user's choice
    if raw_string and raw_string.strip():
        choice = raw_string.strip().lower()
        
        if choice == "1":
            caller.ndb._furniture_data["movable"] = not caller.ndb._furniture_data["movable"]
            return furniture_properties(caller, "", **kwargs)  # Re-display with updated value
        elif choice == "2":
            return furniture_seats(caller, "", **kwargs)
        elif choice == "3":
            caller.ndb._furniture_data["can_recline"] = not caller.ndb._furniture_data["can_recline"]
            return furniture_properties(caller, "", **kwargs)  # Re-display with updated value
        elif choice == "4":
            caller.ndb._furniture_data["can_lie_down"] = not caller.ndb._furniture_data["can_lie_down"]
            return furniture_properties(caller, "", **kwargs)  # Re-display with updated value
        elif choice == "5":
            return furniture_messages(caller, "", **kwargs)
        elif choice in ["s", "save"]:
            return furniture_save(caller, "", **kwargs)
        elif choice in ["q", "quit", "cancel"]:
            return furniture_cancel(caller, "", **kwargs)
        else:
            caller.msg("|rInvalid choice.|n")
            return furniture_properties(caller, "", **kwargs)
    
    # Display mode - show menu
    text = BuilderMenuMixin.format_header("FURNITURE DESIGNER - STEP 3: PROPERTIES")
    text += f"\nFurniture: {caller.ndb._furniture_data['name']}\n\n"
    text += "|y1|n - Movable: " + ("Yes" if caller.ndb._furniture_data["movable"] else "No") + "\n"
    text += "|y2|n - Max Seats: " + str(caller.ndb._furniture_data["max_seats"]) + "\n"
    text += "|y3|n - Can Recline: " + ("Yes" if caller.ndb._furniture_data["can_recline"] else "No") + "\n"
    text += "|y4|n - Can Lie Down: " + ("Yes" if caller.ndb._furniture_data["can_lie_down"] else "No") + "\n"
    text += "|y5|n - Continue to Messages\n"
    text += "|ys|n - Save\n"
    text += "|yq|n - Cancel\n"
    
    options = (
        {"key": "_default", "goto": "furniture_properties"},
    )
    return text, options


def furniture_seats(caller, raw_string, **kwargs):
    """Set max seats using proper EvMenu pattern."""
    # Input mode - process user's input
    if raw_string and raw_string.strip():
        try:
            seats = int(raw_string.strip())
            if 0 <= seats <= 10:
                caller.ndb._furniture_data["max_seats"] = seats
                return furniture_properties(caller, "", **kwargs)
            else:
                caller.msg("|rSeats must be between 0 and 10.|n")
                return furniture_seats(caller, "", **kwargs)  # Re-display
        except ValueError:
            caller.msg("|rPlease enter a valid number.|n")
            return furniture_seats(caller, "", **kwargs)  # Re-display
    
    # Display mode - show prompt
    text = BuilderMenuMixin.format_header("FURNITURE DESIGNER - MAX SEATS")
    text += f"\nFurniture: {caller.ndb._furniture_data['name']}\n"
    text += "\nHow many people can sit on this furniture? (0-10):\n"
    
    options = (
        {"key": "_default", "goto": "furniture_seats"},
    )
    return text, options


def furniture_messages(caller, raw_string, **kwargs):
    """Configure furniture messages."""
    # Input mode - process user's choice
    if raw_string and raw_string.strip():
        choice = raw_string.strip().lower()
        
        if choice == "q":
            return furniture_cancel(caller, "", **kwargs)
        elif choice == "s":
            return furniture_save(caller, "", **kwargs)
        elif choice == "1" and caller.ndb._furniture_data["max_seats"] > 0:
            caller.ndb._editing_msg_type = "sit_msg_first"
            return furniture_msg_input(caller, "", **kwargs)
        elif choice == "2" and caller.ndb._furniture_data["max_seats"] > 0:
            caller.ndb._editing_msg_type = "sit_msg_third"
            return furniture_msg_input(caller, "", **kwargs)
        elif choice == "3" and caller.ndb._furniture_data["can_lie_down"]:
            caller.ndb._editing_msg_type = "lie_msg_first"
            return furniture_msg_input(caller, "", **kwargs)
        elif choice == "4" and caller.ndb._furniture_data["can_lie_down"]:
            caller.ndb._editing_msg_type = "lie_msg_third"
            return furniture_msg_input(caller, "", **kwargs)
        elif choice == "5" and caller.ndb._furniture_data["can_recline"]:
            caller.ndb._editing_msg_type = "recline_msg_first"
            return furniture_msg_input(caller, "", **kwargs)
        elif choice == "6" and caller.ndb._furniture_data["can_recline"]:
            caller.ndb._editing_msg_type = "recline_msg_third"
            return furniture_msg_input(caller, "", **kwargs)
        else:
            caller.msg("|rInvalid choice.|n")
            return furniture_messages(caller, "", **kwargs)
    
    # Display mode - show menu
    text = BuilderMenuMixin.format_header("FURNITURE DESIGNER - MESSAGES")
    text += f"\nFurniture: {caller.ndb._furniture_data['name']}\n\n"
    text += "Configure messages for when players interact with this furniture.\n"
    text += "These can use {target_name} placeholder for the furniture.\n\n"
    
    if caller.ndb._furniture_data["max_seats"] > 0:
        text += "|y1|n - Sitting (1st person): " + (caller.ndb._furniture_data["sit_msg_first"][:30] + "..." if caller.ndb._furniture_data["sit_msg_first"] else "(not set)") + "\n"
        text += "|y2|n - Sitting (3rd person): " + (caller.ndb._furniture_data["sit_msg_third"][:30] + "..." if caller.ndb._furniture_data["sit_msg_third"] else "(not set)") + "\n"
    
    if caller.ndb._furniture_data["can_lie_down"]:
        text += "|y3|n - Lying Down (1st person): " + (caller.ndb._furniture_data["lie_msg_first"][:30] + "..." if caller.ndb._furniture_data["lie_msg_first"] else "(not set)") + "\n"
        text += "|y4|n - Lying Down (3rd person): " + (caller.ndb._furniture_data["lie_msg_third"][:30] + "..." if caller.ndb._furniture_data["lie_msg_third"] else "(not set)") + "\n"
    
    if caller.ndb._furniture_data["can_recline"]:
        text += "|y5|n - Reclining (1st person): " + (caller.ndb._furniture_data["recline_msg_first"][:30] + "..." if caller.ndb._furniture_data["recline_msg_first"] else "(not set)") + "\n"
        text += "|y6|n - Reclining (3rd person): " + (caller.ndb._furniture_data["recline_msg_third"][:30] + "..." if caller.ndb._furniture_data["recline_msg_third"] else "(not set)") + "\n"
    
    text += "|ys|n - Finish and Save\n"
    text += "|yq|n - Cancel\n"
    
    options = (
        {"key": "_default", "goto": "furniture_messages"},
    )
    return text, options


def furniture_msg_input(caller, raw_string, **kwargs):
    """Get custom furniture message using proper EvMenu pattern."""
    msg_type = getattr(caller.ndb, '_editing_msg_type', None)
    if not msg_type:
        return furniture_messages(caller, "", **kwargs)
    
    # Input mode - process user's text
    if raw_string and raw_string.strip():
        caller.ndb._furniture_data[msg_type] = raw_string.strip()
        if hasattr(caller.ndb, '_editing_msg_type'):
            delattr(caller.ndb, '_editing_msg_type')
        return furniture_messages(caller, "", **kwargs)
    
    # Display mode - show prompt
    text = BuilderMenuMixin.format_header("FURNITURE DESIGNER - CUSTOM MESSAGE")
    text += f"\nFurniture: {caller.ndb._furniture_data['name']}\n"
    text += f"Message Type: {msg_type.replace('_', ' ').title()}\n\n"
    text += "Enter the message (use {name} for player name, {furniture} for furniture name):\n"
    text += "Examples:\n"
    text += "  1st person: 'You settle into the comfortable cushions of the {furniture}.'\n"
    text += "  3rd person: '{name} sits down on the {furniture}.'\n\n"
    
    options = (
        {"key": "_default", "goto": "furniture_msg_input"},
    )
    return text, options


def furniture_save(caller, raw_string, **kwargs):
    """Save furniture design."""
    data = caller.ndb._furniture_data
    furniture = add_furniture(
        name=data["name"],
        desc=data["desc"],
        movable=data["movable"],
        max_seats=data["max_seats"],
        can_recline=data["can_recline"],
        can_lie_down=data["can_lie_down"],
        sit_msg_first=data["sit_msg_first"],
        sit_msg_third=data["sit_msg_third"],
        lie_msg_first=data["lie_msg_first"],
        lie_msg_third=data["lie_msg_third"],
        recline_msg_first=data["recline_msg_first"],
        recline_msg_third=data["recline_msg_third"],
        created_by=caller.key
    )
    
    text = BuilderMenuMixin.format_header("SUCCESS")
    text += f"\nFurniture saved!\n"
    text += f"Name: {furniture['name']}\n"
    text += f"ID: {furniture['id']}\n\n"
    text += "You can now spawn it using: |yspawnfurniture {furniture['id']}|n\n"
    
    # Clean up
    if hasattr(caller.ndb, '_furniture_data'):
        delattr(caller.ndb, '_furniture_data')
    
    caller.msg(text)
    return None  # Exit menu


def furniture_cancel(caller, raw_string, **kwargs):
    """Cancel furniture creation."""
    if hasattr(caller.ndb, '_furniture_data'):
        delattr(caller.ndb, '_furniture_data')
    
    caller.msg("|rCancelled.|n")
    return None  # Exit menu


# ============================================================================
# NPC MENU
# ============================================================================

def npc_start(caller, raw_string, **kwargs):
    """Start NPC creation menu."""
    initialize_default_factions()
    
    caller.ndb._npc_data = {
        "name": "",
        "desc": "",
        "lookplace": "",
        "faction": "neutral",
        "wandering_zone": "",
        "is_shopkeeper": False,
        "primary_language": "cantonese",
        "known_languages": ["cantonese"],
        "stats": {
            "body": 1,
            "ref": 1,
            "dex": 1,
            "tech": 1,
            "smrt": 1,
            "will": 1,
            "edge": 1,
        },
        "skills": {
            "chemical": 0,
            "modern_medicine": 0,
            "holistic_medicine": 0,
            "surgery": 0,
            "science": 0,
            "dodge": 0,
            "blades": 0,
            "pistols": 0,
            "rifles": 0,
            "melee": 0,
            "brawling": 0,
            "martial_arts": 0,
            "grappling": 0,
            "snooping": 0,
            "stealing": 0,
            "hiding": 0,
            "sneaking": 0,
            "disguise": 0,
            "tailoring": 0,
            "tinkering": 0,
            "manufacturing": 0,
            "cooking": 0,
            "forensics": 0,
            "decking": 0,
            "electronics": 0,
            "mercantile": 0,
            "streetwise": 0,
            "paint_draw_sculpt": 0,
            "instrument": 0,
        },
    }
    
    return npc_name(caller, "", **kwargs)


def npc_name(caller, raw_string, **kwargs):
    """Get NPC name using proper EvMenu pattern."""
    # Input mode - process user's text
    if raw_string and raw_string.strip():
        name = raw_string.strip()
        
        # Validate
        if len(name) < 2:
            caller.msg("|rName must be at least 2 characters.|n")
            return npc_name(caller, "", **kwargs)  # Re-display this node
        
        if len(name) > 50:
            caller.msg("|rName must be 50 characters or less.|n")
            return npc_name(caller, "", **kwargs)  # Re-display this node
        
        # Store and advance
        caller.ndb._npc_data["name"] = name
        return npc_desc(caller, "", **kwargs)
    
    # Display mode - show prompt
    text = BuilderMenuMixin.format_header("NPC DESIGNER - STEP 1: NAME")
    text += "\nEnter the NPC name (e.g., 'Old Street Vendor', 'Gang Member'):\n"
    
    options = (
        {"key": "_default", "goto": "npc_name"},
    )
    return text, options


def npc_desc(caller, raw_string, **kwargs):
    """Get NPC description using proper EvMenu pattern."""
    # Input mode - process user's text
    if raw_string and raw_string.strip():
        desc = raw_string.strip()
        
        # Validate
        if len(desc) < 5:
            caller.msg("|rDescription must be at least 5 characters.|n")
            return npc_desc(caller, "", **kwargs)  # Re-display this node
        
        if len(desc) > 500:
            caller.msg("|rDescription must be 500 characters or less.|n")
            return npc_desc(caller, "", **kwargs)  # Re-display this node
        
        # Store and advance
        caller.ndb._npc_data["desc"] = desc
        return npc_properties(caller, "", **kwargs)
    
    # Display mode - show prompt
    text = BuilderMenuMixin.format_header("NPC DESIGNER - STEP 2: DESCRIPTION")
    text += f"\nNPC: {caller.ndb._npc_data['name']}\n"
    text += "\nEnter the NPC description:\n"
    
    options = (
        {"key": "_default", "goto": "npc_desc"},
    )
    return text, options


def npc_properties(caller, raw_string, **kwargs):
    """Configure NPC properties."""
    # Input mode - process user's choice
    if raw_string and raw_string.strip():
        choice = raw_string.strip().lower()
        
        if choice == "1":
            return npc_faction(caller, "", **kwargs)
        elif choice == "2":
            return npc_wandering(caller, "", **kwargs)
        elif choice == "3":
            return npc_set_lookplace(caller, "", **kwargs)
        elif choice == "4":
            caller.ndb._npc_data["is_shopkeeper"] = not caller.ndb._npc_data["is_shopkeeper"]
            return npc_properties(caller, "", **kwargs)  # Re-display with updated value
        elif choice == "5":
            return npc_languages(caller, "", **kwargs)
        elif choice == "6":
            return npc_stats_menu(caller, "", **kwargs)
        elif choice == "7":
            return npc_skills_menu(caller, "", **kwargs)
        elif choice in ["s", "save"]:
            return npc_save(caller, "", **kwargs)
        elif choice in ["q", "quit", "cancel"]:
            return npc_cancel(caller, "", **kwargs)
        else:
            caller.msg("|rInvalid choice. Please enter 1-7, s, or q.|n")
            return npc_properties(caller, "", **kwargs)  # Re-display menu
    
    # Display mode - show menu
    text = BuilderMenuMixin.format_header("NPC DESIGNER - PROPERTIES")
    text += f"\nNPC: {caller.ndb._npc_data['name']}\n\n"
    text += "|y1|n - Faction: " + caller.ndb._npc_data["faction"] + "\n"
    text += "|y2|n - Wandering Zone: " + (caller.ndb._npc_data["wandering_zone"] or "(none - static)") + "\n"
    text += "|y3|n - Look Place: " + (caller.ndb._npc_data["lookplace"] or "(none)") + "\n"
    text += "|y4|n - Shopkeeper: " + ("Yes" if caller.ndb._npc_data["is_shopkeeper"] else "No") + "\n"
    text += "|y5|n - Languages: " + ", ".join([lang.capitalize() for lang in caller.ndb._npc_data["known_languages"]]) + "\n"
    text += "|y6|n - Configure Stats\n"
    text += "|y7|n - Configure Skills\n"
    text += "|ys|n - Finish and Save\n"
    text += "|yq|n - Cancel\n"
    
    options = (
        {"key": "_default", "goto": "npc_properties"},
    )
    
    return text, options


def npc_faction(caller, raw_string, **kwargs):
    """Choose NPC faction using proper EvMenu pattern."""
    factions = get_all_factions()
    
    # Input mode - process user's choice
    if raw_string and raw_string.strip():
        choice = raw_string.strip().lower()
        
        if choice == "b":
            return npc_properties(caller, "", **kwargs)
        
        try:
            idx = int(choice)
            if 1 <= idx <= len(factions):
                caller.ndb._npc_data["faction"] = factions[idx - 1]["id"]
                return npc_properties(caller, "", **kwargs)
        except ValueError:
            pass
        
        caller.msg("|rInvalid choice. Enter a number or b.|n")
        return npc_faction(caller, "", **kwargs)
    
    # Display mode - show menu
    text = BuilderMenuMixin.format_header("NPC DESIGNER - SELECT FACTION")
    text += "\nAvailable factions:\n\n"
    
    for idx, faction in enumerate(factions, 1):
        text += f"|y{idx}|n - {faction['name']}: {faction['description']}\n"
    
    text += "|yb|n - Back\n"
    
    options = (
        {"key": "_default", "goto": "npc_faction"},
    )
    return text, options


def npc_languages(caller, raw_string, **kwargs):
    """Configure NPC languages."""
    from world.language.constants import LANGUAGES, COMMON_LANGUAGES, ALL_LANGUAGES
    
    # Builders and higher have access to all languages
    has_builder_perm = caller.locks.check_lockstring(caller, "perm(Builder)")
    available_languages = ALL_LANGUAGES if has_builder_perm else COMMON_LANGUAGES
    
    # Input mode - process user's choice
    if raw_string and raw_string.strip():
        choice = raw_string.strip().lower()
        
        if choice == "b":
            return npc_properties(caller, "", **kwargs)
        
        # Check if it's a language code or number
        lang_codes = sorted([code for code in LANGUAGES.keys() if code in available_languages])
        
        # Try as index (1-based)
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(lang_codes):
                lang_code = lang_codes[idx]
                known = caller.ndb._npc_data["known_languages"]
                
                # Toggle language
                if lang_code in known:
                    if len(known) <= 1:
                        caller.msg("|rNPC must know at least one language.|n")
                        return npc_languages(caller, "", **kwargs)
                    known.remove(lang_code)
                else:
                    if len(known) < 10:
                        known.append(lang_code)
                    else:
                        caller.msg("|rMaximum 10 languages allowed.|n")
                        return npc_languages(caller, "", **kwargs)
                
                caller.ndb._npc_data["known_languages"] = known
                return npc_languages(caller, "", **kwargs)
        except ValueError:
            pass
        
        # Try as language code
        if choice in available_languages:
            known = caller.ndb._npc_data["known_languages"]
            
            if choice in known:
                if len(known) <= 1:
                    caller.msg("|rNPC must know at least one language.|n")
                    return npc_languages(caller, "", **kwargs)
                known.remove(choice)
            else:
                if len(known) < 10:
                    known.append(choice)
                else:
                    caller.msg("|rMaximum 10 languages allowed.|n")
                    return npc_languages(caller, "", **kwargs)
            
            caller.ndb._npc_data["known_languages"] = known
            return npc_languages(caller, "", **kwargs)
        
        caller.msg("|rInvalid choice. Enter a number, language code, or 'b'.|n")
    
    # Display mode - show menu
    from world.language.constants import LANGUAGES, COMMON_LANGUAGES, ALL_LANGUAGES
    
    # Builders and higher have access to all languages
    has_builder_perm = caller.locks.check_lockstring(caller, "perm(Builder)")
    available_languages = ALL_LANGUAGES if has_builder_perm else COMMON_LANGUAGES
    
    lang_codes = sorted([code for code in LANGUAGES.keys() if code in available_languages])
    known = caller.ndb._npc_data["known_languages"]
    primary = caller.ndb._npc_data["primary_language"]
    
    text = BuilderMenuMixin.format_header("NPC DESIGNER - LANGUAGES")
    text += f"\nNPC: {caller.ndb._npc_data['name']}\n"
    text += f"|yFirst language in list will be primary on save|n\n"
    text += f"|yCurrently selected: {', '.join([LANGUAGES[code]['name'] for code in known if code in available_languages])}|n\n\n"
    text += "|yToggle languages (select to add/remove):|n\n"
    
    for idx, code in enumerate(lang_codes, 1):
        lang_name = LANGUAGES[code]['name']
        is_known = 'X' if code in known else ' '
        text += f"|y[{idx}]|n [{is_known}] {lang_name}\n"
    
    if has_builder_perm:
        text += "\n|g[Builder - All languages available]|n\n"
    
    text += f"\n|ySelected: {len(known)}/10|n\n"
    text += "\n|yCommands:|n\n"
    text += "- Enter a number to toggle language\n"
    text += "|yb|n - Back\n"
    
    options = (
        {"key": "_default", "goto": "npc_languages"},
    )
    return text, options


def npc_wandering(caller, raw_string, **kwargs):
    """Set NPC wandering zone using proper EvMenu pattern."""
    # Check if we're first entering this node (display mode) vs processing input
    if not getattr(caller.ndb, '_wandering_input_mode', False):
        # First entry - set flag and display prompt
        caller.ndb._wandering_input_mode = True
        
        text = BuilderMenuMixin.format_header("NPC DESIGNER - WANDERING ZONE")
        text += "\nEnter zone ID for NPC to wander in, or press Enter for static (no wandering):\n"
        
        options = (
            {"key": "_default", "goto": "npc_wandering"},
        )
        
        return text, options
    
    # Input mode - user has entered something (or pressed Enter for static)
    if hasattr(caller.ndb, '_wandering_input_mode'):
        delattr(caller.ndb, '_wandering_input_mode')
    
    zone = raw_string.strip() if raw_string else ""
    
    # Store zone (empty string means static/no wandering)
    caller.ndb._npc_data["wandering_zone"] = zone
    if zone:
        caller.msg(f"|gWandering zone set to: {zone}|n")
    else:
        caller.msg("|gNPC set to static (no wandering)|n")
    return npc_properties(caller, "", **kwargs)


def npc_set_lookplace(caller, raw_string, **kwargs):
    """Set NPC look place (LP) using proper EvMenu pattern."""
    # Check if we're first entering this node (display mode) vs processing input
    if not getattr(caller.ndb, '_lookplace_input_mode', False):
        # First entry - set flag and display prompt
        caller.ndb._lookplace_input_mode = True
        
        text = BuilderMenuMixin.format_header("NPC DESIGNER - LOOK PLACE")
        text += "\nEnter how this NPC appears when others look around the room.\n"
        text += "Example: 'standing behind the counter' or 'lounging by the fire'\n"
        text += "Press Enter to skip:\n"
        
        options = (
            {"key": "_default", "goto": "npc_set_lookplace"},
        )
        
        return text, options
    
    # Input mode - user has entered something (or pressed Enter to skip)
    if hasattr(caller.ndb, '_lookplace_input_mode'):
        delattr(caller.ndb, '_lookplace_input_mode')
    
    lookplace = raw_string.strip() if raw_string else ""
    
    # Validate length if provided
    if lookplace:
        if len(lookplace) < 2:
            caller.msg("|rLook place must be at least 2 characters.|n")
            caller.ndb._lookplace_input_mode = True
            return npc_set_lookplace(caller, "", **kwargs)
        if len(lookplace) > 200:
            caller.msg("|rLook place must be 200 characters or less.|n")
            caller.ndb._lookplace_input_mode = True
            return npc_set_lookplace(caller, "", **kwargs)
    
    # Store lookplace
    caller.ndb._npc_data["lookplace"] = lookplace
    if lookplace:
        caller.msg(f"|gLook place set to: {lookplace}|n")
    else:
        caller.msg("|gLook place cleared.|n")
    return npc_properties(caller, "", **kwargs)


def npc_stats_menu(caller, raw_string, **kwargs):
    """Display stats menu for NPC configuration."""
    # Input mode - process user's choice
    if raw_string and raw_string.strip():
        choice = raw_string.strip().lower()
        
        if choice == "b":
            return npc_properties(caller, "", **kwargs)
        
        # Check if it's a stat number (1-7)
        try:
            stat_num = int(choice)
            if 1 <= stat_num <= 7:
                stat_names = ["body", "ref", "dex", "tech", "smrt", "will", "edge"]
                stat_name = stat_names[stat_num - 1]
                # Store the selected stat in ndb so edit function can access it
                caller.ndb._editing_stat = stat_name
                return npc_edit_stat(caller, "", **kwargs)
        except ValueError:
            pass
        
        caller.msg("|rInvalid choice. Enter 1-7 or b.|n")
        return npc_stats_menu(caller, "", **kwargs)  # Re-display menu
    
    # Display mode - show menu
    text = BuilderMenuMixin.format_header("NPC DESIGNER - CONFIGURE STATS")
    text += f"\nNPC: {caller.ndb._npc_data['name']}\n\n"
    text += "Stats scale from 1-10 (1 = weak, 10 = exceptional)\n\n"
    
    stats = caller.ndb._npc_data["stats"]
    stat_names = ["body", "ref", "dex", "tech", "smrt", "will", "edge"]
    stat_display = {
        "body": "Body (BODY): Your size, toughness, and ability to stay alive and conscious due to physical mass, structure, or other qualities. Important for how much damage you can take.",
        "ref": "Reflexes (REF): Your response time and coordination, as used in aiming, throwing, juggling, etc. Affects ability to hit with ranged weapons.",
        "dex": "Dexterity (DEX): Your overall physical competence for balancing, leaping, jumping, combat, and athletics. Affects ability to hit with melee weapons and dodge attacks.",
        "tech": "Technique (TECH): Your ability to manipulate tools or instruments. Covers knack for using tools, not just reaction speed. Now a real stat!",
        "smrt": "Smarts (SMRT): How generally bright you are, including cleverness, awareness, perception, and ability to learn.",
        "will": "Willpower (WILL): Your determination and ability to face danger and stress. Represents courage and ability to survive long-term privation. Important for how much damage you can take.",
        "edge": "Edge (EDGE): Your ability to impress and influence people through character and charisma; how well you get along with others; how you interact in social situations. Formerly 'Cool'.",
    }
    
    for idx, stat in enumerate(stat_names, 1):
        value = stats[stat]
        text += f"|y{idx}|n - {stat_display[stat].split(':')[0]:30} [Current: {value}]\n"

    emp_value = stats["edge"] + stats["will"]
    text += f"|y*|n - Empathy (EMP): |g[Calculated: {emp_value} (EDGE {stats['edge']} + WILL {stats['will']})]|n\n"

    text += "|yb|n - Back to Properties\n"
    
    options = (
        {"key": "_default", "goto": "npc_stats_menu"},
    )
    
    return text, options


def npc_edit_stat(caller, raw_string, **kwargs):
    """Edit a specific stat using proper EvMenu pattern."""
    # Get stat name from ndb (was stored by npc_stats_menu)
    stat_name = getattr(caller.ndb, '_editing_stat', None)
    if not stat_name:
        return npc_stats_menu(caller, "", **kwargs)
    
    # Input mode - process user's text
    if raw_string and raw_string.strip():
        try:
            value = int(raw_string.strip())
            if 1 <= value <= 10:
                caller.ndb._npc_data["stats"][stat_name] = value
                caller.msg(f"|gStat {stat_name} set to {value}.|n")
                if hasattr(caller.ndb, '_editing_stat'):
                    delattr(caller.ndb, '_editing_stat')
                return npc_stats_menu(caller, "", **kwargs)
            else:
                caller.msg("|rValue must be between 1 and 10.|n")
                return npc_edit_stat(caller, "", **kwargs)  # Re-display
        except (ValueError, TypeError):
            caller.msg("|rPlease enter a valid number.|n")
            return npc_edit_stat(caller, "", **kwargs)  # Re-display
    
    # Display mode - show prompt
    text = BuilderMenuMixin.format_header("NPC DESIGNER - EDIT STAT")
    text += f"\nStat: {stat_name.upper()}\n"
    text += f"Current value: {caller.ndb._npc_data['stats'][stat_name]}\n\n"
    text += "Enter new value (1-10):\n"
    
    options = (
        {"key": "_default", "goto": "npc_edit_stat"},
    )
    
    return text, options


def npc_skills_menu(caller, raw_string, **kwargs):
    """Display skills menu for NPC configuration."""
    # Input mode - process user's choice
    if raw_string and raw_string.strip():
        choice = raw_string.strip().lower()
        
        if choice == "b":
            return npc_properties(caller, "", **kwargs)
        
        # Check if it's a skill number (1-29)
        try:
            skill_num = int(choice)
            if 1 <= skill_num <= 29:
                skill_names = [
                    "chemical", "modern_medicine", "holistic_medicine", "surgery", "science",
                    "dodge", "blades", "pistols", "rifles", "melee",
                    "brawling", "martial_arts", "grappling", "snooping", "stealing",
                    "hiding", "sneaking", "disguise", "tailoring", "tinkering",
                    "manufacturing", "cooking", "forensics", "decking", "electronics",
                    "mercantile", "streetwise", "paint_draw_sculpt", "instrument"
                ]
                skill_name = skill_names[skill_num - 1]
                # Store the selected skill in ndb so edit function can access it
                caller.ndb._editing_skill = skill_name
                return npc_edit_skill(caller, "", **kwargs)
        except ValueError:
            pass
        
        caller.msg("|rInvalid choice. Enter 1-29 or b.|n")
        return npc_skills_menu(caller, "", **kwargs)  # Re-display menu
    
    # Display mode - show menu
    text = BuilderMenuMixin.format_header("NPC DESIGNER - CONFIGURE SKILLS")
    text += f"\nNPC: {caller.ndb._npc_data['name']}\n\n"
    text += "Skills scale from 0-100 (0 = untrained, 100 = master)\n\n"
    
    skills = caller.ndb._npc_data["skills"]
    skill_names = [
        "chemical", "modern_medicine", "holistic_medicine", "surgery", "science",
        "dodge", "blades", "pistols", "rifles", "melee",
        "brawling", "martial_arts", "grappling", "snooping", "stealing",
        "hiding", "sneaking", "disguise", "tailoring", "tinkering",
        "manufacturing", "cooking", "forensics", "decking", "electronics",
        "mercantile", "streetwise", "paint_draw_sculpt", "instrument"
    ]
    skill_display = {
        "chemical": "Chemical",
        "modern_medicine": "Modern Medicine",
        "holistic_medicine": "Holistic Medicine",
        "surgery": "Surgery",
        "science": "Science",
        "dodge": "Dodge",
        "blades": "Blades",
        "pistols": "Pistols",
        "rifles": "Rifles",
        "melee": "Melee",
        "brawling": "Brawling",
        "martial_arts": "Martial Arts",
        "grappling": "Grappling",
        "snooping": "Snooping",
        "stealing": "Stealing",
        "hiding": "Hiding",
        "sneaking": "Sneaking",
        "disguise": "Disguise",
        "tailoring": "Tailoring",
        "tinkering": "Tinkering",
        "manufacturing": "Manufacturing",
        "cooking": "Cooking",
        "forensics": "Forensics",
        "decking": "Decking",
        "electronics": "Electronics",
        "mercantile": "Mercantile",
        "streetwise": "Streetwise",
        "paint_draw_sculpt": "Paint/Draw/Sculpt",
        "instrument": "Instrument",
    }
    
    for idx, skill in enumerate(skill_names, 1):
        value = skills.get(skill, 0)
        text += f"|y{idx:2}|n - {skill_display[skill]:20} [Current: {value}]\n"
    
    text += "\n|yb|n - Back to Properties\n"
    
    options = (
        {"key": "_default", "goto": "npc_skills_menu"},
    )
    
    return text, options


def npc_edit_skill(caller, raw_string, **kwargs):
    """Edit a specific skill using proper EvMenu pattern."""
    # Get skill name from ndb (was stored by npc_skills_menu)
    skill_name = getattr(caller.ndb, '_editing_skill', None)
    if not skill_name:
        return npc_skills_menu(caller, "", **kwargs)
    
    # Input mode - process user's text
    if raw_string and raw_string.strip():
        try:
            value = int(raw_string.strip())
            if 0 <= value <= 100:
                caller.ndb._npc_data["skills"][skill_name] = value
                caller.msg(f"|gSkill {skill_name} set to {value}.|n")
                if hasattr(caller.ndb, '_editing_skill'):
                    delattr(caller.ndb, '_editing_skill')
                return npc_skills_menu(caller, "", **kwargs)
            else:
                caller.msg("|rValue must be between 0 and 100.|n")
                return npc_edit_skill(caller, "", **kwargs)  # Re-display
        except (ValueError, TypeError):
            caller.msg("|rPlease enter a valid number.|n")
            return npc_edit_skill(caller, "", **kwargs)  # Re-display
    
    # Display mode - show prompt
    text = BuilderMenuMixin.format_header("NPC DESIGNER - EDIT SKILL")
    text += f"\nSkill: {skill_name.upper()}\n"
    text += f"Current value: {caller.ndb._npc_data['skills'][skill_name]}\n\n"
    text += "Enter new value (0-100):\n"
    
    options = (
        {"key": "_default", "goto": "npc_edit_skill"},
    )
    
    return text, options


def npc_save(caller, raw_string, **kwargs):
    """Save NPC design."""
    data = caller.ndb._npc_data
    
    # Set primary language to the first language in the known_languages list
    if data["known_languages"]:
        data["primary_language"] = data["known_languages"][0]
    
    npc = add_npc(
        name=data["name"],
        desc=data["desc"],
        faction=data["faction"],
        wandering_zone=data["wandering_zone"],
        is_shopkeeper=data["is_shopkeeper"],
        stats=data["stats"],
        skills=data["skills"],
        created_by=caller.key,
        primary_language=data["primary_language"],
        known_languages=data["known_languages"]
    )
    
    text = BuilderMenuMixin.format_header("SUCCESS")
    text += f"\nNPC saved!\n"
    text += f"Name: {npc['name']}\n"
    text += f"ID: {npc['id']}\n"
    text += f"Faction: {npc['faction']}\n"
    text += f"Primary Language: {npc['primary_language']}\n"
    text += f"Known Languages: {', '.join(npc['known_languages'])}\n"
    text += f"Stats: {npc['stats']}\n"
    text += f"Skills: {npc['skills']}\n\n"
    text += f"You can now spawn it using: |yspawnnpc {npc['id']}|n\n"
    
    if hasattr(caller.ndb, '_npc_data'):
        delattr(caller.ndb, '_npc_data')
    
    caller.msg(text)
    return None  # Exit menu


def npc_cancel(caller, raw_string, **kwargs):
    """Cancel NPC creation."""
    if hasattr(caller.ndb, '_npc_data'):
        delattr(caller.ndb, '_npc_data')
    
    caller.msg("|rCancelled.|n")
    return None  # Exit menu


# ============================================================================
# WEAPON MENU
# ============================================================================

def weapon_start(caller, raw_string, **kwargs):
    """Start weapon creation menu."""
    caller.ndb._weapon_data = {
        "name": "",
        "desc": "",
        "weapon_type": "melee",
        "ammo_type": "",
        "damage_bonus": 0,
        "accuracy_bonus": 0,
        "skill": "brawling",
    }
    
    return weapon_name(caller, "", **kwargs)


def weapon_name(caller, raw_string, **kwargs):
    """Get weapon name using proper EvMenu pattern."""
    # Input mode - process user's text
    if raw_string and raw_string.strip():
        name = raw_string.strip()
        
        # Strip "designweapon" prefix if user accidentally included it
        if name.startswith("designweapon "):
            name = name[len("designweapon "):]
        
        # Validate
        if len(name) < 2:
            caller.msg("|rName must be at least 2 characters.|n")
            return None  # Re-display this node
        
        if len(name) > 50:
            caller.msg("|rName must be 50 characters or less.|n")
            return None  # Re-display this node
        
        # Store and advance
        caller.ndb._weapon_data["name"] = name
        return weapon_desc(caller, "", **kwargs)
    
    # Display mode - show prompt
    text = BuilderMenuMixin.format_header("WEAPON DESIGNER - STEP 1: NAME")
    text += "\nEnter the weapon name (e.g., 'Rusty Pistol', 'Combat Knife'):\n"
    
    options = (
        {"key": "_default", "goto": "weapon_name"},
    )
    return text, options


def weapon_desc(caller, raw_string, **kwargs):
    """Get weapon description using proper EvMenu pattern."""
    # Input mode - process user's text
    if raw_string and raw_string.strip():
        desc = raw_string.strip()
        
        # Validate
        if len(desc) < 5:
            caller.msg("|rDescription must be at least 5 characters.|n")
            return weapon_desc(caller, "", **kwargs)  # Re-display this node
        
        if len(desc) > 500:
            caller.msg("|rDescription must be 500 characters or less.|n")
            return weapon_desc(caller, "", **kwargs)  # Re-display this node
        
        # Store and advance
        caller.ndb._weapon_data["desc"] = desc
        return weapon_type_select(caller, "", **kwargs)
    
    # Display mode - show prompt
    text = BuilderMenuMixin.format_header("WEAPON DESIGNER - STEP 2: DESCRIPTION")
    text += f"\nWeapon: {caller.ndb._weapon_data['name']}\n"
    text += "\nEnter the weapon description:\n"
    
    options = (
        {"key": "_default", "goto": "weapon_desc"},
    )
    return text, options


def weapon_type_select(caller, raw_string, **kwargs):
    """Select weapon type."""
    # Input mode - process user's choice
    if raw_string and raw_string.strip():
        choice = raw_string.strip()
        if choice == "1":
            caller.ndb._weapon_data["weapon_type"] = "melee"
            return weapon_skill_select(caller, "", **kwargs)
        elif choice == "2":
            caller.ndb._weapon_data["weapon_type"] = "ranged"
            return weapon_ammo_type(caller, "", **kwargs)
        else:
            caller.msg("|rChoose 1 or 2:|n")
            return weapon_type_select(caller, "", **kwargs)  # Re-display this node
    
    # Display mode - show prompt
    text = BuilderMenuMixin.format_header("WEAPON DESIGNER - TYPE")
    text += f"\nWeapon: {caller.ndb._weapon_data['name']}\n\n"
    text += "|y1|n - Melee (knife, sword, club, etc.)\n"
    text += "|y2|n - Ranged (gun, bow, etc.)\n"
    
    options = (
        {"key": "_default", "goto": "weapon_type_select"},
    )
    return text, options


def weapon_ammo_type(caller, raw_string, **kwargs):
    """Get ammo type for ranged weapons."""
    # Input mode - process user's text
    if raw_string and raw_string.strip():
        ammo = raw_string.strip()
        if not ammo:
            caller.msg("|rAmmo type cannot be empty.|n")
            return weapon_ammo_type(caller, "", **kwargs)  # Re-display this node
        
        caller.ndb._weapon_data["ammo_type"] = ammo
        return weapon_skill_select(caller, "", **kwargs)
    
    # Display mode - show prompt
    text = BuilderMenuMixin.format_header("WEAPON DESIGNER - AMMO TYPE")
    text += f"\nWeapon: {caller.ndb._weapon_data['name']}\n\n"
    text += "Enter ammo type (e.g., '9mm', 'arrow', '12gauge'):\n"
    
    options = (
        {"key": "_default", "goto": "weapon_ammo_type"},
    )
    return text, options

def weapon_skill_select(caller, raw_string, **kwargs):
    """Select which skill uses this weapon."""
    # Input mode - process user's choice
    if raw_string and raw_string.strip():
        choice = raw_string.strip().lower()
        
        skills = {
            "1": "blades",
            "2": "pistols",
            "3": "rifles",
            "4": "melee",
            "5": "brawling",
            "6": "martial_arts",
        }
        
        if choice in skills:
            caller.ndb._weapon_data["skill"] = skills[choice]
            return weapon_properties(caller, "", **kwargs)
        else:
            caller.msg("|rChoose 1-6:|n")
            return weapon_skill_select(caller, "", **kwargs)  # Re-display this node
    
    # Display mode - show prompt
    text = BuilderMenuMixin.format_header("WEAPON DESIGNER - SKILL")
    text += f"\nWeapon: {caller.ndb._weapon_data['name']}\n"
    text += f"Type: {caller.ndb._weapon_data['weapon_type'].capitalize()}\n\n"
    text += "Select the skill used with this weapon:\n\n"
    text += "|y1|n - Blades (knives, swords, edged weapons)\n"
    text += "|y2|n - Pistols (handguns, revolvers)\n"
    text += "|y3|n - Rifles (rifles, assault rifles)\n"
    text += "|y4|n - Melee (clubs, hammers, blunt force)\n"
    text += "|y5|n - Brawling (fists, unarmed combat)\n"
    text += "|y6|n - Martial Arts (specialized hand-to-hand)\n"
    
    options = (
        {"key": "_default", "goto": "weapon_skill_select"},
    )
    return text, options


def weapon_properties(caller, raw_string, **kwargs):
    """Configure weapon properties."""
    # Input mode - process user's choice
    if raw_string and raw_string.strip():
        choice = raw_string.strip().lower()
        
        if choice == "1":
            return weapon_damage(caller, "", **kwargs)
        elif choice == "2":
            return weapon_accuracy(caller, "", **kwargs)
        elif choice == "s":
            return weapon_save(caller, "", **kwargs)
        elif choice == "q":
            return weapon_cancel(caller, "", **kwargs)
        else:
            caller.msg("|rInvalid choice. Enter 1, 2, s, or q.|n")
            return weapon_properties(caller, "", **kwargs)
    
    # Display mode - show menu
    text = BuilderMenuMixin.format_header("WEAPON DESIGNER - PROPERTIES")
    text += f"\nWeapon: {caller.ndb._weapon_data['name']}\n"
    text += f"Type: {caller.ndb._weapon_data['weapon_type'].capitalize()}\n"
    text += f"Skill: {caller.ndb._weapon_data['skill'].replace('_', ' ').title()}\n"
    if caller.ndb._weapon_data["weapon_type"] == "ranged":
        text += f"Ammo: {caller.ndb._weapon_data['ammo_type']}\n\n"
    else:
        text += "\n"
    
    text += "|y1|n - Base Damage: " + str(caller.ndb._weapon_data["damage_bonus"]) + "\n"
    text += "|y2|n - Accuracy Bonus: " + str(caller.ndb._weapon_data["accuracy_bonus"]) + "\n"
    text += "|ys|n - Finish and Save\n"
    text += "|yq|n - Cancel\n"
    
    options = (
        {"key": "_default", "goto": "weapon_properties"},
    )
    return text, options


def weapon_damage(caller, raw_string, **kwargs):
    """Set base damage."""
    # Input mode - process user's input
    if raw_string and raw_string.strip():
        try:
            damage = int(raw_string.strip())
            if damage < 1 or damage > 30:
                raise ValueError()
            caller.ndb._weapon_data["damage_bonus"] = damage
            return weapon_properties(caller, "", **kwargs)
        except:
            caller.msg("|rEnter a number between 1 and 30.|n")
            return weapon_damage(caller, "", **kwargs)  # Re-display this node
    
    # Display mode - show prompt
    text = BuilderMenuMixin.format_header("WEAPON DESIGNER - BASE DAMAGE")
    text += "\nEnter base damage (1-30):\n"
    
    options = (
        {"key": "_default", "goto": "weapon_damage"},
    )
    return text, options


def weapon_accuracy(caller, raw_string, **kwargs):
    """Set accuracy bonus."""
    # Input mode - process user's input
    if raw_string and raw_string.strip():
        try:
            accuracy = int(raw_string.strip())
            if accuracy < -5 or accuracy > 5:
                raise ValueError()
            caller.ndb._weapon_data["accuracy_bonus"] = accuracy
            return weapon_properties(caller, "", **kwargs)
        except:
            caller.msg("|rEnter a number between -5 and 5.|n")
            return weapon_accuracy(caller, "", **kwargs)  # Re-display this node
    
    # Display mode - show prompt
    text = BuilderMenuMixin.format_header("WEAPON DESIGNER - ACCURACY BONUS")
    text += "\nEnter accuracy bonus (-5 to 5):\n"
    
    options = (
        {"key": "_default", "goto": "weapon_accuracy"},
    )
    return text, options


def weapon_save(caller, raw_string, **kwargs):
    """Save weapon design."""
    data = caller.ndb._weapon_data
    weapon = add_weapon(
        name=data["name"],
        desc=data["desc"],
        weapon_type=data["weapon_type"],
        ammo_type=data["ammo_type"],
        damage_bonus=data["damage_bonus"],
        accuracy_bonus=data["accuracy_bonus"],
        skill=data["skill"],
        created_by=caller.key
    )
    
    text = BuilderMenuMixin.format_header("SUCCESS")
    text += f"\nWeapon saved!\n"
    text += f"Name: {weapon['name']}\n"
    text += f"ID: {weapon['id']}\n"
    text += f"Skill: {weapon['skill'].replace('_', ' ').title()}\n\n"
    text += f"You can now spawn it using: |yspawnweapon {weapon['id']}|n\n"
    
    if hasattr(caller.ndb, '_weapon_data'):
        delattr(caller.ndb, '_weapon_data')
    
    caller.msg(text)
    return None  # Exit menu


def weapon_cancel(caller, raw_string, **kwargs):
    """Cancel weapon creation."""
    if hasattr(caller.ndb, '_weapon_data'):
        delattr(caller.ndb, '_weapon_data')
    
    caller.msg("|rCancelled.|n")
    return None  # Exit menu


# ============================================================================
# CLOTHING/ARMOR MENU
# ============================================================================

def clothing_start(caller, raw_string, **kwargs):
    """Start clothing/armor creation menu."""
    caller.ndb._clothing_data = {
        "name": "",
        "desc": "",
        "item_type": "clothing",
        "armor_value": 0,
        "armor_type": "",
        "rarity": "common",
    }
    
    return clothing_name(caller, "", **kwargs)


def clothing_name(caller, raw_string, **kwargs):
    """Get clothing name using proper EvMenu pattern."""
    # Input mode - process user's text
    if raw_string and raw_string.strip():
        name = raw_string.strip()
        
        # Validate
        if len(name) < 2:
            caller.msg("|rName must be at least 2 characters.|n")
            return clothing_name(caller, "", **kwargs)  # Re-display this node
        
        if len(name) > 50:
            caller.msg("|rName must be 50 characters or less.|n")
            return clothing_name(caller, "", **kwargs)  # Re-display this node
        
        # Store and advance
        caller.ndb._clothing_data["name"] = name
        return clothing_desc(caller, "", **kwargs)
    
    # Display mode - show prompt
    text = BuilderMenuMixin.format_header("CLOTHING/ARMOR DESIGNER - STEP 1: NAME")
    text += "\nEnter the item name (e.g., 'Leather Jacket', 'Tactical Vest'):\n"
    
    options = (
        {"key": "_default", "goto": "clothing_name"},
    )
    return text, options


def clothing_desc(caller, raw_string, **kwargs):
    """Get clothing description using proper EvMenu pattern."""
    # Input mode - process user's text
    if raw_string and raw_string.strip():
        desc = raw_string.strip()
        
        # Validate
        if len(desc) < 5:
            caller.msg("|rDescription must be at least 5 characters.|n")
            return clothing_desc(caller, "", **kwargs)  # Re-display this node
        
        if len(desc) > 500:
            caller.msg("|rDescription must be 500 characters or less.|n")
            return clothing_desc(caller, "", **kwargs)  # Re-display this node
        
        # Store and advance
        caller.ndb._clothing_data["desc"] = desc
        return clothing_type_select(caller, "", **kwargs)
    
    # Display mode - show prompt
    text = BuilderMenuMixin.format_header("CLOTHING/ARMOR DESIGNER - STEP 2: DESCRIPTION")
    text += f"\nItem: {caller.ndb._clothing_data['name']}\n"
    text += "\nEnter the item description:\n"
    
    options = (
        {"key": "_default", "goto": "clothing_desc"},
    )
    return text, options


def clothing_type_select(caller, raw_string, **kwargs):
    """Select clothing or armor."""
    # Input mode - process user's choice
    if raw_string and raw_string.strip():
        choice = raw_string.strip()
        if choice == "1":
            caller.ndb._clothing_data["item_type"] = "clothing"
            return clothing_rarity(caller, "", **kwargs)
        elif choice == "2":
            caller.ndb._clothing_data["item_type"] = "armor"
            return armor_type_select(caller, "", **kwargs)
        else:
            caller.msg("|rChoose 1 or 2:|n")
            return clothing_type_select(caller, "", **kwargs)
    
    # Display mode - show prompt
    text = BuilderMenuMixin.format_header("CLOTHING/ARMOR DESIGNER - TYPE")
    text += f"\nItem: {caller.ndb._clothing_data['name']}\n\n"
    text += "|y1|n - Clothing (no armor value)\n"
    text += "|y2|n - Armor (provides protection)\n"
    
    options = (
        {"key": "_default", "goto": "clothing_type_select"},
    )
    return text, options


def armor_type_select(caller, raw_string, **kwargs):
    """Select armor type."""
    # Input mode - process user's choice
    if raw_string and raw_string.strip():
        choice = raw_string.strip()
        if choice == "1":
            caller.ndb._clothing_data["armor_type"] = "light"
            return armor_value(caller, "", **kwargs)
        elif choice == "2":
            caller.ndb._clothing_data["armor_type"] = "medium"
            return armor_value(caller, "", **kwargs)
        elif choice == "3":
            caller.ndb._clothing_data["armor_type"] = "heavy"
            return armor_value(caller, "", **kwargs)
        else:
            caller.msg("|rChoose 1, 2, or 3:|n")
            return armor_type_select(caller, "", **kwargs)
    
    # Display mode - show prompt
    text = BuilderMenuMixin.format_header("CLOTHING/ARMOR DESIGNER - ARMOR TYPE")
    text += f"\nItem: {caller.ndb._clothing_data['name']}\n\n"
    text += "|y1|n - Light (leather, cloth armor)\n"
    text += "|y2|n - Medium (kevlar, composite)\n"
    text += "|y3|n - Heavy (ballistic plates, combat gear)\n"
    
    options = (
        {"key": "_default", "goto": "armor_type_select"},
    )
    return text, options


def armor_value(caller, raw_string, **kwargs):
    """Set armor value."""
    # Input mode - process user's input
    if raw_string and raw_string.strip():
        try:
            value = int(raw_string.strip())
            if 1 <= value <= 10:
                caller.ndb._clothing_data["armor_value"] = value
                return clothing_rarity(caller, "", **kwargs)
            else:
                caller.msg("|rEnter a number between 1 and 10.|n")
                return armor_value(caller, "", **kwargs)
        except ValueError:
            caller.msg("|rPlease enter a valid number.|n")
            return armor_value(caller, "", **kwargs)
    
    # Display mode - show prompt
    text = BuilderMenuMixin.format_header("CLOTHING/ARMOR DESIGNER - ARMOR VALUE")
    text += "\nEnter armor value (1-10):\n"
    
    options = (
        {"key": "_default", "goto": "armor_value"},
    )
    return text, options


def clothing_rarity(caller, raw_string, **kwargs):
    """Select clothing rarity."""
    # Input mode - process user's choice
    if raw_string and raw_string.strip():
        rarities = {"1": "common", "2": "uncommon", "3": "rare", "4": "epic"}
        choice = raw_string.strip()
        if choice in rarities:
            caller.ndb._clothing_data["rarity"] = rarities[choice]
            return clothing_save(caller, "", **kwargs)
        else:
            caller.msg("|rChoose 1, 2, 3, or 4:|n")
            return clothing_rarity(caller, "", **kwargs)
    
    # Display mode - show prompt
    text = BuilderMenuMixin.format_header("CLOTHING/ARMOR DESIGNER - RARITY")
    text += f"\nItem: {caller.ndb._clothing_data['name']}\n\n"
    text += "|y1|n - Common\n"
    text += "|y2|n - Uncommon\n"
    text += "|y3|n - Rare\n"
    text += "|y4|n - Epic\n"
    
    options = (
        {"key": "_default", "goto": "clothing_rarity"},
    )
    return text, options


def clothing_save(caller, raw_string, **kwargs):
    """Save clothing/armor design."""
    data = caller.ndb._clothing_data
    item = add_clothing_item(
        name=data["name"],
        desc=data["desc"],
        item_type=data["item_type"],
        armor_value=data["armor_value"],
        armor_type=data["armor_type"],
        rarity=data["rarity"],
        created_by=caller.key
    )
    
    text = BuilderMenuMixin.format_header("SUCCESS")
    text += f"\nItem saved!\n"
    text += f"Name: {item['name']}\n"
    text += f"ID: {item['id']}\n\n"
    text += f"You can now spawn it using: |yspawnclothing {item['id']}|n\n"
    
    if hasattr(caller.ndb, '_clothing_data'):
        delattr(caller.ndb, '_clothing_data')
    
    caller.msg(text)
    return None  # Exit menu

