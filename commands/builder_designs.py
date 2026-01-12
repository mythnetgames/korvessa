"""
Builder Design Commands - Commands to start the design menus

Commands:
- designfurniture: Start furniture design menu
- designnpc: Start NPC design menu
- designweapon: Start weapon design menu
- designclothing: Start clothing/armor design menu
- managefactions: Manage factions
"""

from evennia import Command
from evennia.utils.evmenu import EvMenu
from commands.builder_menus import (
    furniture_start, npc_start, weapon_start, clothing_start
)
from world.builder_storage import (
    get_all_furniture, get_all_npcs, get_all_weapons,
    get_all_clothing, get_all_armor, get_all_factions,
    add_faction, delete_faction
)


class CmdDesignFurniture(Command):
    """
    Start the furniture design menu to create custom furniture.
    
    Usage:
        designfurniture
    
    This opens an interactive menu where you can define:
    - Furniture name and description
    - Whether it's movable
    - Number of seats
    - Recline/lie down capabilities
    - Custom messages for interactions
    """
    key = "designfurniture"
    aliases = ["furndesign"]
    locks = "cmd:perm(Builder)"
    help_category = "Building"
    
    def func(self):
        caller = self.caller
        
        # Start the furniture design menu
        EvMenu(caller, "commands.builder_menus", startnode="furniture_start")


class CmdDesignNPC(Command):
    """
    Start the NPC design menu to create custom NPCs.
    
    Usage:
        designnpc
    
    This opens an interactive menu where you can define:
    - NPC name and description
    - Faction affiliation
    - Wandering zone (or static placement)
    - Shopkeeper flag
    """
    key = "designnpc"
    aliases = ["npcdesign"]
    locks = "cmd:perm(Builder)"
    help_category = "Building"
    
    def func(self):
        caller = self.caller
        
        # Start the NPC design menu
        EvMenu(caller, "commands.builder_menus", startnode="npc_start")


class CmdDesignWeapon(Command):
    """
    Start the weapon design menu to create custom weapons.
    
    Usage:
        designweapon
    
    This opens an interactive menu where you can define:
    - Weapon name and description
    - Melee or ranged type
    - Ammo type (for ranged)
    - Damage and accuracy bonuses
    """
    key = "designweapon"
    aliases = ["weapondesign"]
    locks = "cmd:perm(Builder)"
    help_category = "Building"
    
    def func(self):
        caller = self.caller
        
        # Start the weapon design menu
        EvMenu(caller, "commands.builder_menus", startnode="weapon_start")


class CmdDesignClothing(Command):
    """
    Start the clothing/armor design menu to create custom items.
    
    Usage:
        designclothing
    
    This opens an interactive menu where you can define:
    - Item name and description
    - Clothing or armor type
    - Armor value and type (for armor)
    - Rarity level
    """
    key = "designclothing"
    aliases = ["clothingdesign", "designarmor"]
    locks = "cmd:perm(Builder)"
    help_category = "Building"
    
    def func(self):
        caller = self.caller
        
        # Start the clothing design menu
        EvMenu(caller, "commands.builder_menus", startnode="clothing_start")


class CmdListDesigns(Command):
    """
    List all designs created by builders.
    
    Usage:
        listdesigns
        listdesigns furniture
        listdesigns npcs
        listdesigns weapons
        listdesigns clothing
        listdesigns armor
        listdesigns all
    
    Examples:
        listdesigns furniture
        listdesigns all
    """
    key = "listdesigns"
    aliases = ["designs", "builderdesigns"]
    locks = "cmd:perm(Builder)"
    help_category = "Building"
    
    def func(self):
        caller = self.caller
        item_type = self.args.strip().lower() if self.args else "all"
        
        msg = "|c=== BUILDER DESIGNS ===|n\n"
        
        # Furniture
        if item_type in ("all", "furniture"):
            furniture_list = get_all_furniture()
            msg += f"|cFurniture ({len(furniture_list)})|n:\n"
            if furniture_list:
                for item in furniture_list:
                    msg += f"  - {item['name']} (ID: {item['id']}) - by {item.get('created_by', '?')}\n"
            else:
                msg += "  (none)\n"
            msg += "\n"
        
        # NPCs
        if item_type in ("all", "npcs", "npc"):
            npc_list = get_all_npcs()
            msg += f"|cNPCs ({len(npc_list)})|n:\n"
            if npc_list:
                for item in npc_list:
                    msg += f"  - {item['name']} (ID: {item['id']}) - by {item.get('created_by', '?')}\n"
            else:
                msg += "  (none)\n"
            msg += "\n"
        
        # Weapons
        if item_type in ("all", "weapons", "weapon"):
            weapon_list = get_all_weapons()
            msg += f"|cWeapons ({len(weapon_list)})|n:\n"
            if weapon_list:
                for item in weapon_list:
                    msg += f"  - {item['name']} (ID: {item['id']}) - {item['weapon_type']} - by {item.get('created_by', '?')}\n"
            else:
                msg += "  (none)\n"
            msg += "\n"
        
        # Clothing
        if item_type in ("all", "clothing"):
            clothing_list = get_all_clothing()
            msg += f"|cClothing ({len(clothing_list)})|n:\n"
            if clothing_list:
                for item in clothing_list:
                    msg += f"  - {item['name']} (ID: {item['id']}) - {item['rarity']} - by {item.get('created_by', '?')}\n"
            else:
                msg += "  (none)\n"
            msg += "\n"
        
        # Armor
        if item_type in ("all", "armor"):
            armor_list = get_all_armor()
            msg += f"|cArmor ({len(armor_list)})|n:\n"
            if armor_list:
                for item in armor_list:
                    msg += f"  - {item['name']} (ID: {item['id']}) - {item['armor_type']} - by {item.get('created_by', '?')}\n"
            else:
                msg += "  (none)\n"
            msg += "\n"
        
        caller.msg(msg)


class CmdManageFactions(Command):
    """
    Manage factions for NPC affiliations.
    
    Usage:
        managefactions
        managefactions list
        managefactions add <id> = <name> ; <description>
        managefactions delete <id>
    
    Examples:
        managefactions list
        managefactions add kowloon_gang = Kowloon Gang ; Street gang in Kowloon
        managefactions delete kowloon_gang
    """
    key = "managefactions"
    aliases = ["factions", "factionmanage"]
    locks = "cmd:perm(Builder)"
    help_category = "Building"
    
    def func(self):
        caller = self.caller
        args = self.args.strip()
        
        if not args or args.lower() == "list":
            self._list_factions(caller)
        elif args.lower().startswith("add "):
            self._add_faction(caller, args[4:])
        elif args.lower().startswith("delete "):
            self._delete_faction(caller, args[7:])
        else:
            caller.msg("|rUnknown faction command. Use 'managefactions list' for options.|n")
    
    def _list_factions(self, caller):
        """List all factions."""
        factions = get_all_factions()
        
        msg = "|c=== FACTIONS ===|n\n"
        if not factions:
            msg += "(none)\n"
        else:
            for faction in factions:
                msg += f"|y{faction['id']}|n - {faction['name']}\n"
                msg += f"  {faction['description']}\n"
                if faction.get('created_by'):
                    msg += f"  (created by {faction['created_by']})\n"
                msg += "\n"
        
        caller.msg(msg)
    
    def _add_faction(self, caller, args):
        """Add a new faction."""
        if "=" not in args or ";" not in args:
            caller.msg("|rUsage: managefactions add <id> = <name> ; <description>|n")
            return
        
        parts = args.split("=", 1)
        faction_id = parts[0].strip()
        
        rest = parts[1]
        name_parts = rest.split(";", 1)
        faction_name = name_parts[0].strip()
        description = name_parts[1].strip() if len(name_parts) > 1 else ""
        
        if not faction_id or not faction_name:
            caller.msg("|rFaction ID and name cannot be empty.|n")
            return
        
        # Check if ID already exists
        result = add_faction(faction_id, faction_name, description, created_by=caller.key)
        
        if result:
            caller.msg(f"|gFaction created: |y{faction_name}|g (ID: {faction_id})|n")
        else:
            caller.msg(f"|rFaction ID '{faction_id}' already exists.|n")
    
    def _delete_faction(self, caller, args):
        """Delete a faction."""
        faction_id = args.strip()
        
        if not faction_id:
            caller.msg("|rPlease provide a faction ID to delete.|n")
            return
        
        delete_faction(faction_id)
        caller.msg(f"|gDeleted faction: {faction_id}|n")
