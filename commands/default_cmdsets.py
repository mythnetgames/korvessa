"""
Command sets

All commands in the game must be grouped in a cmdset.  A given command
can be part of any number of cmdsets and cmdsets can be added/removed
and merged onto entities at runtime.

To create new commands to populate the cmdset, see
`commands/command.py`.

This module wraps the default command sets of Evennia; overloads them
to add/remove commands from the default lineup. You can create your
own cmdsets by inheriting from them or directly from `evennia.CmdSet`.

"""

from evennia import default_cmds
## from commands.unlogged_commands import CmdAccountCreate, CmdAccountLogin
## from commands.character_menu import (
##     CmdLoginCharacter,
##     CmdSubmitApplication,
##     CmdDeleteApplication,
##     CmdRetireCharacter,
##     CmdViewCharacters,
##     CmdUpdateEmail,
##     CmdChangePassword,
##     CmdOOCMail,
##     CmdLogout,
## )


class CharacterCmdSet(default_cmds.CharacterCmdSet):
    """
    The `CharacterCmdSet` contains general in-game commands like `look`,
    `get`, etc available on in-game Character objects. It is merged with
    the `AccountCmdSet` when an Account puppets a Character.
    """

    key = "DefaultCharacter"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #


class AccountCmdSet(default_cmds.AccountCmdSet):
    """
    This is the cmdset available to the Account at all times. It is
    combined with the `CharacterCmdSet` when the Account puppets a
    Character. It holds game-account-specific commands, channel
    commands, etc.
    """

    key = "DefaultAccount"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        # Add character menu commands
        # self.add(CmdLoginCharacter())
        # self.add(CmdSubmitApplication())
        # self.add(CmdDeleteApplication())
        # self.add(CmdRetireCharacter())
        # self.add(CmdViewCharacters())
        # self.add(CmdUpdateEmail())
        # self.add(CmdChangePassword())
        # self.add(CmdOOCMail())
        # self.add(CmdLogout())


class UnloggedinCmdSet(default_cmds.UnloggedinCmdSet):
    """
    Command set available to the Session before being logged in.  This
    holds commands like creating a new account, logging in, etc.
    """

    key = "DefaultUnloggedin"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        # Remove default create/connect commands to avoid conflicts
        self.remove("create")
        self.remove("connect")
        # Add custom Korvessa login commands and quick aliases
        from commands.unlogged_commands import CmdAccountCreate, CmdAccountLogin, CmdQuickCreate, CmdQuickLogin, CmdQuickDisconnect
        self.add(CmdAccountCreate())
        self.add(CmdAccountLogin())
        self.add(CmdQuickCreate())
        self.add(CmdQuickLogin())
        self.add(CmdQuickDisconnect())

    def at_cmdset_add(self, session):
        """
        Called when this cmdset is added to a session. Display splash screen.
        """
        try:
            from server.conf.connection_screens import CONNECTION_SCREEN
            session.msg(CONNECTION_SCREEN)
        except Exception:
            session.msg("|wWelcome to the game!|n\n(Type |ghelp|n for help.)")


class SessionCmdSet(default_cmds.SessionCmdSet):
    """
    This cmdset is made available on Session level once logged in. It
    is empty by default.
    """

    key = "DefaultSession"

    def at_cmdset_creation(self):
        """
        This is the only method defined in a cmdset, called during
        its creation. It should populate the set with command instances.

        As and example we just add the empty base `Command` object.
        It prints some info.
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #
