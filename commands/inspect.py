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
        if hasattr(target, "tags"):
            try:
                tags = target.tags.all() if hasattr(target.tags, "all") else target.tags
                if tags:
                    output.append(f"|wTags|n: {', '.join(str(t) for t in tags)}")
            except Exception:
                pass
        
        # Scripts
        if hasattr(target, "scripts"):
            try:
                scripts = target.scripts.all() if hasattr(target.scripts, "all") else target.scripts
                if scripts:
                    script_names = [f"{s.key} ({s.dbref})" for s in scripts]
                    output.append(f"|wScripts|n: {', '.join(script_names)}")
            except Exception:
                pass
        
        # Contents (for rooms/containers)
        if hasattr(target, "contents"):
            try:
                contents = target.contents if isinstance(target.contents, (list, tuple)) else [target.contents]
                if contents:
                    contents_str = [f"{obj.key} ({obj.dbref})" for obj in contents if obj]
                    if contents_str:
                        output.append(f"|wContents|n: {', '.join(contents_str)}")
            except Exception:
                pass
        
        # Exits (for rooms)
        if hasattr(target, "exits"):
            try:
                exits = target.exits if isinstance(target.exits, (list, tuple)) else [target.exits]
                if exits:
                    exits_str = [f"{ex.key} ({ex.dbref})" for ex in exits if ex]
                    if exits_str:
                        output.append(f"|wExits|n: {', '.join(exits_str)}")
            except Exception:
                pass
        
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

