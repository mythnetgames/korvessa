from evennia import Command
from evennia.comms.models import ChannelDB

audit_channel = ChannelDB.objects.get_channel("BuilderAudit")

def find_door(room, direction):
    """Find a door object in the room matching the given direction."""
    direction = direction.lower()
    for obj in room.contents:
        if obj.is_typeclass("typeclasses.doors.Door") and getattr(obj.db, "exit_direction", "").lower() == direction:
            return obj
    return None

class CmdAttachDoor(Command):
    """Attach a door to an exit."""
    key = "attachdoor"
    locks = "cmd:perm(Builder)"
    help_category = "Building"
    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: attachdoor <direction>")
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
        if find_door(caller.location, direction):
            caller.msg(f"A door already exists for exit '{direction}'.")
            return
        from typeclasses.doors import Door
        door = Door()
        door.save()  # Ensure DB id exists before setting attributes
        door.db.exit_direction = direction
        door.location = caller.location
        caller.msg(f"Door attached to exit '{direction}'.")
        audit_channel.msg(f"{caller.key} attached door to exit '{direction}'.")

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
        door.attach_lock(lock)
        caller.msg(f"Lock attached to door for exit '{direction}'.")
        audit_channel.msg(f"{caller.key} attached lock to exit '{direction}'.")

class CmdAttachKeypad(Command):
    """Attach a keypad lock to a door on an exit."""
    key = "attachkeypad"
    locks = "cmd:perm(Builder)"
    help_category = "Building"
    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: attachkeypad <direction>")
            return
        direction = self.args.strip().lower()
        door = find_door(caller.location, direction)
        if not door:
            caller.msg(f"No door found for exit '{direction}'.")
            return
        from typeclasses.doors import KeypadLock
        keypad = KeypadLock()
        keypad.save()  # Ensure DB id exists before setting attributes
        door.attach_keypad(keypad)
        caller.msg(f"Keypad lock attached to door for exit '{direction}'.")
        audit_channel.msg(f"{caller.key} attached keypad to exit '{direction}'.")

class CmdRemoveDoor(Command):
    """Remove a door from an exit."""
    key = "removedoor"
    locks = "cmd:perm(Builder)"
    help_category = "Building"
    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: removedoor <direction>")
            return
        direction = self.args.strip().lower()
        door = find_door(caller.location, direction)
        if not door:
            caller.msg(f"No door found for exit '{direction}'.")
            return
        door.delete()
        caller.msg(f"Door removed from exit '{direction}'.")
        audit_channel.msg(f"{caller.key} removed door from exit '{direction}'.")

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
        audit_channel.msg(f"{caller.key} removed keypad from exit '{direction}'.")

class CmdProgramKeypad(Command):
    """Set the keypad's 8-digit combination."""
    key = "programkeypad"
    locks = "cmd:perm(Builder)"
    help_category = "Building"
    def func(self):
        caller = self.caller
        args = self.args.strip().split()
        if len(args) != 2:
            caller.msg("Usage: programkeypad <direction> <combo>")
            return
        direction, combo = args
        direction = direction.strip().lower()
        door = find_door(caller.location, direction)
        if not door or not door.db.keypad:
            caller.msg(f"No keypad found on door for exit '{direction}'.")
            return
        if len(combo) != 8 or not combo.isdigit():
            caller.msg("Combination must be 8 digits.")
            return
        door.db.keypad.db.combination = combo
        caller.msg(f"Keypad combo for exit '{direction}' set to {combo}.")
        audit_channel.msg(f"{caller.key} programmed keypad combo for exit '{direction}' to {combo}.")

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
        door = find_door(caller.location, direction)
        if not door or not door.db.keypad:
            caller.msg(f"No keypad found on door for exit '{direction}'.")
            return
        caller.msg(f"Keypad combo for exit '{direction}': {door.db.keypad.db.combination}")

class CmdOpenDoor(Command):
    """Open a door on an exit."""
    key = "opendoor"
    locks = "cmd:all()"
    help_category = "General"
    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: opendoor <direction>")
            return
        direction = self.args.strip().lower()
        door = find_door(caller.location, direction)
        if not door:
            caller.msg(f"No door found for exit '{direction}'.")
            return
        if door.db.is_open:
            caller.msg("The door is already open.")
            return
        if door.db.is_locked:
            caller.msg("The door is locked.")
            return
        door.db.is_open = True
        caller.msg(door.db.open_msg if hasattr(door.db, "open_msg") else "You open the door.")
        audit_channel.msg(f"{caller.key} opened door on exit '{direction}'.")

class CmdCloseDoor(Command):
    """Close a door on an exit."""
    key = "closedoor"
    locks = "cmd:all()"
    help_category = "General"
    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: closedoor <direction>")
            return
        direction = self.args.strip().lower()
        door = find_door(caller.location, direction)
        if not door:
            caller.msg(f"No door found for exit '{direction}'.")
            return
        if not door.db.is_open:
            caller.msg("The door is already closed.")
            return
        door.db.is_open = False
        caller.msg(door.db.close_msg if hasattr(door.db, "close_msg") else "You close the door.")
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
        exit_obj = caller.location.exits.get(direction)
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
                audit_channel.msg(f"{caller.key} bulk-removed door from exit '{direction}'.")
            elif component == "lock":
                if not hasattr(exit_obj.db, "door") or not exit_obj.db.door.db.lock:
                    caller.msg(f"No lock found on door for exit '{direction}'.")
                    continue
                exit_obj.db.door.db.lock.delete()
                exit_obj.db.door.db.lock = None
                caller.msg(f"Lock removed from door on exit '{direction}'.")
                audit_channel.msg(f"{caller.key} bulk-removed lock from exit '{direction}'.")
            elif component == "keypad":
                if not hasattr(exit_obj.db, "door") or not exit_obj.db.door.db.keypad:
                    caller.msg(f"No keypad found on door for exit '{direction}'.")
                    continue
                exit_obj.db.door.db.keypad.delete()
                exit_obj.db.door.db.keypad = None
                caller.msg(f"Keypad lock removed from door on exit '{direction}'.")
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
        audit_channel.msg(f"{caller.key} unlocked keypad on door.")
        return True
    else:
        self.db.failed_attempts += 1
        caller.msg("Incorrect combination.")
        audit_channel.msg(f"{caller.key} failed keypad attempt ({self.db.failed_attempts}).")
        if self.db.failed_attempts >= 5:
            self.db.cooldown_until = now + 600  # 10 minutes
            self.db.failed_attempts = 0
            caller.msg("|rThe keypad buzzes red! You must wait 10 minutes before trying again.|n")
            audit_channel.msg(f"Keypad cooldown triggered by {caller.key} (10 min lockout).")
        return False
KeypadLock.enter_combo = new_enter_combo

# Helpfile cross-linking (add to help/doors.txt)
# ...existing code...

class CmdPushCombo(Command):
    """Push a combo on a keypad lock for an exit."""
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
        exit_obj = caller.location.exits.get(direction)
        if not exit_obj or not hasattr(exit_obj.db, "door") or not exit_obj.db.door.db.keypad:
            caller.msg(f"No keypad found on door for exit '{direction}'.")
            return
        keypad = exit_obj.db.door.db.keypad
        keypad.enter_combo(combo, caller)

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
            audit_channel.msg(f"{caller.key} locked keypad on exit '{direction}'.")
            return
        caller.msg("No lock or keypad found to lock on exit '{direction}'.")

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
        exit_obj = caller.location.exits.get(direction)
        if not exit_obj or not hasattr(exit_obj.db, "door") or not exit_obj.db.door.db.keypad:
            caller.msg(f"No keypad found on door for exit '{direction}'.")
            return
        keypad = exit_obj.db.door.db.keypad
        if not keypad.db.is_unlocked:
            caller.msg("The keypad is already locked.")
            return
        keypad.db.is_unlocked = False
        caller.msg("You lock the keypad lock.")
        audit_channel.msg(f"{caller.key} locked keypad on exit '{direction}'.")
