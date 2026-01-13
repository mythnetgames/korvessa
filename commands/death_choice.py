"""
Death Choice Commands

Commands for choosing SLEEVE or DIE after death.
These are added to the account when death choice is presented.
"""

from evennia import Command, CmdSet
from evennia.commands.default.muxcommand import MuxCommand


class CmdDeathClone(MuxCommand):
    """
    Choose to transfer to your sleeve backup.
    
    Usage:
        sleeve
    """
    key = "clone"
    locks = "cmd:all()"
    help_category = "Death"
    
    def func(self):
        """Execute the clone choice."""
        # Get the account - when unpuppeted, caller IS the session
        # The session has .account attribute
        if hasattr(self.caller, 'account') and self.caller.account:
            account = self.caller.account
        elif hasattr(self.caller, 'sessions'):
            # Caller is likely an Account
            account = self.caller
        else:
            self.caller.msg("Error: Could not determine account.")
            return
        
        # Check if death choice is pending
        if not getattr(account.ndb, '_death_choice_pending', False):
            self.caller.msg("You are not currently facing a death choice.")
            return
        
        # Process the choice
        from typeclasses.death_progression import _process_death_choice
        _process_death_choice(account, "clone")


class CmdDeathDie(MuxCommand):
    """
    Choose to accept permanent death.
    
    Usage:
        die
    """
    key = "die"
    locks = "cmd:all()"
    help_category = "Death"
    
    def func(self):
        """Execute the die choice."""
        # Get the account
        if hasattr(self.caller, 'account') and self.caller.account:
            account = self.caller.account
        elif hasattr(self.caller, 'sessions'):
            account = self.caller
        else:
            self.caller.msg("Error: Could not determine account.")
            return
        
        # Check if death choice is pending
        if not getattr(account.ndb, '_death_choice_pending', False):
            self.caller.msg("You are not currently facing a death choice.")
            return
        
        # Process the choice
        from typeclasses.death_progression import _process_death_choice
        _process_death_choice(account, "die")


class DeathChoiceCmdSet(CmdSet):
    """
    Cmdset containing the death choice commands.
    Added to account when death choice is presented.
    Uses Replace mergetype to block all other commands.
    """
    key = "death_choice_cmdset"
    priority = 150
    mergetype = "Replace"
    no_exits = True
    no_objs = True
    
    def at_cmdset_creation(self):
        self.add(CmdDeathClone())
        self.add(CmdDeathDie())
