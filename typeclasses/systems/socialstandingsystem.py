"""
Social Standing System for Korvessa

Handles faction standings, thresholds, and effects on prices, access, NPC attitudes, guard responses, and rumors.
Designed for easy integration with personality, skills, and world systems.
"""

FACTIONS = [
    "Civic_Order",
    "Laborers",
    "Merchants",
    "Nobility",
    "Underbelly",
    "Watcher_Cult",
    "Scholars",
    "Feyliks_Freefolk",
]

STANDING_THRESHOLDS = {
    "Trusted": 1000,
    "Favored": 200,
    "Neutral": -199,
    "Distrusted": -200,
    "Hated": -2000,
}

class SocialStandingSystem:
    def __init__(self, character):
        self.character = character
        if not hasattr(self.character.db, "standing") or self.character.db.standing is None:
            self.character.db.standing = {f: 0 for f in FACTIONS}

    def get_standing(self, faction):
        return self.character.db.standing.get(faction, 0)

    def set_standing(self, faction, value):
        if faction not in FACTIONS:
            return False, "Invalid faction"
        self.character.db.standing[faction] = value
        return True, f"Set {faction} standing to {value}"

    def adjust_standing(self, faction, amount):
        if faction not in FACTIONS:
            return False, "Invalid faction"
        self.character.db.standing[faction] = self.get_standing(faction) + amount
        return True, f"Adjusted {faction} standing by {amount}"

    def get_standing_tier(self, faction):
        value = self.get_standing(faction)
        if value >= STANDING_THRESHOLDS["Trusted"]:
            return "Trusted"
        elif value >= STANDING_THRESHOLDS["Favored"]:
            return "Favored"
        elif value > STANDING_THRESHOLDS["Neutral"]:
            return "Neutral"
        elif value > STANDING_THRESHOLDS["Distrusted"]:
            return "Distrusted"
        else:
            return "Hated"

    def get_all_standings(self):
        return {f: self.get_standing(f) for f in FACTIONS}

    def get_all_tiers(self):
        return {f: self.get_standing_tier(f) for f in FACTIONS}
