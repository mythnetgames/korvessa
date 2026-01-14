"""
Auto-Walk Script

Handles step-by-step automatic movement for player characters.
Respects stamina, combat state, and allows interruption.
"""

from evennia.scripts.scripts import DefaultScript
from evennia.utils import delay


# Movement mode configurations: (stamina_cost_per_step, delay_between_steps)
MOVEMENT_MODES = {
    "walk": (0.5, 2.0),      # Slow but efficient
    "jog": (2.0, 1.0),       # Moderate speed and cost
    "run": (4.0, 0.5),       # Fast but tiring
    "sprint": (8.0, 0.25),   # Very fast, very tiring
}

DEFAULT_MODE = "walk"

# Minimum stamina required to continue walking
MIN_STAMINA_THRESHOLD = 5.0


def get_or_create_channel(channel_name):
    """Get or create a debug channel."""
    try:
        from evennia.comms.models import ChannelDB
        return ChannelDB.objects.get_channel(channel_name)
    except Exception:
        return None


def _execute_auto_walk_step(character):
    """
    Standalone function to execute one auto-walk step.
    Called by delay() to move a character one step along their path.
    
    This is a module-level function because it needs to be called
    by the delay() system without relying on script methods.
    """
    pathing_channel = get_or_create_channel("Pathing")
    
    if not character:
        if pathing_channel:
            pathing_channel.msg("STEP_ERROR: Character object is None")
        return
    
    if pathing_channel:
        pathing_channel.msg(f"STEP: {character.key} taking step")
    
    # Check if auto-walk was cancelled
    if getattr(character.ndb, 'auto_walk_cancelled', False):
        if pathing_channel:
            pathing_channel.msg(f"STEP_CANCELLED: {character.key} - cancelled flag set")
        return
    
    # Check interruption conditions
    interrupt_reason = _check_auto_walk_interrupts(character)
    if interrupt_reason:
        if pathing_channel:
            pathing_channel.msg(f"STEP_INTERRUPT: {character.key} - {interrupt_reason}")
        character.msg(f"|rAuto-walk stopped:|n {interrupt_reason}")
        _cleanup_auto_walk(character)
        return
    
    # Get current path
    path = getattr(character.ndb, 'auto_walk_path', [])
    if pathing_channel:
        pathing_channel.msg(f"STEP_PATH: {character.key} - {len(path)} steps remaining")
    
    if not path:
        character.msg(f"|gArrived at destination.|n")
        if pathing_channel:
            pathing_channel.msg(f"STEP_COMPLETE: {character.key} arrived at destination")
        _cleanup_auto_walk(character)
        return
    
    # Get next step
    exit_obj, dest_room = path[0]
    
    if pathing_channel:
        pathing_channel.msg(f"STEP_NEXT: {character.key} - exit={exit_obj.key if exit_obj else 'None'}, dest={dest_room.dbref if dest_room else 'None'}")
    
    # Check exit still exists and is passable
    from world.pathfinding import is_exit_passable_for_player
    if not exit_obj or not hasattr(exit_obj, 'destination'):
        if pathing_channel:
            pathing_channel.msg(f"STEP_ERROR: {character.key} - exit missing or invalid")
        character.msg("|rAuto-walk stopped:|n Path no longer valid (exit missing).")
        _cleanup_auto_walk(character)
        return
    
    if not is_exit_passable_for_player(exit_obj, character):
        if pathing_channel:
            pathing_channel.msg(f"STEP_ERROR: {character.key} - exit not passable ({exit_obj.key})")
        character.msg(f"|rAuto-walk stopped:|n Cannot pass through {exit_obj.key} (blocked or locked).")
        _cleanup_auto_walk(character)
        return
    
    # Check stamina
    mode = getattr(character.ndb, 'auto_walk_mode', DEFAULT_MODE)
    stamina_cost, step_delay = MOVEMENT_MODES.get(mode, MOVEMENT_MODES[DEFAULT_MODE])
    stamina = getattr(character.ndb, 'stamina', None)
    
    if pathing_channel:
        current_stamina = stamina.stamina_current if stamina else 0
        pathing_channel.msg(f"STEP_STAMINA: {character.key} - mode={mode}, current={current_stamina}, cost={stamina_cost}, delay={step_delay}")
    
    if stamina:
        if stamina.stamina_current < stamina_cost:
            if pathing_channel:
                pathing_channel.msg(f"STEP_ERROR: {character.key} - insufficient stamina")
            character.msg(f"|rAuto-walk stopped:|n Too exhausted to continue. Rest to recover stamina.")
            _cleanup_auto_walk(character)
            return
        
        if stamina.stamina_current < MIN_STAMINA_THRESHOLD:
            if pathing_channel:
                pathing_channel.msg(f"STEP_ERROR: {character.key} - stamina critically low")
            character.msg(f"|rAuto-walk stopped:|n Stamina critically low. Rest to recover.")
            _cleanup_auto_walk(character)
            return
        
        # Drain stamina
        stamina.stamina_current = max(0, stamina.stamina_current - stamina_cost)
        if pathing_channel:
            pathing_channel.msg(f"STEP_DRAIN: {character.key} - stamina now {stamina.stamina_current} (drained {stamina_cost})")
    
    # Execute movement
    original_location = character.location
    direction = exit_obj.key
    
    if pathing_channel:
        pathing_channel.msg(f"STEP_MOVE: {character.key} moving {direction} from {original_location.dbref if original_location else 'None'} to {dest_room.dbref if dest_room else 'None'}")
    
    try:
        # Set flag to indicate this is an auto-walk move (not manual)
        character.ndb._is_auto_walk_move = True
        
        # Use move_to for proper movement with all hooks
        result = character.move_to(dest_room, quiet=False)
        
        # Clear the auto-walk move flag
        if hasattr(character.ndb, '_is_auto_walk_move'):
            del character.ndb._is_auto_walk_move
        
        if pathing_channel:
            pathing_channel.msg(f"STEP_MOVE_RESULT: {character.key} - result={result}, new_location={character.location.dbref if character.location else 'None'}")
        
        if result and character.location != original_location:
            # Success - remove this step from path
            character.ndb.auto_walk_path = path[1:]
            
            if pathing_channel:
                pathing_channel.msg(f"STEP_SUCCESS: {character.key} - {len(character.ndb.auto_walk_path)} steps remaining")
            
            # Check if more steps remain
            remaining = len(character.ndb.auto_walk_path)
            if remaining > 0:
                # Schedule next step
                if pathing_channel:
                    pathing_channel.msg(f"STEP_SCHEDULE: {character.key} - next step in {step_delay}s")
                delay(step_delay, _execute_auto_walk_step, character)
            else:
                # Arrived!
                dest_alias = getattr(character.ndb, 'auto_walk_destination', 'destination')
                character.msg(f"|gArrived at {dest_alias}.|n")
                if pathing_channel:
                    pathing_channel.msg(f"STEP_ARRIVED: {character.key} at destination")
                _cleanup_auto_walk(character)
        else:
            # Movement failed
            if pathing_channel:
                pathing_channel.msg(f"STEP_FAIL: {character.key} - movement returned {result}")
            character.msg(f"|rAuto-walk stopped:|n Could not move {direction}.")
            _cleanup_auto_walk(character)
            
    except Exception as e:
        if pathing_channel:
            pathing_channel.msg(f"STEP_ERROR: {character.key} - movement exception: {e}")
        character.msg(f"|rAuto-walk stopped:|n Movement error: {e}")
        _cleanup_auto_walk(character)


def _check_auto_walk_interrupts(character):
    """
    Check for conditions that should interrupt auto-walk.
    
    Returns:
        str: Reason for interruption, or None if no interruption
    """
    if not character:
        return "Character no longer exists"
    
    # Check if manually cancelled
    if getattr(character.ndb, 'auto_walk_cancelled', False):
        return "Cancelled by player"
    
    # Check combat state
    if hasattr(character.ndb, 'combat_handler'):
        handler = character.ndb.combat_handler
        if handler and getattr(handler, 'is_active', False):
            return "Entered combat"
    
    # Check if character is dead or unconscious
    if hasattr(character, 'is_dead') and character.is_dead():
        return "Character is dead"
    
    if hasattr(character, 'is_unconscious') and character.is_unconscious():
        return "Character is unconscious"
    
    # Check if location is None
    if not character.location:
        return "Character has no location"
    
    return None


def _cleanup_auto_walk(character):
    """Clean up all auto-walk state for a character."""
    pathing_channel = get_or_create_channel("Pathing")
    
    if pathing_channel:
        pathing_channel.msg(f"CLEANUP: {character.key} - clearing auto-walk state")
    
    # Clear NDB attributes
    for attr in ['auto_walk_path', 'auto_walk_mode', 'auto_walk_destination', 'auto_walk_cancelled']:
        if hasattr(character.ndb, attr):
            delattr(character.ndb, attr)



    """
    Script that manages automatic walking for a player character.
    
    Attached to the character, it processes one step at a time,
    checking for interruptions between each step.
    """
    
    def at_script_creation(self):
        """Initialize the auto-walk script."""
        self.key = "auto_walk_script"
        self.desc = "Handles automatic pathing for player"
        self.persistent = False  # Don't persist across restarts
        
        # Script does not repeat on its own - we use delay() for variable timing
        self.interval = 0
        self.repeats = 0
        
        pathing_channel = get_or_create_channel("Pathing")
        if pathing_channel:
            pathing_channel.msg(f"CREATION: AutoWalkScript created")
    
    def at_start(self):
        """Called when script starts."""
        # Initialize path data from character
        char = self.obj
        if not char:
            self.stop()
            return
        
        pathing_channel = get_or_create_channel("Pathing")
        
        # Get path data from character NDB
        self.path = getattr(char.ndb, 'auto_walk_path', [])
        self.mode = getattr(char.ndb, 'auto_walk_mode', DEFAULT_MODE)
        self.destination_alias = getattr(char.ndb, 'auto_walk_destination', 'destination')
        
        char.msg("|y[AUTOWALK DEBUG] at_start() called|n")
        if pathing_channel:
            pathing_channel.msg(f"START: {char.key} starting auto-walk to {self.destination_alias} (mode: {self.mode}, path length: {len(self.path)})")
        
        if not self.path:
            char.msg("|r[AUTOWALK DEBUG] at_start() - empty path!|n")
            char.msg("|yNo path to follow.|n")
            if pathing_channel:
                pathing_channel.msg(f"START_ERROR: {char.key} - empty path")
            self.stop()
            return
        
        # Get mode configuration
        stamina_cost, step_delay = MOVEMENT_MODES.get(self.mode, MOVEMENT_MODES[DEFAULT_MODE])
        
        char.msg(f"|gAuto-walk started.|n Mode: |w{self.mode}|n, {len(self.path)} steps to {self.destination_alias}.")
        char.msg("|yType any movement command or |wpath stop|y to cancel.|n")
        char.msg(f"|y[AUTOWALK DEBUG] Scheduling first step in 0.5s|n")
        
        if pathing_channel:
            pathing_channel.msg(f"START_INFO: {char.key} mode={self.mode}, stamina_cost={stamina_cost}, step_delay={step_delay}")
        
        # Schedule first step
        delay(0.5, self._take_step)
    
    def _take_step(self):
        """Take one step along the path."""
        char = self.obj
        pathing_channel = get_or_create_channel("Pathing")
        
        if not char:
            if pathing_channel:
                pathing_channel.msg("STEP_ERROR: Character object is None")
            self.stop()
            return
        
        if pathing_channel:
            pathing_channel.msg(f"STEP: {char.key} taking step")
        
        # Check if script was cancelled
        if not self.is_active:
            if pathing_channel:
                pathing_channel.msg(f"STEP_ERROR: {char.key} - script not active")
            return
        
        # Check interruption conditions
        interrupt_reason = self._check_interrupts()
        if interrupt_reason:
            if pathing_channel:
                pathing_channel.msg(f"STEP_INTERRUPT: {char.key} - {interrupt_reason}")
            char.msg(f"|rAuto-walk stopped:|n {interrupt_reason}")
            self._cleanup()
            return
        
        # Get current path
        path = getattr(char.ndb, 'auto_walk_path', [])
        if pathing_channel:
            pathing_channel.msg(f"STEP_PATH: {char.key} - {len(path)} steps remaining")
        
        if not path:
            char.msg(f"|gArrived at {self.destination_alias}.|n")
            if pathing_channel:
                pathing_channel.msg(f"STEP_COMPLETE: {char.key} arrived at destination")
            self._cleanup()
            return
        
        # Get next step
        exit_obj, dest_room = path[0]
        
        if pathing_channel:
            pathing_channel.msg(f"STEP_NEXT: {char.key} - exit={exit_obj.key if exit_obj else 'None'}, dest={dest_room.dbref if dest_room else 'None'}")
        
        # Check exit still exists and is passable
        from world.pathfinding import is_exit_passable_for_player
        if not exit_obj or not hasattr(exit_obj, 'destination'):
            if pathing_channel:
                pathing_channel.msg(f"STEP_ERROR: {char.key} - exit missing or invalid")
            char.msg("|rAuto-walk stopped:|n Path no longer valid (exit missing).")
            self._cleanup()
            return
        
        if not is_exit_passable_for_player(exit_obj, char):
            if pathing_channel:
                pathing_channel.msg(f"STEP_ERROR: {char.key} - exit not passable ({exit_obj.key})")
            char.msg(f"|rAuto-walk stopped:|n Cannot pass through {exit_obj.key} (blocked or locked).")
            self._cleanup()
            return
        
        # Check stamina
        stamina_cost, step_delay = MOVEMENT_MODES.get(self.mode, MOVEMENT_MODES[DEFAULT_MODE])
        stamina = getattr(char.ndb, 'stamina', None)
        
        if pathing_channel:
            current_stamina = stamina.stamina_current if stamina else 0
            pathing_channel.msg(f"STEP_STAMINA: {char.key} - current={current_stamina}, cost={stamina_cost}")
        
        if stamina:
            if stamina.stamina_current < stamina_cost:
                if pathing_channel:
                    pathing_channel.msg(f"STEP_ERROR: {char.key} - insufficient stamina")
                char.msg(f"|rAuto-walk stopped:|n Too exhausted to continue. Rest to recover stamina.")
                self._cleanup()
                return
            
            if stamina.stamina_current < MIN_STAMINA_THRESHOLD:
                if pathing_channel:
                    pathing_channel.msg(f"STEP_ERROR: {char.key} - stamina critically low")
                char.msg(f"|rAuto-walk stopped:|n Stamina critically low. Rest to recover.")
                self._cleanup()
                return
            
            # Drain stamina
            stamina.stamina_current = max(0, stamina.stamina_current - stamina_cost)
            if pathing_channel:
                pathing_channel.msg(f"STEP_DRAIN: {char.key} - stamina now {stamina.stamina_current}")
        
        # Execute movement
        original_location = char.location
        direction = exit_obj.key
        
        if pathing_channel:
            pathing_channel.msg(f"STEP_MOVE: {char.key} moving {direction} from {original_location.dbref if original_location else 'None'} to {dest_room.dbref if dest_room else 'None'}")
        
        try:
            # Set flag to indicate this is an auto-walk move (not manual)
            char.ndb._is_auto_walk_move = True
            
            # Use move_to for proper movement with all hooks
            result = char.move_to(dest_room, quiet=False)
            
            # Clear the auto-walk move flag
            if hasattr(char.ndb, '_is_auto_walk_move'):
                del char.ndb._is_auto_walk_move
            
            if pathing_channel:
                pathing_channel.msg(f"STEP_MOVE_RESULT: {char.key} - result={result}, new_location={char.location.dbref if char.location else 'None'}")
            
            if result and char.location != original_location:
                # Success - remove this step from path
                char.ndb.auto_walk_path = path[1:]
                
                if pathing_channel:
                    pathing_channel.msg(f"STEP_SUCCESS: {char.key} - {len(char.ndb.auto_walk_path)} steps remaining")
                
                # Check if more steps remain
                remaining = len(char.ndb.auto_walk_path)
                if remaining > 0:
                    # Schedule next step
                    if pathing_channel:
                        pathing_channel.msg(f"STEP_SCHEDULE: {char.key} - next step in {step_delay}s")
                    delay(step_delay, self._take_step)
                else:
                    # Arrived!
                    char.msg(f"|gArrived at {self.destination_alias}.|n")
                    if pathing_channel:
                        pathing_channel.msg(f"STEP_ARRIVED: {char.key} at destination")
                    self._cleanup()
            else:
                # Movement failed
                if pathing_channel:
                    pathing_channel.msg(f"STEP_FAIL: {char.key} - movement returned {result}")
                char.msg(f"|rAuto-walk stopped:|n Could not move {direction}.")
                self._cleanup()
                
        except Exception as e:
            if pathing_channel:
                pathing_channel.msg(f"STEP_ERROR: {char.key} - movement exception: {e}")
            char.msg(f"|rAuto-walk stopped:|n Movement error: {e}")
            self._cleanup()
    
    def _check_interrupts(self):
        """
        Check for conditions that should interrupt auto-walk.
        
        Returns:
            str: Reason for interruption, or None if no interruption
        """
        char = self.obj
        if not char:
            return "Character no longer exists"
        
        # Check if manually cancelled
        if getattr(char.ndb, 'auto_walk_cancelled', False):
            return "Cancelled by player"
        
        # Check combat state
        if hasattr(char.ndb, 'combat_handler'):
            handler = char.ndb.combat_handler
            if handler and getattr(handler, 'is_active', False):
                return "Entered combat"
        
        # Check if character is dead or unconscious
        if hasattr(char, 'is_dead') and char.is_dead():
            return "Character is dead"
        
        if hasattr(char, 'is_unconscious') and char.is_unconscious():
            return "Character is unconscious"
        
        # Check if forcibly moved (teleported)
        expected_room = None
        path = getattr(char.ndb, 'auto_walk_path', [])
        if path:
            # We should be in the room BEFORE the first path step
            # Actually, just trust current location is valid
            pass
        
        # Check if location is None
        if not char.location:
            return "Character has no location"
        
        return None
    
    def _cleanup(self):
        """Clean up auto-walk state and stop script."""
        char = self.obj
        if char:
            # Clear NDB attributes
            for attr in ['auto_walk_path', 'auto_walk_mode', 'auto_walk_destination', 'auto_walk_cancelled']:
                if hasattr(char.ndb, attr):
                    delattr(char.ndb, attr)
        
        self.stop()
    
    def at_stop(self):
        """Called when script stops."""
        # Ensure cleanup happens
        char = self.obj
        if char:
            for attr in ['auto_walk_path', 'auto_walk_mode', 'auto_walk_destination', 'auto_walk_cancelled']:
                if hasattr(char.ndb, attr):
                    delattr(char.ndb, attr)


def start_auto_walk(character, path, mode="walk", destination_alias="destination"):
    """
    Start auto-walking a character along a path.
    
    Args:
        character: The character to move
        path: List of (exit_obj, destination_room) tuples
        mode: Movement mode ("walk", "jog", "run", "sprint")
        destination_alias: Name of destination for messages
        
    Returns:
        bool: True if auto-walk started, False if failed
    """
    pathing_channel = get_or_create_channel("Pathing")
    
    character.msg(f"|y[START_AUTO_WALK] Called with path length: {len(path) if path else 0}|n")
    
    if pathing_channel:
        pathing_channel.msg(f"START_WALK: {character.key if character else 'None'} - path length: {len(path) if path else 0}, mode: {mode}")
    
    if not character or not path:
        character.msg(f"|r[START_AUTO_WALK] Failed: char={bool(character)}, path={bool(path)}|n")
        if pathing_channel:
            pathing_channel.msg(f"START_WALK_ERROR: char={bool(character)}, path={bool(path)}")
        return False
    
    # Cancel any existing auto-walk
    character.msg(f"|y[START_AUTO_WALK] Cancelling any existing auto-walk|n")
    cancel_auto_walk(character, silent=True)
    
    # Validate mode
    if mode not in MOVEMENT_MODES:
        mode = DEFAULT_MODE
        if pathing_channel:
            pathing_channel.msg(f"START_WALK_MODE: {character.key} - invalid mode, using {DEFAULT_MODE}")
    
    # Store path data on character
    character.msg(f"|y[START_AUTO_WALK] Storing path data in NDB|n")
    character.ndb.auto_walk_path = path
    character.ndb.auto_walk_mode = mode
    character.ndb.auto_walk_destination = destination_alias
    character.ndb.auto_walk_cancelled = False
    
    character.msg(f"|y[START_AUTO_WALK] Path stored: {len(path)} steps, mode={mode}|n")
    
    if pathing_channel:
        pathing_channel.msg(f"START_WALK_STORED: {character.key} - NDB state set, path length: {len(path)}, mode={mode}")
    
    # Send user messages
    try:
        stamina_cost, step_delay = MOVEMENT_MODES.get(mode, MOVEMENT_MODES[DEFAULT_MODE])
        character.msg(f"|gAuto-walk started.|n Mode: |w{mode}|n, {len(path)} steps to {destination_alias}.")
        character.msg("|yType any movement command or |wpath stop|y to cancel.|n")
        
        character.msg(f"|y[START_AUTO_WALK] Scheduling first step in 0.5s|n")
        
        # Schedule first step directly using delay, not through script
        delay(0.5, _execute_auto_walk_step, character)
        
        if pathing_channel:
            pathing_channel.msg(f"START_WALK_STARTED: {character.key} - first step scheduled")
        
        character.msg(f"|g[START_AUTO_WALK] Auto-walk scheduled!|n")
        return True
    except Exception as e:
        character.msg(f"|r[START_AUTO_WALK] Exception: {e}|n")
        if pathing_channel:
            pathing_channel.msg(f"START_WALK_ERROR: {character.key} - failed: {e}")
        return False


def cancel_auto_walk(character, silent=False):
    """
    Cancel any active auto-walk for a character.
    
    Args:
        character: The character to stop
        silent: If True, don't send cancellation message
        
    Returns:
        bool: True if auto-walk was active and cancelled
    """
    pathing_channel = get_or_create_channel("Pathing")
    
    if not character:
        if pathing_channel:
            pathing_channel.msg("CANCEL_WALK_ERROR: character is None")
        return False
    
    was_active = False
    
    # Set cancellation flag
    if hasattr(character.ndb, 'auto_walk_path') and character.ndb.auto_walk_path:
        character.ndb.auto_walk_cancelled = True
        was_active = True
        if pathing_channel:
            pathing_channel.msg(f"CANCEL_WALK: {character.key} - flag set")
    
    # Clear NDB attributes
    for attr in ['auto_walk_path', 'auto_walk_mode', 'auto_walk_destination', 'auto_walk_cancelled']:
        if hasattr(character.ndb, attr):
            delattr(character.ndb, attr)
    
    if was_active and not silent:
        character.msg("|yAuto-walk cancelled.|n")
    
    if pathing_channel and was_active:
        pathing_channel.msg(f"CANCEL_WALK_DONE: {character.key} - active={was_active}")
    
    return was_active


def is_auto_walking(character):
    """
    Check if a character is currently auto-walking.
    
    Args:
        character: The character to check
        
    Returns:
        bool: True if auto-walking
    """
    if not character:
        return False
    
    return bool(getattr(character.ndb, 'auto_walk_path', None))
