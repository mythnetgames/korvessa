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


from evennia import default_cmds, CmdSet
from commands import CmdCharacter
from commands import CmdInventory
from commands import CmdAdmin
from commands import CmdClothing
from commands import CmdMedical
from commands import CmdConsumption
from commands import CmdMedicalItems
from commands.CmdSpawnMob import CmdSpawnMob
from commands.CmdBug import CmdBug
from commands.CmdAdmin import CmdHeal, CmdPeace, CmdTestDeathCurtain, CmdWeather, CmdResetMedical, CmdMedicalAudit, CmdTestDeath, CmdTestUnconscious
from commands.CmdFixCharacterOwnership import CmdFixCharacterOwnership
from commands.combat.cmdset_combat import CombatCmdSet
from commands.combat.special_actions import CmdAim, CmdGrapple
from commands.CmdThrow import (
    CmdThrow, CmdPull, CmdCatch, CmdRig, CmdDefuse,
    CmdScan, CmdDetonate, CmdDetonateList, CmdClearDetonator
)
from commands.CmdGraffiti import CmdGraffiti, CmdPress
from commands.CmdCharacter import CmdLongdesc, CmdSkintone
from commands.CmdArmor import CmdArmor, CmdArmorRepair, CmdSlot, CmdUnslot
from commands.nakeds import CmdNakeds
from commands.who import CmdWho, CmdInvisible, CmdWhoLocation
from commands.place import CmdLookPlace, CmdTempPlace, CmdTPEmote
from commands.voice import CmdVoice
from commands.shop import CmdBuy
from commands.window import CmdAttachWindow, CmdRemoveWindow, CmdWindowCoord, CmdDebugWindows
from commands.debugroomcoords import CmdDebugRoomCoords
from commands.debugsensors import CmdDebugSensors
from commands.mapper import CmdMapColor


class UnconsciousCmdSet(CmdSet):
    """
    Command set for unconscious characters.
    Only allows minimal OOC commands - no perception, movement, or actions.
from commands.debugsensors import CmdDebugSensors
    """
    key = "unconscious_cmdset"
    priority = 0  # Same as normal CharacterCmdSet since this replaces it entirely
    no_exits = True  # Prevent exit traversal when unconscious
    
    def at_cmdset_creation(self):
        """
        Add only commands that unconscious characters should be able to use.
        Unconscious = no perception, no movement, no actions.
        """
        # Essential OOC commands only
        self.add(default_cmds.CmdHelp())      # Always allow help
        self.add(default_cmds.CmdWho())       # OOC player information
        self.add(default_cmds.CmdTime())      # OOC time information
        
        # System commands
        self.add(default_cmds.CmdQuit())      # Can always quit
        
        # Staff commands (will be filtered by permissions anyway)
        self.add(default_cmds.CmdPy())        # Staff debugging
        self.add(default_cmds.CmdReload())    # Staff server management
        
        # NO look, NO movement, NO actions when unconscious


class DeathCmdSet(CmdSet):
    """
    Command set for dead characters.
    Only allows minimal OOC commands - no perception, no movement, no actions.
    """
    key = "death_cmdset"
    priority = 0  # Same as normal CharacterCmdSet since this replaces it entirely
    no_exits = True  # Prevent exit traversal when dead
    
    def at_cmdset_creation(self):
        """
        Add only commands that dead characters should be able to use.
        Dead = no perception, no movement, no actions, minimal OOC only.
        """
        # Very minimal set - OOC information only
        self.add(default_cmds.CmdHelp())      # Always allow help
        self.add(default_cmds.CmdWho())       # OOC player information
        self.add(default_cmds.CmdQuit())      # Can always quit
        
        # Staff commands (will be filtered by permissions anyway)
        self.add(default_cmds.CmdPy())        # Staff debugging
        self.add(default_cmds.CmdReload())    # Staff server management
        
        # NO look, NO time, NO movement, NO actions when dead


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
        # Remove default WHO and add custom one
        self.remove("who")
        self.add(CmdWho())
        self.add(CmdInvisible())
        self.add(CmdWhoLocation())
        # Remove default say and add custom one with voice support
        self.remove("say")
        from commands.say import CmdSay
        self.add(CmdSay())
        # Remove default emote and add custom one with voice support
        self.remove("emote")
        from commands.emote import CmdEmote
        self.add(CmdEmote())
        # Add individual attach/remove/program/show commands for doors/locks/keypads
        from commands.door import (
            CmdAttachDoor, CmdAttachLock, CmdAttachKeypad, CmdRemoveDoor, CmdRemoveLock, CmdRemoveKeypad,
            CmdProgramKeypad, CmdShowCombo, CmdSetDoorDesc, CmdSetDoorShortDesc
        )
        self.add(CmdAttachDoor())
        self.add(CmdAttachLock())
        self.add(CmdAttachKeypad())
        self.add(CmdRemoveDoor())
        self.add(CmdRemoveLock())
        self.add(CmdRemoveKeypad())
        self.add(CmdProgramKeypad())
        self.add(CmdShowCombo())
        self.add(CmdSetDoorDesc())
        self.add(CmdSetDoorShortDesc())
        # Add fix room typeclass admin command
        from commands.CmdFixRoomTypeclass import CmdFixRoomTypeclass
        self.add(CmdFixRoomTypeclass())
        # Add wipe coords admin command
        from commands.CmdWipeCoords import CmdWipeCoords
        self.add(CmdWipeCoords())
        # Add mapping commands
        from commands.mapper import (
            CmdMapOn, CmdMapOff, CmdMapRoom, CmdMapColor, CmdMapIcon, CmdAreaIcon, CmdMapIconHelp, CmdMap
        )
        self.add(CmdMapOn())
        self.add(CmdMapOff())
        self.add(CmdMapRoom())
        self.add(CmdMapColor())
        self.add(CmdMapIcon())
        self.add(CmdAreaIcon())
        self.add(CmdMapIconHelp())
        self.add(CmdMap())
        # Add stats command
        from commands.CmdStats import CmdStats
        self.add(CmdStats())
        # Add setstat command (builder and up)
        from commands.CmdSetStat import CmdSetStat
        self.add(CmdSetStat())
        # Add spawnchrome command (builder and up)
        from commands.CmdSpawnChrome import CmdSpawnChrome
        self.add(CmdSpawnChrome())
        # Add chrome install/uninstall commands (builder and up)
        from commands.CmdChromeInstall import CmdChromeInstall, CmdChromeUninstall
        self.add(CmdChromeInstall())
        self.add(CmdChromeUninstall())
        # Add think command
        from commands.CmdThink import CmdThink
        self.add(CmdThink())
        # Add door/lock/keypad commands
        from commands.door import (
            CmdOpenDoor, CmdCloseDoor, CmdLockDoor, CmdUnlockDoor, CmdDoorStatus, CmdSetDoorMsg,
            CmdBulkAttach, CmdBulkRemove, CmdPushCombo, CmdUnlockExit, CmdLockExit, CmdPressLock
        )
        self.add(CmdOpenDoor())
        self.add(CmdCloseDoor())
        self.add(CmdLockDoor())
        self.add(CmdUnlockDoor())
        self.add(CmdDoorStatus())
        self.add(CmdSetDoorMsg())
        self.add(CmdBulkAttach())
        self.add(CmdBulkRemove())
        self.add(CmdPushCombo())
        self.add(CmdUnlockExit())
        self.add(CmdLockExit())
        self.add(CmdPressLock())
        # Add mapping help command
        from commands.mapper import CmdHelpMapping
        self.add(CmdHelpMapping())
        self.add(CmdResetMedical())
        self.add(CmdMedicalAudit())
        # Add shop commands
        self.add(CmdBuy())
        # Add window observation commands (builder and up)
        self.add(CmdAttachWindow())
        self.add(CmdRemoveWindow())
        self.add(CmdWindowCoord())
        self.add(CmdDebugWindows())
        # Add relay system builder/admin commands
        from commands.relay_cmdset import BuilderRelayCmdSet
        self.add(BuilderRelayCmdSet())
        # Add nakeds command
        self.add(CmdNakeds())
        # Add look_place and temp_place commands
        self.add(CmdLookPlace())
        self.add(CmdTempPlace())
        self.add(CmdTPEmote())
        # Add voice command
        self.add(CmdVoice())
        # Add createzone command
        from commands.createzone import CmdCreateZone
        self.add(CmdCreateZone())
        # Add setzone command
        from commands.setzone import CmdSetZone
        self.add(CmdSetZone())
        # Add setcoord command
        from commands.setcoord import CmdSetCoord
        self.add(CmdSetCoord())
        # Add autocoord command
        from commands.autocoord import CmdAutoCoord
        self.add(CmdAutoCoord())
        # Add deletezone command
        from commands.deletezone import CmdDeleteZone
        self.add(CmdDeleteZone())
        # Add zone-aware dig command
        from commands.zonedig import CmdZoneDig
        self.add(CmdZoneDig())

class AccountCmdSet(default_cmds.AccountCmdSet):
    """
    This is the cmdset available to the Account at all times. It is
    combined with the `CharacterCmdSet` when the Account puppets a
        self.add(CmdDebugSensors())
    Character. It holds game-account-specific commands, channel
    commands, etc.
    """

    key = "DefaultAccount"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #
        # Add map toggling commands to account cmdset
        from commands.mapper import CmdMapOn, CmdMapOff
        self.add(CmdMapOn())
        self.add(CmdMapOff())


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
        #
        # any commands you add below will overload the default ones.
        #


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
        # Add map toggling commands to session cmdset
        from commands.mapper import CmdMapOn, CmdMapOff
        self.add(CmdMapOn())
        self.add(CmdMapOff())

