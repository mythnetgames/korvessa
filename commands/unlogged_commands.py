from evennia.commands.command import Command as UnloggedCommand
from evennia.utils import utils
# ...existing code...

# Custom Look command for unlogged-in users
class CmdUnloggedinLook(UnloggedCommand):
    """Display the login screen and any relevant info."""
    key = "look"
    aliases = ["l", "+", ":", ";"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        # Display the connection screen (imported from Evennia's connection_screens)
        try:
            from server.conf.connection_screens import CONNECTION_SCREEN
            self.caller.msg(CONNECTION_SCREEN)
        except Exception:
            self.caller.msg("|wWelcome to the game!|n\n(Type |ghelp|n for help.)")
from evennia.accounts.models import AccountDB
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()

class CmdQuickCreate(UnloggedCommand):
    """Quick alias for account creation: C"""
    key = "C"
    aliases = ["c"]
    locks = "cmd:all()"
    help_category = "Account"

    def func(self):
        self.caller.msg("|g[CREATE]|n Enter a username for your new account:")
        self.caller.ndb.create_step = 1
        self.caller.ndb.create_username = None
        self.session.handler = self.create_prompt_handler

    def create_prompt_handler(self, session, text):
        if not hasattr(self.caller, 'ndb'):
            return
        step = getattr(self.caller.ndb, 'create_step', 1)
        if step == 1:
            self.caller.ndb.create_username = text.strip()
            self.caller.ndb.create_step = 2
            self.caller.msg("|g[CREATE]|n Enter a password for your new account:")
        elif step == 2:
            username = self.caller.ndb.create_username
            password = text.strip()
            del self.caller.ndb.create_step
            del self.caller.ndb.create_username
            self.session.handler = None
            self.caller.execute_cmd(f"create {username} {password}")

class CmdQuickLogin(UnloggedCommand):
    """Quick alias for login: L"""
    key = "L"
    aliases = ["l"]
    locks = "cmd:all()"
    help_category = "Account"

    def func(self):
        self.caller.msg("|g[LOGIN]|n Enter your account username:")
        self.caller.ndb.login_step = 1
        self.caller.ndb.login_username = None
        self.session.handler = self.login_prompt_handler

    def login_prompt_handler(self, session, text):
        if not hasattr(self.caller, 'ndb'):
            return
        step = getattr(self.caller.ndb, 'login_step', 1)
        if step == 1:
            self.caller.ndb.login_username = text.strip()
            self.caller.ndb.login_step = 2
            self.caller.msg("|g[LOGIN]|n Enter your account password:")
        elif step == 2:
            username = self.caller.ndb.login_username
            password = text.strip()
            del self.caller.ndb.login_step
            del self.caller.ndb.login_username
            self.session.handler = None
            self.caller.execute_cmd(f"connect {username} {password}")

class CmdQuickDisconnect(UnloggedCommand):
    """Quick alias for disconnect: X"""
    key = "X"
    aliases = ["x"]
    locks = "cmd:all()"
    help_category = "Account"

    def func(self):
        self.caller.msg("|r[INFO]|n Disconnecting from server...")
        self.session.disconnect()

class CmdAccountCreate(UnloggedCommand):
    """
    Create a new account.

    Usage:
        create <username> <password>
    """
    key = "create"
    aliases = []
    locks = "cmd:all()"
    help_category = "Account"

    def func(self):
        if not self.args or len(self.args.split()) < 2:
            self.caller.msg("|r[ERROR]|n Usage: create <username> <password>")
            return
        username, password = self.args.split(None, 1)
        if len(username) < 3:
            self.caller.msg("|r[ERROR]|n Username must be at least 3 characters.")
            return
        if len(password) < 6:
            self.caller.msg("|r[ERROR]|n Password must be at least 6 characters.")
            return
        try:
            user = User.objects.create_user(username, email="", password=password)
            account = AccountDB.objects.create(user=user)
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
        login <username> <password>
    """
    key = "connect"
    aliases = ["login", "l"]
    locks = "cmd:all()"
    help_category = "Account"

    def func(self):
        if not self.args or len(self.args.split()) < 2:
            self.caller.msg("|r[ERROR]|n Usage: connect <username> <password>")
            return
        username, password = self.args.split(None, 1)
        try:
            user = User.objects.get(username=username)
            account = user.account
            if account.check_password(password):
                self.caller.msg(f"|g[SUCCESS]|n Logged in as {username}.")
                account.msg("|#ffff00CHARACTER MENU|n\n")
                self.show_character_menu(account)
            else:
                self.caller.msg("|r[ERROR]|n Invalid password.")
        except User.DoesNotExist:
            self.caller.msg("|r[ERROR]|n Account not found.")
        except Exception as e:
            self.caller.msg(f"|r[ERROR]|n Login failed: {str(e)}")

    def show_character_menu(self, account):
        menu_text = (
            "|#ffff00═══════════════════════════════════════════════════════════════════════════════|n\n"
            "|#ffff00CHARACTER MANAGEMENT|n\n"
            "|#ffff00═══════════════════════════════════════════════════════════════════════════════|n\n\n"
            "  1. Login a character.\n"
            "  2. Submit a character application.\n"
            "                (Approval required)\n"
            "  3. Delete a pending application.\n"
            "  4. Retire your current character.\n"
            "  5. View your characters.\n"
            "  6. Update your e-mail address.\n"
            "  7. Change your account password.\n"
            "  8. Send/Check OOC Mail.\n\n"
            " 11. Log Out.\n\n"
            "|#ffff00Your Selection:|n "
        )
        account.msg(menu_text)
        account.msg(menu_text)
