"""
Path Commands

Commands for the auto-walking/pathing system.
Allows players to remember locations, calculate routes, and auto-walk.
"""

from evennia import Command, CmdSet


class CmdPath(Command):
    """
    Auto-walk to saved locations or manage path aliases.
    
    Usage:
        path                     - Show help and current status
        path remember <alias>    - Save current location with an alias
        path forget <alias>      - Remove a saved location
        path list                - List all saved locations
        path go <alias>          - Auto-walk to a saved location
        path go <alias> <mode>   - Auto-walk with movement mode (walk/jog/run/sprint)
        path stop                - Cancel current auto-walk
        path to <room_dbref>     - Auto-walk to a specific room (admin)
    
    Movement Modes:
        walk   - Slow but conserves stamina (default)
        jog    - Moderate speed and stamina use
        run    - Fast but drains stamina quickly
        sprint - Very fast but exhausting
        
    Examples:
        path remember home
        path go home
        path go clinic run
        path stop
    """
    
    key = "path"
    aliases = ["autowalk", "goto"]
    locks = "cmd:all()"
    help_category = "Movement"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            self.show_help()
            return
        
        args = self.args.strip().split()
        subcmd = args[0].lower()
        
        if subcmd == "remember":
            self.do_remember(args[1:])
        elif subcmd == "forget":
            self.do_forget(args[1:])
        elif subcmd == "list":
            self.do_list()
        elif subcmd == "go":
            self.do_go(args[1:])
        elif subcmd == "stop":
            self.do_stop()
        elif subcmd == "to":
            self.do_go_dbref(args[1:])
        elif subcmd == "status":
            self.do_status()
        else:
            caller.msg(f"|rUnknown path command:|n {subcmd}")
            caller.msg("Use |wpath|n for help.")
    
    def show_help(self):
        """Show help and current status."""
        caller = self.caller
        
        caller.msg("|w=== Auto-Walk System ===|n")
        caller.msg("")
        caller.msg("|yCommands:|n")
        caller.msg("  |wpath remember <alias>|n - Save current location")
        caller.msg("  |wpath forget <alias>|n   - Remove a saved location")
        caller.msg("  |wpath list|n             - List saved locations")
        caller.msg("  |wpath go <alias>|n       - Auto-walk to location (uses current movement mode)")
        caller.msg("  |wpath go <alias> <mode>|n - Override mode (walk/jog/run/sprint)")
        caller.msg("  |wpath stop|n             - Cancel auto-walk")
        caller.msg("")
        caller.msg("|yMovement Modes:|n")
        caller.msg("  Auto-walk respects your current movement tier set by: stroll, walk, jog, run, sprint")
        caller.msg("")
        
        # Show current status
        from scripts.auto_walk import is_auto_walking
        if is_auto_walking(caller):
            remaining = len(getattr(caller.ndb, 'auto_walk_path', []))
            dest = getattr(caller.ndb, 'auto_walk_destination', 'unknown')
            mode = getattr(caller.ndb, 'auto_walk_mode', 'walk')
            caller.msg(f"|gCurrently auto-walking:|n {remaining} steps to {dest} ({mode})")
        
        # Show saved locations count
        saved = getattr(caller.db, 'path_locations', {}) or {}
        caller.msg(f"|ySaved locations:|n {len(saved)}")
        if saved:
            caller.msg("  Use |wpath list|n to see them.")
    
    def do_remember(self, args):
        """Save current location with an alias."""
        caller = self.caller
        
        if not args:
            caller.msg("Usage: |wpath remember <alias>|n")
            return
        
        alias = args[0].lower()
        
        if not caller.location:
            caller.msg("|rYou have no location to remember.|n")
            return
        
        # Validate alias
        if not alias.isalnum() and "_" not in alias:
            caller.msg("|rAlias must be alphanumeric (letters, numbers, underscores).|n")
            return
        
        if len(alias) > 20:
            caller.msg("|rAlias too long (max 20 characters).|n")
            return
        
        # Get or create saved locations dict
        saved = getattr(caller.db, 'path_locations', None)
        if saved is None:
            saved = {}
        
        # Check limit (max 20 saved locations)
        if alias not in saved and len(saved) >= 20:
            caller.msg("|rYou have reached the maximum of 20 saved locations.|n")
            caller.msg("Use |wpath forget <alias>|n to remove one first.")
            return
        
        # Save the location
        room_dbref = caller.location.dbref
        saved[alias] = room_dbref
        caller.db.path_locations = saved
        
        caller.msg(f"|gSaved location:|n '{alias}' -> {caller.location.key} ({room_dbref})")
    
    def do_forget(self, args):
        """Remove a saved location."""
        caller = self.caller
        
        if not args:
            caller.msg("Usage: |wpath forget <alias>|n")
            return
        
        alias = args[0].lower()
        
        saved = getattr(caller.db, 'path_locations', {}) or {}
        
        if alias not in saved:
            caller.msg(f"|rNo saved location with alias '{alias}'.|n")
            return
        
        del saved[alias]
        caller.db.path_locations = saved
        
        caller.msg(f"|yRemoved saved location:|n '{alias}'")
    
    def do_list(self):
        """List all saved locations."""
        caller = self.caller
        
        saved = getattr(caller.db, 'path_locations', {}) or {}
        
        if not saved:
            caller.msg("|yNo saved locations.|n")
            caller.msg("Use |wpath remember <alias>|n to save your current location.")
            return
        
        caller.msg("|w=== Saved Locations ===|n")
        
        from evennia import search_object
        
        for alias, dbref in sorted(saved.items()):
            results = search_object(dbref)
            if results:
                room = results[0]
                zone = getattr(room, 'zone', 'unknown')
                caller.msg(f"  |c{alias}|n: {room.key} (zone: {zone})")
            else:
                caller.msg(f"  |c{alias}|n: |r[INVALID - room deleted]|n")
        
        caller.msg(f"|yTotal:|n {len(saved)} location(s)")
    
    def do_go(self, args):
        """Auto-walk to a saved location."""
        caller = self.caller
        
        if not args:
            caller.msg("Usage: |wpath go <alias> [mode]|n")
            caller.msg("Modes: walk, jog, run, sprint")
            return
        
        alias = args[0].lower()
        mode = args[1].lower() if len(args) > 1 else None
        
        # If no mode specified, use character's current movement mode
        if not mode or mode not in ["walk", "jog", "run", "sprint"]:
            # Try to get character's current movement tier from stamina system
            current_mode = None
            try:
                stamina = getattr(caller.ndb, 'stamina', None)
                if stamina and hasattr(stamina, 'current_tier'):
                    from world.stamina import MovementTier, TIER_NAMES
                    tier_name = TIER_NAMES.get(stamina.current_tier, "walk").lower()
                    if tier_name in ["walk", "jog", "run", "sprint", "stroll"]:
                        # Map stroll to walk since our pathing system doesn't have stroll
                        current_mode = tier_name if tier_name != "stroll" else "walk"
            except:
                pass
            
            if current_mode and current_mode in ["walk", "jog", "run", "sprint"]:
                mode = current_mode
            else:
                mode = "walk"  # Default to walk
        
        # Get debug channel
        from evennia.comms.models import ChannelDB
        pathing_channel = None
        try:
            pathing_channel = ChannelDB.objects.get_channel("Pathing")
        except:
            pass
        
        if pathing_channel:
            pathing_channel.msg(f"GO_START: {caller.key} requesting path to '{alias}' (mode: {mode})")
        
        # Validate mode (should always be valid now)
        valid_modes = ["walk", "jog", "run", "sprint"]
        if mode not in valid_modes:
            caller.msg(f"|rInvalid mode '{mode}'.|n Valid modes: {', '.join(valid_modes)}")
            if pathing_channel:
                pathing_channel.msg(f"GO_ERROR: {caller.key} - invalid mode '{mode}'")
            return
        
        # Check for combat
        if hasattr(caller.ndb, 'combat_handler'):
            handler = caller.ndb.combat_handler
            if handler and getattr(handler, 'is_active', False):
                caller.msg("|rCannot auto-walk while in combat!|n")
                if pathing_channel:
                    pathing_channel.msg(f"GO_ERROR: {caller.key} - in combat")
                return
        
        # Validate saved location
        from world.pathfinding import validate_saved_location, find_path
        
        valid, result = validate_saved_location(caller, alias)
        if not valid:
            caller.msg(f"|r{result}|n")
            if pathing_channel:
                pathing_channel.msg(f"GO_ERROR: {caller.key} - invalid location '{alias}': {result}")
            return
        
        dest_room = result
        
        if pathing_channel:
            pathing_channel.msg(f"GO_VALIDATED: {caller.key} -> {dest_room.key} ({dest_room.dbref})")
        
        # Check if already there
        if caller.location == dest_room:
            caller.msg(f"|yYou are already at '{alias}'.|n")
            if pathing_channel:
                pathing_channel.msg(f"GO_ALREADY_HERE: {caller.key} - already at destination")
            return
        
        # Find path
        caller.msg(f"|yCalculating route to '{alias}'...|n")
        
        if pathing_channel:
            pathing_channel.msg(f"GO_PATHFIND: {caller.key} finding path from {caller.location.dbref} to {dest_room.dbref}")
        
        path = find_path(caller.location, dest_room, caller)
        
        if pathing_channel:
            if path:
                pathing_channel.msg(f"GO_PATH_FOUND: {caller.key} - {len(path)} steps")
            else:
                pathing_channel.msg(f"GO_PATH_FAILED: {caller.key} - no path found")
        
        if path is None:
            caller.msg(f"|rNo path found to '{alias}'.|n The destination may be unreachable.")
            return
        
        if not path:
            caller.msg(f"|yYou are already at '{alias}'.|n")
            return
        
        # Check stamina for the journey
        from world.pathfinding import estimate_path_stamina_cost
        stamina_cost = estimate_path_stamina_cost(path, mode)
        
        stamina = getattr(caller.ndb, 'stamina', None)
        if stamina:
            if stamina.stamina_current < stamina_cost:
                caller.msg(f"|yWarning:|n Estimated stamina cost ({stamina_cost:.0f}) exceeds current stamina ({stamina.stamina_current:.0f}).")
                caller.msg("You may run out of stamina before arriving. Consider walking instead.")
        
        # Start auto-walk
        from scripts.auto_walk import start_auto_walk
        
        if pathing_channel:
            pathing_channel.msg(f"GO_STARTING: {caller.key} - starting auto-walk with {len(path)} steps")
        
        if start_auto_walk(caller, path, mode, alias):
            # Message is sent by the script
            if pathing_channel:
                pathing_channel.msg(f"GO_STARTED: {caller.key} - auto-walk initiated")
        else:
            caller.msg("|rFailed to start auto-walk.|n")
            if pathing_channel:
                pathing_channel.msg(f"GO_FAILED: {caller.key} - failed to start auto-walk")
    
    def do_go_dbref(self, args):
        """Auto-walk to a specific room by dbref (admin command)."""
        caller = self.caller
        
        # Check permissions
        if not caller.account.is_staff and not caller.account.is_superuser:
            caller.msg("|rThis command requires staff permissions.|n")
            return
        
        if not args:
            caller.msg("Usage: |wpath to <room_dbref> [mode]|n")
            return
        
        dbref = args[0]
        mode = args[1].lower() if len(args) > 1 else "walk"
        
        # Find the room
        from evennia import search_object
        results = search_object(dbref)
        
        if not results:
            caller.msg(f"|rRoom '{dbref}' not found.|n")
            return
        
        dest_room = results[0]
        
        if not hasattr(dest_room, 'exits'):
            caller.msg(f"|r'{dbref}' is not a room.|n")
            return
        
        # Find path
        from world.pathfinding import find_path
        
        caller.msg(f"|yCalculating route to {dest_room.key}...|n")
        
        path = find_path(caller.location, dest_room, caller)
        
        if path is None:
            caller.msg(f"|rNo path found to {dest_room.key}.|n")
            return
        
        if not path:
            caller.msg(f"|yYou are already there.|n")
            return
        
        # Start auto-walk
        from scripts.auto_walk import start_auto_walk
        
        if start_auto_walk(caller, path, mode, dest_room.key):
            pass
        else:
            caller.msg("|rFailed to start auto-walk.|n")
    
    def do_stop(self):
        """Cancel current auto-walk."""
        caller = self.caller
        
        from scripts.auto_walk import cancel_auto_walk, is_auto_walking
        
        if not is_auto_walking(caller):
            caller.msg("|yYou are not currently auto-walking.|n")
            return
        
        cancel_auto_walk(caller)
        # Message is sent by cancel_auto_walk
    
    def do_status(self):
        """Show detailed auto-walk status."""
        caller = self.caller
        
        from scripts.auto_walk import is_auto_walking
        
        if not is_auto_walking(caller):
            caller.msg("|yNot currently auto-walking.|n")
            return
        
        path = getattr(caller.ndb, 'auto_walk_path', [])
        dest = getattr(caller.ndb, 'auto_walk_destination', 'unknown')
        mode = getattr(caller.ndb, 'auto_walk_mode', 'walk')
        
        caller.msg(f"|w=== Auto-Walk Status ===|n")
        caller.msg(f"Destination: |c{dest}|n")
        caller.msg(f"Mode: |w{mode}|n")
        caller.msg(f"Remaining steps: |y{len(path)}|n")
        
        if path:
            # Show next few directions
            next_dirs = [exit_obj.key for exit_obj, _ in path[:5]]
            caller.msg(f"Next directions: {' -> '.join(next_dirs)}{'...' if len(path) > 5 else ''}")


class PathCmdSet(CmdSet):
    """Command set for pathing commands."""
    
    key = "path_cmdset"
    
    def at_cmdset_creation(self):
        self.add(CmdPath())
