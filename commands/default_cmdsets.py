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
from commands.CmdInventory import CmdGet, CmdInventory as CmdInv, CmdGive, CmdDrop
from commands import CmdAdmin
from commands.admin_door_cleanup import CmdCleanupDoors
from commands import CmdClothing
from commands.CmdClothing import CmdWear, CmdRemove, CmdFreeHands
from commands.CmdFightingStyle import CmdFightingStyle
from commands import CmdMedical
from commands.CmdMedical import CmdMedicalInfo
from commands import CmdConsumption
from commands import CmdMedicalItems
from commands.CmdSpawnMob import CmdSpawnMob
from commands.CmdBug import CmdBug
from commands.CmdAdmin import CmdHeal, CmdPeace, CmdTestDeathCurtain, CmdWeather, CmdResetMedical, CmdMedicalAudit, CmdTestDeath, CmdTestUnconscious, CmdSpawnAmmo
from commands.CmdRevive import CmdRevive
from commands.CmdFixCharacterOwnership import CmdFixCharacterOwnership
from commands.fix_baseline_stats import CmdFixBaselineStats
from commands.combat.cmdset_combat import CombatCmdSet
from commands.combat.special_actions import CmdAim, CmdGrapple, CmdReload, CmdAmmo, CmdChoke
from commands.CmdThrow import (
    CmdThrow, CmdPull, CmdCatch, CmdRig, CmdDefuse,
    CmdScan, CmdDetonate, CmdDetonateList, CmdClearDetonator
)
from commands.CmdGraffiti import CmdGraffiti, CmdPress
from commands.CmdCharacter import CmdLongdesc, CmdSkintone
from commands.CmdEyeColor import CmdEyeColor
from commands.CmdDisguise import CmdDisguise, CmdAdjust, CmdScrutinize, CmdPullUp, CmdPullDown, CmdExpose
from commands.CmdArmor import CmdArmor, CmdArmorRepair, CmdSlot, CmdUnslot
from commands.CmdStatAdjust import CmdStatAdjust
from commands.nakeds import CmdNakeds
from commands.wield import CmdWield
from commands.who import CmdWho, CmdInvisible, CmdWhoLocation
from commands.place import CmdLookPlace, CmdTempPlace, CmdTPEmote
from commands.voice import CmdVoice
from commands.petition import CmdPetition, CmdErasePetition, CmdStaffPetition
from commands.pnote import CmdPnotes, CmdPnote, CmdPread, CmdPnoteDelete, CmdPlist
from commands.notes import CmdAddNote, CmdNotes, CmdPagedNotes, CmdReadNote, CmdViewAllNotes, CmdReadStaffNote, CmdNextNote
from commands.npc_admin import CmdCreateNPC, CmdNPCPuppet, CmdNPCUnpuppet, CmdNPCReaction, CmdNPCConfig, CmdNPCStat, CmdNPCSkill, CmdNPCChrome, CmdNPCNakeds, CmdNPCGender, CmdForceWander, CmdForcePath
from commands.look import CmdLook
from commands.shop import CmdBuy
from commands.window import CmdAttachWindow, CmdRemoveWindow, CmdWindowCoord, CmdDebugWindows
from commands.debugroomcoords import CmdDebugRoomCoords
from commands.debugsensors import CmdDebugSensors
from commands.mapper import CmdMapColor
from commands.adminkill import CmdAdminKill
from commands.CmdTogglePickup import CmdTogglePickup
from commands.stamina_admin import CmdStaminaStart, CmdStaminaStatus
from commands.CmdFollow import CmdFollow, CmdUnfollow, CmdLose
from commands.CmdSetRoomType import CmdSetRoomType
from commands.CmdWeather import CmdWeatherRoom
from commands.CmdRepairPulseWatch import CmdRepairPulseWatch
from commands.inspect import CmdInspect
from commands.cube_housing import CubeHousingCmdSet
from commands.economy import EconomyCmdSet


class UnconsciousCmdSet(CmdSet):
    """
    Command set for unconscious characters.
    Only allows minimal OOC commands - no perception, movement, or actions.
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
        from commands.time import CmdTime
        self.add(CmdTime())      # In-game time from clock display
        
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
        # Remove default look and add custom one with petition support
        self.remove("look")
        self.add(CmdLook())
        # Remove default get and add custom one with no_pick support
        self.remove("get")
        self.add(CmdGet())
        # Remove default inventory and add custom categorized one
        self.remove("inventory")
        self.add(CmdInv())
        # Remove default give/drop and add custom ones that block worn items
        self.remove("give")
        self.add(CmdGive())
        self.remove("drop")
        self.add(CmdDrop())
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
            CmdMapOn, CmdMapOff, CmdMapRoom, CmdMapColor, CmdMapIcon, CmdAreaIcon, CmdZoneIcon, CmdMapIconHelp, CmdMap
        )
        self.add(CmdMapOn())
        self.add(CmdMapOff())
        self.add(CmdMapRoom())
        self.add(CmdMapColor())
        self.add(CmdMapIcon())
        self.add(CmdAreaIcon())
        self.add(CmdZoneIcon())
        self.add(CmdMapIconHelp())
        self.add(CmdMap())
        # Add stats command
        from commands.CmdStats import CmdStats
        self.add(CmdStats())
        # Add character appearance commands (longdesc, skintone, eyecolor, nakeds)
        self.add(CmdLongdesc())
        self.add(CmdSkintone())
        self.add(CmdEyeColor())
        # Add disguise and anonymity commands
        self.add(CmdDisguise())
        self.add(CmdAdjust())
        self.add(CmdScrutinize())
        self.add(CmdPullUp())
        self.add(CmdPullDown())
        self.add(CmdExpose())
        # Add stat adjust command (admin)
        self.add(CmdStatAdjust())
        # Add setstat command (builder and up)
        from commands.CmdSetStat import CmdSetStat
        self.add(CmdSetStat())
        # Add fighting style command (character customization)
        self.add(CmdFightingStyle())
        # Add fix baseline stats command (admin)
        self.add(CmdFixBaselineStats())
        # Add spawnchrome command (builder and up)
        from commands.CmdSpawnChrome import CmdSpawnChrome
        self.add(CmdSpawnChrome())
        # Add chromelist command (info command for listing all chrome)
        from commands.CmdChromeList import CmdChromeList
        self.add(CmdChromeList())
        # Add spawnset command for armor sets (builder and up)
        from commands.CmdSpawnSet import CmdSpawnSet
        self.add(CmdSpawnSet())
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
        # Add medical commands
        self.add(CmdResetMedical())
        self.add(CmdMedicalAudit())
        self.add(CmdMedicalInfo())
        # Add revive command (admin)
        self.add(CmdRevive())
        # Add spawn commands (admin)
        self.add(CmdSpawnAmmo())
        # Add combat commands
        self.add(CombatCmdSet())
        # Add ammo management commands (available outside combat too)
        self.add(CmdReload())
        self.add(CmdAmmo())
        # Add combat commands available outside combat
        self.add(CmdAim())      # Can aim at targets or directions outside combat
        self.add(CmdGrapple())  # Can initiate grapple outside combat
        self.add(CmdChoke())    # Can choke when grappling
        # Add wield command
        self.add(CmdWield())
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
        # Add language commands
        from commands.speak import CmdSpeak, CmdLearn
        self.add(CmdSpeak())
        self.add(CmdLearn())
        # Add petition commands
        self.add(CmdPetition())
        self.add(CmdErasePetition())
        self.add(CmdStaffPetition())
        # Add pnote commands
        self.add(CmdPnotes())
        self.add(CmdPnote())
        self.add(CmdPread())
        self.add(CmdPnoteDelete())
        self.add(CmdPlist())
        # Add note commands
        self.add(CmdAddNote())
        self.add(CmdNotes())
        self.add(CmdPagedNotes())
        self.add(CmdReadNote())
        self.add(CmdViewAllNotes())
        self.add(CmdReadStaffNote())
        self.add(CmdNextNote())
        # Add NPC commands
        self.add(CmdCreateNPC())
        self.add(CmdNPCPuppet())
        self.add(CmdNPCUnpuppet())
        self.add(CmdNPCReaction())
        self.add(CmdNPCConfig())
        self.add(CmdNPCStat())
        self.add(CmdNPCSkill())
        self.add(CmdNPCChrome())
        self.add(CmdNPCNakeds())
        self.add(CmdNPCGender())
        self.add(CmdForceWander())
        self.add(CmdForcePath())
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
        # Add cleanup doors command
        self.add(CmdCleanupDoors())
        # Add deletezone command
        from commands.deletezone import CmdDeleteZone
        self.add(CmdDeleteZone())
        # Add zone-aware dig command
        from commands.zonedig import CmdZoneDig
        self.add(CmdZoneDig())
        # Add connect command (dig tool to connect rooms by coordinates)
        from commands.connect import CmdConnect
        self.add(CmdConnect())
        # Add control command
        from commands.control import CmdControl
        self.add(CmdControl())
        # Add room type/tag command
        self.add(CmdSetRoomType())
        # Add weather room toggle command
        self.add(CmdWeatherRoom())
        # Add tailoring commands
        from commands.CmdTailoring import (
            CmdSpawnMaterial, CmdTailorName, CmdTailorCoverage, CmdTailorColor,
            CmdTailorSeeThru, CmdTailorDescribe, CmdTailorMessages, 
            CmdTailorCheck, CmdTailorFinalize
        )
        self.add(CmdSpawnMaterial())
        self.add(CmdTailorName())
        self.add(CmdTailorCoverage())
        self.add(CmdTailorColor())
        self.add(CmdTailorSeeThru())
        self.add(CmdTailorDescribe())
        self.add(CmdTailorMessages())
        self.add(CmdTailorCheck())
        self.add(CmdTailorFinalize())
        # Add clothing commands (wear/remove)
        self.add(CmdWear())
        self.add(CmdRemove())
        self.add(CmdFreeHands())
        # Add clone/backup commands
        from typeclasses.cloning_pod import CmdCloneStatus, CmdSpawnPod, CmdSitInPod, CmdLeavePod, CmdResetPod
        self.add(CmdCloneStatus())
        self.add(CmdSpawnPod())
        self.add(CmdResetPod())
        self.add(CmdSitInPod())
        self.add(CmdLeavePod())
        # Add IP (Investment Points) commands
        from commands.CmdIP import CmdIP, CmdSetSkill, CmdInvest
        self.add(CmdIP())        # Admin: grant/subtract IP
        self.add(CmdSetSkill())  # Admin: directly set skills
        self.add(CmdInvest())    # Player: invest IP into skills
        # Add background command
        from commands.CmdBackground import CmdBackground
        self.add(CmdBackground())
        # Add cooking system commands
        from commands.CmdCooking import (
            CmdDesignRecipe, CmdCook, CmdEat, CmdDrink, CmdTaste, CmdSmellFood,
            CmdSpawnKitchenette, CmdSpawnIngredients, CmdRecipes, 
            CmdApproveRecipe, CmdRejectRecipe, CmdAdminDesignRecipe, CmdEditRecipe, CmdSetNutritious
        )
        self.add(CmdDesignRecipe())      # Player: design new recipes
        self.add(CmdEditRecipe())        # Player: edit existing recipes
        self.add(CmdCook())              # Player: cook at kitchenettes
        self.add(CmdEat())               # Player: eat food
        self.add(CmdDrink())             # Player: drink beverages
        self.add(CmdTaste())             # Player: taste food/drink
        self.add(CmdSmellFood())         # Player: smell food/drink
        self.add(CmdSpawnKitchenette())  # Admin: create kitchenettes
        self.add(CmdSpawnIngredients())  # Admin: create ingredients
        self.add(CmdRecipes())           # Admin: manage recipe queue
        self.add(CmdApproveRecipe())     # Admin: approve recipes
        self.add(CmdRejectRecipe())      # Admin: reject recipes
        self.add(CmdSetNutritious())     # Admin: set nutritious flag
        self.add(CmdAdminDesignRecipe()) # Admin: design auto-approved recipes
        from commands.CmdDeleteRecipe import CmdDeleteRecipe
        self.add(CmdDeleteRecipe())      # Admin: delete approved recipes
        # Add pickup toggle command
        self.add(CmdTogglePickup())      # Admin: toggle if objects can be picked up
        # Add test dummy commands
        from commands.CmdTestDummy import CmdSpawnDummy, CmdDummyStats, CmdDummyHeal, CmdDummyInfo
        self.add(CmdSpawnDummy())        # Admin: spawn test dummy
        self.add(CmdDummyStats())        # Admin: adjust dummy stats
        self.add(CmdDummyHeal())         # Admin: force heal dummy
        self.add(CmdDummyInfo())         # Admin: view dummy info
        # Add follow commands
        self.add(CmdFollow())            # Player: follow another character
        self.add(CmdUnfollow())          # Player: stop following
        self.add(CmdLose())              # Player: shake off followers
        # Add pulse watch repair command
        self.add(CmdRepairPulseWatch())  # Player: repair severed pulse watch with Electronics skill
        # Add movement speed commands (stroll, walk, jog, run, sprint, pace)
        from commands.movement import MovementCmdSet
        self.add(MovementCmdSet())
        # Add pathing/auto-walk commands
        from commands.pathing import CmdPath
        self.add(CmdPath())              # Player: auto-walk to saved locations
        # Add stamina system admin commands
        self.add(CmdStaminaStart())      # Admin: start stamina ticker
        self.add(CmdStaminaStatus())     # Admin: check stamina system status
        # Add cube housing commands
        self.add(CubeHousingCmdSet())    # Housing: enter, close door, pay rent, createcube, etc.
        # Add pad housing commands (replaces cube commands for unified housing)
        from commands.pad_housing import PadHousingCmdSet
        self.add(PadHousingCmdSet())     # Housing: enter, check, close door, pay rent, createpad, setrent, etc.
        # Add economy commands
        self.add(EconomyCmdSet())        # Economy: count, dropmoney, payday, spawncash, etc.
        # Add furniture interaction commands
        from commands.furniture import FurnitureCmdSet
        self.add(FurnitureCmdSet())      # Furniture: sit, lie, stand
        # Add admin design menus for NPCs, furniture, weapons, armor/clothes
        from commands.admin_design_menus import (
            CmdNPCDesignMenu, CmdFurnitureDesignMenu, CmdWeaponDesignMenu, CmdArmorDesignMenu, CmdSpawnNPCDesign, CmdSpawnClothingDesign
        )
        self.add(CmdNPCDesignMenu())      # Builder+: NPC designer (npcdesign)
        self.add(CmdFurnitureDesignMenu())  # Builder+: Furniture designer (furnituredesign)
        self.add(CmdWeaponDesignMenu())     # Builder+: Weapon designer (weapondesign)
        self.add(CmdArmorDesignMenu())      # Builder+: Armor/Clothes designer (armordesign, clothesdesign)
        self.add(CmdSpawnNPCDesign())       # Builder+: spawn NPC from design (spawnnpc)
        self.add(CmdSpawnClothingDesign())  # Builder+: spawn clothing/armor from design
        # Add new builder item creation system
        from commands.builder_designs import (
            CmdDesignFurniture, CmdDesignNPC, CmdDesignWeapon, CmdDesignClothing,
            CmdListDesigns, CmdManageFactions
        )
        self.add(CmdDesignFurniture())    # Builder+: furniture design menu
        self.add(CmdDesignNPC())          # Builder+: NPC design menu
        self.add(CmdDesignWeapon())       # Builder+: weapon design menu
        self.add(CmdDesignClothing())     # Builder+: clothing/armor design menu
        self.add(CmdListDesigns())        # Builder+: list all designs
        self.add(CmdManageFactions())     # Builder+: manage factions
        # Add new builder spawn commands
        from commands.builder_spawners import (
            CmdSpawnFurniture, CmdSpawnNPC, CmdSpawnWeapon, CmdSpawnClothing, CmdSpawnArmor, CmdFixWeaponNames, CmdSpawnProxyModule
        )
        self.add(CmdSpawnFurniture())     # Builder+: spawn furniture
        self.add(CmdSpawnNPC())           # Builder+: spawn NPCs
        self.add(CmdSpawnWeapon())        # Builder+: spawn weapons
        self.add(CmdSpawnClothing())      # Builder+: spawn clothing
        self.add(CmdSpawnArmor())         # Builder+: spawn armor
        self.add(CmdSpawnProxyModule())   # Builder+: spawn proxy modules
        self.add(CmdFixWeaponNames())     # Builder+: fix weapon names
        # Add NPC wandering management command (admin+)
        from commands.cmd_npc_wander import CmdNPCWander
        self.add(CmdNPCWander())          # Admin+: manage NPC wandering in zones
        # Add corpse cleanup command (builder+)
        from commands.corpsecleanup import CmdCorpseCleanup
        self.add(CmdCorpseCleanup())      # Builder+: clean up dead NPCs
        # Add diagnostic loop detection command (admin+)
        from commands.diagnose_loop import CmdDiagnoseLoop
        self.add(CmdDiagnoseLoop())       # Admin+: diagnose infinite loops/runaway scripts
        # Add SafetyNet intranet social system commands
        from commands.CmdSafetyNet import CmdSafetyNet, CmdSafetyNetAdmin
        self.add(CmdSafetyNet())          # Player: SafetyNet social system
        self.add(CmdSafetyNetAdmin())     # Builder+: SafetyNet admin commands
        # Add Okama Gamebud communication system commands
        from commands.CmdGamebud import CmdGamebud
        self.add(CmdGamebud())            # Player: Gamebud peer-to-peer messaging
        # Add slotting system commands
        from commands.slotting import CmdSlot, CmdUnslot
        self.add(CmdSlot())               # Player: slot items into devices
        self.add(CmdUnslot())             # Player: unslot items from devices
        # Add SafetyNet device spawning commands
        from commands.CmdSpawnSafetyNet import (
            CmdSpawnSafetyNetDevice, CmdSpawnWristpad, CmdSpawnComputer, CmdSpawnPortableComputer
        )
        self.add(CmdSpawnSafetyNetDevice())  # Builder+: spawn SafetyNet devices (@spawnsn)
        self.add(CmdSpawnWristpad())        # Builder+: quick spawn wristpad (@wristpad)
        self.add(CmdSpawnComputer())        # Builder+: quick spawn computer (@computer)
        self.add(CmdSpawnPortableComputer())  # Builder+: quick spawn portable computer (@portablecomp)
        # Add inspect command (builder-friendly @examine alternative)
        self.add(CmdInspect())              # Builder+: inspect objects/rooms/characters

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

