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
    Adjust NPC stats (smarts, body, willpower, dexterity, edge, empathy, reflexes, technique).
    
    Usage:
      @npc-stat <npc>=<stat>:<value>
      @npc-stat <npc>/info
    
    Stats use abbreviated internal names:
      smarts -> smrt, willpower -> will, reflexes -> ref
      dexterity -> dex, empathy -> emp, technique -> tech
      body and edge stay the same
    
    Examples:
      @npc-stat vendor=smarts:3
      @npc-stat vendor=body:4
      @npc-stat vendor/info
    """
    key = "@npc-stat"
    aliases = ["@npc-stats", "@npcstat"]
    locks = "cmd:perm(Builder)"
    help_category = "Admin"
    
    # Map user-friendly stat names to internal attribute names
    STAT_MAP = {
        'smarts': 'smrt',
        'smrt': 'smrt',
        'body': 'body',
        'willpower': 'will',
        'will': 'will',
        'dexterity': 'dex',
        'dex': 'dex',
        'edge': 'edge',
        'empathy': '_emp',  # Override the calculated empathy
        'emp': '_emp',
        'reflexes': 'ref',
        'ref': 'ref',
        'technique': 'tech',
        'tech': 'tech',
    }
    
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
            caller.msg(f"|wSmarts:|n {getattr(npc, 'smrt', 1)}")
            caller.msg(f"|wBody:|n {getattr(npc, 'body', 1)}")
            caller.msg(f"|wWillpower:|n {getattr(npc, 'will', 1)}")
            caller.msg(f"|wDexterity:|n {getattr(npc, 'dex', 1)}")
            caller.msg(f"|wEdge:|n {getattr(npc, 'edge', 1)}")
            emp_override = getattr(npc, '_emp', None)
            emp_val = getattr(npc, 'emp', 1)
            if emp_override is not None:
                caller.msg(f"|wEmpathy:|n {emp_val} |y(override)|n")
            else:
                caller.msg(f"|wEmpathy:|n {emp_val} |c(calculated from edge+will)|n")
            caller.msg(f"|wReflexes:|n {getattr(npc, 'ref', 1)}")
            caller.msg(f"|wTechnique:|n {getattr(npc, 'tech', 1)}")
            return
        
        # Validate and map stat name
        if stat not in self.STAT_MAP:
            valid_names = ['smarts', 'body', 'willpower', 'dexterity', 'edge', 'empathy', 'reflexes', 'technique']
            caller.msg(f"|rUnknown stat: {stat}. Valid stats: {', '.join(valid_names)}|n")
            return
        
        internal_stat = self.STAT_MAP[stat]
        
        # Set stat using setattr on the object (not db)
        setattr(npc, internal_stat, value)
        caller.msg(f"|gSet {npc.key}'s {stat} to {value}.|n")


class CmdNPCSkill(Command):
    """
    Adjust NPC skills.
    
    Usage:
      @npc-skill <npc>=<skill>:<value>
      @npc-skill <npc>/list
      @npc-skill <npc>/remove=<skill>
    
    Valid skills:
      chemical, modern medicine, holistic medicine, surgery, science,
      dodge, blades, pistols, rifles, melee, brawling, martial arts,
      grappling, snooping, stealing, hiding, sneaking, disguise,
      tailoring, tinkering, manufacturing, cooking, forensics,
      decking, electronics, mercantile, streetwise, paint/draw/sculpt, instrument
    
    Examples:
      @npc-skill vendor=mercantile:5
      @npc-skill guard=martial arts:8
      @npc-skill vendor/list
      @npc-skill vendor/remove=mercantile
    """
    key = "@npc-skill"
    aliases = ["@npc-skills", "@npcskill"]
    locks = "cmd:perm(Builder)"
    help_category = "Admin"
    
    # Valid skill names (display name -> attribute name)
    VALID_SKILLS = [
        "chemical", "modern medicine", "holistic medicine", "surgery", "science",
        "dodge", "blades", "pistols", "rifles", "melee", "brawling", "martial arts",
        "grappling", "snooping", "stealing", "hiding", "sneaking", "disguise",
        "tailoring", "tinkering", "manufacturing", "cooking", "forensics",
        "decking", "electronics", "mercantile", "streetwise", "paint/draw/sculpt", "instrument"
    ]
    
    def skill_to_attr(self, skill_name):
        """Convert skill display name to attribute name."""
        return skill_name.lower().replace("/", "_")
    
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
            skill = None
            value = None
        elif "/remove=" in self.args:
            parts = self.args.split("/remove=", 1)
            npc_name = parts[0].strip()
            skill = parts[1].strip().lower()
            action = "remove"
            value = None
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
        
        if action == "list":
            caller.msg(f"|c=== Skills for {npc.key} ===|n")
            for skill_name in self.VALID_SKILLS:
                attr_name = self.skill_to_attr(skill_name)
                skill_value = getattr(npc, attr_name, 0)
                if skill_value > 0:
                    caller.msg(f"|w{skill_name.title()}:|n {skill_value}")
        
        elif action == "set":
            # Validate skill name
            if skill not in self.VALID_SKILLS:
                caller.msg(f"|rUnknown skill: {skill}|n")
                caller.msg(f"|yValid skills:|n {', '.join(self.VALID_SKILLS)}")
                return
            
            attr_name = self.skill_to_attr(skill)
            setattr(npc, attr_name, value)
            caller.msg(f"|gSet {npc.key}'s {skill} skill to {value}.|n")
        
        elif action == "remove":
            # Validate skill name
            if skill not in self.VALID_SKILLS:
                caller.msg(f"|rUnknown skill: {skill}|n")
                return
            
            attr_name = self.skill_to_attr(skill)
            setattr(npc, attr_name, 0)
            caller.msg(f"|gReset {npc.key}'s {skill} skill to 0.|n")


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


class CmdForceWander(Command):
    """
    Force NPCs to wander immediately for testing.
    
    Usage:
      forcewander                - Force all wandering NPCs to move
      forcewander <npc>          - Force specific NPC to wander
      forcewander status         - Show wandering status of all NPCs
      forcewander enable <npc>   - Enable wandering for an NPC
      forcewander disable <npc>  - Disable wandering for an NPC
    
    Examples:
      forcewander
      forcewander street vendor
      forcewander status
      forcewander enable gang member
    """
    key = "forcewander"
    locks = "cmd:perm(Builder)"
    help_category = "Admin"
    
    def func(self):
        """Force NPCs to wander."""
        caller = self.caller
        
        if not self.args:
            # Force all wandering NPCs to move
            self._force_all_wander(caller)
            return
        
        args = self.args.strip().lower()
        
        if args == "status":
            self._show_status(caller)
            return
        
        if args.startswith("enable "):
            npc_name = self.args[7:].strip()
            self._enable_wandering(caller, npc_name)
            return
        
        if args.startswith("disable "):
            npc_name = self.args[8:].strip()
            self._disable_wandering(caller, npc_name)
            return
        
        # Force specific NPC to wander
        self._force_npc_wander(caller, self.args.strip())
    
    def _force_all_wander(self, caller):
        """Force all wandering NPCs to move."""
        from evennia.objects.models import ObjectDB
        from random import choice
        
        moved_count = 0
        failed_count = 0
        
        # Find all wandering NPCs
        for obj in ObjectDB.objects.all():
            if (hasattr(obj, "db") and 
                getattr(obj.db, "is_npc", False) and 
                getattr(obj.db, "npc_can_wander", False)):
                
                zone = getattr(obj.db, "npc_zone", None)
                if not zone:
                    continue
                
                # Get zone rooms
                zone_rooms = self._get_zone_rooms(zone)
                if len(zone_rooms) <= 1:
                    failed_count += 1
                    continue
                
                # Get available destinations
                available = [r for r in zone_rooms if r != obj.location]
                if not available:
                    failed_count += 1
                    continue
                
                # Move NPC
                destination = choice(available)
                old_loc = obj.location
                try:
                    # Calculate direction
                    direction = self._get_direction(old_loc, destination)
                    obj.location = destination
                    leave_msg = f"{obj.name} leaves for the {direction}." if direction else f"{obj.name} leaves."
                    arrive_msg = f"{obj.name} arrives from the {direction}." if direction else f"{obj.name} arrives."
                    if old_loc and hasattr(old_loc, "msg_contents"):
                        old_loc.msg_contents(leave_msg)
                    if hasattr(destination, "msg_contents"):
                        destination.msg_contents(arrive_msg)
                    moved_count += 1
                except:
                    obj.location = old_loc
                    failed_count += 1
        
        caller.msg(f"|gForced wandering: {moved_count} NPCs moved, {failed_count} failed/skipped.|n")
    
    def _force_npc_wander(self, caller, npc_name):
        """Force a specific NPC to wander."""
        from random import choice
        
        # Find NPC
        targets = search_object(npc_name)
        if not targets:
            caller.msg(f"|rNPC '{npc_name}' not found.|n")
            return
        
        npc = targets[0]
        if not getattr(npc.db, 'is_npc', False):
            caller.msg(f"|r{npc.key} is not an NPC.|n")
            return
        
        if not getattr(npc.db, "npc_can_wander", False):
            caller.msg(f"|r{npc.key} does not have wandering enabled.|n")
            caller.msg(f"|yUse: forcewander enable {npc.key}|n")
            return
        
        zone = getattr(npc.db, "npc_zone", None)
        if not zone:
            caller.msg(f"|r{npc.key} has no wandering zone set.|n")
            return
        
        # Get zone rooms
        zone_rooms = self._get_zone_rooms(zone)
        if len(zone_rooms) <= 1:
            caller.msg(f"|rZone '{zone}' has only {len(zone_rooms)} room(s). Need at least 2 for wandering.|n")
            return
        
        # Get available destinations
        available = [r for r in zone_rooms if r != npc.location]
        if not available:
            caller.msg(f"|rNo available destination rooms for {npc.key}.|n")
            return
        
        # Move NPC
        destination = choice(available)
        old_loc = npc.location
        try:
            # Calculate direction
            direction = self._get_direction(old_loc, destination)
            npc.location = destination
            leave_msg = f"{npc.name} leaves for the {direction}." if direction else f"{npc.name} leaves."
            arrive_msg = f"{npc.name} arrives from the {direction}." if direction else f"{npc.name} arrives."
            if old_loc and hasattr(old_loc, "msg_contents"):
                old_loc.msg_contents(leave_msg)
            if hasattr(destination, "msg_contents"):
                destination.msg_contents(arrive_msg)
            caller.msg(f"|gMoved {npc.key} from {old_loc.key} to {destination.key}.|n")
        except Exception as e:
            npc.location = old_loc
            caller.msg(f"|rFailed to move {npc.key}: {e}|n")
    
    def _show_status(self, caller):
        """Show wandering status of all NPCs."""
        from evennia.objects.models import ObjectDB
        
        npcs = []
        for obj in ObjectDB.objects.all():
            if hasattr(obj, "db") and getattr(obj.db, "is_npc", False):
                npcs.append(obj)
        
        if not npcs:
            caller.msg("|yNo NPCs found.|n")
            return
        
        caller.msg("|c=== NPC Wandering Status ===|n")
        for npc in npcs:
            can_wander = getattr(npc.db, "npc_can_wander", False)
            zone = getattr(npc.db, "npc_zone", None) or "none"
            location = npc.location.key if npc.location else "nowhere"
            
            # Check if wandering script is running
            script_running = False
            for script in npc.scripts.all():
                if script.key == "npc_wandering":
                    script_running = True
                    break
            
            status_color = "|g" if can_wander and script_running else "|r"
            status = "ACTIVE" if can_wander and script_running else "INACTIVE"
            
            caller.msg(f"{status_color}{npc.key}|n - {status}")
            caller.msg(f"  Zone: {zone}, Location: {location}, Can Wander: {can_wander}, Script: {script_running}")
    
    def _enable_wandering(self, caller, npc_name):
        """Enable wandering for an NPC."""
        # Find NPC
        targets = search_object(npc_name)
        if not targets:
            caller.msg(f"|rNPC '{npc_name}' not found.|n")
            return
        
        npc = targets[0]
        if not getattr(npc.db, 'is_npc', False):
            caller.msg(f"|r{npc.key} is not an NPC.|n")
            return
        
        zone = getattr(npc.db, "npc_zone", None)
        if not zone:
            caller.msg(f"|r{npc.key} has no wandering zone set. Use @npc-zone first.|n")
            return
        
        # Enable wandering
        npc.db.npc_can_wander = True
        
        # Start wandering script
        if hasattr(npc, "_enable_wandering"):
            npc._enable_wandering()
        else:
            # Manually start script if method doesn't exist
            from scripts.npc_wandering import NPCWanderingScript
            script = npc.scripts.add(NPCWanderingScript)
            if script:
                script.start()
        
        caller.msg(f"|gEnabled wandering for {npc.key} in zone '{zone}'.|n")
    
    def _disable_wandering(self, caller, npc_name):
        """Disable wandering for an NPC."""
        # Find NPC
        targets = search_object(npc_name)
        if not targets:
            caller.msg(f"|rNPC '{npc_name}' not found.|n")
            return
        
        npc = targets[0]
        if not getattr(npc.db, 'is_npc', False):
            caller.msg(f"|r{npc.key} is not an NPC.|n")
            return
        
        # Disable wandering
        npc.db.npc_can_wander = False
        
        # Stop wandering script
        if hasattr(npc, "_disable_wandering"):
            npc._disable_wandering()
        else:
            # Manually stop script
            for script in npc.scripts.all():
                if script.key == "npc_wandering":
                    script.stop()
        
        caller.msg(f"|gDisabled wandering for {npc.key}.|n")
    
    def _get_direction(self, from_room, to_room):
        """Calculate direction between two rooms based on coordinates."""
        if not from_room or not to_room:
            return None
        
        dx = getattr(to_room.db, 'x', None)
        dy = getattr(to_room.db, 'y', None)
        fx = getattr(from_room.db, 'x', None)
        fy = getattr(from_room.db, 'y', None)
        
        if dx is None or dy is None or fx is None or fy is None:
            return None
        
        if dx > fx:
            return 'east'
        elif dx < fx:
            return 'west'
        elif dy > fy:
            return 'north'
        elif dy < fy:
            return 'south'
        return None
    
    def _get_zone_rooms(self, zone):
        """Get all rooms in a zone."""
        from evennia.objects.models import ObjectDB
        
        rooms = []
        for room in ObjectDB.objects.all():
            if getattr(room, "zone", None) == zone:
                rooms.append(room)
        return rooms
