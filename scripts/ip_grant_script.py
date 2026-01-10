"""
IP Grant Script - Automatic Investment Points Distribution

This script grants IP to all online players at regular intervals:
- Runs at 00:00, 04:00, 08:00, 12:00, 16:00, 20:00 (every 4 hours)
- Grants a small but meaningful amount of IP (3-5 IP)
- Only grants to players who are logged in and puppeting a character

To start this script (run once in-game as admin):
    @py from scripts.ip_grant_script import IPGrantScript; IPGrantScript.create_if_not_exists()

To stop/remove:
    @script/stop ip_grant_script

To check status:
    @script ip_grant_script
"""

from evennia.scripts.scripts import DefaultScript
from evennia.accounts.models import AccountDB
from evennia.comms.models import ChannelDB
from django.utils import timezone
from datetime import datetime, timedelta
from random import randint


# IP grant amounts
IP_GRANT_MIN = 3
IP_GRANT_MAX = 5

# Target hours for IP grants (24-hour format)
GRANT_HOURS = [0, 4, 8, 12, 16, 20]


class IPGrantScript(DefaultScript):
    """
    Periodically grants IP to online players.
    
    Runs every hour and checks if it's a grant hour.
    When it is, grants IP to all online, puppeting players.
    """
    
    key = "ip_grant_script"
    desc = "Grants IP to online players every 4 hours"
    
    def at_script_creation(self):
        """Initialize the script."""
        # Run every hour to check if it's grant time
        # (More precise timing would require complex scheduling)
        self.interval = 3600  # 1 hour in seconds
        self.persistent = True
        self.start_delay = True
        
        # Track last grant hour to prevent double-grants
        self.db.last_grant_hour = None
    
    def at_repeat(self):
        """Check if it's time to grant IP."""
        now = timezone.now()
        current_hour = now.hour
        
        # Check if this is a grant hour and we haven't already granted this hour
        if current_hour in GRANT_HOURS:
            last_grant = self.db.last_grant_hour
            
            # Only grant if we haven't granted this hour yet
            # Use both hour and day to handle server restarts
            grant_key = f"{now.date()}_{current_hour}"
            
            if last_grant != grant_key:
                self._grant_ip_to_online_players()
                self.db.last_grant_hour = grant_key
    
    def _grant_ip_to_online_players(self):
        """Grant IP to all online players who are puppeting characters."""
        try:
            grants_given = 0
            
            # Get all online accounts
            for account in AccountDB.objects.all():
                try:
                    # Check if account has active sessions
                    sessions = account.sessions.all()
                    if not sessions:
                        continue
                    
                    # Get the puppeted character
                    for session in sessions:
                        puppet = session.puppet
                        if puppet and hasattr(puppet, 'db'):
                            # Grant IP
                            ip_amount = randint(IP_GRANT_MIN, IP_GRANT_MAX)
                            current_ip = getattr(puppet.db, 'ip', 0) or 0
                            puppet.db.ip = current_ip + ip_amount
                            
                            # Notify the player
                            puppet.msg(f"|g[+{ip_amount} IP]|n Automatic Investment Points grant. Total: |y{puppet.db.ip}|n IP")
                            
                            grants_given += 1
                            
                            # Only grant once per account (not per session)
                            break
                            
                except Exception as e:
                    self._debug_log(f"Error granting IP to account {account.name}: {e}")
            
            # Log the grant
            if grants_given > 0:
                self._debug_log(f"Granted IP to {grants_given} online players")
                
        except Exception as e:
            self._debug_log(f"IP grant error: {e}")
    
    def _debug_log(self, message):
        """Log a debug message to Splattercast channel."""
        try:
            splattercast = ChannelDB.objects.get_channel("Splattercast")
            if splattercast:
                splattercast.msg(f"IP_GRANT: {message}")
        except Exception:
            pass
    
    @classmethod
    def create_if_not_exists(cls):
        """
        Create the IP grant script if it doesn't already exist.
        Call this from @py to set up the script.
        """
        from evennia.scripts.models import ScriptDB
        
        # Check if script already exists
        existing = ScriptDB.objects.filter(db_key="ip_grant_script")
        if existing.exists():
            return existing.first()
        
        # Create new script
        script = cls.create(key="ip_grant_script")
        return script


# Additional utility functions for manual IP grants

def grant_ip_to_all_online(amount):
    """
    Manually grant IP to all online players.
    
    Usage (from @py):
        from scripts.ip_grant_script import grant_ip_to_all_online
        grant_ip_to_all_online(10)  # Grant 10 IP to everyone online
    """
    count = 0
    for account in AccountDB.objects.all():
        sessions = account.sessions.all()
        for session in sessions:
            puppet = session.puppet
            if puppet and hasattr(puppet, 'db'):
                current_ip = getattr(puppet.db, 'ip', 0) or 0
                puppet.db.ip = current_ip + amount
                puppet.msg(f"|g[+{amount} IP]|n Admin grant. Total: |y{puppet.db.ip}|n IP")
                count += 1
                break  # Only once per account
    
    return count
