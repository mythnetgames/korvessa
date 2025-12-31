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
    options = ( {"desc": "Begin character creation", "goto": "node_race"}, )
    return text, options

def node_race(caller, raw_string, **kwargs):
    text = "|w[CHARGEN]|n Race selection coming soon. (Stub)\nType |cnext|n to continue."
    options = ( {"desc": "Continue", "goto": "node_personality"}, )
    return text, options

def node_personality(caller, raw_string, **kwargs):
    text = "|w[CHARGEN]|n Personality selection coming soon. (Stub)\nType |cnext|n to continue."
    options = ( {"desc": "Continue", "goto": "node_stats"}, )
    return text, options

def node_stats(caller, raw_string, **kwargs):
    table = EvTable("Stat", "Meaning", "Mechanical Influence")
    for stat, (meaning, influence) in STAT_INFO.items():
        table.add_row(stat, meaning, influence)
    text = "|w[CHARGEN]|n Assign your stats. (Stub)\n" + str(table) + "\nType |cnext|n to continue."
    options = ( {"desc": "Continue", "goto": "node_skills"}, )
    return text, options

def node_skills(caller, raw_string, **kwargs):
    text = "|w[CHARGEN]|n Skill selection coming soon. (Stub)\nType |cnext|n to continue."
    options = ( {"desc": "Continue", "goto": "node_standing"}, )
    return text, options

def node_standing(caller, raw_string, **kwargs):
    table = EvTable("Faction", "Notes")
    for group in STANDING_GROUPS:
        table.add_row(group, "...")
    text = "|w[CHARGEN]|n Social Standing. (Stub)\n" + str(table) + "\nType |cnext|n to continue."
    options = ( {"desc": "Continue", "goto": "node_background"}, )
    return text, options

def node_background(caller, raw_string, **kwargs):
    text = "|w[CHARGEN]|n Enter your character background. (Stub)\nType |cnext|n to continue."
    options = ( {"desc": "Continue", "goto": "node_public_knowledge"}, )
    return text, options

def node_public_knowledge(caller, raw_string, **kwargs):
    table = EvTable("Field", "Example/Notes")
    for field, notes in PUBLIC_KNOWLEDGE_FIELDS:
        table.add_row(field, notes)
    text = "|w[CHARGEN]|n Enter your public knowledge. (Stub)\n" + str(table) + "\nType |cnext|n to continue."
    options = ( {"desc": "Continue", "goto": "node_review"}, )
    return text, options

def node_review(caller, raw_string, **kwargs):
    text = "|w[CHARGEN]|n Review your character and submit. (Stub)\nType |cdone|n to finish."
    options = ( {"desc": "Finish character creation", "goto": "node_done"}, )
    return text, options

def node_done(caller, raw_string, **kwargs):
    text = "|g[SUCCESS]|n Character creation is complete! Use |wic <name>|n to enter the world."
    options = ()
    return text, options
