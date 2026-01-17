"""
Kowloon Door/Lock/Keypad Command Module
Last updated: 2025-11-28
"""
from evennia import Command
import time
from evennia import Command
from evennia.comms.models import ChannelDB

def get_audit_channel():
    return ChannelDB.objects.get_channel("BuilderAudit")

def find_door(room, direction):
    """Find a door object in the room matching the given direction or any alias."""
    direction = direction.lower()
    for obj in room.contents:
        if obj.is_typeclass("typeclasses.doors.Door"):
            # Match direction or any alias
            aliases = getattr(obj.db, "exit_aliases", [])
            if aliases is None:
                aliases = []
            exit_direction = getattr(obj.db, "exit_direction", None)
            if exit_direction:
                exit_direction = exit_direction.lower()
            else:
                exit_direction = ""
            if direction == exit_direction or direction in aliases:
                return obj
    return None

def find_lock(door, direction):
    """Find a lock on the door matching the given direction or any alias."""
    direction = direction.lower()
    lock = getattr(door.db, "lock", None)
    if lock:
        aliases = getattr(lock.db, "exit_aliases", [])
        if direction == getattr(lock.db, "exit_direction", "").lower() or direction in aliases:
            return lock
    return lock if lock else None

def find_keypad(door, direction):
    """Find a keypad on the door matching the given direction or any alias."""
    direction = direction.lower()
    keypad = getattr(door.db, "keypad", None)
    if keypad:
        aliases = getattr(keypad.db, "exit_aliases", [])
        if aliases is None:
            aliases = []
        exit_direction = getattr(keypad.db, "exit_direction", None)
        if exit_direction:
            exit_direction = exit_direction.lower()
        else:
            exit_direction = ""
        if direction == exit_direction or direction in aliases:
            return keypad
    return keypad if keypad else None


def find_exit_by_direction(room, direction):
    """Find an exit in the room by direction or alias."""
    direction = direction.lower()
    for ex in getattr(room, "exits", []):
        aliases = [a.lower() for a in (ex.aliases.all() if hasattr(ex.aliases, "all") else [])]
        if ex.key.lower() == direction or direction in aliases:
            return ex
    return None


class CmdAttachDoor(Command):
    """
    Attach a door to an exit.
    
    Usage:
        attachdoor <direction>
        
    Attaches a door to the specified exit. The door state is stored
    on the exit itself and will show +/- indicators in the room exits.
    Also creates a matching door on the reverse exit in the destination room.
    """
    key = "attachdoor"
    locks = "cmd:perm(Builder)"
    help_category = "Building"
    
    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: attachdoor <direction>")
            return
        direction = self.args.strip().lower()
        
        # Find the exit
        exit_obj = find_exit_by_direction(caller.location, direction)
        if not exit_obj:
            caller.msg(f"No exit found in direction '{direction}'.")
            return
        
        # Check if exit already has a door
        if getattr(exit_obj.db, "has_door", False):
            caller.msg(f"A door already exists on exit '{exit_obj.key}'.")
            return
        
        # Also check for legacy Door objects
        if find_door(caller.location, direction):
            caller.msg(f"A legacy door object exists for exit '{direction}'. Use @cleanup_doors first.")
            return
        
        # Attach door to exit
        exit_obj.attach_door()
        caller.msg(f"Door attached to exit '{exit_obj.key}'.")
        
        audit_channel = get_audit_channel()
        if audit_channel:
            audit_channel.msg(f"{caller.key} attached door to exit '{exit_obj.key}' in {caller.location.key}.")
        
        # Create matching door in destination room
        dest_room = getattr(exit_obj, "destination", None)
        if dest_room:
            # Find reverse direction
            reverse_map = {
                "north": "south", "south": "north", "east": "west", "west": "east",
                "northeast": "southwest", "southwest": "northeast", 
                "northwest": "southeast", "southeast": "northwest",
                "up": "down", "down": "up", "in": "out", "out": "in",
                "n": "s", "s": "n", "e": "w", "w": "e"
            }
            reverse_dir = reverse_map.get(exit_obj.key.lower(), None)
            
            if not reverse_dir:
                # Try to find exit in dest_room that leads back to caller.location
                for ex in getattr(dest_room, "exits", []):
                    if getattr(ex, "destination", None) == caller.location:
                        reverse_dir = ex.key.lower()
                        break
            
            if reverse_dir:
                reverse_exit = find_exit_by_direction(dest_room, reverse_dir)
                if reverse_exit and not getattr(reverse_exit.db, "has_door", False):
                    reverse_exit.attach_door()
                    if audit_channel:
                        audit_channel.msg(f"Auto-attached matching door to exit '{reverse_exit.key}' in {dest_room.key}.")
                    caller.msg(f"Also attached door to reverse exit '{reverse_exit.key}' in {dest_room.key}.")

class CmdAttachLock(Command):
    """Attach a lock to a door on an exit."""
    key = "attachlock"
    locks = "cmd:perm(Builder)"
    help_category = "Building"
    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: attachlock <direction>")
            return
        direction = self.args.strip().lower()
        door = find_door(caller.location, direction)
        if not door:
            caller.msg(f"No door found for exit '{direction}'.")
            return
        from typeclasses.doors import Lock
        lock = Lock()
        lock.save()  # Ensure DB id exists before setting attributes
        # Store all aliases for this exit (including key)
        exit_aliases = [direction]
        for ex in getattr(caller.location, "exits", []):
            if ex.key.lower() == direction or direction in [a.lower() for a in (ex.aliases.all() if hasattr(ex.aliases, "all") else [])]:
                exit_aliases = [ex.key.lower()]
                if hasattr(ex.aliases, "all"):
                    exit_aliases += [a.lower() for a in ex.aliases.all()]
                break
        lock.db.exit_aliases = list(set(exit_aliases))
        door.attach_lock(lock)
        caller.msg(f"Lock attached to door for exit '{direction}'.")
        audit_channel = get_audit_channel()
        if audit_channel:
            audit_channel.msg(f"{caller.key} attached lock to exit '{direction}'.")

class CmdAttachKeypad(Command):
    """
    Attach a keypad lock to a door on an exit.
    
    Usage:
        attachkeypad <direction>
        
    Attaches a keypad to the door on the specified exit. The keypad code
    is stored on the exit itself and syncs with the reverse exit.
    """
    key = "attachkeypad"
    locks = "cmd:perm(Builder)"
    help_category = "Building"
    
    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: attachkeypad <direction>")
            return
        direction = self.args.strip().lower()
        
        # Find the exit
        exit_obj = find_exit_by_direction(caller.location, direction)
        if not exit_obj:
            caller.msg(f"No exit found in direction '{direction}'.")
            return
        
        # Check if exit has a door
        if not getattr(exit_obj.db, "has_door", False):
            caller.msg(f"No door on exit '{exit_obj.key}'. Use 'attachdoor {direction}' first.")
            return
        
        # Check if keypad already exists
        if getattr(exit_obj.db, "door_keypad_code", None):
            caller.msg(f"Exit '{exit_obj.key}' already has a keypad.")
            return
        
        # Attach keypad with default code
        exit_obj.db.door_keypad_code = "00000000"
        exit_obj.db.door_keypad_unlocked = False
        
        caller.msg(f"Keypad lock attached to door for exit '{exit_obj.key}'. Default code: 00000000")
        
        audit_channel = get_audit_channel()
        if audit_channel:
            audit_channel.msg(f"{caller.key} attached keypad to exit '{exit_obj.key}' in {caller.location.key}.")
        
        # Attach matching keypad to reverse exit
        dest_room = getattr(exit_obj, "destination", None)
        if dest_room:
            reverse_exit = exit_obj._get_reverse_exit()
            if reverse_exit and getattr(reverse_exit.db, "has_door", False):
                if not getattr(reverse_exit.db, "door_keypad_code", None):
                    reverse_exit.db.door_keypad_code = "00000000"
                    reverse_exit.db.door_keypad_unlocked = False
                    if audit_channel:
                        audit_channel.msg(f"Auto-attached matching keypad to exit '{reverse_exit.key}' in {dest_room.key}.")
                    caller.msg(f"Also attached keypad to reverse exit '{reverse_exit.key}' in {dest_room.key}.")


class CmdRemoveDoor(Command):
    """
    Remove a door from an exit.
    
    Usage:
        removedoor <direction>
        
    Removes the door from the specified exit and also removes the 
    matching door from the reverse exit in the destination room.
    """
    key = "removedoor"
    locks = "cmd:perm(Builder)"
    help_category = "Building"
    
    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: removedoor <direction>")
            return
        direction = self.args.strip().lower()
        
        # Find the exit
        exit_obj = find_exit_by_direction(caller.location, direction)
        audit_channel = get_audit_channel()
        
        # First check for exit-based door
        if exit_obj and getattr(exit_obj.db, "has_door", False):
            exit_obj.remove_door()
            caller.msg(f"Door removed from exit '{exit_obj.key}'.")
            if audit_channel:
                audit_channel.msg(f"{caller.key} removed door from exit '{exit_obj.key}' in {caller.location.key}.")
            
            # Remove matching door in destination room
            dest_room = getattr(exit_obj, "destination", None)
            if dest_room:
                reverse_map = {
                    "north": "south", "south": "north", "east": "west", "west": "east",
                    "northeast": "southwest", "southwest": "northeast", 
                    "northwest": "southeast", "southeast": "northwest",
                    "up": "down", "down": "up", "in": "out", "out": "in",
                    "n": "s", "s": "n", "e": "w", "w": "e"
                }
                reverse_dir = reverse_map.get(exit_obj.key.lower(), None)
                
                if not reverse_dir:
                    for ex in getattr(dest_room, "exits", []):
                        if getattr(ex, "destination", None) == caller.location:
                            reverse_dir = ex.key.lower()
                            break
                
                if reverse_dir:
                    reverse_exit = find_exit_by_direction(dest_room, reverse_dir)
                    if reverse_exit and getattr(reverse_exit.db, "has_door", False):
                        reverse_exit.remove_door()
                        if audit_channel:
                            audit_channel.msg(f"Auto-removed matching door from exit '{reverse_exit.key}' in {dest_room.key}.")
                        caller.msg(f"Also removed door from reverse exit '{reverse_exit.key}' in {dest_room.key}.")
            return
        
        # Fallback to legacy Door objects
        door = find_door(caller.location, direction)
        if not door:
            caller.msg(f"No door found for exit '{direction}'.")
            return
        
        # Remove door in current room
        door.delete()
        caller.msg(f"Door removed from exit '{direction}'.")
        if audit_channel:
            audit_channel.msg(f"{caller.key} removed door from exit '{direction}'.")
        
        # Remove matching door in destination room
        dest_room = getattr(exit_obj, "destination", None) if exit_obj else None
        if dest_room:
            reverse_map = {
                "north": "south", "south": "north", "east": "west", "west": "east",
                "northeast": "southwest", "southwest": "northeast", 
                "northwest": "southeast", "southeast": "northwest",
                "up": "down", "down": "up", "in": "out", "out": "in"
            }
            reverse_dir = reverse_map.get(direction, None)
            if not reverse_dir:
                for ex in getattr(dest_room, "exits", []):
                    if getattr(ex, "destination", None) == caller.location:
                        reverse_dir = ex.key.lower()
                        break
            rev_door = find_door(dest_room, reverse_dir) if reverse_dir else None
            if rev_door:
                rev_door.delete()
                if audit_channel:
                    audit_channel.msg(f"Auto-removed matching door from exit '{reverse_dir}' in {dest_room.key}.")


class CmdRemoveLock(Command):
    """Remove a lock from a door on an exit."""
    key = "removelock"
    locks = "cmd:perm(Builder)"
    help_category = "Building"
    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: removelock <direction>")
            return
        direction = self.args.strip().lower()
        door = find_door(caller.location, direction)
        if not door or not door.db.lock:
            caller.msg(f"No lock found on door for exit '{direction}'.")
            return
        door.db.lock.delete()
        door.db.lock = None
        caller.msg(f"Lock removed from door for exit '{direction}'.")
        audit_channel = get_audit_channel()
        if audit_channel:
            audit_channel.msg(f"{caller.key} removed lock from exit '{direction}'.")

class CmdRemoveKeypad(Command):
    """Remove a keypad lock from a door on an exit."""
    key = "removekeypad"
    locks = "cmd:perm(Builder)"
    help_category = "Building"
    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: removekeypad <direction>")
            return
        direction = self.args.strip().lower()
        door = find_door(caller.location, direction)
        if not door or not door.db.keypad:
            caller.msg(f"No keypad found on door for exit '{direction}'.")
            return
        door.db.keypad.delete()
        door.db.keypad = None
        caller.msg(f"Keypad lock removed from door for exit '{direction}'.")
        audit_channel = get_audit_channel()
        if audit_channel:
            audit_channel.msg(f"{caller.key} removed keypad from exit '{direction}'.")

class CmdProgramKeypad(Command):
    """
    Set the keypad's 8-digit combination.
    
    Usage:
        programkeypad <direction> <old_combo> <new_combo>
    """
    key = "programkeypad"
    locks = "cmd:perm(Builder)"
    help_category = "Building"
    
    def func(self):
        caller = self.caller
        args = self.args.strip().split()
        if len(args) != 3:
            caller.msg("Usage: programkeypad <direction> <old_combo> <new_combo>")
            return
        direction, old_combo, new_combo = args
        direction = direction.strip().lower()
        
        if len(new_combo) != 8 or not new_combo.isdigit():
            caller.msg("New combination must be 8 digits.")
            return
        
        if len(old_combo) != 8 or not old_combo.isdigit():
            caller.msg("Old combination must be 8 digits.")
            return
        
        # Find the exit
        exit_obj = find_exit_by_direction(caller.location, direction)
        if not exit_obj:
            caller.msg(f"No exit found in direction '{direction}'.")
            return
        
        # Check if exit has a door with keypad
        if not getattr(exit_obj.db, "has_door", False):
            caller.msg(f"No door on exit '{exit_obj.key}'.")
            return
        
        current_code = getattr(exit_obj.db, "door_keypad_code", None)
        if not current_code:
            caller.msg(f"No keypad on door for exit '{exit_obj.key}'. Use 'attachkeypad {direction}' first.")
            return
        
        # Verify old code
        if old_combo != current_code:
            caller.msg("Incorrect old combination.")
            return
        
        # Set the new code
        exit_obj.db.door_keypad_code = new_combo
        caller.msg(f"Keypad combo for exit '{exit_obj.key}' changed from {old_combo} to {new_combo}.")
        
        audit_channel = get_audit_channel()
        if audit_channel:
            audit_channel.msg(f"{caller.key} programmed keypad combo for exit '{exit_obj.key}' to {new_combo}.")
        # Sync combo to paired keypad on reverse exit
        dest_room = getattr(exit_obj, "destination", None)
        if dest_room:
            reverse_exit = exit_obj._get_reverse_exit()
            if reverse_exit and getattr(reverse_exit.db, "door_keypad_code", None):
                reverse_exit.db.door_keypad_code = new_combo
                if audit_channel:
                    audit_channel.msg(f"Auto-synced keypad combo for exit '{reverse_exit.key}' in {dest_room.key}.")
                caller.msg(f"Also synced code to reverse exit '{reverse_exit.key}' in {dest_room.key}.")

class CmdShowCombo(Command):
    """Show the keypad combo (builder+ only)."""
    key = "showcombo"
    locks = "cmd:perm(Builder)"
    help_category = "Building"
    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: showcombo <direction>")
            return
        direction = self.args.strip().lower()
        
        # First check for exit-based door with keypad
        exit_obj = find_exit_by_direction(caller.location, direction)
        if exit_obj and getattr(exit_obj.db, "has_door", False):
            keypad_code = getattr(exit_obj.db, "door_keypad_code", None)
            if keypad_code:
                caller.msg(f"Keypad combo for exit '{exit_obj.key}': {keypad_code}")
                return
            else:
                caller.msg(f"No keypad on door for exit '{exit_obj.key}'.")
                return
        
        # Fallback to legacy Door objects
        door = find_door(caller.location, direction)
        if not door or not door.db.keypad:
            caller.msg(f"No keypad found on door for exit '{direction}'.")
            return
        caller.msg(f"Keypad combo for exit '{direction}': {door.db.keypad.db.combination}")


class CmdOpenDoor(Command):
    """
    Open a door on an exit.
    
    Usage:
        opendoor <direction>
        open door <direction>
    """
    key = "opendoor"
    aliases = ["open door"]
    locks = "cmd:all()"
    help_category = "General"
    
    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: opendoor <direction>")
            return
        direction = self.args.strip().lower()
        
        # First check for exit-based door
        exit_obj = find_exit_by_direction(caller.location, direction)
        if exit_obj and getattr(exit_obj.db, "has_door", False):
            result = exit_obj.door_open(caller)
            if result:
                audit_channel = get_audit_channel()
                if audit_channel:
                    audit_channel.msg(f"{caller.key} opened door on exit '{exit_obj.key}'.")
            return
        
        # Fallback to legacy Door objects
        door = find_door(caller.location, direction)
        if not door:
            # Try to find exit by alias and search for door
            if exit_obj:
                all_aliases = [exit_obj.key.lower()]
                if hasattr(exit_obj.aliases, "all"):
                    all_aliases += [a.lower() for a in exit_obj.aliases.all()]
                for alias in all_aliases:
                    door = find_door(caller.location, alias)
                    if door:
                        break
        
        if not door:
            caller.msg(f"No door found for exit '{direction}'.")
            return
        
        result = door.open(caller)
        if result:
            audit_channel = get_audit_channel()
            if audit_channel:
                audit_channel.msg(f"{caller.key} opened door on exit '{direction}'.")


class CmdCloseDoor(Command):
    """
    Close a door on an exit.
    
    Usage:
        closedoor <direction>
        close door <direction>
    """
    key = "closedoor"
    aliases = ["close door"]
    locks = "cmd:all()"
    help_category = "General"
    
    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: closedoor <direction>")
            return
        direction = self.args.strip().lower()
        
        # First check for exit-based door
        exit_obj = find_exit_by_direction(caller.location, direction)
        if exit_obj and getattr(exit_obj.db, "has_door", False):
            result = exit_obj.door_close(caller)
            if result:
                audit_channel = get_audit_channel()
                if audit_channel:
                    audit_channel.msg(f"{caller.key} closed door on exit '{exit_obj.key}'.")
            return
        
        # Fallback to legacy Door objects
        door = find_door(caller.location, direction)
        if not door:
            # Try to find exit by alias and search for door
            if exit_obj:
                all_aliases = [exit_obj.key.lower()]
                if hasattr(exit_obj.aliases, "all"):
                    all_aliases += [a.lower() for a in exit_obj.aliases.all()]
                for alias in all_aliases:
                    door = find_door(caller.location, alias)
                    if door:
                        break
        
        if not door:
            caller.msg(f"No door found for exit '{direction}'.")
            return
        result = door.close(caller)
        if result:
            audit_channel = get_audit_channel()
            if audit_channel:
                audit_channel.msg(f"{caller.key} closed door on exit '{direction}'.")


class CmdLockDoor(Command):
    """Lock a door on an exit (if you have the key)."""
    key = "lockdoor"
    locks = "cmd:all()"
    help_category = "General"
    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: lockdoor <direction> [key]")
            return
        args = self.args.strip().split()
        direction = args[0].lower()
        key_obj = None
        if len(args) > 1:
            key_obj = caller.search(args[1], quiet=True)
            key_obj = key_obj[0] if key_obj else None
        door = find_door(caller.location, direction)
        if not door or not door.db.lock:
            caller.msg(f"No lock found on door for exit '{direction}'.")
            return
        lock = door.db.lock
        if lock.db.is_locked:
            caller.msg("The lock is already locked.")
            return
        lock.lock(caller)
        door.db.is_locked = True
        caller.msg(lock.db.lock_msg if hasattr(lock.db, "lock_msg") else "You lock the door.")
        audit_channel = get_audit_channel()
        if audit_channel:
            audit_channel.msg(f"{caller.key} locked door on exit '{direction}'.")

class CmdUnlockDoor(Command):
    """Unlock a door on an exit (if you have the key)."""
    key = "unlockdoor"
    locks = "cmd:all()"
    help_category = "General"
    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: unlockdoor <direction> [key]")
            return
        args = self.args.strip().split()
        direction = args[0].lower()
        key_obj = None
        if len(args) > 1:
            key_obj = caller.search(args[1], quiet=True)
            key_obj = key_obj[0] if key_obj else None
        door = find_door(caller.location, direction)
        if not door or not door.db.lock:
            caller.msg(f"No lock found on door for exit '{direction}'.")
            return
        lock = door.db.lock
        if not lock.db.is_locked:
            caller.msg("The lock is already unlocked.")
            return
        if not key_obj or not hasattr(key_obj.db, "key_id") or key_obj.db.key_id != lock.db.key_id:
            caller.msg("You don't have the correct key.")
            return
        lock.unlock(key_obj, caller)
        door.db.is_locked = False
        caller.msg(lock.db.unlock_msg if hasattr(lock.db, "unlock_msg") else "You unlock the door.")
        audit_channel = get_audit_channel()
        if audit_channel:
            audit_channel.msg(f"{caller.key} unlocked door on exit '{direction}'.")

class CmdDoorStatus(Command):
    """Show status of door, lock, and keypad on an exit (builder+ only)."""
    key = "doorstatus"
    locks = "cmd:perm(Builder)"
    help_category = "Building"
    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: doorstatus <direction>")
            return
        direction = self.args.strip().lower()
        exit_obj = None
        for ex in getattr(caller.location, "exits", []):
            aliases = [a.lower() for a in (ex.aliases.all() if hasattr(ex.aliases, "all") else [])]
            if ex.key.lower() == direction or direction in aliases:
                exit_obj = ex
                break
        if not exit_obj:
            caller.msg(f"No exit found in direction '{direction}'.")
            return
        door = getattr(exit_obj.db, "door", None)
        msg = f"Status for exit '{direction}':\n"
        if not door:
            msg += "  No door attached."
        else:
            msg += f"  Door: {'open' if door.db.is_open else 'closed'}\n"
            msg += f"  Lock: {'locked' if door.db.is_locked else 'unlocked'}\n" if hasattr(door.db, "is_locked") else "  Lock: none\n"
            keypad = getattr(door.db, "keypad", None)
            if keypad:
                msg += f"  Keypad: {'unlocked' if keypad.db.is_unlocked else 'locked'}\n"
                msg += f"  Combo: {keypad.db.combination}\n"
                msg += f"  Failed attempts: {getattr(keypad.db, 'failed_attempts', 0)}\n"
            else:
                msg += "  Keypad: none\n"
        caller.msg(msg)

class CmdSetDoorMsg(Command):
    """Set custom open/close/lock/unlock messages for a door (builder+ only)."""
    key = "setdoormsg"
    locks = "cmd:perm(Builder)"
    help_category = "Building"
    def func(self):
        caller = self.caller
        args = self.args.strip().split(None, 2)
        if len(args) != 3:
            caller.msg("Usage: setdoormsg <direction> <type> <message>")
            return
        direction, msgtype, message = args
        exit_obj = caller.location.exits.get(direction)
        if not exit_obj or not hasattr(exit_obj.db, "door"):
            caller.msg(f"No door found on exit '{direction}'.")
            return
        door = exit_obj.db.door
        if msgtype not in ("open", "close", "lock", "unlock"):
            caller.msg("Type must be one of: open, close, lock, unlock.")
            return
        setattr(door.db, f"{msgtype}_msg", message)
        caller.msg(f"Custom {msgtype} message set for door on exit '{direction}'.")
        audit_channel = get_audit_channel()
        if audit_channel:
            audit_channel.msg(f"{caller.key} set custom {msgtype} message for door on exit '{direction}'.")

class CmdBulkAttach(Command):
    """Bulk attach doors/locks/keypads to multiple exits (builder+ only)."""
    key = "bulkattach"
    locks = "cmd:perm(Builder)"
    help_category = "Building"
    def func(self):
        caller = self.caller
        args = self.args.strip().split()
        if len(args) < 2:
            caller.msg("Usage: bulkattach <component> <direction1> [direction2 ...]")
            return
        component = args[0].lower()
        directions = args[1:]
        for direction in directions:
            exit_obj = caller.location.exits.get(direction)
            if not exit_obj:
                caller.msg(f"No exit found in direction '{direction}'.")
                continue
            if component == "door":
                from typeclasses.doors import Door
                door = Door()
                door.save()  # Ensure DB id exists before setting attributes
                door.db.exit_direction = direction
                door.location = caller.location
                exit_obj.db.door = door
                caller.msg(f"Door attached to exit '{direction}'.")
                audit_channel = get_audit_channel()
                if audit_channel:
                    audit_channel.msg(f"{caller.key} bulk-attached door to exit '{direction}'.")
            elif component == "lock":
                from typeclasses.doors import Lock
                if not hasattr(exit_obj.db, "door"):
                    caller.msg(f"No door found on exit '{direction}' for lock attachment.")
                    continue
                lock = Lock()
                lock.save()  # Ensure DB id exists before setting attributes
                exit_obj.db.door.attach_lock(lock)
                caller.msg(f"Lock attached to door on exit '{direction}'.")
                audit_channel = get_audit_channel()
                if audit_channel:
                    audit_channel.msg(f"{caller.key} bulk-attached lock to exit '{direction}'.")
            elif component == "keypad":
                from typeclasses.doors import KeypadLock
                if not hasattr(exit_obj.db, "door"):
                    caller.msg(f"No door found on exit '{direction}' for keypad attachment.")
                    continue
                keypad = KeypadLock()
                keypad.save()  # Ensure DB id exists before setting attributes
                exit_obj.db.door.attach_keypad(keypad)
                caller.msg(f"Keypad lock attached to door on exit '{direction}'.")
                audit_channel = get_audit_channel()
                if audit_channel:
                    audit_channel.msg(f"{caller.key} bulk-attached keypad to exit '{direction}'.")
            else:
                caller.msg("Component must be one of: door, lock, keypad.")
                return

class CmdBulkRemove(Command):
    """Bulk remove doors/locks/keypads from multiple exits (builder+ only)."""
    key = "bulkremove"
    locks = "cmd:perm(Builder)"
    help_category = "Building"
    def func(self):
        caller = self.caller
        args = self.args.strip().split()
        if len(args) < 2:
            caller.msg("Usage: bulkremove <component> <direction1> [direction2 ...]")
            return
        component = args[0].lower()
        directions = args[1:]
        for direction in directions:
            exit_obj = caller.location.exits.get(direction)
            if not exit_obj:
                caller.msg(f"No exit found in direction '{direction}'.")
                continue
            if component == "door":
                if not hasattr(exit_obj.db, "door"):
                    caller.msg(f"No door found on exit '{direction}'.")
                    continue
                exit_obj.db.door.delete()
                exit_obj.db.door = None
                caller.msg(f"Door removed from exit '{direction}'.")
                audit_channel = get_audit_channel()
                if audit_channel:
                    audit_channel.msg(f"{caller.key} bulk-removed door from exit '{direction}'.")
            elif component == "lock":
                if not hasattr(exit_obj.db, "door") or not exit_obj.db.door.db.lock:
                    caller.msg(f"No lock found on door for exit '{direction}'.")
                    continue
                exit_obj.db.door.db.lock.delete()
                exit_obj.db.door.db.lock = None
                caller.msg(f"Lock removed from door on exit '{direction}'.")
                audit_channel = get_audit_channel()
                if audit_channel:
                    audit_channel.msg(f"{caller.key} bulk-removed lock from exit '{direction}'.")
            elif component == "keypad":
                if not hasattr(exit_obj.db, "door") or not exit_obj.db.door.db.keypad:
                    caller.msg(f"No keypad found on door for exit '{direction}'.")
                    continue
                exit_obj.db.door.db.keypad.delete()
                exit_obj.db.door.db.keypad = None
                caller.msg(f"Keypad lock removed from door on exit '{direction}'.")
                audit_channel = get_audit_channel()
                if audit_channel:
                    audit_channel.msg(f"{caller.key} bulk-removed keypad from exit '{direction}'.")
            else:
                caller.msg("Component must be one of: door, lock, keypad.")
                return

# Update KeypadLock to support 10-minute cooldown after 5 failed attempts
from typeclasses.doors import KeypadLock
old_enter_combo = KeypadLock.enter_combo

def new_enter_combo(self, combo, caller):
    if not hasattr(self.db, "failed_attempts"):
        self.db.failed_attempts = 0
    if not hasattr(self.db, "cooldown_until"):
        self.db.cooldown_until = 0
    now = time.time()
    if self.db.cooldown_until and now < self.db.cooldown_until:
        remaining = int((self.db.cooldown_until - now) // 60) + 1
        caller.msg(f"|rThe keypad buzzes red. You must wait {remaining} more minute(s) before trying again.|n")
        return False
    if combo == self.db.combination:
        self.db.is_unlocked = True
        self.db.failed_attempts = 0
        self.db.cooldown_until = 0
        caller.msg("Keypad unlocked.")
        audit_channel = get_audit_channel()
        if audit_channel:
            audit_channel.msg(f"{caller.key} unlocked keypad on door.")
        return True
    else:
        self.db.failed_attempts += 1
        caller.msg("Incorrect combination.")
        audit_channel = get_audit_channel()
        if audit_channel:
            audit_channel.msg(f"{caller.key} failed keypad attempt ({self.db.failed_attempts}).")
        if self.db.failed_attempts >= 5:
            self.db.cooldown_until = now + 600  # 10 minutes
            self.db.failed_attempts = 0
            caller.msg("|rThe keypad buzzes red! You must wait 10 minutes before trying again.|n")
            audit_channel = get_audit_channel()
            if audit_channel:
                audit_channel.msg(f"Keypad cooldown triggered by {caller.key} (10 min lockout).")
        return False
KeypadLock.enter_combo = new_enter_combo

# Helpfile cross-linking (add to help/doors.txt)
# ...existing code...

class CmdPushCombo(Command):
    """
    Push a combo on a keypad lock.
    
    Usage:
        push <combo> on <direction>
        press <combo> on <direction>
    """
    key = "push"
    aliases = ["press"]
    locks = "cmd:all()"
    help_category = "General"
    
    def func(self):
        caller = self.caller
        args = self.args.strip().split()
        if len(args) < 3 or args[1] != "on":
            caller.msg("Usage: push <combo> on <direction>")
            return
        combo = args[0]
        direction = args[2].lower()
        
        # Find the exit
        exit_obj = find_exit_by_direction(caller.location, direction)
        if not exit_obj:
            caller.msg(f"No exit found in direction '{direction}'.")
            return
        
        # Check if exit has a door with keypad
        if not getattr(exit_obj.db, "has_door", False):
            caller.msg(f"No door on exit '{exit_obj.key}'.")
            return
        
        keypad_code = getattr(exit_obj.db, "door_keypad_code", None)
        if not keypad_code:
            caller.msg(f"No keypad on door for exit '{exit_obj.key}'.")
            return
        
        # Check the code
        if combo == keypad_code:
            exit_obj.db.door_keypad_unlocked = True
            caller.msg("Keypad unlocked.")
        else:
            caller.msg("Incorrect combination.")

class CmdUnlockExit(Command):
    """Unlock a door or keypad on an exit."""
    key = "unlock"
    locks = "cmd:all()"
    help_category = "General"
    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: unlock <direction> [key]")
            return
        args = self.args.strip().split()
        direction = args[0].lower()
        key_obj = None
        if len(args) > 1:
            key_obj = caller.search(args[1], quiet=True)
            key_obj = key_obj[0] if key_obj else None
        door = find_door(caller.location, direction)
        if not door:
            caller.msg(f"No door found for exit '{direction}'.")
            return
        # Try to unlock lock first
        if hasattr(door.db, "lock") and door.db.lock:
            lock = door.db.lock
            if not lock.db.is_locked:
                caller.msg("The lock is already unlocked.")
                return
            if not key_obj or not hasattr(key_obj.db, "key_id") or key_obj.db.key_id != lock.db.key_id:
                caller.msg("You don't have the correct key.")
                return
            lock.unlock(key_obj, caller)
            door.db.is_locked = False
            caller.msg(lock.db.unlock_msg if hasattr(lock.db, "unlock_msg") else "You unlock the door.")
            audit_channel = get_audit_channel()
            if audit_channel:
                audit_channel.msg(f"{caller.key} unlocked door on exit '{direction}'.")
            return
        # Try to unlock keypad
        if hasattr(door.db, "keypad") and door.db.keypad:
            keypad = door.db.keypad
            if keypad.db.is_unlocked:
                caller.msg("The keypad is already unlocked.")
                return
            keypad.db.is_unlocked = True
            caller.msg("You unlock the keypad lock.")
            audit_channel = get_audit_channel()
            if audit_channel:
                audit_channel.msg(f"{caller.key} unlocked keypad on exit '{direction}'.")
            return
        caller.msg("No lock or keypad found to unlock on exit '{direction}'.")

class CmdLockExit(Command):
    """Lock a door or keypad on an exit."""
    key = "lock"
    locks = "cmd:all()"
    help_category = "General"
    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: lock <direction> [key]")
            return
        args = self.args.strip().split()
        direction = args[0].lower()
        key_obj = None
        if len(args) > 1:
            key_obj = caller.search(args[1], quiet=True)
            key_obj = key_obj[0] if key_obj else None
        door = find_door(caller.location, direction)
        if not door:
            caller.msg(f"No door found for exit '{direction}'.")
            return
        # Try to lock lock first
        if hasattr(door.db, "lock") and door.db.lock:
            lock = door.db.lock
            if lock.db.is_locked:
                caller.msg("The lock is already locked.")
                return
            lock.lock(caller)
            door.db.is_locked = True
            caller.msg(lock.db.lock_msg if hasattr(lock.db, "lock_msg") else "You lock the door.")
            audit_channel = get_audit_channel()
            if audit_channel:
                audit_channel.msg(f"{caller.key} locked door on exit '{direction}'.")
            return
        # Try to lock keypad
        if hasattr(door.db, "keypad") and door.db.keypad:
            keypad = door.db.keypad
            if not keypad.db.is_unlocked:
                caller.msg("The keypad is already locked.")
                return
            keypad.db.is_unlocked = False
            caller.msg("You lock the keypad lock.")
            audit_channel = get_audit_channel()
            if audit_channel:
                audit_channel.msg(f"{caller.key} locked keypad on exit '{direction}'.")

class CmdSetDoorDesc(Command):
    """Set custom description for a door (builder+ only, bidirectional)."""
    key = "setdoordesc"
    locks = "cmd:perm(Builder)"
    help_category = "Building"
    def func(self):
        caller = self.caller
        args = self.args.strip().split(None, 1)
        if len(args) != 2:
            caller.msg("Usage: setdoordesc <direction> <description>")
            return
        direction, desc = args
        direction = direction.strip().lower()
        door = find_door(caller.location, direction)
        if not door:
            caller.msg(f"No door found for exit '{direction}'.")
            return
        door.set_custom_desc(desc, caller)
        audit_channel = get_audit_channel()
        if audit_channel:
            audit_channel.msg(f"{caller.key} set custom desc for door on exit '{direction}'.")
        # Bidirectional: update paired door in destination room
        exit_obj = None
        for ex in getattr(caller.location, "exits", []):
            aliases = [a.lower() for a in (ex.aliases.all() if hasattr(ex.aliases, "all") else [])]
            if ex.key.lower() == direction or direction in aliases:
                exit_obj = ex
                break
        dest_room = getattr(exit_obj, "destination", None) if exit_obj else None
        if dest_room:
            reverse_dir = None
            reverse_map = {
                "north": "south", "south": "north", "east": "west", "west": "east",
                "northeast": "southwest", "southwest": "northeast", "northwest": "southeast", "southeast": "northwest",
                "up": "down", "down": "up", "in": "out", "out": "in"
            }
            reverse_dir = reverse_map.get(direction, None)
            if not reverse_dir:
                for ex in getattr(dest_room, "exits", []):
                    if getattr(ex, "destination", None) == caller.location:
                        reverse_dir = ex.key.lower()
                        break
            rev_door = find_door(dest_room, reverse_dir) if reverse_dir else None
            if rev_door:
                rev_door.set_custom_desc(desc, caller)
                if audit_channel:
                    audit_channel.msg(f"Auto-set custom desc for paired door '{reverse_dir}' in {dest_room.key}.")

class CmdSetDoorShortDesc(Command):
    """Set custom short description for a door (builder+ only, bidirectional)."""
    key = "setdoorshortdesc"
    locks = "cmd:perm(Builder)"
    help_category = "Building"
    def func(self):
        caller = self.caller
        args = self.args.strip().split(None, 1)
        if len(args) != 2:
            caller.msg("Usage: setdoorshortdesc <direction> <shortdesc>")
            return
        direction, shortdesc = args
        direction = direction.strip().lower()
        door = find_door(caller.location, direction)
        if not door:
            caller.msg(f"No door found for exit '{direction}'.")
            return
        door.set_custom_shortdesc(shortdesc, caller)
        audit_channel = get_audit_channel()
        if audit_channel:
            audit_channel.msg(f"{caller.key} set custom shortdesc for door on exit '{direction}'.")
        # Bidirectional: update paired door in destination room
        exit_obj = None
        for ex in getattr(caller.location, "exits", []):
            aliases = [a.lower() for a in (ex.aliases.all() if hasattr(ex.aliases, "all") else [])]
            if ex.key.lower() == direction or direction in aliases:
                exit_obj = ex
                break
        dest_room = getattr(exit_obj, "destination", None) if exit_obj else None
        if dest_room:
            reverse_dir = None
            reverse_map = {
                "north": "south", "south": "north", "east": "west", "west": "east",
                "northeast": "southwest", "southwest": "northeast", "northwest": "southeast", "southeast": "northwest",
                "up": "down", "down": "up", "in": "out", "out": "in"
            }
            reverse_dir = reverse_map.get(direction, None)
            if not reverse_dir:
                for ex in getattr(dest_room, "exits", []):
                    if getattr(ex, "destination", None) == caller.location:
                        reverse_dir = ex.key.lower()
                        break
            rev_door = find_door(dest_room, reverse_dir) if reverse_dir else None
            if rev_door:
                rev_door.set_custom_shortdesc(shortdesc, caller)
                if audit_channel:
                    audit_channel.msg(f"Auto-set custom shortdesc for paired door '{reverse_dir}' in {dest_room.key}.")

class CmdPressLock(Command):
    """Press lock on keypad for an exit."""
    key = "press lock"
    locks = "cmd:all()"
    help_category = "General"
    def func(self):
        caller = self.caller
        args = self.args.strip().split()
        if len(args) != 2 or args[0] != "on":
            caller.msg("Usage: press lock on <direction>")
            return
        direction = args[1].lower()
        exit_obj = find_exit_by_direction(caller.location, direction)
        if not exit_obj or not hasattr(exit_obj.db, "door") or not exit_obj.db.door.db.keypad:
            caller.msg(f"No keypad found on door for exit '{direction}'.")
            return
        keypad = exit_obj.db.door.db.keypad
        if not keypad.db.is_unlocked:
            caller.msg("The keypad is already locked.")
            return
        keypad.db.is_unlocked = False
        caller.msg("You lock the keypad lock.")
        audit_channel = get_audit_channel()
        if audit_channel:
            audit_channel.msg(f"{caller.key} locked keypad on exit '{direction}'.")
