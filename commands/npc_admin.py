"""
Admin commands for creating and managing NPCs.
"""

from evennia import Command, search_object, create_object


class CmdCreateNPC(Command):
    """
    Create a new NPC.
    
    Usage:
      @create-npc <name>
      @create-npc <name>=<description>
    
    Examples:
      @create-npc street vendor=A weathered merchant selling street food.
      @create-npc gang member
    """
    key = "@create-npc"
    aliases = ["@createnpc", "@npc-create"]
    locks = "cmd:perm(Admin)"
    help_category = "Admin"
    
    def func(self):
        """Create a new NPC."""
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: @create-npc <name> or @create-npc <name>=<description>")
            return
        
        # Parse name and description
        if "=" in self.args:
            name, desc = self.args.split("=", 1)
            name = name.strip()
            desc = desc.strip()
        else:
            name = self.args.strip()
            desc = ""
        
        if not name:
            caller.msg("You must provide an NPC name.")
            return
        
        # Create the NPC
        npc = create_object(
            "typeclasses.npcs.NPC",
            key=name,
            location=caller.location,
            home=caller.location
        )
        
        if desc:
            npc.db.desc = desc
        else:
            npc.db.desc = f"An NPC named {name}."
        
        caller.msg(f"|gCreated NPC: {npc.key} (#{npc.id})|n")
        caller.location.msg_contents(f"{caller.key} has created {npc.key}.")


class CmdNPCPuppet(Command):
    """
    Puppet an NPC (take control of it).
    
    Usage:
      @puppet <npc>
      @npc puppet <npc>
    """
    key = "@puppet"
    aliases = ["@npc-puppet"]
    locks = "cmd:perm(Admin)"
    help_category = "Admin"
    
    def func(self):
        """Puppet an NPC."""
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: @puppet <npc>")
            return
        
        # Find the NPC
        targets = search_object(self.args)
        if not targets:
            caller.msg(f"NPC '{self.args}' not found.")
            return
        
        npc = targets[0]
        
        # Check if it's actually an NPC
        if not getattr(npc.db, 'is_npc', False):
            caller.msg(f"{npc.key} is not an NPC.")
            return
        
        # Try to puppet it
        success, msg = npc.puppet_admin(caller.account)
        if success:
            caller.msg(msg)
            caller.location.msg_contents(f"{caller.key} begins puppeting {npc.key}.")
        else:
            caller.msg(f"|r{msg}|n")


class CmdNPCUnpuppet(Command):
    """
    Stop puppeting an NPC and return to your admin shell.
    
    Usage:
      @unpuppet
      @npc unpuppet
    """
    key = "@unpuppet"
    aliases = ["@npc-unpuppet"]
    locks = "cmd:perm(Admin)"
    help_category = "Admin"
    
    def func(self):
        """Unpuppet the current NPC."""
        caller = self.caller
        
        # Check if caller is an NPC and is being puppeted
        if not getattr(caller.db, 'is_npc', False):
            caller.msg("You are not puppeting an NPC.")
            return
        
        success, msg = caller.unpuppet_admin()
        if success:
            caller.msg(msg)
        else:
            caller.msg(f"|r{msg}|n")


class CmdNPCReaction(Command):
    """
    Add a reaction to an NPC.
    
    Usage:
      @npc-react <npc>=<trigger>/<action>
      @npc-react <npc>/remove=<trigger>
      @npc-react <npc>/list
    
    Examples:
      @npc-react street vendor=hello/say Hey there, friend!
      @npc-react street vendor=greetings/emote smiles warmly
      @npc-react street vendor/list
    """
    key = "@npc-react"
    aliases = ["@npc-reaction", "@npcreact"]
    locks = "cmd:perm(Builder)"
    help_category = "Admin"
    
    def parse(self):
        """Parse the command."""
        self.npc_name = None
        self.sub_cmd = None
        self.trigger = None
        self.action = None
        
        if not self.args:
            return
        
        # Check for sub-commands
        if "/remove" in self.args:
            parts = self.args.split("/remove", 1)
            self.npc_name = parts[0].strip()
            if "=" in parts[1]:
                _, self.trigger = parts[1].split("=", 1)
                self.trigger = self.trigger.strip()
            self.sub_cmd = "remove"
        elif "/list" in self.args:
            self.npc_name = self.args.split("/list")[0].strip()
            self.sub_cmd = "list"
        elif "=" in self.args:
            npc_part, rest = self.args.split("=", 1)
            self.npc_name = npc_part.strip()
            if "/" in rest:
                self.trigger, self.action = rest.split("/", 1)
                self.trigger = self.trigger.strip()
                self.action = self.action.strip()
            self.sub_cmd = "add"
    
    def func(self):
        """Execute the reaction command."""
        caller = self.caller
        
        if not self.npc_name:
            caller.msg("Usage: @npc-react <npc>=<trigger>/<action>")
            return
        
        # Find the NPC
        targets = search_object(self.npc_name)
        if not targets:
            caller.msg(f"NPC '{self.npc_name}' not found.")
            return
        
        npc = targets[0]
        
        # Check if it's an NPC
        if not getattr(npc.db, 'is_npc', False):
            caller.msg(f"{npc.key} is not an NPC.")
            return
        
        if self.sub_cmd == "add":
            if not self.trigger or not self.action:
                caller.msg("Usage: @npc-react <npc>=<trigger>/<action>")
                return
            
            npc.add_reaction(self.trigger, self.action)
            caller.msg(f"|gAdded reaction to {npc.key}: '{self.trigger}' -> '{self.action}|n'")
        
        elif self.sub_cmd == "remove":
            if not self.trigger:
                caller.msg("Usage: @npc-react <npc>/remove=<trigger>")
                return
            
            if npc.remove_reaction(self.trigger):
                caller.msg(f"|gRemoved reactions for '{self.trigger}' from {npc.key}.|n")
            else:
                caller.msg(f"|rNo reactions found for '{self.trigger}'.|n")
        
        elif self.sub_cmd == "list":
            reactions = npc.db.npc_reactions or {}
            if not reactions:
                caller.msg(f"{npc.key} has no reactions configured.")
                return
            
            caller.msg(f"|c=== Reactions for {npc.key} ===|n")
            for trigger, actions in sorted(reactions.items()):
                caller.msg(f"|w{trigger}:|n")
                for action in actions:
                    caller.msg(f"  - {action}")


class CmdNPCConfig(Command):
    """
    Configure NPC properties.
    
    Usage:
      @npc-config <npc>=wander:<yes/no>
      @npc-config <npc>=zone:<zone_name>
      @npc-config <npc>=accent:<accent_name>
      @npc-config <npc>/info
    
    Examples:
      @npc-config street vendor=wander:yes
      @npc-config street vendor=zone:market
      @npc-config street vendor=accent:thick_accent
      @npc-config street vendor/info
    """
    key = "@npc-config"
    aliases = ["@npcconfig"]
    locks = "cmd:perm(Builder)"
    help_category = "Admin"
    
    def func(self):
        """Configure NPC settings."""
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: @npc-config <npc>=<setting>:<value>")
            return
        
        # Parse arguments
        if "/info" in self.args:
            npc_name = self.args.split("/info")[0].strip()
            setting = "info"
            value = None
        elif "=" in self.args:
            npc_name, rest = self.args.split("=", 1)
            npc_name = npc_name.strip()
            if ":" in rest:
                setting, value = rest.split(":", 1)
                setting = setting.strip().lower()
                value = value.strip()
            else:
                caller.msg("Usage: @npc-config <npc>=<setting>:<value>")
                return
        else:
            caller.msg("Usage: @npc-config <npc>=<setting>:<value>")
            return
        
        # Find the NPC
        targets = search_object(npc_name)
        if not targets:
            caller.msg(f"NPC '{npc_name}' not found.")
            return
        
        npc = targets[0]
        
        # Check if it's an NPC
        if not getattr(npc.db, 'is_npc', False):
            caller.msg(f"{npc.key} is not an NPC.")
            return
        
        # Handle settings
        if setting == "info":
            caller.msg(f"|c=== Configuration for {npc.key} ===|n")
            caller.msg(f"|wCan Wander:|n {npc.db.npc_can_wander}")
            caller.msg(f"|wZone:|n {npc.db.npc_zone or 'None'}")
            caller.msg(f"|wAccent:|n {npc.db.npc_accent or 'None'}")
            caller.msg(f"|wBeing Puppeted:|n {npc.is_puppeted()}")
        
        elif setting == "wander":
            value_bool = value.lower() in ('yes', 'true', '1', 'on')
            npc.db.npc_can_wander = value_bool
            caller.msg(f"|gSet {npc.key} wandering to: {value_bool}|n")
        
        elif setting == "zone":
            npc.set_zone(value)
            caller.msg(f"|gSet {npc.key} zone to: {value}|n")
        
        elif setting == "accent":
            npc.set_accent(value)
            caller.msg(f"|gSet {npc.key} accent to: {value}|n")
        
        else:
            caller.msg(f"|rUnknown setting: {setting}|n")
