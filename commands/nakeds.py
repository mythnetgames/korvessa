"""
Nakeds command for managing naked body part descriptions.
Allows setting detailed descriptions for individual body parts that are visible 
when not covered by clothing, with pronoun substitution support.
"""

from evennia import Command


class CmdNakeds(Command):
    """
    Manage naked body part descriptions for your character.
    
    Usage:
        @nakeds                           - View all your naked descriptions
        @naked <bodypart> is <description> - Set a description for a body part
        @naked <bodypart>/clear           - Clear a description for a body part
    
    Examples:
        @naked reye is "%p right eye bulges as if it is about to fall out of %p head at any moment."
        @naked face is "%p face is weathered and scarred from years of battle."
        @naked face/clear
    
    Available body parts:
        leye, reye, lear, rear, head, face, neck, lshoulder, rshoulder, 
        larm, rarm, lhand, rhand, back, chest, abdomen, groin, ass, 
        lthigh, rthigh, lshin, rshin, lfoot, rfoot
    
    Pronoun substitution:
        %s = he/she/it
        %o = him/her/it
        %p = his/her/its
        %q = his/hers/its
        %r = himself/herself/itself
    
    Capitalize the % to capitalize the pronoun (%S, %O, %P, %Q, %R).
    """
    key = "nakeds"
    aliases = ["naked"]
    locks = "cmd:all()"
    help_category = "Character"

    VALID_BODYPARTS = {
        "leye", "reye", "lear", "rear", "head", "face", "neck",
        "lshoulder", "rshoulder", "larm", "rarm", "lhand", "rhand",
        "back", "chest", "abdomen", "groin", "ass",
        "lthigh", "rthigh", "lshin", "rshin", "lfoot", "rfoot"
    }

    def func(self):
        caller = self.caller
        
        # No arguments - show all nakeds
        if not self.args:
            self.show_nakeds(caller)
            return
        
        args = self.args.split()
        
        # Check for /clear suffix
        if "/" in args[0]:
            bodypart, suffix = args[0].split("/", 1)
            if suffix.lower() == "clear":
                self.clear_naked(caller, bodypart)
                return
        
        # Set a naked description - must have 'is' separator
        if "is" not in self.args:
            caller.msg(f"|RUsage: @naked <bodypart> is <description> or @naked <bodypart>/clear|n")
            return
        
        parts = self.args.split(" is ", 1)
        bodypart = parts[0].strip().lower()
        description = parts[1].strip() if len(parts) > 1 else ""
        # Remove leading/trailing quotes if present
        if (description.startswith('"') and description.endswith('"')) or (description.startswith("'") and description.endswith("'")):
            description = description[1:-1].strip()
        
        if not description:
            caller.msg("|RYou must provide a description.|n")
            return
        
        self.set_naked(caller, bodypart, description)

    def show_nakeds(self, caller):
        """Display all naked descriptions for the character."""
        nakeds = caller.db.nakeds or {}
        
        if not nakeds:
            caller.msg("|CYou have no naked body part descriptions set.|n")
            return
        
        msg = "|C=== Naked Body Parts ===|n\n"
        for bodypart in sorted(nakeds.keys()):
            desc = nakeds[bodypart]
            msg += f"|G{bodypart}:|n {desc}\n"
        
        caller.msg(msg)

    def set_naked(self, caller, bodypart, description):
        """Set a naked description for a body part."""
        if bodypart not in self.VALID_BODYPARTS:
            caller.msg(f"|RInvalid body part: {bodypart}|n")
            caller.msg(f"|CValid parts: {', '.join(sorted(self.VALID_BODYPARTS))}|n")
            return
        
        nakeds = caller.db.nakeds or {}
        nakeds[bodypart] = description
        caller.db.nakeds = nakeds
        
        caller.msg(f"|GSet naked {bodypart}:|n {description}")

    def clear_naked(self, caller, bodypart):
        """Clear a naked description for a body part."""
        bodypart = bodypart.lower()
        
        if bodypart not in self.VALID_BODYPARTS:
            caller.msg(f"|RInvalid body part: {bodypart}|n")
            return
        
        nakeds = caller.db.nakeds or {}
        if bodypart in nakeds:
            del nakeds[bodypart]
            caller.db.nakeds = nakeds
            caller.msg(f"|GCleared naked {bodypart}.|n")
        else:
            caller.msg(f"|RNo description set for {bodypart}.|n")
