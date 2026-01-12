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
    
    return {"goto": "furniture_name"}


def furniture_name(caller, raw_string, **kwargs):
    """Get furniture name using proper EvMenu pattern."""
    # Input mode - process user's text
    if raw_string and raw_string.strip():
        name = raw_string.strip()
        
        # Validate
        if len(name) < 2:
            caller.msg("|rName must be at least 2 characters.|n")
            return None  # Re-display this node
        
        if len(name) > 50:
            caller.msg("|rName must be 50 characters or less.|n")
            return None  # Re-display this node
        
        # Store and advance
        caller.ndb._furniture_data["name"] = name
        return {"goto": "furniture_desc"}
    
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
            return None  # Re-display this node
        
        if len(desc) > 500:
            caller.msg("|rDescription must be 500 characters or less.|n")
            return None  # Re-display this node
        
        # Store and advance
        caller.ndb._furniture_data["desc"] = desc
        return {"goto": "furniture_properties"}
    
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
            return None  # Re-display with updated value
        elif choice == "2":
            return {"goto": "furniture_seats"}
        elif choice == "3":
            caller.ndb._furniture_data["can_recline"] = not caller.ndb._furniture_data["can_recline"]
            return None  # Re-display with updated value
        elif choice == "4":
            caller.ndb._furniture_data["can_lie_down"] = not caller.ndb._furniture_data["can_lie_down"]
            return None  # Re-display with updated value
        elif choice == "5":
            return {"goto": "furniture_messages"}
        elif choice in ["s", "save"]:
            return {"goto": "furniture_save"}
        elif choice in ["q", "quit", "cancel"]:
            return {"goto": "furniture_cancel"}
        else:
            caller.msg("|rInvalid choice.|n")
            return None
    
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
                return {"goto": "furniture_properties"}
            else:
                caller.msg("|rSeats must be between 0 and 10.|n")
                return None  # Re-display
        except ValueError:
            caller.msg("|rPlease enter a valid number.|n")
            return None  # Re-display
    
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
            return {"goto": "furniture_cancel"}
        elif choice == "s":
            return {"goto": "furniture_save"}
        elif choice == "1" and caller.ndb._furniture_data["max_seats"] > 0:
            caller.ndb._editing_msg_type = "sit_msg_first"
            return {"goto": "furniture_msg_input"}
        elif choice == "2" and caller.ndb._furniture_data["max_seats"] > 0:
            caller.ndb._editing_msg_type = "sit_msg_third"
            return {"goto": "furniture_msg_input"}
        elif choice == "3" and caller.ndb._furniture_data["can_lie_down"]:
            caller.ndb._editing_msg_type = "lie_msg_first"
            return {"goto": "furniture_msg_input"}
        elif choice == "4" and caller.ndb._furniture_data["can_lie_down"]:
            caller.ndb._editing_msg_type = "lie_msg_third"
            return {"goto": "furniture_msg_input"}
        elif choice == "5" and caller.ndb._furniture_data["can_recline"]:
            caller.ndb._editing_msg_type = "recline_msg_first"
            return {"goto": "furniture_msg_input"}
        elif choice == "6" and caller.ndb._furniture_data["can_recline"]:
            caller.ndb._editing_msg_type = "recline_msg_third"
            return {"goto": "furniture_msg_input"}
        else:
            caller.msg("|rInvalid choice.|n")
            return None
    
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
        return {"goto": "furniture_messages"}
    
    # Input mode - process user's text
    if raw_string and raw_string.strip():
        caller.ndb._furniture_data[msg_type] = raw_string.strip()
        if hasattr(caller.ndb, '_editing_msg_type'):
            delattr(caller.ndb, '_editing_msg_type')
        return {"goto": "furniture_messages"}
    
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
    
    return text, [{"key": "_default", "exec": lambda c, rs: ("", [])}]


def furniture_cancel(caller, raw_string, **kwargs):
    """Cancel furniture creation."""
    if hasattr(caller.ndb, '_furniture_data'):
        delattr(caller.ndb, '_furniture_data')
    
    return "Cancelled.", [{"key": "_default", "exec": lambda c, rs: ("", [])}]


# ============================================================================
# NPC MENU
# ============================================================================

def npc_start(caller, raw_string, **kwargs):
    """Start NPC creation menu."""
    initialize_default_factions()
    
    caller.ndb._npc_data = {
        "name": "",
        "desc": "",
        "faction": "neutral",
        "wandering_zone": "",
        "is_shopkeeper": False,
        "stats": {
            "body": 1,
            "ref": 1,
            "dex": 1,
            "tech": 1,
            "smrt": 1,
            "will": 1,
            "edge": 1,
            "emp": 1,
        },
        "skills": {
            "brawling": 0,
            "blades": 0,
            "blunt": 0,
            "ranged": 0,
            "grapple": 0,
            "dodge": 0,
            "stealth": 0,
            "intimidate": 0,
            "persuasion": 0,
            "perception": 0,
        },
    }
    
    return {"goto": "npc_name"}


def npc_name(caller, raw_string, **kwargs):
    """Get NPC name using proper EvMenu pattern."""
    # Input mode - process user's text
    if raw_string and raw_string.strip():
        name = raw_string.strip()
        
        # Validate
        if len(name) < 2:
            caller.msg("|rName must be at least 2 characters.|n")
            return None  # Re-display this node
        
        if len(name) > 50:
            caller.msg("|rName must be 50 characters or less.|n")
            return None  # Re-display this node
        
        # Store and advance
        caller.ndb._npc_data["name"] = name
        return {"goto": "npc_desc"}
    
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
            return None  # Re-display this node
        
        if len(desc) > 500:
            caller.msg("|rDescription must be 500 characters or less.|n")
            return None  # Re-display this node
        
        # Store and advance
        caller.ndb._npc_data["desc"] = desc
        return {"goto": "npc_properties"}
    
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
            return {"goto": "npc_faction"}
        elif choice == "2":
            return {"goto": "npc_wandering"}
        elif choice == "3":
            caller.ndb._npc_data["is_shopkeeper"] = not caller.ndb._npc_data["is_shopkeeper"]
            return None  # Re-display with updated value
        elif choice == "4":
            return {"goto": "npc_stats_menu"}
        elif choice == "5":
            return {"goto": "npc_skills_menu"}
        elif choice in ["s", "save"]:
            return {"goto": "npc_save"}
        elif choice in ["q", "quit", "cancel"]:
            return {"goto": "npc_cancel"}
        else:
            caller.msg("|rInvalid choice. Please enter 1-5, s, or q.|n")
            return None  # Re-display menu
    
    # Display mode - show menu
    text = BuilderMenuMixin.format_header("NPC DESIGNER - PROPERTIES")
    text += f"\nNPC: {caller.ndb._npc_data['name']}\n\n"
    text += "|y1|n - Faction: " + caller.ndb._npc_data["faction"] + "\n"
    text += "|y2|n - Wandering Zone: " + (caller.ndb._npc_data["wandering_zone"] or "(none - static)") + "\n"
    text += "|y3|n - Shopkeeper: " + ("Yes" if caller.ndb._npc_data["is_shopkeeper"] else "No") + "\n"
    text += "|y4|n - Configure Stats\n"
    text += "|y5|n - Configure Skills\n"
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
        
        if choice == "q":
            return {"goto": "npc_properties"}
        
        try:
            idx = int(choice)
            if 1 <= idx <= len(factions):
                caller.ndb._npc_data["faction"] = factions[idx - 1]["id"]
                return {"goto": "npc_properties"}
        except ValueError:
            pass
        
        caller.msg("|rInvalid choice. Enter a number or q.|n")
        return None
    
    # Display mode - show menu
    text = BuilderMenuMixin.format_header("NPC DESIGNER - SELECT FACTION")
    text += "\nAvailable factions:\n\n"
    
    for idx, faction in enumerate(factions, 1):
        text += f"|y{idx}|n - {faction['name']}: {faction['description']}\n"
    
    text += "|yq|n - Back\n"
    
    options = (
        {"key": "_default", "goto": "npc_faction"},
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
    return {"goto": "npc_properties"}


def npc_stats_menu(caller, raw_string, **kwargs):
    """Display stats menu for NPC configuration."""
    # Input mode - process user's choice
    if raw_string and raw_string.strip():
        choice = raw_string.strip().lower()
        
        if choice == "q":
            return {"goto": "npc_properties"}
        
        # Check if it's a stat number (1-8)
        try:
            stat_num = int(choice)
            if 1 <= stat_num <= 8:
                stat_names = ["body", "ref", "dex", "tech", "smrt", "will", "edge", "emp"]
                stat_name = stat_names[stat_num - 1]
                # Store the selected stat in ndb so edit function can access it
                caller.ndb._editing_stat = stat_name
                return {"goto": "npc_edit_stat"}
        except ValueError:
            pass
        
        caller.msg("|rInvalid choice. Enter 1-8 or q.|n")
        return None  # Re-display menu
    
    # Display mode - show menu
    text = BuilderMenuMixin.format_header("NPC DESIGNER - CONFIGURE STATS")
    text += f"\nNPC: {caller.ndb._npc_data['name']}\n\n"
    text += "Stats scale from 1-10 (1 = weak, 10 = exceptional)\n\n"
    
    stats = caller.ndb._npc_data["stats"]
    stat_names = ["body", "ref", "dex", "tech", "smrt", "will", "edge", "emp"]
    stat_display = {
        "body": "Body (Physical toughness)",
        "ref": "Ref (Reaction speed)",
        "dex": "Dex (Manual dexterity)",
        "tech": "Tech (Technical aptitude)",
        "smrt": "Smrt (Intelligence)",
        "will": "Will (Mental fortitude)",
        "edge": "Edge (Luck/chance)",
        "emp": "Emp (Empathy/social)",
    }
    
    for idx, stat in enumerate(stat_names, 1):
        value = stats[stat]
        text += f"|y{idx}|n - {stat_display[stat]:30} [Current: {value}]\n"
    
    text += "|yq|n - Back to Properties\n"
    
    options = (
        {"key": "_default", "goto": "npc_stats_menu"},
    )
    
    return text, options


def npc_edit_stat(caller, raw_string, **kwargs):
    """Edit a specific stat using proper EvMenu pattern."""
    # Get stat name from ndb (was stored by npc_stats_menu)
    stat_name = getattr(caller.ndb, '_editing_stat', None)
    if not stat_name:
        return {"goto": "npc_stats_menu"}
    
    # Input mode - process user's text
    if raw_string and raw_string.strip():
        try:
            value = int(raw_string.strip())
            if 1 <= value <= 10:
                caller.ndb._npc_data["stats"][stat_name] = value
                caller.msg(f"|gStat {stat_name} set to {value}.|n")
                if hasattr(caller.ndb, '_editing_stat'):
                    delattr(caller.ndb, '_editing_stat')
                return {"goto": "npc_stats_menu"}
            else:
                caller.msg("|rValue must be between 1 and 10.|n")
                return None  # Re-display
        except (ValueError, TypeError):
            caller.msg("|rPlease enter a valid number.|n")
            return None  # Re-display
    
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
        
        if choice == "q":
            return {"goto": "npc_properties"}
        
        # Check if it's a skill number (1-10)
        try:
            skill_num = int(choice)
            if 1 <= skill_num <= 10:
                skill_names = ["brawling", "blades", "blunt", "ranged", "grapple", 
                               "dodge", "stealth", "intimidate", "persuasion", "perception"]
                skill_name = skill_names[skill_num - 1]
                # Store the selected skill in ndb so edit function can access it
                caller.ndb._editing_skill = skill_name
                return {"goto": "npc_edit_skill"}
        except ValueError:
            pass
        
        caller.msg("|rInvalid choice. Enter 1-10 or q.|n")
        return None  # Re-display menu
    
    # Display mode - show menu
    text = BuilderMenuMixin.format_header("NPC DESIGNER - CONFIGURE SKILLS")
    text += f"\nNPC: {caller.ndb._npc_data['name']}\n\n"
    text += "Skills scale from 0-100 (0 = untrained, 100 = master)\n\n"
    
    skills = caller.ndb._npc_data["skills"]
    skill_names = ["brawling", "blades", "blunt", "ranged", "grapple", 
                   "dodge", "stealth", "intimidate", "persuasion", "perception"]
    skill_display = {
        "brawling": "Brawling (Unarmed combat)",
        "blades": "Blades (Edged weapons)",
        "blunt": "Blunt (Heavy blunt weapons)",
        "ranged": "Ranged (Guns/bows)",
        "grapple": "Grapple (Wrestling/holds)",
        "dodge": "Dodge (Evasion)",
        "stealth": "Stealth (Sneaking/hiding)",
        "intimidate": "Intimidate (Threaten/coerce)",
        "persuasion": "Persuasion (Convince/charm)",
        "perception": "Perception (Notice/awareness)",
    }
    
    for idx, skill in enumerate(skill_names, 1):
        value = skills[skill]
        text += f"|y{idx}|n - {skill_display[skill]:30} [Current: {value}]\n"
    
    text += "|yq|n - Back to Properties\n"
    
    options = (
        {"key": "_default", "goto": "npc_skills_menu"},
    )
    
    return text, options


def npc_edit_skill(caller, raw_string, **kwargs):
    """Edit a specific skill using proper EvMenu pattern."""
    # Get skill name from ndb (was stored by npc_skills_menu)
    skill_name = getattr(caller.ndb, '_editing_skill', None)
    if not skill_name:
        return {"goto": "npc_skills_menu"}
    
    # Input mode - process user's text
    if raw_string and raw_string.strip():
        try:
            value = int(raw_string.strip())
            if 0 <= value <= 100:
                caller.ndb._npc_data["skills"][skill_name] = value
                caller.msg(f"|gSkill {skill_name} set to {value}.|n")
                if hasattr(caller.ndb, '_editing_skill'):
                    delattr(caller.ndb, '_editing_skill')
                return {"goto": "npc_skills_menu"}
            else:
                caller.msg("|rValue must be between 0 and 100.|n")
                return None  # Re-display
        except (ValueError, TypeError):
            caller.msg("|rPlease enter a valid number.|n")
            return None  # Re-display
    
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
    npc = add_npc(
        name=data["name"],
        desc=data["desc"],
        faction=data["faction"],
        wandering_zone=data["wandering_zone"],
        is_shopkeeper=data["is_shopkeeper"],
        stats=data["stats"],
        skills=data["skills"],
        created_by=caller.key
    )
    
    text = BuilderMenuMixin.format_header("SUCCESS")
    text += f"\nNPC saved!\n"
    text += f"Name: {npc['name']}\n"
    text += f"ID: {npc['id']}\n"
    text += f"Faction: {npc['faction']}\n"
    text += f"Stats: {npc['stats']}\n"
    text += f"Skills: {npc['skills']}\n\n"
    text += f"You can now spawn it using: |yspawnnpc {npc['id']}|n\n"
    
    if hasattr(caller.ndb, '_npc_data'):
        delattr(caller.ndb, '_npc_data')
    
    return text, [{"key": "_default", "exec": lambda c, rs: ("", [])}]


def npc_cancel(caller, raw_string, **kwargs):
    """Cancel NPC creation."""
    if hasattr(caller.ndb, '_npc_data'):
        delattr(caller.ndb, '_npc_data')
    
    return "Cancelled.", [{"key": "_default", "exec": lambda c, rs: ("", [])}]


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
    }
    
    return {"goto": "weapon_name"}


def weapon_name(caller, raw_string, **kwargs):
    """Get weapon name using proper EvMenu pattern."""
    # Input mode - process user's text
    if raw_string and raw_string.strip():
        name = raw_string.strip()
        
        # Validate
        if len(name) < 2:
            caller.msg("|rName must be at least 2 characters.|n")
            return None  # Re-display this node
        
        if len(name) > 50:
            caller.msg("|rName must be 50 characters or less.|n")
            return None  # Re-display this node
        
        # Store and advance
        caller.ndb._weapon_data["name"] = name
        return {"goto": "weapon_desc"}
    
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
            return None  # Re-display this node
        
        if len(desc) > 500:
            caller.msg("|rDescription must be 500 characters or less.|n")
            return None  # Re-display this node
        
        # Store and advance
        caller.ndb._weapon_data["desc"] = desc
        return {"goto": "weapon_type_select"}
    
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
            return {"goto": "weapon_properties"}
        elif choice == "2":
            caller.ndb._weapon_data["weapon_type"] = "ranged"
            return {"goto": "weapon_ammo_type"}
        else:
            caller.msg("|rChoose 1 or 2:|n")
            return None  # Re-display this node
    
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
            return None  # Re-display this node
        
        caller.ndb._weapon_data["ammo_type"] = ammo
        return {"goto": "weapon_properties"}
    
    # Display mode - show prompt
    text = BuilderMenuMixin.format_header("WEAPON DESIGNER - AMMO TYPE")
    text += f"\nWeapon: {caller.ndb._weapon_data['name']}\n\n"
    text += "Enter ammo type (e.g., '9mm', 'arrow', '12gauge'):\n"
    
    options = (
        {"key": "_default", "goto": "weapon_ammo_type"},
    )
    return text, options


def weapon_properties(caller, raw_string, **kwargs):
    """Configure weapon properties."""
    # Input mode - process user's choice
    if raw_string and raw_string.strip():
        choice = raw_string.strip().lower()
        
        if choice == "1":
            return {"goto": "weapon_damage"}
        elif choice == "2":
            return {"goto": "weapon_accuracy"}
        elif choice == "s":
            return {"goto": "weapon_save"}
        elif choice == "q":
            return {"goto": "weapon_cancel"}
        else:
            caller.msg("|rInvalid choice. Enter 1, 2, s, or q.|n")
            return None
    
    # Display mode - show menu
    text = BuilderMenuMixin.format_header("WEAPON DESIGNER - PROPERTIES")
    text += f"\nWeapon: {caller.ndb._weapon_data['name']}\n"
    text += f"Type: {caller.ndb._weapon_data['weapon_type'].capitalize()}\n"
    if caller.ndb._weapon_data["weapon_type"] == "ranged":
        text += f"Ammo: {caller.ndb._weapon_data['ammo_type']}\n\n"
    else:
        text += "\n"
    
    text += "|y1|n - Damage Bonus: " + str(caller.ndb._weapon_data["damage_bonus"]) + "\n"
    text += "|y2|n - Accuracy Bonus: " + str(caller.ndb._weapon_data["accuracy_bonus"]) + "\n"
    text += "|ys|n - Finish and Save\n"
    text += "|yq|n - Cancel\n"
    
    options = (
        {"key": "_default", "goto": "weapon_properties"},
    )
    return text, options


def weapon_damage(caller, raw_string, **kwargs):
    """Set damage bonus."""
    # Input mode - process user's input
    if raw_string and raw_string.strip():
        try:
            damage = int(raw_string.strip())
            if damage < -5 or damage > 5:
                raise ValueError()
            caller.ndb._weapon_data["damage_bonus"] = damage
            return {"goto": "weapon_properties"}
        except:
            caller.msg("|rEnter a number between -5 and 5.|n")
            return None  # Re-display this node
    
    # Display mode - show prompt
    text = BuilderMenuMixin.format_header("WEAPON DESIGNER - DAMAGE BONUS")
    text += "\nEnter damage bonus (-5 to 5):\n"
    
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
            return {"goto": "weapon_properties"}
        except:
            caller.msg("|rEnter a number between -5 and 5.|n")
            return None  # Re-display this node
    
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
        created_by=caller.key
    )
    
    text = BuilderMenuMixin.format_header("SUCCESS")
    text += f"\nWeapon saved!\n"
    text += f"Name: {weapon['name']}\n"
    text += f"ID: {weapon['id']}\n\n"
    text += f"You can now spawn it using: |yspawnweapon {weapon['id']}|n\n"
    
    if hasattr(caller.ndb, '_weapon_data'):
        delattr(caller.ndb, '_weapon_data')
    
    return text, [{"key": "_default", "exec": lambda c, rs: ("", [])}]


def weapon_cancel(caller, raw_string, **kwargs):
    """Cancel weapon creation."""
    if hasattr(caller.ndb, '_weapon_data'):
        delattr(caller.ndb, '_weapon_data')
    
    return "Cancelled.", [{"key": "_default", "exec": lambda c, rs: ("", [])}]


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
    
    return {"goto": "clothing_name"}


def clothing_name(caller, raw_string, **kwargs):
    """Get clothing name using proper EvMenu pattern."""
    # Input mode - process user's text
    if raw_string and raw_string.strip():
        name = raw_string.strip()
        
        # Validate
        if len(name) < 2:
            caller.msg("|rName must be at least 2 characters.|n")
            return None  # Re-display this node
        
        if len(name) > 50:
            caller.msg("|rName must be 50 characters or less.|n")
            return None  # Re-display this node
        
        # Store and advance
        caller.ndb._clothing_data["name"] = name
        return {"goto": "clothing_desc"}
    
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
            return None  # Re-display this node
        
        if len(desc) > 500:
            caller.msg("|rDescription must be 500 characters or less.|n")
            return None  # Re-display this node
        
        # Store and advance
        caller.ndb._clothing_data["desc"] = desc
        return {"goto": "clothing_type_select"}
    
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
            return {"goto": "clothing_rarity"}
        elif choice == "2":
            caller.ndb._clothing_data["item_type"] = "armor"
            return {"goto": "armor_type_select"}
        else:
            caller.msg("|rChoose 1 or 2:|n")
            return None
    
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
            return {"goto": "armor_value"}
        elif choice == "2":
            caller.ndb._clothing_data["armor_type"] = "medium"
            return {"goto": "armor_value"}
        elif choice == "3":
            caller.ndb._clothing_data["armor_type"] = "heavy"
            return {"goto": "armor_value"}
        else:
            caller.msg("|rChoose 1, 2, or 3:|n")
            return None
    
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
                return {"goto": "clothing_rarity"}
            else:
                caller.msg("|rEnter a number between 1 and 10.|n")
                return None
        except ValueError:
            caller.msg("|rPlease enter a valid number.|n")
            return None
    
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
            return {"goto": "clothing_save"}
        else:
            caller.msg("|rChoose 1, 2, 3, or 4:|n")
            return None
    
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
    
    return text, [{"key": "_default", "exec": lambda c, rs: ("", [])}]
