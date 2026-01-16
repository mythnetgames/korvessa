"""
Inspect command - shows detailed information about objects for builders.
"""

from evennia import Command
from evennia.utils.utils import crop


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
        if hasattr(target, "aliases") and target.aliases:
            try:
                alias_list = target.aliases.all() if hasattr(target.aliases, "all") else target.aliases
                if alias_list:
                    output.append(f"|wAliases|n: {', '.join(str(a) for a in alias_list)}")
            except Exception:
                pass
        
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
            try:
                perms = target.permissions.all() if hasattr(target.permissions, "all") else target.permissions
                if perms:
                    output.append(f"|wPermissions|n: {', '.join(str(p) for p in perms)}")
            except Exception:
                pass
        
        # Locks - show nicely formatted on multiple lines
        if hasattr(target, "locks"):
            try:
                locks_str = str(target.locks)
                if locks_str and locks_str != "Default":
                    locks_list = [lock.strip() for lock in locks_str.split(";")]
                    output.append(f"|wLocks|n:")
                    for lock in locks_list:
                        output.append(f"  {lock}")
                else:
                    output.append(f"|wLocks|n: Default")
            except Exception:
                pass
        
        # Tags
        if hasattr(target, "tags"):
            try:
                tags = target.tags.all() if hasattr(target.tags, "all") else target.tags
                if tags:
                    tag_strs = []
                    for t in tags:
                        if hasattr(t, "db_category") and t.db_category:
                            tag_strs.append(f"{t.db_key}[{t.db_category}]")
                        else:
                            tag_strs.append(str(t))
                    if tag_strs:
                        output.append(f"|wTags|n: {', '.join(tag_strs)}")
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
        
        # Contents (for rooms/containers) - nicely formatted
        if hasattr(target, "contents"):
            try:
                contents = target.contents if isinstance(target.contents, (list, tuple)) else [target.contents]
                if contents:
                    contents_str = [f"{obj.key} ({obj.dbref})" for obj in contents if obj]
                    if contents_str:
                        # Format contents on multiple lines if there are many
                        if len(contents_str) > 3:
                            output.append(f"|wContents|n:")
                            for i in range(0, len(contents_str), 3):
                                output.append("  " + ", ".join(contents_str[i:i+3]))
                        else:
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
        
        # Persistent Attributes - organized display
        if hasattr(target, "db_attributes"):
            try:
                attrs_list = target.db_attributes.all()
                if attrs_list:
                    output.append(f"|wPersistent Attributes|n:")
                    for attr in attrs_list[:30]:  # Limit to 30 attributes
                        try:
                            value_str = str(attr.value)
                            if len(value_str) > 60:
                                value_str = value_str[:60] + "..."
                            if attr.db_category:
                                output.append(f"  {attr.db_key}[{attr.db_category}] = {value_str}")
                            else:
                                output.append(f"  {attr.db_key} = {value_str}")
                        except Exception:
                            pass
                    if len(attrs_list) > 30:
                        output.append(f"  ... and {len(attrs_list) - 30} more attributes")
            except Exception:
                pass
        
        output.append(sep)
        
        caller.msg("\n".join(output))

