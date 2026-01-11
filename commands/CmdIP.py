"""
Investment Points (IP) System Commands

Commands for managing the IP skill progression system:
- CmdIP: Admin command to grant/subtract IP
- CmdInvest: Player command to invest IP into skills
- CmdSetSkill: Admin command to directly set skill values

IP Reward Guidelines:
- Tiny reward (1-5 IP): Minor RP contribution, participation
- Small reward (5-15 IP): Good scene participation, completing simple tasks
- Moderate reward (15-30 IP): Excellent RP, moderate story contribution
- Large reward (30-50 IP): Significant plot advancement, exceptional RP
- Major reward (50-100 IP): Major story arc completion, outstanding contribution

Automatic IP grants (every 4 hours): 2-5 IP for logged-in players
"""

from evennia import Command
from evennia.utils import evmenu
from evennia.utils.evtable import EvTable
import math

# Import IP functions from combat utils
from world.combat.utils import (
    ip_cost_for_next_point, 
    total_ip_to_reach, 
    ip_spent_in_skill,
    SKILL_MAX
)

# List of all skills in the game
SKILL_LIST = [
    "chemical", "modern_medicine", "holistic_medicine", "surgery", "science",
    "dodge", "blades", "pistols", "rifles", "melee", "brawling", "martial_arts",
    "grappling", "snooping", "stealing", "hiding", "sneaking", "disguise",
    "tailoring", "tinkering", "manufacturing", "cooking", "forensics",
    "decking", "electronics", "mercantile", "streetwise", "paint_draw_sculpt",
    "instrument", "athletics"
]

# Skill name display mapping (for pretty printing)
SKILL_DISPLAY_NAMES = {
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
    "athletics": "Athletics"
}


def normalize_skill_name(name):
    """
    Convert a skill name to its internal format.
    Handles spaces, slashes, and case variations.
    """
    # Strip and lowercase
    name = name.strip().lower()
    # Replace spaces with underscores
    name = name.replace(" ", "_")
    # Replace slashes with underscores
    name = name.replace("/", "_")
    return name


def get_skill_display_name(internal_name):
    """Get the display name for a skill."""
    return SKILL_DISPLAY_NAMES.get(internal_name, internal_name.replace("_", " ").title())


def format_raw_skill(value):
    """
    Format a skill value to show hundredths place.
    
    Rounding rules:
    - If thousandths digit < 5: round down (truncate)
    - If thousandths digit >= 5: round up
    
    Args:
        value: The skill value (can be int or float)
        
    Returns:
        str: Formatted string like "45.12" or "45.00"
    """
    if isinstance(value, int):
        return f"{value}.00"
    
    # Get to 3 decimal places for rounding decision
    thousandths = int(value * 1000) % 10
    
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
    
    For combat/skill checks, we use the floor of the raw value,
    UNLESS buffs push the thousandths to >= 5, then round up.
    
    Args:
        raw_value: The raw skill value (can be float)
        
    Returns:
        int: The effective integer skill value
    """
    if isinstance(raw_value, int):
        return raw_value
    
    # Check thousandths place for rounding decision
    thousandths = int(raw_value * 1000) % 10
    
    if thousandths >= 5:
        return math.ceil(raw_value)
    else:
        return math.floor(raw_value)


class CmdIP(Command):
    """
    Admin command to grant or subtract IP from a player.
    
    Usage:
        ip <character> <amount>
        ip <character> +<amount>
        ip <character> -<amount>
        ip <character>
    
    Examples:
        ip Bob 50          - Grant Bob 50 IP
        ip Bob +50         - Grant Bob 50 IP  
        ip Bob -25         - Subtract 25 IP from Bob
        ip Bob             - View Bob's current IP
    
    IP Reward Guidelines:
        Tiny (1-5 IP):     Minor RP, participation
        Small (5-15 IP):   Good scene, simple tasks
        Moderate (15-30):  Excellent RP, story contribution
        Large (30-50):     Plot advancement, exceptional RP
        Major (50-100):    Story arc completion, outstanding work
    """
    
    key = "ip"
    aliases = ["grantip", "awardip"]
    locks = "cmd:perm(Admin) or perm(Builder)"
    help_category = "Admin"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: ip <character> [+/-]<amount>")
            caller.msg("       ip <character>  (to view current IP)")
            return
        
        args = self.args.strip().split()
        
        if len(args) < 1:
            caller.msg("You must specify a character.")
            return
        
        # Find the target character
        char_name = args[0]
        target = caller.search(char_name, global_search=True)
        
        if not target:
            return  # search() already sends error message
        
        # Check if target is a character
        if not hasattr(target, 'db'):
            caller.msg(f"{target.key} is not a valid character.")
            return
        
        # Get current IP
        current_ip = getattr(target.db, 'ip', 0) or 0
        
        # If no amount specified, just show current IP
        if len(args) < 2:
            caller.msg(f"|c{target.key}|n has |y{current_ip}|n IP.")
            return
        
        # Parse the amount
        amount_str = args[1]
        
        try:
            if amount_str.startswith('+'):
                amount = int(amount_str[1:])
            elif amount_str.startswith('-'):
                amount = -int(amount_str[1:])
            else:
                amount = int(amount_str)
        except ValueError:
            caller.msg(f"'{amount_str}' is not a valid number.")
            return
        
        # Apply the change
        new_ip = current_ip + amount
        
        # Don't allow negative IP
        if new_ip < 0:
            caller.msg(f"Cannot reduce IP below 0. {target.key} only has {current_ip} IP.")
            return
        
        target.db.ip = new_ip
        
        # Force save to ensure persistence
        if hasattr(target, 'save'):
            target.save()
        
        # Send messages
        if amount > 0:
            caller.msg(f"|gGranted {amount} IP to {target.key}.|n New total: |y{new_ip}|n IP")
            target.msg(f"|g[+{amount} IP]|n You have received Investment Points! New total: |y{new_ip}|n IP")
        elif amount < 0:
            caller.msg(f"|rSubtracted {abs(amount)} IP from {target.key}.|n New total: |y{new_ip}|n IP")
            target.msg(f"|r[-{abs(amount)} IP]|n Investment Points deducted. New total: |y{new_ip}|n IP")
        else:
            caller.msg(f"No change made. {target.key} has |y{new_ip}|n IP.")


class CmdSetSkill(Command):
    """
    Admin command to directly set a character's skill value.
    Use this when a player has put in the work and deserves a skill adjustment.
    
    Usage:
        setskill <character> <skill> <value>
        setskill <character> <skill> +<amount>
        setskill <character> <skill> -<amount>
    
    Examples:
        setskill Bob brawling 50     - Set Bob's brawling to 50
        setskill Bob brawling +10    - Add 10 to Bob's brawling
        setskill Bob "martial arts" 75  - Set martial arts to 75
    
    Skills can exceed 100 with buffs, but base values should typically cap at 100.
    """
    
    key = "setskill"
    aliases = ["skillset", "adminskill"]
    locks = "cmd:perm(Admin) or perm(Builder)"
    help_category = "Admin"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: setskill \"<character>\" <skill> <value>")
            caller.msg("       setskill \"<character>\" <skill> +/-<amount>")
            return
        
        import shlex
        try:
            args = shlex.split(self.args.strip())
        except ValueError:
            caller.msg("Invalid quoting in arguments.")
            return
        
        if len(args) < 3:
            caller.msg("Usage: setskill \"<character>\" <skill> <value>")
            return
        
        char_name, skill_name, value_str = args[0], args[1], args[2]
        
        # Find target character
        target = caller.search(char_name, global_search=True)
        if not target:
            return
        
        if not hasattr(target, 'db'):
            caller.msg(f"{target.key} is not a valid character.")
            return
        
        # Normalize skill name
        skill_internal = normalize_skill_name(skill_name)
        
        if skill_internal not in SKILL_LIST:
            caller.msg(f"Unknown skill: {skill_name}")
            caller.msg(f"Valid skills: {', '.join(sorted(SKILL_DISPLAY_NAMES.values()))}")
            return
        
        # Get current value
        current_value = getattr(target.db, skill_internal, 0) or 0
        
        # Parse value
        try:
            if value_str.startswith('+'):
                new_value = current_value + float(value_str[1:])
            elif value_str.startswith('-'):
                new_value = current_value - float(value_str[1:])
            else:
                new_value = float(value_str)
        except ValueError:
            caller.msg(f"'{value_str}' is not a valid number.")
            return
        
        # Don't allow negative skills
        if new_value < 0:
            new_value = 0
        
        # Set the skill
        setattr(target.db, skill_internal, new_value)
        
        # Force save to ensure persistence
        if hasattr(target, 'save'):
            target.save()
        
        display_name = get_skill_display_name(skill_internal)
        formatted_value = format_raw_skill(new_value)
        
        caller.msg(f"|gSet {target.key}'s {display_name} to {formatted_value}|n (was {format_raw_skill(current_value)})")
        target.msg(f"|y[Skill Adjusted]|n Your {display_name} is now {formatted_value}")


class CmdInvest(Command):
    """
    Invest your IP (Investment Points) into skills.
    
    Usage:
        invest                      - View your IP and skill costs
        invest <skill>              - See cost to raise a skill
        invest <skill> <amount>     - Invest IP into a skill
        invest <skill> max          - Invest as much as possible
    
    Examples:
        invest brawling 10          - Invest 10 IP into Brawling
        invest "martial arts" 5     - Invest 5 IP into Martial Arts
        invest dodge max            - Max out Dodge with available IP
    
    Skills are capped at 100 base, but buffs can push them higher.
    The cost to raise a skill increases as it gets higher.
    """
    
    key = "invest"
    aliases = ["train", "improve"]
    locks = "cmd:all()"
    help_category = "Character"
    
    def func(self):
        caller = self.caller
        
        # Get current IP
        current_ip = getattr(caller.db, 'ip', 0) or 0
        
        if not self.args:
            # Show IP overview and skill tier costs
            self._show_ip_overview(caller, current_ip)
            return
        
        args = self.args.strip().split()
        
        # Handle quoted skill names
        if self.args.strip().startswith('"'):
            # Find the closing quote
            end_quote = self.args.find('"', 1)
            if end_quote > 0:
                skill_name = self.args[1:end_quote]
                remaining = self.args[end_quote+1:].strip().split()
                amount_str = remaining[0] if remaining else None
            else:
                caller.msg("Invalid syntax. Close your quotes.")
                return
        else:
            skill_name = args[0]
            amount_str = args[1] if len(args) > 1 else None
        
        # Normalize skill name
        skill_internal = normalize_skill_name(skill_name)
        
        if skill_internal not in SKILL_LIST:
            caller.msg(f"|rUnknown skill:|n {skill_name}")
            caller.msg(f"Type |yinvest|n to see all skills.")
            return
        
        # Get current skill value
        current_raw = getattr(caller.db, skill_internal, 0) or 0
        current_int = get_effective_skill(current_raw)
        display_name = get_skill_display_name(skill_internal)
        
        # If no amount, show cost info for this skill
        if not amount_str:
            self._show_skill_cost(caller, skill_internal, display_name, current_raw, current_int, current_ip)
            return
        
        # Parse investment amount
        if amount_str.lower() == 'max':
            # Calculate max investable
            ip_to_invest = current_ip
        else:
            try:
                ip_to_invest = int(amount_str)
            except ValueError:
                caller.msg(f"'{amount_str}' is not a valid number. Use a number or 'max'.")
                return
        
        if ip_to_invest <= 0:
            caller.msg("You must invest a positive amount of IP.")
            return
        
        if ip_to_invest > current_ip:
            caller.msg(f"|rYou only have {current_ip} IP available.|n")
            return
        
        # Calculate what the investment would yield
        new_skill_int, remaining_ip, ip_spent = self._calculate_investment(
            current_int, ip_to_invest
        )
        
        if ip_spent == 0:
            if current_int >= SKILL_MAX:
                caller.msg(f"|y{display_name}|n is already at maximum (100).")
            else:
                next_cost = ip_cost_for_next_point(current_int)
                caller.msg(f"|rInsufficient IP.|n You need |y{next_cost}|n IP to raise {display_name} to {current_int + 1}.")
            return
        
        # Calculate the new raw value (keep any decimal from buffs, add integer skill gain)
        skill_gain = new_skill_int - current_int
        new_raw = current_raw + skill_gain
        
        # Show preview and ask for confirmation
        self._confirm_investment(
            caller, skill_internal, display_name,
            current_raw, new_raw, current_int, new_skill_int,
            ip_spent, current_ip
        )
    
    def _show_ip_overview(self, caller, current_ip):
        """Show IP overview and tier information."""
        msg = []
        msg.append(f"|y=== Investment Points ===|n")
        msg.append(f"Current IP: |g{current_ip}|n")
        msg.append("")
        msg.append("Usage: |yinvest <skill> <amount>|n or |yinvest <skill> max|n")
        
        caller.msg("\n".join(msg))
    
    def _show_skill_cost(self, caller, skill_internal, display_name, current_raw, current_int, current_ip):
        """Show cost information for a specific skill."""
        msg = []
        msg.append(f"|y=== {display_name} ===|n")
        msg.append(f"Current: |w{format_raw_skill(current_raw)}|n (effective: {current_int})")
        
        if current_int >= SKILL_MAX:
            msg.append("|gThis skill is at maximum!|n")
        else:
            next_cost = ip_cost_for_next_point(current_int)
            msg.append(f"Cost for next point ({current_int}->{current_int+1}): |y{next_cost}|n IP")
            
            # Show how many points they could buy
            if current_ip >= next_cost:
                test_skill, test_remaining, test_spent = self._calculate_investment(current_int, current_ip)
                points_buyable = test_skill - current_int
                msg.append(f"With {current_ip} IP, you could raise to |g{test_skill}|n (+{points_buyable} points, {test_spent} IP)")
            else:
                msg.append(f"|rYou need {next_cost - current_ip} more IP for the next point.|n")
        
        msg.append("")
        msg.append(f"Usage: |yinvest {display_name.lower()} <amount>|n")
        
        caller.msg("\n".join(msg))
    
    def _calculate_investment(self, current_skill, ip_pool):
        """
        Calculate the result of investing IP into a skill.
        
        Returns:
            tuple: (new_skill_value, remaining_ip, total_spent)
        """
        skill = current_skill
        spent = 0
        
        while skill < SKILL_MAX and ip_pool > 0:
            cost = ip_cost_for_next_point(skill)
            if ip_pool >= cost:
                ip_pool -= cost
                spent += cost
                skill += 1
            else:
                break
        
        return skill, ip_pool, spent
    
    def _confirm_investment(self, caller, skill_internal, display_name,
                           current_raw, new_raw, current_int, new_int,
                           ip_cost, current_ip):
        """Start the confirmation menu for investment."""
        # Store data for the menu
        caller.ndb._invest_data = {
            'skill_internal': skill_internal,
            'display_name': display_name,
            'current_raw': current_raw,
            'new_raw': new_raw,
            'current_int': current_int,
            'new_int': new_int,
            'ip_cost': ip_cost,
            'current_ip': current_ip
        }
        
        # Show preview
        skill_gain = new_int - current_int
        remaining_ip = current_ip - ip_cost
        
        msg = []
        msg.append(f"|y=== Investment Preview ===|n")
        msg.append(f"|cSkill:|n {display_name}")
        msg.append(f"|cCurrent:|n {format_raw_skill(current_raw)} (effective: {current_int})")
        msg.append(f"|cNew:|n {format_raw_skill(new_raw)} (effective: {new_int})")
        msg.append(f"|cGain:|n +{skill_gain} skill points")
        msg.append(f"|cCost:|n {ip_cost} IP")
        msg.append(f"|cIP After:|n {remaining_ip}")
        msg.append("")
        msg.append("Type |gyes|n to confirm or |rno|n to cancel.")
        
        caller.msg("\n".join(msg))
        
        # Set up the confirmation state
        caller.ndb._awaiting_invest_confirm = True
        caller.cmdset.add("commands.CmdIP.InvestConfirmCmdSet")


class CmdInvestConfirm(Command):
    """Confirm or cancel an investment."""
    
    key = "yes"
    aliases = ["y", "confirm"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        if not getattr(caller.ndb, '_awaiting_invest_confirm', False):
            # Not in confirmation mode, treat as normal command
            caller.msg("What are you confirming?")
            return
        
        data = getattr(caller.ndb, '_invest_data', None)
        if not data:
            caller.msg("No investment pending.")
            self._cleanup(caller)
            return
        
        # Execute the investment
        skill_internal = data['skill_internal']
        new_raw = data['new_raw']
        ip_cost = data['ip_cost']
        current_ip = data['current_ip']
        display_name = data['display_name']
        
        # Apply the changes
        setattr(caller.db, skill_internal, new_raw)
        caller.db.ip = current_ip - ip_cost
        
        # Force save to ensure persistence
        if hasattr(caller, 'save'):
            caller.save()
        
        # Success message
        caller.msg(f"|g[Investment Complete]|n")
        caller.msg(f"{display_name}: {format_raw_skill(new_raw)} (effective: {data['new_int']})")
        caller.msg(f"IP Spent: {ip_cost} | Remaining IP: {current_ip - ip_cost}")
        
        self._cleanup(caller)
    
    def _cleanup(self, caller):
        """Clean up confirmation state."""
        if hasattr(caller.ndb, '_awaiting_invest_confirm'):
            del caller.ndb._awaiting_invest_confirm
        if hasattr(caller.ndb, '_invest_data'):
            del caller.ndb._invest_data
        caller.cmdset.remove("commands.CmdIP.InvestConfirmCmdSet")


class CmdInvestCancel(Command):
    """Cancel an investment."""
    
    key = "no"
    aliases = ["n", "cancel"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        if not getattr(caller.ndb, '_awaiting_invest_confirm', False):
            caller.msg("Nothing to cancel.")
            return
        
        caller.msg("|yInvestment cancelled.|n Your IP has not been spent.")
        
        # Cleanup
        if hasattr(caller.ndb, '_awaiting_invest_confirm'):
            del caller.ndb._awaiting_invest_confirm
        if hasattr(caller.ndb, '_invest_data'):
            del caller.ndb._invest_data
        caller.cmdset.remove("commands.CmdIP.InvestConfirmCmdSet")


from evennia import CmdSet

class InvestConfirmCmdSet(CmdSet):
    """Temporary cmdset for investment confirmation."""
    
    key = "invest_confirm"
    priority = 10
    mergetype = "Union"  # Add these commands alongside existing ones
    
    def at_cmdset_creation(self):
        self.add(CmdInvestConfirm())
        self.add(CmdInvestCancel())
