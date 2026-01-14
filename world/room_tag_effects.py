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
        self.start_delay = 0  # Start immediately
        self.repeats = 0  # Repeat forever
        # If script is paused, resume it
        if hasattr(self, 'is_paused') and self.is_paused:
            self.resume()
        
    def at_repeat(self):
        """Called every interval to process room effects"""
        room = self.obj
        if not room:
            self.stop()
            return
        
        # Get only characters (PCs and NPCs), not exits or objects
        characters = []
        for obj in room.contents:
            # Skip non-characters
            if not hasattr(obj, 'is_typeclass'):
                continue
            # Must be a Character typeclass
            if not obj.is_typeclass("typeclasses.characters.Character", exact=False):
                continue
            # Skip dead characters
            if hasattr(obj, 'is_dead') and obj.is_dead():
                continue
            characters.append(obj)
        
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
        from evennia.comms.models import ChannelDB
        
        try:
            splattercast = ChannelDB.objects.get_channel("Splattercast")
        except:
            splattercast = None
        
        for char in characters:
            try:
                # Random damage message variety
                messages = [
                    "|rYou are burned by the intense heat!|n",
                    "|rFlames scorch your skin!|n",
                    "|rThe fire sears you with unbearable pain!|n",
                ]
                char.msg(random.choice(messages))
                room_messages = [
                    f"|r{char.key} is burned by the intense heat!|n",
                    f"|rFlames scorch {char.key}!|n",
                    f"|r{char.key} screams as fire sears them!|n",
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
            except Exception as e:
                if splattercast:
                    splattercast.msg(f"FIRE_ERROR on {char.key}: {e}")
    
    def _handle_underwater(self, room, characters):
        """Handle underwater stamina/breath drain"""
        UNDERWATER_STAMINA_DRAIN = 5  # Stamina points per tick (every 5 seconds)
        
        for char in characters:
            # Notify on first tick
            if not getattr(char.ndb, "underwater_warned", False):
                char.msg("|cYou are underwater - holding your breath costs stamina.|n")
                char.ndb.underwater_warned = True
            
            # Drain stamina
            if hasattr(char.ndb, 'stamina') and char.ndb.stamina:
                stamina = char.ndb.stamina
                old_stamina = stamina.stamina_current
                stamina.stamina_current = max(0, stamina.stamina_current - UNDERWATER_STAMINA_DRAIN)
                
                # Warn if stamina is getting low
                percent = stamina.stamina_current / stamina.stamina_max if stamina.stamina_max > 0 else 0
                if percent < 0.2 and old_stamina / stamina.stamina_max >= 0.2:
                    char.msg("|rYou are running out of air!|n")
                elif percent <= 0:
                    # Out of stamina - start drowning damage
                    char.msg("|rYou are drowning!|n")
                    room.msg_contents(f"|r{char.key} is drowning!|n", exclude=[char])
                    # Apply damage (could integrate with medical system)
                    if hasattr(char, 'db') and hasattr(char.db, 'hp'):
                        char.db.hp = max(0, (char.db.hp or 0) - 5)
    
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
                char.msg("|yThe crowd is bustling - easier to blend in or take advantage.|n")
                char.ndb.crowded_notified = True


def attach_effect_handler(room):
    """
    Attach effect handler to a room.
    
    Args:
        room: Room object
    """
    from evennia.scripts.models import ScriptDB
    from evennia.comms.models import ChannelDB
    
    try:
        splattercast = ChannelDB.objects.get_channel("Splattercast")
    except:
        splattercast = None
    
    # Delete any existing handlers and create fresh
    existing = ScriptDB.objects.filter(db_obj=room, db_key="room_tag_effects")
    for script in existing:
        if splattercast:
            splattercast.msg(f"FIRE_DEBUG: Deleting old script {script.id}")
        script.delete()
    
    # Create new handler
    from evennia.utils.create import create_script
    handler = create_script(
        RoomTagEffectHandler,
        obj=room,
        key="room_tag_effects",
        autostart=True,
        interval=5,
        start_delay=0,
        repeats=0,
        persistent=True
    )
    
    if splattercast:
        splattercast.msg(f"FIRE_DEBUG: Created new script {handler.id if handler else 'NONE'}, is_active={handler.is_active if handler else 'N/A'}")
    
    # Force start the script
    if handler and not handler.is_active:
        handler.start()
        if splattercast:
            splattercast.msg(f"FIRE_DEBUG: Force started script")
    
    return handler


def remove_effect_handler(room):
    """
    Remove effect handler from a room.
    
    Args:
        room: Room object
    """
    from evennia.scripts.models import ScriptDB
    
    scripts = ScriptDB.objects.filter(db_obj=room, db_key="room_tag_effects")
    for script in scripts:
        script.delete()
