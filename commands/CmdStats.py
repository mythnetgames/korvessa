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
        def stat_line(attr, name, abbr):
            # Special calculation for Empathy stat
            if attr == "emp":
                # Empathy = 33% SMRT + 33% EDGE + 34% EMP
                smrt = getattr(char, "smrt", 0)
                edge = getattr(char, "edge", 0)
                emp = getattr(char, "emp", 0)
                val = int(0.33 * smrt + 0.33 * edge + 0.34 * emp)
                maxval = int(0.33 * getattr(char, "max_smrt", smrt) + 0.33 * getattr(char, "max_edge", edge) + 0.34 * getattr(char, "max_emp", emp))
            else:
                val = getattr(char, attr, 0)
                maxval = getattr(char, f"max_{attr}", val)
            return f"|y{name:<10}|n [ |w{val}|n / |g{maxval}|n ]"
        # Build two columns
        for i in range(4):
            left = left_stats[i]
            right = right_stats[i]
            msg += f"{stat_line(*left):<25}{stat_line(*right):<25}\n"
        # Chrome/augmentations section
        msg += "\n|#870000No chrome or augmentations.|n\n"
        # Skill table
        skills = [
            "Chemical", "Modern Medicine", "Holistic Medicine", "Surgery", "Science", "Dodge", "Blades", "Pistols", "Rifles", "Melee", "Brawling", "Martial Arts", "Grappling", "Snooping", "Stealing", "Hiding", "Sneaking", "Disguise", "Tailoring", "Tinkering", "Manufacturing", "Cooking", "Forensics", "Decking", "Electronics", "Mercantile", "Streetwise", "Paint/Draw/Sculpt", "Instrument"
        ]
        # Underlined header, 'Raw' aligned to column 21
        msg += "\n|y|B|uSkill                Raw|n\n"
        for skill in skills:
            raw = getattr(char, skill.lower().replace("/", "_"), 0)
            msg += f"{skill:<20}{raw:>3}\n"
        char.msg(msg)
