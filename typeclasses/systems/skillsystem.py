"""
Skill System for Korvessa

Handles skill domains, proficiency caps, learning rates, and skill access logic.
Designed for easy integration with XP, training, RP bonuses, and staff/GM overrides.
"""

class SkillSystem:
    # Skill domains
    SKILL_DOMAINS = {
        "Combat": ["Dodge", "Parry", "Grapple", "Weapon"],
        "Stealth": ["Hide", "Sneak", "Pick Locks"],
        "Social": ["Haggle", "Persuasion", "Streetwise"],
        "Crafting": ["Carpentry", "Blacksmithing", "Herbalism"],
        "Survival": ["Track", "Forage", "First Aid"],
        "Lore": ["Investigation", "Lore", "Appraise"],
        "Medical": ["Bandaging", "Chirurgy"],
    }

    # Proficiency caps
    SKILL_PROFICIENCY_CAPS = {
        "starting": 0.40,
        "self_trained": 0.80,
        "teacher_trained": 0.90,
        "gm_exceptional": 0.95,
    }

    SKILL_LEARNING_PENALTY = -0.40  # Global learning penalty

    def __init__(self, character):
        self.character = character

    def get_skill(self, skill_name):
        return self.character.db.skills.get(skill_name, 0.0) if self.character.db.skills else 0.0

    def set_skill(self, skill_name, value):
        if not self.character.db.skills:
            self.character.db.skills = {}
        cap = self.SKILL_PROFICIENCY_CAPS["self_trained"]
        if value > cap:
            value = cap
        self.character.db.skills[skill_name] = value
        return True

    def learn_skill(self, skill_name, amount, trained_by=None, gm_exceptional=False):
        if not self.character.db.skills:
            self.character.db.skills = {}
        current = self.character.db.skills.get(skill_name, 0.0)
        amount *= (1 + self.SKILL_LEARNING_PENALTY)
        if gm_exceptional:
            cap = self.SKILL_PROFICIENCY_CAPS["gm_exceptional"]
        elif trained_by == "teacher":
            cap = self.SKILL_PROFICIENCY_CAPS["teacher_trained"]
        else:
            cap = self.SKILL_PROFICIENCY_CAPS["self_trained"]
        new_value = min(current + amount, cap)
        self.character.db.skills[skill_name] = new_value
        return True, f"{skill_name} increased to {new_value:.2f}"

    def get_skills_by_domain(self, domain):
        skills = self.SKILL_DOMAINS.get(domain, [])
        return {s: self.get_skill(s) for s in skills}
