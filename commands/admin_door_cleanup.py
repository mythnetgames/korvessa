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
        from typeclasses.doors import Door
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
                        door.delete()
                        removed_count += 1
                        caller.msg(f"  REMOVED: {door.key}({door.dbref}) - no location")
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
                        try:
                            door.delete()
                            removed_count += 1
                            caller.msg(f"  REMOVED: {door.key}({door.dbref}) - not in location.contents")
                        except Exception as e:
                            caller.msg(f"  ERROR deleting {door.key}({door.dbref}): {e}")
                    continue
            except Exception as e:
                caller.msg(f"  ERROR checking contents for {door.key}({door.dbref}): {e}")
                continue
            
            # Check if exit_direction field exists and is valid
            exit_direction = getattr(door.db, "exit_direction", None)
            if not exit_direction:
                # Door might not be attached to an exit
                caller.msg(f"  INFO: {door.key}({door.dbref}) in {door.location.key} - no exit_direction set")
                continue
        
        if validate_only:
            caller.msg(f"\n|wValidation complete:|n {invalid_count} invalid door(s) found")
        else:
            caller.msg(f"\n|wCleanup complete:|n {removed_count} door(s) removed, {invalid_count} invalid door(s) found")
