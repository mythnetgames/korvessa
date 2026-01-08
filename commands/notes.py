"""
Player-to-staff notes system.
Players leave notes that staff can review and act on.
"""

from evennia import Command, search_object, EvMenu
from datetime import datetime
from django.db.models import Q


# Available note tags
NOTE_TAGS = [
    "Character Goals",
    "Significant Event",
    "NPC Interaction",
    "PC Interaction",
    "Employment",
    "Investigation",
    "Faction Activity",
    "Combat/Conflict",
    "Plot Development",
    "Staff Assistance Needed",
    "Documentation",
    "Other"
]


class CmdAddNote(Command):
    """
    Leave a note for staff.
    
    This command allows you to document your character's actions,
    goals, and events for staff to review.
    """
    key = "@add-note"
    aliases = ["@addnote"]
    locks = "cmd:all()"
    help_category = "OOC"

    def get_help(self, caller, *args, **kwargs):
        """Return help documentation."""
        return """
|cPLAYER HELP - @ADD-NOTE|n

Leave a note for staff about your character's actions, goals, or events.

|wUsage:|n
  @add-note

This will prompt you through a menu to:
1. Select a tag describing the note's purpose
2. Enter a subject line
3. Write your note content

|wGood note examples:|n
  Tag: Employment
  Subject: Left resume with Hookie for bartender position
  Content: Approached Hookie about a bartender job. Discussed pay and hours. 
           Waiting to hear back about the position.

  Tag: Significant Event
  Subject: Attacked unpuppeted Triad member in Kowloon Walled City
  Content: Engaged in combat with a Triad enforcer who was unpuppeted.
           Defeated him. This should attract attention from the faction.

|wTags available:|n
  Character Goals, Significant Event, NPC Interaction, PC Interaction,
  Employment, Investigation, Faction Activity, Combat/Conflict,
  Plot Development, Staff Assistance Needed, Documentation, Other

|wRead your notes:|n
  @notes  - View all your notes
  @paged-notes  - View notes with pagination

|wWhy leave notes:|n
  Staff cannot see everything. Notes help us track your character's
  actions, goals, and plot developments. Always include context, motivation,
  and what you want to happen next.

|wSee Also:|n
  @notes  - View your notes
  @paged-notes  - Browse notes with pages
"""

        def func(self):
            """Start the note creation menu."""
            caller = self.caller
            EvMenu(
                caller,
                "commands.notes",
                startnode="tag_select",
                persist=False,
                store={}
            )


class CmdNotes(Command):
    """
    View your notes (non-paged).
    """
    key = "@notes"
    locks = "cmd:all()"
    help_category = "OOC"

    def get_help(self, caller, *args, **kwargs):
        """Return help documentation."""
        return """
|cPLAYER HELP - @NOTES|n

View all your notes in a single display.

|wUsage:|n
  @notes

Shows all your notes from oldest to newest with:
  - Note ID number
  - Tag/Category
  - Subject line
  - When you wrote it
  - Status (New/Read)

For large numbers of notes, use @paged-notes for easier browsing.

|wSee Also:|n
  @add-note  - Leave a new note
  @paged-notes  - Browse notes with pagination
"""

    def func(self):
        """Display all player's notes."""
        caller = self.caller
        notes = getattr(caller.db, 'character_notes', None) or []
        
        if not notes:
            caller.msg("|YYou have no notes.|n")
            return
        
        # Sort by ID (ascending, oldest first)
        sorted_notes = sorted(notes, key=lambda n: n.get('id', 0))
        
        caller.msg("|c=== Your Notes ===|n")
        for note in sorted_notes:
            note_id = note.get('id', '?')
            tag = note.get('tag', '?')
            subject = note.get('subject', '?')
            timestamp = note.get('timestamp', '').strftime('%Y-%m-%d %H:%M') if hasattr(note.get('timestamp', ''), 'strftime') else str(note.get('timestamp', ''))
            is_read = note.get('read_by_staff', False)
            status = "|gRead|n" if is_read else "|yNew|n"
            
            caller.msg(f"|w[{note_id}]|n |c[{tag}]|n {subject}")
            caller.msg(f"      {timestamp} - Status: {status}")
            caller.msg(f"      View: |w@read-note {note_id}|n")
            caller.msg("")


class CmdPagedNotes(Command):
    """
    Browse your notes with pagination.
    """
    key = "@paged-notes"
    locks = "cmd:all()"
    help_category = "OOC"

    def get_help(self, caller, *args, **kwargs):
        """Return help documentation."""
        return """
|cPLAYER HELP - @PAGED-NOTES|n

Browse your notes with pagination (5 notes per page).

|wUsage:|n
  @paged-notes
  @paged-notes <page_number>

Shows your notes in an easy-to-browse format with page navigation.

|wSee Also:|n
  @add-note  - Leave a new note
  @notes  - View all notes at once
"""

    def func(self):
        """Display paged notes."""
        caller = self.caller
        notes = getattr(caller.db, 'character_notes', None) or []
        
        if not notes:
            caller.msg("|YYou have no notes.|n")
            return
        
        # Sort by ID (ascending, oldest first)
        sorted_notes = sorted(notes, key=lambda n: n.get('id', 0))
        
        # Parse page number if provided
        page_num = 1
        if self.args:
            try:
                page_num = int(self.args.strip())
            except ValueError:
                caller.msg("Invalid page number.")
                return
        
        # Create paginated display
        pages_per_screen = 5
        total_pages = (len(sorted_notes) + pages_per_screen - 1) // pages_per_screen
        
        if page_num < 1 or page_num > total_pages:
            caller.msg(f"Page {page_num} does not exist. Valid range: 1-{total_pages}")
            return
        
        # Calculate start and end indices
        start_idx = (page_num - 1) * pages_per_screen
        end_idx = start_idx + pages_per_screen
        page_notes = sorted_notes[start_idx:end_idx]
        
        # Display header
        caller.msg(f"|c=== Your Notes (Page {page_num}/{total_pages}) ===|n")
        
        # Display notes on this page
        for note in page_notes:
            note_id = note.get('id', '?')
            tag = note.get('tag', '?')
            subject = note.get('subject', '?')
            timestamp = note.get('timestamp', '').strftime('%Y-%m-%d %H:%M') if hasattr(note.get('timestamp', ''), 'strftime') else str(note.get('timestamp', ''))
            is_read = note.get('read_by_staff', False)
            status = "|gRead|n" if is_read else "|yNew|n"
            
            caller.msg(f"|w[{note_id}]|n |c[{tag}]|n {subject}")
            caller.msg(f"      {timestamp} - Status: {status}")
            caller.msg(f"      View: |w@read-note {note_id}|n")
            caller.msg("")
        
        # Display navigation
        if total_pages > 1:
            nav = "|y["
            if page_num > 1:
                nav += f"@paged-notes {page_num - 1}|n|y (Previous) "
            nav += f"Page {page_num}/{total_pages}"
            if page_num < total_pages:
                nav += "|y (Next) |w@paged-notes " + str(page_num + 1) + "|y]|n"
            else:
                nav += "|y]|n"
            caller.msg(nav)


class CmdReadNote(Command):
    """
    Read a specific note you wrote.
    """
    key = "@read-note"
    aliases = ["@readnote"]
    locks = "cmd:all()"
    help_category = "OOC"

    def func(self):
        """Display a specific note."""
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: @read-note <note_id>")
            return
        
        try:
            note_id = int(self.args.strip())
        except ValueError:
            caller.msg("Invalid note ID.")
            return
        
        notes = getattr(caller.db, 'character_notes', None) or []
        
        for note in notes:
            if note.get('id') == note_id:
                tag = note.get('tag', '?')
                subject = note.get('subject', '?')
                content = note.get('content', '?')
                timestamp = note.get('timestamp', '').strftime('%Y-%m-%d %H:%M') if hasattr(note.get('timestamp', ''), 'strftime') else str(note.get('timestamp', ''))
                is_read = note.get('read_by_staff', False)
                status = "|gRead by staff|n" if is_read else "|yNot yet read by staff|n"
                
                caller.msg(f"|c=== Note #{note_id} ===|n")
                caller.msg(f"|wTag:|n {tag}")
                caller.msg(f"|wSubject:|n {subject}")
                caller.msg(f"|wDate:|n {timestamp}")
                caller.msg(f"|wStatus:|n {status}")
                caller.msg(f"|wContent:|n\n{content}")
                return
        
        caller.msg(f"Note #{note_id} not found.")


# ============================================================================
# MENU NODES FOR NOTE CREATION
# ============================================================================

def tag_select(caller, raw_string, **kwargs):
    store = kwargs.get("store", {})
    options = []
    for i, tag in enumerate(NOTE_TAGS, 1):
        options.append((str(i), tag, "tag_selected", {"selected_tag": tag}))
    text = "|cSelect a tag for your note:|n\n\n"
    for i, tag in enumerate(NOTE_TAGS, 1):
        text += f"  |w{i}|n - {tag}\n"
    return text, options

    
    store = kwargs.get("store", {})
    selected_tag = kwargs.get("selected_tag")
    if selected_tag:
        store["tag"] = selected_tag
    return subject_input(caller, raw_string, **kwargs)

    # Store note on character
    store = kwargs.get("store", {})
    if raw_string and raw_string.strip():
        store["subject"] = raw_string.strip()
        return content_input(caller, "", **kwargs)
    text = f"""
|cEnter a subject line for your note:|n

Current tag: |w{store.get('tag', '?')}|n

|yBad examples:|n
  Job
  Need job
  Talked to NPC

|yGood examples:|n
  Looking for a bartender job
  Left a resume with Hookie for bartender position
  Asked a Triad member about joining as a bruiser
"""
    return text, ()

    if not getattr(caller.db, 'character_notes', None):
    store = kwargs.get("store", {})
    if raw_string and raw_string.strip():
        store["content"] = raw_string.strip()
        return confirm_note(caller, "", **kwargs)
    text = f"""
|cEnter the content of your note:|n

Current tag: |w{store.get('tag', '?')}|n
Current subject: |w{store.get('subject', '?')}|n

|yWrite clearly and include:|n
  - What happened
  - Why your character did it
  - What your character wants to happen next

You can write multiple paragraphs.
"""
    return text, ()

        caller.db.character_notes = []
    store = kwargs.get("store", {})
    text = f"""
|c=== Review Your Note ===|n

|wTag:|n {store.get('tag', '?')}
|wSubject:|n {store.get('subject', '?')}
|wContent:|n
{store.get('content', '?')}

|y[1]|n Save this note
|y[2]|n Cancel
"""
    options = [
        ("1", "Save this note", "save_note"),
        ("2", "Cancel", "cancel_note"),
    ]
    return text, options

    caller.db.character_notes.append(note_entry)
    store = kwargs.get("store", {})
    note_entry = {
        "id": get_next_note_id(caller),
        "timestamp": datetime.now(),
        "tag": store.get("tag", "Other"),
        "subject": store.get("subject", "(Untitled)"),
        "content": store.get("content", ""),
        "read_by_staff": False,
    }
    if not getattr(caller.db, 'character_notes', None):
        caller.db.character_notes = []
    caller.db.character_notes.append(note_entry)
    notify_staff_new_note(caller, note_entry)
    text = f"""
|g=== Note Saved ===|n

Your note has been saved and will be reviewed by staff.

|wTag:|n {store.get('tag', '?')}
|wSubject:|n {store.get('subject', '?')}

Staff will be notified of your note. Thank you!
"""
    caller.msg(text)
    return None

    
    caller.msg("|yNote creation cancelled.|n")
    return None
    # Notify all staff
    notify_staff_new_note(caller, note_entry)
    
    text = f"""
|g=== Note Saved ===|n

Your note has been saved and will be reviewed by staff.

|wTag:|n {store.get('tag', '?')}
|wSubject:|n {store.get('subject', '?')}

Staff will be notified of your note. Thank you!
"""
    
    # End the menu
    menu.close_menu()
    caller.msg(text)


def cancel_note(menu, *args, **kwargs):
    """Cancel note creation."""
    menu.close_menu()
    menu.caller.msg("|yNote creation cancelled.|n")


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_next_note_id(char):
    """Get the next note ID for this character."""
    notes = getattr(char.db, 'character_notes', None) or []
    if not notes:
        return 1
    return max(n.get('id', 0) for n in notes) + 1


def notify_staff_new_note(character, note_entry):
    """Notify all online staff of a new note."""
    from evennia.comms.models import ChannelDB
    from evennia.accounts.models import AccountDB
    
    try:
        # Try to get Splattercast debug channel
        splattercast = ChannelDB.objects.get_channel("Splattercast")
        tag = note_entry.get('tag', 'Other')
        subject = note_entry.get('subject', '(Untitled)')
        note_id = note_entry.get('id', '?')
        splattercast.msg(f"|y[NEW NOTE]|n {character.key} - [{tag}] {subject} (Note #{note_id})")
    except:
        pass
    
    # Also send a message to online staff
    staff_list = AccountDB.objects.filter(is_superuser=True)
    for staff in staff_list:
        for session in staff.sessions.all():
            char = session.get_puppet()
            if char:
                tag = note_entry.get('tag', 'Other')
                subject = note_entry.get('subject', '(Untitled)')
                note_id = note_entry.get('id', '?')
                char.msg(f"|y[NEW NOTE FROM {character.key}]|n [{tag}] {subject} - Note #{note_id}")


# ============================================================================
# STAFF COMMANDS
# ============================================================================

class CmdViewAllNotes(Command):
    """
    Staff command to view all player notes.
    """
    key = "@view-notes"
    aliases = ["@viewnotes", "@staff-notes"]
    locks = "cmd:perm(Admin)"
    help_category = "Admin"

    def get_help(self, caller, *args, **kwargs):
        """Return help documentation."""
        return """
|cSTAFF HELP - @VIEW-NOTES|n

View all player notes or notes for a specific player.

|wUsage:|n
  @view-notes               - View recent notes from all players
  @view-notes <character>   - View all notes from a specific player
  @view-notes <tag>         - View notes with a specific tag
  @view-notes unread        - View only unread notes
  @view-notes mark-read <id> - Mark a note as read

|wExamples:|n
  @view-notes
  @view-notes TestDummy
  @view-notes "Employment"
  @view-notes unread
  @view-notes mark-read 5

|wNote that:|n
  Notes are marked as read when viewed by staff.
  Use 'mark-read' to mark notes staff have already reviewed.
"""

    def func(self):
        """Display player notes based on filter."""
        caller = self.caller
        
        if not self.args:
            # Show recent notes from all players
            self.show_recent_notes(caller)
        else:
            args = self.args.strip()
            
            if args.lower() == "unread":
                self.show_unread_notes(caller)
            elif args.lower().startswith("mark-read"):
                parts = args.split()
                if len(parts) > 1:
                    try:
                        note_id = int(parts[1])
                        self.mark_note_read(caller, note_id)
                    except ValueError:
                        caller.msg("Invalid note ID.")
                else:
                    caller.msg("Usage: @view-notes mark-read <note_id>")
            elif args.startswith('"') and args.endswith('"'):
                # Search by tag
                tag = args[1:-1]
                self.show_notes_by_tag(caller, tag)
            else:
                # Search by player name
                self.show_notes_by_player(caller, args)
    
    def show_recent_notes(self, caller, limit=20):
        """Show recent notes from all players."""
        from evennia.accounts.models import AccountDB
        
        all_notes = []
        for account in AccountDB.objects.all():
            for session in account.sessions.all():
                char = session.get_puppet()
                if char:
                    notes = getattr(char.db, 'character_notes', None) or []
                    for note in notes:
                        note['character'] = char.key
                        all_notes.append(note)
        
        # Sort by timestamp, newest first
        all_notes = sorted(all_notes, key=lambda n: n.get('timestamp', datetime.now()), reverse=True)
        all_notes = all_notes[:limit]
        
        if not all_notes:
            caller.msg("|YNo notes found.|n")
            return
        
        caller.msg(f"|c=== Recent Notes (Last {limit}) ===|n")
        for note in all_notes:
            self.display_note_summary(caller, note)
    
    def show_unread_notes(self, caller):
        """Show all unread notes."""
        from evennia.accounts.models import AccountDB
        
        all_notes = []
        for account in AccountDB.objects.all():
            for session in account.sessions.all():
                char = session.get_puppet()
                if char:
                    notes = getattr(char.db, 'character_notes', None) or []
                    for note in notes:
                        if not note.get('read_by_staff', False):
                            note['character'] = char.key
                            all_notes.append(note)
        
        if not all_notes:
            caller.msg("|gAll notes have been read.|n")
            return
        
        # Sort by timestamp, oldest first
        all_notes = sorted(all_notes, key=lambda n: n.get('timestamp', datetime.now()))
        
        caller.msg(f"|c=== Unread Notes ({len(all_notes)} total) ===|n")
        for note in all_notes:
            self.display_note_summary(caller, note)
    
    def show_notes_by_player(self, caller, player_name):
        """Show notes for a specific player."""
        targets = search_object(player_name)
        if not targets:
            caller.msg(f"Player '{player_name}' not found.")
            return
        
        target = targets[0]
        notes = getattr(target.db, 'character_notes', None) or []
        
        if not notes:
            caller.msg(f"|Y{target.key} has no notes.|n")
            return
        
        # Sort by ID
        notes = sorted(notes, key=lambda n: n.get('id', 0))
        
        caller.msg(f"|c=== Notes for {target.key} ({len(notes)} total) ===|n")
        for note in notes:
            note['character'] = target.key
            self.display_note_summary(caller, note)
    
    def show_notes_by_tag(self, caller, tag_name):
        """Show notes with a specific tag."""
        from evennia.accounts.models import AccountDB
        
        all_notes = []
        for account in AccountDB.objects.all():
            for session in account.sessions.all():
                char = session.get_puppet()
                if char:
                    notes = getattr(char.db, 'character_notes', None) or []
                    for note in notes:
                        if note.get('tag', '').lower() == tag_name.lower():
                            note['character'] = char.key
                            all_notes.append(note)
        
        if not all_notes:
            caller.msg(f"|YNo notes found with tag '{tag_name}'.|n")
            return
        
        # Sort by timestamp, newest first
        all_notes = sorted(all_notes, key=lambda n: n.get('timestamp', datetime.now()), reverse=True)
        
        caller.msg(f"|c=== Notes Tagged '{tag_name}' ({len(all_notes)} total) ===|n")
        for note in all_notes:
            self.display_note_summary(caller, note)
    
    def display_note_summary(self, caller, note):
        """Display a summary of a note."""
        char_name = note.get('character', '?')
        note_id = note.get('id', '?')
        tag = note.get('tag', '?')
        subject = note.get('subject', '?')
        timestamp = note.get('timestamp', '').strftime('%Y-%m-%d %H:%M') if hasattr(note.get('timestamp', ''), 'strftime') else str(note.get('timestamp', ''))
        is_read = note.get('read_by_staff', False)
        status = "|g[READ]|n" if is_read else "|y[NEW]|n"
        
        caller.msg(f"|w[{note_id}]|n {status} |c{char_name}|n - [{tag}] {subject}")
        caller.msg(f"      {timestamp} | View: |w@read-staff-note {char_name} {note_id}|n")
    
    def mark_note_read(self, caller, note_id):
        """Mark a note as read."""
        from evennia.accounts.models import AccountDB
        
        for account in AccountDB.objects.all():
            for session in account.sessions.all():
                char = session.get_puppet()
                if char:
                    notes = getattr(char.db, 'character_notes', None) or []
                    for note in notes:
                        if note.get('id') == note_id:
                            note['read_by_staff'] = True
                            caller.msg(f"|gMarked note #{note_id} as read.|n")
                            return
        
        caller.msg(f"Note #{note_id} not found.")


class CmdReadStaffNote(Command):
    """
    Staff command to read a player's note.
    """
    key = "@read-staff-note"
    aliases = ["@readstaffnote"]
    locks = "cmd:perm(Admin)"
    help_category = "Admin"

    def func(self):
        """Read a specific player note."""
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: @read-staff-note <character> <note_id>")
            return
        
        parts = self.args.split()
        if len(parts) < 2:
            caller.msg("Usage: @read-staff-note <character> <note_id>")
            return
        
        player_name = ' '.join(parts[:-1])
        try:
            note_id = int(parts[-1])
        except ValueError:
            caller.msg("Invalid note ID.")
            return
        
        targets = search_object(player_name)
        if not targets:
            caller.msg(f"Player '{player_name}' not found.")
            return
        
        target = targets[0]
        notes = getattr(target.db, 'character_notes', None) or []
        
        for note in notes:
            if note.get('id') == note_id:
                # Mark as read
                note['read_by_staff'] = True
                
                tag = note.get('tag', '?')
                subject = note.get('subject', '?')
                content = note.get('content', '?')
                timestamp = note.get('timestamp', '').strftime('%Y-%m-%d %H:%M') if hasattr(note.get('timestamp', ''), 'strftime') else str(note.get('timestamp', ''))
                
                caller.msg(f"|c=== Note #{note_id} from {target.key} ===|n")
                caller.msg(f"|wTag:|n {tag}")
                caller.msg(f"|wSubject:|n {subject}")
                caller.msg(f"|wDate:|n {timestamp}")
                caller.msg(f"|wContent:|n\n{content}")
                return
        
        caller.msg(f"Note #{note_id} not found for {target.key}.")

