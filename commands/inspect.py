"""
Inspect command - wrapper for @examine functionality for builders.
"""

from evennia.commands.default.building import CmdExamine


class CmdInspect(CmdExamine):
    """
    Inspect detailed information about an object, room, or character.
    
    Usage:
        inspect [<object>[/attrname]]
        inspect *<account>[/attrname]
    
    Switches:
        /account - examine an Account (same as adding *)
        /object - examine an Object
        /script - examine a Script
        /channel - examine a Channel
    
    Shows detailed game info about an object including its attributes,
    scripts, permissions, and other technical details. If no argument
    is given, the current location is inspected.
    
    This is a builder command for debugging and development.
    """
    
    key = "inspect"
    aliases = ["insp"]
    locks = "cmd:perm(Builder)"
    help_category = "Building"
