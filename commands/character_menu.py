
from evennia.commands.command import Command as BaseCommand

"""
Character menu commands for post-login character selection and management.
"""





class CharacterMenuCommand(BaseCommand):
    """Base command for character menu."""
    key = "char_menu_base"
    locks = "cmd:all()"
    help_category = "Character"

# ...existing code...

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
        objs = ObjectDB.objects.filter(db_key=name)
        acc = self.caller.account if hasattr(self.caller, 'account') else self.caller
        char_exists = any(getattr(obj.db, 'account', None) == acc for obj in objs)
        if char_exists:
            self.caller.msg("|r[ERROR]|n You already have a character with that name.")
            return
        # Create the character
        account = self.caller.account if hasattr(self.caller, 'account') else self.caller
        if hasattr(account, 'dbobj'):
            account = account.dbobj
        char = Character.objects.create(db_key=name, db_account=account)
        char.db.desc = desc
        char.db.is_player = True
        char.db_account = account
        # Set locks so only the creating account can puppet
        char.locks.add(f"puppet:id({account.id})")
        char.at_object_creation()
        char.save()
        # Link character to account using Evennia's handler
        if hasattr(account, "characters"):
            account.characters.add(char)
        # Add character key to account's created_chars list
        created_chars = account.db.created_chars or []
        if char.key not in created_chars:
            created_chars.append(char.key)
            account.db.created_chars = created_chars
            account.save()
        debug_info = (
            f"[DEBUG] key={char.key}, db_account={char.db_account}, "
            f"db_is_player={getattr(char, 'db_is_player', None)}, "
            f"created_chars={account.db.created_chars}"
        )

        self.caller.msg(f"|g[SUCCESS]|n Character '{name}' created. (is_player={getattr(char, 'db_is_player', None)})\n{debug_info}")
            # Automatically select the new character for chargen
            if hasattr(account, 'current_character'):
                account.current_character = char
            else:
                setattr(account, 'current_character', char)

        # Launch EvMenu-based chargen for the new character
        from evennia.utils.evmenu import EvMenu
        EvMenu(self.caller, "commands.chargen", startnode="node_intro", persistent=True, cmd_on_exit=None, auto_quit=True, startnode_input=char)







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
            # Allow Builder+ to bypass chargen/approval
            if not account.locks.check_lockstring(account, "perm(Builder)"):
                if hasattr(character, "is_chargen_complete") and not character.is_chargen_complete():
                    account.msg("|r[ERROR]|n Your character creation is not complete. Please finish all stages before entering the game. Use the chargen command to continue character creation.")
                    # Show main menu options
                    menu = (
                        "\n|wWhat would you like to do next?\n"
                        "|c1.|n Login a character.\n"
                        "|c2.|n Submit a character application. |y(Approval required)|n\n"
                        "|c3.|n Delete a pending application.\n"
                        "|c4.|n Retire your current character.\n"
                        "|c5.|n View your characters.\n"
                        "|c6.|n Update your e-mail address.\n"
                        "|c7.|n Change your account password.\n"
                        "|c8.|n OOC Mail\n"
                        "\n|c11.|n Log Out.\n"
                        "\n|wYour Selection:|n "
                    )
                    account.msg(menu)
                    return
                if hasattr(character, "is_approved") and not character.is_approved():
                    account.msg("|r[ERROR]|n Your character has not been approved by staff yet.")
                    return
            # Ensure character has a valid location
            if not character.location:
                # Try to move to a default room (id=1), or fallback to first available room
                from typeclasses.rooms import Room
                try:
                    default_room = Room.objects.get(id=1)
                except Exception:
                    default_room = Room.objects.first()
                if default_room:
                    character.location = default_room
                    character.save()
            # Only puppet if chargen is complete or Builder+
            if account.locks.check_lockstring(account, "perm(Builder)") or (hasattr(character, "is_chargen_complete") and character.is_chargen_complete()):
                account.msg(f"|g[SUCCESS]|n Entering the world as {char_name}...")
                # Puppeting is handled by Evennia
            # Otherwise, block puppet (already handled above)
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
        """Submit character application for approval."""
        account = self.caller.account if hasattr(self.caller, 'account') else self.caller
        if hasattr(account, 'dbobj'):
            account = account.dbobj
        # Find the most recently created character for this account that is not yet approved
        from evennia.objects.models import ObjectDB
        chars = ObjectDB.objects.filter(db_account=account).order_by('-db_date_created')
        chars = [c for c in chars if getattr(c.db, 'is_player', False)]
        # Find the most recent character that is not approved and not already pending
        char = None
        for c in chars:
            if not getattr(c, 'is_approved', lambda: False)():
                char = c
                break
        if not char:
            account.msg("|r[ERROR]|n You have no characters to submit an application for. Use |wcreatechar <name> [=description]|n to create one.")
            # Show main menu options
            menu = (
                "\n|wWhat would you like to do next?\n"
                "|c1.|n Login a character.\n"
                "|c2.|n Submit a character application. |y(Approval required)|n\n"
                "|c3.|n Delete a pending application.\n"
                "|c4.|n Retire your current character.\n"
                "|c5.|n View your characters.\n"
                "|c6.|n Update your e-mail address.\n"
                "|c7.|n Change your account password.\n"
                "|c8.|n OOC Mail\n"
                "\n|c11.|n Log Out.\n"
                "\n|wYour Selection:|n "
            )
            account.msg(menu)
            return
        if not hasattr(char, 'is_chargen_complete') or not char.is_chargen_complete():
            account.msg("|r[ERROR]|n You must complete character creation before submitting an application.")
            return
        if hasattr(char, 'is_approved') and char.is_approved():
            account.msg("|y[INFO]|n This character is already approved.")
            return
        # Allow re-applying: mark as pending, and launch chargen for editing
        char.db.application_status = 'pending'
        account.msg(f"|g[SUCCESS]|n Application for character '{char.key}' is now pending staff review. You may edit your application by running |cchargen|n again.")
        # (Optional) Notify staff here
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
        """Delete a pending character application."""
        account = self.caller
        from evennia.objects.models import ObjectDB
        chars = ObjectDB.objects.filter(db_account=account).order_by('-db_date_created')
        char = next((c for c in chars if getattr(c.db, 'is_player', False) and getattr(c.db, 'application_status', None) == 'pending'), None)
        if not char:
            account.msg("|r[ERROR]|n You have no pending character application to delete.")
            return
        del char.db.application_status
        account.msg(f"|g[SUCCESS]|n Application for character '{char.key}' has been deleted.")


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
        from evennia.objects.models import ObjectDB
        account = self.caller
        characters = ObjectDB.objects.filter(db_account=account)
        characters = [c for c in characters if getattr(c.db, 'is_player', False)]
        
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


