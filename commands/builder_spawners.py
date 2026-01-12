"""
Builder Spawn Commands - Commands to spawn builder-created items

Commands:
- spawnfurniture: Spawn furniture designs
- spawnnpc: Spawn NPC templates
- spawnweapon: Spawn weapon templates
- spawnclothing: Spawn clothing items
- spawnarmor: Spawn armor items
"""

from evennia import Command, create_object
from world.builder_storage import (
    get_all_furniture, search_furniture,
    get_all_npcs, search_npcs,
    get_all_weapons, search_weapons,
    get_all_clothing, search_clothing,
    get_all_armor, search_armor
)


class CmdSpawnFurniture(Command):
    """
    Spawn furniture from builder designs.
    
    Usage:
        spawnfurniture [<keyword or id>]
    
    With no arguments, lists all available furniture.
    With a keyword, narrows results by searching name/id.
    
    Examples:
        spawnfurniture
        spawnfurniture table
        spawnfurniture furniture_1
    """
    key = "spawnfurniture"
    aliases = ["spawniurniture"]
    locks = "cmd:perm(Builder)"
    help_category = "Building"
    
    def func(self):
        caller = self.caller
        
        # Get search keyword
        keyword = self.args.strip() if self.args else ""
        
        # Search furniture
        if keyword:
            furniture_list = search_furniture(keyword)
        else:
            furniture_list = get_all_furniture()
        
        if not furniture_list:
            caller.msg("|rNo furniture found matching: " + keyword + "|n")
            return
        
        # Build display
        msg = "|cAvailable Furniture:|n\n"
        msg += "-" * 60 + "\n"
        
        for idx, furniture in enumerate(furniture_list, 1):
            msg += f"{idx}. |y{furniture['name']}|n (ID: {furniture['id']})\n"
            msg += f"   Seats: {furniture['max_seats']}, "
            msg += f"Movable: {'Yes' if furniture['movable'] else 'No'}, "
            msg += f"Can Lie: {'Yes' if furniture['can_lie_down'] else 'No'}\n"
        
        msg += "-" * 60 + "\n"
        msg += "Type: |yspawnfurniture <number>|n to spawn, or refine search\n"
        
        # Store for follow-up
        caller.ndb._spawn_furniture_choices = furniture_list
        caller.ndb._spawn_furniture_mode = True
        
        # If they provided just a number, try to spawn immediately
        if keyword and keyword.isdigit():
            self._handle_spawn(caller, keyword)
        else:
            caller.msg(msg)
            caller.ndb._waiting_for_spawn = True
    
    def _handle_spawn(self, caller, choice_str):
        """Handle furniture spawning."""
        if not hasattr(caller.ndb, '_spawn_furniture_choices'):
            caller.msg("|rNo furniture session found.|n")
            return
        
        try:
            idx = int(choice_str.strip()) - 1
            choices = caller.ndb._spawn_furniture_choices
            
            if idx < 0 or idx >= len(choices):
                caller.msg("|rInvalid selection.|n")
                return
            
            furniture_data = choices[idx]
            
            # Create furniture object (you'll need to customize the typeclass)
            furniture = create_object(
                "typeclasses.objects.Object",
                key=furniture_data['name'],
                location=caller.location
            )
            
            # Set attributes from template
            furniture.db.furniture_template_id = furniture_data['id']
            furniture.db.desc = furniture_data['desc']
            furniture.db.max_seats = furniture_data['max_seats']
            furniture.db.is_movable = furniture_data['movable']
            furniture.db.can_lie_down = furniture_data['can_lie_down']
            furniture.db.can_recline = furniture_data['can_recline']
            furniture.db.sit_msg_first = furniture_data['sit_msg_first']
            furniture.db.sit_msg_third = furniture_data['sit_msg_third']
            furniture.db.lie_msg_first = furniture_data['lie_msg_first']
            furniture.db.lie_msg_third = furniture_data['lie_msg_third']
            furniture.db.recline_msg_first = furniture_data['recline_msg_first']
            furniture.db.recline_msg_third = furniture_data['recline_msg_third']
            
            caller.msg(f"|gSpawned: |y{furniture.name}|g (ID: {furniture.id})|n")
            caller.location.msg_contents(f"|g{caller.name} spawns a {furniture.name}.|n", exclude=[caller])
            
            # Clean up
            self._cleanup(caller)
        except (ValueError, IndexError):
            caller.msg("|rInvalid selection.|n")
    
    def _cleanup(self, caller):
        """Clean up temporary storage."""
        for attr in ('_spawn_furniture_choices', '_spawn_furniture_mode', '_waiting_for_spawn'):
            if hasattr(caller.ndb, attr):
                delattr(caller.ndb, attr)


class CmdSpawnNPC(Command):
    """
    Spawn NPCs from builder templates.
    
    Usage:
        spawnnpc [<keyword or id>]
    
    With no arguments, lists all available NPCs.
    With a keyword, narrows results by searching name/id.
    
    Examples:
        spawnnpc
        spawnnpc vendor
        spawnnpc npc_1
    """
    key = "spawnnpc"
    aliases = ["spawnnpcs"]
    locks = "cmd:perm(Builder)"
    help_category = "Building"
    
    def func(self):
        caller = self.caller
        
        # Get search keyword
        keyword = self.args.strip() if self.args else ""
        
        # Search NPCs
        if keyword:
            npc_list = search_npcs(keyword)
        else:
            npc_list = get_all_npcs()
        
        if not npc_list:
            caller.msg("|rNo NPCs found matching: " + keyword + "|n")
            return
        
        # Build display
        msg = "|cAvailable NPCs:|n\n"
        msg += "-" * 80 + "\n"
        
        for idx, npc in enumerate(npc_list, 1):
            msg += f"{idx}. |y{npc['name']}|n (ID: {npc['id']})\n"
            msg += f"   Faction: {npc['faction']}, "
            msg += f"Shopkeeper: {'Yes' if npc['is_shopkeeper'] else 'No'}, "
            msg += f"Wanders: {'Yes' if npc['wandering_zone'] else 'No'}\n"
            
            # Display stats
            if 'stats' in npc:
                stats = npc['stats']
                msg += f"   |cStats:|n Body:{stats.get('body',1)} Ref:{stats.get('ref',1)} Dex:{stats.get('dex',1)} "
                msg += f"Tech:{stats.get('tech',1)} Smrt:{stats.get('smrt',1)} Will:{stats.get('will',1)} "
                msg += f"Edge:{stats.get('edge',1)} Emp:{stats.get('emp',1)}\n"
            
            # Display skills (only non-zero)
            if 'skills' in npc:
                skills = npc['skills']
                skill_display = [f"{s}:{v}" for s, v in skills.items() if v > 0]
                if skill_display:
                    msg += f"   |cSkills:|n {', '.join(skill_display)}\n"
        
        msg += "-" * 80 + "\n"
        msg += "Type: |yspawnnpc <number>|n to spawn, or refine search\n"
        
        # Store for follow-up
        caller.ndb._spawn_npc_choices = npc_list
        caller.ndb._spawn_npc_mode = True
        
        # If they provided just a number, try to spawn immediately
        if keyword and keyword.isdigit():
            self._handle_spawn(caller, keyword)
        else:
            caller.msg(msg)
            caller.ndb._waiting_for_spawn = True
    
    def _handle_spawn(self, caller, choice_str):
        """Handle NPC spawning."""
        if not hasattr(caller.ndb, '_spawn_npc_choices'):
            caller.msg("|rNo NPC session found.|n")
            return
        
        try:
            idx = int(choice_str.strip()) - 1
            choices = caller.ndb._spawn_npc_choices
            
            if idx < 0 or idx >= len(choices):
                caller.msg("|rInvalid selection.|n")
                return
            
            npc_data = choices[idx]
            
            # Create NPC object (use NPC typeclass if available, otherwise Character)
            try:
                npc = create_object(
                    "typeclasses.npcs.NPC",
                    key=npc_data['name'],
                    location=caller.location
                )
            except:
                npc = create_object(
                    "typeclasses.characters.Character",
                    key=npc_data['name'],
                    location=caller.location
                )
            
            # Set attributes from template
            npc.db.npc_template_id = npc_data['id']
            npc.db.desc = npc_data['desc']
            npc.db.faction = npc_data['faction']
            npc.db.wandering_zone = npc_data['wandering_zone']
            npc.db.is_shopkeeper = npc_data['is_shopkeeper']
            npc.db.is_npc = True
            
            # Set stats from template
            if 'stats' in npc_data:
                for stat_name, stat_value in npc_data['stats'].items():
                    setattr(npc.db, stat_name, stat_value)
            
            # Set skills from template
            if 'skills' in npc_data:
                for skill_name, skill_value in npc_data['skills'].items():
                    setattr(npc.db, skill_name, skill_value)
            
            # Enable wandering if zone is set
            if npc_data['wandering_zone']:
                npc.db.npc_can_wander = True
                npc.db.npc_zone = npc_data['wandering_zone']
                # Trigger wandering initialization
                if hasattr(npc, "at_init"):
                    npc.at_init()
            
            caller.msg(f"|gSpawned: |y{npc.name}|g (ID: {npc.id})|n")
            caller.location.msg_contents(f"|g{caller.name} spawns {npc.name}.|n", exclude=[caller])
            
            # Clean up
            self._cleanup(caller)
        except (ValueError, IndexError):
            caller.msg("|rInvalid selection.|n")
    
    def _cleanup(self, caller):
        """Clean up temporary storage."""
        for attr in ('_spawn_npc_choices', '_spawn_npc_mode', '_waiting_for_spawn'):
            if hasattr(caller.ndb, attr):
                delattr(caller.ndb, attr)


class CmdSpawnWeapon(Command):
    """
    Spawn weapons from builder templates.
    
    Usage:
        spawnweapon [<keyword or id>]
    
    With no arguments, lists all available weapons.
    With a keyword, narrows results by searching name/type/id.
    
    Examples:
        spawnweapon
        spawnweapon pistol
        spawnweapon melee
        spawnweapon weapon_1
    """
    key = "spawnweapon"
    aliases = ["spawnweapons"]
    locks = "cmd:perm(Builder)"
    help_category = "Building"
    
    def func(self):
        caller = self.caller
        
        # Get search keyword
        keyword = self.args.strip() if self.args else ""
        
        # Search weapons
        if keyword:
            weapon_list = search_weapons(keyword)
        else:
            weapon_list = get_all_weapons()
        
        if not weapon_list:
            caller.msg("|rNo weapons found matching: " + keyword + "|n")
            return
        
        # Build display
        msg = "|cAvailable Weapons:|n\n"
        msg += "-" * 60 + "\n"
        
        for idx, weapon in enumerate(weapon_list, 1):
            msg += f"{idx}. |y{weapon['name']}|n (ID: {weapon['id']})\n"
            if weapon['weapon_type'] == 'ranged':
                msg += f"   Type: Ranged ({weapon['ammo_type']}), "
            else:
                msg += f"   Type: Melee, "
            msg += f"Damage: {weapon['damage_bonus']:+d}, "
            msg += f"Accuracy: {weapon['accuracy_bonus']:+d}\n"
        
        msg += "-" * 60 + "\n"
        msg += "Type: |yspawnweapon <number>|n to spawn, or refine search\n"
        
        # Store for follow-up
        caller.ndb._spawn_weapon_choices = weapon_list
        caller.ndb._spawn_weapon_mode = True
        
        # If they provided just a number, try to spawn immediately
        if keyword and keyword.isdigit():
            self._handle_spawn(caller, keyword)
        else:
            caller.msg(msg)
            caller.ndb._waiting_for_spawn = True
    
    def _handle_spawn(self, caller, choice_str):
        """Handle weapon spawning."""
        if not hasattr(caller.ndb, '_spawn_weapon_choices'):
            caller.msg("|rNo weapon session found.|n")
            return
        
        try:
            idx = int(choice_str.strip()) - 1
            choices = caller.ndb._spawn_weapon_choices
            
            if idx < 0 or idx >= len(choices):
                caller.msg("|rInvalid selection.|n")
                return
            
            weapon_data = choices[idx]
            
            # Create weapon object
            weapon = create_object(
                "typeclasses.items.Item",
                key=weapon_data['name'],
                location=caller.location
            )
            
            # Set attributes from template
            weapon.db.weapon_template_id = weapon_data['id']
            weapon.db.desc = weapon_data['desc']
            weapon.db.weapon_type = weapon_data['weapon_type']
            weapon.db.ammo_type = weapon_data['ammo_type']
            weapon.db.damage_bonus = weapon_data['damage_bonus']
            weapon.db.accuracy_bonus = weapon_data['accuracy_bonus']
            weapon.db.is_weapon = True
            
            caller.msg(f"|gSpawned: |y{weapon.name}|g (ID: {weapon.id})|n")
            caller.location.msg_contents(f"|g{caller.name} spawns a {weapon.name}.|n", exclude=[caller])
            
            # Clean up
            self._cleanup(caller)
        except (ValueError, IndexError):
            caller.msg("|rInvalid selection.|n")
    
    def _cleanup(self, caller):
        """Clean up temporary storage."""
        for attr in ('_spawn_weapon_choices', '_spawn_weapon_mode', '_waiting_for_spawn'):
            if hasattr(caller.ndb, attr):
                delattr(caller.ndb, attr)


class CmdSpawnClothing(Command):
    """
    Spawn clothing items from builder templates.
    
    Usage:
        spawnclothing [<keyword or id>]
    
    With no arguments, lists all available clothing.
    With a keyword, narrows results by searching name/id.
    
    Examples:
        spawnclothing
        spawnclothing shirt
        spawnclothing clothing_1
    """
    key = "spawnclothing"
    aliases = ["spawnclothes"]
    locks = "cmd:perm(Builder)"
    help_category = "Building"
    
    def func(self):
        caller = self.caller
        
        # Get search keyword
        keyword = self.args.strip() if self.args else ""
        
        # Search clothing
        if keyword:
            clothing_list = search_clothing(keyword)
        else:
            clothing_list = get_all_clothing()
        
        if not clothing_list:
            caller.msg("|rNo clothing found matching: " + keyword + "|n")
            return
        
        # Build display
        msg = "|cAvailable Clothing:|n\n"
        msg += "-" * 60 + "\n"
        
        for idx, item in enumerate(clothing_list, 1):
            msg += f"{idx}. |y{item['name']}|n (ID: {item['id']})\n"
            msg += f"   Rarity: {item['rarity'].capitalize()}\n"
        
        msg += "-" * 60 + "\n"
        msg += "Type: |yspawnclothing <number>|n to spawn, or refine search\n"
        
        # Store for follow-up
        caller.ndb._spawn_clothing_choices = clothing_list
        caller.ndb._spawn_clothing_mode = True
        
        # If they provided just a number, try to spawn immediately
        if keyword and keyword.isdigit():
            self._handle_spawn(caller, keyword)
        else:
            caller.msg(msg)
            caller.ndb._waiting_for_spawn = True
    
    def _handle_spawn(self, caller, choice_str):
        """Handle clothing spawning."""
        if not hasattr(caller.ndb, '_spawn_clothing_choices'):
            caller.msg("|rNo clothing session found.|n")
            return
        
        try:
            idx = int(choice_str.strip()) - 1
            choices = caller.ndb._spawn_clothing_choices
            
            if idx < 0 or idx >= len(choices):
                caller.msg("|rInvalid selection.|n")
                return
            
            clothing_data = choices[idx]
            
            # Create clothing object
            clothing = create_object(
                "typeclasses.objects.Object",
                key=clothing_data['name'],
                location=caller.location
            )
            
            # Set attributes from template
            clothing.db.clothing_template_id = clothing_data['id']
            clothing.db.desc = clothing_data['desc']
            clothing.db.rarity = clothing_data['rarity']
            clothing.db.is_clothing = True
            
            caller.msg(f"|gSpawned: |y{clothing.name}|g (ID: {clothing.id})|n")
            caller.location.msg_contents(f"|g{caller.name} spawns a {clothing.name}.|n", exclude=[caller])
            
            # Clean up
            self._cleanup(caller)
        except (ValueError, IndexError):
            caller.msg("|rInvalid selection.|n")
    
    def _cleanup(self, caller):
        """Clean up temporary storage."""
        for attr in ('_spawn_clothing_choices', '_spawn_clothing_mode', '_waiting_for_spawn'):
            if hasattr(caller.ndb, attr):
                delattr(caller.ndb, attr)


class CmdSpawnArmor(Command):
    """
    Spawn armor items from builder templates.
    
    Usage:
        spawnarmor [<keyword or id>]
    
    With no arguments, lists all available armor.
    With a keyword, narrows results by searching name/type/id.
    
    Examples:
        spawnarmor
        spawnarmor light
        spawnarmor vest
        spawnarmor armor_1
    """
    key = "spawnarmor"
    aliases = ["spawnarmors"]
    locks = "cmd:perm(Builder)"
    help_category = "Building"
    
    def func(self):
        caller = self.caller
        
        # Get search keyword
        keyword = self.args.strip() if self.args else ""
        
        # Search armor
        if keyword:
            armor_list = search_armor(keyword)
        else:
            armor_list = get_all_armor()
        
        if not armor_list:
            caller.msg("|rNo armor found matching: " + keyword + "|n")
            return
        
        # Build display
        msg = "|cAvailable Armor:|n\n"
        msg += "-" * 60 + "\n"
        
        for idx, item in enumerate(armor_list, 1):
            msg += f"{idx}. |y{item['name']}|n (ID: {item['id']})\n"
            msg += f"   Type: {item['armor_type'].capitalize()}, "
            msg += f"Armor: {item['armor_value']}, "
            msg += f"Rarity: {item['rarity'].capitalize()}\n"
        
        msg += "-" * 60 + "\n"
        msg += "Type: |yspawnarmor <number>|n to spawn, or refine search\n"
        
        # Store for follow-up
        caller.ndb._spawn_armor_choices = armor_list
        caller.ndb._spawn_armor_mode = True
        
        # If they provided just a number, try to spawn immediately
        if keyword and keyword.isdigit():
            self._handle_spawn(caller, keyword)
        else:
            caller.msg(msg)
            caller.ndb._waiting_for_spawn = True
    
    def _handle_spawn(self, caller, choice_str):
        """Handle armor spawning."""
        if not hasattr(caller.ndb, '_spawn_armor_choices'):
            caller.msg("|rNo armor session found.|n")
            return
        
        try:
            idx = int(choice_str.strip()) - 1
            choices = caller.ndb._spawn_armor_choices
            
            if idx < 0 or idx >= len(choices):
                caller.msg("|rInvalid selection.|n")
                return
            
            armor_data = choices[idx]
            
            # Create armor object
            armor = create_object(
                "typeclasses.objects.Object",
                key=armor_data['name'],
                location=caller.location
            )
            
            # Set attributes from template
            armor.db.armor_template_id = armor_data['id']
            armor.db.desc = armor_data['desc']
            armor.db.armor_type = armor_data['armor_type']
            armor.db.armor_value = armor_data['armor_value']
            armor.db.rarity = armor_data['rarity']
            armor.db.is_armor = True
            
            caller.msg(f"|gSpawned: |y{armor.name}|g (ID: {armor.id})|n")
            caller.location.msg_contents(f"|g{caller.name} spawns a {armor.name}.|n", exclude=[caller])
            
            # Clean up
            self._cleanup(caller)
        except (ValueError, IndexError):
            caller.msg("|rInvalid selection.|n")
    
    def _cleanup(self, caller):
        """Clean up temporary storage."""
        for attr in ('_spawn_armor_choices', '_spawn_armor_mode', '_waiting_for_spawn'):
            if hasattr(caller.ndb, attr):
                delattr(caller.ndb, attr)
