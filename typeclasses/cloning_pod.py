"""
TerraGroup Cloning Division Pod - Consciousness Backup System

Players can sit in the TerraGroup Cloning Division pod to backup their current state:
- Stats (body, ref, dex, tech, smrt, will, edge, emp)
- Skills
- Nakeds (body descriptions)
- Description

When they die, they respawn in a new sleeve with their LAST BACKED UP state.
Chrome and items are NOT backed up (lost on death).

Pricing:
- New sleeve: Free (will cost money later)
- Update backup: Free (will cost less than new later)
"""

from typeclasses.objects import Object
from evennia.utils import delay
from evennia import Command, CmdSet
from evennia.comms.models import ChannelDB
import time


# ============================================================================
# PRICING CONFIGURATION (adjust these when monetization is added)
# ============================================================================

CLONE_NEW_COST = 0      # Cost for first-time clone backup
CLONE_UPDATE_COST = 0   # Cost for updating existing clone (should be cheaper)


def _log(msg):
    """Log to Splattercast channel."""
    try:
        ch = ChannelDB.objects.get_channel("Splattercast")
        ch.msg(msg)
    except:
        pass


# ============================================================================
# CLONE BACKUP FUNCTIONS
# ============================================================================

def get_clone_cost(character):
    """
    Get the cost for cloning based on whether they already have a backup.
    
    Args:
        character: The character to check
        
    Returns:
        tuple: (cost, is_update) - cost amount and whether this is an update
    """
    has_backup = getattr(character.db, 'clone_backup', None) is not None
    
    if has_backup:
        return (CLONE_UPDATE_COST, True)
    else:
        return (CLONE_NEW_COST, False)


def can_afford_clone(character):
    """
    Check if character can afford to clone/update.
    
    Args:
        character: The character to check
        
    Returns:
        tuple: (can_afford, cost, is_update)
    """
    cost, is_update = get_clone_cost(character)
    
    # For now, everything is free
    if cost == 0:
        return (True, cost, is_update)
    
    # Future: Check character's money
    # current_money = character.db.money or 0
    # return (current_money >= cost, cost, is_update)
    
    return (True, cost, is_update)


def create_clone_backup(character):
    """
    Create or update a clone backup for the character.
    
    Stores: stats, skills, nakeds, description
    Does NOT store: chrome, inventory, current location
    
    Args:
        character: The character to backup
        
    Returns:
        dict: The backup data created
    """
    backup = {
        'timestamp': time.time(),
        
        # Stats (8-stat system)
        'body': getattr(character, 'body', 1),
        'ref': getattr(character, 'ref', 1),
        'dex': getattr(character, 'dex', 1),
        'tech': getattr(character, 'tech', 1),
        'smrt': getattr(character, 'smrt', 1),
        'will': getattr(character, 'will', 1),
        'edge': getattr(character, 'edge', 1),
        'emp': getattr(character, 'emp', 1),
        
        # Skills (copy the whole skills dict if it exists)
        'skills': dict(getattr(character.db, 'skills', {}) or {}),
        
        # Appearance
        'desc': getattr(character.db, 'desc', ''),
        'nakeds': dict(getattr(character.db, 'nakeds', {}) or {}),
        'skintone': getattr(character.db, 'skintone', None),
        'sex': getattr(character, 'sex', 'ambiguous'),
        
        # Character name (base name without Roman numerals)
        'base_name': _get_base_name(character.key),
    }
    
    # Store on character
    character.db.clone_backup = backup
    character.db.clone_backup_count = (character.db.clone_backup_count or 0) + 1
    
    _log(f"CLONE_BACKUP: Created backup for {character.key} (backup #{character.db.clone_backup_count})")
    
    return backup


def _get_base_name(name):
    """Strip Roman numeral suffix from name to get base name."""
    import re
    roman_pattern = r'\s+(M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3}))$'
    return re.sub(roman_pattern, '', name, flags=re.IGNORECASE).strip()


def has_clone_backup(character):
    """Check if character has a clone backup."""
    return getattr(character.db, 'clone_backup', None) is not None


def get_clone_backup(character):
    """Get the clone backup data for a character."""
    return getattr(character.db, 'clone_backup', None)


def restore_from_clone(new_character, backup_data):
    """
    Restore a new character from clone backup data.
    
    Args:
        new_character: The newly created character to restore into
        backup_data: The backup dictionary from the old character
    """
    if not backup_data:
        return False
    
    # Restore stats
    new_character.body = backup_data.get('body', 1)
    new_character.ref = backup_data.get('ref', 1)
    new_character.dex = backup_data.get('dex', 1)
    new_character.tech = backup_data.get('tech', 1)
    new_character.smrt = backup_data.get('smrt', 1)
    new_character.will = backup_data.get('will', 1)
    new_character.edge = backup_data.get('edge', 1)
    new_character.emp = backup_data.get('emp', 1)
    
    # Restore skills
    new_character.db.skills = dict(backup_data.get('skills', {}))
    
    # Restore appearance
    new_character.db.desc = backup_data.get('desc', '')
    new_character.db.nakeds = dict(backup_data.get('nakeds', {}))
    new_character.db.skintone = backup_data.get('skintone')
    new_character.sex = backup_data.get('sex', 'ambiguous')
    
    # Copy the backup to the new character so they can update it
    new_character.db.clone_backup = backup_data
    new_character.db.clone_backup_count = 0  # Reset update count for new sleeve
    
    _log(f"CLONE_RESTORE: Restored {new_character.key} from backup")
    
    return True


# ============================================================================
# TERRAGROUP CLONING DIVISION TYPECLASS
# ============================================================================

class CloningPod(Object):
    """
    A TerraGroup Cloning Division pod that players can sit in to backup their consciousness.
    
    Usage:
        sit in pod - Start the cloning process
        stand - Cancel (if not in cutscene) or auto-stand after completion
    """
    
    def at_object_creation(self):
        """Set up the TerraGroup Cloning Division pod."""
        self.db.desc = (
            "A sleek, coffin-shaped pod made of polished white polymer and brushed steel. "
            "A faint blue glow emanates from within, pulsing slowly like a heartbeat. "
            "The interior is lined with thousands of microscopic neural sensors. "
            "A sleek TerraGroup Cloning Division logo is embossed on the side. "
            "A small display reads: |gTERRAGROUP CLONING DIVISION - CONSCIOUSNESS BACKUP READY|n"
        )
        
        # Pod state
        self.db.occupant = None
        self.db.in_use = False
        
        # Add the pod command set
        self.cmdset.add_default(TerraGroupCloningDivisionCmdSet)
    
    def get_display_name(self, looker, **kwargs):
        """Show status in name."""
        base = super().get_display_name(looker, **kwargs)
        if self.db.in_use:
            return f"{base} |y(IN USE)|n"
        return base
    
    def start_cloning_sequence(self, character):
        """
        Start the cloning/backup sequence.
        
        Args:
            character: The character sitting in the pod
        """
        if self.db.in_use:
            character.msg("The pod is already in use.")
            return False
        
        # Check cost
        can_afford, cost, is_update = can_afford_clone(character)
        if not can_afford:
            character.msg(f"|rInsufficient funds. Cloning costs {cost} credits.|n")
            return False
        
        # Mark pod and character as busy
        self.db.in_use = True
        self.db.occupant = character
        character.ndb._in_terragroup_pod = True
        character.ndb._terragroup_pod = self
        
        # Restrict movement
        character.ndb._movement_locked = True
        
        # Determine message based on update vs new
        if is_update:
            action_msg = "UPDATING CONSCIOUSNESS BACKUP"
        else:
            action_msg = "INITIATING CONSCIOUSNESS BACKUP"
        
        # Start the cutscene
        self._play_cutscene(character, action_msg, is_update)
        
        return True
    
    def _play_cutscene(self, character, action_msg, is_update):
        """Play the 10-second cloning cutscene."""
        
        # Frame 1: Pod closes (immediate)
        character.msg(f"\n|b{'=' * 60}|n")
        character.msg("|bThe pod's canopy slides shut with a soft hiss.|n")
        character.msg("|bCool blue light envelops you as neural sensors activate.|n")
        character.msg(f"|b{'=' * 60}|n\n")
        
        if character.location:
            character.location.msg_contents(
                f"|bThe TerraGroup Cloning Division pod closes around {character.key}, blue light pulsing within.|n",
                exclude=[character]
            )
        
        # Frame 2: Scanning (2 seconds)
        delay(2, self._cutscene_frame_2, character, action_msg)
        
        # Frame 3: Processing (5 seconds)
        delay(5, self._cutscene_frame_3, character)
        
        # Frame 4: Complete (8 seconds)
        delay(8, self._cutscene_frame_4, character, is_update)
        
        # Frame 5: Open pod and finish (10 seconds)
        delay(10, self._complete_cloning, character, is_update)
    
    def _cutscene_frame_2(self, character, action_msg):
        """Scanning phase."""
        if not character or not self.db.in_use:
            return
        character.msg(f"|c[TERRAGROUP CLONING DIVISION - CONSCIOUSNESS BACKUP SYSTEM]|n")
        character.msg(f"|c{action_msg}...|n")
        character.msg("|cScanning neural pathways... mapping synaptic connections...|n")
    
    def _cutscene_frame_3(self, character):
        """Processing phase."""
        if not character or not self.db.in_use:
            return
        character.msg("|cEncoding personality matrix...|n")
        character.msg("|cCompressing memory engrams...|n")
        character.msg("|cVerifying stack integrity...|n")
    
    def _cutscene_frame_4(self, character, is_update):
        """Completion phase."""
        if not character or not self.db.in_use:
            return
        
        if is_update:
            character.msg("|gBackup updated successfully.|n")
            character.msg("|gYour consciousness snapshot has been refreshed.|n")
        else:
            character.msg("|gInitial backup complete.|n")
            character.msg("|gYour consciousness has been archived.|n")
    
    def _complete_cloning(self, character, is_update):
        """Complete the cloning process and open the pod."""
        if not character:
            self._reset_pod()
            return
        
        # Actually create the backup
        backup = create_clone_backup(character)
        
        # Deduct cost (when monetization is added)
        cost, _ = get_clone_cost(character)
        if cost > 0:
            # Future: character.db.money -= cost
            pass
        
        # Final messages
        character.msg(f"\n|g{'=' * 60}|n")
        character.msg("|gPROCEDURE COMPLETE|n")
        character.msg(f"|gBackup timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(backup['timestamp']))}|n")
        character.msg("|gIn the event of sleeve death, your consciousness will be restored.|n")
        character.msg(f"|g{'=' * 60}|n\n")
        
        character.msg("|bThe pod's canopy slides open. You may now stand.|n")
        
        if character.location:
            character.location.msg_contents(
                f"|bThe TerraGroup Cloning Division pod opens with a hiss. {character.key} has completed their backup.|n",
                exclude=[character]
            )
        
        # Unlock movement and auto-stand
        character.ndb._movement_locked = False
        
        # Auto-stand the character
        self._auto_stand(character)
    
    def _auto_stand(self, character):
        """Automatically stand the character up."""
        if not character:
            self._reset_pod()
            return
        
        # Clear character's pod state
        if hasattr(character.ndb, '_in_terragroup_pod'):
            del character.ndb._in_terragroup_pod
        if hasattr(character.ndb, '_terragroup_pod'):
            del character.ndb._terragroup_pod
        
        # Reset pod state
        self._reset_pod()
        
        # Stand the character (clear any sitting state)
        if hasattr(character, 'db') and hasattr(character.db, 'sitting_on'):
            character.db.sitting_on = None
        
        character.msg("|wYou stand up from the TerraGroup Cloning Division pod.|n")
    
    def _reset_pod(self):
        """Reset the pod to available state."""
        self.db.in_use = False
        self.db.occupant = None
    
    def force_eject(self, character):
        """Force eject a character from the pod (for emergencies)."""
        if character:
            character.ndb._movement_locked = False
            if hasattr(character.ndb, '_in_terragroup_pod'):
                del character.ndb._in_terragroup_pod
            if hasattr(character.ndb, '_terragroup_pod'):
                del character.ndb._terragroup_pod
            character.msg("|yYou are ejected from the TerraGroup Cloning Division pod.|n")
        
        self._reset_pod()


# ============================================================================
# TERRAGROUP CLONING DIVISION POD COMMANDS
# ============================================================================

class CmdSitInPod(Command):
    """
    Sit in the TerraGroup Cloning Division pod to backup your consciousness.
    
    Usage:
        sit in pod
        sit pod
        use pod
        enter pod
    
    This will backup your current stats, skills, and appearance.
    When you die, you will be restored to this backup state in a new sleeve.
    """
    
    key = "sit"
    aliases = ["use", "enter"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        # Find the TerraGroup Cloning Division pod in the room
        pod = None
        for obj in caller.location.contents:
            if isinstance(obj, TerraGroupMedicalPod):
                pod = obj
                break
        
        if not pod:
            caller.msg("There's no TerraGroup Cloning Division pod here.")
            return
        
        # Check if already in pod
        if getattr(caller.ndb, '_in_terragroup_pod', False):
            caller.msg("You're already in the TerraGroup Cloning Division pod.")
            return
        
        # Check if pod is in use
        if pod.db.in_use:
            caller.msg("The TerraGroup Cloning Division pod is currently in use.")
            return
        
        # Check cost and show appropriate message
        can_afford, cost, is_update = can_afford_clone(caller)
        
        if is_update:
            caller.msg(f"|cThis will update your existing consciousness backup.|n")
        else:
            caller.msg(f"|cThis will create your first consciousness backup.|n")
        
        if cost > 0:
            caller.msg(f"|cCost: {cost} credits|n")
            if not can_afford:
                caller.msg("|rYou cannot afford this procedure.|n")
                return
        else:
            caller.msg("|cCost: Free|n")
        
        # Start the cloning sequence
        caller.msg("|wYou climb into the TerraGroup Cloning Division pod and lie back...|n")
        
        if caller.location:
            caller.location.msg_contents(
                f"|w{caller.key} climbs into the TerraGroup Cloning Division pod.|n",
                exclude=[caller]
            )
        
        pod.start_cloning_sequence(caller)


class CmdLeavePod(Command):
    """
    Stand up / leave the TerraGroup Cloning Division pod.
    
    Usage:
        stand
        leave
        exit
    
    Note: You cannot leave during the cloning procedure.
    """
    
    key = "stand"
    aliases = ["leave", "exit"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        
        # Check if in pod
        if not getattr(caller.ndb, '_in_terragroup_pod', False):
            caller.msg("You're not in the TerraGroup Cloning Division pod.")
            return
        
        # Check if locked (during cutscene)
        if getattr(caller.ndb, '_movement_locked', False):
            caller.msg("|yProcedure in progress. Please remain still.|n")
            return
        
        # Get the pod and force eject
        pod = getattr(caller.ndb, '_terragroup_pod', None)
        if pod:
            pod.force_eject(caller)
        else:
            # Clean up manually
            caller.ndb._in_terragroup_pod = False
            caller.msg("|wYou stand up from the TerraGroup Cloning Division pod.|n")


class TerraGroupCloningDivisionCmdSet(CmdSet):
    """Commands available at TerraGroup Cloning Division pods."""
    
    key = "terragroup_cloning_division_cmdset"
    priority = 1
    
    def at_cmdset_creation(self):
        self.add(CmdSitInPod())
        self.add(CmdLeavePod())


# ============================================================================
# GENERAL CLONE COMMANDS (add to default cmdset)
# ============================================================================

class CmdCloneStatus(Command):
    """
    Check your sleeve backup status.
    
    Usage:
        clone
        clone status
        backup
        backup status
    
    Shows whether you have a sleeve backup and when it was last updated.
    """
    
    key = "clone"
    aliases = ["backup", "clone status", "backup status"]
    locks = "cmd:all()"
    help_category = "General"
    
    def func(self):
        caller = self.caller
        
        backup = get_clone_backup(caller)
        
        if not backup:
            caller.msg("|r" + "=" * 50 + "|n")
            caller.msg("|rSLEEVE BACKUP STATUS: |RNOT FOUND|n")
            caller.msg("|r" + "=" * 50 + "|n")
            caller.msg("|yYou have no sleeve backup on file.|n")
            caller.msg("|yIf you die, you will need to create a new identity.|n")
            caller.msg("|yFind a TerraGroup Cloning Division pod to create a backup.|n")
            return
        
        # Format timestamp
        backup_time = backup.get('timestamp', 0)
        time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(backup_time))
        
        # Calculate age
        age_seconds = time.time() - backup_time
        if age_seconds < 3600:
            age_str = f"{int(age_seconds / 60)} minutes ago"
        elif age_seconds < 86400:
            age_str = f"{int(age_seconds / 3600)} hours ago"
        else:
            age_str = f"{int(age_seconds / 86400)} days ago"
        
        caller.msg("|g" + "=" * 50 + "|n")
        caller.msg("|gSLEEVE BACKUP STATUS: |GACTIVE|n")
        caller.msg("|g" + "=" * 50 + "|n")
        caller.msg(f"|wLast backup: |c{time_str}|n")
        caller.msg(f"|w            ({age_str})|n")
        caller.msg("|g" + "-" * 50 + "|n")
        caller.msg("|wBacked up data:|n")
        caller.msg(f"  |wStats:|n Body {backup.get('body',1)}, Ref {backup.get('ref',1)}, "
                   f"Dex {backup.get('dex',1)}, Tech {backup.get('tech',1)}")
        caller.msg(f"        |n Smrt {backup.get('smrt',1)}, Will {backup.get('will',1)}, "
                   f"Edge {backup.get('edge',1)}, Emp {backup.get('emp',1)}")
        
        skills = backup.get('skills', {})
        if skills:
            caller.msg(f"  |wSkills:|n {len(skills)} skills backed up")
        else:
            caller.msg(f"  |wSkills:|n None")
        
        caller.msg(f"  |wAppearance:|n Backed up")
        caller.msg("|g" + "-" * 50 + "|n")
        caller.msg("|yNote: Chrome and inventory are NOT backed up.|n")
        caller.msg("|yUpdate your backup regularly at a TerraGroup Cloning Division pod.|n")


class CmdSpawnPod(Command):
    """
    Spawn a TerraGroup Cloning Division pod in the current room.
    
    Usage:
        @spawnpod
    
    Admin command to create a TerraGroup Cloning Division pod.
    """
    
    key = "@spawnpod"
    locks = "cmd:perm(Builder)"
    help_category = "Building"
    
    def func(self):
        from evennia import create_object
        
        pod = create_object(
            TerraGroupMedicalPod,
            key="TerraGroup Cloning Division pod",
            location=self.caller.location
        )
        
        self.caller.msg(f"|gCreated TerraGroup Cloning Division pod: {pod.key} (#{pod.dbref})|n")
        self.caller.location.msg_contents(
            f"|wA TerraGroup Cloning Division pod materializes in the room.|n",
            exclude=[self.caller]
        )
