"""
SafetyNet Device Spawning Command

Staff command to easily spawn SafetyNet access devices for players.
Includes wristpads and computer terminals.
"""

from evennia import Command


class CmdSpawnSafetyNetDevice(Command):
    """
    Spawn SafetyNet access devices.
    
    Usage:
        @spawnsn wristpad - Spawn a standard wristpad
        @spawnsn wristpad/deluxe - Spawn a deluxe wristpad
        @spawnsn computer - Spawn a desktop computer terminal
        @spawnsn computer/personal - Spawn a personal portable computer
        @spawnsn computer/portable - Spawn a portable laptop-style computer
    """
    
    key = "@spawnsn"
    locks = "cmd:perm(Builder)"
    help_category = "Builder"
    
    def func(self):
        caller = self.caller
        args = self.args.strip().lower()
        
        if not args:
            caller.msg("Usage: @spawnsn <device_type>")
            caller.msg("  wristpad - Standard wristpad")
            caller.msg("  wristpad/deluxe - Deluxe wristpad")
            caller.msg("  computer - Desktop computer terminal")
            caller.msg("  computer/personal - Personal computer")
            caller.msg("  computer/portable - Portable laptop")
            return
        
        device_type = args.split("/")[0] if "/" in args else args
        variant = args.split("/")[1] if "/" in args else "standard"
        
        if device_type == "wristpad":
            if variant == "deluxe":
                self._spawn_device("wristpad_deluxe", "wristpad (deluxe)")
            else:
                self._spawn_device("wristpad", "wristpad")
                
        elif device_type == "computer":
            if variant == "personal":
                self._spawn_device("computer_personal", "personal computer")
            elif variant == "portable":
                self._spawn_device("portable_computer", "portable computer")
            else:
                self._spawn_device("computer_terminal", "computer terminal")
        else:
            caller.msg(f"Unknown device type: {device_type}")
            return
    
    def _spawn_device(self, prototype, name):
        """Helper to spawn a device from prototype."""
        caller = self.caller
        try:
            from evennia.prototypes.spawner import spawn
            spawned = spawn(prototype)
            
            if not spawned:
                caller.msg(f"Failed to spawn {name}.")
                return
            
            obj = spawned[0]
            obj.location = caller.location
            caller.msg(f"Spawned {name} (#{obj.id}): {obj.get_display_name(caller)}")
            caller.location.msg_contents(f"{caller.name} spawned a {name}.")
            
        except Exception as e:
            caller.msg(f"Error spawning device: {e}")


# Alternative quick-spawn shortcuts

class CmdSpawnWristpad(Command):
    """Quick spawn a wristpad."""
    key = "@wristpad"
    locks = "cmd:perm(Builder)"
    help_category = "Builder"
    
    def func(self):
        try:
            from evennia.prototypes.spawner import spawn
            spawned = spawn("wristpad")
            if spawned:
                obj = spawned[0]
                obj.location = self.caller.location
                self.caller.msg(f"Spawned wristpad (#{obj.id})")
            else:
                self.caller.msg("Failed to spawn wristpad")
        except Exception as e:
            self.caller.msg(f"Error: {e}")


class CmdSpawnComputer(Command):
    """Quick spawn a computer terminal."""
    key = "@computer"
    locks = "cmd:perm(Builder)"
    help_category = "Builder"
    
    def func(self):
        try:
            from evennia.prototypes.spawner import spawn
            spawned = spawn("computer_terminal")
            if spawned:
                obj = spawned[0]
                obj.location = self.caller.location
                self.caller.msg(f"Spawned computer terminal (#{obj.id})")
            else:
                self.caller.msg("Failed to spawn computer")
        except Exception as e:
            self.caller.msg(f"Error: {e}")


class CmdSpawnPortableComputer(Command):
    """Quick spawn a portable computer."""
    key = "@portablecomp"
    locks = "cmd:perm(Builder)"
    help_category = "Builder"
    
    def func(self):
        try:
            from evennia.prototypes.spawner import spawn
            spawned = spawn("portable_computer")
            if spawned:
                obj = spawned[0]
                obj.location = self.caller.location
                self.caller.msg(f"Spawned portable computer (#{obj.id})")
            else:
                self.caller.msg("Failed to spawn portable computer")
        except Exception as e:
            self.caller.msg(f"Error: {e}")
