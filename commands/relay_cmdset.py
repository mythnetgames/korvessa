"""
Relay system builder/admin command registration for Evennia.
Add this to your default_cmdsets.py to enable relay commands for builders/admins.
"""
from evennia import CmdSet
from typeclasses.relay import RelayCmdSet

class BuilderRelayCmdSet(CmdSet):
    """CmdSet to add relay system commands for builders/admins."""
    key = "BuilderRelayCmdSet"
    priority = 1
    def at_cmdset_creation(self):
        self.add(RelayCmdSet())
