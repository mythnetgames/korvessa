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
        """Launch EvMenu-based chargen with resume/startover prompt."""
        account = self.caller.account if hasattr(self.caller, 'account') else self.caller
        char = getattr(account, 'current_character', None)
        from typeclasses.characters import Character
        if not char and isinstance(self.caller, Character):
            char = self.caller
        if not char:
            self.caller.msg("|r[ERROR]|n You must select or create a character first.")
            return
        # Always call node_intro and pass resume_stage if it exists
        last_stage = getattr(char.db, 'chargen_stage', None)
        EvMenu(self.caller, "commands.chargen", startnode="node_intro", persistent=True, cmd_on_exit=None, auto_quit=True, startnode_input=char, resume_stage=last_stage)

# --- EvMenu Nodes for Chargen ---
def node_intro(caller, raw_string, **kwargs):
    char = kwargs.get("startnode_input")
    if char is None and hasattr(caller, 'db'):
        char = caller
    resume_stage = kwargs.get("resume_stage", None)
    if raw_string and isinstance(raw_string, str):
        choice = raw_string.strip().lower()
        if choice in ("continue", "resume", "1") and resume_stage is not None:
            # Resume from last stage
            stages = CHARGEN_STEPS
            if 0 <= resume_stage < len(stages):
                char.db.chargen_stage = resume_stage
                return stages[resume_stage]
            else:
                char.db.chargen_stage = 0
                return "node_race"
    text = "|wWelcome to Korvessa Character Creation!|n\n\nYou will be guided through a series of steps to define your character.\n\n"
    options = []
    options.append({"desc": "Back", "goto": "node_intro", "key": "back"})
    chargen_stage = getattr(char.db, 'chargen_stage', None) if char is not None else None
    if chargen_stage is not None and chargen_stage > 0:
        text += "Would you like to continue from where you left off?\n"
        options.append({"desc": "Continue from last step", "goto": "node_intro", "key": "continue"})
    else:
        text += "Type |cnext|n to begin.\n"
        options.append({"desc": "Begin character creation", "goto": "node_race", "key": "next"})
    return text, tuple(options)

RACES = [
    ("Human", "Versatile and ambitious, found everywhere."),
    ("Elf", "Graceful, keen senses, attuned to nature and magic."),
    ("Dwarf", "Stout, hardy, skilled with craft and stone."),
]

def node_race(caller, raw_string, **kwargs):
    char = kwargs.get("startnode_input")
    if char is None and hasattr(caller, 'db'):
        char = caller
    if raw_string:
        choice = raw_string.strip().lower()
        for idx, (race, desc) in enumerate(RACES, 1):
            if choice == str(idx) or choice == race.lower():
                char.db.race = race
                return f"|gYou have selected:|n {race} - {desc}\n\nType |cnext|n to continue.", ( {"desc": "Continue", "goto": "node_personality", "key": "next"}, )
        caller.msg("|rInvalid race. Please choose by number or name.")
    # Show clickable race options
    text = "|wSelect your character's race:|n\n"
    options = []
    options.append({"desc": "Back", "goto": "node_intro", "key": "back"})
    for idx, (race, desc) in enumerate(RACES, 1):
        text += f"|c{idx}. {race}|n - {desc}\n"
        options.append({"desc": f"Choose {race}", "goto": "node_race", "key": str(idx)})
    return text, tuple(options)

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
    {
        "name": "Stalwart",
        "desc": "Resilient and tough. +1 STR or CON, Endurance +10%, Athletics +5%, Reduced stamina loss, Laborers +200",
        "stat_choices": ["STR", "CON"],
        "skill_bonuses": {"Endurance": 10, "Athletics": 5},
        "passive": "Reduced stamina loss",
        "standing_shift": {"Laborers": 200},
    },
    {
        "name": "Sharp-Eyed",
        "desc": "Observant and perceptive. +1 WIS or DEX, Perception +10%, Investigation +5%, +3% detect hidden, Civic Order +150",
        "stat_choices": ["WIS", "DEX"],
        "skill_bonuses": {"Perception": 10, "Investigation": 5},
        "passive": "+3% detect hidden",
        "standing_shift": {"Civic_Order": 150},
    },
    {
        "name": "Artificer",
        "desc": "Inventive and skilled. +1 INT or DEX, Crafting +10%, Appraise +5%, Faster repairs, Merchants +150",
        "stat_choices": ["INT", "DEX"],
        "skill_bonuses": {"Crafting": 10, "Appraise": 5},
        "passive": "Faster repairs",
        "standing_shift": {"Merchants": 150},
    },
    {
        "name": "Silver-Tongued",
        "desc": "Charming and persuasive. +1 CHA, Persuasion +10%, Social +5%, Start friendlier, Nobility +150, Merchants +100",
        "stat_choices": ["CHA"],
        "skill_bonuses": {"Persuasion": 10, "Social": 5},
        "passive": "Start friendlier",
        "standing_shift": {"Nobility": 150, "Merchants": 100},
    },
    {
        "name": "Hidden",
        "desc": "Stealthy and elusive. +1 DEX or WIS, Stealth +10%, Streetwise +5%, Harder to detect, Underbelly +200, Civic Order -100",
        "stat_choices": ["DEX", "WIS"],
        "skill_bonuses": {"Stealth": 10, "Streetwise": 5},
        "passive": "Harder to detect",
        "standing_shift": {"Underbelly": 200, "Civic_Order": -100},
    },
    {
        "name": "Devoted",
        "desc": "Faithful and resolute. +1 WIS, Ritual/Meditation +10%, Sense Motive +5%, +1 mental resist, Watcher Cult +250",
        "stat_choices": ["WIS"],
        "skill_bonuses": {"Ritual": 10, "Meditation": 10, "Sense Motive": 5},
        "passive": "+1 mental resist",
        "standing_shift": {"Watcher_Cult": 250},
    },
    {
        "name": "Insightful",
        "desc": "Wise and knowledgeable. +1 INT, Lore +10%, Investigation +5%, Auto-insight on runes/text, Scholars +200",
        "stat_choices": ["INT"],
        "skill_bonuses": {"Lore": 10, "Investigation": 5},
        "passive": "Auto-insight on runes/text",
        "standing_shift": {"Scholars": 200},
    },
    {
        "name": "Freehands",
        "desc": "Adaptable and tough. +1 DEX or CON, Adaptability +10%, +5 any, Environmental resistance, Neutral (no shifts)",
        "stat_choices": ["DEX", "CON"],
        "skill_bonuses": {"Adaptability": 10},
        "passive": "Environmental resistance",
        "standing_shift": {},
    },
]

def node_personality(caller, raw_string, **kwargs):
    char = kwargs.get("startnode_input")
    if char is None and hasattr(caller, 'db'):
        char = caller
    if char is None and hasattr(caller, 'db'):
        char = caller
    if raw_string:
        choice = raw_string.strip().lower()
        for idx, pdata in enumerate(PERSONALITIES, 1):
            pname = pdata["name"].lower()
            if choice == str(idx) or choice == pname:
                char.db.personality = pdata["name"]
                char.db.personality_data = pdata
                # If stat_choices > 1, prompt for stat selection next
                if len(pdata["stat_choices"]) > 1:
                    char.db.personality_pending_stat = True
                    return f"|gYou have selected:|n {pdata['name']}\n{pdata['desc']}\n\nChoose your stat bonus:", tuple({"desc": f"+1 {stat}", "goto": "node_personality_stat", "key": stat} for stat in pdata["stat_choices"])
                else:
                    stat = pdata["stat_choices"][0]
                    char.db.personality_stat_bonus = stat
                    char.db.personality_pending_stat = False
                    # Do NOT apply stat bonus yet; only after point-buy is complete
                    stat_keys = list(STAT_INFO.keys())
                    if not hasattr(char.db, 'stat_assign') or not char.db.stat_assign:
                        char.db.stat_assign = {k: POINT_BUY_START for k in stat_keys}
                    return f"|gYou have selected:|n {pdata['name']}\n{pdata['desc']}\n\nType |cnext|n to continue.", ( {"desc": "Continue", "goto": "node_stats", "key": "next"}, )
        caller.msg("|rInvalid personality. Please choose by number or name.")
    # Show clickable personality options with bonuses
    text = "|wSelect your character's personality:|n\n"
    options = []
    options.append({"desc": "Back", "goto": "node_race", "key": "back"})
    for idx, pdata in enumerate(PERSONALITIES, 1):
        text += f"|c{idx}. {pdata['name']}|n\n    {pdata['desc']}\n\n"
        options.append({"desc": f"Choose {pdata['name']}", "goto": "node_personality", "key": str(idx)})
    return text, tuple(options)

# Node for stat selection if multiple choices
def node_personality_stat(caller, raw_string, **kwargs):
    char = kwargs.get("startnode_input")
    if char is None and hasattr(caller, 'db'):
        char = caller
    if raw_string:
        stat = raw_string.strip().upper()
        pdata = char.db.personality_data
        if stat in pdata["stat_choices"]:
            char.db.personality_stat_bonus = stat
            char.db.personality_pending_stat = False
            # Do NOT apply stat bonus yet; only after point-buy is complete
            stat_keys = list(STAT_INFO.keys())
            if not hasattr(char.db, 'stat_assign') or not char.db.stat_assign:
                char.db.stat_assign = {k: POINT_BUY_START for k in stat_keys}
            return f"|gStat bonus selected: +1 {stat}\nType |cnext|n to continue.", ( {"desc": "Continue", "goto": "node_stats", "key": "next"}, )
        else:
            caller.msg("|rInvalid stat choice. Please select one of the available options.")
    text = "|wChoose your stat bonus:|n\n"
    options = []
    options.append({"desc": "Back", "goto": "node_personality", "key": "back"})
    pdata = char.db.personality_data
    for stat in pdata["stat_choices"]:
        text += f"+1 {stat}\n"
        options.append({"desc": f"+1 {stat}", "goto": "node_personality_stat", "key": stat})
    return text, tuple(options)


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
    if char is None and hasattr(caller, 'db'):
        char = caller
    stat_keys = list(STAT_INFO.keys())
    # Initialize if not set
    personality_stat = getattr(char.db, 'personality_stat_bonus', None)
    if not hasattr(char.db, 'stat_assign') or not char.db.stat_assign:
        char.db.stat_assign = {k: (9 if k == personality_stat else POINT_BUY_START) for k in stat_keys}
    stats = char.db.stat_assign
    # Handle input (direct and clickable)
    if raw_string:
        key = raw_string.strip().lower()
        # Handle EvMenu button clicks: plus_stat/minus_stat
        for stat in stat_keys:
            min_val = 9 if stat == personality_stat else POINT_BUY_MIN
            max_val = 16 if stat == personality_stat else POINT_BUY_MAX
            if key == f"plus_{stat.lower()}":
                amt = 1
            elif key == f"minus_{stat.lower()}":
                amt = -1
            elif key in ("next", "done", "finish", "1"):
                cost_stats = dict(stats)
                if personality_stat and cost_stats.get(personality_stat, 0) > 15:
                    cost_stats[personality_stat] = 15
                cost = calc_point_buy_cost(cost_stats)
                if cost != POINT_BUY_TOTAL:
                    caller.msg(f"|rYou must spend exactly {POINT_BUY_TOTAL} points (currently spent: {cost}).|n")
                else:
                    final_stats = dict(stats)
                    # Apply stat bonus now
                    if personality_stat:
                        final_stats[personality_stat] += 1
                        if final_stats[personality_stat] > 16:
                            final_stats[personality_stat] = 16
                    char.db.stats = final_stats
                    del char.db.stat_assign
                    return "node_skills"
                return
            else:
                amt = None
            if amt is not None:
                new_val = stats[stat] + amt
                if new_val < min_val or new_val > max_val:
                    caller.msg(f"|r{stat} must be between {min_val} and {max_val}.|n")
                else:
                    temp_stats = dict(stats)
                    temp_stats[stat] = new_val
                    cost_stats = temp_stats.copy()
                    if personality_stat and cost_stats.get(personality_stat, 0) > 15:
                        cost_stats[personality_stat] = 15
                    cost = calc_point_buy_cost(cost_stats)
                    if cost > POINT_BUY_TOTAL:
                        caller.msg(f"|rNot enough points. You have {POINT_BUY_TOTAL - calc_point_buy_cost(stats)} left.|n")
                    else:
                        stats[stat] = new_val
                        caller.msg(f"|g{stat} set to {new_val}.|n")
                break
    # Always show the stat menu, regardless of point total
    # Show stat table with clickable + and -
    spent = calc_point_buy_cost(stats)
    text = (
        f"|w[CHARGEN]|n Assign your character's attributes.\nYou have |c{POINT_BUY_TOTAL - spent}|n points left.\n"
        f"Attributes must be between {POINT_BUY_MIN} and {POINT_BUY_MAX}.\n"
        "Click + or - next to each attribute to adjust.\nType |cnext|n when done.\n"
    )
    stat_options = []
    stat_options.append({"desc": "Back", "goto": "node_personality", "key": "back"})
    for stat in stat_keys:
        val = stats[stat]
        # Always recalculate personality_stat in case it changed
        personality_stat = getattr(char.db, 'personality_stat_bonus', None)
        min_val = 9 if stat == personality_stat else POINT_BUY_MIN
        max_val = 16 if stat == personality_stat else POINT_BUY_MAX
        plus_btn = f'|lcplus_{stat.lower()}|l+[+]|lt+|le'
        minus_btn = f'|lcminus_{stat.lower()}|l-[-]|lt-|le'
        text += f"{stat.title()}: {val} {plus_btn} {minus_btn} (min {min_val}, max {max_val})"
        if stat == personality_stat:
            text += " | Personality bonus stat starts at 9."
        text += "\n"
        # Add hidden stat options for EvMenu recognition
        stat_options.append({"desc": "", "goto": "node_stats", "key": f"plus_{stat.lower()}"})
        stat_options.append({"desc": "", "goto": "node_stats", "key": f"minus_{stat.lower()}"})
    text += "\nType |cnext|n when done."
    stat_options.append({"desc": "Continue", "goto": "node_stats", "key": "next"})

    return text, tuple(stat_options)

    # Handle clickable input
    if raw_string:
        key = raw_string.strip().lower()
        for stat in stat_keys:
            min_val = 9 if stat == personality_stat else POINT_BUY_MIN
            max_val = 16 if stat == personality_stat else POINT_BUY_MAX
            if key == f"plus_{stat.lower()}":
                amt = 1
                new_val = stats[stat] + amt
                if new_val < min_val or new_val > max_val:
                    caller.msg(f"|r{stat} must be between {min_val} and {max_val}.|n")
                else:
                    temp_stats = dict(stats)
                    temp_stats[stat] = new_val
                    cost_stats = temp_stats.copy()
                    if personality_stat and cost_stats.get(personality_stat, 0) > 15:
                        cost_stats[personality_stat] = 15
                    cost = calc_point_buy_cost(cost_stats)
                    if cost > POINT_BUY_TOTAL:
                        caller.msg(f"|rNot enough points. You have {POINT_BUY_TOTAL - calc_point_buy_cost(stats)} left.|n")
                    else:
                        stats[stat] = new_val
                        caller.msg(f"|g{stat} increased to {new_val}.|n")
                break
            elif key == f"minus_{stat.lower()}":
                amt = -1
                new_val = stats[stat] + amt
                if new_val < min_val or new_val > max_val:
                    caller.msg(f"|r{stat} must be between {min_val} and {max_val}.|n")
                else:
                    temp_stats = dict(stats)
                    temp_stats[stat] = new_val
                    cost_stats = temp_stats.copy()
                    if personality_stat and cost_stats.get(personality_stat, 0) > 15:
                        cost_stats[personality_stat] = 15
                    cost = calc_point_buy_cost(cost_stats)
                    if cost > POINT_BUY_TOTAL:
                        caller.msg(f"|rNot enough points. You have {POINT_BUY_TOTAL - calc_point_buy_cost(stats)} left.|n")
                    else:
                        stats[stat] = new_val
                        caller.msg(f"|y{stat} decreased to {new_val}.|n")
                break
    return text, tuple(stat_options)

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
    if char is None and hasattr(caller, 'db'):
        char = caller
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
    options = tuple({"desc": f"Choose {group}", "goto": "node_skills", "key": str(idx)} for idx, (group, _) in enumerate(SKILL_GROUPS, 1))
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
    options = ({"desc": "Continue", "goto": "node_background", "key": "next"},)
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
    options = ({"desc": "Continue", "goto": "node_public_knowledge", "key": "next"},)
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
    options = ({"desc": "Continue", "goto": "node_public_knowledge", "key": "next"},)
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
