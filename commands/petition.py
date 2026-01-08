"""
Petition system for players to submit out-of-character requests to staff.
"""

from evennia import Command, search_object
from evennia.utils import utils
from datetime import datetime


class CmdPetition(Command):
    """
    Submit an out-of-character petition to staff.
    
    Usage:
        petition all <message>
        petition <staff member> <message>
    
    This sends an OOC message to the staff. If no staff are online, your
    petition will be stored in the system for later review.
    
    Examples:
        petition all Please animate this ripper so I can ask about chrome.
        petition Dalao My bullets are healing instead of doing damage!
    
    View your petitions:
        look petitions
    
    Erase a petition:
        erase petitions <number>
    """
    key = "petition"
    locks = "cmd:all()"
    help_category = "OOC"

    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: petition all | [staff member] <message>")
            return
        
        # Parse the petition
        parts = self.args.split(None, 1)
        if len(parts) < 2:
            caller.msg("Usage: petition all | [staff member] <message>")
            return
        
        target = parts[0].lower()
        message = parts[1]
        
        # Create petition entry
        petition_entry = {
            "id": self.get_next_petition_id(caller),
            "timestamp": datetime.now(),
            "target": target,
            "message": message,
            "status": "active",  # active, pending, or resolved
        }
        
        # Store petition on character
        if not hasattr(caller.db, 'petitions'):
            caller.db.petitions = []
        caller.db.petitions.append(petition_entry)
        
        # Notify caller
        caller.msg(f"|gPetition #{petition_entry['id']} submitted to {target}.|n")
        
        # Try to notify staff
        self.notify_staff(caller, target, message, petition_entry['id'])
    
    def get_next_petition_id(self, char):
        """Get the next petition ID for this character."""
        if not hasattr(char.db, 'petitions') or not char.db.petitions:
            return 1
        return max(p.get('id', 0) for p in char.db.petitions) + 1
    
    def notify_staff(self, petitioner, target, message, petition_id):
        """Notify staff members of the petition."""
        from evennia.comms.models import ChannelDB
        
        # Try to find the staff channel
        try:
            staff_channel = ChannelDB.objects.get_channel("Staff")
            if target.lower() == "all":
                staff_msg = f"|y[PETITION #{petition_id}]|n {petitioner.key}: {message}"
            else:
                staff_msg = f"|y[PETITION #{petition_id} to {target}]|n {petitioner.key}: {message}"
            
            staff_channel.msg(staff_msg)
        except:
            # Staff channel doesn't exist or no online staff
            pass


class CmdViewPetitions(Command):
    """
    View your petitions and pending requests.
    
    Usage:
        look petitions
        look pending
    """
    key = "look"
    locks = "cmd:all()"
    help_category = "OOC"
    
    def func(self):
        # This is handled by the room's look command
        # We'll implement this through a custom look handler
        pass


class CmdErasePetition(Command):
    """
    Erase one of your petitions or pending requests.
    
    Usage:
        erase petitions <number>
        erase pending <number>
    """
    key = "erase"
    locks = "cmd:all()"
    help_category = "OOC"

    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: erase petitions <number> | erase pending <number>")
            return
        
        parts = self.args.split(None, 1)
        if len(parts) < 2:
            caller.msg("Usage: erase petitions <number> | erase pending <number>")
            return
        
        petition_type = parts[0].lower()
        try:
            petition_id = int(parts[1])
        except ValueError:
            caller.msg("Please specify a valid petition number.")
            return
        
        if petition_type == "petitions":
            self.erase_petition(caller, petition_id)
        elif petition_type == "pending":
            self.erase_pending(caller, petition_id)
        else:
            caller.msg("Usage: erase petitions <number> | erase pending <number>")
    
    def erase_petition(self, char, petition_id):
        """Erase an active petition."""
        if not hasattr(char.db, 'petitions') or not char.db.petitions:
            char.msg("You have no petitions to erase.")
            return
        
        for petition in char.db.petitions:
            if petition.get('id') == petition_id and petition.get('status') == 'active':
                char.db.petitions.remove(petition)
                char.msg(f"|gErased petition #{petition_id}.|n")
                return
        
        char.msg(f"No active petition found with ID #{petition_id}.")
    
    def erase_pending(self, char, petition_id):
        """Erase a pending petition."""
        if not hasattr(char.db, 'petitions') or not char.db.petitions:
            char.msg("You have no pending petitions to erase.")
            return
        
        for petition in char.db.petitions:
            if petition.get('id') == petition_id and petition.get('status') == 'pending':
                char.db.petitions.remove(petition)
                char.msg(f"|gErased pending petition #{petition_id}.|n")
                return
        
        char.msg(f"No pending petition found with ID #{petition_id}.")


class CmdStaffPetition(Command):
    """
    Staff command to manage petitions.
    
    Usage:
        petitions pending <char> <id>    - Move petition to pending
        petitions resolve <char> <id>    - Resolve a petition
        petitions view <char>            - View all petitions from a character
    """
    key = "petitions"
    locks = "cmd:perm(Immortal)"
    help_category = "Admin"

    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: petitions pending <char> <id> | petitions resolve <char> <id> | petitions view <char>")
            return
        
        parts = self.args.split()
        action = parts[0].lower()
        
        if action == "view" and len(parts) >= 2:
            self.view_petitions(caller, ' '.join(parts[1:]))
        elif action == "pending" and len(parts) >= 3:
            try:
                petition_id = int(parts[-1])
                char_name = ' '.join(parts[1:-1])
                self.move_to_pending(caller, char_name, petition_id)
            except ValueError:
                caller.msg("Invalid petition ID.")
        elif action == "resolve" and len(parts) >= 3:
            try:
                petition_id = int(parts[-1])
                char_name = ' '.join(parts[1:-1])
                self.resolve_petition(caller, char_name, petition_id)
            except ValueError:
                caller.msg("Invalid petition ID.")
        else:
            caller.msg("Usage: petitions pending <char> <id> | petitions resolve <char> <id> | petitions view <char>")
    
    def view_petitions(self, admin, char_name):
        """View all petitions from a character."""
        targets = search_object(char_name)
        if not targets:
            admin.msg(f"Character '{char_name}' not found.")
            return
        
        char = targets[0]
        petitions = getattr(char.db, 'petitions', [])
        
        if not petitions:
            admin.msg(f"{char.key} has no petitions.")
            return
        
        admin.msg(f"|c=== Petitions from {char.key} ===|n")
        for p in petitions:
            status = p.get('status', 'active').upper()
            timestamp = p.get('timestamp', '').strftime('%Y-%m-%d %H:%M') if hasattr(p.get('timestamp', ''), 'strftime') else str(p.get('timestamp', ''))
            admin.msg(f"  |w[#{p.get('id', '?')}]|n ({status}) [{timestamp}] to {p.get('target', '?')}: {p.get('message', '?')}")
    
    def move_to_pending(self, admin, char_name, petition_id):
        """Move a petition to pending status."""
        targets = search_object(char_name)
        if not targets:
            admin.msg(f"Character '{char_name}' not found.")
            return
        
        char = targets[0]
        petitions = getattr(char.db, 'petitions', [])
        
        for petition in petitions:
            if petition.get('id') == petition_id:
                petition['status'] = 'pending'
                admin.msg(f"|gMoved petition #{petition_id} to Pending.|n")
                char.msg(f"|yYour petition #{petition_id} is now Pending and will be reviewed by other staff.|n")
                return
        
        admin.msg(f"No petition found with ID #{petition_id}.")
    
    def resolve_petition(self, admin, char_name, petition_id):
        """Resolve (delete) a petition."""
        targets = search_object(char_name)
        if not targets:
            admin.msg(f"Character '{char_name}' not found.")
            return
        
        char = targets[0]
        petitions = getattr(char.db, 'petitions', [])
        
        for petition in petitions:
            if petition.get('id') == petition_id:
                petitions.remove(petition)
                admin.msg(f"|gResolved petition #{petition_id}.|n")
                char.msg(f"|yYour petition #{petition_id} has been resolved.|n")
                return
        
        admin.msg(f"No petition found with ID #{petition_id}.")
