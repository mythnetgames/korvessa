"""
Unlogged-in commands for the Korvessa login system.

These commands are available before account login.
"""

from evennia.commands.command import Command as BaseCommand
from evennia.accounts.models import AccountDB
from django.contrib.auth.models import User
from django.db import IntegrityError


class UnloggedCommand(BaseCommand):
    """Base command for unlogged-in users."""
    
    def at_pre_cmd(self):
        """Check if we're at login screen."""
        # Prevent commands except on login screen
        return False


class CmdAccountCreate(UnloggedCommand):
    """
    Create a new account.
    
    Usage:
        create <username> <password>
    
    Creates a new account. Username must be unique.
    """
    
    key = "create"
    aliases = ["c"]
    locks = "cmd:all()"
    help_category = "Account"
    
    def func(self):
        """Create new account."""
        if not self.args or len(self.args.split()) < 2:
            self.caller.msg("|r[ERROR]|n Usage: create <username> <password>")
            return
        
        username, password = self.args.split(None, 1)
        
        # Validate username
        if len(username) < 3:
            self.caller.msg("|r[ERROR]|n Username must be at least 3 characters.")
            return
        
        if len(password) < 6:
            self.caller.msg("|r[ERROR]|n Password must be at least 6 characters.")
            return
        
        # Try to create account
        try:
            user = User.objects.create_user(username, email="", password=password)
            account = AccountDB.objects.create(user=user)
            
            # Store additional account data
            account.db.email = ""
            account.db.ansi_color = True
            account.db.created_chars = []
            account.db.retired_chars = []
            account.db.pending_apps = []
            account.db.discord_id = None
            account.save()
            
            self.caller.msg(f"|g[SUCCESS]|n Account '{username}' created! Please log in.")
            
        except IntegrityError:
            self.caller.msg("|r[ERROR]|n Account name already exists.")
        except Exception as e:
            self.caller.msg(f"|r[ERROR]|n Failed to create account: {str(e)}")


class CmdAccountLogin(UnloggedCommand):
    """
    Log in to an existing account.
    
    Usage:
        connect <username> <password>
    
    or
    
        login <username> <password>
    """
    
    key = "connect"
    aliases = ["login", "l"]
    locks = "cmd:all()"
    help_category = "Account"
    
    def func(self):
        """Log in to account."""
        if not self.args or len(self.args.split()) < 2:
            self.caller.msg("|r[ERROR]|n Usage: connect <username> <password>")
            return
        
        username, password = self.args.split(None, 1)
        
        try:
            user = User.objects.get(username=username)
            account = user.account
            
            if account.check_password(password):
                self.caller.msg(f"|g[SUCCESS]|n Logged in as {username}.")
                # Transition to character selection menu
                account.msg("|#ffff00CHARACTER MENU|n\n")
                self.show_character_menu(account)
            else:
                self.caller.msg("|r[ERROR]|n Invalid password.")
        except User.DoesNotExist:
            self.caller.msg("|r[ERROR]|n Account not found.")
        except Exception as e:
            self.caller.msg(f"|r[ERROR]|n Login failed: {str(e)}")
    
    def show_character_menu(self, account):
        """Display character selection menu."""
        menu_text = """
|#ffff00═══════════════════════════════════════════════════════════════════════════════|n
|#ffff00CHARACTER MANAGEMENT|n
|#ffff00═══════════════════════════════════════════════════════════════════════════════|n

  1. Login a character.
  2. Submit a character application.
                (Approval required)
  3. Delete a pending application.
  4. Retire your current character.
  5. View your characters.
  6. Update your e-mail address.
  7. Change your account password.
  8. Send/Check OOC Mail.

 11. Log Out.

|#ffff00Your Selection:|n """
        account.msg(menu_text)
