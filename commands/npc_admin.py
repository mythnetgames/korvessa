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
        account = caller.account
        
        # Check if caller is an NPC being puppeted (either via @puppet or built-in puppet)
        if getattr(caller.db, 'is_npc', False):
            # Caller IS an NPC - unpuppet it
            npc_name = caller.key
            
            # If using custom @puppet system, use unpuppet_admin
            if caller.db.puppeted_by:
                success, msg = caller.unpuppet_admin()
                if success:
                    caller.msg(msg)
                else:
                    caller.msg(f"|r{msg}|n")
                return
            
            # Using Evennia's built-in puppet - use @ic to return to main character
            # Find the account's original character (non-NPC)
            original_char = None
            for char in account.characters.all():
                if not getattr(char.db, 'is_npc', False):
                    original_char = char
                    break
            
            if original_char:
                # Get the session - sessions.get() returns a list
                sessions = caller.sessions.get()
                if sessions:
                    session = sessions[0]
                    # Save NPC's current location before unpuppeting
                    npc_location = caller.location
                    npc = caller  # Keep reference to the NPC
                    
                    # Unpuppet the NPC and puppet the original character
                    account.unpuppet_object(session)
                    account.puppet_object(session, original_char)
                    
                    # Ensure the NPC stays in its location
                    if npc_location and npc.location != npc_location:
                        npc.location = npc_location
                    
                    original_char.msg(f"|gYou have released {npc_name}.|n")
                else:
                    caller.msg("|rNo active session found.|n")
            else:
                caller.msg("|rCould not find your original character. Use @ic <character> to return.|n")
            return
        
        # Check if caller is the admin that is puppeting an NPC in this location
        npc_being_puppeted = None
        if caller.location:
            for obj in caller.location.contents:
                if getattr(obj.db, 'is_npc', False) and obj.db.puppeted_by == caller.account:
                    npc_being_puppeted = obj
                    break
        
        if not npc_being_puppeted:
            caller.msg("You are not puppeting an NPC.")
            return
        
        success, msg = npc_being_puppeted.unpuppet_admin()
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


class CmdNPCStat(Command):
    """
    Adjust NPC stats (smarts, body, willpower, dexterity, edge, empathy, reflexes, technique, health, will).
    
    Usage:
      @npc-stat <npc>=<stat>:<value>
      @npc-stat <npc>/info
    
    Examples:
      @npc-stat vendor=smarts:3
      @npc-stat vendor=body:4
      @npc-stat vendor=health:50
      @npc-stat vendor/info
    """
    key = "@npc-stat"
    aliases = ["@npc-stats", "@npcstat"]
    locks = "cmd:perm(Builder)"
    help_category = "Admin"
    
    def func(self):
        """Set NPC stats."""
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: @npc-stat <npc>=<stat>:<value> or @npc-stat <npc>/info")
            return
        
        # Parse arguments
        if "/info" in self.args:
            npc_name = self.args.split("/info")[0].strip()
            show_info = True
            stat = None
            value = None
        elif "=" in self.args:
            npc_name, rest = self.args.split("=", 1)
            npc_name = npc_name.strip()
            show_info = False
            if ":" in rest:
                stat, value = rest.split(":", 1)
                stat = stat.strip().lower()
                try:
                    value = int(value.strip())
                except ValueError:
                    caller.msg("|rStat value must be a number.|n")
                    return
            else:
                caller.msg("Usage: @npc-stat <npc>=<stat>:<value>")
                return
        else:
            caller.msg("Usage: @npc-stat <npc>=<stat>:<value> or @npc-stat <npc>/info")
            return
        
        # Find NPC
        targets = search_object(npc_name)
        if not targets:
            caller.msg(f"NPC '{npc_name}' not found.")
            return
        
        npc = targets[0]
        if not getattr(npc.db, 'is_npc', False):
            caller.msg(f"{npc.key} is not an NPC.")
            return
        
        # Show info
        if show_info:
            caller.msg(f"|c=== Stats for {npc.key} ===|n")
            caller.msg(f"|wSmarts:|n {npc.db.smarts or 1}")
            caller.msg(f"|wBody:|n {npc.db.body or 1}")
            caller.msg(f"|wWillpower:|n {npc.db.willpower or 1}")
            caller.msg(f"|wDexterity:|n {npc.db.dexterity or 1}")
            caller.msg(f"|wEdge:|n {npc.db.edge or 1}")
            caller.msg(f"|wEmpathy:|n {npc.db.empathy or 1}")
            caller.msg(f"|wReflexes:|n {npc.db.reflexes or 1}")
            caller.msg(f"|wTechnique:|n {npc.db.technique or 1}")
            caller.msg(f"|wHealth:|n {npc.db.health or 10}")
            caller.msg(f"|wWill:|n {npc.db.will or 10}")
            return
        
        # Valid stats
        valid_stats = ['smarts', 'body', 'willpower', 'dexterity', 'edge', 'empathy', 'reflexes', 'technique', 'health', 'will']
        if stat not in valid_stats:
            caller.msg(f"|rUnknown stat: {stat}. Valid stats: {', '.join(valid_stats)}|n")
            return
        
        # Set stat
        setattr(npc.db, stat, value)
        caller.msg(f"|gSet {npc.key}'s {stat} to {value}.|n")


class CmdNPCSkill(Command):
    """
    Adjust NPC skills.
    
    Usage:
      @npc-skill <npc>=<skill>:<value>
      @npc-skill <npc>/list
      @npc-skill <npc>/remove=<skill>
    
    Examples:
      @npc-skill vendor=barter:3
      @npc-skill vendor=intimidation:2
      @npc-skill vendor/list
      @npc-skill vendor/remove=barter
    """
    key = "@npc-skill"
    aliases = ["@npc-skills", "@npcskill"]
    locks = "cmd:perm(Builder)"
    help_category = "Admin"
    
    def func(self):
        """Manage NPC skills."""
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: @npc-skill <npc>=<skill>:<value>")
            return
        
        # Parse arguments
        if "/list" in self.args:
            npc_name = self.args.split("/list")[0].strip()
            action = "list"
        elif "/remove=" in self.args:
            parts = self.args.split("/remove=", 1)
            npc_name = parts[0].strip()
            skill = parts[1].strip().lower()
            action = "remove"
        elif "=" in self.args:
            npc_name, rest = self.args.split("=", 1)
            npc_name = npc_name.strip()
            action = "set"
            if ":" in rest:
                skill, value = rest.split(":", 1)
                skill = skill.strip().lower()
                try:
                    value = int(value.strip())
                except ValueError:
                    caller.msg("|rSkill value must be a number.|n")
                    return
            else:
                caller.msg("Usage: @npc-skill <npc>=<skill>:<value>")
                return
        else:
            caller.msg("Usage: @npc-skill <npc>=<skill>:<value>")
            return
        
        # Find NPC
        targets = search_object(npc_name)
        if not targets:
            caller.msg(f"NPC '{npc_name}' not found.")
            return
        
        npc = targets[0]
        if not getattr(npc.db, 'is_npc', False):
            caller.msg(f"{npc.key} is not an NPC.")
            return
        
        # Initialize skills dict if needed
        if not hasattr(npc.db, 'skills') or npc.db.skills is None:
            npc.db.skills = {}
        
        if action == "list":
            if not npc.db.skills:
                caller.msg(f"{npc.key} has no skills configured.")
                return
            caller.msg(f"|c=== Skills for {npc.key} ===|n")
            for skill_name, skill_value in sorted(npc.db.skills.items()):
                caller.msg(f"|w{skill_name}:|n {skill_value}")
        
        elif action == "set":
            npc.db.skills[skill] = value
            caller.msg(f"|gSet {npc.key}'s {skill} skill to {value}.|n")
        
        elif action == "remove":
            if skill in npc.db.skills:
                del npc.db.skills[skill]
                caller.msg(f"|gRemoved {skill} skill from {npc.key}.|n")
            else:
                caller.msg(f"|r{npc.key} doesn't have {skill} skill.|n")


class CmdNPCChrome(Command):
    """
    Manage NPC chrome (implants/cybernetics).
    
    Usage:
      @npc-chrome <npc>=add:<chrome_name>
      @npc-chrome <npc>=remove:<chrome_name>
      @npc-chrome <npc>/list
    
    Examples:
      @npc-chrome guard=add:neural_jack
      @npc-chrome guard=add:reinforced_skeleton
      @npc-chrome guard/list
      @npc-chrome guard=remove:neural_jack
    """
    key = "@npc-chrome"
    aliases = ["@npcchrome", "@npc-implant"]
    locks = "cmd:perm(Builder)"
    help_category = "Admin"
    
    def func(self):
        """Manage NPC chrome."""
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: @npc-chrome <npc>=add:<chrome> or @npc-chrome <npc>/list")
            return
        
        # Parse arguments
        if "/list" in self.args:
            npc_name = self.args.split("/list")[0].strip()
            action = "list"
        elif "=" in self.args:
            npc_name, rest = self.args.split("=", 1)
            npc_name = npc_name.strip()
            if ":" in rest:
                action_type, chrome_name = rest.split(":", 1)
                action_type = action_type.strip().lower()
                chrome_name = chrome_name.strip().lower()
                if action_type not in ['add', 'remove']:
                    caller.msg("Usage: add:<chrome> or remove:<chrome>")
                    return
                action = action_type
            else:
                caller.msg("Usage: @npc-chrome <npc>=add:<chrome> or @npc-chrome <npc>=remove:<chrome>")
                return
        else:
            caller.msg("Usage: @npc-chrome <npc>=add:<chrome>")
            return
        
        # Find NPC
        targets = search_object(npc_name)
        if not targets:
            caller.msg(f"NPC '{npc_name}' not found.")
            return
        
        npc = targets[0]
        if not getattr(npc.db, 'is_npc', False):
            caller.msg(f"{npc.key} is not an NPC.")
            return
        
        # Initialize chrome list if needed
        if not hasattr(npc.db, 'chrome') or npc.db.chrome is None:
            npc.db.chrome = []
        
        if action == "list":
            if not npc.db.chrome:
                caller.msg(f"{npc.key} has no chrome installed.")
                return
            caller.msg(f"|c=== Chrome for {npc.key} ===|n")
            for chrome in npc.db.chrome:
                caller.msg(f"  - {chrome}")
        
        elif action == "add":
            if chrome_name not in npc.db.chrome:
                npc.db.chrome.append(chrome_name)
                caller.msg(f"|gInstalled {chrome_name} on {npc.key}.|n")
            else:
                caller.msg(f"|r{npc.key} already has {chrome_name} installed.|n")
        
        elif action == "remove":
            if chrome_name in npc.db.chrome:
                npc.db.chrome.remove(chrome_name)
                caller.msg(f"|gRemoved {chrome_name} from {npc.key}.|n")
            else:
                caller.msg(f"|r{npc.key} doesn't have {chrome_name} installed.|n")


class CmdNPCNakeds(Command):
    """
    Set NPC body part descriptions (nakeds).
    
    Usage:
      @npc-naked <npc>=<bodypart>:<description>
      @npc-naked <npc>/clear=<bodypart>
      @npc-naked <npc>/info
    
    Examples:
      @npc-naked vendor=torso:A weathered chest with faded scars
      @npc-naked vendor=head:A weather-beaten face with kind eyes
      @npc-naked vendor=info
      @npc-naked vendor/clear=torso
    """
    key = "@npc-naked"
    aliases = ["@npc-nakeds", "@npcnaked"]
    locks = "cmd:perm(Builder)"
    help_category = "Admin"
    
    def func(self):
        """Set NPC nakeds."""
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: @npc-naked <npc>=<bodypart>:<description>")
            return
        
        # Parse arguments
        if "/clear=" in self.args:
            parts = self.args.split("/clear=", 1)
            npc_name = parts[0].strip()
            bodypart = parts[1].strip().lower()
            action = "clear"
        elif "/info" in self.args:
            npc_name = self.args.split("/info")[0].strip()
            action = "info"
        elif "=" in self.args:
            npc_name, rest = self.args.split("=", 1)
            npc_name = npc_name.strip()
            if ":" in rest:
                bodypart, description = rest.split(":", 1)
                bodypart = bodypart.strip().lower()
                description = description.strip()
                action = "set"
            else:
                caller.msg("Usage: @npc-naked <npc>=<bodypart>:<description>")
                return
        else:
            caller.msg("Usage: @npc-naked <npc>=<bodypart>:<description>")
            return
        
        # Find NPC
        targets = search_object(npc_name)
        if not targets:
            caller.msg(f"NPC '{npc_name}' not found.")
            return
        
        npc = targets[0]
        if not getattr(npc.db, 'is_npc', False):
            caller.msg(f"{npc.key} is not an NPC.")
            return
        
        # Initialize nakeds dict if needed
        if not hasattr(npc.db, 'nakeds') or npc.db.nakeds is None:
            npc.db.nakeds = {}
        
        if action == "info":
            if not npc.db.nakeds:
                caller.msg(f"{npc.key} has no custom body part descriptions.")
                return
            caller.msg(f"|c=== Nakeds for {npc.key} ===|n")
            for part, desc in sorted(npc.db.nakeds.items()):
                caller.msg(f"|w{part}:|n {desc}")
        
        elif action == "set":
            npc.db.nakeds[bodypart] = description
            caller.msg(f"|gSet {npc.key}'s {bodypart} description.|n")
        
        elif action == "clear":
            if bodypart in npc.db.nakeds:
                del npc.db.nakeds[bodypart]
                caller.msg(f"|gCleared {bodypart} description for {npc.key}.|n")
            else:
                caller.msg(f"|r{npc.key} doesn't have a custom {bodypart} description.|n")


class CmdNPCGender(Command):
    """
    Set NPC gender.
    
    Usage:
      @npc-gender <npc>=<gender>
      @npc-gender <npc>/info
    
    Valid genders: male, female, neutral
    
    Examples:
      @npc-gender vendor=male
      @npc-gender vendor=female
      @npc-gender vendor=neutral
      @npc-gender vendor/info
    """
    key = "@npc-gender"
    aliases = ["@npcgender"]
    locks = "cmd:perm(Builder)"
    help_category = "Admin"
    
    def func(self):
        """Set NPC gender."""
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: @npc-gender <npc>=<gender> or @npc-gender <npc>/info")
            return
        
        # Parse arguments
        if "/info" in self.args:
            npc_name = self.args.split("/info")[0].strip()
            show_info = True
            gender = None
        elif "=" in self.args:
            npc_name, gender = self.args.split("=", 1)
            npc_name = npc_name.strip()
            gender = gender.strip().lower()
            show_info = False
        else:
            caller.msg("Usage: @npc-gender <npc>=<gender> or @npc-gender <npc>/info")
            return
        
        # Find NPC
        targets = search_object(npc_name)
        if not targets:
            caller.msg(f"NPC '{npc_name}' not found.")
            return
        
        npc = targets[0]
        if not getattr(npc.db, 'is_npc', False):
            caller.msg(f"{npc.key} is not an NPC.")
            return
        
        if show_info:
            current_gender = npc.db.gender or "not set"
            caller.msg(f"|c=== Gender for {npc.key} ===|n")
            caller.msg(f"|wGender:|n {current_gender}")
            return
        
        # Valid genders
        valid_genders = ['male', 'female', 'neutral']
        if gender not in valid_genders:
            caller.msg(f"|rUnknown gender: {gender}. Valid genders: {', '.join(valid_genders)}|n")
            return
        
        # Set gender
        npc.db.gender = gender
        caller.msg(f"|gSet {npc.key}'s gender to {gender}.|n")
