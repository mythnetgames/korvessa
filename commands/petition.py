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
        if not getattr(caller.db, 'petitions', None):
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
        from evennia.accounts.models import AccountDB
        
        if target.lower() == "all":
            # Notify all online admin/immortal users
            staff_msg = f"|y[PETITION #{petition_id}]|n {petitioner.key}: {message}"
            
            # Find all online admins
            for account in AccountDB.objects.filter(db_is_connected=True):
                if account.character and hasattr(account.character, 'is_superuser'):
                    if account.character.is_superuser or account.is_superuser:
                        account.character.msg(staff_msg)
            
            # Also try staff channel
            try:
                staff_channel = ChannelDB.objects.get_channel("Staff")
                staff_channel.msg(staff_msg)
            except:
                pass
        else:
            # Notify specific staff member
            from evennia.utils.search import search_object
            staff_targets = search_object(target)
            if staff_targets:
                staff_member = staff_targets[0]
                staff_msg = f"|y[PETITION #{petition_id} to you]|n {petitioner.key}: {message}"
                staff_member.msg(staff_msg)
            
            # Also notify via staff channel
            try:
                staff_channel = ChannelDB.objects.get_channel("Staff")
                staff_channel.msg(f"|y[PETITION #{petition_id} to {target}]|n {petitioner.key}: {message}")
            except:
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
        petitions                        - View your own petitions
        petitions personal               - View your own petitions
        petitions all                    - View all petitions from all players
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
            # No args - show own petitions
            self.view_own_petitions(caller)
            return
        
        parts = self.args.split()
        action = parts[0].lower()
        
        if action == "personal":
            self.view_own_petitions(caller)
        elif action == "all":
            self.view_all_petitions(caller)
        elif action == "view" and len(parts) >= 2:
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
            caller.msg("Usage: petitions | petitions personal | petitions all | petitions pending <char> <id> | petitions resolve <char> <id> | petitions view <char>")
    
    def view_own_petitions(self, admin):
        """View all petitions from the admin themselves."""
        petitions = getattr(admin.db, 'petitions', None) or []
        
        if not petitions:
            admin.msg(f"You have no petitions.")
            return
        
        admin.msg(f"|c=== Your Petitions ===|n")
        for p in petitions:
            status = p.get('status', 'active').upper()
            timestamp = p.get('timestamp', '').strftime('%Y-%m-%d %H:%M') if hasattr(p.get('timestamp', ''), 'strftime') else str(p.get('timestamp', ''))
            admin.msg(f"  |w[#{p.get('id', '?')}]|n ({status}) [{timestamp}] to {p.get('target', '?')}: {p.get('message', '?')}")
    
    def view_all_petitions(self, admin):
        """View all petitions from all players."""
        from evennia.accounts.models import AccountDB
        
        all_petitions = []
        
        for account in AccountDB.objects.all():
            if account.character:
                petitions = getattr(account.character.db, 'petitions', None) or []
                for p in petitions:
                    p_with_char = p.copy()
                    p_with_char['character'] = account.character.key
                    all_petitions.append(p_with_char)
        
        if not all_petitions:
            admin.msg("There are no petitions in the system.")
            return
        
        # Sort by most recent first
        all_petitions.sort(key=lambda p: p.get('timestamp', ''), reverse=True)
        
        admin.msg(f"|c=== All Petitions in System ({len(all_petitions)} total) ===|n")
        for p in all_petitions:
            status = p.get('status', 'active').upper()
            char = p.get('character', '?')
            timestamp = p.get('timestamp', '').strftime('%Y-%m-%d %H:%M') if hasattr(p.get('timestamp', ''), 'strftime') else str(p.get('timestamp', ''))
            admin.msg(f"  |w[#{p.get('id', '?')}]|n ({status}) [{timestamp}] from {char} to {p.get('target', '?')}: {p.get('message', '?')}")
    
    
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
