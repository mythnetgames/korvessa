"""
Cleanup script for idle/disconnected sessions.

This script runs periodically to:
1. Find sessions that have been idle for too long
2. Remove phantom characters left by network disconnects
3. Clean up stale account sessions
"""

from evennia.scripts.scripts import DefaultScript
from evennia.accounts.models import AccountDB
from evennia.comms.models import ChannelDB
from django.utils import timezone
from datetime import timedelta


class IdleSessionCleanup(DefaultScript):
    """
    Periodically clean up idle and phantom sessions.
    Prevents duplicate characters and ghost accounts.
    """
    
    key = "idle_session_cleanup"
    desc = "Cleans up idle sessions and phantom characters"
    
    def at_script_creation(self):
        """Initialize the script."""
        # Run every 5 minutes (300 seconds)
        self.interval = 300
        self.persistent = True
        self.start_delay = True
        
    def at_repeat(self):
        """Clean up idle/phantom sessions."""
        try:
            # Configuration
            IDLE_TIMEOUT_HOURS = 24
            IDLE_TIMEOUT = timedelta(hours=IDLE_TIMEOUT_HOURS)
            
            now = timezone.now()
            cleaned_up = 0
            
            # Get all accounts
            for account in AccountDB.objects.all():
                try:
                    # Get all sessions for this account
                    sessions = account.sessions.all()
                    
                    if not sessions:
                        continue
                        
                    # Check for idle sessions
                    for session in sessions:
                        # Get last activity time
                        last_cmd_time = getattr(session, 'cmdset_timestamp', None)
                        if not last_cmd_time:
                            last_cmd_time = session.connect_time
                        
                        # If idle too long, disconnect
                        time_since_activity = now - last_cmd_time
                        if time_since_activity > IDLE_TIMEOUT:
                            self._disconnect_session(account, session)
                            cleaned_up += 1
                            
                except Exception as e:
                    # Log but continue
                    self._debug_log(f"Error processing account {account.name}: {e}")
                    
            # Log cleanup results
            if cleaned_up > 0:
                self._debug_log(f"Cleaned up {cleaned_up} idle sessions")
                
        except Exception as e:
            self._debug_log(f"Cleanup script error: {e}")
            
    def _disconnect_session(self, account, session):
        """Safely disconnect a session."""
        try:
            # Unpuppet the character first if puppeted
            if session.puppet:
                character = session.puppet
                # Move character to their home location
                if hasattr(character, 'home'):
                    character.move_to(character.home, quiet=True)
                else:
                    # Fall back to start location
                    from django.conf import settings
                    default_location = settings.DEFAULT_OBJECT_TYPECLASS.objects.get_start_location()
                    if default_location:
                        character.move_to(default_location, quiet=True)
                        
                session.unpuppet()
            
            # Disconnect the session
            session.disconnect()
            
        except Exception as e:
            self._debug_log(f"Error disconnecting session: {e}")
            
    def _debug_log(self, msg):
        """Send message to debug channel."""
        try:
            splattercast = ChannelDB.objects.get_channel("Splattercast")
            splattercast.msg(f"CLEANUP: {msg}")
        except:
            pass


class PhantomCharacterCleanup(DefaultScript):
    """
    Find and clean up duplicate/phantom character instances.
    Runs less frequently than idle cleanup (every 30 minutes).
    """
    
    key = "phantom_character_cleanup"
    desc = "Cleans up duplicate and phantom characters"
    
    def at_script_creation(self):
        """Initialize the script."""
        # Run every 30 minutes
        self.interval = 1800
        self.persistent = True
        self.start_delay = True
        
    def at_repeat(self):
        """Find and handle duplicate characters."""
        try:
            from evennia.objects.models import ObjectDB
            from typeclasses.characters import Character
            
            # Find duplicate characters for same account
            accounts = {}
            
            for char in ObjectDB.objects.filter(db_typeclass_path='typeclasses.characters.Character'):
                try:
                    # Get account that owns this character
                    account = getattr(char, 'account', None)
                    if not account:
                        continue
                        
                    if account not in accounts:
                        accounts[account] = []
                    accounts[account].append(char)
                except:
                    pass
            
            # Check for duplicates
            duplicates_found = 0
            for account, characters in accounts.items():
                if len(characters) > 1:
                    # Keep the one that's been puppeted most recently
                    # Move others to home location
                    characters_sorted = sorted(
                        characters, 
                        key=lambda c: getattr(c, 'last_puppet_time', timezone.now()),
                        reverse=True
                    )
                    
                    # Keep the first (most recently used)
                    for char in characters_sorted[1:]:
                        try:
                            # Move to home
                            if hasattr(char, 'home'):
                                char.move_to(char.home, quiet=True)
                            # Force disconnect any active puppeting
                            for session in account.sessions.all():
                                if session.puppet == char:
                                    session.unpuppet()
                            duplicates_found += 1
                        except Exception as e:
                            self._debug_log(f"Error handling duplicate: {e}")
                            
            if duplicates_found > 0:
                self._debug_log(f"Found and handled {duplicates_found} duplicate characters")
                
        except Exception as e:
            self._debug_log(f"Phantom cleanup error: {e}")
            
    def _debug_log(self, msg):
        """Send message to debug channel."""
        try:
            splattercast = ChannelDB.objects.get_channel("Splattercast")
            splattercast.msg(f"PHANTOM_CLEANUP: {msg}")
        except:
            pass
