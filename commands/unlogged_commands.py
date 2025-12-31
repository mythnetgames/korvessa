    menu_text = """


class CmdAccountCreate(UnloggedCommand):
    menu_text = """
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
    account.msg(menu_text)
            
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
