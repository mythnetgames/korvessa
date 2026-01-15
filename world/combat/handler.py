"""
Combat Handler Module

The combat handler that manages turn-based combat for all combatants
in one or more locations. This module contains the core CombatHandler script
and utility functions for combat management.

This is the central component that orchestrates combat encounters, handling:
- Combat initialization and cleanup
- Turn management and initiative
- Multi-room combat coordination
- Combatant state management
- Integration with proximity and grappling systems
"""

from evennia import DefaultScript, create_script, search_object
from random import randint
from evennia.utils.utils import delay
from world.combat.messages import get_combat_message
from world.medical.utils import select_hit_location, select_target_organ
from evennia.comms.models import ChannelDB
import traceback

from .constants import (
    COMBAT_SCRIPT_KEY, SPLATTERCAST_CHANNEL,
    DB_COMBATANTS, DB_COMBAT_RUNNING, DB_MANAGED_ROOMS,
    DB_CHAR, DB_TARGET_DBREF, DB_GRAPPLING_DBREF, DB_GRAPPLED_BY_DBREF, DB_IS_YIELDING,
    NDB_COMBAT_HANDLER, NDB_PROXIMITY, NDB_SKIP_ROUND,
    DEBUG_PREFIX_HANDLER, DEBUG_SUCCESS, DEBUG_FAIL, DEBUG_ERROR, DEBUG_CLEANUP,
    MSG_GRAPPLE_AUTO_ESCAPE_VIOLENT, MSG_GRAPPLE_AUTO_YIELD,
    COMBAT_ACTION_RETREAT, COMBAT_ACTION_ADVANCE, COMBAT_ACTION_CHARGE, COMBAT_ACTION_DISARM,
    COMBAT_ROUND_INTERVAL, STAGGER_DELAY_INTERVAL, MAX_STAGGER_DELAY,
    # Ammunition system constants
    COMBAT_ACTION_RELOAD, NDB_RELOADING, DEFAULT_AMMO_CAPACITY,
    MSG_OUT_OF_AMMO, MSG_RELOADING, MSG_RELOADED, MSG_NO_AMMO_AVAILABLE,
    # Combat stamina constants
    STAMINA_DRAIN_PER_ROUND, STAMINA_DRAIN_PER_ATTACK, STAMINA_MIN_TO_ATTACK, STAMINA_EXHAUSTED_MSG
)
from .utils import (
    get_numeric_stat, log_combat_action, get_display_name_safe,
    roll_stat, opposed_roll, get_wielded_weapon, is_wielding_ranged_weapon,
    get_weapon_damage, add_combatant, remove_combatant, cleanup_combatant_state,
    cleanup_all_combatants, get_combatant_target, get_combatant_grappling_target,
    get_combatant_grappled_by, get_character_dbref, get_character_by_dbref,
    resolve_bonus_attack, get_combatants_safe, is_ammo_compatible,
    # New 0-100 skill system
    skill_to_bonus, skill_roll, opposed_skill_roll, get_combat_skill_value, combat_roll
)
from .grappling import (
    break_grapple, establish_grapple, resolve_grapple_initiate,
    resolve_grapple_join, resolve_grapple_takeover, resolve_release_grapple, validate_and_cleanup_grapple_state
)


def msg_contents_disguised(location, msg_template, chars_in_template, exclude=None):
    """
    Send a message to all observers in a location, using disguised names.
    
    This function handles sending messages where character names need to be
    replaced with their disguised identities for each observer.
    
    Args:
        location: The room to send the message to
        msg_template: Message template with {char_name} placeholders
                     Use {char0_name}, {char1_name}, etc. for multiple chars
        chars_in_template: List of characters in order matching template placeholders
                          For single char, can be just the character object
        exclude: List of characters to exclude from receiving the message
    """
    if not location:
        return
    
    exclude = exclude or []
    
    # Normalize chars_in_template to a list
    if not isinstance(chars_in_template, (list, tuple)):
        chars_in_template = [chars_in_template]
    
    for observer in location.contents:
        if observer in exclude:
            continue
        if not hasattr(observer, "msg"):
            continue
            
        # Build name substitutions for this observer
        format_kwargs = {}
        for i, char in enumerate(chars_in_template):
            if char:
                display_name = get_display_name_safe(char, observer)
            else:
                display_name = "someone"
            
            # Support both {char0_name} style and {char_name} for single char
            format_kwargs[f"char{i}_name"] = display_name
            if i == 0:
                format_kwargs["char_name"] = display_name
        
        try:
            formatted_msg = msg_template.format(**format_kwargs)
            observer.msg(formatted_msg)
        except (KeyError, ValueError):
            # Fallback if template format fails
            observer.msg(msg_template)


def get_or_create_combat(location):
    """
    Get an existing combat handler for a location or create a new one.
    
    This function ensures that each location has at most one active combat
    handler managing it, and handles the complex logic of multi-room combat
    coordination.
    
    Args:
        location: The room/location that needs combat management
        
    Returns:
        CombatHandler: The combat handler managing this location
    """
    splattercast = ChannelDB.objects.get_channel(SPLATTERCAST_CHANNEL)
    
    # First, check if 'location' is already managed by ANY active CombatHandler
    # This requires iterating through all scripts, which can be slow.
    # A better way might be a global list of active combat handlers, but for now:
    from evennia.scripts.models import ScriptDB
    active_handlers = ScriptDB.objects.filter(db_key=COMBAT_SCRIPT_KEY, db_is_active=True)

    for handler_script in active_handlers:
        # Ensure it's our CombatHandler type and has managed_rooms
        if hasattr(handler_script, "db") and hasattr(handler_script.db, DB_MANAGED_ROOMS):
            if location in getattr(handler_script.db, DB_MANAGED_ROOMS, []):
                splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_GET: Location {location.key} is already managed by active handler {handler_script.key} (on {handler_script.obj.key}). Returning it.")
                return handler_script
    
    # If not managed by an existing handler, check for an inactive one on THIS location
    for script in location.scripts.all():
        if script.key == COMBAT_SCRIPT_KEY:
            # Found a handler on this specific location
            if script.is_active: # Should have been caught by the loop above if it managed this location
                splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_GET: Found active handler {script.key} directly on {location.key} (missed by global check or manages only self). Returning it.")
                # Ensure it knows it manages this location
                managed_rooms = getattr(script.db, DB_MANAGED_ROOMS, [])
                if location not in managed_rooms:
                    managed_rooms.append(location)
                    setattr(script.db, DB_MANAGED_ROOMS, managed_rooms)
                return script
            else:
                splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_GET: Found inactive handler {script.key} on {location.key}. Attempting cleanup.")
                # Only perform database operations if the handler has been saved to the database
                if hasattr(script, 'id') and script.id:
                    try:
                        script.stop() # Ensure it's fully stopped
                        script.save()
                        script.delete()
                        splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_GET: Deleted inactive handler {script.key}.")
                    except Exception as e:
                        splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_GET: Error cleaning up inactive handler {script.key}: {e}. Leaving as-is.")
                else:
                    splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_GET: Inactive handler {script.key} was not saved to database, skipping cleanup.")
                break # Only one handler script per location by key

    # If no suitable handler found, create a new one on this location
    new_script = create_script(
        "world.combat.handler.CombatHandler",
        key=COMBAT_SCRIPT_KEY,
        obj=location, # New handler is "hosted" by this location
        persistent=True,
    )
    
    # Ensure the script is saved to the database before returning
    # This is critical because attributes cannot be set on unsaved objects
    if not new_script.id:
        new_script.save()
        splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_GET: Saved new CombatHandler {new_script.key} to database (id={new_script.id}).")
    
    splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_GET: Created new CombatHandler {new_script.key} on {location.key}.")
    return new_script


class CombatHandler(DefaultScript):
    """
    Script that manages turn-based combat for all combatants in a location.
    
    This is the central orchestrator of combat encounters, handling:
    - Combat state management and lifecycle
    - Turn-based initiative and action resolution
    - Multi-room combat coordination through handler merging
    - Integration with proximity and grappling systems
    - Cleanup and state consistency
    
    The handler uses a database-backed combatants list with entries containing:
    - char: The character object
    - target_dbref: DBREF of their current target
    - grappling_dbref: DBREF of who they're grappling
    - grappled_by_dbref: DBREF of who's grappling them
    - is_yielding: Whether they're actively attacking
    """

    def at_script_creation(self):
        """
        Initialize combat handler script attributes.
        
        Sets up the initial state for a new combat handler, including
        the combatants list, round counter, and room management.
        """
        self.key = COMBAT_SCRIPT_KEY
        self.interval = COMBAT_ROUND_INTERVAL  # Use configurable round interval
        self.persistent = True
        
        # Initialize database attributes using constants
        setattr(self.db, DB_COMBATANTS, [])
        setattr(self.db, "round", 0)
        setattr(self.db, DB_MANAGED_ROOMS, [self.obj])  # Initially manages only its host room
        setattr(self.db, DB_COMBAT_RUNNING, False)
        setattr(self.db, "last_action_time", None)  # Track last hostile action for idle timeout
        
        splattercast = ChannelDB.objects.get_channel(SPLATTERCAST_CHANNEL)
        managed_rooms = getattr(self.db, DB_MANAGED_ROOMS, [])
        splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_CREATE: New handler {self.key} created on {self.obj.key}, initially managing: {[r.key for r in managed_rooms]}. Combat logic initially not running.")

    def start(self):
        """
        Start the combat handler's repeat timer if combat logic isn't already running
        or if the Evennia ticker isn't active.
        
        This method ensures the combat handler is properly running and handles
        cases where the internal state might be out of sync with Evennia's ticker.
        """
        splattercast = ChannelDB.objects.get_channel(SPLATTERCAST_CHANNEL)

        # Use super().is_active to check Evennia's ticker status
        evennia_ticker_is_active = super().is_active
        combat_is_running = getattr(self.db, DB_COMBAT_RUNNING, False)

        if combat_is_running and evennia_ticker_is_active:
            splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_START: Handler {self.key} on {self.obj.key} - combat logic and Evennia ticker are already active. Skipping redundant start.")
            return

        managed_rooms = getattr(self.db, DB_MANAGED_ROOMS, [])
        splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_START: Handler {self.key} on {self.obj.key} (managing {[r.key for r in managed_rooms]}) - ensuring combat logic is running and ticker is scheduled.")
        
        if not combat_is_running:
            splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_START_DETAIL: Setting {DB_COMBAT_RUNNING} = True for {self.key}.")
            setattr(self.db, DB_COMBAT_RUNNING, True)
        
        if not evennia_ticker_is_active:
            splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_START_DETAIL: Evennia ticker for {self.key} is not active (super().is_active=False). Calling force_repeat().")
            self.force_repeat()
        else:
            splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_START_DETAIL: Evennia ticker was already active, but combat logic flag was corrected.")

    def stop_combat_logic(self, cleanup_combatants=True):
        """
        Stop the combat logic while optionally cleaning up combatants.
        
        This method stops the internal combat logic flag and can optionally
        clean up all combatant state. The Evennia ticker may continue running
        but no combat processing will occur.
        
        Args:
            cleanup_combatants (bool): Whether to remove all combatants and clean state
        """
        # CRITICAL: Check if handler has been deleted or never saved
        # This can happen when:
        # 1. remove_combatant() calls stop_combat_logic() on already-deleted handler
        # 2. Handler was created but never saved to database
        if not self.pk or not self.id:
            return
        
        splattercast = ChannelDB.objects.get_channel(SPLATTERCAST_CHANNEL)
        
        combat_was_running = getattr(self.db, DB_COMBAT_RUNNING, False)
        
        splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_{DEBUG_CLEANUP}: Handler {self.key} stopping combat logic. Was running: {combat_was_running}, cleanup_combatants: {cleanup_combatants}")

        if cleanup_combatants:
            self._cleanup_all_combatants()
        
        # Determine if we should delete the script BEFORE modifying db attributes
        combatants = getattr(self.db, DB_COMBATANTS, [])
        should_delete_script = False
        if not combatants and self.pk:
            splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_{DEBUG_CLEANUP}: Handler {self.key} is empty and persistent. Marking for deletion.")
            should_delete_script = True
        
        if should_delete_script:
            # CRITICAL: Delete handler BEFORE setting db attributes
            # After delete(), self.pk becomes None and db attribute access will crash
            # See: COMBAT_HANDLER_DELETION_ANALYSIS.md
            splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_{DEBUG_CLEANUP}: Preparing to delete handler script {self.key}.")
            if hasattr(self, 'id') and self.id:
                try:
                    self.save()
                    self.delete()
                    splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_{DEBUG_CLEANUP}: Successfully deleted handler {self.key}.")
                    # Early return - handler is deleted, no further cleanup needed
                    return
                except Exception as e:
                    splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_{DEBUG_CLEANUP}: Error deleting handler {self.key}: {e}. Trying stop().")
                    try:
                        self.stop()
                        splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_{DEBUG_CLEANUP}: Successfully stopped handler {self.key}.")
                        return  # Don't continue if stop() succeeded - handler may be in invalid state
                    except Exception as e2:
                        splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_{DEBUG_CLEANUP}: Error stopping handler {self.key}: {e2}. Leaving as-is.")
                        return  # Don't continue if both delete() and stop() failed
            else:
                splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_{DEBUG_CLEANUP}: Handler {self.key} was not saved to database, skipping all database operations.")
                return
        
        # Only reach here if handler was NOT deleted
        # Now it's safe to modify db attributes (self.pk is still valid)
        setattr(self.db, DB_COMBAT_RUNNING, False)
        self.db.round = 0
        
        # Stop the ticker if the script is saved to the database
        if hasattr(self, 'id') and self.id:
            try:
                splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_{DEBUG_CLEANUP}: Handler {self.key} is not being deleted. Calling self.stop() to halt ticker.")
                self.stop()
            except Exception as e:
                splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_{DEBUG_CLEANUP}: Error stopping handler {self.key}: {e}. Leaving as-is.")
        else:
            splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_{DEBUG_CLEANUP}: Handler {self.key} is not saved to database, skipping stop() call.")
        
        splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_{DEBUG_CLEANUP}: Combat logic stopped for {self.key}. Round reset to 0.")

    def _cleanup_all_combatants(self):
        """
        Clean up all combatant state and remove them from the handler.
        
        This method clears all proximity relationships, breaks grapples,
        and removes combat-related NDB attributes from all combatants.
        """
        cleanup_all_combatants(self)

    def at_stop(self):
        """
        Called when the script is stopped.
        
        Performs cleanup of all combatant state when the handler is stopped,
        unless a merge is in progress.
        """
        # CRITICAL: Prevent recursive calls when delete() triggers at_stop()
        # If handler is already deleted, don't try to clean up again
        if not self.pk or not self.id:
            return
        
        splattercast = ChannelDB.objects.get_channel(SPLATTERCAST_CHANNEL)
        splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_STOP: Handler {self.key} at_stop() called. Cleaning up combat state.")
        
        # Skip cleanup if merge is in progress to preserve combatant references
        if hasattr(self, '_merge_in_progress') and self._merge_in_progress:
            splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_STOP: Merge in progress for {self.key}, skipping combatant cleanup.")
            self.stop_combat_logic(cleanup_combatants=False)
        else:
            self.stop_combat_logic(cleanup_combatants=True)

    def enroll_room(self, room_to_add):
        """
        Add a room to be managed by this handler.
        
        Args:
            room_to_add: The room to add to managed rooms
        """
        managed_rooms = getattr(self.db, DB_MANAGED_ROOMS, [])
        if room_to_add not in managed_rooms:
            managed_rooms.append(room_to_add)
            setattr(self.db, DB_MANAGED_ROOMS, managed_rooms)

    def merge_handler(self, other_handler):
        """
        Merge another combat handler into this one.
        
        This method handles the complex logic of merging two combat handlers
        when characters move between rooms that are managed by different handlers.
        
        Args:
            other_handler: The CombatHandler to merge into this one
        """
        splattercast = ChannelDB.objects.get_channel(SPLATTERCAST_CHANNEL)
        
        # Defensive logging to understand the merge scenario
        splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_MERGE_DEBUG: self={self} (key={self.key}, id={getattr(self, 'id', 'None')}, obj={self.obj.key})")
        splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_MERGE_DEBUG: other_handler={other_handler} (key={other_handler.key}, id={getattr(other_handler, 'id', 'None')}, obj={other_handler.obj.key})")
        splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_MERGE_DEBUG: Identity check: self is other_handler = {self is other_handler}")
        
        # Safety check: Don't merge a handler with itself
        if other_handler is self:
            splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_MERGE: Attempted to merge handler with itself. Skipping merge.")
            return
        
        # Get combatants from both handlers
        our_combatants = getattr(self.db, DB_COMBATANTS, [])
        their_combatants = getattr(other_handler.db, DB_COMBATANTS, [])
        
        # Merge combatants lists
        for entry in their_combatants:
            char = entry.get(DB_CHAR)
            if char and char not in [e.get(DB_CHAR) for e in our_combatants]:
                our_combatants.append(entry)
        
        # Merge managed rooms
        our_rooms = getattr(self.db, DB_MANAGED_ROOMS, [])
        their_rooms = getattr(other_handler.db, DB_MANAGED_ROOMS, [])
        for room in their_rooms:
            if room not in our_rooms:
                our_rooms.append(room)
        
        # Update our state
        setattr(self.db, DB_COMBATANTS, our_combatants)
        setattr(self.db, DB_MANAGED_ROOMS, our_rooms)
        
        # CRITICAL FIX: Update ALL combatants' handler references after merge
        # This ensures both existing and newly merged combatants point to the correct handler
        from .utils import update_all_combatant_handler_references
        update_all_combatant_handler_references(self)
        
        # Stop and clean up the other handler WITHOUT triggering at_stop cleanup
        # Set a flag to prevent at_stop() from cleaning up combatants during merge
        other_handler._merge_in_progress = True
        other_handler.stop_combat_logic(cleanup_combatants=False)
        
        # Only delete if the handler has been saved to the database
        if hasattr(other_handler, 'id') and other_handler.id:
            try:
                # Ensure the handler is properly saved before deletion
                other_handler.save()
                other_handler.delete()
                splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_MERGE: Deleted other handler {other_handler.key}.")
            except Exception as e:
                splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_MERGE: Error deleting other handler {other_handler.key}: {e}. Handler stopped but not deleted.")
        else:
            splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_MERGE: Other handler {other_handler.key} was not saved to database, skipping delete.")
        
        # Clear the merge flag now that deletion is complete
        if hasattr(other_handler, '_merge_in_progress'):
            delattr(other_handler, '_merge_in_progress')
        
        splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_MERGE: Merged {other_handler.key} into {self.key}. Now managing {len(our_rooms)} rooms with {len(our_combatants)} combatants.")

    def add_combatant(self, char, target=None, initial_grappling=None, initial_grappled_by=None, initial_is_yielding=False):
        """
        Add a character to combat.
        
        Args:
            char: The character to add
            target: Optional initial target
            initial_grappling: Optional character being grappled initially
            initial_grappled_by: Optional character grappling this char initially
            initial_is_yielding: Whether the character starts yielding
        """
        add_combatant(self, char, target, initial_grappling, initial_grappled_by, initial_is_yielding)

    def remove_combatant(self, char):
        """
        Remove a character from combat and clean up their state.
        
        Args:
            char: The character to remove from combat
        """
        remove_combatant(self, char)

    def _cleanup_combatant_state(self, char, entry):
        """
        Clean up all combat-related state for a character.
        
        Args:
            char: The character to clean up
            entry: The character's combat entry
        """
        cleanup_combatant_state(char, entry, self)

    def validate_and_cleanup_grapple_state(self):
        """
        Validate and clean up stale grapple references in the combat handler.
        
        This method checks for and fixes:
        - Stale DBREFs to characters no longer in the database
        - Invalid cross-references (A grappling B but B not grappled by A)
        - Self-grappling references
        - References to characters no longer in combat
        - Orphaned grapple states
        
        Called periodically during combat to maintain data integrity.
        """
        validate_and_cleanup_grapple_state(self)

    def at_repeat(self):
        """
        Main combat loop, processes each combatant's turn in initiative order.
        Handles attacks, misses, deaths, and round progression across managed rooms.
        """
        import time
        
        splattercast = ChannelDB.objects.get_channel(SPLATTERCAST_CHANNEL)
        if not getattr(self.db, DB_COMBAT_RUNNING, False):
            splattercast.msg(f"AT_REPEAT: Handler {self.key} on {self.obj.key} combat logic is not running ({DB_COMBAT_RUNNING}=False). Returning.")
            return

        if not super().is_active:
             splattercast.msg(f"AT_REPEAT: Handler {self.key} on {self.obj.key} Evennia script.is_active=False. Marking {DB_COMBAT_RUNNING}=False and returning.")
             setattr(self.db, DB_COMBAT_RUNNING, False)
             return

        # Check for idle combat (no action in last 60 seconds)
        last_action_time = getattr(self.db, "last_action_time", None)
        if last_action_time is not None:
            time_since_action = time.time() - last_action_time
            if time_since_action > 60:
                splattercast.msg(f"AT_REPEAT: Handler {self.key} - Combat idle for {time_since_action:.1f}s (>60s). Ending combat.")
                self.stop_combat_logic()
                return
        
        # Convert SaverList to regular list to avoid corruption during modifications
        combatants_list = []
        db_combatants = get_combatants_safe(self)
        for entry in db_combatants:
            # Convert each entry to a regular dict to avoid SaverList issues
            regular_entry = dict(entry)
            combatants_list.append(regular_entry)
        splattercast.msg(f"AT_REPEAT_DEBUG: Converted SaverList to regular list with {len(combatants_list)} entries")
        
        # Set up active list tracking for set_target to work during round processing
        self._active_combatants_list = combatants_list
        
        # Debug: Show target_dbref for all combatants at start of round
        for entry in combatants_list:
            char = entry.get(DB_CHAR)
            target_dbref = entry.get(DB_TARGET_DBREF)
            if char:
                splattercast.msg(f"AT_REPEAT_TARGET_DEBUG: {char.key} has target_dbref: {target_dbref}")
        
        # Debug: Also show what's actually in the database
        db_combatants_debug = get_combatants_safe(self)
        for entry in db_combatants_debug:
            char = entry.get(DB_CHAR)
            target_dbref = entry.get(DB_TARGET_DBREF)
            if char:
                splattercast.msg(f"AT_REPEAT_DB_DEBUG: {char.key} has target_dbref: {target_dbref} in database")

        # Validate and clean up stale grapple references
        self.validate_and_cleanup_grapple_state()

        # Remove orphaned combatants (no target, not grappling, not grappled, not targeted)
        from .utils import detect_and_remove_orphaned_combatants
        orphaned_chars = detect_and_remove_orphaned_combatants(self)
        if orphaned_chars:
            # Re-fetch combatants list after orphan removal
            combatants_list = []
            db_combatants = get_combatants_safe(self)
            for entry in db_combatants:
                regular_entry = dict(entry)
                combatants_list.append(regular_entry)
            # Update active list reference after orphan removal
            self._active_combatants_list = combatants_list

        valid_combatants_entries = []
        managed_rooms = getattr(self.db, DB_MANAGED_ROOMS, [])
        for entry in combatants_list:
            char = entry.get(DB_CHAR)
            if not char:
                splattercast.msg(f"AT_REPEAT: Pruning missing character from handler {self.key}.")
                continue
            if not char.location:
                splattercast.msg(f"AT_REPEAT: Pruning {char.key} (no location) from handler {self.key}.")
                if hasattr(char, "ndb") and getattr(char.ndb, NDB_COMBAT_HANDLER) == self:
                    delattr(char.ndb, NDB_COMBAT_HANDLER)
                continue
            if char.location not in managed_rooms:
                splattercast.msg(f"AT_REPEAT: Pruning {char.key} (in unmanaged room {char.location.key}) from handler {self.key}.")
                if hasattr(char, "ndb") and getattr(char.ndb, NDB_COMBAT_HANDLER) == self:
                    delattr(char.ndb, NDB_COMBAT_HANDLER)
                continue
            valid_combatants_entries.append(entry)
        
        # Update the working list
        combatants_list = valid_combatants_entries
        # Update active list reference after validation
        self._active_combatants_list = combatants_list

        if not combatants_list:
            splattercast.msg(f"AT_REPEAT: No valid combatants remain in managed rooms for handler {self.key}. Stopping.")
            self._active_combatants_list = None  # Clear active list tracking
            self.stop_combat_logic()
            return

        if self.db.round == 0:
            if len(combatants_list) > 0:
                splattercast.msg(f"AT_REPEAT: Handler {self.key}. Combatants present. Starting combat in round 1.")
                self.db.round = 1
            else:
                splattercast.msg(f"AT_REPEAT: Handler {self.key}. Waiting for combatants to join...")
                # Save the list back before returning
                setattr(self.db, DB_COMBATANTS, combatants_list)
                self._active_combatants_list = None  # Clear active list tracking
                return

        splattercast.msg(f"AT_REPEAT: Handler {self.key} (managing {[r.key for r in managed_rooms]}). Round {self.db.round} begins.")
        
        # --- PER-ROUND STAMINA DRAIN & COMBAT PROMPT ---
        for entry in combatants_list:
            char = entry.get(DB_CHAR)
            if char and not char.is_dead():
                # Drain stamina each round (combat fatigue)
                stamina = getattr(char.ndb, "stamina", None)
                if stamina:
                    stamina.stamina_current = max(0, stamina.stamina_current - STAMINA_DRAIN_PER_ROUND)
                    splattercast.msg(f"STAMINA_DRAIN_ROUND: {char.key} drained {STAMINA_DRAIN_PER_ROUND} stamina, now at {stamina.stamina_current:.1f}")
                
                # Check for disguise slip due to combat
                try:
                    from world.disguise.core import (
                        check_disguise_slip, trigger_slip_event, 
                        get_anonymity_item, damage_disguise_stability
                    )
                    from world.combat.constants import STABILITY_DAMAGE_COMBAT
                    
                    # Damage skill-based disguise stability in combat
                    damage_disguise_stability(char, STABILITY_DAMAGE_COMBAT, reason="combat")
                    
                    # Check for slip (only applies if character is disguised)
                    slipped, slip_type = check_disguise_slip(char, "combat")
                    if slipped:
                        item, _ = get_anonymity_item(char)
                        trigger_slip_event(char, slip_type, item=item)
                        splattercast.msg(f"DISGUISE_SLIP: {char.key} disguise slipped in combat (type: {slip_type})")
                except ImportError as e:
                    pass  # Disguise system not available
                except Exception as e:
                    splattercast.msg(f"ERROR in disguise slip check for {char.key}: {e}")
                
                # Combat status prompt is now automatically appended to all messages via Character.msg()
                # No need to send it explicitly here
        
        if len(combatants_list) <= 1:
            splattercast.msg(f"AT_REPEAT: Handler {self.key}. Not enough combatants ({len(combatants_list)}) to continue. Ending combat.")
            self._active_combatants_list = None  # Clear active list tracking
            self.stop_combat_logic()
            return

        # Check if all combatants are yielding - if so, end combat peacefully
        # BUT ONLY if there are no active grapples happening
        all_yielding = all(entry.get(DB_IS_YIELDING, False) for entry in combatants_list)
        any_active_grapples = any(
            entry.get(DB_GRAPPLING_DBREF) is not None or entry.get(DB_GRAPPLED_BY_DBREF) is not None
            for entry in combatants_list
        )
        
        if all_yielding and not any_active_grapples:
            splattercast.msg(f"AT_REPEAT: Handler {self.key}. All combatants are yielding with no active grapples. Ending combat peacefully.")
            # Send a message to all combatants about peaceful resolution
            for entry in combatants_list:
                char = entry.get(DB_CHAR)
                if char and char.location:
                    char.msg("|gWith all hostilities ceased, the confrontation comes to a peaceful end.|n")
            # Notify observers in all managed rooms
            for room in managed_rooms:
                if room:
                    room.msg_contents("|gThe confrontation ends peacefully as all participants stand down.|n", 
                                    exclude=[entry.get(DB_CHAR) for entry in combatants_list if entry.get(DB_CHAR)])
            self._active_combatants_list = None  # Clear active list tracking
            self.stop_combat_logic()
            return
        elif all_yielding and any_active_grapples:
            splattercast.msg(f"AT_REPEAT: Handler {self.key}. All combatants yielding but active grapples present. Combat continues in restraint mode.")

        # Sort combatants by initiative for processing
        initiative_order = sorted(combatants_list, key=lambda e: e.get("initiative", 0), reverse=True)
        
        for combat_entry in initiative_order:
            char = combat_entry.get(DB_CHAR)
            splattercast.msg(f"DEBUG_LOOP_ITERATION: Starting processing for {char.key}, combat_entry: {combat_entry}")

            # Always get a fresh reference to ensure we have current data
            current_char_combat_entry = next((e for e in combatants_list if e.get(DB_CHAR) == char), None)
            if not current_char_combat_entry:
                splattercast.msg(f"AT_REPEAT: {char.key} no longer in combatants list. Skipping.")
                continue

            # Skip if character is dead or unconscious (prevents redundant processing after immediate removal)
            if char.is_dead():
                splattercast.msg(f"AT_REPEAT: {char.key} is dead, skipping turn.")
                continue
            elif hasattr(char, 'is_unconscious') and char.is_unconscious():
                splattercast.msg(f"AT_REPEAT: {char.key} is unconscious, skipping turn.")
                continue

            # Skip if character has skip_combat_round flag
            if hasattr(char.ndb, NDB_SKIP_ROUND) and getattr(char.ndb, NDB_SKIP_ROUND):
                delattr(char.ndb, NDB_SKIP_ROUND)
                splattercast.msg(f"AT_REPEAT: {char.key} skipping this round as requested.")
                char.msg("|yYou skip this combat round.|n")
                continue

            # Clear flee attempt flag at start of each round
            if hasattr(char.ndb, "flee_attempted_this_round"):
                delattr(char.ndb, "flee_attempted_this_round")
                splattercast.msg(f"AT_REPEAT: Cleared flee attempt flag for {char.key} at start of new round.")

            # START-OF-TURN NDB CLEANUP for charge flags
            if hasattr(char.ndb, "charging_vulnerability_active"):
                splattercast.msg(f"AT_REPEAT_START_TURN_CLEANUP: Clearing charging_vulnerability_active for {char.key} (was active from their own previous charge).")
                delattr(char.ndb, "charging_vulnerability_active")
            
            # Note: charge_attack_bonus_active is consumed automatically when used in attacks.
            # No need to clean it up here as it should be consumed during the attack phase.
            # Only clean it up if it exists AND has a truthy value AND the character is not going to attack this turn.
            if hasattr(char.ndb, "charge_attack_bonus_active") and getattr(char.ndb, "charge_attack_bonus_active", False):
                # In auto-combat, all characters attack, so bonus will be consumed naturally
                # Only clean up if character won't attack (yielding, dead, unconscious, etc.)
                if (current_char_combat_entry.get(DB_IS_YIELDING, False) or 
                    char.is_dead() or 
                    (hasattr(char, 'is_unconscious') and char.is_unconscious())):
                    splattercast.msg(f"AT_REPEAT_START_TURN_CLEANUP: Clearing unused charge_attack_bonus_active for {char.key} (won't attack this turn).")
                    delattr(char.ndb, "charge_attack_bonus_active")
                else:
                    splattercast.msg(f"AT_REPEAT_START_TURN_CLEANUP: {char.key} has charge_attack_bonus_active - will be consumed during attack.")

            # Get combat action for this character
            combat_action = current_char_combat_entry.get("combat_action")
            splattercast.msg(f"AT_REPEAT: {char.key} combat_action: {combat_action}")

            # Check if character is yielding first
            if current_char_combat_entry.get(DB_IS_YIELDING, False):
                # Exception: Allow certain actions even when yielding
                if combat_action in ["release_grapple", COMBAT_ACTION_ADVANCE, COMBAT_ACTION_RETREAT, COMBAT_ACTION_CHARGE]:
                    splattercast.msg(f"{char.key} is yielding but can still perform {combat_action} action.")
                    # Fall through to normal action processing
                else:
                    # Check if this character is grappling someone (restraint mode)
                    grappling_target = self.get_grappling_obj(current_char_combat_entry)
                    if grappling_target:
                        # Grappler in restraint mode - maintain hold without violence
                        splattercast.msg(f"{char.key} is yielding but maintains restraining hold on {grappling_target.key}.")
                        char.msg(f"You maintain a restraining hold on {get_display_name_safe(grappling_target, char)} without violence.")
                        grappling_target.msg(f"{get_display_name_safe(char, grappling_target)} maintains a gentle but firm restraining hold on you.")
                        msg_contents_disguised(char.location, "|g{char0_name} maintains a restraining hold on {char1_name}.|n", [char, grappling_target], exclude=[char, grappling_target])
                    else:
                        # Regular yielding behavior
                        splattercast.msg(f"{char.key} is yielding and takes no hostile action this turn.")
                        msg_contents_disguised(char.location, "|y{char_name} holds their action, appearing non-hostile.|n", char, exclude=[char])
                        char.msg("|yYou hold your action, appearing non-hostile.|n")
                    continue
                
            # Handle being grappled (auto resist unless yielding)
            grappler = self.get_grappled_by_obj(current_char_combat_entry)
            if grappler:
                # Safety check: prevent self-grappling and invalid grappler
                if grappler == char:
                    splattercast.msg(f"GRAPPLE_ERROR: {char.key} is grappled by themselves! Clearing invalid state.")
                    current_char_combat_entry[DB_GRAPPLED_BY_DBREF] = None
                    grappler = None
                elif not any(e[DB_CHAR] == grappler for e in combatants_list):
                    splattercast.msg(f"GRAPPLE_ERROR: {char.key} is grappled by {grappler.key} who is not in combat! Clearing invalid state.")
                    current_char_combat_entry[DB_GRAPPLED_BY_DBREF] = None
                    grappler = None
                    
            if grappler:
                # Check if the victim is yielding (restraint mode acceptance)
                if current_char_combat_entry.get(DB_IS_YIELDING, False):
                    # Victim is yielding/accepting restraint - no automatic escape attempt
                    splattercast.msg(f"{char.key} is being grappled by {grappler.key} but is yielding (accepting restraint).")
                    char.msg(f"You remain still in {get_display_name_safe(grappler, char)}'s hold, not resisting.")
                    msg_contents_disguised(char.location, "|g{char0_name} does not resist {char1_name}'s hold.|n", [char, grappler], exclude=[char])
                    continue
                    
                # Victim is not yielding - automatically attempt to escape
                splattercast.msg(f"{char.key} is being grappled by {grappler.key} and automatically attempts to escape.")
                char.msg(f"|yYou struggle against {grappler.key}'s grip!|n")
                
                # Setup an escape attempt using new 0-100 skill system
                # Escaper uses whichever is better: BODY or DEX (physical escape)
                # Grappler uses BODY + grappling skill to hold on
                escaper_body = getattr(char.db, "body", 1) or 1
                escaper_dex = getattr(char.db, "dexterity", 1) or 1
                
                grappler_grappling = getattr(grappler.db, "grappling", 0) or 0
                using_brawling_fallback = False
                if grappler_grappling == 0:
                    # Fallback to brawling with penalty
                    grappler_grappling = (getattr(grappler.db, "brawling", 0) or 0) // 3
                    using_brawling_fallback = True
                grappler_body = getattr(grappler.db, "body", 1) or 1
                
                # Calculate stat bonuses
                # Escaper uses whichever stat is more advantageous
                escaper_combined_stat = max(escaper_body, escaper_dex)
                # Grappler uses BODY to hold on
                grappler_combined_stat = grappler_body
                
                escape_result = combat_roll(
                    attacker_skill=escaper_dodge,
                    defender_skill=grappler_grappling,
                    attacker_stat=escaper_combined_stat,
                    defender_stat=grappler_combined_stat
                )
                escaper_roll = escape_result['attacker_roll']
                grappler_roll = escape_result['defender_roll']
                esc_dice, esc_bonus = escape_result['attacker_details']
                grp_dice, grp_bonus = escape_result['defender_details']
                
                fallback_note = " (brawling/3)" if using_brawling_fallback else ""
                splattercast.msg(f"AUTO_ESCAPE_ATTEMPT: {char.key} [max(BODY:{escaper_body},DEX:{escaper_dex})*5={escaper_combined_stat*5:.1f}=d20:{esc_dice}+bonus:{esc_bonus}=roll {escaper_roll}] vs {grappler.key} [grappling{fallback_note}:{grappler_grappling}+BODY*5:{grappler_body*5}=d20:{grp_dice}+bonus:{grp_bonus}=roll {grappler_roll}].")

                if escaper_roll > grappler_roll:
                    # Success - clear grapple
                    current_char_combat_entry[DB_GRAPPLED_BY_DBREF] = None
                    grappler_entry = next((e for e in combatants_list if e[DB_CHAR] == grappler), None)
                    if grappler_entry:
                        grappler_entry[DB_GRAPPLING_DBREF] = None
                    
                    # Successful auto-escape switches victim to violent mode (fighting for their life)
                    was_yielding = current_char_combat_entry.get(DB_IS_YIELDING, False)
                    current_char_combat_entry[DB_IS_YIELDING] = False
                    
                    # Ensure the victim has the grappler as their target for retaliation
                    if not current_char_combat_entry.get(DB_TARGET_DBREF):
                        current_char_combat_entry[DB_TARGET_DBREF] = self._get_dbref(grappler)
                        splattercast.msg(f"AUTO_ESCAPE_TARGET: {char.key} targets {grappler.key} after escaping.")
                    
                    escape_messages = get_combat_message("grapple", "escape_hit", attacker=char, target=grappler)
                    char.msg(escape_messages.get("attacker_msg", f"You break free from {grappler.key}'s grasp!"))
                    grappler.msg(escape_messages.get("victim_msg", f"{char.key} breaks free from your grasp!"))
                    obs_msg = escape_messages.get("observer_msg", f"{char.key} breaks free from {grappler.key}'s grasp!")
                    char.location.msg_contents(obs_msg, exclude=[char, grappler])
                    
                    # Additional message if they switched from yielding to violent
                    if was_yielding:
                        char.msg(MSG_GRAPPLE_AUTO_ESCAPE_VIOLENT)
                    
                    splattercast.msg(f"AUTO_ESCAPE_SUCCESS: {char.key} escaped from {grappler.key}.")
                else:
                    # Failure
                    escape_messages = get_combat_message("grapple", "escape_miss", attacker=char, target=grappler)
                    char.msg(escape_messages.get("attacker_msg", f"You struggle but fail to break free from {grappler.key}'s grasp!"))
                    grappler.msg(escape_messages.get("victim_msg", f"{char.key} struggles but fails to break free from your grasp!"))
                    obs_msg = escape_messages.get("observer_msg", f"{char.key} struggles but fails to break free from {grappler.key}'s grasp!")
                    char.location.msg_contents(obs_msg, exclude=[char, grappler])
                    splattercast.msg(f"AUTO_ESCAPE_FAIL: {char.key} failed to escape {grappler.key}.")
                    
                # Either way, turn ends after escape attempt
                continue

            # Process combat action intent
            if combat_action:
                splattercast.msg(f"AT_REPEAT: {char.key} has action_intent: {combat_action}")
                
                if isinstance(combat_action, str):
                    if combat_action == "grapple_initiate":
                        self._resolve_grapple_initiate(current_char_combat_entry, combatants_list)
                        current_char_combat_entry["combat_action"] = None
                        continue
                    elif combat_action == "grapple_join":
                        self._resolve_grapple_join(current_char_combat_entry, combatants_list)
                        current_char_combat_entry["combat_action"] = None
                        continue
                    elif combat_action == "grapple_takeover":
                        self._resolve_grapple_takeover(current_char_combat_entry, combatants_list)
                        current_char_combat_entry["combat_action"] = None
                        continue
                    elif combat_action == "release_grapple":
                        self._resolve_release_grapple(current_char_combat_entry, combatants_list)
                        current_char_combat_entry["combat_action"] = None
                        continue
                    elif combat_action == "choke":
                        self._resolve_choke(current_char_combat_entry, combatants_list)
                        current_char_combat_entry["combat_action"] = None
                        continue
                    elif combat_action == COMBAT_ACTION_RETREAT:
                        self._resolve_retreat(char, current_char_combat_entry)
                        current_char_combat_entry["combat_action"] = None
                        current_char_combat_entry["combat_action_target"] = None
                        continue
                    elif combat_action == COMBAT_ACTION_ADVANCE:
                        self._resolve_advance(char, current_char_combat_entry)
                        current_char_combat_entry["combat_action"] = None
                        current_char_combat_entry["combat_action_target"] = None
                        continue
                    elif combat_action == COMBAT_ACTION_CHARGE:
                        self._resolve_charge(char, current_char_combat_entry, combatants_list)
                        current_char_combat_entry["combat_action"] = None
                        current_char_combat_entry["combat_action_target"] = None
                        continue
                    elif combat_action == COMBAT_ACTION_DISARM:
                        self._resolve_disarm(char, current_char_combat_entry)
                        current_char_combat_entry["combat_action"] = None
                        current_char_combat_entry["combat_action_target"] = None
                        continue
                    elif combat_action == COMBAT_ACTION_RELOAD:
                        self._resolve_reload(char, current_char_combat_entry)
                        current_char_combat_entry["combat_action"] = None
                        continue
                elif isinstance(combat_action, dict):
                    intent_type = combat_action.get("type")
                    action_target_char = combat_action.get("target")
                    
                    # Validate target
                    is_action_target_valid = False
                    if action_target_char and any(e[DB_CHAR] == action_target_char for e in combatants_list):
                        if action_target_char.location and action_target_char.location in getattr(self.db, DB_MANAGED_ROOMS, []):
                            is_action_target_valid = True
                    
                    if not is_action_target_valid and action_target_char:
                        char.msg(f"The target of your planned action ({action_target_char.key}) is no longer valid.")
                        splattercast.msg(f"{char.key}'s action_intent target {action_target_char.key} is invalid. Intent cleared, falling through.")
                    elif intent_type == "grapple" and is_action_target_valid:
                        # Handle grapple intent
                        can_grapple_target = (char.location == action_target_char.location)
                        
                        if can_grapple_target:
                            # Proximity Check for Grapple
                            if not hasattr(char.ndb, NDB_PROXIMITY): 
                                setattr(char.ndb, NDB_PROXIMITY, set())
                            
                            proximity_set = getattr(char.ndb, NDB_PROXIMITY, set())
                            if not proximity_set:
                                setattr(char.ndb, NDB_PROXIMITY, set())
                                proximity_set = set()
                            
                            # RELOAD RECOVERY: If characters are in mutual combat, restore proximity
                            if action_target_char not in proximity_set and self._are_characters_in_mutual_combat(char, action_target_char):
                                proximity_set.add(action_target_char)
                                setattr(char.ndb, NDB_PROXIMITY, proximity_set)
                                splattercast.msg(f"GRAPPLE_PROXIMITY_RESTORE: {char.key} and {action_target_char.key} proximity restored.")
                            
                            if action_target_char not in proximity_set:
                                char.msg(f"You need to be in melee proximity with {action_target_char.key} to grapple them. Try advancing or charging.")
                                splattercast.msg(f"GRAPPLE FAIL (PROXIMITY): {char.key} not in proximity with {action_target_char.key}.")
                                continue

                            # Grapple roll: Using new 0-100 skill system
                            # Brawling vs Athletics with REF modifier
                            attacker_ref = getattr(char.db, "ref", 1) or 1
                            attacker_brawling = getattr(char.db, "brawling", 0) or 0
                            defender_ref = getattr(action_target_char.db, "ref", 1) or 1
                            defender_athletics = getattr(action_target_char.db, "athletics", 0) or 0
                            
                            grapple_result = combat_roll(
                                attacker_skill=attacker_brawling,
                                defender_skill=defender_athletics,
                                attacker_stat=attacker_ref,
                                defender_stat=defender_ref
                            )
                            attacker_roll = grapple_result['attacker_roll']
                            defender_roll = grapple_result['defender_roll']
                            atk_dice, atk_bonus = grapple_result['attacker_details']
                            def_dice, def_bonus = grapple_result['defender_details']
                            splattercast.msg(f"GRAPPLE ATTEMPT: {char.key} [brawling:{attacker_brawling}+REF*5:{attacker_ref*5}=d20:{atk_dice}+bonus:{atk_bonus}=roll {attacker_roll}] vs {action_target_char.key} [DEX*5:{defender_dex*5}+REF*5:{defender_ref*5}=d20:{def_dice}+bonus:{def_bonus}=roll {defender_roll}].")


                            if attacker_roll > defender_roll:
                                # Store dbrefs for persistence
                                current_char_combat_entry[DB_GRAPPLING_DBREF] = self._get_dbref(action_target_char)
                                target_entry = next((e for e in combatants_list if e[DB_CHAR] == action_target_char), None)
                                if target_entry:
                                    target_entry[DB_GRAPPLED_BY_DBREF] = self._get_dbref(char)
                                
                                # Auto-yield both parties on successful grapple (restraint mode)
                                current_char_combat_entry[DB_IS_YIELDING] = True
                                if target_entry:
                                    target_entry[DB_IS_YIELDING] = True
                                
                                # Notify victim they're auto-yielding
                                action_target_char.msg(MSG_GRAPPLE_AUTO_YIELD)
                                
                                grapple_messages = get_combat_message("grapple", "hit", attacker=char, target=action_target_char)
                                char.msg(grapple_messages.get("attacker_msg"))
                                action_target_char.msg(grapple_messages.get("victim_msg"))
                                obs_msg = grapple_messages.get("observer_msg")
                                if char.location:
                                    char.location.msg_contents(obs_msg, exclude=[char, action_target_char])
                                splattercast.msg(f"GRAPPLE_SUCCESS: {char.key} grappled {action_target_char.key}.")
                            else:
                                # Grapple failed
                                grapple_messages = get_combat_message("grapple", "miss", attacker=char, target=action_target_char)
                                char.msg(grapple_messages.get("attacker_msg"))
                                action_target_char.msg(grapple_messages.get("victim_msg"))
                                obs_msg = grapple_messages.get("observer_msg")
                                if char.location:
                                    char.location.msg_contents(obs_msg, exclude=[char, action_target_char])
                                splattercast.msg(f"GRAPPLE_FAIL: {char.key} failed to grapple {action_target_char.key}.")
                        else:
                            char.msg(f"You can't reach {action_target_char.key} to grapple them from here.")
                            splattercast.msg(f"GRAPPLE FAIL (REACH): {char.key} cannot reach {action_target_char.key}.")
                        
                        continue
                    elif intent_type == "escape_grapple":
                        grappler = self.get_grappled_by_obj(current_char_combat_entry)
                        if grappler and any(e[DB_CHAR] == grappler for e in combatants_list):
                            # Escape roll: Using new 0-100 skill system
                            # Escaper uses whichever is better: BODY or DEX
                            # Grappler uses BODY + grappling skill to hold on
                            escaper_body = getattr(char.db, "body", 1) or 1
                            escaper_dex = getattr(char.db, "dexterity", 1) or 1
                            
                            grappler_grappling = getattr(grappler.db, "grappling", 0) or 0
                            using_brawling_fallback = False
                            if grappler_grappling == 0:
                                # Fallback to brawling with penalty
                                grappler_grappling = (getattr(grappler.db, "brawling", 0) or 0) // 3
                                using_brawling_fallback = True
                            grappler_body = getattr(grappler.db, "body", 1) or 1
                            
                            # Calculate stat bonuses
                            escaper_combined_stat = max(escaper_body, escaper_dex)
                            grappler_combined_stat = grappler_body
                            
                            escape_result = combat_roll(
                                attacker_skill=escaper_dodge,
                                defender_skill=grappler_grappling,
                                attacker_stat=escaper_combined_stat,
                                defender_stat=grappler_combined_stat
                            )
                            escaper_roll = escape_result['attacker_roll']
                            grappler_roll = escape_result['defender_roll']
                            esc_dice, esc_bonus = escape_result['attacker_details']
                            grp_dice, grp_bonus = escape_result['defender_details']
                            fallback_note = " (brawling/3)" if using_brawling_fallback else ""
                            splattercast.msg(f"ESCAPE ATTEMPT: {char.key} [max(BODY:{escaper_body},DEX:{escaper_dex})*5={escaper_combined_stat*5:.1f}=d20:{esc_dice}+bonus:{esc_bonus}=roll {escaper_roll}] vs {grappler.key} [grappling{fallback_note}:{grappler_grappling}+BODY*5:{grappler_body*5}=d20:{grp_dice}+bonus:{grp_bonus}=roll {grappler_roll}].")

                            if escaper_roll > grappler_roll:
                                current_char_combat_entry[DB_GRAPPLED_BY_DBREF] = None
                                grappler_entry = next((e for e in combatants_list if e[DB_CHAR] == grappler), None)
                                if grappler_entry:
                                    grappler_entry[DB_GRAPPLING_DBREF] = None
                                escape_messages = get_combat_message("grapple", "escape_hit", attacker=char, target=grappler)
                                char.msg(escape_messages.get("attacker_msg"))
                                grappler.msg(escape_messages.get("victim_msg"))
                                obs_msg = escape_messages.get("observer_msg")
                                char.location.msg_contents(obs_msg, exclude=[char, grappler])
                                splattercast.msg(f"ESCAPE SUCCESS: {char.key} escaped from {grappler.key}.")
                            else:
                                escape_messages = get_combat_message("grapple", "escape_miss", attacker=char, target=grappler)
                                char.msg(escape_messages.get("attacker_msg"))
                                grappler.msg(escape_messages.get("victim_msg"))
                                obs_msg = escape_messages.get("observer_msg")
                                char.location.msg_contents(obs_msg, exclude=[char, grappler])
                                splattercast.msg(f"ESCAPE FAIL: {char.key} failed to escape {grappler.key}.")
                        continue

            # Standard attack processing - get target and schedule attack with staggered timing
            target = self.get_target(char)
            splattercast.msg(f"AT_REPEAT: After get_target(), {char.key} target is {target.key if target else None}")
            if target:
                # Calculate attack delay based on position in initiative order
                attack_delay = self._calculate_attack_delay(char, initiative_order)
                
                splattercast.msg(f"AT_REPEAT: Scheduling attack for {char.key} -> {target.key} with {attack_delay}s delay")
                
                # Schedule the attack with delay to stagger combat messages
                delay(attack_delay, self._process_delayed_attack, char, target, current_char_combat_entry, combatants_list)
            else:
                splattercast.msg(f"AT_REPEAT: {char.key} has no valid target for attack.")

            # Clear the combat action after processing
            current_char_combat_entry["combat_action"] = None

        # Check for dead or unconscious combatants after all attacks are processed
        # NOTE: Keep _active_combatants_list alive so remove_combatant can use it for auto-retargeting
        remaining_combatants = getattr(self.db, DB_COMBATANTS, [])
        incapacitated_combatants = []
        
        for entry in remaining_combatants:
            char = entry.get(DB_CHAR)
            if char and hasattr(char, 'is_dead') and char.is_dead():
                incapacitated_combatants.append(char)
                splattercast.msg(f"POST_ROUND_DEATH_CHECK: {char.key} is dead, removing from combat.")
            elif char and hasattr(char, 'is_unconscious') and char.is_unconscious():
                incapacitated_combatants.append(char)
                splattercast.msg(f"POST_ROUND_UNCONSCIOUS_CHECK: {char.key} is unconscious, removing from combat.")
                
        # Remove dead and unconscious combatants
        for incapacitated_char in incapacitated_combatants:
            self.remove_combatant(incapacitated_char)

        # Now clear active list tracking since death/unconscious processing is complete
        # and any auto-retargeting has been handled
        self._active_combatants_list = None

        # Check if combat should continue
        remaining_combatants = getattr(self.db, DB_COMBATANTS, [])
        if not remaining_combatants:
            splattercast.msg(f"AT_REPEAT: No combatants remain in handler {self.key}. Stopping.")
            self._active_combatants_list = None  # Clear active list tracking
            self.stop_combat_logic()
            return
        elif len(remaining_combatants) <= 1:
            splattercast.msg(f"AT_REPEAT: Only {len(remaining_combatants)} combatant(s) remain in handler {self.key}. Ending combat.")
            self._active_combatants_list = None  # Clear active list tracking
            self.stop_combat_logic()
            return

        # Save the modified combatants list back to the database to persist combat_action changes
        self.db.combatants = combatants_list
        splattercast.msg(f"AT_REPEAT_SAVE: Saved modified combatants list back to database.")
        
        self.db.round += 1
        splattercast.msg(f"AT_REPEAT: Handler {self.key}. Round {self.db.round} scheduled for next interval.")

    def get_target(self, char):
        """Get the target character for a given character."""
        # Use active list if available (during round processing), otherwise use database
        active_list = getattr(self, '_active_combatants_list', None)
        if active_list:
            combatants_list = active_list
        else:
            combatants_list = getattr(self.db, DB_COMBATANTS, [])
        
        entry = next((e for e in combatants_list if e.get(DB_CHAR) == char), None)
        if entry:
            return self.get_target_obj(entry)
        return None
    
    def set_target(self, char, target):
        """Set the target for a given character."""
        splattercast = ChannelDB.objects.get_channel(SPLATTERCAST_CHANNEL)
        
        # Follow the same pattern as utils.py functions:
        # 1. Get a copy of the combatants list
        # 2. Modify the copy
        # 3. Save the entire modified copy back
        combatants = getattr(self.db, DB_COMBATANTS, [])
        db_entry = next((e for e in combatants if e.get(DB_CHAR) == char), None)
        
        if db_entry:
            new_target_dbref = self._get_dbref(target) if target else None
            old_target_dbref = db_entry.get(DB_TARGET_DBREF)
            
            # Update database entry in the copy
            db_entry[DB_TARGET_DBREF] = new_target_dbref
            
            # CRITICAL: Also update active processing list if it exists
            # This prevents the working copy from reverting the change at end of round
            active_list = getattr(self, '_active_combatants_list', None)
            if active_list:
                active_entry = next((e for e in active_list if e.get(DB_CHAR) == char), None)
                if active_entry:
                    active_entry[DB_TARGET_DBREF] = new_target_dbref
                    splattercast.msg(f"SET_TARGET: Updated both DB and active list for {char.key}")
            
            # Save the modified copy back (following utils.py pattern)
            setattr(self.db, DB_COMBATANTS, combatants)
            
            if target:
                splattercast.msg(f"SET_TARGET: {char.key} target changed from {old_target_dbref} to {new_target_dbref} ({target.key})")
                # Verify the change was saved
                verification_list = getattr(self.db, DB_COMBATANTS, [])
                verification_entry = next((e for e in verification_list if e.get(DB_CHAR) == char), None)
                if verification_entry:
                    actual_dbref = verification_entry.get(DB_TARGET_DBREF)
                    splattercast.msg(f"SET_TARGET_VERIFY: {char.key} database now shows target_dbref: {actual_dbref}")
            else:
                splattercast.msg(f"SET_TARGET: {char.key} target cleared to None")
            
            return True
        return False
    
    # ...existing utility methods...
    def get_target_obj(self, combatant_entry):
        """Get the target object for a combatant entry."""
        return get_combatant_target(combatant_entry, self)
    
    def get_grappling_obj(self, combatant_entry):
        """Get the character that this combatant is grappling."""
        return get_combatant_grappling_target(combatant_entry, self)
    
    def get_grappled_by_obj(self, combatant_entry):
        """Get the character that is grappling this combatant."""
        return get_combatant_grappled_by(combatant_entry, self)
    
    def _get_dbref(self, char):
        """Get DBREF for a character object."""
        return get_character_dbref(char)
    
    def _get_char_by_dbref(self, dbref):
        """Get character object by DBREF."""
        return get_character_by_dbref(dbref)
    
    def _are_characters_in_mutual_combat(self, char1, char2):
        """
        Check if two characters are targeting each other in active combat.
        Used to restore proximity after server reloads.
        """
        combatants_list = getattr(self.db, DB_COMBATANTS, [])
        char1_entry = None
        char2_entry = None
        
        # Find both characters in combatants list
        for entry in combatants_list:
            if entry["char"] == char1:
                char1_entry = entry
            elif entry["char"] == char2:
                char2_entry = entry
        
        # Both must be in combat and targeting each other
        if char1_entry and char2_entry:
            char1_target_dbref = char1_entry.get("target_dbref")
            char2_target_dbref = char2_entry.get("target_dbref") 
            char1_dbref = self._get_dbref(char1)
            char2_dbref = self._get_dbref(char2)
            
            return (char1_target_dbref == char2_dbref and 
                   char2_target_dbref == char1_dbref)
        
        return False
    
    def _validate_and_clean_weapons(self, character):
        """
        Validate that all wielded weapons are still in the character's inventory.
        Clears hands of any weapons that have been lost or dropped.
        
        Args:
            character: The character to validate
        """
        splattercast = ChannelDB.objects.get_channel(SPLATTERCAST_CHANNEL)
        
        if not hasattr(character, 'hands'):
            return
        
        hands = character.hands
        weapons_lost = []
        
        for hand, weapon in hands.items():
            if weapon and weapon.location != character:
                # Weapon is no longer in character's inventory
                weapons_lost.append((hand, weapon))
                hands[hand] = None
        
        if weapons_lost:
            # Save the cleaned hands
            character.hands = hands
            
            # Log lost weapons
            for hand, weapon in weapons_lost:
                character.msg(f"|r[Combat System] Your {weapon.key} was lost!|n")
                splattercast.msg(f"WEAPON_LOST: {character.key} lost {weapon.key} from {hand} hand (location mismatch)")
    
    def _calculate_attack_delay(self, attacker, initiative_order):
        """
        Calculate attack delay to stagger combat messages within a round.
        
        Args:
            attacker: The attacking character
            initiative_order: List of combatants in initiative order
            
        Returns:
            float: Delay in seconds for this attacker's attack
        """
        # Find attacker's position in initiative order
        attacker_position = 0
        for i, entry in enumerate(initiative_order):
            if entry.get(DB_CHAR) == attacker:
                attacker_position = i
                break
        
        # Stagger attacks using configurable interval
        # First attacker goes immediately, subsequent attackers are delayed
        base_delay = attacker_position * STAGGER_DELAY_INTERVAL
        
        # Cap at max delay to ensure all attacks complete before next round
        return min(base_delay, MAX_STAGGER_DELAY)

    def _process_delayed_attack(self, attacker, target, attacker_entry, combatants_list):
        """
        Process a delayed attack - wrapper for _process_attack with validation.
        
        Args:
            attacker: The attacking character
            target: The target character  
            attacker_entry: The attacker's combat entry
            combatants_list: List of all combat entries at time of scheduling
        """
        splattercast = ChannelDB.objects.get_channel(SPLATTERCAST_CHANNEL)
        
        # Validate that attacker still has weapons they're supposed to wield
        self._validate_and_clean_weapons(attacker)
        
        # Validate that combat is still active
        if not getattr(self.db, DB_COMBAT_RUNNING, False):
            splattercast.msg(f"DELAYED_ATTACK: Combat ended before {attacker.key}'s attack on {target.key} could execute.")
            return
            
        # Validate that both characters are still in combat
        current_combatants = getattr(self.db, DB_COMBATANTS, [])
        attacker_still_in_combat = any(e.get(DB_CHAR) == attacker for e in current_combatants)
        target_still_in_combat = any(e.get(DB_CHAR) == target for e in current_combatants)
        
        if not attacker_still_in_combat:
            splattercast.msg(f"DELAYED_ATTACK: {attacker.key} no longer in combat, attack cancelled.")
            return
            
        if not target_still_in_combat:
            splattercast.msg(f"DELAYED_ATTACK: {target.key} no longer in combat, {attacker.key}'s attack cancelled.")
            return
        
        # Check if attacker is dead - dead characters can't attack
        if attacker.is_dead():
            splattercast.msg(f"DELAYED_ATTACK: {attacker.key} has died, attack cancelled.")
            return
            
        # Check if target is dead - no point attacking the dead
        if target.is_dead():
            splattercast.msg(f"DELAYED_ATTACK: {target.key} has died, {attacker.key}'s attack cancelled.")
            return
        
        # Get fresh combat entries
        fresh_attacker_entry = next((e for e in current_combatants if e.get(DB_CHAR) == attacker), None)
        if not fresh_attacker_entry:
            splattercast.msg(f"DELAYED_ATTACK: Could not find fresh entry for {attacker.key}, attack cancelled.")
            return
        
        splattercast.msg(f"DELAYED_ATTACK: Executing {attacker.key} -> {target.key}")
        
        try:
            self._process_attack(attacker, target, fresh_attacker_entry, current_combatants)
            splattercast.msg(f"DELAYED_ATTACK: _process_attack completed for {attacker.key} -> {target.key}")
        except Exception as e:
            splattercast.msg(f"DELAYED_ATTACK: ERROR in _process_attack for {attacker.key} -> {target.key}: {e}")
            import traceback
            splattercast.msg(f"DELAYED_ATTACK: Traceback: {traceback.format_exc()}")

    def _send_combat_prompt(self, char):
        """
        Send a combat status prompt to a character showing vital information.
        
        Shows: Health status (blood level), bleeding, stamina %, and critically damaged organs.
        Only sent if char.db.combat_prompt is not False.
        
        Args:
            char: The character to send the prompt to
        """
        parts = []
        
        # --- HEALTH STATUS (Blood Level) ---
        blood_level = 100.0
        if hasattr(char, 'medical_state') and char.medical_state:
            blood_level = getattr(char.medical_state, 'blood_level', 100.0)
        
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
        if hasattr(char, 'medical_state') and char.medical_state:
            bleed_rate = char.medical_state.calculate_blood_loss_rate()
            is_bleeding = bleed_rate > 0
        
        if is_bleeding and bleed_rate > 0:
            if bleed_rate >= 3:
                parts.append("|R[BLEEDING HEAVILY]|n")
            elif bleed_rate >= 1.5:
                parts.append("|r[BLEEDING]|n")
            else:
                parts.append("|y[bleeding]|n")
        
        # --- STAMINA STATUS ---
        stamina = getattr(char.ndb, "stamina", None)
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
        # Check for extremely damaged organs (functionality < 25%)
        critical_organs = []
        if hasattr(char, 'medical_state') and char.medical_state:
            for organ_name, organ in char.medical_state.organs.items():
                if hasattr(organ, 'get_functionality_percentage'):
                    functionality = organ.get_functionality_percentage()
                    if functionality < 0.25 and organ.current_hp < organ.max_hp:
                        critical_organs.append(organ_name.replace('_', ' '))
        
        if critical_organs:
            organ_list = ", ".join(critical_organs)
            parts.append(f"|R[CRITICAL: {organ_list}]|n")
        
        # --- SEND THE PROMPT ---
        if parts:
            prompt = " | ".join(parts)
            char.msg(prompt)

    def _determine_injury_type(self, weapon):
        """
        Determine the injury type based on weapon's damage_type attribute.
        
        Args:
            weapon: The weapon object being used (or None for unarmed)
            
        Returns:
            str: Valid injury type for medical system
        """
        if not weapon:
            return "blunt"  # Unarmed attacks are blunt trauma
        
        # Get damage_type from weapon, default to "blunt" if not specified
        damage_type = getattr(weapon.db, 'damage_type', 'blunt')
        return damage_type

    def _process_attack(self, attacker, target, attacker_entry, combatants_list):
        """
        Process an attack between two characters.
        
        Args:
            attacker: The attacking character
            target: The target character
            attacker_entry: The attacker's combat entry
            combatants_list: List of all combat entries
        """
        import time
        
        splattercast = ChannelDB.objects.get_channel(SPLATTERCAST_CHANNEL)
        
        # --- STAMINA CHECK FOR ATTACK ---
        # Check if attacker has enough stamina to attack
        stamina = getattr(attacker.ndb, "stamina", None)
        if stamina:
            if stamina.stamina_current < STAMINA_MIN_TO_ATTACK:
                attacker.msg(STAMINA_EXHAUSTED_MSG)
                splattercast.msg(f"ATTACK_EXHAUSTED: {attacker.key} too tired to attack ({stamina.stamina_current:.1f} < {STAMINA_MIN_TO_ATTACK})")
                return
            # Drain stamina for attacking
            stamina.stamina_current = max(0, stamina.stamina_current - STAMINA_DRAIN_PER_ATTACK)
            splattercast.msg(f"STAMINA_DRAIN_ATTACK: {attacker.key} drained {STAMINA_DRAIN_PER_ATTACK} stamina, now at {stamina.stamina_current:.1f}")
        
        # Update last action time (combat is no longer idle)
        self.db.last_action_time = time.time()
        
        # Validate attacker's wielded weapons are still in inventory
        self._validate_and_clean_weapons(attacker)
        
        # Check if target is already dead or unconscious - prevents attacking incapacitated characters
        if target.is_dead():
            splattercast.msg(f"ATTACK_CANCELLED: {target.key} is already dead, cancelling {attacker.key}'s attack.")
            return
        elif hasattr(target, 'is_unconscious') and target.is_unconscious():
            splattercast.msg(f"ATTACK_CANCELLED: {target.key} is unconscious, cancelling {attacker.key}'s attack.")
            return
        
        # Check if attacker is wielding a ranged weapon
        is_ranged_attack = is_wielding_ranged_weapon(attacker)
        
        # Ammo check for ranged weapons
        if is_ranged_attack:
            weapon = get_wielded_weapon(attacker)
            if weapon and getattr(weapon.db, 'uses_ammo', False):
                current_ammo = getattr(weapon.db, 'current_ammo', 0) or 0
                ammo_capacity = getattr(weapon.db, 'ammo_capacity', DEFAULT_AMMO_CAPACITY)
                
                if current_ammo <= 0:
                    # Out of ammo - trigger automatic reload
                    attacker.msg(MSG_OUT_OF_AMMO.format(weapon=weapon.key))
                    
                    # Check if ammo is available
                    ammo_source = self._find_compatible_ammo(attacker, weapon)
                    if ammo_source:
                        # Queue reload action for next turn
                        attacker_entry["combat_action"] = COMBAT_ACTION_RELOAD
                        splattercast.msg(f"AUTO_RELOAD: {attacker.key} out of ammo, queuing reload for next turn.")
                    else:
                        attacker.msg(MSG_NO_AMMO_AVAILABLE.format(weapon=weapon.key))
                        splattercast.msg(f"NO_AMMO: {attacker.key} has no ammunition for {weapon.key}.")
                    return
                
                # Consume one round of ammo
                weapon.db.current_ammo = current_ammo - 1
                splattercast.msg(f"AMMO_CONSUMED: {attacker.key} fired {weapon.key} [{weapon.db.current_ammo}/{ammo_capacity}] remaining.")
        
        # For melee attacks, check same-room and proximity requirements
        if not is_ranged_attack:
            # Check if attacker can reach target (same room for melee)
            if attacker.location != target.location:
                attacker.msg(f"You can't reach {target.key} from here.")
                splattercast.msg(f"ATTACK_FAIL (REACH): {attacker.key} cannot reach {target.key}.")
                return
            
            # Check proximity for melee attacks
            if not hasattr(attacker.ndb, NDB_PROXIMITY):
                setattr(attacker.ndb, NDB_PROXIMITY, set())
            
            # Get proximity set - use proper attribute name
            proximity_set = getattr(attacker.ndb, NDB_PROXIMITY, set())
            if not proximity_set:  # Handle case where attribute exists but is None/empty
                setattr(attacker.ndb, NDB_PROXIMITY, set())
                proximity_set = set()
            
            if target not in proximity_set:
                attacker.msg(f"You need to be in melee proximity with {target.key} to attack them. Try advancing or charging.")
                splattercast.msg(f"ATTACK_FAIL (PROXIMITY): {attacker.key} not in proximity with {target.key}.")
                return
        else:
            # For ranged attacks, just log that we're allowing cross-room attack
            splattercast.msg(f"ATTACK_RANGED: {attacker.key} making ranged attack on {target.key} from {attacker.location.key} to {target.location.key}.")
        
        # Human Shield System Check
        # Check if target is grappling someone who could act as a human shield
        target_entry = None
        for entry in combatants_list:
            if entry.get(DB_CHAR) == target:
                target_entry = entry
                break
        
        original_target = target
        if target_entry:
            grappling_victim = get_combatant_grappling_target(target_entry, self)
            if grappling_victim:
                # Target is grappling someone - check for human shield interception
                shield_chance = self._calculate_shield_chance(target, grappling_victim, is_ranged_attack, combatants_list)
                shield_roll = randint(1, 100)
                
                splattercast.msg(f"HUMAN_SHIELD: {attacker.key} attacking {target.key} who is grappling {grappling_victim.key}. Shield chance: {shield_chance}%, roll: {shield_roll}")
                
                if shield_roll <= shield_chance:
                    # Shield successful - redirect attack to victim
                    self._send_shield_messages(attacker, target, grappling_victim)
                    target = grappling_victim  # Redirect the attack
                    splattercast.msg(f"HUMAN_SHIELD_SUCCESS: Attack redirected from {original_target.key} to {target.key}")
                else:
                    splattercast.msg(f"HUMAN_SHIELD_FAIL: Attack proceeds normally against {target.key}")
        
        # Get weapon and stats
        weapon = get_wielded_weapon(attacker)
        weapon_name = weapon.key if weapon else "unarmed"
        
        # Get weapon type for skill lookup
        weapon_type = "unarmed"
        if weapon and hasattr(weapon, 'db') and hasattr(weapon.db, 'weapon_type'):
            weapon_type = weapon.db.weapon_type
        
        # Get the skill associated with this weapon
        from world.combat.constants import get_weapon_skill, SKILL_BRAWLING
        weapon_skill_name = get_weapon_skill(weapon_type)
        
        # Get attacker's weapon skill level (stored as db attribute, 0-100 scale)
        # Convert skill name to db attribute format (e.g., "blades" -> character.db.blades)
        attacker_weapon_skill = getattr(attacker.db, weapon_skill_name, 0) or 0
        
        # Get target's dodge skill (0-100 scale)
        target_dodge_skill = getattr(target.db, "dodge", 0) or 0
        
        # Get base stats (REF for attack, REF for defense) - stats are 1-10, scaled to add to skill
        attacker_ref = get_numeric_stat(attacker, "ref", 1)
        target_ref = get_numeric_stat(target, "ref", 1)
        
        # NEW 0-100 SKILL SYSTEM with exponential scaling
        # Uses combat_roll() which applies exponential bonus from skills
        # Stats contribute: each point adds 5 effective skill points
        roll_result = combat_roll(
            attacker_skill=attacker_weapon_skill,
            defender_skill=target_dodge_skill,
            attacker_stat=attacker_ref,
            defender_stat=target_ref
        )
        attacker_roll = roll_result['attacker_roll']
        target_roll = roll_result['defender_roll']
        atk_dice, atk_bonus = roll_result['attacker_details']
        def_dice, def_bonus = roll_result['defender_details']
        
        # Check for charge bonus (flat +10 to roll in new system)
        has_attr = hasattr(attacker.ndb, "charge_attack_bonus_active")
        attr_value = getattr(attacker.ndb, "charge_attack_bonus_active", "MISSING")
        splattercast.msg(f"ATTACK_BONUS_DEBUG_DETAILED: {attacker.key} hasattr={has_attr}, value={attr_value}")
        
        if has_attr and getattr(attacker.ndb, "charge_attack_bonus_active", False):
            attacker_roll += 10  # Charge bonus scaled for 0-100 system
            splattercast.msg(f"ATTACK_BONUS: {attacker.key} gets +10 charge attack bonus.")
            splattercast.msg(f"ATTACK_BONUS_DEBUG: {attacker.key} had charge_attack_bonus_active set - this should only happen after using the 'charge' command.")
            # Ensure complete attribute removal - delattr might leave None in Evennia ndb
            try:
                delattr(attacker.ndb, "charge_attack_bonus_active")
            except AttributeError:
                pass
            # Double-check removal worked
            if hasattr(attacker.ndb, "charge_attack_bonus_active"):
                attacker.ndb.charge_attack_bonus_active = None
                delattr(attacker.ndb, "charge_attack_bonus_active")
        else:
            splattercast.msg(f"ATTACK_BONUS_DEBUG: {attacker.key} does not have charge_attack_bonus_active - no bonus applied.")
        
        splattercast.msg(f"ATTACK: {attacker.key} [{weapon_skill_name}:{attacker_weapon_skill}+REF*5:{attacker_ref*5}=d20:{atk_dice}+bonus:{atk_bonus}=roll {attacker_roll}] vs {target.key} [dodge:{target_dodge_skill}+REF*5:{target_ref*5}=d20:{def_dice}+bonus:{def_bonus}=roll {target_roll}] with {weapon_name}")
        
        if attacker_roll > target_roll:
            # Hit - calculate damage with skill scaling
            # Base damage scales with skill: higher skill = more consistent high damage
            base_damage = randint(1, 6)
            skill_damage_bonus = int(skill_to_bonus(attacker_weapon_skill) / 10)  # Up to +10 damage at skill 100
            damage = base_damage + skill_damage_bonus
            
            if weapon:
                # Add weapon damage if applicable
                weapon_damage = get_weapon_damage(weapon, 0)
                damage += weapon_damage
            
            # Determine injury type based on weapon
            injury_type = self._determine_injury_type(weapon)
            
            # Calculate success margin for precision targeting
            success_margin = attacker_roll - target_roll
            
            # Select hit location - Intellect characters target less armored areas
            hit_location = select_hit_location(target, success_margin, attacker)
            
            # Make precision roll for organ targeting within the location
            precision_roll = randint(1, 20)
            # Mix DEX (70%) and SMRT (30%) for precision skill
            attacker_dex = get_numeric_stat(attacker, "dex", 1)
            attacker_smrt = get_numeric_stat(attacker, "smrt", 1)
            precision_skill = int((attacker_dex * 0.7) + (attacker_smrt * 0.3))
            
            # Select specific target organ within the hit location
            target_organ = select_target_organ(hit_location, precision_roll, precision_skill)
            
            # Debug output for precision targeting
            splattercast.msg(f"PRECISION_TARGET: {attacker.key} margin={success_margin}, precision={precision_roll + precision_skill}, hit {hit_location}:{target_organ}")
            
            # weapon_type already determined above for skill lookup
            
            # Apply damage first to determine if this is a killing blow
            # take_damage now returns (died, actual_damage_applied)
            target_died, actual_damage = target.take_damage(damage, location=hit_location, injury_type=injury_type, target_organ=target_organ)
            
            if target_died:
                # This was a killing blow - send kill messages instead of regular attack messages
                kill_messages = get_combat_message(weapon_type, "kill", attacker=attacker, target=target, item=weapon, damage=actual_damage, hit_location=hit_location)
                
                # Send kill messages to establish lethal narrative before death curtain
                if "attacker_msg" in kill_messages:
                    attacker.msg(kill_messages["attacker_msg"])
                if "victim_msg" in kill_messages:
                    target.msg(kill_messages["victim_msg"])
                attacker.location.msg_contents(kill_messages["observer_msg"], exclude=[attacker, target])
                
                splattercast.msg(f"KILLING_BLOW: {attacker.key} delivered killing blow to {target.key} for {actual_damage} damage.")
                
                # Check if death has already been processed to prevent double death curtains
                if hasattr(target, 'ndb') and getattr(target.ndb, 'death_processed', False):
                    splattercast.msg(f"COMBAT_DEATH_SKIP: {target.key} death already processed")
                    
                    # Check if death curtain was deferred and trigger it now after kill message
                    if hasattr(target.ndb, 'death_curtain_pending') and target.ndb.death_curtain_pending:
                        from typeclasses.curtain_of_death import show_death_curtain
                        splattercast.msg(f"COMBAT_DEATH_CURTAIN: {target.key} triggering deferred death curtain after kill message")
                        show_death_curtain(target)
                        target.ndb.death_curtain_pending = False
                else:
                    # Trigger death processing - at_death() will handle death analysis and potentially defer curtain
                    target.at_death()
                    
                    # If death curtain was deferred, trigger it now after kill message
                    if hasattr(target.ndb, 'death_curtain_pending') and target.ndb.death_curtain_pending:
                        from typeclasses.curtain_of_death import show_death_curtain
                        splattercast.msg(f"COMBAT_DEATH_CURTAIN: {target.key} triggering deferred death curtain after kill message")
                        show_death_curtain(target)
                        target.ndb.death_curtain_pending = False
                
                # Remove from combat
                self.remove_combatant(target)
            else:
                # Regular hit - send attack messages
                hit_messages = get_combat_message(weapon_type, "hit", attacker=attacker, target=target, item=weapon, damage=actual_damage, hit_location=hit_location)
                
                # Send attack messages for non-fatal hits
                attacker.msg(hit_messages["attacker_msg"])
                target.msg(hit_messages["victim_msg"]) 
                attacker.location.msg_contents(hit_messages["observer_msg"], exclude=[attacker, target])
                
                splattercast.msg(f"ATTACK_HIT: {attacker.key} hit {target.key} for {actual_damage} damage.")
                
        else:
            # Miss - weapon_type already determined above
            miss_messages = get_combat_message(weapon_type, "miss", attacker=attacker, target=target, item=weapon)
            
            attacker.msg(miss_messages["attacker_msg"])
            target.msg(miss_messages["victim_msg"])
            attacker.location.msg_contents(miss_messages["observer_msg"], exclude=[attacker, target])
            
            splattercast.msg(f"ATTACK_MISS: {attacker.key} missed {target.key}.")
    
    def _calculate_shield_chance(self, grappler, victim, is_ranged_attack, combatants_list):
        """
        Calculate the chance that a grappled victim will act as a human shield.
        
        Args:
            grappler: The character doing the grappling
            victim: The character being grappled (potential shield)
            is_ranged_attack: Whether this is a ranged attack
            combatants_list: List of all combat entries
            
        Returns:
            int: Shield chance percentage (0-100)
        """
        # Base shield chance
        base_chance = 40
        
        # Grappler REF modifier: +5% per point above 1
        grappler_ref = getattr(grappler.db, "ref", 1) if hasattr(grappler, 'db') else 1
        grappler_ref = grappler_ref if isinstance(grappler_ref, (int, float)) else 1
        ref_bonus = (int(grappler_ref) - 1) * 5
        
        # Victim resistance modifier based on yielding state
        victim_entry = None
        for entry in combatants_list:
            if entry.get(DB_CHAR) == victim:
                victim_entry = entry
                break
        
        resistance_modifier = 0
        if victim_entry:
            is_yielding = victim_entry.get(DB_IS_YIELDING, False)
            if is_yielding:
                resistance_modifier = 10  # Easier to position yielding victim
            else:
                resistance_modifier = -10  # Struggling against positioning
        
        # Ranged attack modifier
        ranged_modifier = -20 if is_ranged_attack else 0
        
        # Calculate final chance
        final_chance = base_chance + ref_bonus + resistance_modifier + ranged_modifier
        
        # Clamp to 0-100 range
        return max(0, min(100, final_chance))
    
    def _send_shield_messages(self, attacker, grappler, victim):
        """
        Send human shield interception messages to all parties.
        
        Args:
            attacker: The character making the attack
            grappler: The character using victim as shield
            victim: The character being used as shield
        """
        # Message templates from the spec
        attacker_msg = f"|rYour attack is intercepted by {get_display_name_safe(victim)} as {get_display_name_safe(grappler)} uses them as a shield!|n"
        grappler_msg = f"|yYou position {get_display_name_safe(victim)} to absorb {get_display_name_safe(attacker)}'s attack!|n"
        victim_msg = f"|RYou are forced into the path of {get_display_name_safe(attacker)}'s attack by {get_display_name_safe(grappler)}!|n"
        observer_msg = f"|y{get_display_name_safe(grappler)} uses {get_display_name_safe(victim)} as a human shield against {get_display_name_safe(attacker)}'s attack!|n"
        
        # Send messages
        attacker.msg(attacker_msg)
        grappler.msg(grappler_msg)
        victim.msg(victim_msg)
        
        # Send to observers (exclude the three participants)
        attacker.location.msg_contents(observer_msg, exclude=[attacker, grappler, victim])


    
    def _resolve_grapple_initiate(self, char_entry, combatants_list):
        """Resolve a grapple initiate action."""
        resolve_grapple_initiate(char_entry, combatants_list, self)
    
    def _resolve_grapple_join(self, char_entry, combatants_list):
        """Resolve a grapple join action."""
        resolve_grapple_join(char_entry, combatants_list, self)
    
    def _resolve_grapple_takeover(self, char_entry, combatants_list):
        """Resolve a grapple takeover action."""
        resolve_grapple_takeover(char_entry, combatants_list, self)
    
    def _resolve_release_grapple(self, char_entry, combatants_list):
        """Resolve a release grapple action."""
        resolve_release_grapple(char_entry, combatants_list, self)
    
    def _resolve_choke(self, char_entry, combatants_list):
        """Resolve a choke action - drains target health based on attacker's BODY stat."""
        from evennia.comms.models import ChannelDB
        from .constants import SPLATTERCAST_CHANNEL, DB_CHAR, DB_GRAPPLING_DBREF
        from .utils import get_character_by_dbref, skill_roll
        
        splattercast = ChannelDB.objects.get_channel(SPLATTERCAST_CHANNEL)
        char = char_entry.get(DB_CHAR)
        
        # Find who they're choking
        grappling_dbref = char_entry.get(DB_GRAPPLING_DBREF)
        if not grappling_dbref:
            char.msg("You are not grappling anyone to choke.")
            return
        
        victim = get_character_by_dbref(grappling_dbref)
        if not victim:
            char.msg("Your grapple target no longer exists.")
            return
        
        # Calculate damage based on attacker's BODY stat (strength of grip)
        attacker_body = getattr(char.db, "body", 1) or 1
        
        # Base damage is 1 per BODY point, plus a small die roll
        base_damage = attacker_body
        damage_roll, dice, bonus = skill_roll(base_damage * 5)  # Scale up for consistency
        actual_damage = max(1, damage_roll // 5)  # Convert back to reasonable damage
        
        # Apply damage
        current_hp = getattr(victim.db, "hp", 100) or 100
        new_hp = max(0, current_hp - actual_damage)
        victim.db.hp = new_hp
        
        # Send messages
        char.msg(f"You choke {victim.key}, dealing {actual_damage} damage!")
        victim.msg(f"{char.key} chokes you, dealing {actual_damage} damage! (HP: {new_hp})")
        
        if char.location:
            char.location.msg_contents(
                f"{char.key} chokes {victim.key} for {actual_damage} damage!",
                exclude=[char, victim]
            )
        
        splattercast.msg(f"CHOKE: {char.key} choked {victim.key} for {actual_damage} damage (victim HP now: {new_hp})")
        
        # Check if victim died
        if new_hp <= 0:
            splattercast.msg(f"CHOKE_DEATH: {victim.key} was choked to death by {char.key}!")
            victim.msg(f"You fade away as {char.key}'s grip tightens...")
    
    def resolve_bonus_attack(self, attacker, target):
        """
        Resolve a bonus attack triggered by specific combat events.
        
        Args:
            attacker: The character making the bonus attack
            target: The target of the bonus attack
        """
        resolve_bonus_attack(self, attacker, target)

    def _resolve_retreat(self, char, entry):
        """Resolve a retreat action."""
        from random import randint
        from .utils import get_numeric_stat, initialize_proximity_ndb
        from .proximity import break_proximity, is_in_proximity, establish_proximity
        from .constants import SPLATTERCAST_CHANNEL, DEBUG_PREFIX_HANDLER, NDB_PROXIMITY_UNIVERSAL, DB_GRAPPLING_DBREF
        
        splattercast = ChannelDB.objects.get_channel(SPLATTERCAST_CHANNEL)
        
        splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_RETREAT: {char.key} executing retreat action.")
        
        # Check if in proximity with anyone (combat proximity)
        initialize_proximity_ndb(char)
        combat_proximity_list = getattr(char.ndb, "in_proximity_with", set())
        
        # Also check grenade proximity
        grenade_proximity_list = getattr(char.ndb, NDB_PROXIMITY_UNIVERSAL, [])
        if not isinstance(grenade_proximity_list, list):
            grenade_proximity_list = []
        
        # Combine both proximity systems to get all nearby entities
        all_proximity = set(combat_proximity_list) | set(grenade_proximity_list)
        all_proximity.discard(char)  # Remove self
        
        if not all_proximity:
            char.msg("|yYou are not in melee with anyone to retreat from.|n")
            return
        
        # Check if currently grappling someone
        grappled_victim = None
        grappled_victim_dbref = entry.get(DB_GRAPPLING_DBREF)
        if grappled_victim_dbref:
            grappled_victim = self._get_char_by_dbref(grappled_victim_dbref)
        
        # Get valid opponents (exclude grappled victim from dexterity contest)
        opponents = []
        for entity in all_proximity:
            if (entity != char and 
                entity.location == char.location and
                entity != grappled_victim):  # Exclude grappled victim from contest
                opponents.append(entity)
        
        # Special case: If only in proximity with grappled victim, retreat fails
        if grappled_victim and len(all_proximity) == 1 and grappled_victim in all_proximity:
            char.msg("|rYou cannot retreat while grappling your only opponent! You are physically latched together.|n")
            splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_RETREAT: {char.key} cannot retreat - only in proximity with grappled victim {grappled_victim.key}.")
            return
        
        # If no valid opponents for contest (shouldn't happen after above check, but safety)
        if not opponents:
            char.msg("|yYou are not in melee with anyone to retreat from.|n")
            return
        
        # Find the highest opponent athletics + REF for retreat difficulty (0-100 system)
        highest_opponent_skill = 0
        for opponent in opponents:
            opp_ref = getattr(opponent.db, "ref", 1) or 1
            opp_athletics = getattr(opponent.db, "athletics", 0) or 0
            # In new system: skill + (stat * 5)
            opp_total = opp_athletics + (opp_ref * 5)
            if opp_total > highest_opponent_skill:
                highest_opponent_skill = opp_total
        
        # Make opposed roll using new 0-100 skill system
        char_ref = getattr(char.db, "ref", 1) or 1
        char_athletics = getattr(char.db, "athletics", 0) or 0
        
        # Use skill_roll for each side
        char_total, char_dice, char_bonus = skill_roll(char_athletics + (char_ref * 5))
        opp_total, opp_dice, opp_bonus = skill_roll(highest_opponent_skill)
        
        splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_RETREAT: {char.key} [DEX*5:{char_dex*5}+REF*5:{char_ref*5}=d20:{char_dice}+bonus:{char_bonus}=roll {char_total}] vs highest opponent [total_skill:{highest_opponent_skill}=d20:{opp_dice}+bonus:{opp_bonus}=roll {opp_total}]")
        
        if char_total > opp_total:
            # Success - break proximity with opponents but maintain with grappled victim
            for opponent in opponents:
                if is_in_proximity(char, opponent):
                    break_proximity(char, opponent)
            
            # Always ensure proximity is maintained with grappled victim during retreat
            if grappled_victim:
                if not is_in_proximity(char, grappled_victim):
                    establish_proximity(char, grappled_victim)
                splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_RETREAT: Maintained proximity with grappled victim {grappled_victim.key} during retreat.")
            
            char.msg("|gYou successfully retreat from melee combat.|n")
            msg_contents_disguised(char.location, "|y{char_name} retreats from melee combat.|n", char, exclude=[char])
            splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_RETREAT: {char.key} successfully retreated from melee.")
        else:
            # Failure - remain in proximity
            char.msg("|rYour retreat fails! You remain locked in melee.|n")
            msg_contents_disguised(char.location, "|y{char_name} tries to retreat but remains engaged.|n", char, exclude=[char])
            splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_RETREAT: {char.key} failed to retreat from melee.")

    def _resolve_advance(self, char, entry):
        """Resolve an advance action."""
        from random import randint
        from .utils import get_numeric_stat, initialize_proximity_ndb
        from .proximity import establish_proximity, is_in_proximity
        from .constants import SPLATTERCAST_CHANNEL, DEBUG_PREFIX_HANDLER, DB_COMBATANTS, DB_IS_YIELDING
        
        splattercast = ChannelDB.objects.get_channel(SPLATTERCAST_CHANNEL)
        target = entry.get("combat_action_target")
        
        if not target:
            char.msg("|rNo target specified for advance action.|n")
            return
        
        # Check if target is still in combat
        combatants_list = getattr(self.db, DB_COMBATANTS, [])
        if not any(e[DB_CHAR] == target for e in combatants_list):
            char.msg(f"|r{target.key} is no longer in combat.|n")
            return
        
        splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_ADVANCE: {char.key} executing advance action on {target.key}.")
        
        # Check if target is in the same room
        if target.location == char.location:
            # Same room - try to establish proximity
            initialize_proximity_ndb(char)
            initialize_proximity_ndb(target)
            
            if is_in_proximity(char, target):
                char.msg(f"|yYou are already in melee proximity with {target.key}.|n")
                return
            
            # Make opposed roll for proximity using new 0-100 skill system
            char_ref = getattr(char.db, "ref", 1) or 1
            char_athletics = getattr(char.db, "athletics", 0) or 0
            target_ref = getattr(target.db, "ref", 1) or 1
            target_athletics = getattr(target.db, "athletics", 0) or 0
            
            advance_result = combat_roll(
                attacker_skill=char_athletics,
                defender_skill=target_athletics,
                attacker_stat=char_ref,
                defender_stat=target_ref
            )
            char_roll = advance_result['attacker_roll']
            target_roll = advance_result['defender_roll']
            char_dice, char_bonus = advance_result['attacker_details']
            tgt_dice, tgt_bonus = advance_result['defender_details']
            
            splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_ADVANCE: {char.key} [athletics:{char_athletics}+REF*5:{char_ref*5}=d20:{char_dice}+bonus:{char_bonus}=roll {char_roll}] vs {target.key} [athletics:{target_athletics}+REF*5:{target_ref*5}=d20:{tgt_dice}+bonus:{tgt_bonus}=roll {target_roll}]")
            
            if char_roll > target_roll:
                # Success - establish proximity
                establish_proximity(char, target)
                
                char.msg(f"You successfully advance to melee range with {get_display_name_safe(target, char)}.")
                target.msg(f"|y{get_display_name_safe(char, target)} advances to melee range with you.|n")
                msg_contents_disguised(char.location, "|y{char0_name} advances to melee range with {char1_name}.|n", [char, target], exclude=[char, target])
                splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_ADVANCE: {char.key} successfully advanced to melee with {target.key}.")
            else:
                # Failure - no proximity established
                char.msg(f"|rYour advance on {get_display_name_safe(target, char)} fails! They keep their distance.|n")
                target.msg(f"{get_display_name_safe(char, target)} tries to advance on you but you keep your distance.")
                msg_contents_disguised(char.location, "|y{char0_name} tries to advance on {char1_name} but fails to close the distance.|n", [char, target], exclude=[char, target])
                splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_ADVANCE: {char.key} failed to advance on {target.key}.")
        else:
            # Different room - check if it's a managed room and try to move there
            managed_rooms = getattr(self.db, DB_MANAGED_ROOMS, [])
            target_room = target.location
            
            if target_room not in managed_rooms:
                char.msg(f"|r{target.key} is no longer in a combat area you can reach.|n")
                return
            
            # Check if advancing character is grappling someone and should drag them
            grappled_victim = self.get_grappling_obj(entry)
            should_drag_victim = False
            
            if grappled_victim:
                # Check drag conditions: grappling someone, yielding, and not targeted by others (except victim and advance target)
                is_yielding = entry.get(DB_IS_YIELDING, False)
                
                # Check if targeted by others in the same room (excluding the victim and the advance target)
                is_targeted_by_others_not_victim = False
                for e in combatants_list:
                    other_char = e[DB_CHAR]
                    if (other_char != char and other_char != grappled_victim and other_char != target and
                        other_char.location == char.location):  # Only check same-room combatants
                        if self.get_target_obj(e) == char:
                            is_targeted_by_others_not_victim = True
                            break
                
                # Drag conditions: grappling someone, yielding, and not targeted by others (except victim and advance target)
                if is_yielding and not is_targeted_by_others_not_victim:
                    should_drag_victim = True
                    splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_ADVANCE_DRAG: {char.key} meets drag conditions - will attempt to drag {grappled_victim.key}.")
                else:
                    char.msg(f"|rYou cannot advance to another room while actively grappling {grappled_victim.key} - others are targeting you or you're being aggressive.|n")
                    splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_ADVANCE_DRAG_BLOCKED: {char.key} cannot drag {grappled_victim.key} - yielding:{is_yielding}, targeted_by_others:{is_targeted_by_others_not_victim}")
                    return
            
            # Try to move to the target's room
            # Find the exit from current room to target room
            exit_to_target = None
            for exit_obj in char.location.exits:
                if exit_obj.destination == target_room:
                    exit_to_target = exit_obj
                    break
            
            if not exit_to_target:
                char.msg(f"|rYou cannot find a way to {target.key}'s location.|n")
                return
            
            # Make opposed roll for movement using new 0-100 skill system
            char_ref = getattr(char.db, "ref", 1) or 1
            char_athletics = getattr(char.db, "athletics", 0) or 0
            target_ref = getattr(target.db, "ref", 1) or 1
            target_athletics = getattr(target.db, "athletics", 0) or 0
            
            advance_result = combat_roll(
                attacker_skill=char_athletics,
                defender_skill=target_athletics,
                attacker_stat=char_ref,
                defender_stat=target_ref
            )
            char_roll = advance_result['attacker_roll']
            target_roll = advance_result['defender_roll']
            char_dice, char_bonus = advance_result['attacker_details']
            tgt_dice, tgt_bonus = advance_result['defender_details']
            
            splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_ADVANCE_MOVE: {char.key} [athletics:{char_athletics}+REF*5:{char_ref*5}=d20:{char_dice}+bonus:{char_bonus}=roll {char_roll}] vs {target.key} [athletics:{target_athletics}+REF*5:{target_ref*5}=d20:{tgt_dice}+bonus:{tgt_bonus}=roll {target_roll}]")
            
            if char_roll > target_roll:
                # Success - move to target's room
                old_location = char.location
                
                # Clear aim states before moving (consistent with traversal)
                from .utils import clear_aim_state
                if hasattr(char, "clear_aim_state"):
                    char.clear_aim_state(reason_for_clearing="as you advance")
                else:
                    clear_aim_state(char)
                
                # Handle grapple victim dragging if needed
                if should_drag_victim and grappled_victim:
                    # Announce dragging
                    char.msg(f"You drag {get_display_name_safe(grappled_victim, char)} with you as you advance to {target_room.key}.")
                    grappled_victim.msg(f"|r{get_display_name_safe(char, grappled_victim)} drags you along as they advance to {target_room.key}!|n")
                    msg_contents_disguised(old_location, "|y{char0_name} drags {char1_name} along as they advance toward " + target_room.key + ".|n", [char, grappled_victim], exclude=[char, grappled_victim])
                    splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_ADVANCE_DRAG: {char.key} is dragging {grappled_victim.key} from {old_location.key} to {target_room.key}.")
                    
                    # Move both characters
                    char.move_to(target_room)
                    grappled_victim.move_to(target_room, quiet=True, move_hooks=False)
                    
                    # Re-establish proximity between grappler and victim after drag
                    from .proximity import establish_proximity
                    establish_proximity(char, grappled_victim)
                    splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_ADVANCE_DRAG: Re-established proximity between {char.key} and dragged victim {grappled_victim.key} in {target_room.key}.")
                    
                    # Announce arrival in new location
                    msg_contents_disguised(target_room, "|y{char0_name} arrives dragging {char1_name}.|n", [char, grappled_victim], exclude=[char, grappled_victim])
                else:
                    # Normal single character movement
                    char.move_to(target_room)
                
                # Check for rigged grenades after successful movement
                from commands.CmdThrow import check_rigged_grenade, check_auto_defuse
                check_rigged_grenade(char, exit_to_target)
                
                # Check for auto-defuse opportunities after advancing to new room
                check_auto_defuse(char)
                
                if should_drag_victim and grappled_victim:
                    char.msg(f"You successfully advance to {target_room.key} with {grappled_victim.key} in tow to engage {target.key}.")
                    target.msg(f"|y{char.key} advances into the room dragging {grappled_victim.key} to engage you!|n")
                    splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_ADVANCE_MOVE: {char.key} successfully moved to {target_room.key} with {grappled_victim.key} to engage {target.key}.")
                else:
                    char.msg(f"You successfully advance to {target_room.key} to engage {get_display_name_safe(target, char)}.")
                    target.msg(f"|y{get_display_name_safe(char, target)} advances into the room to engage you!|n")
                    msg_contents_disguised(old_location, "|y{char0_name} advances toward " + target_room.key + " to engage {char1_name}.|n", [char, target], exclude=[char])
                    msg_contents_disguised(target_room, "|y{char0_name} advances into the room to engage {char1_name}!|n", [char, target], exclude=[char, target])
                    splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_ADVANCE_MOVE: {char.key} successfully moved to {target_room.key} to engage {target.key}.")
            else:
                # Failure - no movement
                char.msg(f"|rYour advance toward {target.key} fails! You cannot reach their position.|n")
                target.msg(f"{char.key} tries to advance toward your position but fails to reach you.")
                msg_contents_disguised(char.location, "|y{char0_name} attempts to advance toward {char1_name} but fails to reach them.|n", [char, target], exclude=[char])
                splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_ADVANCE_MOVE: {char.key} failed to move to {target.key}.")
                
                # Check if target has ranged weapon for bonus attack
                if is_wielding_ranged_weapon(target):
                    target.msg(f"Your ranged weapon gives you a clear shot as {char.key} fails to reach you!")
                    char.msg(f"|r{target.key} takes advantage of your failed advance to attack from range!|n")
                    splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_ADVANCE_MOVE_BONUS: {target.key} gets bonus attack vs {char.key} for failed cross-room advance.")
                    self.resolve_bonus_attack(target, char)

    def _resolve_charge(self, char, entry, combatants_list):
        """Resolve a charge action."""
        from random import randint
        from .utils import get_numeric_stat, initialize_proximity_ndb, roll_with_disadvantage, standard_roll, clear_aim_state, is_wielding_ranged_weapon
        from .proximity import establish_proximity, is_in_proximity
        from .constants import SPLATTERCAST_CHANNEL, DEBUG_PREFIX_HANDLER
        
        splattercast = ChannelDB.objects.get_channel(SPLATTERCAST_CHANNEL)
        target = entry.get("combat_action_target")
        
        if not target:
            char.msg("|rNo target specified for charge action.|n")
            return
        
        # Validate target is still in combat
        if not any(e["char"] == target for e in combatants_list):
            char.msg(f"|r{target.key} is no longer in combat.|n")
            return
        
        splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_CHARGE: {char.key} executing charge action on {target.key}.")
        
        # Initialize proximity for both characters
        initialize_proximity_ndb(char)
        initialize_proximity_ndb(target)
        
        # Check if already in proximity
        if is_in_proximity(char, target):
            char.msg(f"|yYou are already in melee proximity with {target.key}.|n")
            # Clear the charge action since it's not needed
            combatants_list = list(self.db.combatants)
            for combat_entry in combatants_list:
                if combat_entry["char"] == char:
                    combat_entry["combat_action"] = None
                    combat_entry["combat_action_target"] = None
                    break
            self.db.combatants = combatants_list
            
            # Instead of waiting for normal attack phase, make an immediate bonus attack
            # This makes the charge feel more aggressive and responsive
            splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_CHARGE: {char.key} already in proximity with {target.key}, making immediate bonus attack.")
            self.resolve_bonus_attack(char, target)
            return
        
        # Handle same room vs different room charge
        if target.location == char.location:
            # Same room charge - use disadvantage on athletics with new 0-100 skill system
            char_ref = getattr(char.db, "ref", 1) or 1
            char_athletics = getattr(char.db, "athletics", 0) or 0
            target_ref = getattr(target.db, "ref", 1) or 1
            target_athletics = getattr(target.db, "athletics", 0) or 0
            
            # Roll with disadvantage: roll 2d20, take lowest, add exponential skill bonus
            # Charger's effective skill = athletics + ref*5
            from .utils import skill_to_bonus, skill_roll
            charger_effective_skill = char_athletics + (char_ref * 5)
            defender_effective_skill = target_athletics + (target_ref * 5)
            
            roll1 = randint(1, 20)
            roll2 = randint(1, 20)
            charger_dice = min(roll1, roll2)  # Disadvantage - take lowest
            charger_bonus = skill_to_bonus(charger_effective_skill)
            charge_roll = charger_dice + charger_bonus
            
            # Defender rolls normally
            defender_dice = randint(1, 20)
            defender_bonus = skill_to_bonus(defender_effective_skill)
            resist_roll = defender_dice + defender_bonus
            
            splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_CHARGE_SAME_ROOM: {char.key} [athletics:{char_athletics}+REF*5:{char_ref*5}, disadvantage:{roll1},{roll2}>>d20:{charger_dice}+bonus:{charger_bonus}=roll {charge_roll}] vs {target.key} [athletics:{target_athletics}+REF*5:{target_ref*5}=d20:{defender_dice}+bonus:{defender_bonus}=roll {resist_roll}]")
            
            if charge_roll > resist_roll:
                # Success - establish proximity and charge bonus
                
                # Check if charger is grappling someone and release them
                if entry.get(DB_GRAPPLING_DBREF):
                    grappled_victim = self.get_grappling_obj(entry)
                    
                    if grappled_victim:
                        # Release the grapple - update the actual combatants list
                        for combatant_entry in combatants_list:
                            if combatant_entry[DB_CHAR] == char:
                                combatant_entry[DB_GRAPPLING_DBREF] = None
                            elif combatant_entry[DB_CHAR] == grappled_victim:
                                combatant_entry[DB_GRAPPLED_BY_DBREF] = None
                        
                        # Announce grapple release
                        char.msg(f"|yYou release your grapple on {grappled_victim.get_display_name(char)} as you charge {target.key}!|n")
                        if grappled_victim.access(char, "view"):
                            grappled_victim.msg(f"|y{char.get_display_name(grappled_victim)} releases their grapple on you to charge {target.get_display_name(grappled_victim)}!|n")
                        
                        splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_CHARGE_GRAPPLE_RELEASE: {char.key} released grapple on {grappled_victim.key} due to successful charge.")
                
                establish_proximity(char, target)
                
                # Clear aim states
                clear_aim_state(char)
                
                # Update target on successful charge
                self.set_target(char, target)
                
                # Set charge bonus
                char.ndb.charge_attack_bonus_active = True
                splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_CHARGE: {char.key} charge_attack_bonus_active set to True by successful charge.")
                
                char.msg(f"You charge {get_display_name_safe(target, char)} and slam into melee range! Your next attack will have a bonus.")
                target.msg(f"|r{get_display_name_safe(char, target)} charges at you and crashes into melee range!|n")
                msg_contents_disguised(char.location, "|y{char0_name} charges at {char1_name} with reckless abandon!|n", [char, target], exclude=[char, target])
                splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_CHARGE: {char.key} successfully charged {target.key}.")
            else:
                # Failure - charge penalty
                char.msg(f"|rYour reckless charge at {get_display_name_safe(target, char)} fails spectacularly!|n")
                target.msg(f"|y{get_display_name_safe(char, target)} charges at you but you dodge, leaving them off-balance!|n")
                msg_contents_disguised(char.location, "|y{char0_name} charges recklessly at {char1_name} but misses and stumbles!|n", [char, target], exclude=[char, target])
                
                # Check if target has ranged weapon for bonus attack
                if is_wielding_ranged_weapon(target):
                    if hasattr(self, 'resolve_bonus_attack'):
                        self.resolve_bonus_attack(target, char)
                        splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_CHARGE: {char.key} failed charge against ranged weapon user {target.key}, bonus attack triggered.")
                
                # Apply charge failure penalty
                char.ndb.charge_penalty = True
                char.msg("|rYour failed charge leaves you off-balance!|n")
                splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_CHARGE: {char.key} failed charge on {target.key}, penalty applied.")
        else:
            # Different room charge - move to target's room
            managed_rooms = getattr(self.db, DB_MANAGED_ROOMS, [])
            if target.location not in managed_rooms:
                char.msg(f"|r{target.key} is not in a room you can charge to.|n")
                return
            
            # Check for valid path
            target_room = target.location
            exits_to_target = [ex for ex in char.location.exits if ex.destination == target_room]
            
            if not exits_to_target:
                char.msg(f"|rThere is no clear path to charge at {target.key}.|n")
                return
            
            # Check if target has ranged weapon
            target_has_ranged = is_wielding_ranged_weapon(target)
            
            # Charge uses disadvantage for cross-room with new 0-100 skill system
            char_ref = getattr(char.db, "ref", 1) or 1
            char_athletics = getattr(char.db, "athletics", 0) or 0
            target_ref = getattr(target.db, "ref", 1) or 1
            target_athletics = getattr(target.db, "athletics", 0) or 0
            
            # Roll with disadvantage: roll 2d20, take lowest, add exponential skill bonus
            from .utils import skill_to_bonus
            charger_effective_skill = char_athletics + (char_ref * 5)
            defender_effective_skill = target_athletics + (target_ref * 5)
            
            roll1 = randint(1, 20)
            roll2 = randint(1, 20)
            charger_dice = min(roll1, roll2)  # Disadvantage - take lowest
            charger_bonus = skill_to_bonus(charger_effective_skill)
            charge_roll = charger_dice + charger_bonus
            
            # Defender rolls normally
            defender_dice = randint(1, 20)
            defender_bonus = skill_to_bonus(defender_effective_skill)
            resist_roll = defender_dice + defender_bonus
            
            splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_CHARGE_CROSS_ROOM: {char.key} [athletics:{char_athletics}+REF*5:{char_ref*5}, disadvantage:{roll1},{roll2}>>d20:{charger_dice}+bonus:{charger_bonus}=roll {charge_roll}] vs {target.key} [athletics:{target_athletics}+REF*5:{target_ref*5}=d20:{defender_dice}+bonus:{defender_bonus}=roll {resist_roll}]")
            
            if charge_roll > resist_roll:
                # Success - move and establish proximity
                exit_to_use = exits_to_target[0]
                char.move_to(target_room)
                
                # Check if charger is grappling someone and release them
                if entry.get(DB_GRAPPLING_DBREF):
                    grappled_victim = self.get_grappling_obj(entry)
                    
                    if grappled_victim:
                        # Release the grapple - update the actual combatants list
                        for combatant_entry in combatants_list:
                            if combatant_entry[DB_CHAR] == char:
                                combatant_entry[DB_GRAPPLING_DBREF] = None
                            elif combatant_entry[DB_CHAR] == grappled_victim:
                                combatant_entry[DB_GRAPPLED_BY_DBREF] = None
                        
                        # Announce grapple release (victim might be in different room now)
                        char.msg(f"|yYou release your grapple on {grappled_victim.get_display_name(char)} as you charge away!|n")
                        if grappled_victim.access(char, "view"):
                            grappled_victim.msg(f"|y{char.get_display_name(grappled_victim)} releases their grapple on you and charges away!|n")
                        
                        splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_CHARGE_GRAPPLE_RELEASE: {char.key} released grapple on {grappled_victim.key} due to successful cross-room charge.")
                
                # Check for rigged grenades after successful movement
                from commands.CmdThrow import check_rigged_grenade, check_auto_defuse
                check_rigged_grenade(char, exit_to_use)
                
                # Check for auto-defuse opportunities after charging to new room
                check_auto_defuse(char)
                
                clear_aim_state(char)
                establish_proximity(char, target)
                
                # Update target on successful charge
                self.set_target(char, target)
                
                # Set charge bonus
                char.ndb.charge_attack_bonus_active = True
                splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_CHARGE: {char.key} charge_attack_bonus_active set to True by successful cross-room charge.")
                
                char.msg(f"You charge recklessly through the {exit_to_use.key} and crash into melee with {get_display_name_safe(target, char)}! Your next attack will have a bonus.")
                target.msg(f"|r{get_display_name_safe(char, target)} charges recklessly through the {exit_to_use.key} and crashes into melee with you!|n")
                msg_contents_disguised(char.location, "|y{char0_name} charges recklessly from " + (exit_to_use.get_return_exit().key if exit_to_use.get_return_exit() else "elsewhere") + " and crashes into melee!|n", [char, target], exclude=[char, target])
                splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_CHARGE: {char.key} successfully charged cross-room and engaged {target.key} in melee.")
            else:
                # Failure - charge penalty and potential ranged attack
                clear_aim_state(char)
                
                if target_has_ranged:
                    char.msg(f"|r{target.key} stops your reckless charge with covering fire!|n")
                    target.msg(f"You stop {char.key}'s reckless charge with your ranged weapon!")
                    
                    # Trigger bonus attack if available
                    if hasattr(self, 'resolve_bonus_attack'):
                        self.resolve_bonus_attack(target, char)
                        splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_CHARGE: {char.key} failed cross-room charge against ranged weapon user {target.key}, bonus attack triggered.")
                else:
                    char.msg(f"|rYour reckless charge at {target.key} fails as you stumble at the entrance!|n")
                    target.msg(f"|y{char.key} attempts to charge at you but stumbles at the entrance!|n")
                    splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_CHARGE: {char.key} failed cross-room charge on {target.key}.")
                
                # Apply charge failure penalty
                char.ndb.charge_penalty = True
                char.msg("|rYour failed charge leaves you off-balance!|n")

    def _resolve_disarm(self, char, entry):
        """Resolve a disarm action."""
        from random import randint
        from .utils import get_numeric_stat, initialize_proximity_ndb, roll_stat, log_combat_action
        from .proximity import is_in_proximity
        from .constants import (
            SPLATTERCAST_CHANNEL, DEBUG_PREFIX_HANDLER, MSG_DISARM_FAILED, MSG_DISARM_RESISTED,
            MSG_DISARM_TARGET_EMPTY_HANDS, MSG_DISARM_NOTHING_TO_DISARM, MSG_DISARM_SUCCESS_ATTACKER,
            MSG_DISARM_SUCCESS_VICTIM, MSG_DISARM_SUCCESS_OBSERVER
        )
        
        splattercast = ChannelDB.objects.get_channel(SPLATTERCAST_CHANNEL)
        target = entry.get("combat_action_target")
        
        if not target:
            char.msg("|rNo target specified for disarm action.|n")
            return
        
        # Validate target is still in combat and same room
        if target.location != char.location:
            char.msg(f"|r{target.key} is no longer in the same room.|n")
            return
        
        combatants_list = getattr(self.db, "combatants", [])
        if not any(e["char"] == target for e in combatants_list):
            char.msg(f"|r{target.key} is no longer in combat.|n")
            return
        
        splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_DISARM: {char.key} executing disarm action on {target.key}.")
        
        # Check proximity
        initialize_proximity_ndb(char)
        if not is_in_proximity(char, target):
            char.msg(f"|rYou must be in melee proximity with {target.key} to disarm them.|n")
            return
        
        # Check target's hands
        hands = getattr(target, "hands", {})
        if not hands:
            char.msg(MSG_DISARM_TARGET_EMPTY_HANDS.format(target=target.key))
            log_combat_action(char, "disarm_fail", target, details="target has nothing in their hands")
            return
        
        # Find weapon to disarm (prioritize weapons, then any held item)
        weapon_hand = None
        for hand, item in hands.items():
            if item and hasattr(item.db, "weapon_type") and item.db.weapon_type:
                weapon_hand = hand
                break
        
        if not weapon_hand:
            for hand, item in hands.items():
                if item:
                    weapon_hand = hand
                    break
        
        if not weapon_hand:
            char.msg(MSG_DISARM_NOTHING_TO_DISARM.format(target=target.key))
            log_combat_action(char, "disarm_fail", target, details="nothing found to disarm")
            return
        
        # Grit vs Grit opposed roll
        disarm_roll = roll_stat(char, "grit")
        resist_roll = roll_stat(target, "grit")
        
        splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_DISARM: {char.key} (grit roll:{disarm_roll}) vs {target.key} (grit roll:{resist_roll})")
        log_combat_action(char, "disarm_attempt", target, details=f"rolls {disarm_roll} (grit) vs {resist_roll} (grit)")
        
        if disarm_roll <= resist_roll:
            char.msg(MSG_DISARM_FAILED.format(target=target.key))
            target.msg(MSG_DISARM_RESISTED.format(attacker=char.key))
            log_combat_action(char, "disarm_fail", target, success=False)
            splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_DISARM: {char.key} failed to disarm {target.key}.")
            return
        
        # Success - disarm the item
        item = hands[weapon_hand]
        hands[weapon_hand] = None
        item.move_to(target.location, quiet=True)
        
        char.msg(MSG_DISARM_SUCCESS_ATTACKER.format(target=target.key, item=item.key))
        target.msg(MSG_DISARM_SUCCESS_VICTIM.format(attacker=char.key, item=item.key))
        target.location.msg_contents(
            MSG_DISARM_SUCCESS_OBSERVER.format(attacker=char.key, target=target.key, item=item.key),
            exclude=[char, target]
        )
        log_combat_action(char, "disarm_success", target, details=f"disarmed {item.key}")
        splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_DISARM: {char.key} successfully disarmed {item.key} from {target.key}.")

    def _find_compatible_ammo(self, char, weapon):
        """
        Find compatible ammunition in character's inventory.
        
        Args:
            char: Character to search inventory of
            weapon: Weapon to find ammo for
            
        Returns:
            Ammunition object if found, None otherwise
        """
        if not weapon or not getattr(weapon.db, 'uses_ammo', False):
            return None
        
        weapon_ammo_type = getattr(weapon.db, 'ammo_type', None)
        if not weapon_ammo_type:
            return None
        
        # Search character's inventory for compatible ammo
        for item in char.contents:
            # Check if it's an ammunition item
            if hasattr(item, 'is_compatible_with') and callable(item.is_compatible_with):
                if item.is_compatible_with(weapon):
                    # Make sure it has rounds available
                    current_rounds = getattr(item.db, 'current_rounds', 0) or 0
                    if current_rounds > 0:
                        return item
            # Also check for loose ammo with matching type (using compatibility check)
            elif hasattr(item.db, 'ammo_type') and is_ammo_compatible(item.db.ammo_type, weapon_ammo_type):
                current_rounds = getattr(item.db, 'current_rounds', 0) or 0
                if current_rounds > 0:
                    return item
        
        return None
    
    def _reload_weapon(self, char, weapon, ammo_source=None):
        """
        Reload a weapon from an ammunition source.
        
        Args:
            char: Character doing the reload
            weapon: Weapon to reload
            ammo_source: Optional specific ammo to use, or find automatically
            
        Returns:
            tuple: (success, rounds_loaded, message)
        """
        splattercast = ChannelDB.objects.get_channel(SPLATTERCAST_CHANNEL)
        
        if not weapon:
            return (False, 0, "No weapon to reload.")
        
        uses_ammo = getattr(weapon.db, 'uses_ammo', False)
        if not uses_ammo:
            return (False, 0, f"{weapon.key} doesn't use ammunition.")
        
        ammo_capacity = getattr(weapon.db, 'ammo_capacity', DEFAULT_AMMO_CAPACITY)
        current_ammo = getattr(weapon.db, 'current_ammo', 0) or 0
        
        # Check if weapon is already full
        if current_ammo >= ammo_capacity:
            return (False, 0, f"{weapon.key} is already fully loaded.")
        
        # Find ammo source if not provided
        if not ammo_source:
            ammo_source = self._find_compatible_ammo(char, weapon)
        
        if not ammo_source:
            return (False, 0, MSG_NO_AMMO_AVAILABLE.format(weapon=weapon.key))
        
        # Calculate how many rounds to transfer
        rounds_needed = ammo_capacity - current_ammo
        source_rounds = getattr(ammo_source.db, 'current_rounds', 0) or 0
        rounds_to_load = min(rounds_needed, source_rounds)
        
        if rounds_to_load <= 0:
            return (False, 0, f"No rounds available in {ammo_source.key}.")
        
        # Transfer rounds
        weapon.db.current_ammo = current_ammo + rounds_to_load
        ammo_source.db.current_rounds = source_rounds - rounds_to_load
        
        # Delete empty ammo container
        if ammo_source.db.current_rounds <= 0:
            container_type = getattr(ammo_source.db, 'container_type', 'magazine')
            ammo_source.delete()
            splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_RELOAD: Empty {container_type} deleted after reload.")
        
        splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_RELOAD: {char.key} loaded {rounds_to_load} rounds into {weapon.key} ({weapon.db.current_ammo}/{ammo_capacity}).")
        
        return (True, rounds_to_load, MSG_RELOADED.format(weapon=weapon.key))
    
    def _resolve_reload(self, char, entry):
        """
        Resolve a reload action during combat.
        Takes a full combat turn.
        
        Args:
            char: Character performing the reload
            entry: Character's combat entry
        """
        from .utils import log_combat_action
        splattercast = ChannelDB.objects.get_channel(SPLATTERCAST_CHANNEL)
        
        splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_RELOAD: {char.key} executing reload action.")
        
        # Get wielded weapon
        weapon = get_wielded_weapon(char)
        
        if not weapon:
            char.msg("|rYou aren't holding a weapon to reload.|n")
            splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_RELOAD: {char.key} has no weapon to reload.")
            return
        
        uses_ammo = getattr(weapon.db, 'uses_ammo', False)
        if not uses_ammo:
            char.msg(f"|r{weapon.key} doesn't use ammunition.|n")
            splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_RELOAD: {weapon.key} doesn't use ammo.")
            return
        
        # Check if already full
        ammo_capacity = getattr(weapon.db, 'ammo_capacity', DEFAULT_AMMO_CAPACITY)
        current_ammo = getattr(weapon.db, 'current_ammo', 0) or 0
        
        if current_ammo >= ammo_capacity:
            char.msg(f"|y{weapon.key} is already fully loaded [{current_ammo}/{ammo_capacity}].|n")
            splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_RELOAD: {weapon.key} already full.")
            return
        
        # Attempt reload
        success, rounds_loaded, message = self._reload_weapon(char, weapon)
        
        if success:
            # Announce reload to room
            new_ammo = getattr(weapon.db, 'current_ammo', 0)
            char.msg(message)
            char.location.msg_contents(
                MSG_RELOADING.format(name=char.key, weapon=weapon.key),
                exclude=[char]
            )
            log_combat_action(char, "reload_success", details=f"loaded {rounds_loaded} into {weapon.key} ({new_ammo}/{ammo_capacity})")
            splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_RELOAD_SUCCESS: {char.key} reloaded {weapon.key}.")
        else:
            char.msg(message)
            log_combat_action(char, "reload_fail", details=message)
            splattercast.msg(f"{DEBUG_PREFIX_HANDLER}_RELOAD_FAIL: {char.key} failed to reload: {message}")
