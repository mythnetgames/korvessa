"""
Custom spawn command that supports spawning armor sets.

Extends Evennia's spawn command to handle prototypes with spawn_batch attribute,
which spawns multiple prototypes at once.
"""

from evennia.commands.default.building import CmdSpawn as DefaultCmdSpawn
from evennia.prototypes import spawner, prototypes as protlib
from evennia import Command


class CmdSpawnSet(Command):
    """
    Spawn a full armor set or batch of items.
    
    Usage:
        spawnset <prototype_key>
        
    This command spawns all items defined in a prototype's spawn_batch list.
    Use this for armor sets like SCRAP_ARMOR_SET, MILITARY_ARMOR_SET, etc.
    
    Examples:
        spawnset SCRAP_ARMOR_SET     - Spawns all 5 pieces of scrap armor
        spawnset MILITARY_ARMOR_SET  - Spawns all 5 pieces of military armor
        
    Available armor sets:
        SCRAP_ARMOR_SET      - Tier 1 (Rating 2)
        MAKESHIFT_ARMOR_SET  - Tier 2 (Rating 4)
        STANDARD_ARMOR_SET   - Tier 3 (Rating 6)
        REINFORCED_ARMOR_SET - Tier 4 (Rating 8)
        MILITARY_ARMOR_SET   - Tier 5 (Rating 10)
    """
    
    key = "spawnset"
    aliases = ["spawnarmorset", "armorset"]
    locks = "cmd:perm(Builder)"
    help_category = "Building"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: spawnset <prototype_key>")
            caller.msg("Available armor sets: SCRAP_ARMOR_SET, MAKESHIFT_ARMOR_SET, "
                      "STANDARD_ARMOR_SET, REINFORCED_ARMOR_SET, MILITARY_ARMOR_SET")
            return
        
        prototype_key = self.args.strip().upper()
        location = caller.location
        
        if not location:
            caller.msg("You must be in a room to spawn armor sets.")
            return
        
        # Try to get the prototype
        try:
            prototype = protlib.search_prototype(prototype_key)
        except Exception:
            prototype = None
            
        if not prototype:
            caller.msg(f"Prototype '{prototype_key}' not found.")
            return
            
        # Handle list result from search
        if isinstance(prototype, list):
            if len(prototype) == 0:
                caller.msg(f"Prototype '{prototype_key}' not found.")
                return
            elif len(prototype) > 1:
                caller.msg(f"Multiple prototypes match '{prototype_key}'. Please be more specific.")
                return
            prototype = prototype[0]
        
        # Check permissions via prototype_locks
        prototype_locks = prototype.get("prototype_locks", "")
        if "spawn:perm(Builder)" in prototype_locks:
            if not caller.check_permstring("Builder"):
                caller.msg("You don't have permission to spawn this prototype.")
                return
        
        # Spawn the set prototype first to get the object with attributes
        try:
            objs = spawner.spawn(prototype_key, location=location)
        except Exception as e:
            caller.msg(f"Error spawning set template: {e}")
            return
        
        if not objs:
            caller.msg("Failed to spawn set template.")
            return
        
        set_obj = objs[0]
        
        # Get the spawn_batch list from the object's attributes
        spawn_batch = None
        if hasattr(set_obj.db, 'spawn_batch'):
            spawn_batch = set_obj.db.spawn_batch
        
        if not spawn_batch:
            caller.msg(f"Set template '{prototype_key}' has no spawn_batch data.")
            # Clean up the template object
            set_obj.delete()
            return
        
        # Spawn each item in the batch
        spawned_items = []
        
        for item_proto_key in spawn_batch:
            try:
                # Spawn the item directly into the location
                objs = spawner.spawn(item_proto_key, location=location)
                if objs:
                    for obj in objs:
                        spawned_items.append(obj)
                        # Ensure it's in the room
                        if obj.location != location:
                            obj.location = location
            except Exception as e:
                caller.msg(f"Error spawning {item_proto_key}: {e}")
                continue
        
        # Delete the template object
        set_obj.delete()
        
        if spawned_items:
            item_names = [obj.key for obj in spawned_items]
            caller.msg(f"Spawned {len(spawned_items)} items in {location.key}: {', '.join(item_names)}")
            # Also notify the room
            location.msg_contents(f"{caller.key} has spawned {len(spawned_items)} items here.", exclude=[caller])
        else:
            caller.msg("No items were spawned. Check that the prototype definitions are correct.")
