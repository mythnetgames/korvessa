"""
Account

The Account represents the game "account" and each login has only one
Account object. An Account is what chats on default channels but has no
other in-game-world existence. Rather the Account puppets Objects (such
as Characters) in order to actually participate in the game world.


Guest

Guest accounts are simple low-level accounts that are created/deleted
on the fly and allows users to test the game without the commitment
of a full registration. Guest accounts are deactivated by default; to
activate them, add the following line to your settings file:

    GUEST_ENABLED = True

You will also need to modify the connection screen to reflect the
possibility to connect with a guest account. The setting file accepts
several more options for customizing the Guest account system.

"""

from evennia.accounts.accounts import DefaultAccount, DefaultGuest


class Account(DefaultAccount):
    def puppet_object(self, session, obj):
        """
        Called when this Account puppets a Character (obj) on a session.
        Override to force @mapon logic and handle location following.
        """
        # Call the original Evennia logic
        super().puppet_object(session, obj)
        
        # Force @mapon logic silently
        if hasattr(self, 'db'):
            self.db.mapper_enabled = True
        if hasattr(self, 'ndb'):
            self.ndb.mapper_enabled = True
        if session:
            session.ndb.mapper_enabled = True
        if hasattr(obj, 'ndb'):
            obj.ndb.mapper_enabled = True

    def unpuppet_object(self, session):
        """
        Called when an account stops puppeting an object.
        """
        # Call the original unpuppet
        super().unpuppet_object(session)

    def _is_clone_awakening_locked(self):
        """Check if this account is locked during clone awakening."""
        if getattr(self.ndb, '_clone_awakening_locked', False):
            return True
        # Also check all sessions
        for session in self.sessions.all():
            if getattr(session.ndb, '_clone_awakening_locked', False):
                return True
        return False

    def _is_death_choice_pending(self):
        """Check if this account is waiting for a death choice."""
        return getattr(self.ndb, '_death_choice_pending', False)

    def at_look(self, target=None, session=None, **kwargs):
        """
        Called when this object performs a look.
        Block OOC menu during clone awakening or death choice.
        """
        if self._is_clone_awakening_locked() or self._is_death_choice_pending():
            # Return empty string - don't show OOC menu during awakening/choice
            return ""
        return super().at_look(target=target, session=session, **kwargs)

    def msg(self, text=None, from_obj=None, session=None, options=None, **kwargs):
        """
        Override msg to allow messages during awakening, but block OOC menu.
        """
        # Always allow messages through - the cutscene needs to display
        super().msg(text=text, from_obj=from_obj, session=session, options=options, **kwargs)

    def check_available_slots(self, **kwargs):
        """
        Override Evennia's default to exclude archived characters from slot count.

        Helper method used to determine if an account can create additional characters
        using the character slot system. Archived characters don't count toward the limit.

        Returns:
            str (optional): An error message regarding the status of slots. If present, this
               will halt character creation. If not, character creation can proceed.
        """
        from django.conf import settings
        
        # Get max allowed characters
        max_slots = settings.MAX_NR_CHARACTERS
        if max_slots is None:
            # No limit
            return None
        
        # Count only active (non-archived) characters
        active_count = 0
        for char in self.characters:
            archived = char.db.archived if hasattr(char.db, 'archived') else False
            if not archived:
                active_count += 1
        
        # Check if we have slots available
        available_slots = max(0, max_slots - active_count)
        
        if available_slots <= 0:
            if not (self.is_superuser or self.check_permstring("Developer")):
                plural = "" if max_slots == 1 else "s"
                return f"You may only have a maximum of {max_slots} character{plural}."
        
        return None

    @property
    def at_character_limit(self):
        """
        Check if account has reached the maximum character limit.
        
        Note: This does NOT bypass for superusers anymore. The limit applies to everyone
        for menu display purposes. Character creation itself may still allow bypass.
        
        Returns:
            bool: True if at max characters, False otherwise.
        """
        from django.conf import settings
        
        max_slots = settings.MAX_NR_CHARACTERS
        if max_slots is None:
            return False
        
        # Count active (non-archived) characters - defensive coding
        active_count = 0
        for char in self.characters:
            if not char or not hasattr(char, 'db'):
                continue
            archived = getattr(char.db, 'archived', False)
            if not archived:
                active_count += 1
        
        return active_count >= max_slots

    def at_post_login(self, session=None, **kwargs):
        """
        Called after successful login, handles character detection and auto-puppeting.
        
        We override the default entirely because we have custom logic for:
        - Auto-puppeting single characters
        - Starting character creation for new accounts
        - Handling archived characters
        """
        # Block OOC menu if clone awakening is in progress
        if getattr(self.ndb, '_clone_awakening_locked', False):
            if session:
                session.ndb._clone_awakening_locked = True
            return  # Do not show OOC menu
        
        # Force map display ON for every account and session on login
        # Force @mapon logic on login, but do not echo any output or check coordinates
        self.db.mapper_enabled = True
        self.ndb.mapper_enabled = True
        self.db.show_room_desc = True
        self.ndb.show_room_desc = True
        if session:
            session.ndb.mapper_enabled = True
            session.ndb.show_room_desc = True
        # Use Evennia's account.characters (the _playable_characters list) - this is the authoritative source
        all_characters = self.characters.all()
        
        # Filter for active (non-archived) characters
        # Be defensive: only treat explicitly archived=True as archived
        active_chars = []
        for char in all_characters:
            archived_status = getattr(char.db, 'archived', False)
            
            # Only exclude if explicitly archived
            if archived_status is not True:
                active_chars.append(char)
        
        # CRITICAL: Only start character creation if there are ZERO active characters
        if len(active_chars) == 0:
            # No active characters - start character creation
            # Import here to avoid circular imports
            try:
                from commands.charcreate import start_character_creation
                
                # Restore last_character if it's missing but we have archived characters
                # This handles cases where last_character was cleared or lost
                if not self.db.last_character:
                    # Find most recently archived character
                    archived_chars = []
                    for char in all_characters:
                        if getattr(char.db, 'archived', False) is True:
                            archived_date = getattr(char.db, 'archived_date', 0)
                            archived_chars.append((archived_date, char))
                    
                    # Sort by archive date (most recent first) and use the newest
                    if archived_chars:
                        archived_chars.sort(reverse=True, key=lambda x: x[0])
                        self.db.last_character = archived_chars[0][1]
                
                # Check if they have a last_character (from death or manual archival)
                # If so, use respawn flow with flash clone + template options
                is_respawn = bool(self.db.last_character)
                old_character = self.db.last_character if is_respawn else None
                
                start_character_creation(self, is_respawn=is_respawn, old_character=old_character)
            except ImportError as e:
                # Graceful fallback if charcreate not available yet
                self.msg("|rCharacter creation system not available. Please contact an admin.|n")
        elif len(active_chars) == 1:
            # Exactly one active character - auto-puppet for convenience
            if session:
                self.puppet_object(session, active_chars[0])
            else:
                # No session means we can't auto-puppet - this shouldn't happen
                self.msg("|yAuto-puppet failed: No session. Use 'ic' to connect.|n")
        else:
            # Multiple active characters - let user choose with 'ic <name>'
            # The default OOC behavior will handle this
            pass


class Guest(DefaultGuest):
    """
    This class is used for guest logins. Unlike Accounts, Guests and their
    characters are deleted after disconnection.
    
    Guests are restricted to only character creation or ic <name> to play.
    """

    def at_post_login(self, session=None, **kwargs):
        """
        Called after successful guest login.
        
        Guests only get character creation or auto-puppet - no OOC menu.
        """
        # Get playable characters
        all_characters = self.characters.all()
        
        # Filter for active (non-archived) characters
        active_chars = []
        for char in all_characters:
            archived_status = getattr(char.db, 'archived', False)
            if archived_status is not True:
                active_chars.append(char)
        
        if len(active_chars) == 0:
            # No characters - start character creation
            try:
                from commands.charcreate import start_character_creation
                start_character_creation(self, is_respawn=False, old_character=None)
            except ImportError:
                self.msg("|rCharacter creation system not available. Please contact an admin.|n")
        elif len(active_chars) == 1:
            # One character - auto-puppet
            if session:
                self.puppet_object(session, active_chars[0])
            else:
                self.msg("|yUse |wic|y to enter the game.|n")
        else:
            # Multiple characters - tell them to use ic
            self.msg("|yYou have multiple characters. Use |wic <name>|y to enter the game.|n")
            for char in active_chars:
                self.msg(f"  - {char.key}")

    def at_look(self, target=None, session=None, **kwargs):
        """
        Block the OOC menu for guests - they should only use ic or chargen.
        """
        # Return minimal info instead of full OOC menu
        return ""
