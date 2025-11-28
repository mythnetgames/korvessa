from evennia import Command

class CmdStats(Command):
    """
    View your character's stats.
    Usage: stats
    Aliases: sc, score
    """
    key = "stats"
    aliases = ["sc", "score"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        char = self.caller
        # Stat definitions: (attribute, display name, abbreviation)
        stats = [
            ("smrt", "Smarts", "SMRT"),
            ("will", "Willpower", "WILL"),
            ("edge", "Edge", "EDGE"),
            ("ref", "Reflexes", "REF"),
            ("body", "Body", "BODY"),
            ("dex", "Dexterity", "DEX"),
            ("emp", "Empathy", "EMP"),
            ("tech", "Technique", "TECH"),
        ]
        # Two-column display
        left_stats = stats[:4]
        right_stats = stats[4:]
        msg = "|ystats|n\n"
        # Get stat values (current/max)
        def stat_line(attr, name):
            val = getattr(char, attr, 0)
            maxval = getattr(char, f"max_{attr}", val)
            return f"|y{name:<10}|n [ |w{val}|n / |g{maxval}|n ]"
        # Build two columns
        for i in range(4):
            left = left_stats[i]
            right = right_stats[i]
            msg += f"{stat_line(*left):<25}{stat_line(*right):<25}\n"
        # Chrome/augmentations section
        msg += "\n|rNo chrome or augmentations.|n\n"
        # Skill table
        skills = [
            "Chemical", "Modern Medicine", "Holistic Medicine", "Surgery", "Science", "Dodge", "Blades", "Pistols", "Rifles", "Melee", "Brawling", "Martial Arts", "Grappling", "Snooping", "Stealing", "Hiding", "Sneaking", "Disguise", "Tailoring", "Tinkering", "Manufacturing", "Cooking", "Forensics", "Decking", "Electronics", "Mercantile", "Streetwise", "Paint/Draw/Sculpt", "Instrument"
        ]
        msg += "\n|[bg_b]|wSkill        Raw|n\n"
        for skill in skills:
            raw = getattr(char, skill.lower().replace("/", "_"), 0)
            msg += f"{skill:<20}{raw}\n"
        char.msg(msg)
