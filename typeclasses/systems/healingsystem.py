"""
Healing & Injury System for Korvessa

Tracks injuries by tier and provides APIs for adding, healing, and downgrading injuries using various methods.
Designed for easy integration with medical skills, rest, and staff tools.
"""

class HealingSystem:
    INJURY_TIERS = ["Minor", "Moderate", "Major", "Critical"]
    HEALING_METHODS = ["Bandaging", "First Aid", "Chirurgy", "Herbalism", "Rest"]

    def __init__(self, character):
        self.character = character

    def get_injuries(self):
        return self.character.db.injuries or []

    def add_injury(self, tier, description):
        if tier not in self.INJURY_TIERS:
            return False, "Invalid injury tier"
        injuries = self.character.db.injuries or []
        injuries.append({"tier": tier, "desc": description})
        self.character.db.injuries = injuries
        return True, f"Added {tier} injury: {description}"

    def heal_injury(self, method, amount=1):
        if method not in self.HEALING_METHODS:
            return False, "Invalid healing method"
        injuries = self.character.db.injuries or []
        healed = 0
        for i in range(amount):
            for idx, inj in enumerate(injuries):
                if method == "Bandaging" and inj["tier"] == "Minor":
                    injuries.pop(idx)
                    healed += 1
                    break
                elif method == "First Aid" and inj["tier"] in ["Minor", "Moderate"]:
                    if inj["tier"] == "Moderate":
                        inj["tier"] = "Minor"
                    else:
                        injuries.pop(idx)
                    healed += 1
                    break
                elif method == "Chirurgy" and inj["tier"] in ["Major", "Critical"]:
                    if inj["tier"] == "Critical":
                        inj["tier"] = "Major"
                    else:
                        injuries.pop(idx)
                    healed += 1
                    break
                elif method == "Herbalism" and inj["tier"] in ["Minor", "Moderate"]:
                    if inj["tier"] == "Moderate":
                        inj["tier"] = "Minor"
                        healed += 1
                        break
                elif method == "Rest":
                    injuries = [inj for inj in injuries if inj["tier"] != "Minor"]
                    healed = amount
                    break
        self.character.db.injuries = injuries
        return True, f"Healed {healed} injuries with {method}"
