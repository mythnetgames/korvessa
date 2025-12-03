"""
Personality System for Korvessa

Handles personality selection, stat/skill/social standing bonuses, and passives.
Designed for easy integration with character creation, skills, and faction systems.
"""

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

class PersonalitySystem:
    def __init__(self, character):
        self.character = character

    def set_personality(self, personality_name, stat_choice=None):
        pers = PERSONALITIES.get(personality_name)
        if not pers:
            return False
        self.character.db.personality = personality_name
        # Apply stat bonus
        if stat_choice and stat_choice in pers["stat_choices"]:
            self.character.db[stat_choice] += 1
        else:
            if len(pers["stat_choices"]) == 1:
                self.character.db[pers["stat_choices"][0]] += 1
        self.character.db.skill_bonuses = pers["skill_bonuses"]
        self.character.db.personality_passive = pers["passive"]
        self.character.db.standing_shift = pers["standing_shift"]
        return True

    def get_personality(self):
        pname = self.character.db.personality
        if not pname:
            return None
        pers = PERSONALITIES.get(pname)
        return {
            "name": pname,
            "stat_choices": pers["stat_choices"],
            "skill_bonuses": self.character.db.skill_bonuses,
            "passive": self.character.db.personality_passive,
            "standing_shift": self.character.db.standing_shift,
        }
