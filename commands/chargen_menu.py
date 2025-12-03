"""
Chargen Menu for Korvessa (Evennia EvMenu)

Guides players through character creation: race, personality, stat buy, skills, standing, facts.
Integrates with modular systems in typeclasses/systems/.
"""
from evennia import CmdSet
from evennia.utils.evmenu import EvMenu

class CmdChargenMenu(CmdSet):
    """CmdSet to start the chargen menu."""
    key = "ChargenMenu"
    priority = 1

    def at_cmdset_creation(self):
        self.add(CmdStartChargen())

class CmdStartChargen:
    """Command to start character generation."""
    key = "chargen"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        EvMenu(self.caller, "commands.chargen_menu", startnode="node_welcome")

# Menu nodes

def node_welcome(caller, raw_string, **kwargs):
    text = (
        "Welcome to Korvessa Character Creation!\n"
        "You will choose your name, race, personality, assign stats, select skills, set your social standing, and enter public facts.\n"
           "Type 1 or press enter to begin.\n"
    )
    options = [
           {"desc": "Begin character creation", "goto": "node_charname", "key": ("1", "", "next")},
    ]
    return text, options

# Character name entry node
def node_charname(caller, raw_string, **kwargs):
    import evennia
    evennia.logger.log_info(f"[DEBUG] node_charname: caller={caller} type={type(caller)} raw_string={raw_string}")
    text = "Step 0: Enter your character's name. This will be your IC shell name.\n"
    text += "(Example: Anea, Borin, Elenwen)\n"
    if raw_string:
        name = raw_string.strip()
        if not name or len(name) < 2:
            return "Name must be at least 2 characters.", []
        kwargs["charname"] = name
        # Create character and switch to IC immediately
        from evennia import create_object
        from typeclasses.characters import Character
        account = caller.account if hasattr(caller, "account") else caller
        newchar = create_object(Character, key=name, account=account)
        caller.account.sessid_login(newchar)
        caller.ndb.chargen_character = newchar  # Store reference for later chargen steps
        return f"Name '{name}' saved! You are now IC as {name}. Proceeding to race selection...", [{"desc": "Continue", "goto": ("node_race", kwargs)}]
    options = [
        {"desc": "Enter character name", "goto": ("node_charname", kwargs)},
    ]
    return text, options



# Race selection node
def node_race(caller, raw_string, **kwargs):
    text = (
        "Step 1: Choose your character's race.\n"
        "Races available: |wElf|n, |wHuman|n, |wDwarf|n.\n"
        "Type the race name to select."
    )
    options = [
        {"desc": "Elf", "goto": ("node_personality", {"race": "Elf"})},
        {"desc": "Human", "goto": ("node_personality", {"race": "Human"})},
        {"desc": "Dwarf", "goto": ("node_personality", {"race": "Dwarf"})},
    ]
    return text, options

# Personality selection node
def node_personality(caller, raw_string, **kwargs):
    from typeclasses.systems.personalitysystem import PERSONALITIES
    text = "Step 2: Choose your character's personality.\n\n"
    for pname, pdata in PERSONALITIES.items():
        text += f"|w{pname}|n: Stat choices: {', '.join(pdata['stat_choices'])}; Skill bonuses: {', '.join([f'{k} +{int(v*100)}%' for k,v in pdata['skill_bonuses'].items()])}; Passive: {pdata['passive']}\n"
    text += "\nType the personality name to select."
    options = [
        {"desc": pname, "goto": ("node_stats", {**kwargs, "personality": pname})} for pname in PERSONALITIES.keys()
    ]
    return text, options
# Stat assignment (point buy) node
def node_stats(caller, raw_string, **kwargs):
    stat_names = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]
    point_buy_costs = {8: 0, 9: 1, 10: 2, 11: 3, 12: 4, 13: 5, 14: 7, 15: 9}
    pool = 27
    text = (
        "Step 3: Assign your stats using point buy.\n"
        "You have 27 points to spend. Stats range from 8 to 15.\n"
        "Costs: 8(0), 9(1), 10(2), 11(3), 12(4), 13(5), 14(7), 15(9)\n"
        "Type your stat assignment as: STR=10 DEX=14 CON=12 INT=10 WIS=10 CHA=8\n"
        "(You must assign all six stats. Total cost must not exceed 27 points.)"
    )
    # Parse user input if provided
    if raw_string:
        try:
            assignments = dict(
                (k.strip(), int(v.strip()))
                for k, v in (pair.split("=") for pair in raw_string.split() if "=" in pair)
            )
        except Exception:
            return "Invalid format. Please use: STR=10 DEX=14 CON=12 INT=10 WIS=10 CHA=8", []
        # Validation
        if set(assignments.keys()) != set(stat_names):
            return "You must assign all six stats.", []
        total_cost = 0
        for stat in stat_names:
            val = assignments[stat]
            if val < 8:
                return f"{stat} is already at minimum (8). You can't lower it further.", []
            if val > 15:
                return f"{stat} is already at maximum (15). You can't raise it further.", []
            total_cost += point_buy_costs.get(val, 0)
        if total_cost > pool:
            return f"Total cost {total_cost} exceeds pool (27). Please reassign.", []
        # If valid, pass assignments to next node
        kwargs["stats"] = assignments
        return "Stats accepted! Proceeding to skill selection...", [{"desc": "Continue", "goto": ("node_skills", kwargs)}]
    options = [
        {"desc": "Enter stat assignment", "goto": ("node_stats", kwargs)},
    ]
    return text, options
# Skill selection node
def node_skills(caller, raw_string, **kwargs):
    from typeclasses.systems.skillsystem import SkillSystem
    skill_domains = list(SkillSystem.SKILL_DOMAINS.keys())
    text = "Step 4: Select your starting skill domain.\n\n"
    for domain in skill_domains:
        skills = SkillSystem.SKILL_DOMAINS[domain]
        text += f"|w{domain}|n: {', '.join(skills)}\n"
    text += "\nType the domain name to select."
    options = [
        {"desc": domain, "goto": ("node_skills_individual", {**kwargs, "domain": domain})} for domain in skill_domains
    ]
    return text, options

# Individual skill selection node
def node_skills_individual(caller, raw_string, **kwargs):
    from typeclasses.systems.skillsystem import SkillSystem
    domain = kwargs.get("domain")
    skills = SkillSystem.SKILL_DOMAINS.get(domain, [])
    text = f"Step 4b: Select your starting skills from the |w{domain}|n domain.\n"
    text += "Choose up to 2 skills. Type skill names separated by spaces (e.g. Dodge Parry).\n"
    text += f"Available: {', '.join(skills)}"
    if raw_string:
        selected = [s for s in raw_string.split() if s in skills]
        if len(selected) == 0:
            return "You must select at least one skill.", []
        if len(selected) > 2:
            return "You can only select up to 2 skills.", []
        kwargs["skills"] = selected
        return "Skills accepted! Proceeding to social standing...", [{"desc": "Continue", "goto": ("node_standing", kwargs)}]
    options = [
        {"desc": "Enter skill selection", "goto": ("node_skills_individual", kwargs)},
    ]
    return text, options
# Social standing info node
def node_standing(caller, raw_string, **kwargs):
    from typeclasses.systems.socialstandingsystem import FACTIONS
    text = "Step 5: Social Standing\n\n"
    text += "Your initial faction standings are set to neutral.\n"
    text += "Staff may adjust your standings after review.\n"
    text += "Factions: " + ", ".join(FACTIONS) + "\n"
    options = [
        {"desc": "Continue to character facts", "goto": ("node_facts", kwargs)},
    ]
    return text, options
# Character facts entry node
def node_facts(caller, raw_string, **kwargs):
    from typeclasses.systems.characterfactssystem import FACT_FIELDS
    facts = kwargs.get("facts", {})
    # Find next field to fill
    for field in FACT_FIELDS:
        if field not in facts or not facts[field]:
            text = f"Step 6: Enter your character's {field.replace('_', ' ').title()}\n"
            text += "(Example: "
            if field == "name_as_known":
                text += "Anea the Smith's Daughter)\n"
            elif field == "apparent_age":
                text += "Mid 20s)\n"
            elif field == "appearance_notes":
                text += "Walks with a limp)\n"
            elif field == "common_rumors":
                text += "Works odd hours near the mines)\n"
            elif field == "known_affiliations":
                text += "Often seen at laborer taverns)\n"
            elif field == "reputation_tier":
                text += "Minor, Moderate, Strong)\n"
            else:
                text += ")\n"
            if raw_string:
                facts[field] = raw_string.strip()
                kwargs["facts"] = facts
                return f"{field.replace('_', ' ').title()} saved!", [{"desc": "Continue", "goto": ("node_facts", kwargs)}]
            options = [
                {"desc": f"Enter {field.replace('_', ' ').title()}", "goto": ("node_facts", kwargs)},
            ]
            return text, options
    # All facts entered
    text = "All character facts entered!\nStaff will review for lore consistency.\nType 'next' to enter your character's background."
    options = [
        {"desc": "Enter background information", "goto": ("node_background", kwargs)},
    ]
    return text, options
# Background information entry node
def node_background(caller, raw_string, **kwargs):
    text = "Step 7: Enter your character's background story.\n"
    text += "This is for staff review and helps ground your character in the world.\n"
    text += "(Example: Grew up in the laborer district, lost a parent to mine collapse, dreams of joining the Watcher's Cult.)\n"
    if raw_string:
        kwargs["background"] = raw_string.strip()
        return "Background saved! Proceeding to final confirmation...", [{"desc": "Continue", "goto": ("node_confirm", kwargs)}]
    options = [
        {"desc": "Enter background story", "goto": ("node_background", kwargs)},
    ]
    return text, options
# Final confirmation node
def node_confirm(caller, raw_string, **kwargs):
    text = "Character creation complete!\n\nSummary of your choices:\n"
    text += f"Name: {kwargs.get('charname', 'N/A')}\n"
    text += f"Race: {kwargs.get('race', 'N/A')}\n"
    text += f"Personality: {kwargs.get('personality', 'N/A')}\n"
    text += f"Stats: {kwargs.get('stats', {})}\n"
    text += f"Skills: {kwargs.get('skills', [])}\n"
    text += f"Character Facts: {kwargs.get('facts', {})}\n"
    text += f"Background: {kwargs.get('background', '')}\n"
    text += "\nYour character will be reviewed by staff for lore and consistency.\nWelcome to Korvessa!"
    # Character creation logic
    if not caller.db.chargen_complete:
        from evennia import create_object
        from typeclasses.characters import Character
        charname = kwargs.get('charname', None)
        if charname:
            # Create character and link to account
            newchar = create_object(Character, key=charname, account=caller.account)
            # Set stats
            stats = kwargs.get('stats', {})
            for stat, value in stats.items():
                newchar.db[stat] = value
            # Set personality
            personality = kwargs.get('personality', None)
            if personality:
                newchar.set_personality(personality)
            # Set skills
            skills = kwargs.get('skills', [])
            for skill in skills:
                newchar.skillsys.set_skill(skill, 0.4)  # Starting proficiency
            # Set character facts
            facts = kwargs.get('facts', {})
            for field, value in facts.items():
                newchar.factsys.set_fact(field, value)
            # Set background
            background = kwargs.get('background', None)
            if background:
                newchar.db.background = background
            caller.db.chargen_complete = True
            text += f"\nCharacter '{charname}' created and linked to your account!"
            # Auto-switch to IC mode
            caller.account.sessid_login(newchar)
            text += "\nYou have entered the game as your new character!"
            options = []
            return text, options
    # If chargen already complete, just show summary
    options = []
    return text, options
