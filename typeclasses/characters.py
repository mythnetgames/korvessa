"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from evennia.objects.objects import DefaultCharacter
from .objects import ObjectParent
from .systems.skillsystem import SkillSystem
from .systems.combatsystem import CombatSystem
from .systems.healingsystem import HealingSystem
from .systems.xpsystem import XPSystem
from .systems.personalitysystem import PersonalitySystem
from .systems.socialstandingsystem import SocialStandingSystem
from .systems.characterfactssystem import CharacterFactsSystem


class Character(ObjectParent, DefaultCharacter):
            # ----------------------
            # CHARACTER FACTS / PUBLIC KNOWLEDGE SYSTEM (modular)
            # ----------------------
            # Uses CharacterFactsSystem class from typeclasses/systems/characterfactssystem.py
            # Access via self.factsys.set_fact(), self.factsys.get_all_facts(), etc.

            @property
            def factsys(self):
                """
                Returns CharacterFactsSystem instance for this character.
                """
                if not hasattr(self, "_factsys"):
                    self._factsys = CharacterFactsSystem(self)
                return self._factsys
        # ----------------------
        # SOCIAL STANDING SYSTEM (modular)
        # ----------------------
        # Uses SocialStandingSystem class from typeclasses/systems/socialstandingsystem.py
        # Access via self.socialstandingsys.get_standing(), self.socialstandingsys.set_standing(), etc.

        @property
        def socialstandingsys(self):
            """
            Returns SocialStandingSystem instance for this character.
            """
            if not hasattr(self, "_socialstandingsys"):
                self._socialstandingsys = SocialStandingSystem(self)
            return self._socialstandingsys
    # ----------------------
    # HEALING & INJURY SYSTEM (modular)
    # ----------------------
    # Uses HealingSystem class from typeclasses/systems/healingsystem.py
    # Access via self.healingsys.get_injuries(), self.healingsys.add_injury(), etc.

    @property
    def healingsys(self):
        """
        Returns HealingSystem instance for this character.
        """
        if not hasattr(self, "_healingsys"):
            self._healingsys = HealingSystem(self)
        return self._healingsys
    # ----------------------
    # COMBAT SYSTEM (modular)
    # ----------------------
    # Uses CombatSystem class from typeclasses/systems/combatsystem.py
    # Access via self.combatsys.get_stamina(), self.combatsys.apply_combat_modifiers(), etc.

    @property
    def combatsys(self):
        """
        Returns CombatSystem instance for this character.
        """
        if not hasattr(self, "_combatsys"):
            self._combatsys = CombatSystem(self)
        return self._combatsys
    # ----------------------
    # SKILLS SYSTEM (modular)
    # ----------------------
    # Uses SkillSystem class from typeclasses/systems/skillsystem.py
    # Access via self.skillsys.get_skill(), self.skillsys.set_skill(), etc.

    def at_object_creation(self):
        super().at_object_creation()
        # ...existing code...
        self.skillsys = SkillSystem(self)

    @property
    def skillsys(self):
        """
        Returns SkillSystem instance for this character.
        """
        if not hasattr(self, "_skillsys"):
            self._skillsys = SkillSystem(self)
        return self._skillsys
    # ----------------------
    # XP ECONOMY SYSTEM (modular)
    # ----------------------
    # Uses XPSystem class from typeclasses/systems/xpsystem.py
    # Access via self.xpsys.get_xp(), self.xpsys.add_xp(), etc.

    @property
    def xpsys(self):
        """
        Returns XPSystem instance for this character.
        """
        if not hasattr(self, "_xpsys"):
            self._xpsys = XPSystem(self)
        return self._xpsys
        # ----------------------
        # D&D 5E-INSPIRED POINT BUY SYSTEM
        # ----------------------
        # Players assign stats using a point pool (default: 27 points)
        # Stat values range from 8 to 15 before modifiers
        # Costs: 8(0), 9(1), 10(2), 11(3), 12(4), 13(5), 14(7), 15(9)
        POINT_BUY_COSTS = {8: 0, 9: 1, 10: 2, 11: 3, 12: 4, 13: 5, 14: 7, 15: 9}
        POINT_BUY_MIN = 8
        POINT_BUY_MAX = 15
        POINT_BUY_POOL = 27

        def validate_point_buy(self, stat_values):
            """
            Validate a dict of stat assignments against point buy rules.
            Args:
                stat_values (dict): {stat_name: value}
            Returns:
                (bool, str): True if valid, else False and reason.
            """
            total_cost = 0
            for stat in self.STAT_NAMES:
                val = stat_values.get(stat, self.POINT_BUY_MIN)
                if val < self.POINT_BUY_MIN or val > self.POINT_BUY_MAX:
                    return False, f"{stat} value {val} out of range ({self.POINT_BUY_MIN}-{self.POINT_BUY_MAX})"
                total_cost += self.POINT_BUY_COSTS.get(val, 0)
            if total_cost > self.POINT_BUY_POOL:
                return False, f"Total cost {total_cost} exceeds pool ({self.POINT_BUY_POOL})"
            return True, "Valid point buy"

        def assign_stats_point_buy(self, stat_values):
            """
            Assign stats using point buy, if valid.
            Args:
                stat_values (dict): {stat_name: value}
            Returns:
                (bool, str): Success and message.
            """
            valid, msg = self.validate_point_buy(stat_values)
            if not valid:
                return False, msg
            for stat in self.STAT_NAMES:
                self.db[stat] = stat_values.get(stat, self.POINT_BUY_MIN)
            return True, "Stats assigned via point buy"
    """
    The Character just re-implements some of the Object's methods and hooks
    to represent a Character entity in-game.

    See mygame/typeclasses/objects.py for a list of
    properties and methods available on all Object child classes like this.

    """

    # Core stats for Korvessa
    # -------------------------------------------------------------------------
    # KORVESSA CHARACTER SYSTEMS - DOCUMENTATION & SCAFFOLDING
    # -------------------------------------------------------------------------
    # This class is the main hub for all character-related mechanics in Korvessa.
    # Future systems (XP, skills, combat, social standing, etc.) should integrate here.
    #
    # SYSTEMS:
    #   - Stats: STR, DEX, CON, INT, WIS, CHA
    #   - Personality: Defines starting bonuses, passives, and social standing shifts
    #   - Skills: To be added (proficiency, domains, learning)
    #   - XP Economy: To be added (gain, spend, buyout)
    #   - Combat: To be added (modifiers, stamina, outcomes)
    #   - Social Standing: To be added (factions, thresholds)
    #   - Character Facts: To be added (public knowledge)
    #   - Healing/Injury: To be added
    #   - Staff Tools: To be added
    # -------------------------------------------------------------------------

    # Core stats
    STAT_NAMES = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]

    # Personality definitions (from design doc)
    PERSONALITIES = {
        "Stalwart": {
            "stat_choices": ["STR", "CON"],
            "skill_bonuses": {"Endurance": 0.10, "Athletics": 0.05},
            "passive": "Reduced stamina loss",
            "standing_shift": {"Laborers": 200},
        },
        "Sharp-Eyed": {
            "stat_choices": ["WIS", "DEX"],
            "skill_bonuses": {"Perception": 0.10, "Investigation": 0.05},
            "passive": "+3% detect hidden",
            "standing_shift": {"Civic_Order": 150},
        },
        "Artificer": {
            "stat_choices": ["INT", "DEX"],
            "skill_bonuses": {"Crafting": 0.10, "Appraise": 0.05},
            "passive": "Faster repairs",
            "standing_shift": {"Merchants": 150},
        },
        "Silver-Tongued": {
            "stat_choices": ["CHA"],
            "skill_bonuses": {"Persuasion": 0.10, "Social": 0.05},
            "passive": "Start friendlier",
            "standing_shift": {"Nobility": 150, "Merchants": 100},
        },
        "Hidden": {
            "stat_choices": ["DEX", "WIS"],
            "skill_bonuses": {"Stealth": 0.10, "Streetwise": 0.05},
            "passive": "Harder to detect",
            "standing_shift": {"Underbelly": 200, "Civic_Order": -100},
        },
        "Devoted": {
            "stat_choices": ["WIS"],
            "skill_bonuses": {"Ritual": 0.10, "Sense Motive": 0.05},
            "passive": "+1 mental resist",
            "standing_shift": {"Watcher_Cult": 250},
        },
        "Insightful": {
            "stat_choices": ["INT"],
            "skill_bonuses": {"Lore": 0.10, "Investigation": 0.05},
            "passive": "Auto-insight on runes/text",
            "standing_shift": {"Scholars": 200},
        },
        "Freehands": {
            "stat_choices": ["DEX", "CON"],
            "skill_bonuses": {"Adaptability": 0.10},
            "passive": "Environmental resistance",
            "standing_shift": {},
        },
    }

    def at_object_creation(self):
        """
        Called only at initial creation.
        Initializes character stats and personality.
        Future systems should hook into this for initial setup.
        """
        super().at_object_creation()
        # Default stat values (can be adjusted by chargen/personality)
        for stat in self.STAT_NAMES:
            self.db[stat] = 5  # Baseline value, adjust as needed
        # Personality scaffolding
        self.db.personality = None  # Will be set during character creation

    # ----------------------
    # STATS API
    # ----------------------
    def get_stat(self, stat_name):
        """
        Return the value of a stat.
        """
        return self.db.get(stat_name, None)

    def set_stat(self, stat_name, value):
        """
        Set the value of a stat.
        """
        if stat_name in self.STAT_NAMES:
            self.db[stat_name] = value
            return True
        return False

    # ----------------------
    # PERSONALITY API
    # ----------------------
    def set_personality(self, personality_name, stat_choice=None):
        """
        Assign a personality to the character and apply bonuses.
        Args:
            personality_name (str): Name of the personality.
            stat_choice (str): Stat to receive the bonus (if multiple options).
        """
        pers = self.PERSONALITIES.get(personality_name)
        if not pers:
            return False
        self.db.personality = personality_name
        # Apply stat bonus
        if stat_choice and stat_choice in pers["stat_choices"]:
            self.db[stat_choice] += 1
        else:
            # If only one choice, apply automatically
            if len(pers["stat_choices"]) == 1:
                self.db[pers["stat_choices"][0]] += 1
        # Skill bonuses, passives, standing shifts are scaffolded for future systems
        self.db.skill_bonuses = pers["skill_bonuses"]
        self.db.personality_passive = pers["passive"]
        self.db.standing_shift = pers["standing_shift"]
        return True

    def get_personality(self):
        """
        Return the character's personality and its effects.
        """
        pname = self.db.personality
        if not pname:
            return None
        pers = self.PERSONALITIES.get(pname)
        return {
            "name": pname,
            "stat_choices": pers["stat_choices"],
            "skill_bonuses": self.db.skill_bonuses,
            "passive": self.db.personality_passive,
            "standing_shift": self.db.standing_shift,
        }

    # ----------------------
    # FUTURE SYSTEMS: XP, SKILLS, COMBAT, SOCIAL STANDING, ETC.
    # ----------------------
    # Add hooks and APIs here for future expansion. See design doc for details.
