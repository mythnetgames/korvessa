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


def get_effective_skill(raw_value, char=None, skill_attr=None):
    """
    Get the effective (integer) skill value from a raw value.
    Round down unless thousandths >= 5.
    Applies room tag bonuses if character and skill are provided.
    """
    if isinstance(raw_value, int) and raw_value == 0 and char is None:
        return raw_value
    
    if raw_value == 0:
        effective = 0
    else:
        thousandths = int(abs(raw_value) * 1000) % 10
        
        if thousandths >= 5:
            effective = math.ceil(raw_value)
        else:
            effective = math.floor(raw_value)
    
    # Apply room tag bonuses if character and location are available
    if char and skill_attr and char.location:
        from world.room_tags import get_room_skill_bonuses
        bonuses = get_room_skill_bonuses(char.location)
        if skill_attr in bonuses:
            effective += bonuses[skill_attr]
    
    return effective


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
            ("str", "Strength", "STR"),
            ("dex", "Dexterity", "DEX"),
            ("con", "Constitution", "CON"),
            ("int", "Intelligence", "INT"),
            ("wis", "Wisdom", "WIS"),
            ("cha", "Charisma", "CHA"),
        ]
        # Two-column display
        left_stats = stats[:3]
        right_stats = stats[3:]
        msg = "|ystats|n\n"
        # Get stat values (current/max)
        def stat_line(attr, name, abbr):
            # D&D stats use the same logic
            val = getattr(char, attr, 10)
            return f"|#dfdf00{name:<15}|n [ |w{val}|n ]"
        # Build two columns
        for i in range(3):
            left = left_stats[i]
            right = right_stats[i]
            msg += f"{stat_line(*left):<30}{stat_line(*right):<30}\n"
        
        # Investment Points (IP) section
        current_ip = getattr(char.db, 'ip', 0) or 0
        msg += f"\n|y[ Investment Points: |w{current_ip}|y IP ]|n"
        msg += f" |xType 'invest' to spend IP on skills.|n\n"
        
        # Skill table organized by domain
        skills_by_domain = {
            "COMBAT": [
                ("Dodge", "dodge"),
                ("Parry", "parry"),
                ("Blades", "blades"),
                ("Ranged", "ranged"),
                ("Melee", "melee"),
                ("Brawling", "brawling"),
                ("Grappling", "grappling"),
            ],
            "STEALTH/SUBTERFUGE": [
                ("Lockpicking", "lockpicking"),
                ("Stealing", "stealing"),
                ("Stealth", "stealth"),
                ("Disguise", "disguise"),
            ],
            "SOCIAL": [
                ("Haggle", "haggle"),
                ("Persuasion", "persuasion"),
                ("Streetwise", "streetwise"),
            ],
            "CRAFTING": [
                ("Carpentry", "carpentry"),
                ("Herbalism", "herbalism"),
                ("Tailoring", "tailoring"),
                ("Cooking", "cooking"),
            ],
            "SURVIVAL": [
                ("Tracking", "tracking"),
                ("Foraging", "foraging"),
            ],
            "LORE": [
                ("Investigation", "investigation"),
                ("Lore", "lore"),
                ("Appraise", "appraise"),
            ],
            "MEDICAL": [
                ("First Aid", "first_aid"),
                ("Chirurgy", "chirurgy"),
            ],
            "CREATIVE": [
                ("Arts", "arts"),
                ("Instrument", "instrument"),
            ],
        }
        
        def format_skill_line(display_name, attr_name, char):
            """Format a single skill line with value and color coding."""
            raw = getattr(char.db, attr_name, 0) or 0
            effective = get_effective_skill(raw, char=char, skill_attr=attr_name)
            
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
            
            # Format with any bonus/malus indicators
            bonus_indicator = ""
            if effective > math.floor(raw):
                bonus_indicator = f" |G(+{effective - math.floor(raw)})|n"
            elif effective < math.floor(raw):
                bonus_indicator = f" |R({effective - math.floor(raw)})|n"
            
            return f"{display_name:<18} {eff_color}{effective:>3}|n{bonus_indicator}"
        
        # Split domains into left (0-3) and right (4-7)
        domain_list = list(skills_by_domain.items())
        left_domains = domain_list[:4]
        right_domains = domain_list[4:]
        
        msg += "\n"
        
        # Generate lines for left and right columns
        left_lines = []
        right_lines = []
        
        # Generate left column
        for domain, skills in left_domains:
            left_lines.append(f"|#ffff00{domain}:|n")
            for display_name, attr_name in skills:
                left_lines.append(f"  {format_skill_line(display_name, attr_name, char)}")
            left_lines.append("")  # Blank line between domains
        
        # Generate right column
        for domain, skills in right_domains:
            right_lines.append(f"|#ffff00{domain}:|n")
            for display_name, attr_name in skills:
                right_lines.append(f"  {format_skill_line(display_name, attr_name, char)}")
            right_lines.append("")  # Blank line between domains
        
        # Combine into two columns
        max_lines = max(len(left_lines), len(right_lines))
        for i in range(max_lines):
            left_text = left_lines[i] if i < len(left_lines) else ""
            right_text = right_lines[i] if i < len(right_lines) else ""
            
            # Pad left column to consistent width
            if right_text:
                msg += f"{left_text:<50} {right_text}\n"
            else:
                msg += f"{left_text}\n"
        
        char.msg(msg)
