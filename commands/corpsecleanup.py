"""
Corpse Cleanup Command - Remove all dead NPCs from the game world

Usage:
    corpsecleanup              - List all dead NPCs
    corpsecleanup all          - Delete all dead NPCs
    corpsecleanup <npc_id>     - Delete specific NPC by ID
    corpsecleanup <npc_name>   - Delete specific NPC by name
"""

from evennia import Command, search_object


class CmdCorpseCleanup(Command):
    """
    Clean up dead NPCs from the game world.
    
    Usage:
        corpsecleanup              - List all dead NPCs
        corpsecleanup all          - Delete all dead NPCs
        corpsecleanup <id/name>    - Delete specific dead NPC
    """
    
    key = "corpsecleanup"
    aliases = ["cleanup", "corpse_cleanup"]
    locks = "cmd:perm(Builder)"
    help_category = "Building"
    
    def func(self):
        caller = self.caller
        args = self.args.strip().lower() if self.args else ""
        
        # Find all dead NPCs
        dead_npcs = self._find_dead_npcs()
        
        if not dead_npcs:
            caller.msg("|yNo dead NPCs found.|n")
            return
        
        # List mode (default or "list")
        if not args or args == "list":
            self._list_dead_npcs(caller, dead_npcs)
            return
        
        # Delete all mode
        if args == "all":
            self._delete_all_corpses(caller, dead_npcs)
            return
        
        # Delete specific NPC by ID or name
        self._delete_specific_npc(caller, args, dead_npcs)
    
    def _find_dead_npcs(self):
        """Find all dead NPCs in the game."""
        from evennia.search import search_object
        
        dead_npcs = []
        
        # Search for all objects with NPC marker
        try:
            all_npcs = search_object(db_is_npc=True)
            for npc in all_npcs:
                # Check if dead using override_place or db.death_processed flag
                if self._is_dead(npc):
                    dead_npcs.append(npc)
        except:
            # Fallback: search by death-related attributes
            all_objects = search_object()
            for obj in all_objects:
                if (hasattr(obj, 'db') and getattr(obj.db, 'is_npc', False) and 
                    self._is_dead(obj)):
                    dead_npcs.append(obj)
        
        return dead_npcs
    
    def _is_dead(self, npc):
        """Check if an NPC is dead."""
        # Check override_place for death description
        if hasattr(npc, 'override_place'):
            place = str(npc.override_place or "").lower()
            if 'deceased' in place or 'motionless' in place or 'dead' in place:
                return True
        
        # Check death_processed flag
        if hasattr(npc, 'db'):
            if getattr(npc.db, 'death_processed', False):
                return True
        
        if hasattr(npc, 'ndb'):
            if getattr(npc.ndb, 'death_processed', False):
                return True
        
        # Check medical system
        try:
            if hasattr(npc, 'is_dead') and callable(npc.is_dead):
                if npc.is_dead():
                    return True
        except:
            pass
        
        return False
    
    def _list_dead_npcs(self, caller, dead_npcs):
        """Display list of dead NPCs."""
        caller.msg("|cDead NPCs:|n")
        caller.msg("-" * 80)
        
        for idx, npc in enumerate(dead_npcs, 1):
            location = f"at {npc.location.key}" if npc.location else "nowhere"
            template_id = getattr(npc.db, 'npc_template_id', 'unknown') if hasattr(npc, 'db') else 'unknown'
            caller.msg(f"|y{idx}|n. |c{npc.name}|n (|wID:|n {npc.id}, Template: {template_id}) - {location}")
        
        caller.msg("-" * 80)
        caller.msg(f"|yTotal dead NPCs:|n {len(dead_npcs)}")
        caller.msg(f"|yUsage:|n |ccorpsecleanup all|n to delete all, or |ccorpsecleanup <name>|n for specific NPC")
    
    def _delete_all_corpses(self, caller, dead_npcs):
        """Delete all dead NPCs."""
        count = len(dead_npcs)
        
        for npc in dead_npcs:
            npc.delete()
        
        caller.msg(f"|gDeleted {count} dead NPC(s).|n")
        
        # Log to admin channel
        try:
            from evennia.comms.models import ChannelDB
            admin_channel = ChannelDB.objects.get_channel("Admin")
            admin_channel.msg(f"|g{caller.name} cleaned up {count} dead NPCs.|n")
        except:
            pass
    
    def _delete_specific_npc(self, caller, search_term, dead_npcs):
        """Delete a specific dead NPC by name or ID."""
        matches = []
        
        for npc in dead_npcs:
            # Match by ID
            if str(npc.id) == search_term:
                matches = [npc]
                break
            
            # Match by name
            if search_term in npc.name.lower():
                matches.append(npc)
        
        if not matches:
            caller.msg(f"|rNo dead NPC found matching: {search_term}|n")
            return
        
        if len(matches) > 1:
            caller.msg(f"|rMultiple matches for '{search_term}':|n")
            for npc in matches:
                caller.msg(f"  - {npc.name} (ID: {npc.id})")
            caller.msg("|yBe more specific or use the ID.|n")
            return
        
        npc = matches[0]
        name = npc.name
        npc_id = npc.id
        npc.delete()
        
        caller.msg(f"|gDeleted dead NPC:|n |c{name}|n (ID: {npc_id})")
        
        # Log to admin channel
        try:
            from evennia.comms.models import ChannelDB
            admin_channel = ChannelDB.objects.get_channel("Admin")
            admin_channel.msg(f"|g{caller.name} cleaned up dead NPC: {name}|n")
        except:
            pass
