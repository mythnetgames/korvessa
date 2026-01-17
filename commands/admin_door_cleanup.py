"""
Admin command to clean up stale door references.
"""

from evennia import Command
from evennia.objects.models import ObjectDB


class CmdCleanupDoors(Command):
    """
    Clean up stale or orphaned door objects from rooms.
    
    Usage:
        @cleanup_doors           - Find and remove invalid doors
        @cleanup_doors validate  - Check for stale door references without removing
    """
    key = "@cleanup_doors"
    aliases = ["@door_cleanup"]
    locks = "cmd:perm(Admin)"
    help_category = "Admin"
    
    def func(self):
        caller = self.caller
        arg = self.args.strip().lower()
        validate_only = arg == "validate"
        
        caller.msg("Scanning for stale door objects...")
        
        removed_count = 0
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
            
            # Check if exit_direction field exists and is valid
            exit_direction = getattr(door.db, "exit_direction", None)
            if not exit_direction:
                invalid_count += 1
                if validate_only:
                    caller.msg(f"  INVALID: {door.key}({door.dbref}) in {door.location.key} - no exit_direction")
                else:
                    caller.msg(f"  REMOVING: {door.key}({door.dbref}) - no exit_direction set")
                    door.delete()
                    removed_count += 1
                continue
            
            # Check if the exit still exists
            exit_obj = None
            try:
                # Search for exit by direction in the room
                for exit in door.location.exits:
                    if exit and exit.key.lower() == exit_direction.lower():
                        exit_obj = exit
                        break
            except Exception as e:
                caller.msg(f"  ERROR checking exits for {door.key}({door.dbref}): {e}")
                continue
            
            if not exit_obj:
                # Exit doesn't exist anymore - orphaned door
                invalid_count += 1
                if validate_only:
                    caller.msg(f"  INVALID: {door.key}({door.dbref}) in {door.location.key} - exit '{exit_direction}' does not exist")
                else:
                    caller.msg(f"  REMOVING: {door.key}({door.dbref}) - exit '{exit_direction}' was deleted")
                    door.delete()
                    removed_count += 1
        
        if validate_only:
            caller.msg(f"\n|wValidation complete:|n {invalid_count} invalid door(s) found")
        else:
            caller.msg(f"\n|wCleanup complete:|n {removed_count} door(s) removed, {invalid_count} invalid door(s) found")
