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
        
        # Check for spawn_batch attribute
        spawn_batch = prototype.get("spawn_batch", [])
        
        if not spawn_batch:
            caller.msg(f"Prototype '{prototype_key}' is not a batch spawn prototype. "
                      "Use the regular @spawn command instead.")
            return
        
        # Check permissions via prototype_locks
        prototype_locks = prototype.get("prototype_locks", "")
        if "spawn:perm(Builder)" in prototype_locks:
            if not caller.check_permstring("Builder"):
                caller.msg("You don't have permission to spawn this prototype.")
                return
        
        # Spawn each item in the batch
        spawned_items = []
        location = caller.location
        
        for item_proto_key in spawn_batch:
            try:
                # Spawn the item
                objs = spawner.spawn(item_proto_key, location=location)
                if objs:
                    spawned_items.extend(objs)
            except Exception as e:
                caller.msg(f"Error spawning {item_proto_key}: {e}")
                continue
        
        if spawned_items:
            item_names = [obj.key for obj in spawned_items]
            caller.msg(f"Spawned {len(spawned_items)} items: {', '.join(item_names)}")
        else:
            caller.msg("No items were spawned. Check that the prototype definitions are correct.")
