"""
Chrome/Cyberware Listing Command

Displays all available chrome with their names, shortnames, and what they do.
"""

from evennia import Command
from world.chrome_prototypes import (
    NT_PROBCAL, NT_PARAMP, BS_SKULL_PLATING, NT_NERVES, BS_NERVES, MGT_NRVZAP, NT_AXON,
    MORIKAWA_KABUTO, NT_SURFACE_WIRING, BS_FACE_PLATING, MORIKAWA_MENPO,
    MGT_BUG_EYES, BS_CYBEREYE_SET, AS_CYBEREYE_SET, BS_CYBEREYE, AS_CYBEREYE,
    BS_REINFORCED_CYBEREYE_SET, BS_REINFORCED_CYBEREYE, MORIKAWA_GAZE,
    BS_CYBEREAR_SET_EXT, BS_CYBEREAR_SET_INT, AS_CYBEREAR_SET_EXT, AS_CYBEREAR_SET_INT,
    BS_CYBERARM_SET, AS_CYBERARM_SET, BS_CYBERARM, AS_CYBERARM,
    BS_CYBERLEG_SET, AS_CYBERLEG_SET, BS_CYBERLEG, AS_CYBERLEG,
    BS_CYBERFEET_SET, AS_CYBERFEET_SET, BS_CYBERFOOT, AS_CYBERFOOT,
)


class CmdChromeList(Command):
    """
    List all available chrome/cyberware with descriptions and shortnames.

    Usage:
        chromelist
        chromelist <category>

    Categories:
        head        - Cranial implants and headgear
        face        - Facial implants and armor
        eyes        - Eye replacement systems
        ears        - Ear replacement systems
        arms        - Arm replacement systems
        legs        - Leg replacement systems
        feet        - Foot replacement systems
        all         - Everything
    """

    key = "chromelist"
    aliases = ["chromelist"]
    locks = "cmd:perm(Builder)"
    help_category = "Admin"

    CHROME_PROTOTYPES = {
        # HEAD CHROME
        "head": [
            NT_PROBCAL, NT_PARAMP, BS_SKULL_PLATING, NT_NERVES, BS_NERVES, MGT_NRVZAP, NT_AXON, MORIKAWA_KABUTO,
        ],
        # FACE CHROME
        "face": [
            NT_SURFACE_WIRING, BS_FACE_PLATING, MORIKAWA_MENPO,
        ],
        # EYE CHROME
        "eyes": [
            MGT_BUG_EYES, BS_CYBEREYE_SET, AS_CYBEREYE_SET, BS_CYBEREYE, AS_CYBEREYE,
            BS_REINFORCED_CYBEREYE_SET, BS_REINFORCED_CYBEREYE, MORIKAWA_GAZE,
        ],
        # EAR CHROME
        "ears": [
            BS_CYBEREAR_SET_EXT, BS_CYBEREAR_SET_INT, AS_CYBEREAR_SET_EXT, AS_CYBEREAR_SET_INT,
        ],
        # ARM CHROME
        "arms": [
            BS_CYBERARM_SET, AS_CYBERARM_SET, BS_CYBERARM, AS_CYBERARM,
        ],
        # LEG CHROME
        "legs": [
            BS_CYBERLEG_SET, AS_CYBERLEG_SET, BS_CYBERLEG, AS_CYBERLEG,
        ],
        # FEET CHROME
        "feet": [
            BS_CYBERFEET_SET, AS_CYBERFEET_SET, BS_CYBERFOOT, AS_CYBERFOOT,
        ],
    }

    def func(self):
        caller = self.caller
        category = self.args.strip().lower() if self.args.strip() else "all"

        if category == "all":
            # Show all categories
            self._display_all_chrome(caller)
        elif category in self.CHROME_PROTOTYPES:
            self._display_category(caller, category)
        else:
            caller.msg(f"Unknown category: {category}")
            caller.msg("Available categories: head, face, eyes, ears, arms, legs, feet, all")
            return

    def _display_all_chrome(self, caller):
        """Display all chrome organized by category."""
        output = []
        output.append("|y=== ALL CHROME ===|n")
        output.append("")

        for category in ["head", "face", "eyes", "ears", "arms", "legs", "feet"]:
            self._add_category_output(output, category)

        caller.msg("\n".join(output))

    def _display_category(self, caller, category):
        """Display chrome from a specific category."""
        output = []
        output.append(f"|y=== {category.upper()} CHROME ===|n")
        output.append("")
        self._add_category_output(output, category)
        caller.msg("\n".join(output))

    def _add_category_output(self, output, category):
        """Add formatted chrome list for a category to output."""
        output.append(f"|c{category.upper()}|n")
        output.append("-" * 70)

        for proto in self.CHROME_PROTOTYPES[category]:
            key = proto.get("key", "Unknown")
            shortname = proto.get("shortname", "N/A")
            buff_desc = proto.get("buff_description", "")
            abilities = proto.get("abilities", "")
            chrome_type = proto.get("chrome_type", "")
            empathy_cost = proto.get("empathy_cost", 0)

            # Build what it does
            effects = []
            if buff_desc:
                effects.append(buff_desc)
            if abilities:
                effects.append(abilities)

            what_it_does = " | ".join(effects) if effects else "Cosmetic/Utility"

            # Color code based on type
            type_color = "|g[EXT]|n" if chrome_type == "external" else "|b[INT]|n"

            # Format the line
            line = f"  |w{key}|n {type_color}"
            line += f"\n      Shortname: |y{shortname}|n | Empathy: |r{empathy_cost}|n"
            line += f"\n      Effect: {what_it_does}"
            line += "\n"

            output.append(line)

        output.append("")
