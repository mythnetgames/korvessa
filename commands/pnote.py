"""
Pnote system for staff to leave messages for players.
"""

from evennia import Command, search_object
from datetime import datetime


class CmdPnotes(Command):
    """
    List and search pnotes.
    """
    key = "pnotes"
    locks = "cmd:all()"
    help_category = "OOC"

    def get_help(self, caller, *args, **kwargs):
        """Return appropriate help based on caller permission."""
        is_staff = caller.is_superuser if hasattr(caller, 'is_superuser') else False
        
        if is_staff:
            return """
|cSTAFF HELP - PNOTES|n

List and search pnotes left by staff for players.

|wUsage:|n
  pnotes                   - View your submitted petitions AND petitions for you
  pnotes <player>          - View a specific player's pnotes
  pnotes "<search term>"   - Search your pnotes for a term
  pnotes <player> "<term>" - Search a player's pnotes for a term

|wExamples:|n
  pnotes
  pnotes TestDummy
  pnotes "chrome"
  pnotes Dalao "combat"

|wSee Also:|n
  pnote   - Add a pnote for a player
  pread   - Read a player's pnote
  pdel    - Delete a pnote
"""
        else:
            return """
|cPLAYER HELP - PNOTES|n

View and search your pnotes from staff.

|wUsage:|n
  pnotes                 - List all your pnotes
  pnotes <search term>   - Search your pnotes for a term

|wExamples:|n
  pnotes
  pnotes "combat approval"
  pnotes chrome

|wSee Also:|n
  pread   - Read a specific pnote
  pdel    - Delete a pnote
"""

    def func(self):
        caller = self.caller
        is_staff = caller.is_superuser if hasattr(caller, 'is_superuser') else False
        
        if not self.args:
            # No args - list own pnotes
            if is_staff:
                self.list_pnotes(caller, caller, None)
            else:
                self.list_pnotes(caller, caller, None)
            return
        
        # Parse arguments
        args = self.args.strip()
        
        # Check for quoted search term
        if '"' in args:
            if is_staff:
                # Could be: pnotes "<term>" or pnotes <player> "<term>"
                # Find the quoted section
                quote_start = args.find('"')
                quote_end = args.find('"', quote_start + 1)
                
                if quote_end == -1:
                    caller.msg("Unclosed quote in search term.")
                    return
                
                search_term = args[quote_start+1:quote_end]
                before_quote = args[:quote_start].strip()
                
                if before_quote:
                    # pnotes <player> "<term>"
                    target_name = before_quote
                    targets = search_object(target_name)
                    if not targets:
                        caller.msg(f"Player '{target_name}' not found.")
                        return
                    target = targets[0]
                    self.list_pnotes(caller, target, search_term)
                else:
                    # pnotes "<term>"
                    self.list_pnotes(caller, caller, search_term)
            else:
                caller.msg("Players cannot use quoted search terms. Usage: pnotes <search term>")
        else:
            # No quotes - could be player name or search term (for players)
            if is_staff:
                # Try to find as player
                targets = search_object(args)
                if targets:
                    self.list_pnotes(caller, targets[0], None)
                else:
                    caller.msg(f"Player '{args}' not found.")
            else:
                # For players, it's a search term
                self.list_pnotes(caller, caller, args)
    
    def list_pnotes(self, caller, target, search_term=None):
        """List pnotes for a target, optionally filtered by search term."""
        pnotes = getattr(target.db, 'pnotes', None) or []
        
        if search_term:
            # Filter by search term (case-insensitive)
            search_lower = search_term.lower()
            filtered_pnotes = [p for p in pnotes if search_lower in p.get('message', '').lower()]
        else:
            filtered_pnotes = pnotes
        
        if not filtered_pnotes:
            if search_term:
                caller.msg(f"|YNo pnotes found matching '{search_term}'.|n")
            else:
                caller.msg(f"|YNo pnotes found.|n")
            return
        
        title = f"Pnotes for {target.key}" if target != caller else "Your Pnotes"
        if search_term:
            title += f" (matching '{search_term}')"
        
        caller.msg(f"|c=== {title} ===|n")
        for note in filtered_pnotes:
            from_staff = note.get('from_staff', '?')
            timestamp = note.get('timestamp', '').strftime('%Y-%m-%d %H:%M') if hasattr(note.get('timestamp', ''), 'strftime') else str(note.get('timestamp', ''))
            note_id = note.get('id', '?')
            preview = note.get('message', '')[:50] + ('...' if len(note.get('message', '')) > 50 else '')
            caller.msg(f"  |w[{note_id}]|n from {from_staff} [{timestamp}]: {preview}")
            caller.msg(f"        Read: |wpread {note_id}|n | Delete: |wpdel {note_id}|n")


class CmdPnote(Command):
    """
    View or add pnotes (staff messages to players).
    """
    key = "pnote"
    locks = "cmd:all()"
    help_category = "OOC"

    def get_help(self, caller, *args, **kwargs):
        """Return appropriate help based on caller permission."""
        is_staff = caller.is_superuser if hasattr(caller, 'is_superuser') else False
        
        if is_staff:
            return """
|cSTAFF HELP - PNOTE|n

Leave messages for players that they can read when they log in.

|wUsage:|n
  pnote <character> = <message>

|wExamples:|n
  pnote Test Dummy = Great work on that contract!
  pnote Dalao = Chrome approved for installation

|wSee Also:|n
  pnotes  - List and search pnotes
  pread   - Read a player's pnote
  pdel    - Delete a pnote
"""
        else:
            return """
|cPLAYER HELP - PNOTE|n

View pnotes left for you by staff.

|wUsage:|n
  pnote  - List all your pnotes

|wSee Also:|n
  pread   - Read a specific pnote
  pdel    - Delete a pnote
"""

    def func(self):
        caller = self.caller
        
        # Check if caller is staff
        is_staff = caller.is_superuser if hasattr(caller, 'is_superuser') else False
        
        if not self.args:
            # No args - show own pnotes (for players) or tell staff to provide target
            if is_staff:
                caller.msg("Usage: pnote <character> = <message>")
            else:
                self.view_own_pnotes(caller)
            return
        
        # If staff, parse target and message
        if is_staff:
            if '=' not in self.args:
                caller.msg("Usage: pnote <character> = <message>")
                return
            
            parts = self.args.split('=', 1)
            target_name = parts[0].strip()
            message = parts[1].strip()
            
            if not target_name or not message:
                caller.msg("Usage: pnote <character> = <message>")
                return
            
            self.add_pnote(caller, target_name, message)
        else:
            # Players can only list their own pnotes
            caller.msg("Usage: pnote")
    
    def view_own_pnotes(self, player):
        """Display list of pnotes for a player."""
        pnotes = getattr(player.db, 'pnotes', None) or []
        
        if not pnotes:
            player.msg("|YYou have no pnotes.|n")
            return
        
        player.msg("|c=== Your Pnotes ===|n")
        for i, note in enumerate(pnotes, 1):
            from_staff = note.get('from_staff', '?')
            timestamp = note.get('timestamp', '').strftime('%Y-%m-%d %H:%M') if hasattr(note.get('timestamp', ''), 'strftime') else str(note.get('timestamp', ''))
            preview = note.get('message', '')[:50] + ('...' if len(note.get('message', '')) > 50 else '')
            player.msg(f"  |w[{i}]|n from {from_staff} [{timestamp}]: {preview}")
            player.msg(f"       Read with: |wpread {i}|n")
    
    def add_pnote(self, staff, target_name, message):
        """Add a pnote for a player."""
        targets = search_object(target_name)
        if not targets:
            staff.msg(f"Player '{target_name}' not found.")
            return
        
        target = targets[0]
        
        # Create pnote entry
        pnote_entry = {
            "id": self.get_next_pnote_id(target),
            "timestamp": datetime.now(),
            "from_staff": staff.key,
            "message": message,
        }
        
        # Store pnote on target
        if not getattr(target.db, 'pnotes', None):
            target.db.pnotes = []
        target.db.pnotes.append(pnote_entry)
        
        staff.msg(f"|gPnote #{pnote_entry['id']} added to {target.key}.|n")
        
        # Notify target if online
        if target.sessions.all():
            target.msg(f"|y[PNOTE]|n You have received a new pnote from {staff.key}. Type |wpread|n to view.")
    
    def get_next_pnote_id(self, char):
        """Get the next pnote ID for this character."""
        pnotes = getattr(char.db, 'pnotes', None) or []
        if not pnotes:
            return 1
        return max(p.get('id', 0) for p in pnotes) + 1


class CmdPread(Command):
    """
    Read a pnote.
    """
    key = "pread"
    locks = "cmd:all()"
    help_category = "OOC"

    def get_help(self, caller, *args, **kwargs):
        """Return appropriate help based on caller permission."""
        is_staff = caller.is_superuser if hasattr(caller, 'is_superuser') else False
        
        if is_staff:
            return """
|cSTAFF HELP - PREAD|n

Read a pnote left for a player.

|wUsage:|n
  pread <entry>               - Read one of your own pnotes
  pread <character> <entry>   - Read a player's pnote

|wExamples:|n
  pread 1
  pread Test Dummy 1
  pread Dalao 3

|wSee Also:|n
  pnotes  - List and search pnotes
  pnote   - Add a pnote for a player
  pdel    - Delete a pnote
"""
        else:
            return """
|cPLAYER HELP - PREAD|n

Read one of your pnotes from staff.

|wUsage:|n
  pread <entry>  - Read a specific pnote by number

|wExamples:|n
  pread 1
  pread 2

To find the entry numbers, use:
  pnotes - Lists all your pnotes with their numbers

|wSee Also:|n
  pnotes  - List your pnotes
  pdel    - Delete a pnote
"""

    def func(self):
        caller = self.caller
        is_staff = caller.is_superuser if hasattr(caller, 'is_superuser') else False
        
        if not self.args:
            caller.msg("Usage: pread <entry> | pread <character> <entry>")
            return
        
        parts = self.args.split()
        
        if is_staff and len(parts) >= 2:
            # Staff reading someone else's pnote
            target_name = ' '.join(parts[:-1])
            try:
                pnote_id = int(parts[-1])
            except ValueError:
                caller.msg("Invalid pnote ID.")
                return
            
            self.read_other_pnote(caller, target_name, pnote_id)
        elif len(parts) == 1:
            # Player reading own pnote or staff shorthand
            try:
                pnote_id = int(parts[0])
            except ValueError:
                caller.msg("Invalid pnote ID.")
                return
            
            self.read_own_pnote(caller, pnote_id)
        else:
            caller.msg("Usage: pread <entry> | pread <character> <entry>")
    
    def read_own_pnote(self, char, pnote_id):
        """Read own pnote."""
        pnotes = getattr(char.db, 'pnotes', None) or []
        
        for note in pnotes:
            if note.get('id') == pnote_id:
                from_staff = note.get('from_staff', '?')
                timestamp = note.get('timestamp', '').strftime('%Y-%m-%d %H:%M') if hasattr(note.get('timestamp', ''), 'strftime') else str(note.get('timestamp', ''))
                message = note.get('message', '')
                
                char.msg(f"|c=== Pnote #{pnote_id} ===|n")
                char.msg(f"|yFrom:|n {from_staff}")
                char.msg(f"|yDate:|n {timestamp}")
                char.msg(f"|yMessage:|n\n{message}")
                return
        
        char.msg(f"No pnote found with ID #{pnote_id}.")
    
    def read_other_pnote(self, staff, target_name, pnote_id):
        """Staff reading another character's pnote."""
        targets = search_object(target_name)
        if not targets:
            staff.msg(f"Player '{target_name}' not found.")
            return
        
        target = targets[0]
        pnotes = getattr(target.db, 'pnotes', None) or []
        
        for note in pnotes:
            if note.get('id') == pnote_id:
                from_staff = note.get('from_staff', '?')
                timestamp = note.get('timestamp', '').strftime('%Y-%m-%d %H:%M') if hasattr(note.get('timestamp', ''), 'strftime') else str(note.get('timestamp', ''))
                message = note.get('message', '')
                
                staff.msg(f"|c=== Pnote #{pnote_id} for {target.key} ===|n")
                staff.msg(f"|yFrom:|n {from_staff}")
                staff.msg(f"|yDate:|n {timestamp}")
                staff.msg(f"|yMessage:|n\n{message}")
                return
        
        staff.msg(f"No pnote found with ID #{pnote_id} for {target.key}.")


class CmdPnoteDelete(Command):
    """
    Delete a pnote.
    
    Usage (Players):
        pdel <entry number>      - Delete your pnote
    
    Usage (Staff):
        pdel <character> <entry> - Delete a player's pnote
    """
    key = "pdel"
    locks = "cmd:all()"
    help_category = "OOC"

    def func(self):
        caller = self.caller
        is_staff = caller.is_superuser if hasattr(caller, 'is_superuser') else False
        
        if not self.args:
            caller.msg("Usage: pdel <entry> | pdel <character> <entry>")
            return
        
        parts = self.args.split()
        
        if is_staff and len(parts) >= 2:
            # Staff deleting someone else's pnote
            target_name = ' '.join(parts[:-1])
            try:
                pnote_id = int(parts[-1])
            except ValueError:
                caller.msg("Invalid pnote ID.")
                return
            
            self.delete_other_pnote(caller, target_name, pnote_id)
        elif len(parts) == 1:
            # Player deleting own pnote
            try:
                pnote_id = int(parts[0])
            except ValueError:
                caller.msg("Invalid pnote ID.")
                return
            
            self.delete_own_pnote(caller, pnote_id)
        else:
            caller.msg("Usage: pdel <entry> | pdel <character> <entry>")
    
    def delete_own_pnote(self, char, pnote_id):
        """Delete own pnote."""
        pnotes = getattr(char.db, 'pnotes', None) or []
        
        for note in pnotes:
            if note.get('id') == pnote_id:
                pnotes.remove(note)
                char.msg(f"|gDeleted pnote #{pnote_id}.|n")
                return
        
        char.msg(f"No pnote found with ID #{pnote_id}.")
    
    def delete_other_pnote(self, staff, target_name, pnote_id):
        """Staff deleting another character's pnote."""
        targets = search_object(target_name)
        if not targets:
            staff.msg(f"Player '{target_name}' not found.")
            return
        
        target = targets[0]
        pnotes = getattr(target.db, 'pnotes', None) or []
        
        for note in pnotes:
            if note.get('id') == pnote_id:
                pnotes.remove(note)
                staff.msg(f"|gDeleted pnote #{pnote_id} for {target.key}.|n")
                return
        
        staff.msg(f"No pnote found with ID #{pnote_id} for {target.key}.")
