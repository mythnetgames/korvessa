"""
Admin command to clean up legacy door objects and migrate to exit-based doors.
"""

from evennia import Command
from evennia.objects.models import ObjectDB


class CmdCleanupDoors(Command):
    """
    Clean up legacy door objects from rooms.
    
    Usage:
        @cleanup_doors           - Find and remove all legacy Door objects
        @cleanup_doors validate  - Check for legacy doors without removing
        @cleanup_doors migrate   - Remove legacy doors and attach doors to exits
    
    Legacy Door objects are room contents that should be replaced with
    exit-based doors (door properties stored directly on exits).
    """
    key = "@cleanup_doors"
    aliases = ["@door_cleanup"]
    locks = "cmd:perm(Admin)"
    help_category = "Admin"
    
    def func(self):
        caller = self.caller
        arg = self.args.strip().lower()
        validate_only = arg == "validate"
        migrate_mode = arg == "migrate"
        
        caller.msg("Scanning for legacy door objects...")
        
        removed_count = 0
        migrated_count = 0
        invalid_count = 0
        
        # Get all door objects
        try:
            all_doors = ObjectDB.objects.filter(db_typeclass_path__contains="doors.Door")
        except Exception as e:
            caller.msg(f"Error querying doors: {e}")
            return
        
        for door in all_doors:
            # Check if door is in a valid location
            if not door.location:
                invalid_count += 1
                if validate_only:
                    caller.msg(f"  INVALID: {door.key}({door.dbref}) - no location")
                else:
                    try:
                        caller.msg(f"  REMOVING: {door.key}({door.dbref}) - no location")
                        door.delete()
                        removed_count += 1
                    except Exception as e:
                        caller.msg(f"  ERROR deleting {door.key}({door.dbref}): {e}")
                continue
            
            # Check if door is actually in location.contents
            try:
                if door not in door.location.contents:
                    invalid_count += 1
                    if validate_only:
                        caller.msg(f"  INVALID: {door.key}({door.dbref}) - not in {door.location.key}.contents")
                    else:
                        caller.msg(f"  REMOVING: {door.key}({door.dbref}) - not in location.contents")
                        door.delete()
                        removed_count += 1
                    continue
            except Exception as e:
                caller.msg(f"  ERROR checking contents for {door.key}({door.dbref}): {e}")
                continue
            
            # Get exit direction
            exit_direction = getattr(door.db, "exit_direction", None)
            room = door.location
            
            if validate_only:
                if exit_direction:
                    caller.msg(f"  LEGACY: {door.key}({door.dbref}) in {room.key} - direction '{exit_direction}'")
                else:
                    caller.msg(f"  LEGACY: {door.key}({door.dbref}) in {room.key} - no exit_direction set")
                invalid_count += 1
                continue
            
            if migrate_mode and exit_direction:
                # Find the exit and attach door to it
                exit_obj = None
                for ex in getattr(room, "exits", []):
                    aliases = [a.lower() for a in (ex.aliases.all() if hasattr(ex.aliases, "all") else [])]
                    if ex.key.lower() == exit_direction.lower() or exit_direction.lower() in aliases:
                        exit_obj = ex
                        break
                
                if exit_obj and not getattr(exit_obj.db, "has_door", False):
                    # Migrate door state to exit
                    exit_obj.db.has_door = True
                    exit_obj.db.door_is_open = getattr(door.db, "is_open", False)
                    exit_obj.db.door_is_locked = getattr(door.db, "is_locked", False)
                    exit_obj.db.door_desc = getattr(door.db, "desc", "A sturdy door blocks the way.")
                    
                    # Migrate keypad if present
                    keypad = getattr(door.db, "keypad", None)
                    if keypad:
                        exit_obj.db.door_keypad_code = getattr(keypad.db, "combination", None)
                        exit_obj.db.door_keypad_unlocked = getattr(keypad.db, "is_unlocked", False)
                        keypad.delete()
                    
                    # Migrate lock if present
                    lock = getattr(door.db, "lock", None)
                    if lock:
                        lock.delete()
                    
                    caller.msg(f"  MIGRATED: {door.key}({door.dbref}) -> exit '{exit_obj.key}'")
                    door.delete()
                    migrated_count += 1
                else:
                    caller.msg(f"  REMOVING: {door.key}({door.dbref}) - no matching exit or exit already has door")
                    door.delete()
                    removed_count += 1
            else:
                # Just remove the legacy door
                caller.msg(f"  REMOVING: {door.key}({door.dbref}) in {room.key}")
                
                # Clean up keypad/lock
                keypad = getattr(door.db, "keypad", None)
                if keypad:
                    keypad.delete()
                lock = getattr(door.db, "lock", None)
                if lock:
                    lock.delete()
                    
                door.delete()
                removed_count += 1
        
        if validate_only:
            caller.msg(f"\n|wValidation complete:|n {invalid_count} legacy door(s) found")
            caller.msg("Use '@cleanup_doors' to remove them, or '@cleanup_doors migrate' to migrate to exit-based doors.")
        elif migrate_mode:
            caller.msg(f"\n|wMigration complete:|n {migrated_count} door(s) migrated, {removed_count} door(s) removed")
        else:
            caller.msg(f"\n|wCleanup complete:|n {removed_count} legacy door(s) removed")
