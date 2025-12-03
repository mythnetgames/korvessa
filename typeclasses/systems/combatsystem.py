"""
Combat System for Korvessa

Handles combat modifiers, stamina, hit chance, damage, retreat, crowd control, and social reaction hooks.
Designed for easy integration with skills, stats, and social standing systems.
"""

class CombatSystem:
    COMBAT_MODIFIERS = {
        "base_hit_chance": -0.05,  # Reduced slightly
        "damage_reduction": 0.15,  # 10–15% less damage
        "stamina_drain": 1.25,     # Increased cost for maneuvers
        "retreat_difficulty": 1.2, # Harder to escape
        "crowd_control_duration": 0.7, # Shortened durations
    }

    def __init__(self, character):
        self.character = character

    def get_stamina(self):
        return self.character.db.stamina or 10

    def set_stamina(self, value):
        self.character.db.stamina = value
        return True

    def apply_combat_modifiers(self, hit_chance, damage, maneuver_type=None):
        hit_chance += self.COMBAT_MODIFIERS["base_hit_chance"]
        damage *= (1 - self.COMBAT_MODIFIERS["damage_reduction"])
        return hit_chance, damage

    def drain_stamina(self, amount):
        drain = amount * self.COMBAT_MODIFIERS["stamina_drain"]
        self.set_stamina(max(self.get_stamina() - drain, 0))
        return drain

    def can_retreat(self, dex, athletics):
        difficulty = (10 - dex) * self.COMBAT_MODIFIERS["retreat_difficulty"] - athletics
        return difficulty < 5, difficulty

    def apply_crowd_control(self, duration):
        return duration * self.COMBAT_MODIFIERS["crowd_control_duration"]

    def social_reaction_to_combat(self, location, standing):
        if location == "public":
            return "Guards intervene"
        elif location == "laborer":
            return "Workers join in or scatter"
        elif location == "underbelly":
            return "Ignored or thieves take advantage"
        return "Unusual response"
