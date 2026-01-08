"""
Custom Look command that handles petitions viewing.
"""

from evennia.commands.default.general import CmdLook as DefaultCmdLook


class CmdLook(DefaultCmdLook):
    """
    Look at the world and people around you with petition support.
    
    Usage:
        look
        look <object>
        look petitions     - View your petitions
        look pending       - View your pending petitions
    """
    
    def func(self):
        """Override look to handle petitions."""
        caller = self.caller
        
        # Check if looking at petitions
        if self.args and self.args.lower() == "petitions":
            self.view_petitions(caller)
            return
        elif self.args and self.args.lower() == "pending":
            self.view_pending(caller)
            return
        
        # Otherwise use default look
        super().func()
    
    def view_petitions(self, char):
        """Display active petitions for the character."""
        petitions = getattr(char.db, 'petitions', [])
        active_petitions = [p for p in petitions if p.get('status') == 'active']
        
        if not active_petitions:
            char.msg("|YYou have no active petitions.|n")
            return
        
        char.msg("|c=== Your Petitions ===|n")
        for p in active_petitions:
            timestamp = p.get('timestamp', '').strftime('%Y-%m-%d %H:%M') if hasattr(p.get('timestamp', ''), 'strftime') else str(p.get('timestamp', ''))
            char.msg(f"  |w[#{p.get('id', '?')}]|n [{timestamp}] to {p.get('target', '?')}: {p.get('message', '?')}")
            char.msg(f"      To erase: erase petitions {p.get('id', '?')}")
    
    def view_pending(self, char):
        """Display pending petitions for the character."""
        petitions = getattr(char.db, 'petitions', [])
        pending_petitions = [p for p in petitions if p.get('status') == 'pending']
        
        if not pending_petitions:
            char.msg("|YYou have no pending petitions.|n")
            return
        
        char.msg("|c=== Your Pending Petitions ===|n")
        char.msg("|yThese petitions are being reviewed by other staff members.|n")
        for p in pending_petitions:
            timestamp = p.get('timestamp', '').strftime('%Y-%m-%d %H:%M') if hasattr(p.get('timestamp', ''), 'strftime') else str(p.get('timestamp', ''))
            char.msg(f"  |w[#{p.get('id', '?')}]|n [{timestamp}] to {p.get('target', '?')}: {p.get('message', '?')}")
            char.msg(f"      To erase: erase pending {p.get('id', '?')}")
