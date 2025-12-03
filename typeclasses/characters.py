"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from evennia.objects.objects import DefaultCharacter

from .objects import ObjectParent


class Character(ObjectParent, DefaultCharacter):
                    # ----------------------
                    # COMBAT SYSTEM
                    # ----------------------
                    # Combat is slower, more dangerous, and stamina-focused.
                    # Mechanics: weapon speed, hit chance, damage, stamina drain, retreat, crowd control.
                    # Social reactions: NPCs respond based on Standing and location.

                    COMBAT_MODIFIERS = {
                        "base_hit_chance": -0.05,  # Reduced slightly
                        "damage_reduction": 0.15,  # 10–15% less damage
                        "stamina_drain": 1.25,     # Increased cost for maneuvers
                        "retreat_difficulty": 1.2, # Harder to escape
                        "crowd_control_duration": 0.7, # Shortened durations
                    }

                    def get_stamina(self):
                        """
                        Return current stamina value.
                        """
                        return self.db.stamina or 10  # Default value, adjust as needed

                    def set_stamina(self, value):
                        """
                        Set stamina value.
                        """
                        self.db.stamina = value
                        return True

                    def apply_combat_modifiers(self, hit_chance, damage, maneuver_type=None):
                        """
                        Apply global combat modifiers to hit chance and damage.
                        Args:
                            hit_chance (float): Base hit chance
                            damage (float): Base damage
                            maneuver_type (str): Type of maneuver (optional)
                        Returns:
                            (float, float): Modified hit chance, damage
                        """
                        hit_chance += self.COMBAT_MODIFIERS["base_hit_chance"]
                        damage *= (1 - self.COMBAT_MODIFIERS["damage_reduction"])
                        # Stamina drain and retreat/crowd control can be handled in future hooks
                        return hit_chance, damage

                    def drain_stamina(self, amount):
                        """
                        Drain stamina for maneuvers, applying global modifier.
                        """
                        drain = amount * self.COMBAT_MODIFIERS["stamina_drain"]
                        self.set_stamina(max(self.get_stamina() - drain, 0))
                        return drain

                    def can_retreat(self, dex, athletics):
                        """
                        Determine if retreat is possible, factoring in difficulty.
                        Args:
                            dex (int): DEX stat
                            athletics (float): Athletics skill
                        Returns:
                            (bool, float): Success and difficulty
                        """
                        difficulty = (10 - dex) * self.COMBAT_MODIFIERS["retreat_difficulty"] - athletics
                        return difficulty < 5, difficulty

                    def apply_crowd_control(self, duration):
                        """
                        Apply crowd control duration modifier.
                        """
                        return duration * self.COMBAT_MODIFIERS["crowd_control_duration"]

                    def social_reaction_to_combat(self, location, standing):
                        """
                        Scaffold: NPCs respond to combat based on location and Standing.
                        Args:
                            location (str): Zone type
                            standing (dict): Faction standings
                        Returns:
                            str: Description of likely NPC reaction
                        """
                        # Example logic, expand for full system
                        if location == "public":
                            return "Guards intervene"
                        elif location == "laborer":
                            return "Workers join in or scatter"
                        elif location == "underbelly":
                            return "Ignored or thieves take advantage"
                        return "Unusual response"
                # ----------------------
                # SKILLS SYSTEM
                # ----------------------
                # Skills are grouped into domains and have proficiency caps.
                # Learning rates are affected by global penalties, RP bonuses, and grinding penalties.
                # Skills are purchased via Training Points (from XP).
                # Staff may lock skills behind Standing, teachers, or storylines.

                SKILL_DOMAINS = {
                    "Combat": ["Dodge", "Parry", "Grapple", "Weapon"],
                    "Stealth": ["Hide", "Sneak", "Pick Locks"],
                    "Social": ["Haggle", "Persuasion", "Streetwise"],
                    "Crafting": ["Carpentry", "Blacksmithing", "Herbalism"],
                    "Survival": ["Track", "Forage", "First Aid"],
                    "Lore": ["Investigation", "Lore", "Appraise"],
                    "Medical": ["Bandaging", "Chirurgy"],
                }

                SKILL_PROFICIENCY_CAPS = {
                    "starting": 0.40,
                    "self_trained": 0.80,
                    "teacher_trained": 0.90,
                    "gm_exceptional": 0.95,
                }

                SKILL_LEARNING_PENALTY = -0.40  # Global learning penalty

                def get_skill(self, skill_name):
                    """
                    Return current proficiency for a skill (0.0–1.0).
                    """
                    return self.db.skills.get(skill_name, 0.0) if self.db.skills else 0.0

                def set_skill(self, skill_name, value):
                    """
                    Set proficiency for a skill, respecting caps.
                    """
                    if not self.db.skills:
                        self.db.skills = {}
                    # Determine cap (scaffold: expand with training/teacher/GM logic)
                    cap = self.SKILL_PROFICIENCY_CAPS["self_trained"]
                    if value > cap:
                        value = cap
                    self.db.skills[skill_name] = value
                    return True

                def learn_skill(self, skill_name, amount, trained_by=None, gm_exceptional=False):
                    """
                    Increase skill proficiency, applying learning penalties and caps.
                    Args:
                        skill_name (str): Skill to learn
                        amount (float): Amount to increase
                        trained_by (str): 'teacher' or None
                        gm_exceptional (bool): If GM grants exceptional cap
                    """
                    if not self.db.skills:
                        self.db.skills = {}
                    current = self.db.skills.get(skill_name, 0.0)
                    # Apply global penalty
                    amount *= (1 + self.SKILL_LEARNING_PENALTY)
                    # RP activity bonus and grinding penalty can be added here
                    # Determine cap
                    if gm_exceptional:
                        cap = self.SKILL_PROFICIENCY_CAPS["gm_exceptional"]
                    elif trained_by == "teacher":
                        cap = self.SKILL_PROFICIENCY_CAPS["teacher_trained"]
                    else:
                        cap = self.SKILL_PROFICIENCY_CAPS["self_trained"]
                    new_value = min(current + amount, cap)
                    self.db.skills[skill_name] = new_value
                    return True, f"{skill_name} increased to {new_value:.2f}"

                def get_skills_by_domain(self, domain):
                    """
                    Return all skills and proficiencies in a domain.
                    """
                    skills = self.SKILL_DOMAINS.get(domain, [])
                    return {s: self.get_skill(s) for s in skills}
            # ----------------------
            # XP ECONOMY SYSTEM
            # ----------------------
            # XP is gained from RP, crafting, labor, combat, trading, etc.
            # Daily cap: 200 XP
            # XP can be spent on training points, NPC interaction, story, business, plot progression, sunset buyout
            XP_DAILY_CAP = 200
            XP_USE_COSTS = {
                "training_point": 200,
                "minor_npc_interaction": 400,
                "story_notice": 600,
                "small_business": 5000,
                "full_shop": 36000,
                "plot_progression": 4200,
            }

            def get_xp(self):
                """
                Return current XP value.
                """
                return self.db.xp or 0

            def add_xp(self, amount):
                """
                Add XP, respecting daily cap.
                Args:
                    amount (int): XP to add
                Returns:
                    (bool, str): Success and message
                """
                # Track daily XP gain (scaffold: should reset daily)
                daily_xp = self.db.daily_xp or 0
                if daily_xp + amount > self.XP_DAILY_CAP:
                    return False, f"Daily XP cap ({self.XP_DAILY_CAP}) exceeded"
                self.db.xp = self.get_xp() + amount
                self.db.daily_xp = daily_xp + amount
                return True, f"Added {amount} XP"

            def spend_xp(self, use_type):
                """
                Spend XP for a specific use (training, interaction, etc.).
                Args:
                    use_type (str): Type of XP purchase
                Returns:
                    (bool, str): Success and message
                """
                cost = self.XP_USE_COSTS.get(use_type)
                if cost is None:
                    return False, "Invalid XP use type"
                if self.get_xp() < cost:
                    return False, f"Not enough XP (need {cost})"
                self.db.xp = self.get_xp() - cost
                # Scaffold: trigger effects for each use type (training, business, etc.)
                return True, f"Spent {cost} XP on {use_type}"

            def sunset_buyout(self, buyout_type):
                """
                Spend remaining XP on sunset buyout options (business, rumor, reputation, standing shift).
                Args:
                    buyout_type (str): Type of buyout
                Returns:
                    (bool, str): Success and message
                """
                # Scaffold: implement buyout logic and options
                self.db.xp = 0
                return True, f"XP spent on {buyout_type} (character sunset)"
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
