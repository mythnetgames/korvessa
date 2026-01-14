from evennia import Command
import time
import math
from datetime import datetime

# Import IP functions for display
from world.combat.utils import ip_cost_for_next_point, SKILL_MAX


def format_raw_skill(value):
    """
    Format a skill value to show hundredths place.
    
    Rounding rules:
    - If thousandths digit < 5: round down (truncate)
    - If thousandths digit >= 5: round up
    """
    if isinstance(value, int):
        return f"{value}.00"
    
    if value == 0:
        return "0.00"
    
    # Get to 3 decimal places for rounding decision
    thousandths = int(abs(value) * 1000) % 10
    
    if thousandths >= 5:
        # Round up to hundredths
        rounded = math.ceil(value * 100) / 100
    else:
        # Round down (truncate) to hundredths
        rounded = math.floor(value * 100) / 100
    
    return f"{rounded:.2f}"


def get_effective_skill(raw_value):
    """
    Get the effective (integer) skill value from a raw value.
    Round down unless thousandths >= 5.
    """
    if isinstance(raw_value, int):
        return raw_value
    
    if raw_value == 0:
        return 0
    
    thousandths = int(abs(raw_value) * 1000) % 10
    
    if thousandths >= 5:
        return math.ceil(raw_value)
    else:
        return math.floor(raw_value)


class CmdStats(Command):
    """
    View your character's stats.
    Usage: stats
    Aliases: sc, score
    """
    key = "stats"
    aliases = ["sc", "score"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        char = self.caller
        # Stat definitions: (attribute, display name, abbreviation)
        stats = [
            ("smrt", "Smarts", "SMRT"),
            ("will", "Willpower", "WILL"),
            ("edge", "Edge", "EDGE"),
            ("ref", "Reflexes", "REF"),
            ("body", "Body", "BODY"),
            ("dex", "Dexterity", "DEX"),
            ("emp", "Empathy", "EMP"),
            ("tech", "Technique", "TECH"),
        ]
        # Two-column display
        left_stats = stats[:4]
        right_stats = stats[4:]
        msg = "|ystats|n\n"
        # Get stat values (current/max)
        def stat_line(attr, name, abbr):
            # Empathy is now calculated via property (edge + willpower) / 2
            # All stats use the same logic now
            val = getattr(char, attr, 0)
            maxval = getattr(char, f"max_{attr}", val)
            return f"|#dfdf00{name:<10}|n [ |w{val}|n / |g{maxval}|n ]"
        # Build two columns
        for i in range(4):
            left = left_stats[i]
            right = right_stats[i]
            msg += f"{stat_line(*left):<25}{stat_line(*right):<25}\n"
        
        # Consciousness backup status - shown right below stats
        clone_backup = getattr(char.db, 'clone_backup', None)
        if clone_backup:
            # Has consciousness backup - show in bright green with timestamp
            backup_timestamp = clone_backup.get('timestamp', 0)
            backup_datetime = datetime.fromtimestamp(backup_timestamp)
            formatted_time = backup_datetime.strftime("%Y-%m-%d %H:%M:%S")
            msg += f"\n|G[ CONSCIOUSNESS BACKUP ACTIVE ]|n |gLast Updated: {formatted_time}|n\n"
        else:
            # No consciousness backup - show warning in bright red
            msg += f"\n|R[ NO CONSCIOUSNESS BACKUP - DEATH IS PERMANENT ]|n\n"
        
        # Chrome/augmentations section
        chrome_list = getattr(char.db, 'installed_chrome_list', None)
        if chrome_list and isinstance(chrome_list, list) and len(chrome_list) > 0:
            msg += "\n|#870000Chrome & Augmentations:|n\n"
            for chrome in chrome_list:
                chrome_name = chrome.get("name", "Unknown")
                chrome_slot = chrome.get("slot", "unknown")
                msg += f"  |y{chrome_name}|n ({chrome_slot})\n"
        else:
            msg += "\n|#870000No chrome or augmentations.|n\n"
        
        # Investment Points (IP) section
        current_ip = getattr(char.db, 'ip', 0) or 0
        msg += f"\n|y[ Investment Points: |w{current_ip}|y IP ]|n"
        msg += f" |xType 'invest' to spend IP on skills.|n\n"
        
        # Skill table with raw values showing hundredths
        skills = [
            ("Chemical", "chemical"),
            ("Modern Medicine", "modern_medicine"),
            ("Holistic Medicine", "holistic_medicine"),
            ("Surgery", "surgery"),
            ("Science", "science"),
            ("Dodge", "dodge"),
            ("Blades", "blades"),
            ("Pistols", "pistols"),
            ("Rifles", "rifles"),
            ("Melee", "melee"),
            ("Brawling", "brawling"),
            ("Martial Arts", "martial_arts"),
            ("Grappling", "grappling"),
            ("Athletics", "athletics"),
            ("Snooping", "snooping"),
            ("Stealing", "stealing"),
            ("Hiding", "hiding"),
            ("Sneaking", "sneaking"),
            ("Disguise", "disguise"),
            ("Tailoring", "tailoring"),
            ("Tinkering", "tinkering"),
            ("Manufacturing", "manufacturing"),
            ("Cooking", "cooking"),
            ("Forensics", "forensics"),
            ("Decking", "decking"),
            ("Electronics", "electronics"),
            ("Mercantile", "mercantile"),
            ("Streetwise", "streetwise"),
            ("Paint/Draw/Sculpt", "paint_draw_sculpt"),
            ("Instrument", "instrument"),
        ]
        
        # Underlined header, 'Raw' aligned to column 21
        msg += "\n|#ffff00|[#00005f|uSkill                Raw     Eff|n\n"
        for display_name, attr_name in skills:
            raw = getattr(char.db, attr_name, 0) or 0
            raw_formatted = format_raw_skill(raw)
            effective = get_effective_skill(raw)
            
            # Color code based on skill level
            if effective >= 90:
                eff_color = "|M"  # Magenta/purple for mastery
            elif effective >= 76:
                eff_color = "|C"  # Cyan for advanced
            elif effective >= 46:
                eff_color = "|G"  # Green for professional
            elif effective >= 21:
                eff_color = "|Y"  # Yellow for competent
            elif effective > 0:
                eff_color = "|w"  # White for novice
            else:
                eff_color = "|x"  # Grey for untrained
            
            msg += f"{display_name:<20}{raw_formatted:>7}  {eff_color}{effective:>3}|n\n"
        
        char.msg(msg)
