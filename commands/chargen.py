"""
Character Generation (Chargen) and Introduction System for Korvessa

Handles step-by-step character creation, stat assignment, personality, skills, standing, and public knowledge.
"""

from evennia.commands.command import Command as BaseCommand
from evennia.utils.evtable import EvTable
from evennia.utils.evmenu import EvMenu

CHARGEN_STEPS = [
    "race",
    "personality",
    "stats",
    "skills",
    "standing",
    "background",
    "public_knowledge",
    "review",
]

STAT_INFO = {
    "STR": ("Physical strength", "Melee damage, shove/grapple success, labor tasks"),
    "DEX": ("Agility, precision", "Hit chance, stealth, lockpicking, crafting finesse"),
    "CON": ("Resilience & stamina", "HP, stamina drain, injury thresholds, regen"),
    "INT": ("Knowledge & analysis", "Crafting complexity, learning rate, investigation"),
    "WIS": ("Perception & intuition", "Detect hidden, sense motive, ritual aptitude"),
    "CHA": ("Influence & presence", "Prices, persuasion, intimidation, NPC attitude"),
}

STANDING_GROUPS = [
    "Civic_Order", "Laborers", "Merchants", "Nobility", "Underbelly", "Watcher_Cult", "Scholars", "Feyliks_Freefolk"
]

STANDING_THRESHOLDS = [
    (1000, "Trusted"),
    (200, "Favored"),
    (-199, "Neutral"),
    (-200, "Distrusted"),
    (-2000, "Hated"),
]

PUBLIC_KNOWLEDGE_FIELDS = [
    ("Name as Known", "Street/common name"),
    ("Apparent Age", "Helps perception-based rolls"),
    ("Appearance Notes", "Visible traits only"),
    ("Common Rumors", "Everyday gossip"),
    ("Known Affiliations", "Based on Standing or RP"),
    ("Reputation Tier", "Minor, Moderate, Strong"),
]

class CmdChargen(BaseCommand):
    """
    Begin or continue character creation using EvMenu.
    Usage:
        chargen
    """
    key = "chargen"
    locks = "cmd:all()"
    help_category = "Character"

    def func(self):
        """Launch EvMenu-based chargen."""
        account = self.caller.account if hasattr(self.caller, 'account') else self.caller
        char = getattr(account, 'current_character', None)
        # If no selected character, use self.caller if it is a Character instance
        from typeclasses.characters import Character
        if not char and isinstance(self.caller, Character):
            char = self.caller
        if not char:
            self.caller.msg("|r[ERROR]|n You must select or create a character first.")
            return
        EvMenu(self.caller, "commands.chargen", startnode="node_intro", persistent=True, cmd_on_exit=None, auto_quit=True, startnode_input=char)

# --- EvMenu Nodes for Chargen ---
def node_intro(caller, raw_string, **kwargs):
    char = kwargs.get("startnode_input")
    text = (
        "|wWelcome to Korvessa Character Creation!|n\n\n"
        "You will be guided through a series of steps to define your character's race, stats, personality, skills, social standing, and public knowledge.\n\n"
        "Type |cnext|n to begin."
    )
    options = (
        {"desc": "Begin character creation", "goto": "node_race", "key": ("next", "begin", "start", 1)},
    )
    return text, options

RACES = [
    ("Human", "Versatile and ambitious, found everywhere."),
    ("Elf", "Graceful, keen senses, attuned to nature and magic."),
    ("Dwarf", "Stout, hardy, skilled with craft and stone."),
    ("Orc", "Strong, resilient, often misunderstood."),
    ("Fey", "Mysterious, magical, and unpredictable."),
    ("Halfling", "Small, nimble, and lucky."),
    ("Beastkin", "Animal traits, keen instincts, and senses."),
    # 'Immortal' is reserved for admin/staff and not shown in chargen
]

def node_race(caller, raw_string, **kwargs):
    char = kwargs.get("startnode_input")
    if raw_string:
        choice = raw_string.strip().lower()
        for idx, (race, desc) in enumerate(RACES, 1):
            if choice == str(idx) or choice == race.lower():
                char.db.race = race
                caller.msg(f"|gYou have selected:|n {race} - {desc}")
                return "node_personality"
        caller.msg("|rInvalid race. Please choose by number or name.")
    table = EvTable("#", "Race", "Description")
    for idx, (race, desc) in enumerate(RACES, 1):
        table.add_row(str(idx), race, desc)
    text = (
        "|w[CHARGEN]|n Select your character's race.\n" + str(table) +
        "\nType the |cnumber|n or |cname|n of your choice."
    )
    options = tuple()
    return text, options

# Top-level chargen steps and questions
CHARGEN_STEPS = [
    "race",
    "personality",

        "stats",
        "skills",
        "standing",
        "background",
        "public_knowledge",
        "application_questions",
        "review",
    ]

# Application questions for approval
APPLICATION_QUESTIONS = [
    ("Character Motivation", "What drives your character? What are their goals or ambitions?"),
    ("Roleplay Sample", "Write a short in-character scene or dialogue to demonstrate how you will play this character."),
    ("Player Intent", "What do you hope to explore or accomplish with this character on Korvessa?")
]

# Personality options
PERSONALITIES = [
    ("Sharp-Eyed", "Observant, quick to notice details and changes."),
    ("Silver-Tongued", "Persuasive, charming, and socially adept."),
    ("Brooding", "Quiet, intense, and thoughtful."),
    ("Reckless", "Bold, daring, and sometimes impulsive."),
    ("Scholarly", "Curious, analytical, and loves learning."),
    ("Fey-Touched", "Unpredictable, whimsical, and creative."),
]

def node_personality(caller, raw_string, **kwargs):
    char = kwargs.get("startnode_input")
    if raw_string:
        choice = raw_string.strip().lower()
        for idx, (personality, desc) in enumerate(PERSONALITIES, 1):
            if choice == str(idx) or choice == personality.lower():
                char.db.personality = personality
                caller.msg(f"|gYou have selected:|n {personality} - {desc}")
                return "node_stats"
        caller.msg("|rInvalid personality. Please choose by number or name.")
    table = EvTable("#", "Personality", "Description")
    for idx, (personality, desc) in enumerate(PERSONALITIES, 1):
        table.add_row(str(idx), personality, desc)
    text = (
        "|w[CHARGEN]|n Select your character's personality.\n" + str(table) +
        "\nType the |cnumber|n or |cname|n of your choice."
    )
    options = tuple()
    return text, options


# D&D 5e point buy config
POINT_BUY_START = 8
POINT_BUY_MAX = 15
POINT_BUY_MIN = 8
POINT_BUY_TOTAL = 27
POINT_BUY_COSTS = {8:0, 9:1, 10:2, 11:3, 12:4, 13:5, 14:7, 15:9}

def calc_point_buy_cost(stats):
    total = 0
    for val in stats.values():
        total += POINT_BUY_COSTS.get(val, 100)  # 100 = illegal
    return total

def node_stats(caller, raw_string, **kwargs):
    char = kwargs.get("startnode_input")
    stat_keys = list(STAT_INFO.keys())
    # Initialize if not set
    if not hasattr(char.db, 'stat_assign') or not char.db.stat_assign:
        char.db.stat_assign = {k: POINT_BUY_START for k in stat_keys}
    stats = char.db.stat_assign
    # Handle input
    if raw_string:
        parts = raw_string.strip().upper().split()
        if len(parts) == 2 and parts[0] in stat_keys and parts[1].lstrip("+-").isdigit():
            stat, amt = parts[0], int(parts[1])
            new_val = stats[stat] + amt
            if new_val < POINT_BUY_MIN or new_val > POINT_BUY_MAX:
                caller.msg(f"|r{stat} must be between {POINT_BUY_MIN} and {POINT_BUY_MAX}.|n")
            else:
                # Calculate new cost
                temp_stats = stats.copy()
                temp_stats[stat] = new_val
                cost = calc_point_buy_cost(temp_stats)
                if cost > POINT_BUY_TOTAL:
                    caller.msg(f"|rNot enough points. You have {POINT_BUY_TOTAL - calc_point_buy_cost(stats)} left.|n")
                else:
                    stats[stat] = new_val
                    caller.msg(f"|g{stat} set to {new_val}.|n")
        elif raw_string.strip().lower() in ("next", "done", "finish", "1"):
            cost = calc_point_buy_cost(stats)
            if cost != POINT_BUY_TOTAL:
                caller.msg(f"|rYou must spend exactly {POINT_BUY_TOTAL} points (currently spent: {cost}).|n")
            else:
                char.db.stats = stats.copy()
                del char.db.stat_assign
                return "node_skills"
        else:
            caller.msg("|rUsage: <STAT> <amount> (e.g. STR 2, DEX -1), or 'next' to continue.")
    # Show table
    table = EvTable("Stat", "Value", "Meaning", "Influence", "Cost")
    for stat in stat_keys:
        meaning, influence = STAT_INFO[stat]
        val = stats[stat]
        cost = POINT_BUY_COSTS.get(val, "-")
        table.add_row(stat, str(val), meaning, influence, str(cost))
    spent = calc_point_buy_cost(stats)
    text = (
        f"|w[CHARGEN]|n Assign your stats using D&D 5e point buy.\nYou have |c{POINT_BUY_TOTAL - spent}|n points left.\n"
        f"Stats must be between {POINT_BUY_MIN} and {POINT_BUY_MAX}.\n"
        "Usage: <STAT> <amount> (e.g. STR 2, DEX -1)\n"
        "Type |cnext|n when done.\n" + str(table)
    )
    options = tuple()
    return text, options

SKILL_GROUPS = [
    ("Combat", "Weapons, tactics, and fighting."),
    ("Stealth", "Sneaking, hiding, and subtlety."),
    ("Social", "Persuasion, deception, and leadership."),
    ("Crafting", "Making, repairing, and inventing."),
    ("Survival", "Wilderness, foraging, and endurance."),
    ("Lore", "Knowledge, research, and history."),
    ("Medical", "Healing, diagnosis, and care."),
]

def node_skills(caller, raw_string, **kwargs):
    char = kwargs.get("startnode_input")
    if raw_string:
        choice = raw_string.strip().lower()
        for idx, (group, desc) in enumerate(SKILL_GROUPS, 1):
            if choice == str(idx) or choice == group.lower():
                char.db.skill_group = group
                caller.msg(f"|gYou have selected:|n {group} - {desc}")
                return "node_standing"
        caller.msg("|rInvalid skill group. Please choose by number or name.")
    table = EvTable("#", "Skill Group", "Description")
    for idx, (group, desc) in enumerate(SKILL_GROUPS, 1):
        table.add_row(str(idx), group, desc)
    text = (
        "|w[CHARGEN]|n Select your primary skill group.\n" + str(table) +
        "\nType the |cnumber|n or |cname|n of your choice."
    )
    options = tuple()
    return text, options

def node_standing(caller, raw_string, **kwargs):
    char = kwargs.get("startnode_input")
    # Standing assignment config
    pool = 5
    if not hasattr(char.db, 'standing_assign') or not char.db.standing_assign:
        char.db.standing_assign = {k: 0 for k in STANDING_GROUPS}
        char.db.standing_pool = pool
    standing = char.db.standing_assign
    points = char.db.standing_pool
    if raw_string:
        parts = raw_string.strip().split()
        if len(parts) == 2 and parts[0] in STANDING_GROUPS and parts[1].lstrip("+-").isdigit():
            group, amt = parts[0], int(parts[1])
            if amt > 0 and points >= amt:
                standing[group] += amt
                char.db.standing_pool -= amt
                caller.msg(f"|gAdded {amt} to {group}.|n")
            elif amt < 0 and standing[group] + amt >= 0:
                standing[group] += amt
                char.db.standing_pool -= amt
                caller.msg(f"|yRemoved {-amt} from {group}.|n")
            else:
                caller.msg("|rInvalid standing change.|n")
        elif raw_string.strip().lower() in ("next", "done", "finish", "1"):
            if points > 0:
                caller.msg(f"|rYou must assign all points before continuing.|n")
            else:
                char.db.standing = standing.copy()
                del char.db.standing_assign
                del char.db.standing_pool
                return "node_background"
        else:
            caller.msg("|rUsage: <FACTION> <amount> (e.g. Merchants 2, Nobility -1), or 'next' to continue.")
    table = EvTable("Faction", "Points")
    for group in STANDING_GROUPS:
        table.add_row(group, str(standing[group]))
    text = (
        f"|w[CHARGEN]|n Assign your social standing.\nYou have |c{char.db.standing_pool}|n points to distribute.\n"
        "Usage: <FACTION> <amount> (e.g. Merchants 2, Nobility -1)\n"
        "Type |cnext|n when done.\n" + str(table)
    )
    options = tuple()
    return text, options

def node_background(caller, raw_string, **kwargs):
    char = kwargs.get("startnode_input")
    if not hasattr(char.db, 'background_entry'):
        char.db.background_entry = ""
    if raw_string:
        if raw_string.strip().lower() in ("next", "done", "finish", "1"):
            if not char.db.background_entry:
                caller.msg("|rPlease enter a background before continuing.|n")
            else:
                return "node_public_knowledge"
        else:
            char.db.background_entry = raw_string.strip()
            caller.msg("|gBackground saved. Type |cnext|n to continue.|n")
    text = (
        "|w[CHARGEN]|n Enter your character background.\n"
        "Type your background and press enter. When satisfied, type |cnext|n to continue.\n"
        f"Current: |w{char.db.background_entry}|n"
    )
    options = tuple()
    return text, options

def node_public_knowledge(caller, raw_string, **kwargs):
    char = kwargs.get("startnode_input")
    if not hasattr(char.db, 'public_knowledge_entry') or not char.db.public_knowledge_entry:
        char.db.public_knowledge_entry = {field: "" for field, _ in PUBLIC_KNOWLEDGE_FIELDS}
        char.db.public_knowledge_field = 0
    pk = char.db.public_knowledge_entry
    idx = char.db.public_knowledge_field
    fields = [field for field, _ in PUBLIC_KNOWLEDGE_FIELDS]
    if idx >= len(fields):
        char.db.public_knowledge = pk.copy()
        del char.db.public_knowledge_entry
        del char.db.public_knowledge_field
        return "node_review"
    field = fields[idx]
    if raw_string:
        if raw_string.strip().lower() in ("skip",):
            pk[field] = "(skipped)"
            char.db.public_knowledge_field += 1
            return node_public_knowledge(caller, "", **kwargs)
        elif raw_string.strip().lower() in ("next", "done", "finish", "1"):
            caller.msg("|rPlease enter a value or type 'skip' to skip this field.|n")
        else:
            pk[field] = raw_string.strip()
            char.db.public_knowledge_field += 1
            return node_public_knowledge(caller, "", **kwargs)
    notes = dict(PUBLIC_KNOWLEDGE_FIELDS)[field]
    text = (
        f"|w[CHARGEN]|n Enter your public knowledge: |c{field}|n\n"
        f"({notes})\n"
        f"Current: |w{pk[field]}|n\n"
        "Type your answer and press enter, or type |cskip|n to skip."
    )
    options = tuple()
    return text, options

def node_review(caller, raw_string, **kwargs):
    text = "|w[CHARGEN]|n Review your character and submit. (Stub)\nType |cdone|n to finish."
    options = (
        {"desc": "Finish character creation", "goto": "node_done", "key": ("done", "finish", 1)},
    )
    return text, options

def node_done(caller, raw_string, **kwargs):
    text = "|g[SUCCESS]|n Character creation is complete! Use |wic <name>|n to enter the world."
    options = ()
    return text, options
