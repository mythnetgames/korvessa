"""
Inspect command - shows detailed information about objects for builders.
"""

from evennia import Command


class CmdInspect(Command):
    """
    Inspect detailed information about an object, room, or character.
    
    Usage:
        inspect [<object>]
    
    Shows detailed game info about an object including its attributes,
    scripts, permissions, and other technical details. If no argument
    is given, the current location is inspected.
    
    This is a builder command for debugging and development.
    """
    
    key = "inspect"
    aliases = ["insp"]
    locks = "cmd:perm(Builder)"
    help_category = "Building"
    
    def func(self):
        """Execute the inspect command."""
        caller = self.caller
        
        # Determine target
        if not self.args:
            target = caller.location
            if not target:
                caller.msg("You have no location to inspect.")
                return
        else:
            target = caller.search(self.args.strip())
            if not target:
                return  # search handles error message
        
        # Build inspection output
        output = []
        sep = "-" * 60
        output.append(sep)
        
        # Basic info
        output.append(f"|wName/key|n: {target.key} ({target.dbref})")
        
        # Aliases
        if hasattr(target, "aliases") and target.aliases.all():
            output.append(f"|wAliases|n: {', '.join(target.aliases.all())}")
        
        # Typeclass
        if hasattr(target, "typeclass_path"):
            output.append(f"|wTypeclass|n: {target.typename} ({target.typeclass_path})")
        
        # Location
        if hasattr(target, "location") and target.location:
            output.append(f"|wLocation|n: {target.location.key} ({target.location.dbref})")
        
        # Home
        if hasattr(target, "home") and target.home:
            output.append(f"|wHome|n: {target.home.key} ({target.home.dbref})")
        
        # Destination (for exits)
        if hasattr(target, "destination") and target.destination:
            output.append(f"|wDestination|n: {target.destination.key} ({target.destination.dbref})")
        
        # Permissions
        if hasattr(target, "permissions"):
            perms = target.permissions.all()
            if perms:
                output.append(f"|wPermissions|n: {', '.join(perms)}")
        
        # Locks
        if hasattr(target, "locks"):
            locks_str = str(target.locks)
            if locks_str:
                output.append(f"|wLocks|n: {locks_str}")
        
        # Tags
        if hasattr(target, "tags") and target.tags.all():
            tags = target.tags.all()
            output.append(f"|wTags|n: {', '.join(str(t) for t in tags)}")
        
        # Scripts
        if hasattr(target, "scripts") and target.scripts.all():
            scripts = target.scripts.all()
            script_names = [f"{s.key} ({s.dbref})" for s in scripts]
            output.append(f"|wScripts|n: {', '.join(script_names)}")
        
        # Contents (for rooms/containers)
        if hasattr(target, "contents") and target.contents:
            contents = [f"{obj.key} ({obj.dbref})" for obj in target.contents]
            output.append(f"|wContents|n: {', '.join(contents)}")
        
        # Exits (for rooms)
        if hasattr(target, "exits") and target.exits:
            exits = [f"{ex.key} ({ex.dbref})" for ex in target.exits]
            output.append(f"|wExits|n: {', '.join(exits)}")
        
        # Persistent Attributes
        if hasattr(target, "db") and hasattr(target.db, "all"):
            attrs = []
            for key, value in target.db.all().items():
                value_str = str(value)
                if len(value_str) > 50:
                    value_str = value_str[:50] + "..."
                attrs.append(f"  {key} = {value_str}")
            if attrs:
                output.append("|wPersistent Attributes|n:")
                output.extend(attrs[:20])  # Limit to 20 attributes
                if len(attrs) > 20:
                    output.append(f"  ... and {len(attrs) - 20} more")
        
        output.append(sep)
        
        caller.msg("\n".join(output))

