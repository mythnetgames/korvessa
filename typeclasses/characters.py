"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from evennia.objects.objects import DefaultCharacter
from evennia.typeclasses.attributes import AttributeProperty
from evennia.comms.models import ChannelDB  # Ensure this is imported

from .objects import ObjectParent


class Character(ObjectParent, DefaultCharacter):

    def at_post_login(self, session=None, **kwargs):
        """
        Called every time a player logs in. Enable mapper only if player has municipal wristpad.
        Also checks if player is within 3 hours of an IP grant tick and grants missed IP if applicable.
        """
        from world.safetynet.utils import has_municipal_wristpad
        
        # Only enable mapper if player has a municipal wristpad
        if has_municipal_wristpad(self):
            if self.account and hasattr(self.account, 'db'):
                self.account.db.mapper_enabled = True
            self.ndb.mapper_enabled = True
        else:
            if self.account and hasattr(self.account, 'db'):
                self.account.db.mapper_enabled = False
            self.ndb.mapper_enabled = False
        
        # Reset proxy active state on login - players must re-enable each session
        from world.safetynet.utils import check_access_device
        try:
            device_type, device = check_access_device(self)
            if device:
                proxy = getattr(device.db, "slotted_proxy", None)
                if proxy:
                    proxy.db.is_active = False
        except:
            pass
        
        # Check for missed IP grant from login catch-up
        try:
            from scripts.ip_grant_script import grant_missed_ip_on_login
            grant_missed_ip_on_login(self)
        except Exception as e:
            # Silently fail if IP grant system not ready
            pass
        
        # Show map and room description immediately
        from commands.mapper import CmdMap
        cmd = CmdMap()
        cmd.caller = self
        cmd.args = ""
        cmd.func()
        
        # Show pending petitions on login
        self.show_pending_petitions()

    def at_post_puppet(self, **kwargs):
        """
        Called just after puppeting has been completed. Suppress the "has entered
        the game" message if an admin is puppeting this character. Also ensure the
        puppet is in a location so the admin can see room activity.
        
        Args:
            **kwargs: Arbitrary, optional arguments
        """
        from django.utils.translation import gettext as _
        
        # Show the account link message
        self.msg(_("\nYou become |c{name}|n.\n").format(name=self.key))
        self.msg((self.at_look(self.location), {"type": "look"}), options=None)

        # Check if the controlling account is an admin
        is_admin_puppeted = False
        if self.account:
            is_admin_puppeted = self.account.is_superuser or self.account.is_staff
        
        # If puppet is in None location (was stored), try to restore their previous location
        if not self.location and is_admin_puppeted:
            prelogout_location = self.db.prelogout_location
            if prelogout_location:
                self.location = prelogout_location
                self.msg(f"Restored to |c{self.location.name}|n.")
        
        # Only show "has entered the game" if NOT puppeted by an admin
        if self.location and not is_admin_puppeted:
            def message(obj, from_obj):
                obj.msg(
                    _("{name} has entered the game.").format(name=self.get_display_name(obj)),
                    from_obj=from_obj,
                )

            self.location.for_contents(message, exclude=[self], from_obj=self)

    def show_pending_petitions(self):
        """Display pending and active petitions on login."""
        petitions = getattr(self.db, 'petitions', None) or []
        active_count = len([p for p in petitions if p.get('status') == 'active'])
        pending_count = len([p for p in petitions if p.get('status') == 'pending'])
        
        if active_count > 0 or pending_count > 0:
            self.msg("|y=== You have pending petitions ===|n")
            if active_count > 0:
                self.msg(f"  |c{active_count} active petition(s)|n - type |wlook petitions|n to view")
            if pending_count > 0:
                self.msg(f"  |c{pending_count} pending petition(s)|n - type |wlook pending|n to view")

    def at_post_unpuppet(self, account=None, session=None, **kwargs):
        """
        Called when a character is unpuppeted. Suppress the "left the game" 
        message if an admin was puppeting this character.
        
        Args:
            account: The account that was controlling this character
            session: The session that just disconnected
            **kwargs: Additional arguments
        """
        # Check if the account controlling this character is an admin
        is_admin_puppeted = False
        if account:
            # Check if the account has admin/staff permissions
            is_admin_puppeted = account.is_superuser or account.is_staff
        
        if not self.sessions.count():
            # Character no longer controlled by any session
            if self.location and not is_admin_puppeted:
                # Only show the "left game" message if NOT puppeted by admin
                def message(obj, from_obj):
                    from django.utils.translation import gettext as _
                    obj.msg(
                        _("{name} has left the game{reason}.").format(
                            name=self.get_display_name(obj),
                            reason=kwargs.get("reason", ""),
                        ),
                        from_obj=from_obj,
                    )

                self.location.for_contents(message, exclude=[self], from_obj=self)
            
            # Store prelogout location regardless
            if self.location:
                self.db.prelogout_location = self.location
            self.location = None

    def at_before_move(self, destination, **kwargs):
        """
        Called before the character moves to a new location.
        If this character is grappling someone, drag them along.
        If this character is grappled, they move with their grappler.
        
        Args:
            destination: The location the character is moving to
            **kwargs: Additional arguments
            
        Returns:
            bool: True to allow move, False to prevent it
        """
        from world.combat.constants import DB_CHAR, DB_GRAPPLING_DBREF, DB_GRAPPLED_BY_DBREF
        from world.combat.utils import get_character_by_dbref
        
        # Check if this character has an active grapple
        handler = getattr(self.ndb, "combat_handler", None)
        if not handler:
            return True  # Allow move if no combat
        
        # Find this character's combat entry
        char_entry = next((e for e in handler.db.combatants if e["char"] == self), None)
        if not char_entry:
            return True  # Allow move if not in combat
        
        # Check if grappling someone - if so, drag them
        grappling_dbref = char_entry.get(DB_GRAPPLING_DBREF)
        if grappling_dbref:
            # Find the grappled victim
            victim = get_character_by_dbref(grappling_dbref)
            if victim and victim.location != destination:
                # Drag victim to new location
                victim.location = destination
                victim.msg(f"{self.key} drags you to {destination.key}.")
                self.msg(f"You drag {victim.key} with you to {destination.key}.")
        
        return True  # Allow the move

    def at_server_start(self):
        """
        Called on every character at server reboot. Enable mapper only if player has municipal wristpad.
        """
        from world.safetynet.utils import has_municipal_wristpad
        
        # Only enable mapper if player has a municipal wristpad
        if has_municipal_wristpad(self):
            if self.account and hasattr(self.account, 'db'):
                self.account.db.mapper_enabled = True
            self.ndb.mapper_enabled = True
        else:
            if self.account and hasattr(self.account, 'db'):
                self.account.db.mapper_enabled = False
            self.ndb.mapper_enabled = False
        
        # Force map display only if mapper is enabled
        if self.ndb.mapper_enabled:
            try:
                from commands.mapper import CmdMapOn
                cmd = CmdMapOn()
                cmd.caller = self
                cmd.func()
            except Exception as e:
                self.msg(f"Map enabling failed on reboot: {e}")

    # =========================================================================
    # The Character just re-implements some of the Object's methods and hooks
    # to represent a Character entity in-game.
    #
    # See mygame/typeclasses/objects.py for a list of
    # properties and methods available on all Object child classes like this.
    #
    # In this instance, we are also adding the new stat system attributes using AttributeProperty.
    # =========================================================================
    
    # New Stat System Attributes
    # Smarts, Willpower, Edge, Reflexes, Body, Dexterity, Empathy, Technique
    smrt = AttributeProperty(1, category='stat', autocreate=True)
    will = AttributeProperty(1, category='stat', autocreate=True)
    edge = AttributeProperty(1, category='stat', autocreate=True)
    ref = AttributeProperty(1, category='stat', autocreate=True)
    body = AttributeProperty(1, category='stat', autocreate=True)
    dex = AttributeProperty(1, category='stat', autocreate=True)
    _emp = AttributeProperty(None, category='stat', autocreate=True)  # Override value, None = calculated
    tech = AttributeProperty(1, category='stat', autocreate=True)
    sex = AttributeProperty("ambiguous", category="biology", autocreate=True)
    
    @property
    def emp(self):
        """
        Empathy is calculated as edge + willpower.
        Can be overridden by admin setting _emp to a specific value.
        """
        if self._emp is not None:
            return self._emp
        # Calculate from edge + willpower
        edge_val = getattr(self, 'edge', 1)
        will_val = getattr(self, 'will', 1)
        return edge_val + will_val
    
    @emp.setter
    def emp(self, value):
        """Set empathy override. Set to None to use calculated value."""
        self._emp = value
    
    # Shop System Attributes
    is_merchant = AttributeProperty(False, category="shop", autocreate=True)
    is_holographic = AttributeProperty(False, category="shop", autocreate=True)
    tokens = AttributeProperty(0, category="shop", autocreate=True)
    
    # Death tracking system
    death_count = AttributeProperty(1, category='mortality', autocreate=True)
    
    # Appearance attributes - stored in db but no auto-creation for optional features
    # skintone is set via @skintone command and stored as db.skintone

    # ===================================================================
    # DISGUISE & ANONYMITY SYSTEM ATTRIBUTES
    # ===================================================================
    
    # Active skill-based disguise profile (dict with display_name, stability, etc.)
    # Set via 'disguise' command, cleared on break or manual removal
    active_disguise = AttributeProperty(None, category='disguise', autocreate=True)
    
    # Saved disguise profiles created with Disguise skill
    # Structure: {profile_id: {display_name, description, voice_override, ...}}
    disguise_profiles = AttributeProperty({}, category='disguise', autocreate=True)
    
    # Characters whose true identity this character knows (bypasses future disguises)
    # Structure: {dbref: {true_name, witnessed_at}}
    known_identities = AttributeProperty({}, category='disguise', autocreate=True)

    @property
    def gender(self):
        """
        Maps gender settings to Evennia's pronoun system.
        Returns a string suitable for use with $pron() functions.
        
        For NPCs with db.gender set (via @npc-gender), uses that directly.
        For regular characters, maps the sex attribute:
        - "male", "man", "masculine" -> "male"
        - "female", "woman", "feminine" -> "female"  
        - "ambiguous", "neutral", "non-binary", "they" -> "neutral"
        - default -> "neutral"
        """
        # Check for NPC gender setting first (set via @npc-gender command)
        if hasattr(self.db, 'gender') and self.db.gender:
            npc_gender = self.db.gender.lower().strip()
            if npc_gender in ('male', 'female', 'neutral'):
                return npc_gender
        
        # Fall back to sex attribute for regular characters
        sex_value = (self.sex or "ambiguous").lower().strip()
        
        # Male mappings
        if sex_value in ("male", "man", "masculine", "m"):
            return "male"
        # Female mappings
        elif sex_value in ("female", "woman", "feminine", "f"):
            return "female"
        # Neutral/ambiguous mappings (default)
        else:
            return "neutral"

# Possession Identifier
    def is_possessed(self):
        """
        Returns True if this character is currently puppeted by a player session.
        """
        return bool(self.sessions.all())

# Health Points - REMOVED in Phase 3: Pure Medical System
    # Legacy HP system eliminated - health now managed entirely by medical system
    # Death/unconsciousness determined by organ functionality and medical conditions

    # Character Placement Descriptions
    look_place = AttributeProperty("standing here.", category='description', autocreate=True)
    temp_place = AttributeProperty("", category='description', autocreate=True)
    override_place = AttributeProperty("", category='description', autocreate=True)
    
    def get_display_name(self, looker=None, **kwargs):
        """
        Get the display name for this character, accounting for disguises and anonymity.
        
        Identity Display Priority (highest to lowest):
        1. True name (if a slip occurred and not corrected)
        2. Active disguise display name (if skill disguise intact)
        3. Active disguise anonymity descriptor
        4. Item-based anonymity descriptor (hood up, mask on, etc.)
        5. True name (fallback)
        
        Args:
            looker: The character looking at this one
            **kwargs: Additional arguments
            
        Returns:
            str: The appropriate display name
        """
        # Import here to avoid circular imports
        try:
            from world.disguise.core import get_display_identity
            display_name, is_true = get_display_identity(self, looker)
            return display_name
        except ImportError:
            # Disguise system not available, fall back to true name
            return self.key

    def at_object_creation(self):
        """
        Called once, at creation, to set dynamic stats.
        """
        super().at_object_creation()

        # Initialize nakeds system for naked body part descriptions
        if not self.db.nakeds:
            self.db.nakeds = {}

        # Initialize combat prompt OFF by default (opt-in only)
        self.db.combat_prompt = False

        # Initialize language system
        self._initialize_language_system()

        # Initialize medical system - replaces legacy HP system
        self._initialize_medical_state()

    def _initialize_language_system(self):
        """Initialize the character's language system."""
        from world.language.utils import initialize_character_languages
        initialize_character_languages(self)

    def at_pre_move(self, destination, **kwargs):
        """
        Called before the character moves to a new location.
        Notifies windows that observe the character's current room about departure.
        Blocks movement if character is in a TerraGroup Cloning Division pod procedure.
        Cancels auto-walk if this is a manual movement.
        Cancels Gamebud typing if in progress.
        """
        # Block movement if in TerraGroup Cloning Division pod
        if getattr(self.ndb, '_movement_locked', False):
            self.msg("|yYou cannot move during the TerraGroup Cloning Division procedure.|n")
            return False
        
        # Cancel Gamebud typing if in progress (silent - no messages)
        try:
            from world.gamebud.core import cancel_gamebud_typing
            cancel_gamebud_typing(self, silent=True)
        except ImportError:
            pass  # Gamebud module not available
        
        # Cancel auto-walk if this is a MANUAL movement (not auto-walk's own moves)
        if not getattr(self.ndb, '_is_auto_walk_move', False):
            try:
                from scripts.auto_walk import cancel_auto_walk
                if cancel_auto_walk(self, silent=True):
                    self.msg("|y[Auto-walk cancelled - manual movement detected.]|n")
            except ImportError:
                pass  # Auto-walk module not available
        
        # Notify windows that observe this current room about the character leaving
        if self.location:
            self._notify_window_observers('leave', None)
        return True

    def at_post_move(self, source_location, **kwargs):
        """
        Called after the character moves to a new location.
        Shows map+room description (if mapper enabled) or plain description (if disabled).
        Also triggers window observation messages for any windows observing this room.
        Clears @temp_place when moving to a new room.
        Sends consistent movement messages for other players to see.
        """
        # Check if exit system already handled messages AND display
        exit_handled = getattr(self.ndb, "_exit_handled_messages", False)
        if exit_handled:
            # Exit system handled everything including room display, skip all at_post_move logic
            return
        
        # Send custom movement messages to maintain consistency
        if source_location and self.location != source_location:
            # Try to find the actual exit that was used
            direction = None
            exit_used = None
            
            # Check exits from source location to find which one leads to current location
            if hasattr(source_location, 'exits'):
                for exit_obj in source_location.exits:
                    if exit_obj and hasattr(exit_obj, 'destination') and exit_obj.destination == self.location:
                        exit_used = exit_obj
                        direction = exit_obj.key.lower()
                        break
            
            # Fall back to coordinate-based direction if no exit found
            if not direction:
                direction = self._get_direction_from_rooms(source_location, self.location)
            
            # Send departure message to old location
            leave_msg = f"{self.name} leaves for the {direction}." if direction else f"{self.name} leaves."
            source_location.msg_contents(leave_msg, exclude=[self])
            
            # For arrival, show opposite direction (e.g., if went OUT, arrived from IN)
            opposite_direction = self._get_opposite_direction(direction) if direction else None
            arrive_msg = f"{self.name} arrives from the {opposite_direction}." if opposite_direction else f"{self.name} arrives."
            self.location.msg_contents(arrive_msg, exclude=[self])
        
        # Clear temp_place when changing rooms
        if hasattr(self.ndb, 'temp_place'):
            delattr(self.ndb, 'temp_place')
        
        # Check if player has a municipal wristpad WORN - required for map display
        from world.safetynet.utils import has_municipal_wristpad
        has_wristpad = has_municipal_wristpad(self)
        
        # Sync ndb with persistent state based on wristpad
        self.ndb.mapper_enabled = has_wristpad
        self.ndb.show_room_desc = not has_wristpad
        
        if has_wristpad:
            # Show map view (which includes room description)
            from commands.mapper import CmdMap
            cmd = CmdMap()
            cmd.caller = self
            cmd.args = ""
            cmd.func()
        else:
            # Show plain room description without map
            appearance = self.location.return_appearance(self, force_display=True)
            self.msg(appearance)

        # Notify windows that observe entry/exit in this room
        self._notify_window_observers('enter', source_location)
    def at_look(self, target=None, **kwargs):
        """
        Called when the character uses the look command.
        When looking at the room (or nothing), shows the room and map (if mapper enabled).
        When looking at an object/character, shows their description.
        """
        if target is None or target == self.location:
            # Looking at the room
            # Check if player has a municipal wristpad WORN - required for map display
            from world.safetynet.utils import has_municipal_wristpad
            has_wristpad = has_municipal_wristpad(self)
            
            # Sync ndb with persistent state based on wristpad
            self.ndb.mapper_enabled = has_wristpad
            self.ndb.show_room_desc = not has_wristpad
            
            if has_wristpad:
                # Show map view with room description on right side
                from commands.mapper import CmdMap
                cmd = CmdMap()
                cmd.caller = self
                cmd.args = ""
                cmd.func()
                return
            else:
                # No wristpad - show plain room description
                appearance = self.location.return_appearance(self, force_display=True)
                return appearance
        else:
            # Looking at an object/character - show their description
            return target.return_appearance(self)

    def _notify_window_observers(self, movement_type, previous_location):
        """
        Notify windows that observe this character's current room.

        Args:
            movement_type: 'enter' or 'leave'
            previous_location: The location the character came from (only used for 'enter')
        """
        # Check if character has required attributes (location and coordinates)
        if not self.location or not hasattr(self.location.db, 'x') or not hasattr(self.location.db, 'y'):
            return

        current_x = self.location.db.x
        current_y = self.location.db.y
        current_z = getattr(self.location.db, 'z', 0)

        # Find all windows everywhere that observe this room
        from evennia.objects.models import ObjectDB
        all_windows = ObjectDB.objects.filter(db_typeclass_path='typeclasses.window.Window')

        for window_obj in all_windows:
            try:
                # Check if window targets this room
                if (window_obj.db.target_x == current_x and
                    window_obj.db.target_y == current_y and
                    window_obj.db.target_z == current_z):

                    # Determine direction if available
                    direction = None
                    if movement_type == 'enter' and previous_location:
                        direction = self._get_direction_from_rooms(previous_location, self.location)

                    # Call the window's relay method
                    window_obj.relay_movement(self, movement_type, direction)
            except (AttributeError, TypeError):
                # Skip if window doesn't have required attributes
                pass

    def _get_opposite_direction(self, direction):
        """
        Get the opposite direction for a given direction.
        
        Args:
            direction: A direction string (north, south, east, west, up, down, in, out, etc)
            
        Returns:
            The opposite direction string, or None if direction not recognized
        """
        opposites = {
            "north": "south",
            "south": "north",
            "east": "west",
            "west": "east",
            "northeast": "southwest",
            "northwest": "southeast",
            "southeast": "northwest",
            "southwest": "northeast",
            "up": "down",
            "down": "up",
            "in": "out",
            "out": "in"
        }
        return opposites.get(direction.lower()) if direction else None

    def _get_direction_from_rooms(self, from_room, to_room):
        """
        Determine the direction from one room to another.

        Args:
            from_room: The source room
            to_room: The destination room

        Returns:
            Direction string or None
        """
        if not from_room or not to_room:
            return None

        # Get coordinates
        from_x = getattr(from_room.db, 'x', None)
        from_y = getattr(from_room.db, 'y', None)
        to_x = getattr(to_room.db, 'x', None)
        to_y = getattr(to_room.db, 'y', None)

        if None in (from_x, from_y, to_x, to_y):
            return None

        # Calculate direction, including diagonals
        dx = to_x - from_x
        dy = to_y - from_y

        # Handle diagonals first (both dx and dy are non-zero)
        if dx > 0 and dy > 0:
            return "northeast"
        elif dx < 0 and dy > 0:
            return "northwest"
        elif dx > 0 and dy < 0:
            return "southeast"
        elif dx < 0 and dy < 0:
            return "southwest"
        # Handle cardinal directions
        elif dy > 0:
            return "north"
        elif dy < 0:
            return "south"
        elif dx > 0:
            return "east"
        elif dx < 0:
            return "west"

        return None

    def _initialize_medical_state(self):
        """Initialize the character's medical state."""
        from world.medical.utils import initialize_character_medical_state
        initialize_character_medical_state(self)

    def move_to(self, destination, quiet=False, emit_to_obj=None, use_destination=True, **kwargs):
        """
        Override move_to to handle follower movement and suppress default Evennia messages.
        We handle our own custom directional messages in at_post_move() instead.
        When a character moves, their followers move with them.
        """
        # Store the original location for follow system and custom messages
        original_location = self.location
        
        # Always use quiet=True to suppress Evennia's default "arrives to Zone X from Y" messages
        # We generate our own custom directional messages in at_post_move() instead
        result = super().move_to(destination, quiet=True, emit_to_obj=emit_to_obj, use_destination=use_destination, **kwargs)
        
        # Handle followers after successful move
        if result and original_location and self.location != original_location:
            # Trigger the follow system
            try:
                from scripts.follow_system import handle_character_move
                handle_character_move(self, self.location, original_location)
            except Exception as e:
                # Don't break movement if follow system fails
                pass
        
        return result


    @property
    def medical_state(self):
        """Get the character's medical state, loading from db if needed."""
        if not hasattr(self, '_medical_state') or self._medical_state is None:
            from world.medical.utils import load_medical_state
            load_medical_state(self)
        return self._medical_state
        
    @medical_state.setter
    def medical_state(self, value):
        """Set the character's medical state."""
        self._medical_state = value
        
    def save_medical_state(self):
        """Save medical state to database."""
        from world.medical.utils import save_medical_state
        save_medical_state(self)

    def msg(self, text=None, from_obj=None, session=None, **kwargs):
        """
        Override msg method to implement death message filtering and combat prompt appending.
        
        Dead characters receive only death-related messages for immersion.
        The _death_curtain_active flag bypasses ALL filtering.
        Combat prompt is appended to every message when in combat with prompt enabled.
        """
        # If not dead, use normal messaging
        if not self.is_dead():
            # Append combat prompt if in combat
            text = self._append_combat_prompt(text)
            return super().msg(text=text, from_obj=from_obj, session=session, **kwargs)
        
        # CRITICAL: Allow ALL messages when death curtain/progression flag is set
        # This is the main mechanism for death messages to get through
        if getattr(self.ndb, '_death_curtain_active', False):
            text = self._append_combat_prompt(text)
            return super().msg(text=text, from_obj=from_obj, session=session, **kwargs)
        
        # Also allow if in active death progression
        if getattr(self.ndb, '_death_progression_active', False):
            text = self._append_combat_prompt(text)
            return super().msg(text=text, from_obj=from_obj, session=session, **kwargs)
            
        # No text = nothing to filter
        if not text:
            return
            
        # Allow messages from staff (for admin commands)
        if from_obj and hasattr(from_obj, 'locks'):
            try:
                if from_obj.locks.check(from_obj, "perm(Builder)"):
                    if not self._is_social_message(text, kwargs):
                        text = self._append_combat_prompt(text)
                        return super().msg(text=text, from_obj=from_obj, session=session, **kwargs)
            except:
                pass
            
        # Block all other messages for immersion - dead characters see nothing
        return
    
    def _append_combat_prompt(self, text):
        """
        Append status prompt to the end of a message showing vitals.
        
        Requires:
        - Combat prompt enabled (combat_prompt = True)
        - Character has a municipal wristpad (without it, prompt cannot display)
        
        Args:
            text: The original message text
            
        Returns:
            str: Text with status prompt appended if enabled, otherwise original text
        """
        # Check if prompt is disabled (default is OFF - must be explicitly True)
        # Use explicit True check since unset attributes may return None
        if not getattr(self.db, 'combat_prompt', False) is True:
            return text
        
        # Check if character has a municipal wristpad - cannot display prompt without it
        from world.safetynet.utils import has_municipal_wristpad
        if not has_municipal_wristpad(self):
            return text
        
        # Don't show during death, cloning, or revival sequences
        if self.is_dead():
            return text
        if getattr(self.ndb, '_death_curtain_active', False):
            return text
        if getattr(self.ndb, '_death_progression_active', False):
            return text
        if getattr(self.ndb, '_cloning_active', False):
            return text
        if getattr(self.ndb, '_revival_active', False):
            return text
        
        # Build status prompt
        parts = []
        
        # --- HEALTH STATUS (Blood Level) ---
        blood_level = 100.0
        if hasattr(self, 'medical_state') and self.medical_state:
            blood_level = getattr(self.medical_state, 'blood_level', 100.0)
        
        if blood_level > 75:
            health_color = "|g"
            health_status = "Healthy"
        elif blood_level > 50:
            health_color = "|y"
            health_status = "Wounded"
        elif blood_level > 25:
            health_color = "|r"
            health_status = "Injured"
        else:
            health_color = "|R"
            health_status = "Critical"
        
        parts.append(f"{health_color}Blood: {blood_level:.0f}% ({health_status})|n")
        
        # --- BLEEDING STATUS ---
        is_bleeding = False
        bleed_rate = 0
        if hasattr(self, 'medical_state') and self.medical_state:
            bleed_rate = self.medical_state.calculate_blood_loss_rate()
            is_bleeding = bleed_rate > 0
        
        if is_bleeding and bleed_rate > 0:
            if bleed_rate >= 3:
                parts.append("|R[BLEEDING HEAVILY]|n")
            elif bleed_rate >= 1.5:
                parts.append("|r[BLEEDING]|n")
            else:
                parts.append("|y[bleeding]|n")
        
        # --- STAMINA STATUS ---
        stamina = getattr(self.ndb, "stamina", None)
        if stamina:
            stam_pct = (stamina.stamina_current / stamina.stamina_max * 100) if stamina.stamina_max > 0 else 0
            if stam_pct > 50:
                stam_color = "|g"
            elif stam_pct > 20:
                stam_color = "|y"
            else:
                stam_color = "|r"
            parts.append(f"{stam_color}Stamina: {stam_pct:.0f}%|n")
        
        # --- CRITICAL ORGAN DAMAGE ---
        critical_organs = []
        if hasattr(self, 'medical_state') and self.medical_state:
            for organ_name, organ in self.medical_state.organs.items():
                if hasattr(organ, 'get_functionality_percentage'):
                    functionality = organ.get_functionality_percentage()
                    if functionality < 0.25 and organ.current_hp < organ.max_hp:
                        critical_organs.append(organ_name.replace('_', ' '))
        
        if critical_organs:
            organ_list = ", ".join(critical_organs)
            parts.append(f"|R[CRITICAL: {organ_list}]|n")
        
        # Append prompt to text
        if parts:
            prompt = " | ".join(parts)
            if isinstance(text, str):
                return f"{text}\n{prompt}"
            elif isinstance(text, tuple) and len(text) >= 1:
                # Handle (text, options) format
                return (f"{text[0]}\n{prompt}", text[1]) if len(text) > 1 else (f"{text[0]}\n{prompt}",)
        
        return text
        
    def _is_social_message(self, text, kwargs):
        """
        Determine if this is a social message that should be blocked even for staff.
        
        Args:
            text: Message text
            kwargs: Message parameters
            
        Returns:
            bool: True if this is a social message, False otherwise
        """
        # Check for social message indicators
        if isinstance(kwargs.get('type'), str):
            social_types = ['say', 'pose', 'emote', 'tell', 'whisper', 'ooc']
            if kwargs['type'] in social_types:
                return True
                
        # Check text patterns for social messages
        if isinstance(text, str):
            social_patterns = [' says, "', ' tells you', ' whispers', ' emotes']
            for pattern in social_patterns:
                if pattern in text:
                    return True
                    
        return False

# Mortality Management
    def take_damage(self, amount, location="chest", injury_type="generic", target_organ=None):
        """
        Apply damage to a specific body location with injury type.
        
        This is the primary damage method using the pure medical system.
        Replaces the old dual HP/medical approach.
        
        Args:
            amount (int): Damage amount
            location (str): Body location (head, chest, left_arm, etc.)
            injury_type (str): Type of injury (cut, blunt, bullet, etc.)
            target_organ (str): If specified, target this specific organ
            
        Returns:
            tuple: (died: bool, actual_damage: int) - Whether character died and actual damage applied after armor
        """
        if not isinstance(amount, int) or amount <= 0:
            return (False, 0)

        # Check for armor before applying damage
        final_damage = self._calculate_armor_damage_reduction(amount, location, injury_type)
        
        # Calculate armor protection for condition reduction
        armor_absorbed = amount - final_damage
        armor_protection_ratio = armor_absorbed / amount if amount > 0 else 0.0
        
        # Debug log damage before and after armor
        try:
            from world.combat.utils import debug_broadcast
            if final_damage < amount:
                debug_broadcast(f"{self.key} took {amount} raw damage → armor absorbed {armor_absorbed} → {final_damage} damage applied (protection: {armor_protection_ratio:.1%})", 
                               "DAMAGE", "ARMOR_CALC")
            else:
                debug_broadcast(f"{self.key} took {amount} raw damage (no armor protection)", 
                               "DAMAGE", "NO_ARMOR")
        except ImportError:
            pass
        
        # Apply anatomical damage through medical system
        # Pass armor protection ratio to reduce chance of bleeding/bruising/cuts
        from world.medical.utils import apply_anatomical_damage
        damage_results = apply_anatomical_damage(self, final_damage, location, injury_type, target_organ, armor_protection_ratio)
        
        # Save medical state after damage
        self.save_medical_state()
        
        # Debug broadcast damage application
        try:
            from world.combat.utils import debug_broadcast
            debug_broadcast(f"Applied {final_damage} {injury_type} damage to {self.key}'s {location}", 
                           "DAMAGE", "SUCCESS")
        except ImportError:
            pass  # debug_broadcast not available
        
        # Handle death/unconsciousness state changes
        died = self.is_dead()
        unconscious = self.is_unconscious()
        
        if died:
            self.at_death()  # Direct call to main death handler
        elif unconscious:
            self._handle_unconsciousness()
        
        # Return death status and actual damage applied (after armor) for combat system
        return (died, final_damage)
    
    def _calculate_armor_damage_reduction(self, damage, location, injury_type):
        """
        Calculate damage reduction from stacked armor at the specified location.
        
        Integrates with clothing system - processes all armor layers for cumulative protection.
        
        Args:
            damage (int): Original damage amount
            location (str): Body location being hit
            injury_type (str): Type of damage (bullet, cut, stab, blunt, etc.)
            
        Returns:
            int: Final damage after armor reduction from all layers
        """
        # If no clothing system available, no armor protection
        if not hasattr(self, 'db') or not self.db.worn_items:
            return damage
            
        # Find all armor covering this location, sorted by layer (outermost first)
        armor_layers = []
        # Cache coverage calculations and track seen items to avoid duplicates
        coverage_cache = {}
        seen_items = set()
        
        for loc, items in self.db.worn_items.items():
            for item in items:
                # Skip if we've already processed this item
                if id(item) in seen_items:
                    continue
                seen_items.add(id(item))
                
                # Check if this item covers the hit location and has armor rating
                # Use cached coverage to avoid repeated function calls
                if item not in coverage_cache:
                    coverage_cache[item] = getattr(item, 'get_current_coverage', lambda: getattr(item, 'coverage', []))()
                current_coverage = coverage_cache[item]
                
                if location in current_coverage:
                    # Check if this is a plate carrier - needs special handling
                    if (hasattr(item, 'is_plate_carrier') and 
                        getattr(item, 'is_plate_carrier', False)):
                        # DEBUG: Log plate carrier detection
                        try:
                            from world.combat.utils import debug_broadcast
                            installed = getattr(item, 'installed_plates', {})
                            debug_broadcast(f"PLATE_CARRIER detected: {item.key} for {location}, installed_plates={list(installed.keys())}", 
                                           "ARMOR_CALC", "DEBUG")
                        except:
                            pass
                        # Expand plate carrier into multiple sequential layers
                        carrier_layers = self._expand_plate_carrier_layers(item, location)
                        # DEBUG: Log expansion results
                        try:
                            from world.combat.utils import debug_broadcast
                            debug_broadcast(f"PLATE_EXPAND: {len(carrier_layers)} layers created from {item.key}", 
                                           "ARMOR_CALC", "DEBUG")
                            for layer in carrier_layers:
                                debug_broadcast(f"  Layer {layer['layer']}: {layer['item'].key} ({layer['armor_type']}, rating={layer['armor_rating']})", 
                                               "ARMOR_CALC", "DEBUG")
                        except:
                            pass
                        armor_layers.extend(carrier_layers)
                    else:
                        # Regular armor - single layer
                        armor_rating = getattr(item, 'armor_rating', 0)
                        if armor_rating > 0:
                            armor_layers.append({
                                'item': item,
                                'layer': getattr(item, 'layer', 2),
                                'armor_rating': armor_rating,
                                'armor_type': getattr(item, 'armor_type', 'generic')
                            })
        
        if not armor_layers:
            return damage  # No armor at this location
            
        # Sort by layer (outermost first) - higher layer numbers are outer
        armor_layers.sort(key=lambda x: x['layer'], reverse=True)
        
        # Apply armor layers sequentially (outer to inner)
        remaining_damage = damage
        total_damage_reduction = 0
        armor_debug_info = []
        
        for armor_layer in armor_layers:
            if remaining_damage <= 0:
                break  # No damage left to absorb
                
            item = armor_layer['item']
            # Safety check: ensure item still exists (edge case: deleted mid-combat)
            if not item or not hasattr(item, 'pk') or not item.pk:
                continue
                
            armor_rating = armor_layer['armor_rating']
            armor_type = armor_layer['armor_type']
            
            # Calculate this layer's damage reduction
            base_reduction_percent = self._get_armor_effectiveness(armor_type, injury_type, armor_rating)
            
            # Apply weakness exploitation if present
            weakness_penalty = armor_layer.get('weakness_exploited', 0.0)
            final_reduction_percent = max(0.0, base_reduction_percent - weakness_penalty)
            
            # Use round() instead of int() to avoid losing effectiveness on low damage
            layer_damage_reduction = round(remaining_damage * final_reduction_percent)
            
            # Apply the reduction
            remaining_damage = max(0, remaining_damage - layer_damage_reduction)
            total_damage_reduction += layer_damage_reduction
            
            # Degrade this armor layer
            self._degrade_armor(item, layer_damage_reduction)
            
            # Track for debug output
            if layer_damage_reduction > 0:
                effectiveness_display = f"{final_reduction_percent*100:.0f}%"
                if weakness_penalty > 0:
                    effectiveness_display += f"(-{weakness_penalty*100:.0f}%)"
                armor_debug_info.append(f"{item.key}({effectiveness_display}={layer_damage_reduction}dmg)")
        
        # Debug broadcast armor effectiveness
        try:
            from world.combat.utils import debug_broadcast
            if total_damage_reduction > 0:
                debug_info = " + ".join(armor_debug_info)
                debug_broadcast(f"Armor absorbed {total_damage_reduction} damage: {debug_info} for {self.key}", 
                               "ARMOR", "SUCCESS")
        except ImportError:
            pass
            
        return int(remaining_damage)  # Ensure return type is always int
    
    def _expand_plate_carrier_layers(self, carrier, location):
        """
        Expand a plate carrier into multiple armor layers for the specified location.
        
        Each layer (base carrier + each applicable plate) gets processed separately
        with its own armor type and effectiveness calculation.
        
        Args:
            carrier: The plate carrier item
            location (str): Hit location (e.g., "chest", "back", "abdomen")
            
        Returns:
            list: List of armor layer dicts, each with item, layer, armor_rating, armor_type
        """
        layers = []
        base_layer_number = getattr(carrier, 'layer', 2)
        
        # Plates are outer layers (higher number = processed first)
        plate_layer_number = base_layer_number + 1
        
        # Layer 1: Base carrier (always present if carrier has rating)
        base_rating = getattr(carrier, 'armor_rating', 0)
        if base_rating > 0:
            layers.append({
                'item': carrier,
                'layer': base_layer_number,  # Inner layer
                'armor_rating': base_rating,
                'armor_type': getattr(carrier, 'armor_type', 'generic')
            })
        
        # Layer 2+: Installed plates that protect this location
        if hasattr(carrier, 'installed_plates'):
            installed_plates = carrier.db.installed_plates or {}
            slot_coverage = carrier.db.plate_slot_coverage or {}
            
            # DEBUG: Log what we're working with
            try:
                from world.combat.utils import debug_broadcast
                debug_broadcast(f"PLATE_LOOP: Processing {len(installed_plates)} slots for {location}", 
                               "ARMOR_CALC", "DEBUG")
                debug_broadcast(f"PLATE_LOOP: installed_plates type={type(installed_plates)}, value={installed_plates}", 
                               "ARMOR_CALC", "DEBUG")
                debug_broadcast(f"PLATE_LOOP: slot_coverage={slot_coverage}", 
                               "ARMOR_CALC", "DEBUG")
            except:
                pass
            
            for slot_name, plate in installed_plates.items():
                # DEBUG: Log each slot
                try:
                    from world.combat.utils import debug_broadcast
                    plate_type = type(plate).__name__ if plate else "None"
                    plate_key = plate.key if plate and hasattr(plate, 'key') else "N/A"
                    plate_layer = getattr(plate, 'layer', 'MISSING') if plate else "N/A"
                    debug_broadcast(f"PLATE_SLOT: slot={slot_name}, type={plate_type}, key={plate_key}, layer={plate_layer}, has_rating={hasattr(plate, 'armor_rating') if plate else False}", 
                                   "ARMOR_CALC", "DEBUG")
                except Exception as e:
                    from world.combat.utils import debug_broadcast
                    debug_broadcast(f"PLATE_SLOT_ERROR: {e}", "ARMOR_CALC", "ERROR")
                    pass
                    
                if not plate or not hasattr(plate, 'armor_rating'):
                    continue
                
                # Check if this plate protects the hit location
                protected_locations = slot_coverage.get(slot_name, [])
                # DEBUG: Log coverage check
                try:
                    from world.combat.utils import debug_broadcast
                    debug_broadcast(f"PLATE_COVERAGE: slot={slot_name}, protects={protected_locations}, location={location}, match={location in protected_locations}", 
                                   "ARMOR_CALC", "DEBUG")
                except:
                    pass
                if location not in protected_locations:
                    continue
                
                # Get plate's armor properties
                plate_rating = getattr(plate, 'armor_rating', 0)
                plate_type = getattr(plate, 'armor_type', 'generic')
                
                # For abdomen with 2 side plates, each contributes half its rating
                # This is because side plates are angled and only partially cover abdomen
                if location == "abdomen" and slot_name in ["left_side", "right_side"]:
                    plate_rating = plate_rating // 2
                
                if plate_rating > 0:
                    layers.append({
                        'item': plate,  # Reference the plate itself for degradation
                        'layer': plate_layer_number,  # Outer layer - processed before carrier
                        'armor_rating': plate_rating,
                        'armor_type': plate_type  # Use plate's material, not carrier's
                    })
        
        return layers

    
    def _get_total_armor_rating(self, item, location=None):
        """
        Get total armor rating for an item, including installed plates for carriers.
        For plate carriers, only counts plates in slots that protect the specified location.
        
        Args:
            item: The armor item to evaluate
            location (str): Hit location to check (e.g., "chest", "back", "torso")
            
        Returns:
            int: Total armor rating (base item + installed plates)
        """
        base_rating = getattr(item, 'armor_rating', 0)
        
        # Check if this is a plate carrier with installed plates
        if (hasattr(item, 'is_plate_carrier') and 
            getattr(item, 'is_plate_carrier', False) and
            hasattr(item, 'installed_plates')):
            
            installed_plates = getattr(item, 'installed_plates', {})
            plate_rating_bonus = 0
            
            # Get slot-to-location mapping (if available)
            slot_coverage = getattr(item, 'plate_slot_coverage', {})
            
            for slot_name, plate in installed_plates.items():
                if plate and hasattr(plate, 'armor_rating'):
                    # If location is specified and we have slot coverage mapping,
                    # only count plates that protect this location
                    if location and slot_coverage:
                        protected_locations = slot_coverage.get(slot_name, [])
                        if location not in protected_locations:
                            continue  # This plate doesn't protect this location
                    
                    plate_rating_bonus += getattr(plate, 'armor_rating', 0)
            
            return base_rating + plate_rating_bonus
        
        return base_rating
    
    def _get_armor_effectiveness(self, armor_type, injury_type, armor_rating):
        """
        Calculate armor effectiveness percentage based on armor type vs injury type.
        
        Args:
            armor_type (str): Type of armor (kevlar, steel, leather, etc.)
            injury_type (str): Type of incoming damage
            armor_rating (int): Armor rating (1-10 scale)
            
        Returns:
            float: Damage reduction percentage (0.0 to 0.95)
        """
        from world.combat.constants import ARMOR_EFFECTIVENESS_MATRIX
        
        # Get base effectiveness from centralized matrix
        base_effectiveness = ARMOR_EFFECTIVENESS_MATRIX.get(
            armor_type, 
            ARMOR_EFFECTIVENESS_MATRIX['generic']
        )
        effectiveness = base_effectiveness.get(injury_type, 0.2)  # Default 20% for unknown damage types
        
        # Scale by armor rating (1-10 becomes 0.1-1.0 multiplier)
        rating_multiplier = min(1.0, armor_rating / 10.0)
        final_effectiveness = effectiveness * rating_multiplier
        
        # Cap at 95% damage reduction to prevent invulnerability
        return min(0.95, final_effectiveness)
    
    def _degrade_armor(self, armor_item, damage_absorbed):
        """
        Degrade armor durability based on damage absorbed.
        
        Args:
            armor_item: The armor item that absorbed damage
            damage_absorbed (int): Amount of damage the armor absorbed
        """
        if not hasattr(armor_item, 'armor_durability'):
            # Initialize durability if not set
            max_durability = getattr(armor_item, 'armor_rating', 5) * 20  # Rating * 20 = max durability
            armor_item.armor_durability = max_durability
            armor_item.max_armor_durability = max_durability
        
        # Reduce durability
        armor_item.armor_durability = max(0, armor_item.armor_durability - damage_absorbed)
        
        # Calculate current effectiveness
        durability_percent = armor_item.armor_durability / armor_item.max_armor_durability
        original_rating = getattr(armor_item, 'base_armor_rating', armor_item.armor_rating)
        
        # Degrade armor rating based on durability
        armor_item.armor_rating = max(1, int(original_rating * durability_percent))
        
        # Store original rating if not already stored
        if not hasattr(armor_item, 'base_armor_rating'):
            armor_item.base_armor_rating = original_rating
    
    # Legacy method take_anatomical_damage removed - functionality merged into take_damage()
    
    def is_admin(self):
        """
        Check if this character's account has admin/builder permissions.
        
        Returns:
            bool: True if character is controlled by an admin/builder account
        """
        # Check if we have an account with admin perms
        if hasattr(self, 'account') and self.account:
            return self.account.check_permstring("Builder") or self.account.check_permstring("Admin") or self.account.check_permstring("Developer")
        return False
    
    def is_dead(self):
        """
        Returns True if character should be considered dead.
        
        Uses pure medical system - death from vital organ failure or blood loss.
        Admins are immortal and cannot die.
        """
        # Admins are immortal - never considered dead
        if self.is_admin():
            # If admin somehow has death state, auto-heal them
            self._admin_auto_heal()
            return False
        
        try:
            medical_state = self.medical_state
            if medical_state:
                return medical_state.is_dead()
        except AttributeError:
            pass  # Medical system not available - character is alive
        
        return False
    
    def _admin_auto_heal(self):
        """
        Auto-heal admins if they have critical injuries that would cause death.
        Called when an admin's death state is checked and they have fatal damage.
        """
        try:
            medical_state = self.medical_state
            if medical_state and medical_state.is_dead():
                # Reset vital organs to functional state
                from world.medical.utils import full_heal
                full_heal(self)
                self.msg("|y[Admin Protection] You have been automatically healed from fatal injuries.|n")
                
                # Clear death flags
                if hasattr(self.db, 'death_processed'):
                    del self.db.death_processed
                if hasattr(self.ndb, 'death_processed'):
                    del self.ndb.death_processed
                if hasattr(self.ndb, 'death_curtain_pending'):
                    del self.ndb.death_curtain_pending
                    
                # Clear override place if it was set for death
                if hasattr(self, 'override_place') and 'deceased' in str(self.override_place).lower():
                    self.override_place = None
        except Exception:
            pass  # Silently fail if medical system not available
        
    def is_unconscious(self):
        """
        Returns True if character is unconscious.
        
        Uses medical system to determine unconsciousness from injuries,
        blood loss, or pain.
        """
        try:
            medical_state = self.medical_state
            if medical_state:
                return medical_state.is_unconscious()
        except AttributeError:
            pass  # Medical system not available
        return False

    def _handle_unconsciousness(self):
        """
        Handle character becoming unconscious from medical injuries.
        
        Provides unconsciousness messaging to character and room.
        Triggers removal from combat if currently fighting.
        """
        from evennia.comms.models import ChannelDB
        from world.combat.constants import SPLATTERCAST_CHANNEL, NDB_COMBAT_HANDLER
        from evennia.utils.utils import delay
        
        # Prevent double unconsciousness processing
        if hasattr(self, 'ndb') and getattr(self.ndb, 'unconsciousness_processed', False):
            try:
                splattercast = ChannelDB.objects.get_channel(SPLATTERCAST_CHANNEL)
                splattercast.msg(f"UNCONSCIOUS_SKIP: {self.key} already processed unconsciousness, skipping")
            except:
                pass
            return
            
        # Mark unconsciousness as processed
        if not hasattr(self, 'ndb'):
            self.ndb = {}
        self.ndb.unconsciousness_processed = True
        
        # Set unconscious placement description
        self.override_place = "unconscious and motionless."
        
        # Check if character is in active combat - if so, defer unconsciousness message
        is_in_combat = hasattr(self.ndb, NDB_COMBAT_HANDLER) and getattr(self.ndb, NDB_COMBAT_HANDLER) is not None
        
        if is_in_combat:
            # Set flag for combat system to trigger unconsciousness message after attack message
            self.ndb.unconsciousness_pending = True
            try:
                splattercast = ChannelDB.objects.get_channel(SPLATTERCAST_CHANNEL)
                splattercast.msg(f"UNCONSCIOUS_COMBAT: {self.key} unconsciousness message deferred - in active combat")
            except:
                pass
            
            # Safety fallback - trigger message after 5 seconds if combat doesn't handle it
            def fallback_unconsciousness_message():
                if hasattr(self.ndb, 'unconsciousness_pending') and self.ndb.unconsciousness_pending:
                    try:
                        splattercast = ChannelDB.objects.get_channel(SPLATTERCAST_CHANNEL)
                        splattercast.msg(f"UNCONSCIOUS_FALLBACK: {self.key} triggering fallback unconsciousness message")
                    except:
                        pass
                    self._show_unconsciousness_message()
                    self.ndb.unconsciousness_pending = False
            
            delay(5, fallback_unconsciousness_message)
        else:
            # Not in combat - show unconsciousness message immediately
            self._show_unconsciousness_message()

    def _show_unconsciousness_message(self):
        """
        Show the unconsciousness message to character and room.
        Separated from _handle_unconsciousness for deferred messaging coordination.
        
        NOTE: Messages commented out to avoid duplicates with consciousness suppression conditions.
        """
        # self.msg("|rYou collapse, unconscious from your injuries!|n")
        # if self.location:
        #     self.location.msg_contents(
        #         f"|r{self.key} collapses, unconscious!|n",
        #         exclude=self
        #     )
        
        # Check if character is in combat and remove them
        combat_handler = getattr(self.ndb, "combat_handler", None)
        if combat_handler:
            try:
                combat_handler.remove_combatant(self)
                # Optional: Debug broadcast for tracking
                try:
                    from world.combat.utils import debug_broadcast
                    debug_broadcast(f"{self.key} removed from combat due to unconsciousness", "MEDICAL", "UNCONSCIOUS")
                except ImportError:
                    pass  # debug_broadcast not available
            except Exception as e:
                # Optional: Debug broadcast for tracking errors
                try:
                    from world.combat.utils import debug_broadcast
                    debug_broadcast(f"Error removing {self.key} from combat on unconsciousness: {e}", "MEDICAL", "ERROR")
                except ImportError:
                    pass  # debug_broadcast not available
        
        # Optional: Debug broadcast for tracking
        try:
            from world.combat.utils import debug_broadcast
            debug_broadcast(f"{self.key} became unconscious from medical injuries", "MEDICAL", "UNCONSCIOUS")
        except ImportError:
            pass  # debug_broadcast not available
        
        # Apply unconscious command restrictions
        self.apply_unconscious_state()

    def debug_death_analysis(self):
        """
        Debug method to show detailed cause of death analysis.
        Returns comprehensive information about why character died or current vital status.
        """
        try:
            medical_state = self.medical_state
            if not medical_state:
                return "No medical state available"
            
            from world.medical.constants import BLOOD_LOSS_DEATH_THRESHOLD
            
            # Check vital organ capacities
            blood_pumping = medical_state.calculate_body_capacity("blood_pumping")
            breathing = medical_state.calculate_body_capacity("breathing") 
            digestion = medical_state.calculate_body_capacity("digestion")
            consciousness = medical_state.calculate_body_capacity("consciousness")
            
            # Check blood level
            blood_level = medical_state.blood_level
            blood_loss_fatal = blood_level <= (100.0 - BLOOD_LOSS_DEATH_THRESHOLD)
            
            # Build analysis
            analysis = [
                f"=== DEATH ANALYSIS FOR {self.key} ===",
                f"Blood Pumping Capacity: {blood_pumping:.1%} {'FATAL' if blood_pumping <= 0 else 'OK'}",
                f"Breathing Capacity: {breathing:.1%} {'FATAL' if breathing <= 0 else 'OK'}",
                f"Digestion Capacity: {digestion:.1%} {'FATAL' if digestion <= 0 else 'OK'}",
                f"Consciousness: {consciousness:.1%} {'UNCONSCIOUS' if consciousness < 0.3 else 'CONSCIOUS'}",
                f"Blood Level: {blood_level:.1f}% {'FATAL BLOOD LOSS' if blood_loss_fatal else 'OK'}",
                f"Pain Level: {medical_state.pain_level:.1f}",
                f"Overall Status: {'DEAD' if self.is_dead() else 'ALIVE'}"
            ]
            
            # If dead, identify primary cause
            if self.is_dead():
                causes = []
                if blood_pumping <= 0:
                    causes.append("HEART FAILURE")
                if breathing <= 0:
                    causes.append("RESPIRATORY FAILURE") 
                if digestion <= 0:
                    causes.append("LIVER FAILURE")
                if blood_loss_fatal:
                    causes.append("BLOOD LOSS")
                
                analysis.append(f"Primary Cause(s): {', '.join(causes)}")
            
            return "\n".join(analysis)
            
        except Exception as e:
            return f"Error in death analysis: {e}"
    
    def archive_character(self, reason="manual", disconnect_msg=None):
        """
        Archive this character and disconnect any active sessions.
        
        Args:
            reason (str): Why the character is being archived (e.g., "death", "manual")
            disconnect_msg (str): Optional custom disconnect message. If None, uses default.
        """
        import time
        
        # Log warning if archiving a staff character (shouldn't happen normally)
        if self.account and self.account.is_superuser:
            try:
                splattercast = ChannelDB.objects.get_channel("Splattercast")
                splattercast.msg(f"WARNING: Archiving staff character {self.key} (Account: {self.account.key}, Reason: {reason})")
            except:
                pass
        
        # Set account's last_character for respawn flow
        if self.account:
            self.account.db.last_character = self
            
            # CRITICAL: Remove character from account's character list
            # This allows a new character to be created (MAX_NR_CHARACTERS=1)
            if self in self.account.characters:
                self.account.characters.remove(self)
                try:
                    splattercast = ChannelDB.objects.get_channel("Splattercast")
                    splattercast.msg(f"ARCHIVE: Removed {self.key} from {self.account.key}'s character list")
                except:
                    pass
        
        # Increment death_count for proper Roman numeral naming on respawn
        # (This ensures "Jorge Jackson" -> "Jorge Jackson II" etc.)
        self.death_count += 1
        
        # Set archive flags
        self.db.archived = True
        self.db.archived_reason = reason
        self.db.archived_date = time.time()
        
        # Move character to Limbo to prevent appearing as NPC in game world
        from evennia import search_object
        limbo = search_object("#2")  # Limbo is always dbref #2
        if limbo:
            limbo = limbo[0]
            current_location = self.location
            self.move_to(limbo, quiet=True, move_hooks=False)
            
            # Log the move
            try:
                splattercast = ChannelDB.objects.get_channel("Splattercast")
                splattercast.msg(f"ARCHIVE: Moved {self.key} from {current_location.key if current_location else 'None'} to Limbo")
            except:
                pass
        
        # Disconnect any active sessions
        if self.sessions.all():
            if not disconnect_msg:
                disconnect_msg = "|ySleeve has been archived. Please reconnect to continue.|n"
            
            for session in self.sessions.all():
                session.sessionhandler.disconnect(session, reason=disconnect_msg)
    
    def get_death_cause(self):
        """
        Get simple death cause for user-facing messages.
        
        Returns:
            str: Simple death cause description or None if not dead
        """
        if not self.is_dead():
            return None
            
        try:
            medical_state = self.medical_state
            if not medical_state:
                return "unknown causes"
            
            from world.medical.constants import BLOOD_LOSS_DEATH_THRESHOLD
            
            # Check causes in priority order
            blood_pumping = medical_state.calculate_body_capacity("blood_pumping")
            breathing = medical_state.calculate_body_capacity("breathing") 
            digestion = medical_state.calculate_body_capacity("digestion")
            blood_level = medical_state.blood_level
            blood_loss_fatal = blood_level <= (100.0 - BLOOD_LOSS_DEATH_THRESHOLD)
            
            # Return first fatal condition found (in priority order)
            if blood_loss_fatal:
                return "blood loss"
            elif blood_pumping <= 0:
                return "heart failure"
            elif breathing <= 0:
                return "respiratory failure"
            elif digestion <= 0:
                return "organ failure"
            else:
                return "critical injuries"
                
        except Exception:
            return "unknown causes"
        
    def get_medical_status(self):
        """
        Get a detailed medical status report.
        
        Returns:
            str: Human-readable medical status
        """
        from world.medical.utils import get_medical_status_summary
        return get_medical_status_summary(self)
        
    def add_medical_condition(self, condition_type, location=None, severity="minor", **kwargs):
        """
        Add a medical condition to this character.
        
        Args:
            condition_type (str): Type of condition (bleeding, fracture, etc.)
            location (str, optional): Body location affected
            severity (str): Severity level
            **kwargs: Additional condition properties
            
        Returns:
            MedicalCondition: The added condition
        """
        condition = self.medical_state.add_condition(condition_type, location, severity, **kwargs)
        self.save_medical_state()
        return condition

    def get_search_candidates(self, searchdata, **kwargs):
        """
        Override to include aimed-at room contents when aiming.
        
        This is called by the search method to determine what objects
        are available to search through. When aiming at a direction,
        this includes both current room and aimed-room contents.
        
        Args:
            searchdata (str): The search criterion
            **kwargs: Same as passed to search method
            
        Returns:
            list: Objects that can be searched through
        """
        # Get the default candidates first
        candidates = super().get_search_candidates(searchdata, **kwargs)
        
        # Don't interfere with self-lookup or basic character functionality
        # Only enhance when specifically aiming at a direction
        aiming_direction = getattr(self.ndb, 'aiming_direction', None) if hasattr(self, 'ndb') else None
        
        if (candidates is not None and 
            aiming_direction and 
            self.location and
            hasattr(self.location, 'search_for_target')):  # Make sure the room supports this
            try:
                # Use the room's search_for_target method to get unified candidates
                # This leverages the existing vetted aiming logic
                unified_candidates = self.location.search_for_target(
                    self, searchdata, return_candidates_only=True
                )
                if unified_candidates:
                    # Use the unified candidates instead of default ones
                    # This maintains ordinal support and all existing logic
                    candidates = unified_candidates
            except (AttributeError, TypeError):
                # If anything goes wrong, fall back to default candidates
                # This ensures we never break normal searching
                pass
        
        return candidates

    def at_death(self):
        """
        Handles what happens when this character dies.
        Shows death curtain which will then start the death progression system.
        Admins are immortal and will be auto-healed instead of dying.
        """
        from .curtain_of_death import show_death_curtain
        from evennia.comms.models import ChannelDB
        from world.combat.constants import SPLATTERCAST_CHANNEL, NDB_COMBAT_HANDLER
        from evennia.utils.utils import delay
        
        # Admins are immortal - auto-heal instead of dying
        if self.is_admin():
            self._admin_auto_heal()
            try:
                splattercast = ChannelDB.objects.get_channel(SPLATTERCAST_CHANNEL)
                splattercast.msg(f"AT_DEATH_ADMIN: {self.key} is an admin - auto-healing instead of death")
            except:
                pass
            return
        
        # Prevent double death processing using PERSISTENT db flag (survives server reload)
        if self.db.death_processed:
            try:
                splattercast = ChannelDB.objects.get_channel(SPLATTERCAST_CHANNEL)
                splattercast.msg(f"AT_DEATH_SKIP: {self.key} already processed death (db flag), skipping")
            except:
                pass
            return
            
        # Mark death as processed IMMEDIATELY using db (persistent) to prevent ANY race conditions
        self.db.death_processed = True
        
        # Also set NDB flag for backwards compatibility
        if not hasattr(self, 'ndb'):
            self.ndb = {}
        self.ndb.death_processed = True
        
        # IMMEDIATELY remove from combat to prevent continued attacks on dead character
        # This must happen before any delays to stop the combat round from processing more attacks
        if hasattr(self.ndb, NDB_COMBAT_HANDLER) and getattr(self.ndb, NDB_COMBAT_HANDLER) is not None:
            handler = getattr(self.ndb, NDB_COMBAT_HANDLER)
            try:
                splattercast = ChannelDB.objects.get_channel(SPLATTERCAST_CHANNEL)
                splattercast.msg(f"AT_DEATH: Immediately removing {self.key} from combat handler {handler.key} to prevent further attacks")
            except:
                pass
            try:
                handler.remove_combatant(self)
            except Exception as e:
                try:
                    splattercast = ChannelDB.objects.get_channel(SPLATTERCAST_CHANNEL)
                    splattercast.msg(f"AT_DEATH_REMOVAL_ERROR: Failed to remove {self.key} from combat: {e}")
                except:
                    pass
        
        # Note: death_count is NOT incremented here - it will be incremented in the 
        # death_progression.py script at the definitive point of permanent death
        # (right before the character is moved to limbo). This ensures it only
        # increments exactly once, even if at_death() is called multiple times.
        
        # Clear any previous unconsciousness state since death supersedes it
        if getattr(self.ndb, 'unconsciousness_processed', False):
            self.ndb.unconsciousness_processed = False
        
        # Set death placement description for persistent visual indication
        self.override_place = "lying motionless and deceased."
        
        # Always show death analysis when character dies
        try:
            splattercast = ChannelDB.objects.get_channel(SPLATTERCAST_CHANNEL)
            death_analysis = self.debug_death_analysis()
            splattercast.msg(death_analysis)
        except Exception as e:
            # Fallback if splattercast channel not available
            pass
        
        # Check if character is in active combat - if so, defer death curtain
        is_in_combat = hasattr(self.ndb, NDB_COMBAT_HANDLER) and getattr(self.ndb, NDB_COMBAT_HANDLER) is not None
        
        if is_in_combat:
            # Set flag for combat system to trigger death curtain after kill message
            self.ndb.death_curtain_pending = True
            try:
                splattercast = ChannelDB.objects.get_channel(SPLATTERCAST_CHANNEL)
                splattercast.msg(f"AT_DEATH_COMBAT: {self.key} death curtain deferred - in active combat")
            except:
                pass
            
            # Safety fallback - trigger curtain after 5 seconds if combat doesn't handle it
            def fallback_death_curtain():
                if hasattr(self.ndb, 'death_curtain_pending') and self.ndb.death_curtain_pending:
                    try:
                        splattercast = ChannelDB.objects.get_channel(SPLATTERCAST_CHANNEL)
                        splattercast.msg(f"AT_DEATH_FALLBACK: {self.key} triggering fallback death curtain")
                    except:
                        pass
                    show_death_curtain(self)
                    self.ndb.death_curtain_pending = False
            
            delay(5, fallback_death_curtain)
        else:
            # Not in combat - show death curtain immediately
            # Death curtain will start death progression when it completes
            show_death_curtain(self)
        
        # Apply death command restrictions immediately
        self.apply_death_state()

    # MEDICAL REVIVAL SYSTEM - Command Set Management
    
    def apply_unconscious_state(self, force_test=False):
        """
        Apply unconscious command restrictions by replacing the default cmdset.
        
        Args:
            force_test (bool): If True, apply restrictions even for staff (for testing)
        """
        if not force_test and not self.is_unconscious():
            return
            
        # Check if character has builder/developer permissions
        if not force_test and self.locks.check(self, "perm(Builder)"):
            return  # Staff bypass cmdset restrictions
        
        # Remove current default cmdset and replace with unconscious cmdset
        try:
            self.cmdset.remove_default()
        except Exception:
            pass  # No default cmdset to remove, that's fine
            
        from commands.default_cmdsets import UnconsciousCmdSet
        self.cmdset.add_default(UnconsciousCmdSet)
        
        # Set placement description
        self.override_place = "unconscious and motionless."
        
        # Notify area
        if self.location:
            self.location.msg_contents(f"{self.key} collapses on the ground in an unconscious heap.", exclude=[self])
        self.msg("You lose consciousness and slip into darkness...")

    def apply_death_state(self, force_test=False):
        """
        Apply death command restrictions by replacing the default cmdset.
        
        Args:
            force_test (bool): If True, apply restrictions even for staff (for testing)
        """
        if not force_test and not self.is_dead():
            return
            
        # Remove unconscious restrictions first if they exist
        self.remove_unconscious_state()
        
        # Check if character has builder/developer permissions
        if not force_test and self.locks.check(self, "perm(Builder)"):
            # Staff bypass cmdset restrictions unless force_test=True
            pass
        else:
            # Remove current default cmdset and replace with death cmdset
            try:
                self.cmdset.remove_default()
            except Exception:
                pass  # No default cmdset to remove, that's fine
                
            from commands.default_cmdsets import DeathCmdSet
            self.cmdset.add_default(DeathCmdSet)
        
        # Placement description already set in at_death()
        # TODO: Add death experience script for atmospheric immersion when implemented

    def remove_unconscious_state(self):
        """
        Remove unconscious command restrictions by restoring the normal default cmdset.
        """
        try:
            # Remove current default cmdset (should be unconscious cmdset)
            self.cmdset.remove_default()
        except Exception:
            pass  # No default cmdset to remove, that's fine
            
        # Restore normal character cmdset
        from commands.default_cmdsets import CharacterCmdSet
        self.cmdset.add_default(CharacterCmdSet)
        
        # Clear placement description - but only if it's unconscious-specific
        if (hasattr(self, 'override_place') and 
            self.override_place == "unconscious and motionless."):
            self.override_place = None
        
        # Notify recovery - but only if character is not dead
        if not self.is_dead():
            if self.location:
                self.location.msg_contents(f"{self.key} regains consciousness.", exclude=[self])
            self.msg("You slowly regain consciousness...")

    def remove_death_state(self):
        """
        Remove death command restrictions and restore normal cmdset.
        """
        try:
            # Remove current default cmdset (should be death cmdset)
            self.cmdset.remove_default()
        except Exception:
            pass  # No default cmdset to remove, that's fine
            
        # Restore normal character cmdset
        from commands.default_cmdsets import CharacterCmdSet
        self.cmdset.add_default(CharacterCmdSet)
        
        # Clear placement description
        if hasattr(self, 'override_place'):
            self.override_place = None
        
        # Restart medical script if character has conditions and script is stopped
        if (hasattr(self, 'medical_state') and self.medical_state and 
            self.medical_state.conditions):
            try:
                from evennia.comms.models import ChannelDB
                splattercast = ChannelDB.objects.get_channel("Splattercast")
                
                # Find stopped medical script and restart it
                medical_scripts = self.scripts.get("medical_script")
                stopped_scripts = [s for s in medical_scripts if not s.is_active]
                
                if stopped_scripts:
                    stopped_scripts[0].start()
                    splattercast.msg(f"REVIVAL_RESTART: Restarted medical script for {self.key}")
                    
                    # Force immediate processing to overcome start_delay
                    from evennia.utils import delay
                    delay(0.1, stopped_scripts[0].at_repeat)
                    splattercast.msg(f"REVIVAL_IMMEDIATE: Forced immediate medical processing for {self.key}")
                else:
                    # Create new script if none exists
                    from world.medical.script import MedicalScript
                    from evennia import create_script
                    script = create_script(MedicalScript, obj=self, autostart=True)
                    splattercast.msg(f"REVIVAL_CREATE: Created new medical script for {self.key}")
                    
                    # Force immediate processing for new script too
                    from evennia.utils import delay
                    delay(0.1, script.at_repeat)
                    splattercast.msg(f"REVIVAL_IMMEDIATE_NEW: Forced immediate medical processing for new script for {self.key}")
            except Exception as e:
                try:
                    splattercast.msg(f"REVIVAL_ERROR: Failed to restart medical script for {self.key}: {e}")
                except:
                    pass
        
        # Clear death processing flags (both ndb and db)
        if hasattr(self.ndb, 'death_processed'):
            self.ndb.death_processed = False
        if hasattr(self.db, 'death_processed'):
            del self.db.death_processed
        
        # Notify revival
        if self.location:
            self.location.msg_contents(f"|g{self.key} has been revived!|n", exclude=[self])
        self.msg("|gYou have been revived! You feel the spark of life return.|n")

    def apply_final_death_state(self):
        """
        Apply final death state after death progression completes.
        This is permanent death until manual revival by admin.
        """
        from evennia.comms.models import ChannelDB
        from world.combat.constants import SPLATTERCAST_CHANNEL
        
        # Update placement description for permanent death
        self.override_place = "lying motionless and deceased."
        
        # Ensure death cmdset is applied (should already be done)
        if not hasattr(self, '_death_cmdset_applied'):
            self.apply_death_state(force_test=True)
            self._death_cmdset_applied = True
        
        # Log final death
        try:
            splattercast = ChannelDB.objects.get_channel(SPLATTERCAST_CHANNEL)
            splattercast.msg(f"FINAL_DEATH: {self.key} has entered permanent death state")
        except:
            pass

    def validate_attack_target(self):
        """
        Validate if this character can be attacked.
        
        Called by CmdAttack before combat initiation. Returns None for valid
        targets, or an error message string to prevent the attack.
        
        Returns:
            None if valid target, or str with error message if invalid
        """
        # Holographic merchants cannot be attacked
        if getattr(self.db, 'is_holographic', False):
            return "A holographic merchant cannot be attacked - target validation failed"
        
        # Character is a valid attack target
        return None

    # MR. HANDS SYSTEM
    # Persistent hand slots: supports dynamic anatomy eventually
    hands = AttributeProperty(
        {"left": None, "right": None},
        category="equipment",
        autocreate=True
    )

    # NAKEDS SYSTEM
    # Naked body part descriptions - detailed descriptions for individual body parts
    # Stored as a dictionary mapping body part names to description strings
    # Structure: {"head": "description", "face": "description", ...}
    
    # PLACEMENT SYSTEM (@look_place, @temp_place)
    # Note: look_place and override_place are defined as AttributeProperty above
    # Temporary placement description (cleared when changing rooms, stored in NDB)
    @property
    def temp_place(self):
        """Get temporary placement description."""
        return getattr(self.ndb, 'temp_place', None)
    
    @temp_place.setter
    def temp_place(self, value):
        """Set temporary placement description."""
        if value is None:
            if hasattr(self.ndb, 'temp_place'):
                delattr(self.ndb, 'temp_place')
        else:
            self.ndb.temp_place = value
    
    
    # CLOTHING SYSTEM
    # Storage for worn clothing items organized by body location
    worn_items = AttributeProperty({}, category="clothing", autocreate=True)

    # Structure: {
    #     "chest": [jacket_obj, shirt_obj],  # Ordered by layer (outer first)
    #     "head": [hat_obj],
    #     "left_hand": [glove_obj],
    #     "right_hand": [glove_obj]
    # }

    def wield_item(self, item, hand="right"):
        hands = self.hands
        if hand not in hands:
            return f"You don't have a {hand} hand."

        if hands[hand]:
            return f"You're already holding something in your {hand}."
        
        # Check if item is already in another hand
        for other_hand, held_item in hands.items():
            if held_item == item:
                if other_hand == hand:
                    return f"You're already wielding {item.get_display_name(self)} in your {hand} hand."
                else:
                    return f"You're already wielding {item.get_display_name(self)} in your {other_hand} hand."

        if item.location != self:
            return "You're not carrying that item."
        
        # Check if item is currently worn
        if hasattr(self, 'is_item_worn') and self.is_item_worn(item):
            return "You can't wield something you're wearing. Remove it first."

        hands[hand] = item
        # Keep item.location = self (wielded items stay in inventory location-wise)
        # They're just tracked separately in the hands dict
        self.hands = hands  # Save updated hands dict
        return f"You wield {item.get_display_name(self)} in your {hand} hand."
    
    def unwield_item(self, hand="right"):
        hands = self.hands
        item = hands.get(hand, None)

        if not item:
            return f"You're not holding anything in your {hand} hand."

        item.location = self
        hands[hand] = None
        self.hands = hands
        return f"You unwield {item.get_display_name(self)} from your {hand} hand."
    
    def list_held_items(self):
        hands = self.hands
        lines = []
        for hand, item in hands.items():
            if item:
                lines.append(f"{hand.title()} Hand: {item.get_display_name(self)}")
            else:
                lines.append(f"{hand.title()} Hand: (empty)")
        return lines

    def clear_aim_state(self, reason_for_clearing=""):
        """
        Clears any current aiming state (character or direction) for this character.
        Provides feedback to the character and any previously aimed-at target.

        Args:
            reason_for_clearing (str, optional): A short phrase describing why aim is cleared,
                                                 e.g., "as you move", "as you stop aiming".
        Returns:
            bool: True if an aim state was actually cleared, False otherwise.
        """
        splattercast = ChannelDB.objects.get_channel("Splattercast")
        stopped_aiming_message_parts = []
        log_message_parts = []
        action_taken = False

        # Clear character-specific aim
        old_aim_target_char = getattr(self.ndb, "aiming_at", None)
        if old_aim_target_char:
            action_taken = True
            del self.ndb.aiming_at
            log_message_parts.append(f"stopped aiming at {old_aim_target_char.key}")
            
            if hasattr(old_aim_target_char, "ndb") and getattr(old_aim_target_char.ndb, "aimed_at_by", None) == self:
                del old_aim_target_char.ndb.aimed_at_by
                old_aim_target_char.msg(f"{self.get_display_name(old_aim_target_char)} is no longer aiming directly at you.")
            
            # Clear override_place and handle mutual showdown cleanup
            self._clear_aim_override_place_on_aim_clear(old_aim_target_char)
            
            stopped_aiming_message_parts.append(f"at {old_aim_target_char.get_display_name(self)}")

        # Clear directional aim
        old_aim_direction = getattr(self.ndb, "aiming_direction", None)
        if old_aim_direction:
            action_taken = True
            del self.ndb.aiming_direction
            log_message_parts.append(f"stopped aiming {old_aim_direction}")
            
            # Clear directional aim override_place
            self.override_place = ""
            
            stopped_aiming_message_parts.append(f"{old_aim_direction}")

        if action_taken:
            # Construct details of what was being aimed at for the player message
            aim_details_for_msg = ""
            if stopped_aiming_message_parts:
                # stopped_aiming_message_parts contains things like "at {target_name}" or "{direction}"
                # Example: " at YourTarget", " east", or " at YourTarget, east"
                aim_details_for_msg = f" {', '.join(stopped_aiming_message_parts)}"

            # Base player message
            player_msg_text = f"You stop aiming{aim_details_for_msg}"

            # Append the reason, but only if it's not the default "as you stop aiming"
            # (which is implicit when the player uses the 'stop aiming' command)
            if reason_for_clearing and reason_for_clearing != "as you stop aiming":
                player_msg_text += f" {reason_for_clearing.strip()}"
            
            player_msg_text += "." # Add a period at the end.
            self.msg(player_msg_text)

            # Construct log message (this part's logic for suffix remains the same)
            log_reason_suffix = ""
            if reason_for_clearing:
                log_reason_suffix = f" ({reason_for_clearing.strip()})" # Log always includes the reason clearly
            splattercast.msg(f"AIM_CLEAR: {self.key} {', '.join(log_message_parts)}{log_reason_suffix}.")
        
        return action_taken

    def _clear_aim_override_place_on_aim_clear(self, target):
        """
        Clear override_place for aiming when clearing aim state, handling mutual showdown cleanup.
        
        Args:
            target: The character that was being aimed at
        """
        # Check if they were in a mutual showdown
        if (hasattr(self, 'override_place') and hasattr(target, 'override_place') and
            self.override_place == "locked in a deadly showdown." and 
            target.override_place == "locked in a deadly showdown."):
            # They were in a showdown - clear aimer's place, check if target should revert to normal aiming
            self.override_place = ""
            
            # If target is still aiming at aimer, revert them to normal aiming
            target_still_aiming = getattr(target.ndb, "aiming_at", None)
            if target_still_aiming == self:
                target.override_place = f"aiming carefully at {self.key}."
            else:
                # Target isn't aiming at anyone, clear their place too
                target.override_place = ""

    # ===================================================================
    # CLOTHING SYSTEM METHODS
    # ===================================================================
    
    def wear_item(self, item):
        """Wear a clothing item, handling layer conflicts and coverage"""
        # Validate item is wearable
        if not item.is_wearable():
            return False, "That item can't be worn."
        
        # Auto-unwield if currently held (move to inventory)
        hands = getattr(self, 'hands', {})
        for hand, held_item in hands.items():
            if held_item == item:
                hands[hand] = None
                item.location = self  # Move to inventory
                self.hands = hands    # Save updated hands
                break
        
        # Validate item is in inventory (now that we've unwielded if needed)
        if item.location != self:
            return False, "You're not carrying that item."
        
        # Get item's current coverage (accounting for style states)
        item_coverage = item.get_current_coverage()
        item_layer = getattr(item, 'layer', 2)
        
        # Check for layer conflicts before wearing
        if not self.db.worn_items:
            self.db.worn_items = {}
        
        # Detect layer conflicts
        conflicts = []
        for location in item_coverage:
            if location in self.db.worn_items:
                for worn_item in self.db.worn_items[location]:
                    # Skip None items (deleted items)
                    if worn_item is None:
                        continue
                    worn_layer = getattr(worn_item, 'layer', 2)
                    
                    # CONFLICT 1: Trying to wear same layer at same location
                    if worn_layer == item_layer:
                        conflicts.append({
                            'type': 'same_layer',
                            'location': location,
                            'item': worn_item,
                            'message': f"You're already wearing {worn_item.key} on your {location.replace('_', ' ')} (both layer {item_layer})."
                        })
                    
                    # CONFLICT 2: Trying to wear inner layer over outer layer
                    elif item_layer < worn_layer:
                        conflicts.append({
                            'type': 'under_outer',
                            'location': location,
                            'item': worn_item,
                            'message': f"You can't wear {item.key} (layer {item_layer}) under {worn_item.key} (layer {worn_layer}) - remove the outer layer first."
                        })
        
        # If conflicts found, report them concisely in natural language
        if conflicts:
            # Group conflicts by item (not by location) to reduce spam
            conflicts_by_item = {}
            for conflict in conflicts:
                conflicting_item = conflict['item']
                if conflicting_item not in conflicts_by_item:
                    conflicts_by_item[conflicting_item] = {
                        'type': conflict['type'],
                        'locations': [],
                        'layer': getattr(conflicting_item, 'layer', 2)
                    }
                conflicts_by_item[conflicting_item]['locations'].append(conflict['location'])
            
            # Separate by conflict type
            same_layer_items = [k for k, v in conflicts_by_item.items() if v['type'] == 'same_layer']
            under_outer_items = [k for k, v in conflicts_by_item.items() if v['type'] == 'under_outer']
            
            # Build natural language error message with proper grammar
            # Use item.key (what they're trying to wear) and conflicting item keys
            if same_layer_items and under_outer_items:
                # Both types of conflicts
                if len(same_layer_items) == 1:
                    same_part = f"the {same_layer_items[0].key}"
                else:
                    same_names = [f"the {i.key}" for i in same_layer_items]
                    if len(same_names) == 2:
                        same_part = f"{same_names[0]} and {same_names[1]}"
                    else:
                        same_part = ", ".join(same_names[:-1]) + f", and {same_names[-1]}"
                
                if len(under_outer_items) == 1:
                    under_part = f"the {under_outer_items[0].key}"
                else:
                    under_names = [f"the {i.key}" for i in under_outer_items]
                    if len(under_names) == 2:
                        under_part = f"{under_names[0]} and {under_names[1]}"
                    else:
                        under_part = ", ".join(under_names[:-1]) + f", and {under_names[-1]}"
                
                error_msg = f"You cannot wear the {item.key} over {same_part}, and you would need to wear it under {under_part}."
            elif same_layer_items:
                # Only same-layer conflicts - explain you can't wear it over what's already worn
                if len(same_layer_items) == 1:
                    error_msg = f"You cannot wear the {item.key} over the {same_layer_items[0].key} you are already wearing."
                elif len(same_layer_items) == 2:
                    error_msg = f"You cannot wear the {item.key} over the {same_layer_items[0].key} and the {same_layer_items[1].key} you are already wearing."
                else:
                    names = [f"the {i.key}" for i in same_layer_items]
                    item_list = ", ".join(names[:-1]) + f", and {names[-1]}"
                    error_msg = f"You cannot wear the {item.key} over {item_list} you are already wearing."
            else:
                # Only under-outer conflicts
                if len(under_outer_items) == 1:
                    error_msg = f"You cannot wear the {item.key} under the {under_outer_items[0].key} - remove it first."
                elif len(under_outer_items) == 2:
                    error_msg = f"You cannot wear the {item.key} under the {under_outer_items[0].key} and the {under_outer_items[1].key} - remove them first."
                else:
                    names = [f"the {i.key}" for i in under_outer_items]
                    item_list = ", ".join(names[:-1]) + f", and {names[-1]}"
                    error_msg = f"You cannot wear the {item.key} under {item_list} - remove them first."
            
            return False, error_msg
        
        # No conflicts - proceed with wearing
        for location in item_coverage:
            if location not in self.db.worn_items:
                self.db.worn_items[location] = []
            
            # Get current items and filter out None items
            location_items = [item_obj for item_obj in self.db.worn_items[location] if item_obj is not None]
            
            # Find insertion point based on layer (outer layers first, higher numbers first)
            insert_index = 0
            for i, worn_item in enumerate(location_items):
                if worn_item is None:
                    continue
                worn_layer = getattr(worn_item, 'layer', 2)
                if item.layer <= worn_layer:
                    insert_index = i + 1
                else:
                    break
            
            # Insert and reassign to trigger db save
            location_items.insert(insert_index, item)
            self.db.worn_items[location] = location_items
        
        # Call at_wear hook on the item if it exists
        if hasattr(item, 'at_wear'):
            try:
                item.at_wear(self)
            except Exception:
                pass  # If hook fails, continue anyway
        
        return True, f"You put on {item.key}."
    
    def remove_item(self, item):
        """Remove worn clothing item, checking for outer layers blocking removal"""
        # Validate item is worn
        if not self.is_item_worn(item):
            return False, "You're not wearing that item."
        
        # Check if item has at_pre_remove hook that blocks removal
        if hasattr(item, 'at_pre_remove'):
            try:
                result = item.at_pre_remove(self)
                if result is False:
                    # Hook blocked removal - message already sent by the hook
                    return False, ""
            except Exception:
                pass  # If hook fails, proceed with removal
        
        # Ensure worn_items is initialized
        if not self.db.worn_items:
            self.db.worn_items = {}
        
        # Check if any outer layers are blocking removal
        item_layer = getattr(item, 'layer', 2)
        item_coverage = getattr(item, 'get_current_coverage', lambda: getattr(item, 'coverage', []))()
        
        blocking_items = []
        if self.db.worn_items:
            for location in item_coverage:
                if location in self.db.worn_items:
                    for worn_item in self.db.worn_items[location]:
                        if worn_item == item:
                            continue
                        worn_layer = getattr(worn_item, 'layer', 2)
                        
                        # Outer layers (higher numbers) block removal of inner layers
                        if worn_layer > item_layer:
                            blocking_items.append({
                                'item': worn_item,
                                'location': location,
                                'layer': worn_layer
                            })
        
        # If blocked, report it in natural language
        if blocking_items:
            # Get unique items (may block at multiple locations)
            unique_blockers = {}
            for block in blocking_items:
                blocker = block['item']
                if blocker not in unique_blockers:
                    unique_blockers[blocker] = {
                        'layer': block['layer'],
                        'locations': []
                    }
                unique_blockers[blocker]['locations'].append(block['location'])
            
            # Natural language, single-sentence response
            if len(unique_blockers) == 1:
                blocker = list(unique_blockers.keys())[0]
                error_msg = f"Remove the {blocker.key} first."
            elif len(unique_blockers) == 2:
                blocker1, blocker2 = list(unique_blockers.keys())
                error_msg = f"Remove the {blocker1.key} and the {blocker2.key} first."
            else:
                # 3+ blockers
                names = [f"the {b.key}" for b in unique_blockers.keys()]
                item_list = ", ".join(names[:-1]) + f", and {names[-1]}"
                error_msg = f"Remove {item_list} first."
            
            return False, error_msg
        
        # No blocking - proceed with removal
        if self.db.worn_items:
            for location in list(self.db.worn_items.keys()):
                items = self.db.worn_items[location]
                if item in items:
                    # Create new list without the item and reassign to trigger db save
                    new_items = [i for i in items if i != item]
                    if new_items:
                        self.db.worn_items[location] = new_items
                    else:
                        del self.db.worn_items[location]
        
        return True, f"You remove {item.key}."
    
    def is_item_worn(self, item):
        """Check if a specific item is currently worn"""
        if not self.db.worn_items:
            return False
        
        for items in self.db.worn_items.values():
            for worn_item in items:
                if worn_item is None:
                    continue
                # Check by reference first
                if worn_item == item:
                    return True
                # Also check by dbref/id in case references differ
                if hasattr(worn_item, 'id') and hasattr(item, 'id'):
                    if worn_item.id == item.id:
                        return True
        return False
    
    def get_worn_items(self, location=None):
        """Get worn items, optionally filtered by location"""
        if not self.db.worn_items:
            return []
        
        if location:
            # Filter out None items that may have been deleted
            return [item for item in self.db.worn_items.get(location, []) if item is not None]
        
        # Return all worn items (deduplicated since items can cover multiple locations)
        seen_items = set()
        all_items = []
        for items in self.db.worn_items.values():
            for item in items:
                # Skip None items (deleted items)
                if item is not None and item not in seen_items:
                    seen_items.add(item)
                    all_items.append(item)
        return all_items
    
    def is_location_covered(self, location):
        """Check if body location is covered by clothing"""
        if not self.db.worn_items:
            return False
        
        return bool(self.db.worn_items.get(location, []))
    
    def get_coverage_description(self, location):
        """Get clothing description for covered location"""
        if not self.db.worn_items or location not in self.db.worn_items:
            return None
        
        # Get outermost (first) item for this location
        items = self.db.worn_items[location]
        if not items:
            return None
        
        outermost_item = items[0]
        return outermost_item.get_current_worn_desc()
    
    def _build_clothing_coverage_map(self):
        """Map each body location to outermost covering clothing item."""
        coverage = {}
        if not self.db.worn_items:
            return coverage
        
        for location, items in self.db.worn_items.items():
            if items:
                # First item is outermost due to layer ordering
                # Filter out None items that may have been deleted
                valid_items = [item for item in items if item is not None]
                if valid_items:
                    coverage[location] = valid_items[0]
        
        return coverage

    # ===================================================================
    # LONGDESC APPEARANCE SYSTEM
    # ===================================================================

    def get_longdesc_appearance(self, looker=None, **kwargs):
        """
        Builds and returns the character's longdesc appearance.
        
        Returns:
            str: Formatted appearance with base description + longdescs
        """
        # Get base description
        base_desc = self.db.desc or ""
        
        # Get visible body descriptions (longdesc + clothing integration)
        visible_body_descriptions = self._get_visible_body_descriptions(looker)
        
        if not visible_body_descriptions:
            return base_desc
        
        # Combine with smart paragraph formatting
        formatted_body_descriptions = self._format_longdescs_with_paragraphs(visible_body_descriptions)
        
        # Combine base description with body descriptions
        if base_desc:
            return f"{base_desc}\n\n{formatted_body_descriptions}"
        else:
            return formatted_body_descriptions

    def _get_visible_body_descriptions(self, looker=None):
        """
        Get all visible descriptions, integrating clothing and chrome with existing longdesc system.
        
        Args:
            looker: Character looking (for future permission checks)
            
        Returns:
            list: List of (location, description) tuples in anatomical order
        """
        from world.combat.constants import ANATOMICAL_DISPLAY_ORDER
        
        descriptions = []
        coverage_map = self._build_clothing_coverage_map()
        nakeds = self.db.nakeds or {}
        
        # Get installed chrome
        installed_chrome = getattr(self.db, 'installed_chrome_list', None) or []
        chrome_map = {}  # Map location -> chrome data
        
        # Slot to location mapping for chrome
        chrome_slot_mapping = {
            'head': ['head'],
            'face': ['face'],
            'eyes': ['leye', 'reye'],
            'eye': ['leye'],  # Single eye (would need to check which one)
            'ears': ['lear', 'rear'],
            'arms': ['larm', 'rarm', 'lhand', 'rhand'],
            'arm': ['larm'],  # Single arm
            'legs': ['lthigh', 'rthigh', 'lshin', 'rshin'],
            'leg': ['lthigh', 'rshin'],  # Single leg
            'feet': ['lfoot', 'rfoot'],
            'foot': ['lfoot'],  # Single foot
        }
        
        for chrome in installed_chrome:
            slot = chrome.get('slot')
            if slot and chrome.get('type') == 'external':
                # Map chrome slot to actual anatomical locations
                locations = chrome_slot_mapping.get(slot, [])
                for loc in locations:
                    chrome_map[loc] = chrome
        
        # Track which clothing items we've already added to avoid duplicates
        added_clothing_items = set()
        
        # Process in anatomical order
        for location in ANATOMICAL_DISPLAY_ORDER:
            # Priority: chrome > clothing > nakeds
            if location in chrome_map:
                # Location covered by chrome - get the worn_desc from proto
                chrome_data = chrome_map[location]
                chrome_shortname = chrome_data.get('shortname')
                
                # Get prototype to find worn_desc
                if chrome_shortname:
                    proto = self._get_chrome_prototype(chrome_shortname)
                    if proto and proto.get('worn_desc'):
                        descriptions.append((location, proto['worn_desc']))
                        continue
            
            if location in coverage_map:
                # Location covered by clothing - use outermost item's current worn_desc
                clothing_item = coverage_map[location]
                
                # Only add each clothing item once, regardless of how many locations it covers
                # Also check that clothing_item is not None (items can be deleted)
                if clothing_item and clothing_item not in added_clothing_items:
                    # Use new method with $pron() processing and color integration
                    desc = clothing_item.get_current_worn_desc_with_perspective(looker, self)
                    if desc:
                        descriptions.append((location, desc))
                        added_clothing_items.add(clothing_item)
            else:
                # Location not covered - use character's naked description if set with template variable processing
                if location in nakeds and nakeds[location]:
                    # Longdesc should have skintone applied
                    processed_desc = self._process_description_variables(nakeds[location], looker, force_third_person=True, apply_skintone=True)
                    
                    # Add wounds to this location if any exist
                    try:
                        from world.medical.wounds import append_wounds_to_longdesc
                        processed_desc = append_wounds_to_longdesc(processed_desc, self, location, looker)
                    except ImportError:
                        # Wound system not available, continue without wounds
                        pass
                    
                    descriptions.append((location, processed_desc))
                else:
                    # No longdesc for this location, but check for standalone wounds
                    try:
                        from world.medical.wounds import get_character_wounds
                        wounds = get_character_wounds(self)
                        location_wounds = [w for w in wounds if w['location'] == location]
                        
                        if location_wounds:
                            # Create standalone wound description for this location
                            from world.medical.wounds import get_wound_description
                            wound = location_wounds[0]  # Use first/most significant wound
                            wound_desc = get_wound_description(
                                injury_type=wound['injury_type'],
                                location=wound['location'],
                                severity=wound['severity'],
                                stage=wound['stage'],
                                organ=wound.get('organ'),
                                character=self
                            )
                            descriptions.append((location, wound_desc))
                    except ImportError:
                        # Wound system not available, continue without wounds
                        pass
        
        # Add any extended anatomy not in default order (clothing or nakeds)
        all_locations = set(nakeds.keys()) | set(coverage_map.keys())
        for location in all_locations:
            if location not in ANATOMICAL_DISPLAY_ORDER:
                if location in coverage_map:
                    # Extended location with clothing
                    clothing_item = coverage_map[location]
                    # Check that clothing_item is not None (items can be deleted)
                    if clothing_item and clothing_item not in added_clothing_items:
                        # Use new method with $pron() processing and color integration
                        desc = clothing_item.get_current_worn_desc_with_perspective(looker, self)
                        if desc:
                            descriptions.append((location, desc))
                            added_clothing_items.add(clothing_item)
                elif location in nakeds and nakeds[location]:
                    # Extended location with nakeds - apply template variable processing and skintone
                    processed_desc = self._process_description_variables(nakeds[location], looker, force_third_person=True, apply_skintone=True)
                    
                    # Add wounds to this extended location if any exist
                    try:
                        from world.medical.wounds import append_wounds_to_longdesc
                        processed_desc = append_wounds_to_longdesc(processed_desc, self, location, looker)
                    except ImportError:
                        # Wound system not available, continue without wounds
                        pass
                    
                    descriptions.append((location, processed_desc))
                else:
                    # No longdesc for extended location, but check for standalone wounds
                    try:
                        from world.medical.wounds import get_character_wounds
                        wounds = get_character_wounds(self)
                        location_wounds = [w for w in wounds if w['location'] == location]
                        
                        if location_wounds:
                            # Create standalone wound description for this extended location
                            from world.medical.wounds import get_wound_description
                            wound = location_wounds[0]  # Use first/most significant wound
                            wound_desc = get_wound_description(
                                injury_type=wound['injury_type'],
                                location=wound['location'],
                                severity=wound['severity'],
                                stage=wound['stage'],
                                organ=wound.get('organ'),
                                character=self
                            )
                            descriptions.append((location, wound_desc))
                    except ImportError:
                        # Wound system not available, continue without wounds
                        pass
        
        return descriptions

    def _format_longdescs_with_paragraphs(self, longdesc_list):
        """
        Formats longdesc descriptions with smart paragraph breaks.
        
        Args:
            longdesc_list: List of (location, description) tuples
            
        Returns:
            str: Formatted description with paragraph breaks
        """
        from world.combat.constants import (
            PARAGRAPH_BREAK_THRESHOLD, 
            ANATOMICAL_REGIONS,
            REGION_BREAK_PRIORITY,
            ANATOMICAL_DISPLAY_ORDER
        )
        
        if not longdesc_list:
            return ""
        
        # Sort descriptions by ANATOMICAL_DISPLAY_ORDER to ensure proper grouping
        def get_location_order(item):
            location, _ = item
            try:
                return ANATOMICAL_DISPLAY_ORDER.index(location)
            except ValueError:
                return len(ANATOMICAL_DISPLAY_ORDER)  # Put unknown locations at end
        
        sorted_longdesc_list = sorted(longdesc_list, key=get_location_order)
        
        paragraphs = []
        current_paragraph = []
        current_char_count = 0
        current_region = None
        
        for location, description in sorted_longdesc_list:
            # Clean up whitespace but preserve periods within descriptions
            description = description.strip()
            if not description:
                continue
            
            # Ensure description ends with exactly one period
            # Remove any trailing periods first, then add one back
            description = description.rstrip('.')
            if description:  # Make sure there's still text after stripping
                description = description + '.'
            
            # Determine which anatomical region this location belongs to
            location_region = self._get_anatomical_region(location)
            
            # Check if we should break for a new paragraph
            should_break = False
            
            if REGION_BREAK_PRIORITY and current_region and location_region != current_region:
                # Region changed - always break on region change
                should_break = True
            elif current_char_count + len(description) > PARAGRAPH_BREAK_THRESHOLD:
                # Would exceed threshold - break now
                should_break = True
            
            if should_break and current_paragraph:
                # Finish current paragraph and start new one
                # Join descriptions (each already has its own period)
                paragraph_text = " ".join(current_paragraph)
                paragraphs.append(paragraph_text)
                current_paragraph = []
                current_char_count = 0
            
            # Add description to current paragraph
            current_paragraph.append(description)
            current_char_count += len(description) + 1  # +1 for space
            current_region = location_region
        
        # Add final paragraph
        if current_paragraph:
            paragraph_text = " ".join(current_paragraph)
            paragraphs.append(paragraph_text)
        
        # Add color reset at end of each paragraph to prevent color bleeding
        paragraphs = [p + "|n" for p in paragraphs]
        
        return "\n\n".join(paragraphs)

    def _get_anatomical_region(self, location):
        """
        Determines which anatomical region a location belongs to.
        
        Args:
            location: Body location string
            
        Returns:
            str: Region name or 'extended' for non-standard anatomy
        """
        from world.combat.constants import ANATOMICAL_REGIONS
        
        for region_name, locations in ANATOMICAL_REGIONS.items():
            if location in locations:
                return region_name
        return "extended"

    def has_location(self, location):
        """
        Checks if this character has a specific body location.
        
        Args:
            location: Body location to check
            
        Returns:
            bool: True if character has this location
        """
        nakeds = self.nakeds or {}
        return location in nakeds

    def get_available_locations(self):
        """
        Gets list of all body locations this character has.
        
        Returns:
            list: List of available body location names
        """
        nakeds = self.nakeds or {}
        return list(nakeds.keys())

    def set_naked(self, location, description):
        """
        Sets a naked description for a specific body part.
        
        Args:
            location: Body location
            description: Description text (None to clear)
            
        Returns:
            bool: True if successful, False if location invalid
        """
        if not description:
            return self.clear_naked(location)
        
        nakeds = self.db.nakeds or {}
        nakeds[location] = description
        self.db.nakeds = nakeds
        return True

    def get_naked(self, location):
        """
        Gets naked description for a specific body part.
        
        Args:
            location: Body location
            
        Returns:
            str or None: Description text or None if unset
        """
        nakeds = self.db.nakeds or {}
        return nakeds.get(location)
    
    def clear_naked(self, location):
        """
        Clears naked description for a specific body part.
        
        Args:
            location: Body location
            
        Returns:
            bool: True if successful
        """
        nakeds = self.db.nakeds or {}
        if location in nakeds:
            del nakeds[location]
            self.db.nakeds = nakeds
            return True
        return False

    def return_appearance(self, looker, **kwargs):
        """
        This method is called when someone looks at this character.
        Returns a clean character appearance with name, description, longdesc+clothing, and wielded items.
        
        Args:
            looker: Character doing the looking
            **kwargs: Additional parameters
            
        Returns:
            str: Complete character appearance in clean format
        """
        # Debug: Make sure this method is being called
        
        # Build appearance components
        parts = []
        
        # 1. Character name (header) + main description (no blank line between)
        name_and_desc = [self.get_display_name(looker)]
        if self.db.desc:
            # Initial description should NOT have skintone applied
            processed_desc = self._process_description_variables(self.db.desc, looker, force_third_person=True, apply_skintone=False)
            name_and_desc.append(processed_desc)
        
        parts.append('\n'.join(name_and_desc))
        
        # 2. Nakeds + clothing integration (uses automatic paragraph parsing)
        if not self.db.nakeds:
            self.db.nakeds = {}
        
        visible_body_descriptions = self._get_visible_body_descriptions(looker)
        if visible_body_descriptions:
            formatted_body_descriptions = self._format_longdescs_with_paragraphs(visible_body_descriptions)
            parts.append(formatted_body_descriptions)
        
        # 3. Wielded items section (using hands system)
        hands = self.attributes.get('hands', category='equipment') or {'left': None, 'right': None}
        wielded_items = [item for item in hands.values() if item is not None]
        
        if wielded_items:
            wielded_names = [obj.get_display_name(looker) for obj in wielded_items]
            if len(wielded_names) == 1:
                wielded_text = f"{self.get_display_name(looker)} is holding a {wielded_names[0]}."
            elif len(wielded_names) == 2:
                wielded_text = f"{self.get_display_name(looker)} is holding a {wielded_names[0]} and a {wielded_names[1]}."
            else:
                # Multiple items: "a item1, a item2, and a item3"
                wielded_with_articles = [f"a {name}" for name in wielded_names]
                wielded_text = f"{self.get_display_name(looker)} is holding {', '.join(wielded_with_articles[:-1])}, and {wielded_with_articles[-1]}."
            parts.append(wielded_text)
        else:
            # Show explicitly when hands are empty
            parts.append(f"{self.get_display_name(looker)} is holding nothing.")
        
        # 4. Staff-only comprehensive inventory (with explicit admin messaging)
        if looker.check_permstring("Builder"):
            all_contents = [obj for obj in self.contents if obj.location == self]
            if all_contents:
                content_names = [f"{obj.get_display_name(looker)} [{obj.dbref}]" for obj in all_contents]
                parts.append(f"|wWith your administrative visibility, you see:|n {', '.join(content_names)}")
        
        # Join all parts with appropriate spacing (blank lines between major sections)
        return '\n\n'.join(parts)

    def _process_description_variables(self, desc, looker, force_third_person=False, apply_skintone=False):
        """
        Process template variables in descriptions for perspective-aware text.
        
        Uses simple template variables like {their}, {they}, {name} similar to {color}.
        Also supports percent-sign pronoun codes: %p, %s, %o, %q, %r
        
        Args:
            desc (str): Description text with potential template variables
            looker (Character): Who is looking at this character
            force_third_person (bool): If True, always use 3rd person pronouns
            apply_skintone (bool): If True, apply skintone coloring (for longdescs only)
            
        Returns:
            str: Description with variables substituted
        """
        if not desc or not looker:
            return desc
        
        # First, convert percent-sign pronoun codes (%p, %s, %o, %q, %r) to curly braces for processing
        desc = self._convert_percent_pronouns_to_template(desc, looker, force_third_person)
        
        # Replace %N with character's display name (for clothing worn descriptions)
        # %N is always third person (the wearer's name as seen by observer)
        if "%N" in desc:
            desc = desc.replace("%N", self.get_display_name(looker))
            
        # Map of available template variables based on perspective
        is_self = (looker == self) and not force_third_person
        
        # Get pronoun information for this character
        gender_mapping = {
            'male': 'male',
            'female': 'female', 
            'neutral': 'plural',
            'nonbinary': 'plural',
            'other': 'plural'
        }
        
        character_gender = gender_mapping.get(self.gender, 'plural')
        
        # Simple template variable mapping (like {color})
        variables = {
            # Most common - possessive pronouns (lowercase)
            'their': 'your' if is_self else self._get_pronoun('possessive', character_gender),
            
            # Subject and object pronouns (lowercase)
            'they': 'you' if is_self else self._get_pronoun('subject', character_gender),
            'them': 'you' if is_self else self._get_pronoun('object', character_gender),
            
            # Possessive absolute and reflexive (less common, lowercase)
            'theirs': 'yours' if is_self else self._get_pronoun('possessive_absolute', character_gender),
            'themselves': 'yourself' if is_self else self._get_pronoun('reflexive', character_gender),
            'themself': 'yourself' if is_self else self._get_pronoun('reflexive', character_gender),  # Alternative form
            
            # Capitalized versions for sentence starts
            'Their': 'Your' if is_self else self._get_pronoun('possessive', character_gender).capitalize(),
            'They': 'You' if is_self else self._get_pronoun('subject', character_gender).capitalize(),
            'Them': 'You' if is_self else self._get_pronoun('object', character_gender).capitalize(),
            'Theirs': 'Yours' if is_self else self._get_pronoun('possessive_absolute', character_gender).capitalize(),
            'Themselves': 'Yourself' if is_self else self._get_pronoun('reflexive', character_gender).capitalize(),
            'Themself': 'Yourself' if is_self else self._get_pronoun('reflexive', character_gender).capitalize(),  # Alternative form
            
            # Character names
            'name': 'you' if is_self else self.get_display_name(looker),
            "name's": 'your' if is_self else f"{self.get_display_name(looker)}'s",
            
            # Legacy support for existing verbose names (can be removed later)
            'observer_pronoun_possessive': 'your' if is_self else self._get_pronoun('possessive', character_gender),
            'observer_pronoun_subject': 'you' if is_self else self._get_pronoun('subject', character_gender),
            'observer_pronoun_object': 'you' if is_self else self._get_pronoun('object', character_gender),
            'observer_pronoun_possessive_absolute': 'yours' if is_self else self._get_pronoun('possessive_absolute', character_gender),
            'observer_pronoun_reflexive': 'yourself' if is_self else self._get_pronoun('reflexive', character_gender),
            'observer_character_name': 'you' if is_self else self.get_display_name(looker),
            'observer_character_name_possessive': 'your' if is_self else f"{self.get_display_name(looker)}'s"
        }
        
        # Substitute all variables in the description
        try:
            processed_desc = desc.format(**variables)
        except (KeyError, ValueError) as e:
            # If there are template errors, use original description and log the issue
            processed_desc = desc
            # Debug: Log the error (remove this later)
            print(f"Template processing error in _process_description_variables: {e}")
            print(f"Description: {desc[:100]}...")  # First 100 chars
            print(f"Variables available: {list(variables.keys())}")
            
        # Apply skintone coloring only if requested (for longdescs only)
        if apply_skintone:
            skintone = getattr(self.db, 'skintone', None)
            skintone_code = None
            if skintone:
                from world.combat.constants import SKINTONE_PALETTE
                skintone_code = SKINTONE_PALETTE.get(skintone)
                if skintone_code:
                    # Wrap the entire processed description in the skintone color
                    # Don't add |n at end - period handling happens later in _format_longdescs_with_paragraphs
                    processed_desc = f"{skintone_code}{processed_desc}"
            
            # Apply eye color to "eye" or "eyes" mentions
            eye_color = getattr(self.db, 'eye_color', None)
            if eye_color:
                from world.combat.constants import EYE_COLOR_PALETTE
                eye_color_code = EYE_COLOR_PALETTE.get(eye_color)
                if eye_color_code:
                    import re
                    # Replace "eye" or "eyes" with colored versions, case-insensitive
                    # Use word boundaries to avoid matching "eyebrows" etc
                    # After eye color, return to skintone (or |n if no skintone)
                    reset_code = skintone_code if skintone_code else "|n"
                    processed_desc = re.sub(r'\b(eyes?)\b', lambda m: f"{eye_color_code}{m.group(1)}{reset_code}", processed_desc, flags=re.IGNORECASE)
                
        return processed_desc
    
    def _get_pronoun(self, pronoun_type, gender):
        """
        Get specific pronoun based on gender and type.
        
        Args:
            pronoun_type (str): Type of pronoun (subject, object, possessive, etc.)
            gender (str): Gender identifier (male, female, plural)
            
        Returns:
            str: Appropriate pronoun
        """
        pronouns = {
            'male': {
                'subject': 'he',
                'object': 'him', 
                'possessive': 'his',
                'possessive_absolute': 'his',
                'reflexive': 'himself'
            },
            'female': {
                'subject': 'she',
                'object': 'her',
                'possessive': 'her', 
                'possessive_absolute': 'hers',
                'reflexive': 'herself'
            },
            'plural': {  # Used for they/them, nonbinary, neutral, other
                'subject': 'they',
                'object': 'them',
                'possessive': 'their',
                'possessive_absolute': 'theirs', 
                'reflexive': 'themselves'
            }
        }
        
        return pronouns.get(gender, pronouns['plural']).get(pronoun_type, 'they')

    def _convert_percent_pronouns_to_template(self, desc, looker, force_third_person=False):
        """
        Convert percent-sign pronoun codes to template variable format.
        
        Supports: %p (possessive), %s (subject), %o (object), %q (possessive absolute), %r (reflexive), %n (name)
        Capitalize % to capitalize the pronoun: %P, %S, %O, %Q, %R, %N
        
        Args:
            desc (str): Description with percent-sign pronouns
            looker (Character): Who is looking
            force_third_person (bool): If True, always use 3rd person
            
        Returns:
            str: Description with percent codes replaced by template variables
        """
        import re
        
        is_self = (looker == self) and not force_third_person
        
        # Build pronoun mapping from character gender
        gender_mapping = {
            'male': 'male',
            'female': 'female', 
            'neutral': 'plural',
            'nonbinary': 'plural',
            'other': 'plural'
        }
        character_gender = gender_mapping.get(self.gender, 'plural')
        
        # Get pronouns for this character
        pronouns_dict = {
            'p': self._get_pronoun('possessive', character_gender),  # his/her/their
            's': self._get_pronoun('subject', character_gender),    # he/she/they
            'o': self._get_pronoun('object', character_gender),     # him/her/them
            'q': self._get_pronoun('possessive_absolute', character_gender),  # his/hers/theirs
            'r': self._get_pronoun('reflexive', character_gender),  # himself/herself/themselves
            'n': 'you' if is_self else self.get_display_name(looker)  # character's name
        }
        
        # For self viewing, swap pronouns
        if is_self:
            pronouns_dict = {
                'p': 'your',
                's': 'you',
                'o': 'you',
                'q': 'yours',
                'r': 'yourself',
                'n': 'you'
            }
        
        # Replace %p, %s, %o, %q, %r, %n and their capitalized versions
        result = desc
        for code, pronoun in pronouns_dict.items():
            # Lowercase version
            result = result.replace(f'%{code}', pronoun)
            # Capitalized version - use title() for multi-word names
            if code == 'n':
                # For names, use title case to capitalize each word
                result = result.replace(f'%{code.upper()}', pronoun.title())
            else:
                # For pronouns, just capitalize first letter
                result = result.replace(f'%{code.upper()}', pronoun.capitalize())
        
        return result

    def _get_chrome_prototype(self, shortname):
        """Get chrome prototype definition by shortname."""
        from world import chrome_prototypes
        
        # Get all prototype dictionaries from the module
        for name in dir(chrome_prototypes):
            obj = getattr(chrome_prototypes, name)
            if isinstance(obj, dict) and obj.get("shortname", "").lower() == shortname.lower():
                return obj
        return None
