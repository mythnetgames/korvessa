"""
Room tag effects system.

Handles active effects like ON FIRE, SMOKED OUT, UNDERWATER, etc.
This script runs periodically to apply damage, status effects, and other ongoing room effects.
"""

from evennia.scripts.scripts import DefaultScript
from world.room_tags import ALL_TAGS, has_tag


class RoomTagEffectHandler(DefaultScript):
    """
    Handles active effects from room tags.
    
    Runs every 5 seconds to apply damage, effects, and checks from room tags.
    Should be attached to individual rooms as needed.
    """
    
    is_active = True
    persistent = True
    
    def at_script_creation(self):
        """Initialize script"""
        self.key = "room_tag_effects"
        self.desc = "Handles active effects from room tags"
        self.interval = 5  # Run every 5 seconds
        
    def at_repeat(self):
        """Called every interval to process room effects"""
        room = self.obj
        if not room:
            self.stop()
            return
        
        # Get characters in room
        characters = [obj for obj in room.contents 
                     if obj.is_typeclass("typeclasses.characters.Character")]
        
        if not characters:
            return
        
        # Process each active tag
        if has_tag(room, "FIRE"):
            self._handle_on_fire(room, characters)
        
        if has_tag(room, "UNDERWATER"):
            self._handle_underwater(room, characters)
        
        if has_tag(room, "UNSTABLE"):
            self._handle_unstable(room, characters)
        
        if has_tag(room, "CROWDED"):
            self._handle_crowded(room, characters)
    
    def _handle_on_fire(self, room, characters):
        """Apply fire damage and burns every tick"""
        import random
        from world.medical.conditions import BurnCondition
        
        for char in characters:
            # Random damage message variety
            messages = [
                "|r[!] You're burned by the intense heat!|n",
                "|r[!] Flames scorch your skin!|n",
                "|r[!] The fire sears you with unbearable pain!|n",
            ]
            char.msg(random.choice(messages))
            room_messages = [
                f"|r[!] {char.key} is burned by the intense heat!|n",
                f"|r[!] Flames scorch {char.key}'s skin!|n",
                f"|r[!] {char.key} screams as fire sears them!|n",
            ]
            room.msg_contents(random.choice(room_messages), exclude=[char])
            
            # Create burn wounds
            if hasattr(char, 'medical_state'):
                medical_state = char.medical_state
                
                # Determine severity based on existing burns
                existing_burns = [c for c in medical_state.conditions if c.condition_type == "burn"]
                burn_severity = 1 + len(existing_burns)  # Stacking burns get worse
                
                # Randomly pick body location for the burn
                locations = ["chest", "arms", "legs", "head", "back"]
                location = random.choice(locations)
                
                # Create burn condition
                burn = BurnCondition(burn_severity, location)
                medical_state.conditions.append(burn)
                burn.start_condition(char)
                
                # If severe enough, also cause bleeding
                if burn_severity >= 3:
                    from world.medical.conditions import BleedingCondition
                    if random.random() < 0.3:  # 30% chance for severe burns to cause bleeding
                        bleed = BleedingCondition(max(1, burn_severity - 2), location)
                        medical_state.conditions.append(bleed)
                        bleed.start_condition(char)
    
    def _handle_underwater(self, room, characters):
        """Handle underwater stamina/breath drain"""
        # This would integrate with stamina system
        # For now, just notify
        for char in characters:
            if not getattr(char.ndb, "underwater_warned", False):
                char.msg("|c[!] You're underwater - holding your breath costs stamina.|n")
                char.ndb.underwater_warned = True
    
    def _handle_unstable(self, room, characters):
        """Random chance for characters to fall to room below"""
        import random
        from evennia.objects.models import ObjectDB
        
        for char in characters:
            # 15% chance per tick to trigger fall check
            if random.random() < 0.15:
                # Roll dexterity check
                dex = getattr(char.db, "dex", 1) or 1
                fall_roll = random.randint(1, 100)
                dc = 50 - (dex * 5)  # Higher dex = easier to catch yourself
                
                if fall_roll > dc:
                    # Failed - character falls
                    char.msg("|r[!] The floor gives way beneath you!|n")
                    room.msg_contents(f"|r[!] {char.key} falls through the unstable floor!|n", exclude=[char])
                    
                    # Try to find room below (z-1)
                    below_room = None
                    try:
                        if hasattr(room.db, 'z'):
                            z_below = room.db.z - 1
                            x = getattr(room.db, 'x', 0)
                            y = getattr(room.db, 'y', 0)
                            # Search for room at z-1
                            for potential_room in ObjectDB.objects.filter(db_typeclass_path="typeclasses.rooms.Room"):
                                if (getattr(potential_room.db, 'x', 0) == x and 
                                    getattr(potential_room.db, 'y', 0) == y and 
                                    getattr(potential_room.db, 'z', 0) == z_below):
                                    below_room = potential_room
                                    break
                    except:
                        pass
                    
                    # Move character
                    if below_room:
                        char.move_to(below_room, move_type="teleport")
                        char.msg(f"|y[!] You crash into the {below_room.key} below!|n")
                    else:
                        char.msg("|r[!] You plummet into the void!|n")
    
    def _handle_crowded(self, room, characters):
        """Crowded rooms provide skill bonuses"""
        # This is passive - bonuses applied at skill check time
        # Just remind characters
        for char in characters:
            if not getattr(char.ndb, "crowded_notified", False):
                char.msg("|y[!] The crowd is bustling - easier to blend in or take advantage.|n")
                char.ndb.crowded_notified = True


def attach_effect_handler(room):
    """
    Attach effect handler to a room.
    
    Args:
        room: Room object
    """
    from evennia.scripts.models import ScriptDB
    
    # Check if already attached
    existing = ScriptDB.objects.filter(db_obj=room, db_key="room_tag_effects")
    if existing.exists():
        return existing[0]
    
    # Create new handler
    from evennia.utils.create import create_script
    handler = create_script(
        RoomTagEffectHandler,
        obj=room,
        key="room_tag_effects",
        autostart=True
    )
    return handler


def remove_effect_handler(room):
    """
    Remove effect handler from a room.
    
    Args:
        room: Room object
    """
    from evennia.scripts.models import ScriptDB
    
    scripts = ScriptDB.objects.filter(obj=room, db_key="room_tag_effects")
    for script in scripts:
        script.delete()
