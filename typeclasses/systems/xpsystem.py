"""
XP Economy System for Korvessa

Tracks XP, enforces daily cap, and provides APIs for gaining, spending, and sunset buyout logic.
Designed for easy integration with skills, purchases, and story systems.
"""

class XPSystem:
    XP_DAILY_CAP = 200
    XP_USE_COSTS = {
        "training_point": 200,
        "minor_npc_interaction": 400,
        "story_notice": 600,
        "small_business": 5000,
        "full_shop": 36000,
        "plot_progression": 4200,
    }

    def __init__(self, character):
        self.character = character

    def get_xp(self):
        return self.character.db.xp or 0

    def add_xp(self, amount):
        daily_xp = self.character.db.daily_xp or 0
        if daily_xp + amount > self.XP_DAILY_CAP:
            return False, f"Daily XP cap ({self.XP_DAILY_CAP}) exceeded"
        self.character.db.xp = self.get_xp() + amount
        self.character.db.daily_xp = daily_xp + amount
        return True, f"Added {amount} XP"

    def spend_xp(self, use_type):
        cost = self.XP_USE_COSTS.get(use_type)
        if cost is None:
            return False, "Invalid XP use type"
        if self.get_xp() < cost:
            return False, f"Not enough XP (need {cost})"
        self.character.db.xp = self.get_xp() - cost
        return True, f"Spent {cost} XP on {use_type}"

    def sunset_buyout(self, buyout_type):
        self.character.db.xp = 0
        return True, f"XP spent on {buyout_type} (character sunset)"
