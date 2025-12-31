
# ...existing code...

# Place CmdCreateCharacter after CharacterMenuCommand and all imports
class CmdCreateCharacter(CharacterMenuCommand):
    """
    Create a new character.

    Usage:
        charcreate <name> [=description]
    """
    key = "charcreate"
    aliases = ["createchar", "createcharacter", "newchar"]

    def func(self):
        """Create a new character for this account."""
        if not self.args:
            self.caller.msg("|r[ERROR]|n Usage: charcreate <name> [=description]")
            return
        parts = self.args.split("=", 1)
        name = parts[0].strip()
        desc = parts[1].strip() if len(parts) > 1 else ""
        if len(name) < 3:
            self.caller.msg("|r[ERROR]|n Character name must be at least 3 characters.")
            return
        from typeclasses.characters import Character
        # Check for duplicate name for this account
        from evennia.objects.models import ObjectDB
        if ObjectDB.objects.filter(db_key=name, db_account=self.caller).exists():
            self.caller.msg("|r[ERROR]|n You already have a character with that name.")
            return
        # Create the character
        char = Character.objects.create(db_key=name, db_account=self.caller)
        char.db.desc = desc
        char.at_object_creation()
        self.caller.msg(f"|g[SUCCESS]|n Character '{name}' created. You may now submit an application or log in as this character.")
"""
Character menu commands for post-login character selection and management.
"""

from evennia.commands.command import Command as BaseCommand
from evennia.objects.models import ObjectDB
from evennia.accounts.models import AccountDB


class CharacterMenuCommand(BaseCommand):
    """Base command for character menu."""
    
    key = "char_menu_base"
    locks = "cmd:all()"
    help_category = "Character"


class CmdLoginCharacter(CharacterMenuCommand):
    """
    Log in to one of your characters.
    
    Usage:
        login <character_name>
    
    or from the menu:
        1
    """
    
    key = "login"
    aliases = ["1", "play"]
    
    def func(self):
        """Login to character."""
        if not self.args:
            self.caller.msg("|r[ERROR]|n Which character do you want to play?")
            return
        
        char_name = self.args.strip()
        account = self.caller
        
        try:
            # Find character owned by this account
            character = ObjectDB.objects.get(db_key=char_name, db_account=account)
            
            # Puppeting is handled by Evennia - just notify
            account.msg(f"|g[SUCCESS]|n Entering the world as {char_name}...")
            
        except ObjectDB.DoesNotExist:
            account.msg("|r[ERROR]|n Character not found or not owned by you.")


class CmdSubmitApplication(CharacterMenuCommand):
    """
    Submit a character application for approval.
    
    Usage:
        apply
    
    or from the menu:
        2
    """
    
    key = "apply"
    aliases = ["2"]
    
    def func(self):
        """Submit character application."""
        account = self.caller
        account.msg("|y[INFO]|n Character application system not yet implemented.")


class CmdDeleteApplication(CharacterMenuCommand):
    """
    Delete a pending character application.
    
    Usage:
        delete_app
    
    or from the menu:
        3
    """
    
    key = "delete_app"
    aliases = ["3"]
    
    def func(self):
        """Delete application."""
        account = self.caller
        account.msg("|y[INFO]|n Application deletion not yet implemented.")


class CmdRetireCharacter(CharacterMenuCommand):
    """
    Retire your current character.
    
    Usage:
        retire
    
    or from the menu:
        4
    """
    
    key = "retire"
    aliases = ["4"]
    
    def func(self):
        """Retire character."""
        account = self.caller
        account.msg("|y[INFO]|n Character retirement not yet implemented.")


class CmdViewCharacters(CharacterMenuCommand):
    """
    View all your characters.
    
    Usage:
        characters
    
    or from the menu:
        5
    """
    
    key = "characters"
    aliases = ["5", "chars"]
    
    def func(self):
        """List all characters."""
        account = self.caller
        characters = ObjectDB.objects.filter(db_account=account, db_is_player=True)
        
        if not characters.exists():
            account.msg("|y[INFO]|n You have no characters yet.")
            return
        
        account.msg("|#ffff00YOUR CHARACTERS|n")
        account.msg("─" * 50)
        
        for char in characters:
            level = char.db.level or 1
            standing = char.db.standing or {}
            account.msg(f"  |w{char.key}|n (Level {level})")


class CmdUpdateEmail(CharacterMenuCommand):
    """
    Update your account email address.
    
    Usage:
        email <new_email@address.com>
    
    or from the menu:
        6
    """
    
    key = "email"
    aliases = ["6"]
    
    def func(self):
        """Update email."""
        if not self.args:
            current_email = self.caller.db.email or "(not set)"
            self.caller.msg(f"|y[INFO]|n Current email: {current_email}")
            return
        
        email = self.args.strip()
        # Basic email validation
        if "@" not in email or "." not in email:
            self.caller.msg("|r[ERROR]|n Invalid email format.")
            return
        
        self.caller.db.email = email
        self.caller.msg(f"|g[SUCCESS]|n Email updated to {email}")


class CmdChangePassword(CharacterMenuCommand):
    """
    Change your account password.
    
    Usage:
        password <old_password> <new_password>
    
    or from the menu:
        7
    """
    
    key = "password"
    aliases = ["7"]
    
    def func(self):
        """Change password."""
        if not self.args or len(self.args.split()) < 2:
            self.caller.msg("|r[ERROR]|n Usage: password <old_password> <new_password>")
            return
        
        old_pwd, new_pwd = self.args.split(None, 1)
        account = self.caller
        
        if not account.check_password(old_pwd):
            account.msg("|r[ERROR]|n Current password incorrect.")
            return
        
        if len(new_pwd) < 6:
            account.msg("|r[ERROR]|n New password must be at least 6 characters.")
            return
        
        account.set_password(new_pwd)
        account.save()
        account.msg("|g[SUCCESS]|n Password changed!")


class CmdOOCMail(CharacterMenuCommand):
    """
    Check your OOC Mail.
    
    Usage:
        mail
    
    or from the menu:
        9
    """
    
    key = "mail"
    aliases = ["9", "oocmail"]
    
    def func(self):
        """Check mail."""
        account = self.caller
        account.msg("|y[INFO]|n OOC Mail system not yet implemented.")


class CmdLogout(CharacterMenuCommand):
    """
    Log out from your account.
    
    Usage:
        logout
    
    or from the menu:
        11
    """
    
    key = "logout"
    aliases = ["11", "quit"]
    
    def func(self):
        """Log out."""
        account = self.caller
        account.msg("|y[INFO]|n Goodbye!")
        # Evennia will handle disconnection
