"""
Character Facts / Public Knowledge System for Korvessa

Tracks public knowledge about a character, including name, age, appearance, rumors, affiliations, and reputation tier.
Provides hooks for skill rolls against public knowledge and staff verification.
Designed for easy integration with character creation, lore, and social systems.
"""

FACT_FIELDS = [
    "name_as_known",
    "apparent_age",
    "appearance_notes",
    "common_rumors",
    "known_affiliations",
    "reputation_tier",
]

class CharacterFactsSystem:
    def __init__(self, character):
        self.character = character
        if not hasattr(self.character.db, "facts") or self.character.db.facts is None:
            self.character.db.facts = {field: None for field in FACT_FIELDS}

    def set_fact(self, field, value):
        if field not in FACT_FIELDS:
            return False, "Invalid fact field"
        self.character.db.facts[field] = value
        return True, f"Set {field} to {value}"

    def get_fact(self, field):
        return self.character.db.facts.get(field, None)

    def get_all_facts(self):
        return {field: self.get_fact(field) for field in FACT_FIELDS}

    def roll_against_public_knowledge(self, skill, dc):
        """
        Scaffold: Roll a skill against a DC to reveal public knowledge fragments.
        Args:
            skill (str): Skill used for the roll
            dc (int): Difficulty class
        Returns:
            dict: Revealed facts/fragments
        """
        # Example logic, expand for full system
        skill_value = self.character.skillsys.get_skill(skill)
        if skill_value * 100 >= dc:
            return self.get_all_facts()
        else:
            # Reveal only some facts if roll fails
            return {k: v for k, v in self.get_all_facts().items() if k in ["name_as_known", "appearance_notes"]}
