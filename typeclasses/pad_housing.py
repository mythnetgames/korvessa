"""
Pad Housing System

Implements the pad door access system for larger rentable housing units.
Pads are multi-room zones with keypad-locked doors that require a code to enter.
Unlike cubes, pads create their own zone and can contain multiple rooms.
"""

import time
import random
import string
from evennia.objects.objects import DefaultExit, DefaultRoom
from evennia.typeclasses.attributes import AttributeProperty
from .exits import Exit
from .rooms import Room


# Pad-specific constants
PAD_CODE_LENGTH = 6
PAD_CODE_CHARSET = string.ascii_uppercase + string.digits
PAD_DEFAULT_WEEKLY_RENT = 1  # Default weekly rent in dollars, can be changed via SETRENT
RENT_PERIOD_SECONDS = 7 * 24 * 3600  # 7 days in seconds


def generate_unique_pad_code():
    """
    Generate a unique 6-character alphanumeric code (A-Z, 0-9).
    Checks against all active pad codes to ensure uniqueness.
    """
    from evennia.objects.models import ObjectDB
    
    # Get all active pad door codes
    active_codes = set()
    
    # Check PadDoor codes
    pad_doors = ObjectDB.objects.filter(
        db_typeclass_path__contains="PadDoor"
    )
    
    now = time.time()
    for door in pad_doors:
        # Only count codes from pads with active rent
        rent_until = door.db.rent_paid_until_ts or 0
        if rent_until > now and door.db.current_door_code:
            active_codes.add(door.db.current_door_code.upper())
    
    # Also check CubeDoor codes to ensure uniqueness across all housing
    cube_doors = ObjectDB.objects.filter(
        db_typeclass_path__contains="CubeDoor"
    )
    
    for door in cube_doors:
        rent_until = door.db.rent_paid_until_ts or 0
        if rent_until > now and door.db.current_door_code:
            active_codes.add(door.db.current_door_code.upper())
    
    # Generate unique code
    for _ in range(100):  # Max attempts
        code = ''.join(random.choice(PAD_CODE_CHARSET) for _ in range(PAD_CODE_LENGTH))
        if code not in active_codes:
            return code
    
    # Fallback - should never happen with 36^6 possibilities
    return ''.join(random.choice(PAD_CODE_CHARSET) for _ in range(PAD_CODE_LENGTH))


class PadDoor(Exit):
    """
    A keypad-locked door for pad housing units.
    
    Requires a valid code and current rent to traverse.
    Access is granted via the ENTER <code> <direction> command.
    Unlike cube doors, pad doors do NOT auto-traverse - player must walk through.
    
    Attributes:
        current_door_code: 6-character A-Z0-9 code
        rent_paid_until_ts: Unix timestamp when rent expires
        current_renter_id: Character dbref of current renter
        weekly_rent: Weekly rent amount in dollars
        zone_id: The zone this pad belongs to
        hallway_room_id: The hallway room this door connects from
        is_entry_door: True if this is the door INTO the pad (from hallway)
    """
    
    # Door properties
    current_door_code = AttributeProperty(None, category="housing", autocreate=True)
    rent_paid_until_ts = AttributeProperty(0, category="housing", autocreate=True)
    current_renter_id = AttributeProperty(None, category="housing", autocreate=True)
    weekly_rent = AttributeProperty(PAD_DEFAULT_WEEKLY_RENT, category="housing", autocreate=True)
    zone_id = AttributeProperty(None, category="housing", autocreate=True)
    hallway_room_id = AttributeProperty(None, category="housing", autocreate=True)
    is_entry_door = AttributeProperty(False, category="housing", autocreate=True)
    is_unlocked = AttributeProperty(False, category="housing", autocreate=True)  # Temp unlock state
    paired_door_id = AttributeProperty(None, category="housing", autocreate=True)
    
    def at_object_creation(self):
        """Called when the pad door is first created."""
        super().at_object_creation()
        # Tag as pad_door for easy searching
        self.tags.add("pad_door", category="housing")
    
    @property
    def current_renter(self):
        """Get the current renter character object."""
        if self.current_renter_id:
            from evennia.objects.models import ObjectDB
            try:
                return ObjectDB.objects.get(id=self.current_renter_id)
            except ObjectDB.DoesNotExist:
                return None
        return None
    
    @current_renter.setter
    def current_renter(self, char):
        """Set the current renter."""
        if char:
            self.current_renter_id = char.id
        else:
            self.current_renter_id = None
    
    def is_rent_current(self):
        """Check if rent is paid up."""
        if not self.rent_paid_until_ts:
            return False
        return time.time() <= self.rent_paid_until_ts
    
    def is_assigned(self):
        """Check if pad has an active renter and code."""
        return bool(self.current_door_code and self.current_renter_id)
    
    def check_code(self, code):
        """Check if the provided code matches."""
        if not self.current_door_code:
            return False
        return code.upper() == self.current_door_code.upper()
    
    def can_traverse(self, code):
        """
        Check if traversal is allowed with the given code.
        
        Returns:
            tuple: (allowed: bool, error_message: str or None)
        """
        if not self.current_door_code:
            return (False, "The keypad is dark. This unit is unassigned.")
        
        if not self.is_rent_current():
            return (False, "The keypad buzzes. Payment required. A red indicator flashes.")
        
        if not self.check_code(code):
            return (False, "The keypad beeps angrily. A red indicator flashes.")
        
        return (True, None)
    
    def at_traverse(self, traversing_object, target_location, **kwargs):
        """
        Override default traversal - pad doors cannot be traversed normally.
        They require the ENTER command with the correct code to unlock first.
        
        For entry doors (from hallway): Must use ENTER <code> to unlock, then walk through.
        For exit doors (from inside pad): Must use ENTER <code> to unlock, then walk through.
        """
        # Check if this is an authorized traversal (door is unlocked)
        if kwargs.get("pad_authorized") or self.is_unlocked:
            # Clear the unlock state after traversal
            self.is_unlocked = False
            # Also clear paired door unlock state
            if self.paired_door_id:
                from evennia.objects.models import ObjectDB
                try:
                    paired = ObjectDB.objects.get(id=self.paired_door_id)
                    if paired and hasattr(paired, 'is_unlocked'):
                        paired.is_unlocked = False
                except ObjectDB.DoesNotExist:
                    pass
            return super().at_traverse(traversing_object, target_location, **kwargs)
        
        # Door is locked - block traversal
        traversing_object.msg("The door is locked. A red indicator light glows steadily.")
        return False
    
    def at_failed_traverse(self, traversing_object, **kwargs):
        """Called when traversal fails."""
        traversing_object.msg("The door is locked. A red indicator light glows steadily.")
    
    def unlock_door(self):
        """Temporarily unlock the door for traversal."""
        self.is_unlocked = True
        # Also unlock paired door
        if self.paired_door_id:
            from evennia.objects.models import ObjectDB
            try:
                paired = ObjectDB.objects.get(id=self.paired_door_id)
                if paired and hasattr(paired, 'is_unlocked'):
                    paired.is_unlocked = True
            except ObjectDB.DoesNotExist:
                pass
    
    def lock_door(self):
        """Lock the door."""
        self.is_unlocked = False
        # Also lock paired door
        if self.paired_door_id:
            from evennia.objects.models import ObjectDB
            try:
                paired = ObjectDB.objects.get(id=self.paired_door_id)
                if paired and hasattr(paired, 'is_unlocked'):
                    paired.is_unlocked = False
            except ObjectDB.DoesNotExist:
                pass
    
    def get_rent_remaining(self):
        """Get human-readable time until rent expires."""
        if not self.rent_paid_until_ts:
            return "No rent paid"
        
        remaining = self.rent_paid_until_ts - time.time()
        if remaining <= 0:
            return "Expired"
        
        days = int(remaining // 86400)
        hours = int((remaining % 86400) // 3600)
        minutes = int((remaining % 3600) // 60)
        
        parts = []
        if days:
            parts.append(f"{days} day{'s' if days != 1 else ''}")
        if hours:
            parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        if minutes and not days:  # Only show minutes if less than a day
            parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
        
        return ", ".join(parts) if parts else "Less than a minute"
    
    def add_rent_time(self, dollars):
        """
        Add rent time based on payment amount.
        
        Args:
            dollars: Amount paid in dollars
            
        Returns:
            float: Seconds of rent time added
        """
        # weekly_rent dollars = 7 days (RENT_PERIOD_SECONDS)
        # seconds_per_dollar = RENT_PERIOD_SECONDS / weekly_rent
        if self.weekly_rent <= 0:
            self.weekly_rent = PAD_DEFAULT_WEEKLY_RENT
        
        seconds_per_dollar = RENT_PERIOD_SECONDS / self.weekly_rent
        seconds_added = dollars * seconds_per_dollar
        
        # If rent has expired, start from now
        now = time.time()
        if not self.rent_paid_until_ts or self.rent_paid_until_ts < now:
            self.rent_paid_until_ts = now + seconds_added
        else:
            self.rent_paid_until_ts = self.rent_paid_until_ts + seconds_added
        
        # Sync to paired door
        if self.paired_door_id:
            from evennia.objects.models import ObjectDB
            try:
                paired_door = ObjectDB.objects.get(id=self.paired_door_id)
                paired_door.rent_paid_until_ts = self.rent_paid_until_ts
            except ObjectDB.DoesNotExist:
                pass
        
        return seconds_added
    
    def get_formatted_exit_name(self):
        """
        Get the exit name with door status indicator.
        
        Returns:
            str: Exit name with + (locked) or - (unlocked) prefix
        """
        indicator = "+" if not self.is_unlocked else "-"
        return f"{indicator}{self.key}"
    
    def get_entry_door(self):
        """
        Get the entry door (the one from the hallway) for this pad.
        If this IS the entry door, return self.
        Otherwise, find it via the paired door.
        """
        if self.is_entry_door:
            return self
        if self.paired_door_id:
            from evennia.objects.models import ObjectDB
            try:
                paired = ObjectDB.objects.get(id=self.paired_door_id)
                if paired and hasattr(paired, 'is_entry_door') and paired.is_entry_door:
                    return paired
            except ObjectDB.DoesNotExist:
                pass
        return None


class PadRoom(Room):
    """
    A room inside a pad housing unit.
    
    Part of a pad zone with a linked PadDoor exit.
    """
    
    # Pad room properties
    pad_zone_id = AttributeProperty(None, category="housing", autocreate=True)
    is_pad_entry = AttributeProperty(False, category="housing", autocreate=True)
    
    def at_object_creation(self):
        """Called when the pad room is first created."""
        super().at_object_creation()
        # Tag for easy identification - defer tag addition to avoid _SaverList issues
        # Tags will be added in at_init instead
    
    def at_init(self):
        """Called after object is fully initialized."""
        super().at_init()
        # Add tag for easy identification
        try:
            self.tags.add("pad_room", category="housing")
        except Exception:
            # Silently ignore tag errors during initialization
            pass
    
    def get_pad_door(self):
        """
        Find the PadDoor exit that leads out of this pad.
        
        Returns:
            PadDoor or None
        """
        for exit_obj in self.exits:
            if exit_obj.is_typeclass("typeclasses.pad_housing.PadDoor"):
                return exit_obj
        return None
    
    def get_exit_to_hallway(self):
        """
        Find any exit that leads out of the pad (to the hallway).
        
        Returns:
            Exit or None
        """
        # First try to find a PadDoor
        pad_door = self.get_pad_door()
        if pad_door:
            return pad_door
        
        # Otherwise find any exit
        if self.exits:
            return self.exits[0]
        
        return None
